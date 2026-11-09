"""Bước Hỏi AI Local qua hàng việc/lease và ACK của SDK hiện hành.

Core cấp kênh đã xác thực, schema offline, cấu hình và bộ ghi. Không mở
CSDL, đọc khóa từ đĩa/env hoặc gọi engine khác. DEMO phải bật tường minh.
"""

from __future__ import annotations

from dataclasses import asdict
from copy import deepcopy
from pathlib import Path
import io
import json
import re
import socket
import threading
import time

from ...sdk_core.bootstrap import Bootstrap, LoiBootstrap, PROTOCOL, gui_thong_diep
from ...sdk_core.engine import KenhCore, LoiEngine, SDKEngine
from ...sdk_core.ngu_canh import _xoa_loi
from . import bi_mat as bm
from .dto import KetQuaAI, TruongAI, YeuCauAI
from .hoi import AdapterHoiAI
from .lib import ai_cuc_bo
from .lib.cong_ai import CAI_DAT_MAC_DINH, CongAI, chon_model_local, kiem_prompt


GIOI_HAN_MANIFEST_BYTE = 64 * 1024


class LoiPhienBanGoi(LoiBootstrap):
    """Lỗi readiness hữu hạn; không đưa lỗi đọc/JSON của gói ra ngoài."""

    def __init__(self):
        super().__init__('Gói Hỏi AI hỏng phiên bản.')
        self.ma = 'AI_GOI_HONG_PHIEN_BAN'


def _doc_phien_ban():
    try:
        with Path(__file__).with_name('engine.json').open('rb') as luong:
            raw = luong.read(GIOI_HAN_MANIFEST_BYTE + 1)
        if len(raw) > GIOI_HAN_MANIFEST_BYTE:
            return None
        manifest = json.loads(raw.decode('utf-8'))
        version = manifest.get('phien_ban') if isinstance(manifest, dict) else None
        if (isinstance(version, str) and len(version) <= 100
                and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?'
                                 r'(?:\+[0-9A-Za-z.-]+)?', version)):
            return version
    except (OSError, ValueError, RecursionError):
        pass
    return None


# Manifest là nguồn duy nhất; gói hỏng vẫn import được để readiness báo lỗi.
PHIEN_BAN = _doc_phien_ban()
HAN_DRAIN_GIAY = 300
CHO_THU_LAI_TOI_DA_GIAY = 2.0
CAPABILITY = 'ai.hoi@1'
CONTRACTS = ['hoi_ai.v2', 'tra_loi_ai.v2']
HOI = 'urn:ktt:contract:hoi_ai.v2'
TRA_LOI = 'urn:ktt:contract:tra_loi_ai.v2'


class _MaskTat:
    """Chặn đường Mask ở bản chỉ Local; không đọc khóa hoặc che dữ liệu."""

    def co_khoa(self):
        return False

    def che(self, *args, **kwargs):
        raise RuntimeError('AI_CHI_LOCAL')

    mo_che = ket_thuc = che


def doc_cau_hinh_local(settings, *, kiem_schema):
    """Đọc đúng schema của gói; chỉ chuyển seam settings cũ trong RAM.

    Metadata discovery chưa có ở settings runtime cũ được phép thiếu khi
    đọc; không bịa loại phần mềm/thời điểm. Admin ghi vẫn kiểm đủ manifest.
    local_ai.models/quy_tac/dia_chi cũ phải lưu lại, không âm thầm bỏ qua.
    """
    try:
        if settings is None or settings == {}:
            return {}
        config = deepcopy(settings)
        with Path(__file__).with_name('engine.json').open('rb') as stream:
            raw = stream.read(GIOI_HAN_MANIFEST_BYTE + 1)
        if len(raw) > GIOI_HAN_MANIFEST_BYTE:
            raise ValueError()
        schema = json.loads(raw.decode('utf-8'))['cau_hinh_schema']
        # Envelope cổng cũ vẫn dùng cho seam bí mật; runtime luôn khóa Cloud.
        value = deepcopy(config)
        legacy = value.pop('cong_ai', None)
        if legacy is not None and (not isinstance(legacy, dict)
                                   or set(legacy) - set(CAI_DAT_MAC_DINH)):
            raise ValueError()
        schema['properties']['model_phat_hien']['items']['required'] = [
            'id_model', 'trang_thai', 'bat']
        if not kiem_schema(schema, value):
            raise ValueError()
        if 'local_ai' in value:
            local = value['local_ai']
            parsed = ai_cuc_bo._parse_url(local['url'])
            config['local_ai']['url'] = parsed.geturl()
        return config
    except Exception as exc:
        _xoa_loi(exc)
    raise LoiBootstrap('Cần lưu lại cấu hình máy AI cục bộ theo mẫu hiện hành trước khi tiếp tục.') from None


