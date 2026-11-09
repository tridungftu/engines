"""Shared editable document layout, preserving geometry without absolute text boxes."""
from copy import deepcopy
import io
import re
import zipfile
from defusedxml import ElementTree as ET
import pymupdf

from .extraction import W, paragraph_text, barcode_translation


def inside(box, rect):
    x,y = (box[0]+box[2])/2,(box[1]+box[3])/2
    return rect[0]-1 <= x <= rect[2]+1 and rect[1]-1 <= y <= rect[3]+1


def infer_alignment(box, left, right):
    width = right-left
    if width <= 0:
        return 'left'
    if abs((box[0]+box[2])/2-(left+right)/2)<width*.05 and box[2]-box[0]<width*.82:
        return 'center'
    if abs(box[2]-right)<8 and box[0]-left>width*.2:
        return 'right'
    return 'left'


def native_tables(page):
    result = []
    for source in page.find_tables().tables:
        cells = [list(cell) for cell in source.cells if cell]
        def clustered(values):
            groups=[]
            for value in sorted(values):
                if not groups or value-groups[-1][-1]>2:
                    groups.append([value])
                else:
                    groups[-1].append(value)
            return [sum(g)/len(g) for g in groups]
        xs=clustered([c[i] for c in cells for i in (0,2)])
        ys=clustered([c[i] for c in cells for i in (1,3)])
        if len(xs)<2 or len(ys)<2 or len(xs)>41 or len(ys)>101:
            continue
        items=[]
        for box in cells:
            c0,c1=[min(range(len(xs)),key=lambda j:abs(xs[j]-box[i])) for i in (0,2)]
            r0,r1=[min(range(len(ys)),key=lambda j:abs(ys[j]-box[i])) for i in (1,3)]
            if c1>c0 and r1>r0:
                items.append({'row':r0,'col':c0,'rowspan':r1-r0,'colspan':c1-c0,'bbox':box,'unit_ids':[]})
        result.append({'type':'table','bbox':list(source.bbox),'rows':len(ys)-1,'cols':len(xs)-1,
                       'cells':items,'col_widths':[b-a for a,b in zip(xs,xs[1:])], 'source':'pdf_geometry','uncertain':False})
    return result


def build_blocks(page, tables):
    units=page['units']
    # OCR can put a short list label after its taller neighbouring formula.
    # Group by line centre before reading left-to-right, retaining every unit.
    lines=[]
    for unit in sorted(units,key=lambda u:(u['bbox'][1],u['bbox'][0])):
        box=unit['bbox'];cy=(box[1]+box[3])/2;h=box[3]-box[1]
        match=next((line for line in reversed(lines[-3:]) if abs(line['cy']-cy)<max(3,min(line['height'],h)*.45)),None)
        if match is None: lines.append({'cy':cy,'height':h,'items':[unit]})
        else: match['items'].append(unit)
    units=[u for line in lines for u in sorted(line['items'],key=lambda u:u['bbox'][0])]
    page['units']=units
    # Clear any previous assignments; geometry is immutable across review edits.
    tables=deepcopy(tables)
    for table in tables:
        for cell in table['cells']:
            cell['unit_ids']=[]
    outside=[]
    for unit in units:
        assigned=False
        for ti,table in enumerate(tables):
            if not inside(unit['bbox'],table['bbox']):
                continue
            candidates=[c for c in table['cells'] if inside(unit['bbox'],c['bbox'])]
            if len(candidates)==1:
                cell=candidates[0]
                cell['unit_ids'].append(unit['id'])
                unit['table_cell']={'table':ti,'row':cell['row'],'col':cell['col']}
                unit['style']['align']=infer_alignment(unit['bbox'],cell['bbox'][0],cell['bbox'][2])
                if unit['bbox'][0]<cell['bbox'][0]-3 or unit['bbox'][2]>cell['bbox'][2]+3:
                    table['uncertain']=True
                assigned=True
                break
            table['uncertain']=True
        if not assigned:
            outside.append(unit)
    left=min((u['bbox'][0] for u in outside),default=40)
    right=max((u['bbox'][2] for u in outside),default=page['width']-40)
    blocks=[]
    for unit in outside:
        unit['style'].setdefault('align',infer_alignment(unit['bbox'],left,right))
        box=unit['bbox']
        previous=blocks[-1] if blocks else None
        if previous and abs((previous['bbox'][1]+previous['bbox'][3])/2-(box[1]+box[3])/2)<max(3,(box[3]-box[1])*.45) and -min(12,(previous['bbox'][2]-previous['bbox'][0])*.4)<=box[0]-previous['bbox'][2]<90:
            previous['unit_ids'].append(unit['id'])
            previous['bbox']=[min(previous['bbox'][0],box[0]),min(previous['bbox'][1],box[1]),max(previous['bbox'][2],box[2]),max(previous['bbox'][3],box[3])]
        else:
            blocks.append({'type':'paragraph','bbox':list(box),'unit_ids':[unit['id']]})
    for ti,table in enumerate(tables):
        blocks.append(table)
        if table['uncertain']:
            page['issues'].append({'id':f"p{page['number']}-table{ti}",'type':'table_structure','resolved':False,
                                   'bbox':table['bbox'],'message':'Ranh giới/ô gộp của bảng chưa chắc chắn. Kiểm tra hàng, cột với ảnh gốc.'})
    blocks.sort(key=lambda b:(b['bbox'][1],b['bbox'][0]))
    page['blocks']=blocks
    page['margins']={'left':max(18,min(72,left)), 'right':max(18,min(72,page['width']-right)),
                     'top':max(18,min(50,min((u['bbox'][1] for u in units),default=36))), 'bottom':24}
    return page


