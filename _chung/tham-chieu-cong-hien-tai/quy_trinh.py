"""G2-28: runner Core trên hàng việc G2-14, transaction do caller quản lý.

SQL giữ DAG, CAS, quyền và lease; Python chỉ gọi cửa hẹp. Không chạy mã từ
định nghĩa. dau_ra là JSON đã kiểm contract ở Core, cùng tx với kết quả/tệp.
Khi SQL trả DUNG_QUYEN, caller phải commit để giữ dấu dừng và audit; không
ghi nghiệp vụ/công bố sau đó. Nếu callback đã ghi rồi mới mất quyền, để
exception thoát tx; sau rollback, gọi tien bằng tx mới để lưu dừng/audit,
như cổng MTQ hiện có. SDK/HTTP được nối ở G2-28b.
"""

from collections.abc import Mapping
import re
from uuid import UUID

from .tiep_nhan import _json, _khoa
from .viec import _ctx, _giu, _cas, _so, _tx, _LOI as _LOI_VIEC
from .phap_nhan_demo import _LOI as _LOI_DEMO
from .doi_cau_truc import _doc_truong


class LoiQuyTrinh(RuntimeError):
    """Chỉ giữ chẩn đoán allowlist, không giữ driver/SQL/giá trị tham số."""

    def __init__(self, ma, *, sqlstate=None, constraint_name=None, ma_raise=None):
        self.ma = ma
        self.sqlstate = (sqlstate if isinstance(sqlstate, str)
                         and re.fullmatch(r'[0-9A-Z]{5}', sqlstate) else None)
        self.constraint_name = (constraint_name if isinstance(constraint_name, str)
                                and constraint_name in _RANG_BUOC else None)
        self.ma_raise = (ma_raise if isinstance(ma_raise, str) and ma_raise in _MA_RAISE else None)
        self.http_status = 409 if ma in {'QUY_TRINH_CAS', 'QUY_TRINH_TRUNG', 'QUY_TRINH_DA_DUNG', 'VIEC_MAT_LEASE'} else (
            404 if ma == 'QUY_TRINH_KHONG_THAY' else 403 if ma in {'QUY_TRINH_PHIEN', 'VIEC_CONG_TAC'}
            else 422 if ma in _LOI else 500)
        chi_tiet = [f'{ten}={gia_tri}' for ten, gia_tri in (
            ('sqlstate', self.sqlstate), ('constraint_name', self.constraint_name),
            ('ma_raise', self.ma_raise)) if gia_tri is not None]
        super().__init__('Thao tác quy trình thất bại (' + ma + ')'
                         + (': ' + '; '.join(chi_tiet) if chi_tiet else ''))


_LOI = {'QUY_TRINH_CAS', 'QUY_TRINH_TRUNG', 'QUY_TRINH_KHONG_THAY',
        'QUY_TRINH_PHIEN', 'QUY_TRINH_DA_DUNG', 'QUY_TRINH_DINH_NGHIA', 'QUY_TRINH_DAG',
        'QUY_TRINH_POINTER', 'QUY_TRINH_DAU_VAO', 'VIEC_MAT_LEASE', 'VIEC_CONG_TAC'}

_MA_RAISE = _LOI | _LOI_VIEC | _LOI_DEMO
# Tên cố định từ DDL 030/014 trên đường bắt đầu/chuyển bước. Không phản
# chiếu identifier tùy ý: cả tên constraint hợp lệ cũng có thể chứa dữ liệu.
_RANG_BUOC = frozenset({
    'quy_trinh_pkey', 'quy_trinh_phap_nhan_id_fkey', 'quy_trinh_module_fkey',
    'quy_trinh_ma_check', 'quy_trinh_phien_ban_check', 'quy_trinh_buoc_check',
    'quy_trinh_ma_bam_check', 'quy_trinh_tao_boi_fkey',
    'quy_trinh_module_phien_ban_module_fkey',
    'quy_trinh_lan_pkey', 'quy_trinh_lan_tao_boi_fkey',
    'quy_trinh_lan_revision_check', 'quy_trinh_lan_trang_thai_check',
    'quy_trinh_lan_phap_nhan_id_module_khoa_key', 'quy_trinh_lan_id_phap_nhan_id_module_key',
    'quy_trinh_lan_phap_nhan_id_module_ma_phien_ban_fkey',
    'viec_quy_trinh_fk', 'viec_quy_trinh_cap', 'viec_quy_trinh_buoc',
    'hang_viec_pkey', 'hang_viec_phap_nhan_id_fkey', 'hang_viec_module_fkey',
    'hang_viec_loai_check', 'hang_viec_phien_ban_check', 'hang_viec_engine_id_fkey',
    'hang_viec_phien_ban_contract_check', 'hang_viec_khoa_chong_trung_check',
    'hang_viec_bang_tham_chieu_check', 'hang_viec_toi_da_lan_thu_check',
    'hang_viec_thu_lai_giay_check', 'hang_viec_giu_ngay_check', 'hang_viec_trang_thai_check',
    'hang_viec_so_lan_thu_check', 'hang_viec_the_he_check', 'hang_viec_phien_ban_dong_check',
    'hang_viec_giu_phien_id_fkey', 'hang_viec_ma_loi_check', 'hang_viec_tao_boi_fkey',
    'hang_viec_phap_nhan_id_module_khoa_chong_trung_key', 'hang_viec_id_phap_nhan_id_module_key',
    'hang_viec_check', 'hang_viec_check1', 'hang_viec_lan_thu_fk',
    'buoc_viec_pkey', 'buoc_viec_viec_id_ma_buoc_key',
    'buoc_viec_id_viec_id_phap_nhan_id_module_key',
    'buoc_viec_viec_id_phap_nhan_id_module_fkey',
})