def _kiem_local(provider):
    cfg = ai_cuc_bo.local_ai_settings({'local_ai': provider.local_ai})
    if not cfg['enabled']:
        return False
    config = deepcopy(provider.cau_hinh_model)
    rules = config.get('quy_tac_model')
    if not isinstance(rules, list):
        return False
    result = ai_cuc_bo.discover_local_models({'local_ai': cfg})
    return any(chon_model_local(config, r.get('module'), r.get('function'), result)[2] is None
               for r in rules if isinstance(r, dict))


def _hoi_v2(dau_vao, *, provider, kiem_schema):
    """Tái dùng adapter/cổng đã có; v1 chỉ là dạng nội bộ của adapter cũ."""
    if not isinstance(provider, CongAI) or not callable(kiem_schema):
        raise TypeError('Cần cổng AI và bộ kiểm cấu trúc do hệ thống cấp.')
    if not isinstance(dau_vao, dict) or set(dau_vao) != {
            'yeu_cau', 'nguon_core', 'du_lieu_ket_qua', 'revision_tep_truoc'}:
        raise ValueError('Yêu cầu hỏi AI chưa hợp lệ.')
    yc, nguon = deepcopy(dau_vao['yeu_cau']), deepcopy(dau_vao['nguon_core'])
    kiem_prompt(yc.get('chi_dan') if isinstance(yc, dict) else None)
    if (not kiem_schema({'$ref': HOI}, yc)
            or not kiem_schema({'$ref': HOI + '#/$defs/nguon_core'}, nguon)
            or any(yc[key] != nguon[key] for key in (
                'ma_function', 'ma_prompt', 'phien_ban_prompt'))
            or nguon['vi_tri']['tep_id'] not in nguon['nguon_tep_ids']):
        raise ValueError('Nguồn yêu cầu hỏi AI chưa hợp lệ.')
    meta = dau_vao['du_lieu_ket_qua']
    if (not isinstance(meta, dict) or (meta.get('ma_contract'), meta.get('phien_ban_contract'))
            != ('tra_loi_ai.v2', '2.0.0')):
        raise ValueError('Cấu trúc kết quả hỏi AI chưa hợp lệ.')
    # Core trả nguồn qua SDK sau khi kiểm binding/quyền/lease. Adapter V2
    # dùng nguồn riêng này để chọn model; không lấy ngữ cảnh từ payload.
    out = AdapterHoiAI(provider, kiem_schema=kiem_schema).goi(yc, nguon_core=nguon)
    if not kiem_schema({'$ref': TRA_LOI}, out):
        raise ValueError('Kết quả hỏi AI chưa đạt cấu trúc đã công bố.')
    return out


class ProviderAIGia:
    """Echo DEMO xác định được; LOCAL dưới đây chỉ là nguồn giả lập."""

    def san_sang(self):
        return True

    def goi(self, yeu_cau):
        if not isinstance(yeu_cau, YeuCauAI):
            raise TypeError('Cần DTO YeuCauAI')
        if not isinstance(yeu_cau.van_ban, str) or len(yeu_cau.van_ban) > 16384:
            raise ValueError('Cần văn bản DEMO tối đa 16384 ký tự')
        truong = {ten: TruongAI(ten, yeu_cau.van_ban, yeu_cau.van_ban, 'LOCAL')
                  for ten in (yeu_cau.truong or ('van_ban_demo',))}
        return KetQuaAI(yeu_cau.loai_viec, 'VANG', truong, 'LOCAL',
                        'Kết quả DEMO từ provider giả, chưa được duyệt.',
                        ly_do=('GIA_LAP',))


