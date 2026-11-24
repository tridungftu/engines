"""AI-13: đã kiểm bằng Core giả (CoreGia), Local HTTP giả; 0 lượt Cloud."""
from copy import deepcopy
import inspect
import json

import pytest

from e_hoi_ai import ai_cuc_bo, chay, hoi_prompt
from e_hoi_ai.cong_ai import HUONG_DAN_DINH_DANG
from e_hoi_ai.khuon_json import json_chuan
from local_gia import TAI_LIEU, core_demo, nap_cau_hinh
from test_hoi_tai_lieu import khong_mang_ngoai_va_khong_cloud, local, hoi as hoi_cu
from test_hoi_yeu_cau import YEU_CAU, KHUON, DU_LIEU

PROMPT = "DEMO: 20 cộng 20 bằng bao nhiêu? Trả lời một số."


def hoi(*, prompt=PROMPT, tai_lieu="", loai="van_ban", yeu_cau=None, tham_so=None):
    vao = {"loai": loai, loai: tai_lieu if loai == "van_ban" else {"phien_ban": 1, "van_ban": tai_lieu}}
    ts = {"prompt": prompt, **(tham_so or {})}
    if yeu_cau is not None:
        vao = {"loai": "yeu_cau_ai", "yeu_cau_ai": deepcopy(yeu_cau)}
        ts = tham_so or {}
    return core_demo().chay_thu(chay.app, "ai.hoi_theo_prompt@1", vao, ts)


def ket_qua(kq):
    assert kq["trang_thai"] == "XONG", kq
    assert kq["loi"] is None
    return kq["ket_qua"]["truong"]


@pytest.mark.parametrize("ollama", [False, True])
@pytest.mark.parametrize("loai", ["van_ban", "van_ban_tai_lieu", "yeu_cau_ai"])
@pytest.mark.parametrize("tai_lieu", ["", " \r\nDEMO Ánh Dương\fNFD: A\u0301nh\u200b\n "])
def test_noi_dung_tung_byte_mot_message_user(local, ollama, loai, tai_lieu):
    prompt = " \r\n" + PROMPT + " NFD: a\u0301\u200b\r\n "
    local.tra_loi = " \r\n40\n "
    if ollama:
        local.tags = [{"name": "model-demo"}]
    yc = {**YEU_CAU, "prompt": prompt, "tai_lieu": tai_lieu, "khuon_tra_loi": None,
          "chuyen_tiep": {"ghi_chu": "DEMO KHONG GUI METADATA"}}
    ra = ket_qua(hoi(prompt=prompt, tai_lieu=tai_lieu, loai=loai,
                    yeu_cau=yc if loai == "yeu_cau_ai" else None,
                    tham_so={"tra_noi_dung_gui": True}))
    gui = prompt + ("\n\n" + tai_lieu if tai_lieu else "")
    req = local.yeu_cau[0]
    assert req["messages"] == [{"role": "user", "content": gui}]
    assert req["messages"][0]["content"].encode("utf-8") == gui.encode("utf-8")
    assert ra["noi_dung_gui_ai"].encode("utf-8") == gui.encode("utf-8")
    assert ra["tra_loi"] == local.tra_loi and ra["du_lieu_json"] == ra["canh_bao"] == ""
    assert "response_format" not in req and "format" not in req
    assert all(dong not in gui for dong in HUONG_DAN_DINH_DANG.splitlines())
    assert "DEMO KHONG GUI METADATA" not in json.dumps(req)
    assert local.luot[-1] == ("POST", "/api/chat" if ollama else "/v1/chat/completions")
    assert req.get("max_tokens", req.get("options", {}).get("num_predict")) == 8192
    assert local.so_luot_hoi == 1


@pytest.mark.parametrize("bat", [None, False, True])
def test_tra_noi_dung_gui_tuy_chon_mac_dinh_rong(local, bat):
    local.tra_loi = "40"
    ra = ket_qua(hoi(tham_so={} if bat is None else {"tra_noi_dung_gui": bat}))
    assert ra["noi_dung_gui_ai"] == (PROMPT if bat else "")
    assert ra["tra_loi"] == "40" and ra["du_lieu_json"] == ""


def test_40_nguyen_van_khac_nang_luc_trich_dan_cu(local):
    local.tra_loi = "40"
    ra = ket_qua(hoi())
    cu = ket_qua(hoi_cu(van_ban="", tham_so={
        "ma_prompt": "demo.cong", "phien_ban_prompt": "1", "prompt": PROMPT,
    }))
    assert ra["tra_loi"] == "40"
    assert cu["tra_loi"].startswith("không thấy căn cứ") and cu["co_can_cu"] is False
    assert len(local.yeu_cau[0]["messages"]) == 1
    assert len(local.yeu_cau[1]["messages"]) == 2


