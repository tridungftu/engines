"""B8: mở XLSX trên chính tệp AI, dùng chung gate/map/patch của Word.

Reader B3 ghép rich runs cùng ô, giữ nguồn shared/index và chặn sheet
phải đổi tên/phần lạ. Writer B4 kiểm số/format/bytes ô bất biến. Không
tra kho, không fallback workbook mới hoặc Office COM.
"""
from .doc_excel import doc_excel
from .mo_tep_word import _bao_ve_mo, _mo_tep


@_bao_ve_mo
def mo_excel(du_lieu, *, buoc):
    return _mo_tep(du_lieu, buoc=buoc, loai='xlsx', doc=doc_excel)
