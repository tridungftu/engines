"""MASK-3E: function che/mở che qua việc Core, chỉ nhận tham chiếu.

Tệp riêng chứa văn bản, mã yêu cầu và mã lượt ổn định do Core cấp. Kho RAM
chỉ công bố kết quả sau chốt nguyên tử. F/G tiêm goi_kho gắn với SDK/lease;
chưa công bố contract/capability hoặc tự mở transport, CSDL hay nguồn ngoài.
"""
from __future__ import annotations

import io
import json
import logging
import socket
import subprocess  # Giữ điểm mock kiểm chặn launcher cũ; không spawn.
import threading
import time
from uuid import UUID

# Test độc lập của khung cũ còn yêu cầu import này; không gọi helper nguồn ngoài.
from kho_tri_thuc.nguon.trich6_host import env_con
from kho_tri_thuc.sdk_core.ho_so_engine import BoKhoiChayTaiKhoan, LoiKhoiChayTaiKhoan
from kho_tri_thuc.sdk_core.bootstrap import BiMatBootstrap, Bootstrap, LoiBootstrap
from kho_tri_thuc.sdk_core.engine import KenhCore, LoiEngine, SDKEngine
from kho_tri_thuc.sdk_core.ngu_canh import _xoa_loi
from . import che_van_ban
from .kho_qua_core import KhoQuaCore, LoiKhoQuaCore


CAPABILITIES = {'mask.che_van_ban': 'che', 'mask.mo_che_van_ban': 'mo_che'}
# Luồng tệp riêng, không nâng trần JSON của kênh IPC (1 MiB).
MAX_BYTES = 4 * 1024 * 1024
# Tổng số lần gửi, gồm lần đầu; Core có thể phát lại việc với cùng mã ổn định.
MAX_LAN_GUI_KET_QUA = 3
MAX_LAN_XU_LY = 3  # Gồm lần đầu; giữ giới hạn gửi của adapter, không retry vô hạn.
CHO_NHAN_VIEC_GIAY = 0.1
PHIEN_BAN = '0.1.0.dev1'
HO_SO_TAI_KHOAN = 'mask'


class LoiMask(RuntimeError):
    def __init__(self, ma):
        self.ma = ma
        thong_bao = {
            'MASK_DAU_VAO': 'Yêu cầu xử lý định danh chưa hợp lệ.',
            'MASK_KHO_CHUA_NOI': 'Chưa kết nối kho định danh của hệ thống.',
            'MASK_XU_LY': 'Không thể hoàn tất xử lý định danh an toàn.',
            'MASK_XUNG_DOT_LUOT': 'Danh mục vừa thay đổi. Cần thử lại lượt xử lý.',
            'MASK_BAN_GIAO_CHUA_XAC_NHAN': 'Hệ thống chưa xác nhận kết quả. Cần thử lại.',
            'MASK_LAUNCHER_DA_BO': 'Cách khởi chạy nguồn che dữ liệu này đã ngừng sử dụng.',
        }
        super().__init__(thong_bao.get(ma, ma))


def _uuid(gia_tri):
    if not isinstance(gia_tri, str):
        raise LoiMask('MASK_DAU_VAO')
    return str(UUID(gia_tri))


def _kiem_yeu_cau(capability, yeu_cau):
    if capability not in CAPABILITIES or not isinstance(yeu_cau, dict):
        raise LoiMask('MASK_DAU_VAO')
    bat_buoc = {'van_ban', 'ma_yeu_cau', 'ma_luot'}
    tuy_chon = ({'dinh_danh_da_biet'} if capability == 'mask.che_van_ban' else {'dong_viec'})
    if not bat_buoc <= set(yeu_cau) or set(yeu_cau) - bat_buoc - tuy_chon:
        raise LoiMask('MASK_DAU_VAO')
    _uuid(yeu_cau['ma_yeu_cau'])
    _uuid(yeu_cau['ma_luot'])
    van_ban = yeu_cau['van_ban']
    if (not isinstance(van_ban, str) or len(van_ban) > 500_000
            or (capability == 'mask.che_van_ban' and not van_ban.strip())
            or type(yeu_cau.get('dong_viec', False)) is not bool):
        raise LoiMask('MASK_DAU_VAO')
    if capability == 'mask.che_van_ban':
        # Kiểm trước snapshot, dùng đúng bộ kiểm của lõi, không thêm bộ che.
        che_van_ban._kiem_dinh_danh(
            [] if yeu_cau.get('dinh_danh_da_biet') is None else yeu_cau['dinh_danh_da_biet'],
            la_khai_bao=True)