def native_page(source, number):
    page={'number':number,'width':source.rect.width,'height':source.rect.height,'mode':'native',
          'units':[],'blocks':[],'issues':[],'warnings':[]}
    translation=barcode_translation(source)
    try:
        tables=native_tables(source)
    except Exception:
        tables=[]
        page['issues'].append({'id':f'p{number}-table-failed','type':'table_structure','resolved':False,
                               'bbox':list(source.rect),'message':'Không phân tích được bảng. Kiểm tra cấu trúc trang trước khi xuất bản cuối.'})
    for block in source.get_text('dict',flags=pymupdf.TEXTFLAGS_TEXT,sort=True)['blocks']:
        for line in block.get('lines',[]):
            groups=[]
            for span in line['spans']:
                # Separate distant columns while retaining adjacent mixed formatting runs.
                if not groups or span['bbox'][0]-groups[-1][-1]['bbox'][2]>14:
                    groups.append([span])
                else:
                    groups[-1].append(span)
            for group in groups:
                runs=[]
                for span in group:
                    runs.append({'text':span['text'].translate(translation),'size':round(span['size'],1),
                                 'bold':bool(span['flags']&16),'italic':bool(span['flags']&2)})
                text=''.join(r['text'] for r in runs).strip()
                if not text:
                    continue
                box=[min(s['bbox'][0] for s in group),min(s['bbox'][1] for s in group),
                     max(s['bbox'][2] for s in group),max(s['bbox'][3] for s in group)]
                page['units'].append({'id':f'p{number}-u{len(page["units"])}','bbox':box,'text':text,
                                      'runs':runs,'style':{k:runs[0][k] for k in ('size','bold','italic')},'source':'native'})
    return build_blocks(page,tables)


def word_layout(data, legacy, embedded_pages=None):
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
    if embedded_pages is not None:
        append_embedded_pages(page, embedded_pages)
    elif '[Chữ từ ảnh nhúng ' in legacy.text:
        extra=legacy.text[legacy.text.index('[Chữ từ ảnh nhúng '):]
        uid=f'p1-u{len(page["units"])}'
        page['units'].append({'id':uid,'text':extra,'bbox':[0,0,515,20],'style':{'size':12},'source':'embedded_ocr'})
        page['blocks'].append({'type':'paragraph','unit_ids':[uid]})
        page['issues'].append({'id':'p1-embedded','type':'embedded_image','resolved':False,'bbox':[0,0,515,20],
                               'message':'Ảnh nhúng trong Word đang dùng OCR một engine; kiểm tra phần chữ từ ảnh trước khi xác nhận.'})
    return page


def append_embedded_pages(page, embedded_pages):
    """Keep embedded-image readings and differences on the logical DOCX page.

    DOCX has no reliable physical page map. Flow boxes serve Word export; the
    original image box and image index remain explicit reference metadata.
    """
    width = max(72, page['width']-page['margins']['left']-page['margins']['right'])
    cursor = max((unit['bbox'][3] for unit in page['units']), default=0)+24
    for index, embedded in enumerate(embedded_pages, 1):
        prefix = f'p1-img{index}-'
        label_id = prefix+'label'
        page['units'].append({'id': label_id, 'text': f'Chữ từ ảnh nhúng {index}',
                              'bbox': [0, cursor, width, cursor+16],
                              'style': {'size': 12, 'bold': True}, 'source': 'embedded_label'})
        page['blocks'].append({'type': 'paragraph', 'unit_ids': [label_id]})
        cursor += 20
        scale = width/max(1, embedded['width'])

        def flow_box(box):
            return [box[0]*scale, cursor+box[1]*scale,
                    box[2]*scale, cursor+box[3]*scale]

        ids = {unit['id']: prefix+unit['id'].split('-', 1)[1]
               for unit in embedded['units']}
        for original in embedded['units']:
            unit = deepcopy(original)
            old_id = unit['id']
            unit['id'] = ids[old_id]
            unit['reference'] = {**unit.get('reference', {}), 'page_number': 1,
                'region_id': unit['id'], 'embedded_image_index': index,
                'coordinate_space': 'embedded_image_points', 'image_bbox': list(unit['bbox'])}
            unit['bbox'] = flow_box(unit['bbox'])
            unit['style']['size'] = min(48, max(8, unit['style'].get('size', 12)*scale))
            unit.pop('table_cell', None)
            for part in unit.get('parts', []):
                part['id'] = unit['id']+part['id'][len(old_id):]
            page['units'].append(unit)
        for original in embedded.get('blocks', []):
            block = deepcopy(original)
            if 'bbox' in block:
                block['bbox'] = flow_box(block['bbox'])
            if block['type'] == 'table':
                block['col_widths'] = [value*scale for value in block['col_widths']]
                for cell in block['cells']:
                    cell['unit_ids'] = [ids[uid] for uid in cell['unit_ids']]
                    if 'bbox' in cell:
                        cell['bbox'] = flow_box(cell['bbox'])
            else:
                block['unit_ids'] = [ids[uid] for uid in block['unit_ids']]
            page['blocks'].append(block)
        for original in embedded.get('issues', []):
            issue = deepcopy(original)
            issue['id'] = prefix+issue['id'].split('-', 1)[1]
            if 'bbox' in issue:
                issue['bbox'] = flow_box(issue['bbox'])
            page['issues'].append(issue)
        page['issues'].append({'id': prefix+'layout', 'type': 'embedded_image', 'resolved': False,
            'bbox': [0, cursor, width, cursor+embedded['height']*scale],
            'message': f'Chữ từ ảnh nhúng {index} được đưa riêng vào cuối tài liệu; kiểm tra với ảnh gốc trong Word.'})
        for warning in embedded.get('warnings', []):
            if warning not in page['warnings']:
                page['warnings'].append(warning)
        cursor += embedded['height']*scale+24
