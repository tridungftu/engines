"""TRICH-1b: thay seam AI nguồn review v3/2026-10-15a bằng CongAI.goi.

Nguồn: src/kho_tri_thuc/m4/review_goc/trich_xuat/ai_local.py (chỉ đọc).
SHA256: 5ee214ea442fc924bc60a871e1f4328cfc4ae74b859160904089430fdd7dba77.
Chỉ giữ giao diện kết quả/ngoại lệ; không chép client hay protocol của nguồn.
CongAI do Core tiêm; snapshot cấu hình mỗi lượt, luôn tắt Cloud. DTO không
có token: bộ đếm tương thích bộ xuất nguồn là 0, token_da_do=False.
"""

from copy import copy, deepcopy
from dataclasses import asdict, replace

from ..e_hoi_ai.lib.cong_ai import CongAI, KetQuaAI, YeuCauAI, HE_THONG, HUONG_DAN_DINH_DANG

NGUON = "src/kho_tri_thuc/m4/review_goc/trich_xuat/ai_local.py"
NGUON_SHA256 = "5ee214ea442fc924bc60a871e1f4328cfc4ae74b859160904089430fdd7dba77"
PHIEN_BAN_NGUON = "2026-10-15a"

# Từng thay đổi câu hỏi/protocol; TRICH-4b dùng làm đối chiếu trước/sau.
# Không nới test gốc dùng mock protocol cũ; các ca thay thế ở test_g3_trich_1b.
CAU_HOI_DOI = (
    dict(id="TRICH-NHOM", goc="build_prompt / hoi_trich: ket_qua + schema riêng",
         moi="YeuCauAI: mỗi mã là ten; don_vi/ghi_chu là trường phụ có dẫn chứng",
         ly_do="CongAI chỉ nhận truong/gia_tri/trich_dan; không nhận schema riêng. "
               "Bỏ trường không tìm thấy thay vì yêu cầu bịa câu Không quy định; "
               "chỉ giữ ghi chú nguyên văn, không yêu cầu suy ra giá trị."),
    dict(id="TRICH-VI-TRI", goc="ai_tim_vi_tri: vi_tri[{ma, ids}] trên mục lục",
         moi="Tối đa ba trường ma.1/ma.2/ma.3, giá trị ID, trích nguyên dòng mục lục",
         ly_do="Giá trị ID phải có trong dẫn chứng để qua kiểm cổng chung; "
               "giữ tối đa ba vị trí hợp lệ, không thêm đường Local riêng."),
    dict(id="TRICH-RA-LAI", goc="ra_lai dùng build_prompt và hoi_trich của nguồn",
         moi="Cùng DTO/câu hỏi TRICH-NHOM, từng đoạn toàn hợp đồng",
         ly_do="Giữ thuật toán xác nhận/mâu thuẫn của nguồn, đồng nhất định dạng cổng."),
    dict(id="TRICH-JSON", goc="SYSTEM + JSON_NHAC, hỏi lại JSON, schema/num_ctx/think riêng",
         moi="CongAI.goi dựng câu hỏi và kiểm KetQuaAI theo mẫu cổng chung",
         ly_do="Cổng chung sở hữu định dạng, kiểm dẫn chứng và xử lý lỗi; "
               "không mở rộng cổng hoặc tự đoán giới hạn context/token."),
)

CHI_DAN_TRICH = (
    "Trích tham số hợp đồng xây dựng, chỉ dùng Văn bản. Giữ nguyên số liệu, "
    "không suy diễn hoặc tính ra giá trị. Tên trường chính là mã tham số; "
    "trường <mã>.don_vi là đơn vị nguyên văn, <mã>.ghi_chu là ghi chú nguyên văn "
    "nếu có. Mỗi trường phải có trích dẫn nguyên văn chứa giá trị. "
    "Không có thông tin thì bỏ trường. Không trả ket_qua hoặc schema khác."
)
CHI_DAN_VI_TRI = (
    "Tìm vị trí tham số trong MỤC LỤC HỢP ĐỒNG. Với mỗi mã, chọn tối đa 3 ID "
    "có khả năng chứa thông tin nhất, đặt vào trường <mã>.1, <mã>.2, <mã>.3; "
    "mỗi giá trị là một ID, trích_dẫn là nguyên dòng mục lục chứa ID đó. "
    "Không có vị trí thì bỏ trường."
)

