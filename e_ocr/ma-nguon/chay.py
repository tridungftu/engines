"""Khung OCR-4a và function OCR-VUNG; bootstrap chưa công bố readiness thật.

Dùng Bootstrap G2-21; Core sở hữu launcher, listener và Windows Job.
nhan_viec là seam do hồ sơ chạy/test cấp: kiểm request bằng bo_doc rồi trả
SDKEngine của việc được Core cấp. Không dựng IPC/lease hoặc cổng OCR khác.
Backend DEMO chỉ mã hóa văn bản. Nhánh vùng đọc ảnh qua SDK và dùng
mask_ocr trong gói; không gọi ABBYY hoặc dựng transport mới.
"""

from __future__ import annotations

import io
import json
import socket
import threading
import time

from ...sdk_core.bootstrap import Bootstrap, LoiBootstrap, PROTOCOL, gui_thong_diep
from ...sdk_core.engine import SDKEngine
from ...sdk_core.ngu_canh import _xoa_loi
from ...sdk_core.primitives import DataError
from .vung import CAPABILITY, MAX_BYTES, kiem_yeu_cau, trich_vung


PHIEN_BAN = '0.1.0-demo.1'


class BackendOCRGia:
    def san_sang(self):
        return True

    def xu_ly(self, van_ban_demo):
        if not isinstance(van_ban_demo, str) or len(van_ban_demo) > 16384:
            raise ValueError('Cần văn bản DEMO tối đa 16384 ký tự')
        return van_ban_demo.encode('utf-8')


def xu_ly_tai_lieu(raw, duoi, *, chon_nguon, huy=None):
    """Core tiêm ChonNguonOCR và bytes đã kiểm quyền; không tự mở backend.

    Trả kết quả chung cùng nguồn đọc/lý do chuyển để Core lưu phản hồi
    nguồn. Contract, tham chiếu tệp, lease và ACK vẫn do Core quản lý.
    Không dùng đường DOCX cũ làm transport PDF vì sẽ đếm trang hai lần.
    """
    from .chon_nguon import ChonNguonOCR
    if not isinstance(chon_nguon, ChonNguonOCR):
        raise TypeError('Cần bộ chọn nguồn do Core cấp.')
    return chon_nguon.doc(raw, duoi, huy=huy)


def trang_thai_nguon(*, chon_nguon):
    """Dữ liệu cho màn quản lý engine; chưa công bố readiness OCR thật."""
    from .chon_nguon import ChonNguonOCR
    if not isinstance(chon_nguon, ChonNguonOCR):
        raise TypeError('Cần bộ chọn nguồn do Core cấp.')
    return chon_nguon.trang_thai()


def xu_ly_function(capability, raw, yeu_cau, *, revision=1, image_text=None):
    """Định tuyến function vùng; không thêm transport hoặc backend OCR."""
    if capability != CAPABILITY:
        raise DataError('OCR_NANG_LUC', 'Năng lực nhận dạng được yêu cầu chưa được hỗ trợ.')
    return trich_vung(raw, yeu_cau, revision=revision, image_text=image_text)


def xu_ly_viec(sdk, *, backend, image_text=None):
    """Metadata/lease do Core cấp; nhánh DEMO giữ nguyên đường OCR-4a.

    Function vùng nhận bytes qua mo_doc và gửi JSON qua ghi_ket_qua.
    Kiểm mock không chứng minh readiness hay môi trường OCR thật đã đạt.
    """
    if not isinstance(sdk, SDKEngine):
        raise TypeError('Cần SDKEngine do Core cấp')
    dau_vao = sdk.doc_dau_vao()
    ten = 'ocr-demo.txt'
    if 'capability' in dau_vao:
        if dau_vao['capability'] != CAPABILITY:
            raise DataError('OCR_NANG_LUC', 'Năng lực nhận dạng được yêu cầu chưa được hỗ trợ.')
        request = dau_vao.get('yeu_cau')
        kiem_yeu_cau(request)
        metadata = dau_vao.get('du_lieu_ket_qua')
        if (not isinstance(metadata, dict) or metadata.get('ma_contract') != 'van_ban_vung.v1'
                or metadata.get('phien_ban_contract') != '1.0.0'
                or type(metadata.get('revision_truoc')) is not int
                or metadata['revision_truoc'] < 0):
            raise DataError('OCR_VUNG_KET_QUA', 'Thông tin bàn giao kết quả đọc vùng không hợp lệ.')
        with sdk.mo_doc(request['tham_chieu_tep']['tep_id']) as luong:
            anh = luong.read(MAX_BYTES + 1)
        result = xu_ly_function(CAPABILITY, anh, request,
                               revision=metadata['revision_truoc'] + 1, image_text=image_text)
        raw = json.dumps(result, ensure_ascii=False, allow_nan=False).encode('utf-8')
        ten = 'ocr-vung.json'
    else:
        raw = backend.xu_ly(dau_vao['van_ban_demo'])
    with io.BytesIO(raw) as luong:
        while True:
            # Core có thể đã đọc hết luồng rồi mới lỗi trước ACK. Giữ cùng
            # kết quả/lease, gửi lại từ đầu; chỉ giải phóng sau khi được ACK.
            luong.seek(0)
            try:
                return sdk.ghi_ket_qua(luong=luong, ten=ten,
                    du_lieu=dau_vao['du_lieu_ket_qua'],
                    revision_tep_truoc=dau_vao['revision_tep_truoc'])
            except Exception as exc:
                _xoa_loi(exc)
            time.sleep(0.1)


