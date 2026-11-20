"""Đã kiểm bằng Core giả (CoreGia); không chứng nhận quyền/vòng đời Core thật.

CoreGia 2.2.0 _mo_tep chỉ so json.dumps(tep_id) là chuỗi con của đầu vào,
kho tệp toàn cục; mỗi chay_thu/giao_viec tạo việc độc lập. Vì vậy test mở
được tệp không chứng minh điều kiện cùng việc của Core thật.
CC-1: CoreGia nhận byte JSON module tự lập, không mô phỏng multipart/nút JS.
CC-2: kiểm riêng hình dạng nghiêm và phải chạy lại chuỗi trên Core tập.
"""

from copy import deepcopy
from hashlib import sha256
import json

import pytest
from kho_tri_thuc_sdk.engine import Engine
from kho_tri_thuc_sdk.thu import CoreGia

from e_phan_luong.chay import app


def co_tham_chieu_tep(dau_vao, tep_id):
    """PL-5 dùng lại: phần kiểm hình dạng của $.** ? (@.tep_id == $t).

    Phải có đối tượng mang đúng khóa tep_id với mã tệp bằng chính xác id,
    ở bất kỳ độ sâu nào (kể cả trong mảng). Chuỗi trơn không đủ quyền.
    Hàm chỉ xét hình dạng JSON, không kiểm tệp tồn tại/cùng việc/pháp nhân.
    """
    if not isinstance(tep_id, str) or not tep_id:
        return False
    cho = [dau_vao]
    while cho:
        nut = cho.pop()
        if isinstance(nut, dict):
            if nut.get("tep_id") == tep_id:
                return True
            cho.extend(nut.values())
        elif isinstance(nut, list):
            cho.extend(nut)
    return False


def phong_bi_tra_loi(chuyen_tiep):
    """Phong bì AI DEMO dựng tay, không gọi model hay engine khác."""
    return {"loai": "tra_loi_ai", "tra_loi_ai": {
        "phien_ban": 1, "trang_thai": "co_can_cu", "tra_loi": "Phân loại DEMO.",
        "du_lieu": {"phan_loai": []}, "trich_dan": [],
        "kiem_trich_dan": {"dat": True, "loi": []}, "nha_cung_cap": "local",
        "model": "DEMO-model-gia", "ly_do_chon_model": "Mô phỏng DEMO nội bộ",
        "ma_prompt": "demo.phan_loai", "phien_ban_prompt": "DEMO-1",
        "phien_ban_engine": "DEMO-AI 0.1.0", "bam_dau_vao": "sha256:" + "0" * 64,
        "chuyen_tiep": chuyen_tiep, "canh_bao": []}}