# Nguyên văn mẫu câu hỏi nguồn (các chỗ {ds}/{blocks}/{phan} là dữ liệu
# động); lưu cùng câu mới để TRICH-4b không phải suy ngược từ mô tả protocol.
CAU_TRICH_GOC = (
    "Trích các tham số sau từ các đoạn hợp đồng bên dưới.\n\nTHAM SỐ:\n{ds}\n\n"
    "QUY TẮC:\n"
    "- Mỗi tham số một phần tử trong 'ket_qua', giữ đúng mã.\n"
    "- gia_tri: ngắn gọn, giữ nguyên số liệu như trong hợp đồng (vd 7.915.563.292; 90; 0,15). "
    "Nếu hợp đồng ghi 'Không áp dụng' thì ghi 'Không áp dụng'. Không có thông tin thì ghi 'Không quy định'.\n"
    "- don_vi: đồng, %, ngày, tháng, bộ, %/ngày… (để trống nếu không có).\n"
    "- dieu_khoan: lấy từ nhãn trong ngoặc vuông của đoạn chứa thông tin (vd 'Điều 5 – Khoản 5.3').\n"
    "- trich_dan: chép NGUYÊN VĂN một câu ngắn trong hợp đồng chứa giá trị, không sửa chữ nào.\n"
    "- ghi_chu: ghi 'Suy ra' nếu giá trị được tính ra chứ không ghi trực tiếp (vd tỷ lệ giữ lại = 100% - tỷ lệ thanh toán).\n\n"
    "CÁC ĐOẠN HỢP ĐỒNG:\n\n{blocks}"
)
CAU_VI_TRI_GOC = (
    "Dưới đây là MỤC LỤC HỢP ĐỒNG (ID | Điều/Khoản | đầu nội dung){phan}. "
    "Với mỗi tham số, chọn tối đa 3 ID của mục có khả năng chứa thông tin nhất. "
    "Không có thì để danh sách rỗng.\n\nTHAM SỐ:\n{ds}\n\nMỤC LỤC HỢP ĐỒNG:\n{muc_luc}"
)
CAU_HE_THONG_GOC = (
    "Bạn là chuyên viên trích xuất dữ liệu hợp đồng xây dựng. Chỉ dùng các đoạn hợp đồng được cung cấp. "
    "Không suy diễn, không bịa. Trả lời đúng định dạng JSON được yêu cầu."
)
CAU_NHAC_GOC = "\n\nCHỈ TRẢ VỀ JSON hợp lệ đúng schema, không thêm chữ nào khác ngoài JSON."
for _doi in CAU_HOI_DOI:
    _doi["cau_goc"] = (CAU_VI_TRI_GOC if _doi["id"] == "TRICH-VI-TRI" else
                       CAU_HE_THONG_GOC + CAU_NHAC_GOC if _doi["id"] == "TRICH-JSON" else CAU_TRICH_GOC)
    _doi["cau_moi"] = (CHI_DAN_VI_TRI + "\nTHAM SỐ:\n{ds}" if _doi["id"] == "TRICH-VI-TRI" else
                       HE_THONG + "\n\n" + HUONG_DAN_DINH_DANG if _doi["id"] == "TRICH-JSON" else
                       CHI_DAN_TRICH + "\nTHAM SỐ:\n{ds}")


class AILoi(Exception):
    """Không có kết quả dùng được từ cổng chung (tương ứng AILoi nguồn)."""


class DaDung(Exception):
    """Người dùng dừng, tương ứng DaDung nguồn."""