def xu_ly_viec(sdk, *, provider, khi_loi_ban_giao=None, demo=False, kiem_schema=None):
    """Đọc đầu vào Core, chạy một lần, giữ cùng kết quả đến ACK/mất lease."""
    if not isinstance(sdk, SDKEngine):
        raise TypeError('Cần SDKEngine do Core cấp')
    dau_vao = sdk.doc_dau_vao()
    if demo:
        yeu_cau = dau_vao['yeu_cau_demo']
        if not isinstance(yeu_cau, YeuCauAI):
            raise TypeError('Cần DTO YeuCauAI')
        ket_qua = provider.goi(yeu_cau)
        if not isinstance(ket_qua, KetQuaAI):
            raise TypeError('Cần DTO KetQuaAI')
        ket_qua = asdict(ket_qua)
    else:
        ket_qua = _hoi_v2(dau_vao, provider=provider, kiem_schema=kiem_schema)
    raw = json.dumps(ket_qua, ensure_ascii=False, allow_nan=False).encode('utf-8')
    with io.BytesIO(raw) as luong:
        while True:
            luong.seek(0)
            try:
                ack = sdk.ghi_ket_qua(luong=luong, ten='ai-demo.json' if demo else 'tra-loi-ai.json',
                    du_lieu=dau_vao['du_lieu_ket_qua'],
                    revision_tep_truoc=dau_vao['revision_tep_truoc'])
                if not demo and (not isinstance(ack, dict) or ack.get('da_ban_giao') is not True):
                    raise LoiEngine()
                return ack
            except LoiEngine as exc:
                if exc.ma == 'VIEC_MAT_LEASE':
                    raise
                # Chưa có ACK: giữ cả bộ đệm và kênh, không chạy lại provider.
                _xoa_loi(exc)
                if khi_loi_ban_giao is not None:
                    khi_loi_ban_giao()
                time.sleep(0.1)


class _VongNhan:
    """Một worker tuần tự; ngừng nhận và drain cả lời gọi bàn giao Core.

    Không shutdown listener dùng chung với Core; không kill việc khi drain.
    """

    def __init__(self, bootstrap, nhan_viec, provider):
        self.bootstrap, self.nhan_viec, self.provider = bootstrap, nhan_viec, provider
        self.khoa = threading.Lock()
        self.dung = False
        self.loi = False
        self.loi_ban_giao = threading.Event()
        self.demo, self.kiem_schema = False, None
        self.worker = threading.Thread(target=self._chay, name='hoi-ai')

    def bat_dau(self):
        self.bootstrap.socket.settimeout(0.1)
        self.worker.start()

    def _chay(self):
        try:
            while True:
                with self.khoa:
                    if self.dung:
                        return
                try:
                    conn, _ = self.bootstrap.accept()
                except socket.timeout:
                    continue
                except LoiBootstrap as exc:
                    if exc.ma == 'CHUA_CO_QUYEN_ACCEPT':
                        return
                    raise
                with conn:
                    with self.khoa:
                        if self.dung:
                            return
                        # Đã đăng ký việc trước ngừng nhận: drain phải chờ.
                    conn.settimeout(5)
                    kenh = self.nhan_viec(conn, self.bootstrap.bo_doc)
                    # Việc đã nhận phải chờ Core ACK, kể cả khi đang drain.
                    conn.settimeout(None)
                    if self.demo:
                        xu_ly_viec(kenh, provider=self.provider, demo=True,
                                   khi_loi_ban_giao=self.loi_ban_giao.set)
                    else:
                        self._chay_kenh(kenh)
        except Exception as exc:
            _xoa_loi(exc)
            self.loi = True

    def _chay_kenh(self, kenh):
        if (not isinstance(kenh, KenhCore)
                or not callable(getattr(kenh, 'nhan_viec', None))
                or not callable(getattr(kenh, 'ket_thuc', None))):
            raise TypeError('Cần kênh hàng việc do hệ thống cấp.')
        while not self.dung:
            try:
                giu = kenh.nhan_viec()
            except LoiEngine as exc:
                thu_lai = getattr(exc, 'thu_lai_duoc', False)
                retry_after = getattr(exc, 'retry_after', None)
                _xoa_loi(exc)
                if not thu_lai:
                    # Chưa giữ lease nào: mất kênh chỉ kết thúc vòng nhận rảnh.
                    self.ngung_accept()
                    return
                cho = (min(CHO_THU_LAI_TOI_DA_GIAY, max(0.1, retry_after))
                       if type(retry_after) is int else 0.1)
                time.sleep(cho)
                continue
            if giu is None:
                time.sleep(0.1)
                continue
            sdk = SDKEngine(giu, kenh_core=kenh)
            dung, mat_lease = threading.Event(), threading.Event()

            def heartbeat():
                while not dung.wait(30):
                    try:
                        sdk.heartbeat()
                    except LoiEngine as exc:
                        if exc.ma == 'VIEC_MAT_LEASE':
                            mat_lease.set()
                            return
                        _xoa_loi(exc)

            worker = threading.Thread(target=heartbeat, name='ai-lease', daemon=True)
            try:
                sdk.heartbeat()
                worker.start()
                result = xu_ly_viec(sdk, provider=self.provider, kiem_schema=self.kiem_schema,
                                   khi_loi_ban_giao=self.loi_ban_giao.set)
                trang_thai, kid, ma = 'XONG', result['ket_qua_id'], None
            except Exception as exc:
                if getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE':
                    mat_lease.set()
                trang_thai, kid, ma = 'LOI', None, 'AI_XU_LY_LOI'
                _xoa_loi(exc)
            finally:
                dung.set()
                if worker.ident is not None:
                    worker.join()
            # ACK kết quả và ACK kết thúc là hai bước riêng, cả hai đều drain.
            while not mat_lease.is_set():
                try:
                    if kenh.ket_thuc(giu, trang_thai=trang_thai, ket_qua_id=kid, ma_loi=ma) is True:
                        break
                except LoiEngine as exc:
                    if exc.ma == 'VIEC_MAT_LEASE':
                        break
                    _xoa_loi(exc)
                self.loi_ban_giao.set()
                time.sleep(0.1)
                try:
                    sdk.heartbeat()
                except LoiEngine as exc:
                    if exc.ma == 'VIEC_MAT_LEASE':
                        break
                    _xoa_loi(exc)

    def ngung_accept(self):
        with self.khoa:
            self.dung = True

    def drain(self):
        while self.worker.is_alive():
            self.worker.join(0.1)
            if self.worker.is_alive() and self.loi_ban_giao.is_set():
                return False
        return not self.loi