def _duong(duong):
    if not isinstance(duong, str) or (duong and not duong.startswith('/')) or re.search(r'~([^01]|$)', duong):
        raise ValueError('JSON pointer không hợp lệ')
    return [] if not duong else [x.replace('~1', '/').replace('~0', '~') for x in duong[1:].split('/')]


def json_pointer(data, duong):
    """RFC6901: không ép kiểu, không chạy JSONPath hoặc mã tùy ý."""
    for k in _duong(duong):
        if isinstance(data, dict) and k in data:
            data = data[k]
        elif isinstance(data, list) and re.fullmatch(r'0|[1-9][0-9]{0,8}', k) and int(k) < len(data):
            data = data[int(k)]
        else:
            raise ValueError('Thiếu nguồn JSON pointer')
    return data


def kiem_dinh(buoc):
    """Kiểm sớm ở Core; CSDL kiểm độc lập khi đăng ký để giữ biên an toàn."""
    _json(buoc)
    bat_buoc = {'ma', 'phu_thuoc', 'loai', 'phien_ban', 'capability', 'engine_id', 'adapter', 'contract', 'cho_duyet', 'anh_xa'}
    tuy_chon = {'dieu_kien', 'co_tac_dong_ngoai', 'thu_lai_an_toan', 'phu_thuoc_neu_co'}
    if not isinstance(buoc, list) or not 1 <= len(buoc) <= 100:
        raise ValueError('Cần 1–100 bước')
    ten = set()
    for b in buoc:
        if (not isinstance(b, dict) or not bat_buoc <= b.keys() or b.keys() - bat_buoc - tuy_chon
                or not isinstance(b['ma'], str) or not re.fullmatch('[a-z][a-z0-9_]{0,39}', b['ma'])
                or b['ma'] in ten or not isinstance(b['phu_thuoc'], list)
                or any(not isinstance(x, str) for x in b['phu_thuoc'])
                or len(set(b['phu_thuoc'])) != len(b['phu_thuoc'])
                or not isinstance(b['loai'], str) or not re.fullmatch('[A-Z][A-Z0-9_-]{0,79}', b['loai'])
                or type(b['phien_ban']) is not int or not 1 <= b['phien_ban'] <= 999999999
                or type(b['cho_duyet']) is not bool or not isinstance(b['anh_xa'], dict)
                or not isinstance(b['capability'], str) or not b['capability']
                or any(k in b and type(b[k]) is not bool for k in ('co_tac_dong_ngoai', 'thu_lai_an_toan'))):
            raise ValueError('Định nghĩa bước không hợp lệ')
        mem = b.get('phu_thuoc_neu_co', [])
        if (not isinstance(mem, list) or any(not isinstance(x, str) for x in mem)
                or len(set(mem)) != len(mem) or set(mem) & set(b['phu_thuoc'])):
            raise ValueError('Phụ thuộc tùy chọn không hợp lệ')
        phu_thuoc = set(b['phu_thuoc']) | set(mem)
        if b['engine_id'] is not None:
            if not isinstance(b['engine_id'], str) or str(UUID(b['engine_id'])) != b['engine_id']:
                raise ValueError('Engine phải là UUID chuẩn đã ghim')
        for k in ('adapter', 'contract'):
            if (not isinstance(b[k], dict) or b[k].keys() != {'ma', 'phien_ban'}
                    or any(not isinstance(v, str) or not v for v in b[k].values())):
                raise ValueError('Cần adapter/contract có phiên bản cố định')
        paths = []
        for nguon in b['anh_xa'].values():
            if isinstance(nguon, list):
                if not nguon:
                    raise ValueError('Cần ít nhất một nguồn ánh xạ')
                paths.extend(nguon)
            else:
                paths.append(nguon)
        if any(not isinstance(k, str) or not k for k in b['anh_xa']):
            raise ValueError('Đích ánh xạ phải là khóa đầu vào')
        if 'dieu_kien' in b:
            dk = b['dieu_kien']
            if (not isinstance(dk, dict) or dk.keys() not in ({'duong', 'bang'}, {'duong', 'trong'})
                    or ('trong' in dk and not isinstance(dk['trong'], list))):
                raise ValueError('Chỉ nhận điều kiện bằng hoặc thuộc danh sách khai báo')
            paths.append(dk['duong'])
        for path in paths:
            parts = _duong(path)
            if (len(parts) < 2 or parts[0] not in {'dau_vao', 'buoc'}
                    or (parts[0] == 'buoc' and (len(parts) < 3 or parts[2] != 'dau_ra'
                        or parts[1] not in phu_thuoc))):
                raise ValueError('Ánh xạ phải đọc đầu vào hoặc output bước phụ thuộc')
        ten.add(b['ma'])
    done = set()
    while len(done) < len(buoc):
        ready = {b['ma'] for b in buoc
                 if set(b['phu_thuoc']) | set(b.get('phu_thuoc_neu_co', [])) <= done}
        if not ready - done:
            raise ValueError('DAG có vòng hoặc phụ thuộc không tồn tại')
        done |= ready
    return buoc


