"""Chuyen word_layout cua mask_ocr: giu thu tu, o rong, gridSpan/vMerge.

Chi goi sau extract_docx da kiem cau truc; khong co runtime review.
"""
import io
import re
import zipfile
from . import common as ET
from .extraction import W, paragraph_text


def word_layout(data, legacy):
    """Use existing validated OOXML, not OCR, for Word tables and formatting."""
    page={'number':1,'width':595.3,'height':841.9,'mode':'document','units':[],'blocks':[],
          'issues':[],'warnings':legacy.warnings,'margins':{'left':40,'right':40,'top':36,'bottom':36}}
    styles={}; defaults={'size':12,'bold':False,'italic':False,'align':'left'}; normal='Normal'
    def properties(rpr,ppr=None):
        result={}
        if rpr is not None:
            for tag,key in [('b','bold'),('i','italic')]:
                el=rpr.find(W+tag)
                if el is not None: result[key]=el.get(W+'val','1') not in ('0','false','off')
            size=rpr.find(W+'sz')
            if size is not None: result['size']=float(size.get(W+'val','24'))/2
        if ppr is not None:
            jc=ppr.find(W+'jc')
            if jc is not None: result['align']={'both':'justify','center':'center','right':'right'}.get(jc.get(W+'val'),'left')
        return result
    def inherited(style_id,seen=None):
        seen=set() if seen is None else seen
        if style_id in seen or style_id not in styles: return {}
        seen.add(style_id); entry=styles[style_id]
        return {**inherited(entry['parent'],seen),**entry['properties']}
    def parse_paragraph(node):
        ppr=node.find(W+'pPr'); sid=node.find(W+'pPr/'+W+'pStyle')
        base={**defaults,**inherited(sid.get(W+'val') if sid is not None else normal),**properties(None,ppr)}
        runs=[]
        for run in node.iter(W+'r'):
            text=paragraph_text(run)
            if not text:
                continue
            props=run.find(W+'rPr')
            rid=run.find(W+'rPr/'+W+'rStyle')
            runs.append({'text':text,**base,**inherited(rid.get(W+'val') if rid is not None else ''),**properties(props)})
        if not runs:
            return []
        style={k:runs[0][k] for k in ('size','bold','italic')}
        style['align']=base['align']
        uid=f'p1-u{len(page["units"])}'
        unit={'id':uid,'text':''.join(r['text'] for r in runs),'runs':runs,'style':style,
              'bbox':[0,len(page['units'])*16,515,len(page['units'])*16+14],'source':'native'}
        page['units'].append(unit)
        return [uid]
    def parse_children(parent):
        blocks=[]
        for node in parent:
            if node.tag==W+'p':
                ids=parse_paragraph(node)
                if ids:
                    blocks.append({'type':'paragraph','unit_ids':ids})
            elif node.tag==W+'tbl':
                grid=node.find(W+'tblGrid')
                widths=[float(c.get(W+'w','1440'))/20 for c in grid] if grid is not None else []
                cells=[]; active={}; cols=0
                rows=node.findall(W+'tr')
                for rowindex,row in enumerate(rows):
                    before=row.find(W+'trPr/'+W+'gridBefore')
                    col=int(before.get(W+'val','0')) if before is not None else 0
                    next_active={}
                    for cell in row.findall(W+'tc'):
                        span=cell.find(W+'tcPr/'+W+'gridSpan')
                        count=int(span.get(W+'val','1')) if span is not None else 1
                        merge=cell.find(W+'tcPr/'+W+'vMerge')
                        if merge is not None and merge.get(W+'val','continue')=='continue' and col in active:
                            anchor=active[col]; anchor['rowspan']+=1; next_active[col]=anchor
                        else:
                            ids=[]
                            for paragraph in cell.findall(W+'p'):
                                ids.extend(parse_paragraph(paragraph))
                            anchor={'row':rowindex,'col':col,'rowspan':1,'colspan':count,'unit_ids':ids}
                            cells.append(anchor)
                            if merge is not None:
                                next_active[col]=anchor
                        col+=count
                    active=next_active; cols=max(cols,col)
                if cols>40 or len(rows)>100:
                    from .common import ExtractionError
                    raise ExtractionError('Bảng Word vượt 100 hàng hoặc 40 cột; hãy chia nhỏ bảng.')
                if len(widths)!=cols:
                    widths=[515/max(cols,1)]*cols
                blocks.append({'type':'table','rows':len(rows),'cols':cols,'cells':cells,'col_widths':widths,'source':'docx'})
            elif node.tag not in {W+'sectPr',W+'tcPr'}:
                blocks.extend(parse_children(node))
        return blocks
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if 'word/styles.xml' in archive.namelist():
            style_root=ET.fromstring(archive.read('word/styles.xml'))
            defaults.update(properties(style_root.find(W+'docDefaults/'+W+'rPrDefault/'+W+'rPr'),style_root.find(W+'docDefaults/'+W+'pPrDefault/'+W+'pPr')))
            for entry in style_root.findall(W+'style'):
                sid=entry.get(W+'styleId'); parent=entry.find(W+'basedOn')
                styles[sid]={'parent':parent.get(W+'val') if parent is not None else '', 'properties':properties(entry.find(W+'rPr'),entry.find(W+'pPr'))}
                if entry.get(W+'type')=='paragraph' and entry.get(W+'default')=='1': normal=sid
        root=ET.fromstring(archive.read('word/document.xml'))
        section=root.find('.//'+W+'sectPr')
        if section is not None:
            size=section.find(W+'pgSz'); margins=section.find(W+'pgMar')
            if size is not None:
                page.update(width=float(size.get(W+'w','11906'))/20,height=float(size.get(W+'h','16838'))/20)
            if margins is not None:
                page['margins']={key:float(margins.get(W+key,'720'))/20 for key in ('left','right','top','bottom')}
        page['blocks']=parse_children(root.find(W+'body'))
        # Preserve readable header/footer/notes text in the simplified output as well.
        for name in sorted(archive.namelist()):
            if re.fullmatch(r'word/(?:header\d+|footer\d+|footnotes|endnotes)\.xml',name):
                extra=ET.fromstring(archive.read(name))
                page['blocks'].extend(parse_children(extra))
    if '[Chữ từ ảnh nhúng ' in legacy.text:
        extra=legacy.text[legacy.text.index('[Chữ từ ảnh nhúng '):]
        uid=f'p1-u{len(page["units"])}'
        page['units'].append({'id':uid,'text':extra,'bbox':[0,0,515,20],'style':{'size':12},'source':'embedded_ocr'})
        page['blocks'].append({'type':'paragraph','unit_ids':[uid]})
        page['issues'].append({'id':'p1-embedded','type':'embedded_image','resolved':False,'bbox':[0,0,515,20],
                               'message':'Ảnh nhúng trong Word đang dùng OCR một engine; kiểm tra phần chữ từ ảnh trước khi xác nhận.'})
    return page