def chay(*, kiem_chu_ky, nhan_viec, provider=None, settings=None,
         mask=None, bo_ghi=None, nha_cung_cap=None, local_transport=None,
         kiem_xac_suat=None, kiem_schema=None, demo=False, bootstrap=None):
    """Core tiêm settings/Mask/bộ ghi để chạy CongAI qua bí mật bootstrap.

    Thiếu cấu hình/model/bộ kiểm/bộ ghi không được báo readiness thật.
    demo=True là nhánh khung cũ tường minh, không công bố contract thật.
    """
    if not callable(kiem_chu_ky) or not callable(nhan_viec):
        raise TypeError('Cần bộ kiểm chữ ký và seam nhận việc của Core')
    if type(demo) is not bool:
        raise TypeError('Cần khai rõ chế độ chạy thử.')
    if not demo and (not callable(kiem_schema) or not all(
            callable(getattr(bo_ghi, ten, None)) for ten in ('ghi', 'thong_ke', 'da_ban_giao', 'thu_lai'))
                     or (provider is not None and not isinstance(provider, CongAI))):
        raise TypeError('Cần cổng AI, bộ kiểm cấu trúc và bộ ghi của hệ thống.')
    dung_cong = not demo
    if demo:
        provider = ProviderAIGia() if provider is None else provider
    settings = {} if settings is None else settings
    if bootstrap is not None and not isinstance(bootstrap, Bootstrap):
        raise TypeError('Cần kênh khởi động do hệ thống cấp.')
    vong = bi_mat = None
    bat_dau = False
    da_thu_hoi = False
    dung_cung = False

    def thu_hoi_bi_mat():
        nonlocal da_thu_hoi
        if bi_mat is not None and not da_thu_hoi:
            bi_mat.thu_hoi()
            da_thu_hoi = True

    def cho_drain():
        da_bao = False
        han = time.monotonic() + HAN_DRAIN_GIAY
        while not vong.drain():
            if not da_bao:
                gui_thong_diep(bootstrap._ra, {
                    'protocol': PROTOCOL, 'kieu': 'drain_chua_xong'})
                da_bao = True
            time.sleep(0.1)
        # Nhật ký không cần khóa AI: thu RAM ngay khi worker đã xong.
        thu_hoi_bi_mat()
        nhip_lui = 0.1
        # Worker xong chưa đủ: nhật ký vẫn có thể đang chờ ACK của Core.
        while bo_ghi is not None and not bo_ghi.da_ban_giao():
            if not da_bao and time.monotonic() >= han:
                gui_thong_diep(bootstrap._ra, {
                    'protocol': PROTOCOL, 'kieu': 'drain_chua_xong'})
                da_bao = True
            # Hạn chỉ để báo Core; giữ kênh và retry đến ACK hoặc dừng cứng.
            try:
                bo_ghi.thu_lai()
            except Exception as exc:
                # Giữ hàng đợi hiện có, không giữ lỗi seam có thể chứa bí mật.
                _xoa_loi(exc)
            if not bo_ghi.da_ban_giao():
                time.sleep(nhip_lui)
                nhip_lui = min(2.0, nhip_lui * 2)
        return True

    try:
        if bootstrap is None:
            bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky)
        if PHIEN_BAN is None:
            raise LoiPhienBanGoi()
        if dung_cong:
            settings = doc_cau_hinh_local(settings, kiem_schema=kiem_schema)
            bi_mat = bm.BiMatRAM.tu_bootstrap(bootstrap, settings)
            provider = bm.tao_cong_ai(settings, bi_mat=bi_mat, mask=mask if mask is not None else _MaskTat(),
                bo_ghi=bo_ghi, nha_cung_cap=nha_cung_cap,
                local_transport=local_transport, kiem_xac_suat=kiem_xac_suat)
            # QD-20261106-01: runtime bản 1 chỉ Local, 0 lượt Mask/Cloud.
            # Khóa ngay cổng vừa dựng trước khi cấp cho worker; cai_dat đã
            # được chuẩn hóa riêng nên không đổi cấu hình do Core tiêm.
            provider.cai_dat['cloud_bat'] = False
        vong = _VongNhan(bootstrap, nhan_viec, provider)
        vong.demo, vong.kiem_schema = demo, kiem_schema
        bootstrap.bao_san_sang(phien_ban=PHIEN_BAN, contracts=[] if demo else list(CONTRACTS),
            kiem_san_sang=provider.san_sang if demo else lambda: _kiem_local(provider))
        bat_dau = True
        vong.bat_dau()
        # Quá hạn chỉ báo drain chưa xong; vẫn giữ vòng bàn giao chờ Core ACK.
        bootstrap.cho_thu_hoi(ngung_accept=vong.ngung_accept, drain=cho_drain)
    except (KeyboardInterrupt, SystemExit):
        # Core buộc kết thúc; không giả ACK cho metadata còn chờ.
        # TerminateProcess/đóng Job thì OS tự thu hồi mọi handle của con.
        dung_cung = True
        raise
    finally:
        try:
            if bat_dau:
                vong.ngung_accept()
            if bootstrap is not None and (not bat_dau or dung_cung or (
                    vong.drain() and (bo_ghi is None or bo_ghi.da_ban_giao()))):
                bootstrap.socket.close()
        finally:
            # Cả lỗi trước readiness, trong drain hoặc chính cleanup đều thu RAM.
            thu_hoi_bi_mat()
            if bootstrap is not None and getattr(bootstrap, 'bi_mat', None) is not None:
                bootstrap.bi_mat.thu_hoi()


def chay_tu_core(*, bootstrap, kiem_chu_ky, nhan_viec, settings, bo_ghi, kiem_schema):
    """Điểm vào launcher: dùng bootstrap đã xác minh và các seam Core cấp.

    Giữ nguyên preflight Local, contracts, vòng lease/ACK và drain của chay;
    launcher không công bố sẵn sàng hoặc tự bật chế độ DEMO thay engine.
    """
    return chay(bootstrap=bootstrap, kiem_chu_ky=kiem_chu_ky,
        nhan_viec=nhan_viec, settings=settings, bo_ghi=bo_ghi, kiem_schema=kiem_schema)