class _VongNhan:
    """Một worker tuần tự; ngừng nhận dưới cùng khóa với đăng ký việc.

    Không shutdown listener dùng chung với Core. Timeout accept chỉ để
    đánh thức worker; drain không đặt hạn hủy hoặc kill việc đang chạy.
    """

    def __init__(self, bootstrap, nhan_viec, backend):
        self.bootstrap, self.nhan_viec, self.backend = bootstrap, nhan_viec, backend
        self.khoa = threading.Lock()
        self.dung = False
        self.loi = False
        # Không tự giải phóng việc chưa bàn giao; giữ để Core/Admin xử lý.
        self._giu_khi_loi = threading.Event()
        self.worker = threading.Thread(target=self._chay, name='ocr-demo')

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
                    # Bootstrap thu quyền trước callback ngung_accept.
                    if exc.ma == 'CHUA_CO_QUYEN_ACCEPT':
                        return
                    raise
                with conn:
                    with self.khoa:
                        if self.dung:
                            return
                        # Việc đã được đăng ký trước ngừng nhận: drain phải chờ.
                    # Timeout listener chỉ đánh thức accept, không được cắt ACK.
                    conn.settimeout(None)
                    try:
                        sdk = self.nhan_viec(conn, self.bootstrap.bo_doc)
                        xu_ly_viec(sdk, backend=self.backend)
                    except Exception as exc:
                        _xoa_loi(exc)
                        self.loi = True
                        self.ngung_accept()
                        self._giu_khi_loi.wait()
                        return
        except Exception as exc:
            _xoa_loi(exc)
            self.loi = True

    def ngung_accept(self):
        with self.khoa:
            self.dung = True

    def drain(self):
        # Chỉ hạn chờ để báo tiến độ; không hủy việc hoặc cắt chờ ACK.
        self.worker.join(0.1)
        if self.loi:
            self._giu_khi_loi.wait(0.1)
        return not self.worker.is_alive() and not self.loi


def chay(*, kiem_chu_ky, nhan_viec, backend=None):
    """Entrypoint tiêm seam, không có CLI/cấu hình tự mở backend thật.

    Readiness contracts=[]: listener/khung giả sẵn sàng không chứng minh
    ocr.trich_van_ban@1 hoặc ocr.trich_bang@1 đã hoạt động.
    """
    if not callable(kiem_chu_ky) or not callable(nhan_viec):
        raise TypeError('Cần bộ kiểm chữ ký và seam nhận việc của Core')
    backend = BackendOCRGia() if backend is None else backend
    bootstrap = Bootstrap.nhan(kiem_chu_ky=kiem_chu_ky)
    vong = _VongNhan(bootstrap, nhan_viec, backend)
    bat_dau = False
    try:
        bootstrap.bao_san_sang(phien_ban=PHIEN_BAN, contracts=[],
                               kiem_san_sang=backend.san_sang)
        vong.bat_dau()
        bat_dau = True
        try:
            bootstrap.cho_thu_hoi(ngung_accept=vong.ngung_accept, drain=vong.drain)
        except LoiBootstrap as exc:
            if exc.ma != 'DRAIN_CHUA_XONG':
                raise
            _xoa_loi(exc)
            gui_thong_diep(bootstrap._ra,
                {'protocol': PROTOCOL, 'kieu': 'drain_chua_xong'})
            # Lệnh thu hồi đã được bootstrap nhận; không đọc lại stdin hay
            # đòi Core gửi lại lệnh. Worker tiếp tục retry đến khi có ACK.
            while not vong.drain():
                pass
            bootstrap.socket.close()
            gui_thong_diep(bootstrap._ra,
                {'protocol': PROTOCOL, 'kieu': 'da_thu_hoi'})
    finally:
        if bat_dau:
            vong.ngung_accept()
            while not vong.drain():
                pass
            bootstrap.socket.close()
        else:
            bootstrap.socket.close()