def _goi(conn, sql, ts):
    ma = 'QUY_TRINH_THAT_BAI'
    sqlstate = constraint_name = ma_raise = None
    try:
        row = conn.execute(sql, ts).fetchone()
        return row['r'] if isinstance(row, Mapping) else row[0]
    except Exception as exc:
        diag = _doc_truong(exc, 'diag')
        chinh = _doc_truong(diag, 'message_primary')
        if isinstance(chinh, str) and chinh in _LOI:
            ma = chinh
        elif isinstance(chinh, str) and chinh in {'VIEC_PHIEN', 'MODULE_PHIEN'}:
            ma = 'QUY_TRINH_PHIEN'
        sqlstate = _doc_truong(exc, 'sqlstate')
        constraint_name = _doc_truong(diag, 'constraint_name')
        ma_raise = chinh
        diag = chinh = None
    ts = None
    # Raise ngoài except như G2-00b: không giữ driver trong context/cause.
    raise LoiQuyTrinh(ma, sqlstate=sqlstate, constraint_name=constraint_name, ma_raise=ma_raise)


def dang_ky(conn, ma_quy_trinh, phien_ban, buoc, *, phien_ban_module, **ctx):
    """Core đăng ký bản bất biến; SQL kiểm cấu trúc kể cả caller bỏ qua Python."""
    ts = _ctx(conn, ctx)
    _so(phien_ban, 1, 2**31-1)
    if not isinstance(buoc, list) or not buoc or not isinstance(phien_ban_module, str):
        raise ValueError('Cần các bước và phiên bản module đã ghim')
    return _goi(conn, 'SELECT loi.quy_trinh_dang_ky(%s,%s,%s,%s,%s,%s,%s,%s::jsonb) AS r',
                (*ts, ma_quy_trinh, phien_ban, phien_ban_module, _json(kiem_dinh(buoc))))


def liet_ke(conn, **ctx):
    return _goi(conn, 'SELECT loi.quy_trinh_liet_ke(%s,%s,%s,%s) AS r', _ctx(conn, ctx))


def anh_xa(conn, ma_quy_trinh, yeu_cau, *, ma, module, phap_nhan_id, nguoi_dung_id):
    """Ánh xạ request HTTP chuẩn qua cửa DEFINER; không đọc bảng bằng runtime.

    phap_nhan_id lấy từ header đã kiểm với phiên. Khi hai tập ID rỗng,
    SQL kiểm hành động ở PN này, không gọi resolver đối tượng của module.
    """
    _tx(conn)
    return _goi(conn, 'SELECT loi.quy_trinh_anh_xa(%s,%s,%s,%s,%s,%s::jsonb) AS r',
                (ma.lay_de_truyen(), module, UUID(str(phap_nhan_id)),
                 UUID(str(nguoi_dung_id)), ma_quy_trinh, _json(yeu_cau)))


def bat_dau(conn, ma_quy_trinh, phien_ban, dau_vao, khoa, *, bang_tham_chieu, tham_chieu_id, **ctx):
    ts = _ctx(conn, ctx)
    _so(phien_ban, 1, 2**31-1)
    return _goi(conn, 'SELECT loi.quy_trinh_bat_dau(%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s) AS r',
                (*ts, ma_quy_trinh, phien_ban, _json(dau_vao), _khoa(khoa), bang_tham_chieu, UUID(str(tham_chieu_id))))


