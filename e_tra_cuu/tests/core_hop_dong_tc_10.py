"""Adapter kiểm hợp đồng C-TC-03/04; CHỈ tests, không phải Core/RLS thật.

Cache chỉ giữ tham chiếu và metadata. Runner chỉ nối callback CoreGia;
không đưa các lớp này vào gói engine hoặc dùng chúng để chứng nhận Core.
"""

from copy import deepcopy
import json


def json_khoa(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


class CacheHopDongGia:
    def __init__(self):
        self.ban = {}
        self.nhat_ky = []

    def khoa(self, ngu_canh, ma_ngu_nghia, thuc_the):
        # Dùng cùng mã ngữ nghĩa cho A/B để kiểm điều kiện thực thể độc lập.
        return (ngu_canh["phap_nhan_id"], ngu_canh["module"], ngu_canh["ma_pham_vi"],
                tuple(sorted(ngu_canh["nhom"])), ma_ngu_nghia,
                tuple(sorted(json_khoa(e) for e in thuc_the)))

    def luu(self, ngu_canh, ma_ngu_nghia, thuc_the, tham_chieu, phu_thuoc, hien_hanh):
        if phu_thuoc["phu_thuoc_thoi_diem"] or phu_thuoc["duoc_tai_dung_cache"] is False:
            return False
        ids = {n["ma_nguon"] for n in phu_thuoc["nguon"]}
        assert ids and ids <= hien_hanh.keys()
        # Không lấy nguồn của một khẳng định đại diện cho toàn bộ câu trả lời.
        self.ban[self.khoa(ngu_canh, ma_ngu_nghia, thuc_the)] = {
            "tham_chieu": deepcopy(tham_chieu),
            "nguon": {i: deepcopy(hien_hanh[i]) for i in ids}}
        return True

    def doc(self, ngu_canh, ma_ngu_nghia, thuc_the, quyen, hien_hanh, *, bo_qua_cache=False):
        if bo_qua_cache:
            self.nhat_ky.append("bo_qua_cache")
            return None
        ban = self.ban.get(self.khoa(ngu_canh, ma_ngu_nghia, thuc_the))
        if ban is None:
            return None
        # Phải kiểm mọi nguồn, kể cả nguồn thứ hai của câu có mâu thuẫn.
        if any(i not in quyen or hien_hanh.get(i) != old for i, old in ban["nguon"].items()):
            self.nhat_ky.append("nguon_het_hieu_luc_hoac_mat_quyen")
            return None
        self.nhat_ky.append("trung_cache")
        return deepcopy(ban["tham_chieu"])

    def su_kien(self, ten, ma_nguon):
        assert ten in {"tai_lieu.phien_ban_moi", "tai_lieu.doi_nhom", "ket_qua.da_duyet",
                       "cong_bo.m9.cap_nhat", "quyen.thu_hoi", "tai_lieu.het_hieu_luc"}
        self.ban = {k: v for k, v in self.ban.items() if ma_nguon not in v["nguon"]}
        self.nhat_ky.append(ten)


class DieuPhoiBaTangGia:
    def __init__(self, tang_mot, tang_hai, tang_ba):
        self.cac_tang = {1: tang_mot, 2: tang_hai, 3: tang_ba}
        self.da_chay = []
        self.viec_nen = []

    def _chay(self, tang):
        self.da_chay.append(tang)
        # Callback chạy engine thật qua CoreGia. Không đổi lỗi/ChuaRo thành dữ liệu rỗng.
        q = self.cac_tang[tang]()
        if q["trang_thai_do"] != "da_do":
            return {"http": 503, "trang_thai": "LOI", "ket_qua": None}
        return {"http": 200, "trang_thai": "XONG", "ket_qua": q["xuat"]["ket_qua"]}

    def hoi(self):
        for tang in (1, 2):
            ra = self._chay(tang)
            if ra["trang_thai"] != "XONG" or ra["ket_qua"]["co_can_cu"]:
                return ra
        self.viec_nen.append("DEMO-TC10-NEN-3")
        return {"http": 202, "viec_id": self.viec_nen[-1], "trang_thai": "CHO", "ket_qua": None}

    def chay_nen(self):
        assert self.viec_nen, "Chưa có việc nền DEMO."
        self.viec_nen.pop(0)
        return self._chay(3)


def loc_nguon_truoc_ai(danh_sach_metadata, ngu_canh, quyen, doc_noi_dung):
    """Mô phỏng thứ tự Core phải làm; không mô phỏng SQL hay RLS thật."""
    return [doc_noi_dung(n) for n in danh_sach_metadata
            if n["phap_nhan_id"] == ngu_canh["phap_nhan_id"]
            and n["nhom"] in ngu_canh["nhom"] and n["ma_nguon"] in quyen and n["con_hieu_luc"]]