def xu_ly_function(capability, yeu_cau, *, goi_kho):
    """Hàm nội bộ; yeu_cau đã đọc từ tệp riêng, không phải hàng việc.

    goi_kho(operation, **payload) là callable Core tin cậy, không lấy từ
    đầu vào. Payload snapshot/chốt theo KhoQuaCore, không RPC từng mục kho.
    Lỗi/xung đột không tự che lại; phát lại cùng hai mã mới lấy được kết quả cũ.
    """
    ma_loi = 'MASK_XU_LY'
    try:
        _kiem_yeu_cau(capability, yeu_cau)
        if not callable(goi_kho):
            raise LoiMask('MASK_KHO_CHUA_NOI')
        kho = KhoQuaCore(goi_kho=goi_kho, ma_yeu_cau=yeu_cau['ma_yeu_cau'],
                         ma_luot=yeu_cau['ma_luot'], loai=CAPABILITIES[capability])
        if kho.da_chot:
            return kho.chot()
        if capability == 'mask.che_van_ban':
            kq = che_van_ban.che(yeu_cau['van_ban'], yeu_cau.get('dinh_danh_da_biet'), kho)
        else:
            kq = che_van_ban.mo_che(yeu_cau['van_ban'], _uuid(yeu_cau['ma_yeu_cau']),
                                    kho, dong_viec=yeu_cau.get('dong_viec', False))
        return kho.chot(kq)
    except Exception as exc:
        if isinstance(exc, LoiMask):
            ma_loi = exc.ma
        elif isinstance(exc, LoiKhoQuaCore) and exc.ma == 'MASK_XUNG_DOT_LUOT':
            ma_loi = exc.ma
        elif getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE':
            ma_loi = 'VIEC_MAT_LEASE'
        _xoa_loi(exc)
    finally:
        # Không giữ văn bản/snapshot/nhật ký trong frame ngoại lệ ra ngoài.
        capability = yeu_cau = kho = kq = goi_kho = None
    raise LoiMask(ma_loi)


def _kiem_envelope(dau_vao):
    truong = {'capability', 'yeu_cau', 'du_lieu_ket_qua', 'revision_tep_truoc'}
    if (not isinstance(dau_vao, dict) or set(dau_vao) != truong
            or dau_vao['capability'] not in CAPABILITIES):
        raise LoiMask('MASK_DAU_VAO')
    request = dau_vao['yeu_cau']
    if not isinstance(request, dict) or set(request) != {'tham_chieu_tep'}:
        raise LoiMask('MASK_DAU_VAO')
    ref = request['tham_chieu_tep']
    if not isinstance(ref, dict) or set(ref) != {'tep_id'}:
        raise LoiMask('MASK_DAU_VAO')
    _uuid(ref['tep_id'])
    meta = dau_vao['du_lieu_ket_qua']
    can = {'bien_the', 'ma_contract', 'phien_ban_contract', 'trang_thai',
           'ly_do', 'revision_truoc', 'nguon'}
    if (not isinstance(meta, dict) or not can <= set(meta) or set(meta) - can - {'goc_id'}
            or any(not isinstance(meta[k], str) or not meta[k]
                   for k in ('bien_the', 'ma_contract', 'phien_ban_contract', 'trang_thai'))
            or (meta['ly_do'] is not None and not isinstance(meta['ly_do'], str))
            or not isinstance(meta['nguon'], list)
            or any(type(n) is not int or n < 0
                   for n in (meta['revision_truoc'], dau_vao['revision_tep_truoc']))):
        raise LoiMask('MASK_DAU_VAO')


def _object_json(pairs):
    ket_qua = {}
    for k, v in pairs:
        if k in ket_qua:
            raise LoiMask('MASK_DAU_VAO')
        ket_qua[k] = v
    return ket_qua


def _doc_json(raw):
    def sai_so(_):
        raise LoiMask('MASK_DAU_VAO')
    if not isinstance(raw, bytes) or len(raw) > MAX_BYTES:
        raise LoiMask('MASK_DAU_VAO')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_object_json, parse_constant=sai_so)


