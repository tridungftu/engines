"""G2-32-E2: router theo pins Core, dùng registry/hồ sơ/KT và hàng việc cũ.

Composition root dựng một router cho bộ pins và GhimLoaiViec đã kiểm; mỗi
(module, loai, phien_ban) chỉ thuộc một capability/contract cố định, kể cả qua
các lần khởi động nhờ hàng việc kiểm lại binding. Đổi binding phải đăng ký loại
hoặc phiên bản việc mới. Cung cấp
ho_so_runtime(ghim) -> (TienTrinhCore, thông điệp san_sang) và
doc_kt(conn, ghim) -> snapshot KetQuaKiem tin cậy. Không nhận các provider này
từ module/HTTP. Router không spawn, connect, commit hay tự chọn engine khác.
UUID việc trả về còn thuộc transaction caller; boundary chỉ trả 202 sau commit.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from datetime import datetime, timezone
from functools import wraps
import re
from types import MappingProxyType
from uuid import UUID

from . import dang_ky, ho_so_chay, so_cong, viec
from .http import LoiHTTP
from .tien_trinh import TienTrinhCore, LoiTienTrinh
from .tiep_nhan import _tx
from ..sdk_core.ngu_canh import _xoa_loi


class LoiDichVuEngine(RuntimeError):
    def __init__(self, ma='ENGINE_CHUA_SAN_SANG', http_status=503):
        self.ma, self.http_status = ma, http_status
        self.headers = {'Retry-After': '2'} if http_status == 503 else {}
        super().__init__(ma)


def _an_loi(ham):
    @wraps(ham)
    def boc(*args, **kwargs):
        ma, status = 'ENGINE_CHUA_SAN_SANG', 503
        try:
            return ham(*args, **kwargs)
        except Exception as exc:
            if isinstance(exc, LoiDichVuEngine):
                ma, status = exc.ma, exc.http_status
            elif isinstance(exc, viec.LoiViec):
                ma, status = exc.ma, exc.http_status
            elif ((isinstance(exc, LoiTienTrinh)
                    and exc.ma == 'TIEN_TRINH_KHONG_HOP_LE')
                    or (isinstance(exc, LoiHTTP) and exc.status == 503)
                    or (isinstance(exc, so_cong.LoiSoCong)
                        and exc.ma in {'CONG_MAT_LEASE', 'CONG_KHONG_THAY', 'CONG_CAN_DOI_CHIEU'})
                    or (isinstance(exc, ho_so_chay.LoiHoSoChay)
                        and exc.ma == 'HO_SO_CHAY_KHONG_THAY')):
                pass
            else:
                # Giữ loại lỗi để boundary xử lý lỗi lập trình/kết nối; ẩn raw secret.
                _xoa_loi(exc)
                raise
            _xoa_loi(exc)
        finally:
            args = kwargs = None
        raise LoiDichVuEngine(ma, status) from None
    return boc


def _can(dieu_kien):
    if not dieu_kien:
        raise LoiDichVuEngine()


def _ban(value):
    # So sánh chính xác; không nhận range, wildcard, latest hoặc chuỗi rỗng.
    if not isinstance(value, str) or not re.fullmatch(r'[0-9][0-9A-Za-z_.+\-]{0,63}', value):
        raise ValueError('Cần phiên bản cố định')


@dataclass(frozen=True)
class GhimContract:
    ma: str
    phien_ban: str
    ma_bam: str

    def __post_init__(self):
        if not isinstance(self.ma, str) or not re.fullmatch(r'[a-z][a-z0-9_.]{0,95}', self.ma):
            raise ValueError('Mã contract không hợp lệ')
        _ban(self.phien_ban)
        if not isinstance(self.ma_bam, str) or not re.fullmatch('[0-9a-f]{64}', self.ma_bam):
            raise ValueError('Cần SHA256 contract')


@dataclass(frozen=True)
class GhimEngine:
    capability: str
    engine_id: UUID
    ma_engine: str
    phien_ban_engine: str
    ma_bam_goi: str
    ma_adapter: str
    phien_ban_adapter: str
    dau_vao: GhimContract
    dau_ra: GhimContract
    ho_so_mau_id: UUID
    row_version: str
    ma_bam_schema: str

    def __post_init__(self):
        if (not isinstance(self.capability, str)
                or not re.fullmatch(r'[a-z][a-z0-9_.]*@[1-9][0-9]*', self.capability)
                or not isinstance(self.engine_id, UUID) or not isinstance(self.ho_so_mau_id, UUID)
                or not isinstance(self.ma_engine, str)
                or not re.fullmatch('[a-z][a-z0-9_]{0,30}', self.ma_engine)
                or not isinstance(self.ma_adapter, str)
                or not re.fullmatch('[a-z][a-z0-9_]{0,62}', self.ma_adapter)
                or not isinstance(self.dau_vao, GhimContract)
                or not isinstance(self.dau_ra, GhimContract)):
            raise ValueError('Pins engine không hợp lệ')
        _ban(self.phien_ban_engine)
        _ban(self.phien_ban_adapter)
        try:
            ho_so_chay._ban(self.row_version)
        except ho_so_chay.LoiHoSoChay:
            raise ValueError('Cần row_version hồ sơ cố định') from None
        for bam in (self.ma_bam_goi, self.ma_bam_schema):
            if not isinstance(bam, str) or not re.fullmatch('[0-9a-f]{64}', bam):
                raise ValueError('Cần SHA256 đã ghim')


class DichVuEngine:
    def __init__(self, ghim, *, loai_viec, ho_so_runtime, doc_kt, doc_hoi_ai=None):
        pins = tuple(ghim)
        if (not pins or any(not isinstance(p, GhimEngine) for p in pins)
                or len({p.capability for p in pins}) != len(pins)
                or not callable(ho_so_runtime) or not callable(doc_kt)
                or (doc_hoi_ai is not None and not callable(doc_hoi_ai))):
            raise ValueError('Cần pins duy nhất và provider Core')
        self._ghim = MappingProxyType({p.capability: p for p in pins})
        bindings = tuple(loai_viec)
        if (not bindings or any(not isinstance(g, viec.GhimLoaiViec) for g in bindings)
                or len({(g.module, g.loai, g.phien_ban) for g in bindings}) != len(bindings)
                or {g.capability for g in bindings} != set(self._ghim)):
            raise ValueError('Cần ghim loại việc duy nhất cho từng năng lực')
        for g in bindings:
            p = self._ghim[g.capability]
            if (g.engine_id, g.ma_contract, g.phien_ban_contract) != (
                    p.engine_id, p.dau_ra.ma, p.dau_ra.phien_ban):
                raise ValueError('Loại việc không khớp năng lực đã ghim')
        self._loai_viec = MappingProxyType({(g.module, g.loai, g.phien_ban): g for g in bindings})
        self._ho_so_runtime, self._doc_kt = ho_so_runtime, doc_kt
        # Chỉ composition root cấp. Provider đọc khai báo của gói đã cài,
        # trả (SHA256 gói, khai báo) với đúng bốn trường hoi_ai.v2 dưới đây.
        # Manifest hiện chưa có nơi khai prompt; không suy function từ adapter,
        # không tự tạo định dạng gói. Chưa nối provider thì đóng bước Hỏi AI.
        self._doc_hoi_ai = doc_hoi_ai
        self._schema_hoi_ai = None

    def nguon_hoi_ai(self, conn, *, ghim, giu, dau_vao, phien_ban_module):
        """Xác minh bước chuỗi trước khi trả văn bản cho engine, trong tx ngắn.

        doc_hoi_ai(conn, module=..., phien_ban_module=..., ma_function=...,
        ma_prompt=..., phien_ban_prompt=...) là provider tin cậy của Core,
        không nhận từ request/module/engine. Khai báo gồm ma_function,
        ma_prompt, phien_ban_prompt, chi_dan; SHA gói phải khớp registry.
        """
        from .dispatcher import KiemSchema
        from ..sdk_core import kenh_khung as k
        k._can(self._loai_viec.get((ghim.module, ghim.loai, ghim.phien_ban)) == ghim
            and giu.module == ghim.module and callable(self._doc_hoi_ai), 'KENH_KHONG_DU_QUYEN')
        p = self._chon(ghim.capability)
        k._can((p.ma_engine, p.capability, p.dau_vao.ma, p.dau_vao.phien_ban,
                p.dau_ra.ma, p.dau_ra.phien_ban, p.engine_id) ==
            ('e_hoi_ai', 'ai.hoi@1', 'hoi_ai.v2', '2.0.0',
             'tra_loi_ai.v2', '2.0.0', ghim.engine_id), 'KENH_KHONG_DU_QUYEN')
        self._doi_chieu(conn, p)
        if (ghim.module, ghim.loai) == ('core', 'CHAY_THU_HOI_AI'):
            return self._nguon_hoi_ai_thu(conn, giu, ghim)
        data = deepcopy(dau_vao)
        k._can(isinstance(data, dict) and set(data) == {
            'yeu_cau', 'nguon_core', 'du_lieu_ket_qua', 'revision_tep_truoc'},
            'KENH_DU_LIEU_KHONG_HOP_LE')
        if self._schema_hoi_ai is None:
            self._schema_hoi_ai = KiemSchema()
        ref = 'urn:ktt:contract:hoi_ai.v2'
        yc, nguon = data['yeu_cau'], data['nguon_core']
        k._can(self._schema_hoi_ai.kiem({'$ref': ref}, yc)
            and self._schema_hoi_ai.kiem({'$ref': ref + '#/$defs/nguon_core'}, nguon),
            'KENH_DU_LIEU_KHONG_HOP_LE')
        fields = ('ma_function', 'ma_prompt', 'phien_ban_prompt')
        k._can((nguon['ma_module'], nguon['phap_nhan_id'], nguon['viec_id']) ==
            (giu.module, str(giu.phap_nhan_id), str(giu.viec_id))
            and all(yc[key] == nguon[key] for key in fields), 'KENH_KHONG_DU_QUYEN')
        rows = dang_ky.doc_dang_ky(conn, loai='phien_ban_module', ma=giu.module)
        rows = [r for r in rows if r['module'] == giu.module
                and r['so_phien_ban'] == phien_ban_module and r['trang_thai'] == 'da_cai']
        k._can(len(rows) == 1, 'KENH_KHONG_DU_QUYEN')
        bam, khai_bao = self._doc_hoi_ai(conn, module=giu.module,
            phien_ban_module=phien_ban_module, **{key: yc[key] for key in fields})
        k._can(isinstance(bam, str) and re.fullmatch('[0-9a-f]{64}', bam)
            and bam == rows[0]['ma_bam_goi'] and isinstance(khai_bao, dict)
            and set(khai_bao) == {*fields, 'chi_dan'}
            and all(khai_bao[key] == yc[key] for key in (*fields, 'chi_dan')),
            'KENH_KHONG_DU_QUYEN')
        # Core dựng lại danh tính và metadata prompt từ binding đã đối chiếu.
        data['nguon_core'] = {**nguon, 'ma_module': giu.module,
            'phap_nhan_id': str(giu.phap_nhan_id), 'viec_id': str(giu.viec_id),
            **{key: khai_bao[key] for key in fields}}
        return data

    def _nguon_hoi_ai_thu(self, conn, giu, ghim):
        """Nguồn tạm của Core, cùng contract/provider gói của bước Hỏi AI."""
        from ..sdk_core import kenh_khung as k
        from .dispatcher import KiemSchema
        k._can((ghim.phien_ban, ghim.phien_ban_contract, giu.hanh_dong) ==
            (1, '2.0.0', 'CORE:DU_LIEU:LAP'), 'KENH_KHONG_DU_QUYEN')
        row = viec._goi(conn, 'SELECT loi.ai_chay_thu_dau_vao(%s,%s,%s,%s,%s) AS r',
            (giu.ma.lay_de_truyen(), giu.phap_nhan_id, giu.viec_id, giu.instance_id, giu.the_he))
        inp, module = row['dau_vao'], row['ma_module']
        fields = ('ma_function', 'ma_prompt', 'phien_ban_prompt')
        expected = dict(ma_function=row['ma_function'], ma_prompt=inp['ma_prompt'],
                        phien_ban_prompt=inp['phien_ban_prompt'])
        rows = [r for r in dang_ky.doc_dang_ky(conn, loai='phien_ban_module', ma=module)
                if r['module'] == module and r['trang_thai'] == 'da_cai'
                and r['so_phien_ban'] == inp['phien_ban_module']]
        k._can(len(rows) == 1 and rows[0]['ma_bam_goi'] == inp['ma_bam_goi'], 'KENH_KHONG_DU_QUYEN')
        digest, prompt = self._doc_hoi_ai(conn, module=module,
            phien_ban_module=inp['phien_ban_module'], **expected)
        k._can(digest == inp['ma_bam_goi'] and isinstance(prompt, dict)
            and set(prompt) == {*fields, 'chi_dan'}
            and all(prompt[key] == expected[key] for key in fields), 'KENH_KHONG_DU_QUYEN')
        # hoi_ai.v2 chưa có trường câu hỏi riêng: đưa vào dữ liệu, giữ nguyên chỉ dẫn.
        text, question = (inp[key].replace('\r\n', '\n') for key in ('tai_lieu', 'cau_hoi'))
        yc = dict(loai_viec='CHAY_THU', van_ban=text + ' Câu hỏi: ' + question,
                  **prompt, truong=['tra_loi'], chi_cuc_bo=True)
        ref = str(UUID(row['id']))
        source = dict(ma_module=module, **expected, phap_nhan_id=str(giu.phap_nhan_id),
            viec_id=str(giu.viec_id), revision=1, nguon_tep_ids=[ref],
            vi_tri=dict(tep_id=ref, dinh_vi='Nội dung chạy thử DEMO'))
        if self._schema_hoi_ai is None:
            self._schema_hoi_ai = KiemSchema()
        k._can(self._schema_hoi_ai.kiem({'$ref': 'urn:ktt:contract:hoi_ai.v2'}, yc)
            and self._schema_hoi_ai.kiem({'$ref': 'urn:ktt:contract:hoi_ai.v2#/$defs/nguon_core'}, source),
            'KENH_DU_LIEU_KHONG_HOP_LE')
        return dict(yeu_cau=yc, nguon_core=source, revision_tep_truoc=0,
            du_lieu_ket_qua=dict(bien_the='ocr', ma_contract='tra_loi_ai.v2', phien_ban_contract='2.0.0',
                trang_thai='thanh_cong', ly_do=None, revision_truoc=0, nguon=[]))

    def _chon(self, capability):
        if not isinstance(capability, str) or capability not in self._ghim:
            raise LoiDichVuEngine('ENGINE_CHUA_GHIM', 503)
        return self._ghim[capability]

    def _doi_chieu(self, conn, p):
        from .ung_dung import _kiem_kt_module
        rows = dang_ky.doc_dang_ky(conn, loai='engine', ma=p.ma_engine)
        rows = [r for r in rows if str(r['id']) == str(p.engine_id)]
        _can(len(rows) == 1)
        row = rows[0]
        _can((row['ma'], row['so_phien_ban'], row['ma_bam_goi'],
              row['ma_adapter'], row['phien_ban_adapter']) ==
             (p.ma_engine, p.phien_ban_engine, p.ma_bam_goi,
              p.ma_adapter, p.phien_ban_adapter))
        caps = [c for c in row['nang_luc'] if c['ma'] == p.capability]
        _can(len(caps) == 1 and caps[0]['dau_vao'] == p.dau_vao.ma
             and caps[0]['dau_ra'] == p.dau_ra.ma)
        for pin in (p.dau_vao, p.dau_ra):
            contracts = dang_ky.doc_dang_ky(conn, loai='contract', ma=pin.ma)
            found = [c for c in contracts if c['phien_ban'] == pin.phien_ban]
            _can(len(found) == 1 and found[0]['ma'] == pin.ma
                 and found[0]['ma_bam'] == pin.ma_bam
                 and found[0]['trang_thai'] == 'dang_dung')
        profile = ho_so_chay.bootstrap(conn, p.ma_engine, p.row_version)
        _can(profile['row_version'] == p.row_version
             and profile['ho_so_mau_id'] == str(p.ho_so_mau_id)
             and profile['phien_ban_engine'] == p.phien_ban_engine
             and profile['ma_bam_schema'] == p.ma_bam_schema)
        _kiem_kt_module(self._doc_kt(conn, p), doi_tuong=p.ma_engine, phien_ban=p.phien_ban_engine)

    def _san_sang(self, conn, p, controller, message):
        _can(controller.trang_thai == 'ready' and controller.chu_accept == 'con'
             and controller._phien_ban == p.phien_ban_engine
             and controller._module == p.ma_engine
             and p.dau_ra.ma in controller._contracts
             and controller._proc is not None
             and not getattr(getattr(controller, '_vong_doi', None), 'dang_dung', False))
        dong = so_cong.doc(conn, controller.id)
        _can(dong['module'] is None and dong['engine_ho_so_id'] == str(p.ho_so_mau_id)
             and dong['giu_boi'] == str(controller.instance_id)
             and type(dong['the_he']) is int and dong['the_he'] == controller.the_he
             and dong['trang_thai'] == 'CON_GIU' and dong.get('het_hieu_luc_luc') is None
             and dong['dia_chi_nghe'] in ('127.0.0.1', '::1')
             and type(dong['cong']) is int and 1024 <= dong['cong'] <= 65535)
        try:
            den = datetime.fromisoformat(str(dong['giu_den']))
        except ValueError:
            raise LoiDichVuEngine() from None
        _can(den.tzinfo is not None and den > datetime.now(timezone.utc))
        # Dùng nguyên bộ kiểm PID/lần tạo/nonce/instance/thế hệ/version/contract.
        controller._kiem_san_sang(message, dong)

    @staticmethod
    def _metadata(p):
        return dict(capability=p.capability, engine_id=str(p.engine_id), ma_engine=p.ma_engine,
            phien_ban_engine=p.phien_ban_engine,
            adapter=dict(ma=p.ma_adapter, phien_ban=p.phien_ban_adapter),
            dau_vao=dict(ma=p.dau_vao.ma, phien_ban=p.dau_vao.phien_ban),
            dau_ra=dict(ma=p.dau_ra.ma, phien_ban=p.dau_ra.phien_ban))

    def _thuc_hien(self, conn, capability, ham, *, can_controller=False):
        try:
            _tx(conn)
        except ValueError:
            raise LoiDichVuEngine('ENGINE_CAN_TRANSACTION', 400) from None
        p = self._chon(capability)
        controller, message = self._ho_so_runtime(p)
        _can(isinstance(controller, TienTrinhCore))
        with controller.khoa:
            self._doi_chieu(conn, p)
            self._san_sang(conn, p, controller, message)
            return ham(p, controller) if can_controller else ham(p)

    @_an_loi
    def kha_nang(self, conn, capability):
        return self._thuc_hien(conn, capability, self._metadata)

    @_an_loi
    def liet_ke(self, conn):
        return [self.kha_nang(conn, cap) for cap in sorted(self._ghim)]

    @_an_loi
    def gui_viec(self, conn, capability, *, loai, phien_ban, khoa_dedupe,
                 tham_chieu_id, bang_tham_chieu, co_tac_dong_ngoai=False,
                 thu_lai_an_toan=False, toi_da_lan_thu=3, thu_lai_giay=60,
                 giu_ngay=None, **ctx):
        """SQL hàng việc kiểm lại phiên/MTQ/công tắc/loại việc/dedupe, cùng tx.

        Không nhận engine_id/adapter/contract override từ caller. Tham chiếu
        đầu vào do provider HangViecCore E1 phân giải, không dựng kho/hàng mới.
        """
        if set(ctx) - {'ma', 'module', 'phap_nhan_id', 'hanh_dong'}:
            raise LoiDichVuEngine('ENGINE_DAU_VAO', 400)

        def tao(p):
            try:
                g = self._loai_viec.get((ctx.get('module'), loai, phien_ban))
                if type(phien_ban) is not int or g is None or g.capability != p.capability:
                    raise LoiDichVuEngine('ENGINE_LOAI_VIEC_KHONG_KHOP', 400)
                return viec.tao_viec(conn,
                    loai=loai, phien_ban=phien_ban, khoa_dedupe=khoa_dedupe,
                    tham_chieu_id=tham_chieu_id, bang_tham_chieu=bang_tham_chieu,
                    engine_id=p.engine_id, phien_ban_contract=p.dau_ra.phien_ban,
                    capability=p.capability, ma_contract=p.dau_ra.ma, ghim_loai_viec=g,
                    co_tac_dong_ngoai=co_tac_dong_ngoai, thu_lai_an_toan=thu_lai_an_toan,
                    toi_da_lan_thu=toi_da_lan_thu, thu_lai_giay=thu_lai_giay,
                    giu_ngay=giu_ngay, **ctx)
            except (TypeError, ValueError):
                raise LoiDichVuEngine('ENGINE_DAU_VAO', 400) from None

        return self._thuc_hien(conn, capability, tao)

    @_an_loi
    def nhan_viec(self, conn, capability, *, loai, phien_ban, lease_giay=120,
                  instance_id=None, **ctx):
        """Provider Core cho HangViecCore E1; caller giữ transaction/commit.

        instance_id do worker Core cấp phải là instance đang ready của pins;
        không được kéo hộ instance khác hoặc instance trước lần khởi động lại.
        """
        if set(ctx) - {'ma', 'module', 'phap_nhan_id', 'hanh_dong'}:
            raise LoiDichVuEngine('ENGINE_DAU_VAO', 400)

        def nhan(p, controller):
            g = self._loai_viec.get((ctx.get('module'), loai, phien_ban))
            if type(phien_ban) is not int or g is None or g.capability != p.capability:
                raise LoiDichVuEngine('ENGINE_LOAI_VIEC_KHONG_KHOP', 400)
            try:
                _can(instance_id is None or UUID(str(instance_id)) == controller.instance_id)
                return viec.nhan_engine(conn, controller.instance_id,
                    ghim_loai_viec=g, lease_giay=lease_giay, **ctx)
            except (TypeError, ValueError):
                raise LoiDichVuEngine('ENGINE_DAU_VAO', 400) from None

        return self._thuc_hien(conn, capability, nhan, can_controller=True)
