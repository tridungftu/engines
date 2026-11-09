"""CE-2: biên dịch và ghim khai báo chuỗi engine (`urn:ktt:manifest:chuoi.v1`).

Module chỉ khai tên bước, capability và ánh xạ; Core biên dịch thành định nghĩa
quy trình mà runner G2-28/CE-1 (migration 105) chạy được, ghim engine/adapter/
contract từ registry Core và băm kết quả. Không SQL, không mở kết nối, không
chạy mã từ khai báo, không tự cấp quyền. Dữ liệu ví dụ/test chỉ DEMO.

Bước Cloud chỉ được đọc đầu ra của bước che (Mask); không nhận đầu ra chưa che như kết quả trích (chặt hơn dự thảo B2, theo TL 48; lead chấp nhận).

Mã băm: `ma_bam_ghim` (CE-2, băm JSON chuẩn hóa gồm cả ghim engine/contract) là mã
khác với `ma_bam` do SQL `loi.quy_trinh_dang_ky` tự tính trên jsonb; không so sánh trực tiếp.

Chưa làm (để sau):
- `thu_lai_an_toan`/`co_tac_dong_ngoai` hiện suy từ `ra_cloud`; cần trường "tác động ngoài"
  trong registry engine.
- `khi` của bước Cloud chưa xét trường hợp trỏ bước `sau_neu_co`; nhận diện Mask còn theo
  tiền tố `mask.` chứ chưa theo engine; ví dụ B2 của dự thảo cần sửa tài liệu cho khớp.

Thuần: `bien_dich` không chạm CSDL. `dang_ky` chỉ gọi (1) hàm đăng ký loại việc
do Core truyền vào và (2) `quy_trinh.dang_ky` hiện có.
"""

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import re

from . import goi, quy_trinh

LUOC_DO = 'urn:ktt:manifest:chuoi.v1'
_MA_CHUOI = re.compile(r'chuoi_[a-z][a-z0-9_]{0,72}')
_MA_BUOC = re.compile(r'[a-z][a-z0-9_]{0,39}')
_PHIEN_BAN = re.compile(r'[1-9][0-9]{0,8}')
_GOC_MASK = 'mask.'
_CON_SOT = ('kiem_tra', 'con_sot')


class LoiChuoi(ValueError):
    """Mã lỗi cố định + thông điệp nghiệp vụ trung tính; không chứa giá trị khai báo."""

    def __init__(self, ma, thong_diep):
        self.ma = ma
        self.thong_diep = thong_diep
        super().__init__(f'{thong_diep} ({ma})')


MA_LOI = {
    'CHUOI_JSON': 'Tệp khai báo chuỗi không đọc được hoặc có khóa trùng.',
    'CHUOI_LUOC_DO': 'Khai báo chuỗi không đúng lược đồ chuỗi xử lý.',
    'CHUOI_MA_SAI': 'Mã chuỗi, phiên bản hoặc module không hợp lệ.',
    'CHUOI_MA_TRUNG': 'Có hai bước trùng mã.',
    'CHUOI_PHU_THUOC_LA': 'Bước phụ thuộc vào bước không tồn tại, vào chính nó hoặc khai trùng.',
    'CHUOI_VONG': 'Các bước phụ thuộc lẫn nhau thành vòng.',
    'CHUOI_KET_QUA_SAI': 'Bước kết quả cuối hoặc bước bổ sung không tồn tại.',
    'CHUOI_POINTER_SAI': 'Nguồn dữ liệu của bước chỉ được lấy từ đầu vào chuỗi hoặc kết quả bước đã khai phụ thuộc.',
    'CHUOI_ENGINE_KHONG_CO': 'Bước dùng năng lực engine chưa được module khai hoặc chưa có trong danh mục engine của Core.',
    'CHUOI_RA_CLOUD_THIEU': 'Bước đưa dữ liệu ra Cloud phải khai rõ và phải đi sau bước che định danh.',
    'CHUOI_RA_CLOUD_SAI': 'Khai báo đưa dữ liệu ra Cloud không đạt điều kiện an toàn.',
    'CHUOI_BIEN_DICH': 'Chuỗi không biên dịch được thành quy trình chạy.',
    'CHUOI_DANG_KY': 'Không đăng ký được loại việc hoặc quy trình của chuỗi.',
}