def xu_ly_viec(sdk, *, goi_kho):
    """Đọc envelope Core → mo_doc → chốt → ghi_ket_qua/ACK.

    Không ép vào contract cũ noi_dung_da_che.v1. Metadata do Core cung cấp,
    F kiểm schema/bàn giao riêng, G gắn quyền kho; đây chưa là readiness thật.
    Giữ bộ đệm đến ACK hoặc hết trần gửi; heartbeat cùng lease, mất lease thì dừng.
    """
    if not isinstance(sdk, SDKEngine):
        raise TypeError('Cần kênh xử lý do hệ thống cấp.')
    if not callable(goi_kho):
        raise LoiMask('MASK_KHO_CHUA_NOI')
    dung, mat_lease = threading.Event(), threading.Event()
    ma_loi = 'MASK_XU_LY'

    def heartbeat():
        cho = 30
        while not dung.wait(cho):
            try:
                sdk.heartbeat()
                cho = 30
            except Exception as exc:
                mat = getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE'
                _xoa_loi(exc)
                if mat:
                    mat_lease.set()
                    return
                cho = 1

    worker = threading.Thread(target=heartbeat, name='mask-heartbeat', daemon=True)
    try:
        # Lấy hạn mới trước khi đặt lịch; không truy cập thuộc tính riêng SDK.
        sdk.heartbeat()
        worker.start()
        dau_vao = sdk.doc_dau_vao()
        _kiem_envelope(dau_vao)
        with sdk.mo_doc(dau_vao['yeu_cau']['tham_chieu_tep']['tep_id']) as tep:
            raw = tep.read(MAX_BYTES + 1)
        yeu_cau = _doc_json(raw)
        if mat_lease.is_set():
            raise LoiEngine('VIEC_MAT_LEASE')
        kq = xu_ly_function(dau_vao['capability'], yeu_cau, goi_kho=goi_kho)
        raw = json.dumps(kq, ensure_ascii=False, allow_nan=False).encode('utf-8')
        with io.BytesIO(raw) as luong:
            for lan in range(MAX_LAN_GUI_KET_QUA):
                if mat_lease.is_set():
                    raise LoiEngine('VIEC_MAT_LEASE')
                luong.seek(0)
                try:
                    return sdk.ghi_ket_qua(luong=luong, ten='mask-van-ban.json',
                        du_lieu=dau_vao['du_lieu_ket_qua'],
                        revision_tep_truoc=dau_vao['revision_tep_truoc'])
                except Exception as exc:
                    mat = getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE'
                    _xoa_loi(exc)
                    if mat:
                        mat_lease.set()
                if mat_lease.is_set():
                    raise LoiEngine('VIEC_MAT_LEASE')
                if lan + 1 == MAX_LAN_GUI_KET_QUA:
                    raise LoiMask('MASK_BAN_GIAO_CHUA_XAC_NHAN')
                time.sleep(0.1)
    except Exception as exc:
        if isinstance(exc, LoiMask):
            ma_loi = exc.ma
        elif getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE':
            ma_loi = 'VIEC_MAT_LEASE'
        _xoa_loi(exc)
    finally:
        dung.set()
        if worker.ident is not None:
            worker.join()
        dau_vao = yeu_cau = kq = raw = tep = luong = goi_kho = None
    raise LoiMask(ma_loi)


def _ket_thuc_viec(kenh, giu, sdk_viec, *, trang_thai, ket_qua_id, ma_loi):
    """Chờ xác nhận kết thúc trước khi nhận tiếp, kể cả khi đang dừng.

    Chỉ Core xác nhận mất lease mới cho phép bỏ chờ. Lỗi kênh không đồng
    nghĩa đã kết thúc; giữ cùng trạng thái/kết quả và gia hạn khi thử lại.
    """
    while True:
        try:
            if kenh.ket_thuc(giu, trang_thai=trang_thai,
                            ket_qua_id=ket_qua_id, ma_loi=ma_loi) is True:
                return
        except Exception as exc:
            mat = getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE'
            _xoa_loi(exc)
            if mat:
                return
        try:
            sdk_viec.heartbeat()
        except Exception as exc:
            mat = getattr(exc, 'ma', None) == 'VIEC_MAT_LEASE'
            _xoa_loi(exc)
            if mat:
                return
        time.sleep(CHO_NHAN_VIEC_GIAY)