@pytest.mark.parametrize("prompt", [None, "", " \n\t"])
@pytest.mark.parametrize("phong_bi", [False, True])
def test_thieu_prompt_truoc_moi_mang(local, prompt, phong_bi):
    yc = {**YEU_CAU, "prompt": prompt} if phong_bi else None
    kq = hoi(prompt=prompt, yeu_cau=yc)
    assert kq["trang_thai"] == "LOI" and kq["loi"]["ma"] == "THIEU_PROMPT"
    assert not local.luot and kq["ket_qua"] is None


def test_khong_gui_tham_so_prompt_cung_tra_thieu_prompt(local):
    kq = core_demo().chay_thu(chay.app, "ai.hoi_theo_prompt@1", {"loai": "van_ban", "van_ban": ""}, {})
    assert kq["loi"]["ma"] == "THIEU_PROMPT" and not local.luot


def test_hai_nguon_uu_tien_toan_bo_phong_bi_canh_bao_rieng(local, capsys):
    local.tra_loi = "40"
    local.models.append({"id": "model-demo-uu-tien", "context_length": 65536})
    yc = {**YEU_CAU, "prompt": PROMPT, "tai_lieu": "", "khuon_tra_loi": None,
          "model_uu_tien": "model-demo-uu-tien"}
    ra = ket_qua(hoi(yeu_cau=yc, tham_so={
        "prompt": "DEMO KHONG DUNG PROMPT NAY", "ma_prompt": "DEMO bỏ qua mã sai dạng",
        "phien_ban_prompt": "DEMO bỏ qua", "model_uu_tien": "model-khong-co",
        "tra_noi_dung_gui": True,
    }))
    assert ra["tra_loi"] == "40" and "bỏ qua" in ra["canh_bao"]
    assert ra["model"] == "model-demo-uu-tien" and ra["ly_do_chon_model"] == "model_uu_tien"
    assert ra["noi_dung_gui_ai"] == PROMPT
    assert local.yeu_cau[0]["messages"] == [{"role": "user", "content": PROMPT}]
    log = capsys.readouterr().err
    assert json.loads(log)["ma_prompt"] == YEU_CAU["ma_prompt"]
    assert "KHONG DUNG PROMPT" not in log and PROMPT not in log


def test_phong_bi_thieu_prompt_khong_lay_prompt_tham_so(local):
    kq = hoi(yeu_cau={**YEU_CAU, "prompt": ""}, tham_so={"prompt": PROMPT})
    assert kq["loi"]["ma"] == "THIEU_PROMPT" and not local.luot


@pytest.mark.parametrize("ollama", [False, True])
@pytest.mark.parametrize("hoi_lai", [False, True])
def test_khuon_gui_nguyen_schema_khong_boc_tra_json_da_kiem(local, ollama, hoi_lai):
    if ollama:
        local.tags = [{"name": "model-demo"}]
    text = ' \n' + json.dumps(DU_LIEU, ensure_ascii=False, indent=2) + '\r\n '
    local.tra_loi_tung_luot = ([{"sai": True}] if hoi_lai else []) + [text]
    ra = ket_qua(hoi(yeu_cau=YEU_CAU))
    assert ra["tra_loi"] == text
    assert json.loads(ra["du_lieu_json"]) == DU_LIEU
    assert ra["canh_bao"] == "" and ra["noi_dung_gui_ai"] == ""
    assert local.so_luot_hoi == (2 if hoi_lai else 1)
    gui = YEU_CAU["prompt"] + "\n\n" + TAI_LIEU
    for req in local.yeu_cau:
        assert req["messages"] == [{"role": "user", "content": gui}]
        schema = req["format"] if ollama else req["response_format"]["json_schema"]["schema"]
        assert json_chuan(schema) == json_chuan(KHUON)
    if hoi_lai:
        assert local.yeu_cau[0] == local.yeu_cau[1]


@pytest.mark.parametrize("phan_hoi", ["DEMO không phải JSON", '{"a":1,"a":2}',
                                     '```json\n{"so":40}\n```', '{"so":true}', '{"so":1e999}'])
def test_sai_khuon_hoi_lai_dung_mot_lan(local, phan_hoi):
    local.tra_loi = phan_hoi
    yc = {**YEU_CAU, "khuon_tra_loi": {"type": "object", "required": ["so"],
                                       "properties": {"so": {"type": "integer"}}}}
    kq = hoi(yeu_cau=yc)
    assert kq["loi"]["ma"] == "AI_TRA_SAI_KHUON" and kq["ket_qua"] is None
    assert local.so_luot_hoi == 2 and local.yeu_cau[0] == local.yeu_cau[1]


def test_khuon_khong_hop_le_chan_truoc_mang(local):
    kq = hoi(yeu_cau={**YEU_CAU, "khuon_tra_loi": {"type": "string", "pattern": "DEMO"}})
    assert kq["loi"]["ma"] == "KHUON_KHONG_HOP_LE" and not local.luot