class AIChung:
    la_cloud = False
    ten = "Cổng AI chung (Local)"
    url = "CongAI"  # Metadata tương thích pipeline, không phải địa chỉ máy AI.

    def __init__(self, cong_ai, *, cloud=None, dung=None,
                 loai_hop_dong="XD", ten_loai="Hợp đồng xây dựng"):
        if cloud is not None:
            raise ValueError("TRICH_CLOUD_BI_CHAN")
        if not isinstance(cong_ai, CongAI):
            raise TypeError("TRICH_CAN_CONG_AI")
        self._cong = cong_ai
        self.loai_hop_dong = loai_hop_dong
        self.ten_loai = ten_loai
        self.dung = dung
        self.model = str(cong_ai.local_ai.get("model") or "")
        self.tok_vao = self.tok_ra = self.so_lan_goi = 0
        self.phan_hoi = []

    def _kiem_dung(self):
        if self.dung is not None and self.dung.is_set():
            raise DaDung()

    def goi(self, yeu_cau):
        self._kiem_dung()
        if not isinstance(yeu_cau, YeuCauAI):
            raise TypeError("TRICH_CAN_YEU_CAU_AI")
        # LHD-E2: XD giữ nguyên DTO/câu hỏi từng chữ, kể cả tìm vị trí/rà lại.
        if self.loai_hop_dong != "XD":
            if not isinstance(self.ten_loai, str) or not self.ten_loai.strip():
                raise ValueError("TRICH_DANH_MUC_KHONG_HO_TRO")
            # Chỉ đổi mẫu chỉ dẫn; giữ nguyên phần tham số từ danh mục từng byte.
            chi_dan, moc_tham_so, tham_so = yeu_cau.chi_dan.partition("\nTHAM SỐ:\n")
            chi_dan = chi_dan.replace("hợp đồng xây dựng", self.ten_loai.strip())
            chi_dan = chi_dan.replace("MỤC LỤC HỢP ĐỒNG", "MỤC LỤC " + self.ten_loai.strip().upper())
            yeu_cau = replace(yeu_cau, chi_dan=chi_dan + moc_tham_so + tham_so)
        # Không sửa cổng/cấu hình dùng chung; Cloud không được fallback kể cả lỗi.
        cong = copy(self._cong)
        cong.cai_dat = deepcopy(self._cong.cai_dat)
        cong.local_ai = deepcopy(self._cong.local_ai)
        cong.cai_dat["cloud_bat"] = False
        kq = cong.goi(yeu_cau)
        self.so_lan_goi += 1
        self._kiem_dung()
        if not isinstance(kq, KetQuaAI):
            raise TypeError("TRICH_CAN_KET_QUA_AI")
        if kq.duong not in ("LOCAL", "KHONG") or any(
                t.nguon != "LOCAL" for t in kq.truong.values()):
            raise AILoi("TRICH_CLOUD_BI_CHAN")
        # Giữ phản hồi đầy đủ và mã lượt nguồn, gồm lý do/trường bị loại.
        self.phan_hoi.append(asdict(kq))
        return kq

    def hoi_trich(self, yeu_cau, what="AI"):
        kq = self.goi(yeu_cau)
        self._kiem_loi(kq)
        items = []
        for ma in yeu_cau.truong:
            if "." in ma or ma not in kq.truong:
                continue
            t = kq.truong[ma]
            item = dict(ma=ma, gia_tri=t.gia_tri, trich_dan=t.trich_dan,
                        dieu_khoan="", don_vi="", ghi_chu="")
            for key in ("don_vi", "ghi_chu"):
                extra = kq.truong.get(f"{ma}.{key}")
                if extra is not None:
                    item[key] = extra.gia_tri
            items.append(item)
        return items, 0, 0

    @staticmethod
    def _kiem_loi(kq):
        # KHONG cũng là kết quả hợp lệ khi không tìm thấy thông tin hoặc
        # dẫn chứng bị loại. Chỉ lỗi vận hành/định dạng mới là AILoi nguồn.
        loi = [ma for ma in kq.ly_do if ma in (
            "LOCAL_TAT", "LOCAL_KHONG_CHAY", "LOCAL_LOI", "PHAN_HOI_KHONG_HOP_LE")]
        if loi:
            # goi đã giữ nguyên KetQuaAI trong phan_hoi trước khi báo lỗi.
            raise AILoi(f"{', '.join(loi)}: {kq.thong_bao}")

    def tim_vi_tri(self, params, muc_luc, rows):
        names = tuple(f"{p['ma']}.{i}" for p in params for i in range(1, 4))
        ds = "\n".join(f"- {p['ma']} | {p['mo_ta']}" for p in params)
        yc = YeuCauAI("BOC_TACH_HOP_DONG", muc_luc,
                      CHI_DAN_VI_TRI + "\nTHAM SỐ:\n" + ds, names)
        kq = self.goi(yc)
        self._kiem_loi(kq)
        found = {}
        for p in params:
            ids = []
            for i in range(1, 4):
                t = kq.truong.get(f"{p['ma']}.{i}")
                # Giữ ID thực của phần mục lục đang hỏi, không nhận ID phần khác.
                if t and t.gia_tri in rows and t.gia_tri not in ids:
                    ids.append(t.gia_tri)
            found[p["ma"]] = ids
        return found