def chay_vong(sdk, *, goi_kho, dung):
    """Kênh Core đã xác thực → từng lease → ACK → kết thúc.

    sdk là kênh KenhCore được composition root cấp, có nhan_viec/ket_thuc;
    SDKEngine hiện hành chỉ xử lý một lease. goi_kho(operation, giu, **p)
    cùng chữ ký KenhCore.goi_mask, được gắn lại cho chính việc vừa nhận.
    dung là Event: dừng nhận mới, không hủy việc hoặc bỏ chờ kết thúc.
    Thiếu ACK kết quả: ngừng heartbeat, để Core thu hồi lease rồi khôi phục;
    đối soát ACK phía Core thuộc lát J8b-Core.
    """
    if (not isinstance(sdk, KenhCore)
            or not callable(getattr(sdk, 'nhan_viec', None))
            or not callable(getattr(sdk, 'ket_thuc', None))
            or not callable(goi_kho)
            or not callable(getattr(dung, 'is_set', None))
            or not callable(getattr(dung, 'wait', None))):
        raise TypeError('Cần kênh nhận việc và tín hiệu dừng do hệ thống cấp.')
    while not dung.is_set():
        giu = None
        loi_nhan = False
        try:
            giu = sdk.nhan_viec()
        except Exception as exc:
            thu_lai = (getattr(exc, 'ma', None) == 'CHUA_SAN_SANG'
                       and getattr(exc, 'thu_lai_duoc', False) is True)
            loi_nhan = not thu_lai
            _xoa_loi(exc)
        if loi_nhan:
            raise LoiMask('MASK_XU_LY')
        if giu is None:
            dung.wait(CHO_NHAN_VIEC_GIAY)
            continue
        # Dừng đến trong lúc nhận vẫn phải hoàn tất lease vừa được Core cấp.
        sdk_viec = SDKEngine(giu, kenh_core=sdk)

        def kho_viec(operation, **payload):
            return goi_kho(operation, giu, **payload)

        trang_thai, ket_qua_id, ma_loi = 'LOI', None, 'MASK_XU_LY'
        chua_ro_ket_qua = False
        try:
            for lan in range(MAX_LAN_XU_LY):
                xung_dot = False
                try:
                    ack = xu_ly_viec(sdk_viec, goi_kho=kho_viec)
                    if (not isinstance(ack, dict)
                            or not isinstance(ack.get('ket_qua_id'), str)
                            or not ack['ket_qua_id'].strip()):
                        raise LoiMask('MASK_BAN_GIAO_CHUA_XAC_NHAN')
                    ket_qua_id = ack['ket_qua_id']
                    trang_thai, ma_loi = 'XONG', None
                    break
                except Exception as exc:
                    xung_dot = getattr(exc, 'ma', None) == 'MASK_XUNG_DOT_LUOT'
                    chua_ro_ket_qua = (getattr(exc, 'ma', None)
                                      == 'MASK_BAN_GIAO_CHUA_XAC_NHAN')
                    ma_loi = 'MASK_XUNG_DOT_LUOT' if xung_dot else 'MASK_XU_LY'
                    _xoa_loi(exc)
                if not xung_dot or lan + 1 == MAX_LAN_XU_LY:
                    break
                # Cùng mã yêu cầu/lượt; lần sau lấy snapshot mới từ Core.
                time.sleep(CHO_NHAN_VIEC_GIAY)
        finally:
            if chua_ro_ket_qua:
                # xu_ly_viec đã dừng/join heartbeat. Core có thể đã commit;
                # không đoán mã kết quả hay kết thúc với ket_qua_id=None.
                logging.getLogger(__name__).warning('MASK_KET_QUA_CHUA_RO')
            else:
                _ket_thuc_viec(sdk, giu, sdk_viec, trang_thai=trang_thai,
                              ket_qua_id=ket_qua_id, ma_loi=ma_loi)
            giu = sdk_viec = kho_viec = ack = None