def kiem_dau_vao_buoc(lan_chay):
    """Bước tự quyết định nguồn bắt buộc qua ánh xạ/điều kiện của runner.

    Hai tập ID rỗng không tự gây lỗi. Chỉ lỗi pointer do bước thực sự đọc
    nguồn thiếu mới thành 422; không phản chiếu pointer hoặc dữ liệu nguồn.
    """
    if (lan_chay.get('trang_thai') == 'DUNG_LOI'
            and lan_chay.get('ma_loi') == 'QUY_TRINH_POINTER'):
        raise LoiQuyTrinh('QUY_TRINH_DAU_VAO', ma_raise='QUY_TRINH_POINTER')


def tien(conn, lan_chay_id, **ctx):
    """Quét lại sau commit/restart; không nhận lease cũ để chuyển bước."""
    return _goi(conn, 'SELECT loi.quy_trinh_tien(%s,%s,%s,%s,%s) AS r',
                (*_ctx(conn, ctx), UUID(str(lan_chay_id))))


def tiep_tuc(conn, lan_chay_id, buoc, revision_truoc, du_lieu, khoa, **ctx):
    return _goi(conn, 'SELECT loi.quy_trinh_tiep_tuc(%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s) AS r',
                (*_ctx(conn, ctx), UUID(str(lan_chay_id)), buoc, _cas(revision_truoc),
                 _json(du_lieu), _khoa(khoa)))


def hoan_tat(conn, lan_chay_id, buoc, giu_viec, dau_ra, *, ket_qua_id=None):
    """Kiểm lease trước ghi; hoàn tất và lưu đầu ra cùng transaction.

    Không ghi nghiệp vụ trước cửa này nếu chưa kiểm lease bằng G2-14 trên
    cùng kết nối. Exception mất lease phải thoát transaction và rollback.
    """
    return _goi(conn, 'SELECT loi.quy_trinh_hoan_tat(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s) AS r',
                (*_giu(conn, giu_viec), UUID(str(lan_chay_id)), buoc, _json(dau_ra),
                 None if ket_qua_id is None else UUID(str(ket_qua_id))))


def kiem_ghi(conn, lan_chay_id, buoc, giu_viec):
    """Cửa kiểm ngay trước ghi và trước công bố trên cùng tx/lease.

    DUNG_QUYEN là kết quả cần commit; caller không được ghi sau kết quả này.
    SQL giữ khóa quyền, lần chạy và việc tới cuối transaction.
    """
    return _goi(conn, 'SELECT loi.quy_trinh_kiem_ghi(%s,%s,%s,%s,%s,%s,%s,%s,%s) AS r',
                (*_giu(conn, giu_viec), UUID(str(lan_chay_id)), buoc))


def thuc_hien_buoc(conn, lan_chay_id, buoc, giu_viec, dau_ra, *, ghi, cong_bo=None):
    """Core gọi callbacks đã kiểm contract; không callback nào đến từ định nghĩa.

    ghi(conn) trả UUID kết quả hoặc None; cong_bo(conn, UUID) tùy chọn.
    Mọi exception phải thoát tx để rollback cả callback và trạng thái việc.
    Nếu đã dừng trước callback, trả trạng thái để caller commit DA_DUNG ngay.
    Nếu dừng sau callback, QUY_TRINH_DA_DUNG buộc rollback nghiệp vụ; worker
    gọi lại bằng tx mới để kết thúc DA_DUNG mà không chờ lease hết hạn.
    """
    _json(dau_ra)
    r = kiem_ghi(conn, lan_chay_id, buoc, giu_viec)
    if r['trang_thai'] != 'DANG_CHAY':
        return r
    ket_qua_id = ghi(conn)
    if cong_bo is not None:
        r = kiem_ghi(conn, lan_chay_id, buoc, giu_viec)
        if r['trang_thai'] != 'DANG_CHAY':
            # Caller phai rollback ghi nghiep vu; sau rollback goi tien de luu dung/audit.
            raise LoiQuyTrinh('QUY_TRINH_DA_DUNG' if r['trang_thai'].startswith('DUNG_') else 'QUY_TRINH_PHIEN')
        cong_bo(conn, ket_qua_id)
    r = hoan_tat(conn, lan_chay_id, buoc, giu_viec, dau_ra, ket_qua_id=ket_qua_id)
    if r['trang_thai'] != 'DANG_CHAY':
        raise LoiQuyTrinh('QUY_TRINH_DA_DUNG' if r['trang_thai'].startswith('DUNG_') else 'QUY_TRINH_PHIEN')
    return r
