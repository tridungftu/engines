"""OCR-5a: bọc CongOCR chung và giữ kết quả tới ACK của Core.

Core tiêm đúng cổng/sổ Review-M4 đang dùng và vùng bàn giao bền vững có ACL
theo việc. Không tạo CongOCR, HotFolderClient, worker hay sổ trang khác.
BanGiaoOCR gắn với một viec_id do Core cấp; có thể truyền thẳng vào seam
cong_ocr của van_ban/bang. Nhật ký chỉ ghi tình trạng bàn giao, không tính
trang. Chưa ACK không có nghĩa đã bàn giao hoặc đã duyệt nghiệp vụ.

Ghi ý định trước lời gọi có tác động: crash sau wait(), kể cả trước khi
CongOCR ghi đệm, để lại "cần đối chiếu". Không tự OCR lại, không hoàn trang;
chỉ CongOCR quyết định hoàn khi chứng minh chưa gửi/rút được đầu vào.
Review nguyên gốc không tham gia khóa vẫn cần lead cách ly/chuyển sang
cổng chung (giới hạn đã ghi trong cong_ocr.py); adapter không khắc phục
được bên ghi ngoài cổng. Nối bootstrap/ACL thật thuộc OCR-4b/5b.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
from uuid import UUID

from .lib.cong_ocr import TRAN_KET_QUA_MAC_DINH, CongOCR, _docx_hop_le, _khoa_tep
from ...sdk_core.primitives import DataError
from ...sdk_core.engine import LoiEngine, SDKEngine


CAN_DOI_CHIEU = "can_doi_chieu"
CHO_CORE = "cho_core_xac_nhan"
DA_BAN_GIAO = "da_ban_giao"
TRAN_NHAT_KY_BAN_GIAO = 64 * 1024
TRAN_DOCX_BAN_GIAO = TRAN_KET_QUA_MAC_DINH


def _can_doi_chieu():
    return DataError("OCR_CAN_DOI_CHIEU", "Việc nhận dạng cần đối chiếu với Core; không tự gửi lại.")


def _doc_co_tran(tep: Path, tran: int) -> bytes:
    if tep.stat().st_size > tran:
        raise ValueError("Tệp bàn giao vượt dung lượng cho phép.")
    # Tệp có thể lớn thêm sau stat; luôn giới hạn cả lượt đọc thực tế.
    with tep.open("rb") as f:
        raw = f.read(tran + 1)
    if len(raw) > tran:
        raise ValueError("Tệp bàn giao vượt dung lượng cho phép.")
    return raw


def _ghi_ben(tep: Path, raw: bytes):
    # Khóa theo việc bao trùm ghi/rename. Không xóa kết quả hay nhật ký.
    tam = tep.with_suffix(tep.suffix + ".tmp")
    with tam.open("wb") as f:
        f.write(raw)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tam, tep)


class BanGiaoOCR:
    def __init__(self, cong_ocr: CongOCR, *, viec_id, thu_muc_ban_giao):
        if not isinstance(cong_ocr, CongOCR):
            raise TypeError("Cần CongOCR dùng chung do Core cấp")
        try:
            self.viec_id = str(UUID(str(viec_id)))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Cần UUID việc do Core cấp") from None
        self.cong_ocr = cong_ocr
        self.thu_muc = Path(thu_muc_ban_giao).resolve() / self.viec_id
        self._tep = self.thu_muc / "trang_thai.json"
        self._docx = self.thu_muc / "ket_qua.docx"
        self._khoa = self.thu_muc / "ban_giao.lock"

    def _doc(self):
        try:
            raw = _doc_co_tran(self._tep, TRAN_NHAT_KY_BAN_GIAO)
            data = json.loads(raw)
            if (not isinstance(data, dict) or data.get("viec_id") != self.viec_id
                    or data.get("trang_thai") not in (CAN_DOI_CHIEU, CHO_CORE, DA_BAN_GIAO)):
                raise ValueError
            return data
        except FileNotFoundError:
            return None
        except (ValueError, TypeError):
            # Không đặt nhật ký hỏng về chưa chạy.
            raise _can_doi_chieu() from None

    def _ghi(self, data):
        _ghi_ben(self._tep, json.dumps(data, ensure_ascii=False,
                                     allow_nan=False).encode("utf-8"))

    def _ket_qua(self, data):
        try:
            raw = _doc_co_tran(self._docx, TRAN_DOCX_BAN_GIAO)
        except (OSError, ValueError):
            raw = b""
        if (not _docx_hop_le(raw)
                or hashlib.sha256(raw).hexdigest() != data.get("sha256_docx")):
            self._ghi(data | {"trang_thai": CAN_DOI_CHIEU, "ly_do": "cần đối chiếu"})
            raise _can_doi_chieu()
        return raw

    def trang_thai(self):
        """Đọc cùng khóa: không kết luận việc đang chạy đã bị gián đoạn."""
        with _khoa_tep(self._khoa, self.cong_ocr.nghi):
            data = self._doc()
            return "chua_chay" if data is None else data["trang_thai"]

    def ocr(self, raw: bytes, duoi: str, *, huy=None) -> bytes:
        # Kiểm trước ghi ý định; cùng định dạng mà CongOCR đang hỗ trợ.
        if (not isinstance(raw, bytes) or not raw or not isinstance(duoi, str)
                or duoi.lower().lstrip(".") not in ("pdf", "jpg", "jpeg", "png", "tif", "tiff")):
            raise DataError("OCR_DINH_DANG", "Chỉ nhận PDF hoặc ảnh scan được hỗ trợ.")
        nguon = dict(sha256=hashlib.sha256(raw).hexdigest(),
                     duoi=duoi.lower().lstrip("."))
        with _khoa_tep(self._khoa, self.cong_ocr.nghi, huy):
            data = self._doc()
            if data is not None:
                if data.get("nguon") != nguon:
                    raise DataError("OCR_VIEC_XUNG_DOT", "Mã việc đã gắn với đầu vào khác.")
                if data["trang_thai"] == CAN_DOI_CHIEU:
                    raise _can_doi_chieu()
                return self._ket_qua(data)
            data = dict(viec_id=self.viec_id, nguon=nguon,
                        trang_thai=CAN_DOI_CHIEU, ly_do="cần đối chiếu")
            self._ghi(data)  # Phải bền vững trước khi có thể gửi ABBYY.
            docx = self.cong_ocr.ocr(raw, duoi, huy=huy)
            if not _docx_hop_le(docx):
                raise _can_doi_chieu()
            _ghi_ben(self._docx, docx)
            self._ghi(data | {"trang_thai": CHO_CORE, "ly_do": None,
                              "sha256_docx": hashlib.sha256(docx).hexdigest()})
            return docx

    def ban_giao(self, *, sdk: SDKEngine, du_lieu, revision_tep_truoc):
        """Core cấp SDK của chính việc này và metadata đã kiểm quyền.

        Một lần gửi kết quả đã giữ, không vòng lặp retry. Mất ACK giữ DOCX
        và trạng thái chờ; Core đối chiếu trước khi gọi lại. Crash khi gửi
        cũng không làm OCR lại hoặc hoàn trang. SDK tự kiểm lease/quyền;
        adapter không tự gắn provenance hay trạng thái duyệt nghiệp vụ.
        """
        if not isinstance(sdk, SDKEngine):
            raise TypeError("Cần SDKEngine của việc do Core cấp")
        # SDK hiện giữ lease trong slot riêng, chưa có accessor công khai.
        # Chỉ đọc tại adapter e_ocr; Core vẫn phải xác minh toàn bộ lease.
        giu_viec = getattr(sdk, "_SDKEngine__giu", None)
        if str(getattr(giu_viec, "viec_id", None)) != self.viec_id:
            raise LoiEngine("VIEC_MAT_LEASE")
        with _khoa_tep(self._khoa, self.cong_ocr.nghi):
            data = self._doc()
            if data is None or data["trang_thai"] == CAN_DOI_CHIEU:
                raise _can_doi_chieu()
            if data["trang_thai"] == DA_BAN_GIAO:
                return False
            docx = self._ket_qua(data)
            with io.BytesIO(docx) as luong:
                ack = sdk.ghi_ket_qua(luong=luong, ten="ocr.docx",
                                     du_lieu=du_lieu, revision_tep_truoc=revision_tep_truoc)
            # BanGiaoKetQua.ghi() cũng trả dictionary trước commit. Chỉ ACK
            # từ xac_nhan_da_commit(), có ID biên nhận, mới kết thúc bàn giao.
            if (not isinstance(ack, dict) or ack.get("da_ban_giao") is not True
                    or not isinstance(ack.get("ket_qua_id"), str)
                    or not ack["ket_qua_id"].strip()):
                raise DataError("OCR_CHUA_XAC_NHAN", "Core chưa xác nhận nhận kết quả.")
            self._ghi(data | {"trang_thai": DA_BAN_GIAO})
            return ack