def app_thu():
    """Năng lực thử riêng ở ngoài gói, không làm năng lực runtime thành công giả."""
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = [
        {"ma": "demo.chuan_bi@1", "ten": "Tải tệp DEMO lên CoreGia", "nhan": ["tep"], "tra": "yeu_cau_ai",
         "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 300}},
        {"ma": "demo.ai_gia@1", "ten": "Trả lời AI DEMO dựng tay", "nhan": ["yeu_cau_ai"], "tra": "tra_loi_ai",
         "gioi_han": {"thoi_han_giay": 300}},
        {"ma": "demo.mo_lai@1", "ten": "Mở tệp DEMO từ chuyển tiếp", "nhan": ["tra_loi_ai"], "tra": "van_ban",
         "gioi_han": {"tep_toi_da_mib": 20, "thoi_han_giay": 300}}]
    thu = Engine(phieu)

    @thu.nang_luc("demo.chuan_bi@1")
    def chuan_bi(viec):
        with viec.mo_tep(viec.dau_vao["tep"]["tep_id"]) as f:
            raw = f.read()
        tep = viec.tai_tep_ra("lo-DEMO-chuyen-tiep.json", raw, "application/json")
        ct = {"phan_luong": {"phien_ban": 1, "tep_lo": tep,
              "bam_tep": "sha256:" + sha256(raw).hexdigest(), "khau": "ktt_duyet", "khong_can_ai": False}}
        assert len(json.dumps(ct, ensure_ascii=False).encode("utf-8")) <= 4096
        return {"loai": "yeu_cau_ai", "yeu_cau_ai": {
            "phien_ban": 1, "ma_prompt": "demo.phan_loai", "phien_ban_prompt": "DEMO-1",
            "prompt": "Phân loại DEMO.", "tai_lieu": "Dữ liệu DEMO.", "khuon_tra_loi": None,
            "bat_buoc_trich_dan": False, "model_uu_tien": None, "chuyen_tiep": ct}}

    @thu.nang_luc("demo.ai_gia@1")
    def ai_gia(viec):
        return phong_bi_tra_loi(deepcopy(viec.dau_vao["yeu_cau_ai"]["chuyen_tiep"]))

    @thu.nang_luc("demo.mo_lai@1")
    def mo_lai(viec):
        pl = viec.dau_vao["tra_loi_ai"]["chuyen_tiep"]["phan_luong"]
        tep = pl["tep_lo"]
        assert set(tep) == {"tep_id", "ten", "mime", "kich_thuoc"}
        assert co_tham_chieu_tep(viec.dau_vao, tep["tep_id"])
        with viec.mo_tep(tep["tep_id"]) as f:
            raw = f.read()
        assert "sha256:" + sha256(raw).hexdigest() == pl["bam_tep"]
        assert len(raw) == tep["kich_thuoc"]
        return {"loai": "van_ban", "van_ban": raw.decode("utf-8")}

    return thu


def test_byte_json_module_tu_lap_va_tep_long_trong_chuyen_tiep():
    core = CoreGia()
    thu = app_thu()
    raw = json.dumps({"phien_ban": 1, "ma_module": "demo_thanh_toan", "nghiep_vu": []},
                     ensure_ascii=False).encode("utf-8")
    tep = core.them_tep("lo-DEMO.json", raw, "application/json")
    dau_vao = {"loai": "tep", "tep": tep}
    for buoc, ma in enumerate(("demo.chuan_bi@1", "demo.ai_gia@1", "demo.mo_lai@1"), 1):
        id_viec = core.giao_viec(ma, dau_vao, buoc=buoc)
        core.chay(thu)
        kq = core.xem(id_viec)
        assert kq["trang_thai"] == "XONG", kq
        dau_vao = kq["ket_qua"]
    assert dau_vao == {"loai": "van_ban", "van_ban": raw.decode("utf-8")}


@pytest.mark.parametrize("pb,mong", [
    ({"chuyen_tiep": {"phan_luong": {"tep_lo": {"tep_id": "tep-DEMO"}}}}, True),
    ({"chuyen_tiep": [{"sau": [{"tep_id": "tep-DEMO"}]}]}, True),
    ({"chuyen_tiep": {"tep_lo": "tep-DEMO"}}, False),
    ({"tep_id_khac": "tep-DEMO"}, False),
    ({"tep_id": "tien-to-tep-DEMO-hau-to"}, False),
    ({"tep_id": "tep-DEMO-khac"}, False),
    ({"tep_id": None}, False),
])
def test_hinh_dang_nghiem_cho_pl5(pb, mong):
    assert co_tham_chieu_tep(pb, "tep-DEMO") is mong


def test_core_gia_cho_chuoi_tron_nhung_kiem_nghiem_tu_choi():
    core = CoreGia()
    tep = core.them_tep("tep-DEMO.json", b'{"DEMO":true}', "application/json")
    pb = phong_bi_tra_loi({"tep_lo": tep["tep_id"]})
    assert not co_tham_chieu_tep(pb, tep["tep_id"])
    phieu = deepcopy(app.phieu)
    phieu["nang_luc"] = [{"ma": "demo.long@1", "ten": "Đo độ lỏng CoreGia DEMO",
        "nhan": ["tra_loi_ai"], "tra": "van_ban", "gioi_han": {"thoi_han_giay": 300}}]
    thu = Engine(phieu)

    @thu.nang_luc("demo.long@1")
    def mo(viec):
        with viec.mo_tep(viec.dau_vao["tra_loi_ai"]["chuyen_tiep"]["tep_lo"]) as f:
            assert f.read() == b'{"DEMO":true}'
        return {"loai": "van_ban", "van_ban": "CoreGia lỏng hơn Core thật."}

    assert core.chay_thu(thu, "demo.long@1", pb)["trang_thai"] == "XONG"