@pytest.mark.parametrize("khuon,phan_hoi", [
    ({"type": "integer"}, "40"),
    ({"type": "array", "items": {"type": "integer"}}, "[40]"),
    ({"$defs": {"so": {"type": "integer"}}, "$ref": "#/$defs/so"}, "40"),
    ({"type": "object", "required": ["so"], "properties": {"so": {"const": 999}}}, '{"so":999}'),
])
def test_khong_hau_kiem_so_ngoai_nguon_khi_khop_schema(local, khuon, phan_hoi):
    local.tra_loi = phan_hoi
    ra = ket_qua(hoi(yeu_cau={**YEU_CAU, "khuon_tra_loi": khuon, "tai_lieu": "DEMO không có số."}))
    assert ra["tra_loi"] == phan_hoi and json.loads(ra["du_lieu_json"]) == json.loads(phan_hoi)
    assert local.so_luot_hoi == 1


@pytest.mark.parametrize("thoi_diem", ["truoc", "metadata", "post", "hoi_lai"])
def test_huy_khong_nop_hoac_gui_them(local, monkeypatch, thoi_diem):
    core = core_demo()
    goc = core._tien_do
    ids = []
    def tien_do(ma, viec_id, phan_tram, cau):
        ids.append(viec_id)
        if thoi_diem == "truoc" or thoi_diem == "hoi_lai" and phan_tram == 50:
            core.huy(viec_id)
        return goc(ma, viec_id, phan_tram, cau)
    monkeypatch.setattr(core, "_tien_do", tien_do)
    def khi_nhan(phuong_thuc, duong):
        if thoi_diem == "metadata" and phuong_thuc == "GET" or thoi_diem == "post" and phuong_thuc == "POST":
            core.huy(ids[0])
    local.khi_nhan = khi_nhan
    kq = hoi(yeu_cau=YEU_CAU if thoi_diem == "hoi_lai" else None)
    assert kq["trang_thai"] == "HUY" and kq["ket_qua"] is None
    assert local.so_luot_hoi == (1 if thoi_diem in ("post", "hoi_lai") else 0)
    assert core.so_lan_ghi["ket_qua"] == 0


def test_local_connect_loi_thu_lai_duoc_khong_cloud(local, monkeypatch):
    def loi(*args, **kwargs):
        raise ai_cuc_bo.LocalAIKhongSanSang("DEMO lỗi kết nối.")
    monkeypatch.setattr(ai_cuc_bo, "_gui_post", loi)
    kq = hoi()
    assert kq["loi"]["ma"] == "LOCAL_AI_KHONG_SAN_SANG" and kq["loi"]["thu_lai_duoc"] is True
    assert kq["ket_qua"] is None and local.so_luot_hoi == 0


@pytest.mark.parametrize("cat", [False, True])
def test_nguon_co_the_da_nhan_khong_hoi_lai_khong_nop(local, cat):
    local.cat_sau_post = cat
    local.ma_http = 202
    kq = hoi(yeu_cau=YEU_CAU)
    assert kq["trang_thai"] == "CHUA_RO" and kq["ket_qua"] is None
    assert local.so_luot_hoi == 1 and kq["ma_tuong_quan"].startswith("local-")


@pytest.mark.parametrize("kieu", ["byte", "context", "thieu_context"])
@pytest.mark.parametrize("ollama", [False, True])
def test_ngan_sach_ai_9_chan_truoc_post(local, kieu, ollama):
    if ollama:
        local.tags = [{"name": "model-demo"}]
        muc = local.dang_chay[0]
    else:
        muc = local.models[0]
    if kieu == "thieu_context":
        muc.pop("context_length")
    elif kieu == "context":
        muc["context_length"] = 8192
    kq = hoi(prompt="DEMO " + "á" * 33000 if kieu == "byte" else PROMPT)
    assert kq["loi"]["ma"] == ("LOCAL_AI_KHONG_SAN_SANG" if kieu == "thieu_context" else "VUOT_GIOI_HAN")
    assert local.so_luot_hoi == 0 and kq["ket_qua"] is None


@pytest.mark.parametrize("truong", ["prompt", "tai_lieu"])
@pytest.mark.parametrize("phong_bi", [False, True])
def test_tran_500000_ky_tu_truoc_mang(local, truong, phong_bi):
    ts = {"prompt": PROMPT, "tai_lieu": ""}
    ts[truong] = "DEMO" + "a" * 500000
    kq = hoi(yeu_cau={**YEU_CAU, **ts} if phong_bi else None, **ts)
    assert kq["loi"]["ma"] == "VUOT_GIOI_HAN" and not local.luot


def test_nhat_ky_khong_noi_dung_ke_ca_bat_tra_noi_dung(local, capsys):
    local.tra_loi = "DEMO: câu trả lời nguyên văn 999 VND"
    ket_qua(hoi(tai_lieu=TAI_LIEU, tham_so={"tra_noi_dung_gui": True}))
    log = capsys.readouterr()
    assert not log.out and json.loads(log.err)["ket_qua_kiem"] == "DAT"
    assert all(x not in log.err for x in (PROMPT, TAI_LIEU, local.tra_loi, local.url))


def test_nang_luc_moi_khong_goi_khung_hoac_hau_kiem():
    ma = inspect.getsource(hoi_prompt)
    assert all(ten not in ma for ten in ("HUONG_DAN_DINH_DANG", "ghep_khung", "danh_gia"))