def _loi(ma, chi_tiet=None):
    thong_diep = MA_LOI[ma]
    return LoiChuoi(ma, thong_diep + (' ' + chi_tiet if chi_tiet else ''))


def _json_chuan(du_lieu):
    return json.dumps(du_lieu, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def ma_bam_json(du_lieu):
    return hashlib.sha256(_json_chuan(du_lieu).encode('utf-8')).hexdigest()


@lru_cache(maxsize=1)
def _kiem_luoc_do():
    validator, checker, registry, _resource, schemas = goi.dung_registry_schema()
    return validator(schemas[LUOC_DO], registry=registry, format_checker=checker)


def doc_chuoi(raw):
    """Đọc bytes JSON bằng bộ đọc gói (từ chối khóa trùng, số không hữu hạn, quá sâu)."""
    try:
        return goi.doc_json(raw, goi.GioiHan())
    except goi.LoiGoi:
        raise _loi('CHUOI_JSON') from None


def kiem_luoc_do(doc):
    """Chỉ kiểm cấu trúc theo `chuoi.v1`; khóa lạ, thiếu, sai kiểu → CHUOI_LUOC_DO."""
    loi = next(iter(sorted(_kiem_luoc_do().iter_errors(doc), key=lambda e: list(map(str, e.path)))), None)
    if loi is not None:
        # Chỉ nêu vị trí, không in giá trị khai báo.
        vi_tri = '/' + '/'.join(str(p) for p in loi.absolute_path)
        raise _loi('CHUOI_LUOC_DO', f'Vị trí: {vi_tri}.')
    # Lược đồ giữ từ khóa tối thiểu của bộ kiểm dự phòng (G2-17): mẫu tên khóa kiểm ở đây.
    if 'co' in doc['dau_vao']:  # trùng vùng /dau_vao/co/<cờ> do Core chụp
        raise _loi('CHUOI_LUOC_DO', 'Vị trí: /dau_vao/co.')
    nhom = [('/dau_vao', doc['dau_vao'])] + [(f'/buoc/{i}/vao', b['vao']) for i, b in enumerate(doc['buoc'])]
    for vi_tri, muc in nhom:
        if (vi_tri == '/dau_vao' and not muc) or len(muc) > 32 or any(
                not _MA_BUOC.fullmatch(k) for k in muc):
            raise _loi('CHUOI_LUOC_DO', f'Vị trí: {vi_tri}.')
    return doc


@dataclass(frozen=True)
class LoaiViecChuoi:
    loai: str
    phien_ban: int
    engine_id: str
    capability: str
    buoc: str


@dataclass(frozen=True)
class ChuoiDaBienDich:
    ma: str
    phien_ban: int
    module: str
    phien_ban_module: str
    ten_hien_thi: str
    buoc: tuple          # định nghĩa runner, đúng khóa mà quy_trinh.kiem_dinh nhận
    loai_viec: tuple
    ghim_buoc: tuple     # {ma, capability, engine, ma_bam_goi, ma_bam_schema, contract_vao}
    dau_vao: dict
    co: tuple
    ket_qua_cuoi: str
    bo_sung: tuple
    thoi_han_giay: object
    ma_bam_ghim: str

    def dinh_nghia_runner(self):
        """Bản sao sâu để caller không sửa được bản đã ghim."""
        return json.loads(_json_chuan(list(self.buoc)))


def _so_phien_ban(phien_ban):
    if isinstance(phien_ban, bool) or not isinstance(phien_ban, (int, str)) \
            or not _PHIEN_BAN.fullmatch(str(phien_ban)):
        raise _loi('CHUOI_MA_SAI')
    return int(phien_ban)


def _tach(duong):
    try:
        return quy_trinh._duong(duong)
    except ValueError:
        raise _loi('CHUOI_POINTER_SAI') from None


def _kiem_phu_thuoc(buoc_khai):
    ma = [b['ma'] for b in buoc_khai]
    if len(set(ma)) != len(ma):
        raise _loi('CHUOI_MA_TRUNG')
    ten = set(ma)
    phu = {}
    for b in buoc_khai:
        cung, mem = b.get('sau', []), b.get('sau_neu_co', [])
        if (b['ma'] in cung or b['ma'] in mem or set(cung) & set(mem)
                or not (set(cung) | set(mem)) <= ten):
            raise _loi('CHUOI_PHU_THUOC_LA', f'Bước: {b["ma"]}.')
        phu[b['ma']] = set(cung) | set(mem)
    xong = set()
    while len(xong) < len(ma):
        san_sang = {m for m in ma if m not in xong and phu[m] <= xong}
        if not san_sang:
            raise _loi('CHUOI_VONG')
        xong |= san_sang
    return phu


def _kiem_pointer(duong, b, doc, phu):
    p = _tach(duong)
    if len(p) < 2 or p[0] not in ('dau_vao', 'buoc'):
        raise _loi('CHUOI_POINTER_SAI', f'Bước: {b["ma"]}.')
    if p[0] == 'buoc':
        if len(p) < 3 or p[2] != 'dau_ra' or p[1] not in phu[b['ma']]:
            raise _loi('CHUOI_POINTER_SAI', f'Bước: {b["ma"]}.')
    elif p[1] == 'co':
        if len(p) != 3 or p[2] not in {c['ma'] for c in doc.get('co', [])}:
            raise _loi('CHUOI_POINTER_SAI', f'Bước: {b["ma"]}.')
    elif p[1] not in doc['dau_vao']:
        raise _loi('CHUOI_POINTER_SAI', f'Bước: {b["ma"]}.')


def _kiem_ra_cloud(doc, theo_ma, cloud_cap):
    co_mac_dinh = {c['ma']: c['mac_dinh'] for c in doc.get('co', [])}
    for b in doc['buoc']:
        la_mask = b['capability'].startswith(_GOC_MASK)
        khai = b.get('ra_cloud', False)
        if la_mask and khai:
            raise _loi('CHUOI_RA_CLOUD_SAI', f'Bước: {b["ma"]}.')
        if b['capability'].split('@')[0] in cloud_cap and not khai:
            raise _loi('CHUOI_RA_CLOUD_THIEU', f'Bước: {b["ma"]}.')
        if not khai:
            continue
        # Phụ thuộc cứng trực tiếp vào đúng một bước che định danh.
        mask = [m for m in b.get('sau', []) if theo_ma[m]['capability'].startswith(_GOC_MASK)]
        if len(mask) != 1 or 'khi' not in b:
            raise _loi('CHUOI_RA_CLOUD_THIEU', f'Bước: {b["ma"]}.')
        m = mask[0]
        khi = b['khi']
        if (set(khi) != {'duong', 'bang'} or khi['bang'] is not False
                or khi['duong'] != '/'.join(('', 'buoc', m, 'dau_ra') + _CON_SOT)):
            raise _loi('CHUOI_RA_CLOUD_SAI', f'Bước: {b["ma"]}.')
        # Cloud mặc định tắt: bước che chỉ chạy khi cờ bật tường minh, cờ mặc định false.
        khi_mask = theo_ma[m].get('khi')
        p = _tach(khi_mask['duong']) if khi_mask else []
        if (not khi_mask or khi_mask.get('bang') is not True or len(p) != 3
                or p[:2] != ['dau_vao', 'co'] or co_mac_dinh.get(p[2]) is not False):
            raise _loi('CHUOI_RA_CLOUD_SAI', f'Bước: {m}.')
        # Chỉ nhận nội dung đã che; không đọc đầu vào gốc hay kết quả bước chưa che.
        for nguon in b['vao'].values():
            for duong in nguon if isinstance(nguon, list) else [nguon]:
                q = _tach(duong)
                if q[:3] != ['buoc', m, 'dau_ra']:
                    raise _loi('CHUOI_RA_CLOUD_SAI', f'Bước: {b["ma"]}.')


def bien_dich(doc, *, ma, phien_ban, module, phien_ban_module, engine_dung, ghim,
              ra_cloud_capability):
    """Khai báo chuỗi → ChuoiDaBienDich.

    engine_dung: các capability module đã khai trong module.json.
    ghim: ánh xạ capability → GhimEngine (registry Core); không nhận engine,
    adapter, contract từ khai báo của module.
    ra_cloud_capability: capability (không số phiên bản) mà registry đánh dấu
    có dữ liệu rời máy; khai thiếu `ra_cloud` thì từ chối. BẮT BUỘC truyền (không mặc
    định rỗng) để không mở Cloud do quên.
    """
    if (not isinstance(ma, str) or not _MA_CHUOI.fullmatch(ma)
            or not isinstance(module, str) or not re.fullmatch(r'[a-z][a-z0-9_]{0,30}', module)
            or not isinstance(phien_ban_module, str) or not phien_ban_module):
        raise _loi('CHUOI_MA_SAI')
    so_pb = _so_phien_ban(phien_ban)
    kiem_luoc_do(doc)
    phu = _kiem_phu_thuoc(doc['buoc'])
    theo_ma = {b['ma']: b for b in doc['buoc']}
    for ten_buoc in [doc['ket_qua_cuoi'], *doc.get('bo_sung', [])]:
        if ten_buoc not in theo_ma:
            raise _loi('CHUOI_KET_QUA_SAI')
    _kiem_ra_cloud(doc, theo_ma, frozenset(ra_cloud_capability))
    for b in doc['buoc']:
        paths = [d for nguon in b['vao'].values() for d in (nguon if isinstance(nguon, list) else [nguon])]
        if 'khi' in b:
            paths.append(b['khi']['duong'])
        for duong in paths:
            _kiem_pointer(duong, b, doc, phu)
        if (b['capability'] not in set(engine_dung) or b['capability'] not in ghim
                or ghim[b['capability']].capability != b['capability']):
            raise _loi('CHUOI_ENGINE_KHONG_CO', f'Bước: {b["ma"]}.')

    ten_chuoi = ma[len('chuoi_'):].upper()
    buoc_rt, loai_viec, ghim_buoc = [], [], []
    for b in doc['buoc']:
        pin = ghim[b['capability']]
        loai = f'C-{ten_chuoi}-{b["ma"].upper()}'
        if not re.fullmatch(r'[A-Z][A-Z0-9_-]{0,79}', loai):
            raise _loi('CHUOI_MA_SAI', 'Tên loại việc quá dài.')
        eid = str(pin.engine_id)
        d = {'ma': b['ma'], 'phu_thuoc': sorted(b.get('sau', [])), 'loai': loai,
             'phien_ban': so_pb, 'capability': b['capability'], 'engine_id': eid,
             'adapter': {'ma': pin.ma_adapter, 'phien_ban': pin.phien_ban_adapter},
             'contract': {'ma': pin.dau_ra.ma, 'phien_ban': pin.dau_ra.phien_ban},
             'cho_duyet': False,
             'anh_xa': {k: (list(v) if isinstance(v, list) else v) for k, v in sorted(b['vao'].items())},
             'co_tac_dong_ngoai': bool(b.get('ra_cloud', False)),
             # Bước có tác động ngoài (Cloud) không tự thử lại; bước nội bộ thì an toàn.
             'thu_lai_an_toan': not b.get('ra_cloud', False)}
        if b.get('sau_neu_co'):
            d['phu_thuoc_neu_co'] = sorted(b['sau_neu_co'])
        if 'khi' in b:
            khi = b['khi']
            d['dieu_kien'] = ({'duong': khi['duong'], 'bang': khi['bang']} if 'bang' in khi
                              else {'duong': khi['duong'], 'trong': list(khi['trong'])})
        buoc_rt.append(d)
        loai_viec.append(LoaiViecChuoi(loai, so_pb, eid, b['capability'], b['ma']))
        ghim_buoc.append({'ma': b['ma'], 'capability': b['capability'], 'engine': eid,
                          'ma_bam_goi': pin.ma_bam_goi, 'ma_bam_schema': pin.ma_bam_schema,
                          'contract_vao': {'ma': pin.dau_vao.ma, 'phien_ban': pin.dau_vao.phien_ban,
                                           'ma_bam': pin.dau_vao.ma_bam},
                          'contract_ra': {'ma': pin.dau_ra.ma, 'phien_ban': pin.dau_ra.phien_ban,
                                          'ma_bam': pin.dau_ra.ma_bam}})
    try:
        quy_trinh.kiem_dinh(buoc_rt)
    except ValueError:
        raise _loi('CHUOI_BIEN_DICH') from None
    noi_dung = {'luoc_do': LUOC_DO, 'ma': ma, 'phien_ban': so_pb, 'module': module,
                'phien_ban_module': phien_ban_module, 'ten_hien_thi': doc['ten_hien_thi'],
                'dau_vao': doc['dau_vao'], 'co': doc.get('co', []), 'buoc': buoc_rt,
                'ghim_buoc': ghim_buoc, 'ket_qua_cuoi': doc['ket_qua_cuoi'],
                'bo_sung': sorted(doc.get('bo_sung', [])),
                'thoi_han_giay': doc.get('gioi_han', {}).get('thoi_han_giay')}
    return ChuoiDaBienDich(
        ma=ma, phien_ban=so_pb, module=module, phien_ban_module=phien_ban_module,
        ten_hien_thi=doc['ten_hien_thi'], buoc=tuple(buoc_rt), loai_viec=tuple(loai_viec),
        ghim_buoc=tuple(ghim_buoc), dau_vao=doc['dau_vao'], co=tuple(doc.get('co', [])),
        ket_qua_cuoi=doc['ket_qua_cuoi'], bo_sung=tuple(sorted(doc.get('bo_sung', []))),
        thoi_han_giay=noi_dung['thoi_han_giay'], ma_bam_ghim=ma_bam_json(noi_dung))


def dang_ky(conn, chuoi, *, dang_ky_loai, **ctx):
    """Đăng ký loại việc rồi quy trình đã biên dịch.

    dang_ky_loai(conn, module, loai, phien_ban, engine_id, **ctx) là hàm Core do
    caller truyền vào (hiện chưa có hàm Python nào ghi loi.dang_ky_loai_viec;
    xem báo cáo CE-2). Module không tự cấp quyền; quy_trinh.dang_ky vẫn do
    SQL kiểm Admin, contract, loại việc và engine.
    """
    if not isinstance(chuoi, ChuoiDaBienDich) or not callable(dang_ky_loai):
        raise _loi('CHUOI_DANG_KY')
    if ctx.get('module', chuoi.module) != chuoi.module:
        raise _loi('CHUOI_DANG_KY')
    ctx['module'] = chuoi.module
    # module truyền riêng ở vị trí thứ hai, không lặp trong **ctx.
    ctx_loai = {k: v for k, v in ctx.items() if k != 'module'}
    for l in chuoi.loai_viec:
        dang_ky_loai(conn, chuoi.module, l.loai, l.phien_ban, l.engine_id, **ctx_loai)
    return quy_trinh.dang_ky(conn, chuoi.ma, chuoi.phien_ban, chuoi.dinh_nghia_runner(),
                             phien_ban_module=chuoi.phien_ban_module, **ctx)
