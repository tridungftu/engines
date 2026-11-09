"""HD-3b: vòng đời profile DEMO, chỉ điều phối các seam giả trong RAM.

Dùng lại PhienGia của HD-2a và kết quả kiểm G2-27. Không tải hóa đơn,
không xóa tệp, không tạo tài khoản/ACL, không nhận credential. Portal giả
không phải cầu nối Python/Node hay bằng chứng nguồn HD-2c đã hỗ trợ profile.

Core giả sở hữu SoPhienDemo và giữ nó khi thay controller sau crash. Sổ
RAM này không bền qua restart tiến trình; Core thật phải có sổ bền và đối
chiếu browser/Job, bàn giao, profile trước khi cho phép phiên mới. G2-33b
chưa có nên tài khoản riêng/ACL/phiên Windows thật luôn CHUA_KIEM.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from threading import RLock
from typing import Protocol

from ...core.kiem_tra_tien_trinh import kiem_tra_tien_trinh
from ...sdk_core.ho_so_engine import KetQuaKiem
from ...sdk_core.primitives import text_id
from .tai import PhienGia


def kiem_tra_moi_truong() -> tuple[KetQuaKiem, ...]:
    """G2-27 không conn/không bằng chứng: tuyệt đối không kết nối CSDL.

    DAT ở test vòng đời DEMO không được nâng thành DAT cho môi trường thật.
    Không nhận cờ caller tự xác nhận tài khoản, ACL hay coverage nguồn.
    """
    results = kiem_tra_tien_trinh('e_hoa_don', phien_ban='1.0.0')
    return tuple(replace(r, ly_do=r.ly_do + (
        'engines/e_hoa_don/phien.py:1: '
        'Thiếu seam tài khoản riêng/ACL/phiên Windows có màn hình G2-33b; '
        'chưa chạy ca âm từ tài khoản engine thật.',
    )) for r in results) + tuple(
        KetQuaKiem(ma, 'CHUA_KIEM', 'C0', (
            'engines/e_hoa_don/portal.cjs:1: ' + reason,
        ), 'e_hoa_don', '1.0.0') for ma, reason in (
            ('HD_PROFILE_NGUON', 'Thiếu seam profile/job riêng của nguồn; '
             'DEMO không chứng minh ACL hoặc dọn profile trên đĩa.'),
            ('HD_COVERAGE_NGUON', 'Thiếu seam lỗi nhóm/coverage nguồn; '
             'không suy COMPLETE từ sự kiện done.'),
        )
    )


class LoiPhienDemo(RuntimeError):
    """Chỉ mã lỗi cố định; không mang thông báo/cause từ seam."""


class PortalDemo(Protocol):
    def mo(self, phien: PhienGia) -> bool: ...
    def dong(self, phien: PhienGia) -> bool: ...


class CoreDemo(Protocol):
    def ban_giao(self, phien: PhienGia, ket_thuc: str) -> bool:
        """ACK đúng phiên/pháp nhân sau khi giữ đủ tệp/coverage/biên nhận.

        Bao gồm lỗi/hủy/crash: Core giữ việc dở, không tự coi tải đã xong.
        Retry phải idempotent, kể cả đã lưu nhưng mất ACK.
        """
        ...


class DonProfileDemo(Protocol):
    def __call__(self, phien: PhienGia) -> bool:
        """Chỉ dọn profile giả trong RAM; retry idempotent, True khi đã sạch."""
        ...


@dataclass(frozen=True)
class TienDoPhien:
    phien: PhienGia
    ket_thuc: str | None = None
    da_dong: bool = False
    da_ack: bool = False
    da_don: bool = False


class SoPhienDemo:
    """Sổ do Core giả giữ chung cho mọi pháp nhân/controller của engine.

    Giữ cả profile đã dọn để không cấp lại. Không chứa cookie/credential.
    Không thay sổ bền Core; tạo sổ mới không phải phục hồi crash.
    """

    def __init__(self):
        self._khoa = RLock()
        self._phien: dict[str, TienDoPhien] = {}


class QuanLyPhienDemo:
    """Một engine giả tuần tự; bất kỳ profile chưa sạch đều chặn phiên mới.

    Các seam chỉ được thao tác trên dữ liệu DEMO trong RAM. Không tự nạp
    portal nguồn hay cấp đường dẫn userDataDir thật. Caller Core phải dùng
    lại cùng sổ khi controller chết; không truyền bí mật trong PhienGia.
    """

    def __init__(self, *, so: SoPhienDemo, portal: PortalDemo,
                 core: CoreDemo, don_profile: DonProfileDemo):
        self._so, self._portal = so, portal
        self._core, self._don_profile = core, don_profile

    def mo_phien(self, *, demo: bool, phap_nhan_id: str,
                 nguon_id: str) -> PhienGia:
        if demo is not True:
            raise LoiPhienDemo('HD_CHI_DEMO')
        phap_nhan_id, nguon_id = text_id(phap_nhan_id), text_id(nguon_id)
        with self._so._khoa:
            if any(not r.da_don for r in self._so._phien.values()):
                raise LoiPhienDemo('HD_PROFILE_CHUA_DON')
            phien = PhienGia(phap_nhan_id, nguon_id)
            if (phien.phien_id in self._so._phien or any(
                    r.phien.profile_id == phien.profile_id
                    for r in self._so._phien.values())):
                raise LoiPhienDemo('HD_PROFILE_DA_DUNG')
            # Ghi nhận trước mở browser: mở lỗi/crash vẫn giữ chặn.
            self._so._phien[phien.phien_id] = TienDoPhien(phien)
            ok = False
            try:
                ok = self._portal.mo(phien) is True
            except Exception:
                pass
            except BaseException:
                self._ghi(phien, ket_thuc='crash')
                raise
            if not ok:
                self._ghi(phien, ket_thuc='loi')
                raise LoiPhienDemo('HD_MO_PROFILE_LOI')
            return phien

    def _doc(self, phien: PhienGia) -> TienDoPhien:
        if not isinstance(phien, PhienGia):
            raise LoiPhienDemo('HD_PHIEN_SAI')
        record = self._so._phien.get(phien.phien_id)
        if record is None or record.phien != phien:
            raise LoiPhienDemo('HD_PHIEN_SAI')
        return record

    def _ghi(self, phien: PhienGia, **fields) -> TienDoPhien:
        record = replace(self._doc(phien), **fields)
        self._so._phien[phien.phien_id] = record
        return record

    def tien_do(self, phien: PhienGia) -> TienDoPhien:
        with self._so._khoa:
            return self._doc(phien)

    def ket_thuc(self, phien: PhienGia, ket_thuc: str) -> TienDoPhien:
        if ket_thuc not in ('xong', 'loi', 'huy', 'crash'):
            raise LoiPhienDemo('HD_KET_THUC_SAI')
        with self._so._khoa:
            record = self._doc(phien)
            if record.ket_thuc not in (None, ket_thuc):
                raise LoiPhienDemo('HD_KET_THUC_DA_GHI')
            self._ghi(phien, ket_thuc=ket_thuc)
            return self._don(phien)

    @staticmethod
    def _xac_nhan(call, code, *args):
        ok = False
        try:
            ok = call(*args) is True
        except Exception:
            pass
        # Ném ngoài except để không giữ exception context có bí mật DEMO.
        if not ok:
            raise LoiPhienDemo(code)

    def _don(self, phien: PhienGia) -> TienDoPhien:
        record = self._doc(phien)
        if not record.da_dong:
            self._xac_nhan(self._portal.dong, 'HD_DONG_BROWSER_LOI', phien)
            record = self._ghi(phien, da_dong=True)
        if not record.da_ack:
            self._xac_nhan(self._core.ban_giao, 'HD_CHO_ACK', phien, record.ket_thuc)
            record = self._ghi(phien, da_ack=True)
        if not record.da_don:
            self._xac_nhan(self._don_profile, 'HD_DON_PROFILE_LOI', phien)
            record = self._ghi(phien, da_don=True)
        return record

    def phuc_hoi_crash(self) -> tuple[TienDoPhien, ...]:
        """Core giả gọi khi đã thu hồi chủ cũ; không tự tải/mở lại browser.

        Giữ kết luận/ACK đã có. Dọn lỗi vẫn chặn tất cả pháp nhân; không
        giải phóng dựa vào việc controller cũ biến mất hay sổ đang rỗng.
        """
        with self._so._khoa:
            results = []
            for record in tuple(self._so._phien.values()):
                if record.da_don:
                    continue
                if record.ket_thuc is None:
                    self._ghi(record.phien, ket_thuc='crash')
                results.append(self._don(record.phien))
            return tuple(results)