def main(*, kiem_chu_ky, nhan_viec):
    """Core gọi tường minh, tiêm kênh từ socket Bootstrap như OCR.

    nhan_viec(conn, bo_doc) trả kênh đã xác thực có goi_mask, không tự dựng
    transport hay đọc cấu hình. Chưa công bố capability trước lát J6–J7.
    Lệnh thu hồi của Bootstrap ngừng nhận và chờ việc hiện tại hoàn tất.
    """
    if not callable(kiem_chu_ky) or not callable(nhan_viec):
        raise TypeError('Cần bộ kiểm chữ ký và kênh nhận việc do hệ thống cấp.')
    bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky)
    dung, loi = threading.Event(), threading.Event()

    def chay():
        try:
            while not dung.is_set():
                try:
                    conn, _ = bootstrap.accept()
                except socket.timeout:
                    continue
                except LoiBootstrap as exc:
                    thu_hoi = exc.ma == 'CHUA_CO_QUYEN_ACCEPT'
                    _xoa_loi(exc)
                    if thu_hoi:
                        return
                    raise LoiMask('MASK_XU_LY')
                with conn:
                    conn.settimeout(None)
                    kenh = nhan_viec(conn, bootstrap.bo_doc)
                    chay_vong(kenh, goi_kho=kenh.goi_mask, dung=dung)
        except Exception as exc:
            _xoa_loi(exc)
            loi.set()

    worker = threading.Thread(target=chay, name='mask-vong-viec')

    def drain():
        while worker.is_alive():
            worker.join(CHO_NHAN_VIEC_GIAY)
        return True

    try:
        bootstrap.bao_san_sang(phien_ban=PHIEN_BAN, contracts=[],
                               kiem_san_sang=lambda: True)
        bootstrap.socket.settimeout(CHO_NHAN_VIEC_GIAY)
        worker.start()
        bootstrap.cho_thu_hoi(ngung_accept=dung.set, drain=drain)
    finally:
        dung.set()
        drain()
        bootstrap.bi_mat.thu_hoi()
        bootstrap.socket.close()
    if loi.is_set():
        raise LoiMask('MASK_XU_LY')


class TienTrinhMask:
    """Chốt tương thích khung cũ; không còn launcher/run_privacy.py.

    Giữ kiểm cấu hình trước spawn cho caller cũ. Cấu hình hợp lệ cũng bị
    từ chối: lõi đã ở trong gói, không cấp khóa/mở danh mục nguồn ngoài.
    Core phải dùng xu_ly_viec mới; không tự chuyển sang launcher cũ khi lỗi.
    """
    def __init__(self, *, thu_muc_mask, cong, cap_khoa=None,
                 kiem_san_sang=None, cho_phep_dung=None,
                 bat_khoi_chay_tai_khoan=False, bo_khoi_chay_tai_khoan=None,
                 ho_so_tai_khoan=HO_SO_TAI_KHOAN, gan_job=None, bi_mat=None):
        if type(cong) is not int or not 1024 <= cong <= 65535:
            raise LoiMask('CONG_KHONG_HOP_LE')
        if type(bat_khoi_chay_tai_khoan) is not bool:
            raise LoiMask('CO_TAI_KHOAN_KHONG_HOP_LE')
        self._cap, self._ready, self._stop = cap_khoa, kiem_san_sang, cho_phep_dung
        self._bat, self._bo = bat_khoi_chay_tai_khoan, bo_khoi_chay_tai_khoan
        self._ho_so, self._job, self._bi_mat = ho_so_tai_khoan, gan_job, bi_mat

    def khoi_dong(self):
        ma = 'MASK_LAUNCHER_DA_BO'
        try:
            if not callable(self._cap):
                raise LoiMask('THIEU_SEAM_CAP_KHOA')
            if not callable(self._ready) or not callable(self._stop):
                raise LoiMask('THIEU_SEAM_VONG_DOI')
            if self._bat:
                if not isinstance(self._bo, BoKhoiChayTaiKhoan):
                    raise LoiMask('KHOI_CHAY_TAI_KHOAN_CHUA_CAU_HINH')
                if not callable(self._job):
                    raise LoiMask('THIEU_SEAM_GAN_JOB')
                if not isinstance(self._bi_mat, BiMatBootstrap):
                    raise LoiMask('THIEU_KENH_BI_MAT')
                self._bo.kiem_tra(self._ho_so)
        except Exception as exc:
            if isinstance(exc, (LoiMask, LoiKhoiChayTaiKhoan)):
                ma = exc.ma
            _xoa_loi(exc)
        finally:
            if isinstance(self._bi_mat, BiMatBootstrap):
                self._bi_mat.thu_hoi()
                self._bi_mat = None
        raise LoiMask(ma)
