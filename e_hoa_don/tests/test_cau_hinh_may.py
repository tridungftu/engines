"""Cấu hình chỉ ở thư mục DEMO tạm; không đọc tệp cấu hình máy thật."""

import json
from pathlib import PurePosixPath, PureWindowsPath
import pytest
from kho_tri_thuc_sdk.engine import LoiNghiepVu
from kho_tri_thuc_sdk.thu import CoreGia

from e_hoa_don import cau_hinh_may
from e_hoa_don.cau_hinh_may import CAU_HINH_TOI_DA_BYTE, THU_MUC_GOI, doc_cau_hinh
from e_hoa_don.chay import app


def test_thieu_khong_chan_xml(xml_demo):
    assert doc_cau_hinh() is None
    with pytest.raises(LoiNghiepVu) as exc:
        doc_cau_hinh(bat_buoc=True)
    assert exc.value.ma == "CHUA_CAU_HINH"
    assert exc.value.thong_diep == "Chưa cấu hình chức năng này."
    core = CoreGia()
    tep = core.them_tep("DEMO.xml", xml_demo)
    assert core.chay_thu(app, "hoa_don.doc_xml@2", {"loai": "tep", "tep": tep})["trang_thai"] == "XONG"


def test_mac_dinh_programdata_trong_demo(tmp_path, monkeypatch):
    monkeypatch.delenv("KTT_ENGINE_CAU_HINH")
    duong = tmp_path / "PROGRAMDATA-DEMO/KhoTriThuc/engines/e_hoa_don/cau_hinh.json"
    assert doc_cau_hinh() is None
    assert not duong.parent.exists()  # không tự tạo thư mục cấu hình/kho tạm.
    duong.parent.mkdir(parents=True)
    duong.write_text('{"phien_ban": 1}', encoding="utf-8")
    assert doc_cau_hinh() == {"phien_ban": 1}


@pytest.mark.parametrize("he_dieu_hanh,lop_duong,goc,mong_doi", [
    ("posix", PurePosixPath, None, "/var/lib/KhoTriThuc/engines/e_hoa_don/cau_hinh.json"),
    ("nt", PureWindowsPath, None, "C:/ProgramData/KhoTriThuc/engines/e_hoa_don/cau_hinh.json"),
    ("posix", PurePosixPath, "/srv/PROGRAMDATA-DEMO", "/srv/PROGRAMDATA-DEMO/KhoTriThuc/engines/e_hoa_don/cau_hinh.json"),
    ("nt", PureWindowsPath, "D:/PROGRAMDATA-DEMO", "D:/PROGRAMDATA-DEMO/KhoTriThuc/engines/e_hoa_don/cau_hinh.json"),
], ids=["linux-thieu-bien", "windows-thieu-bien", "linux-uu-tien-programdata", "windows-uu-tien-programdata"])
def test_chon_duong_mac_dinh(he_dieu_hanh, lop_duong, goc, mong_doi, monkeypatch):
    # PurePath chỉ tính đường, không đọc/ghi /var/lib hay cấu hình máy thật.
    with monkeypatch.context() as patch:
        patch.delenv("KTT_ENGINE_CAU_HINH")
        patch.delenv("PROGRAMDATA")
        if goc is not None:
            patch.setenv("PROGRAMDATA", goc)
        patch.setattr(cau_hinh_may.os, "name", he_dieu_hanh)
        patch.setattr(cau_hinh_may, "Path", lop_duong)
        ket_qua = cau_hinh_may._tep_mac_dinh()
    assert ket_qua.as_posix() == mong_doi


@pytest.mark.parametrize("he_dieu_hanh", ["posix", "nt"])
@pytest.mark.parametrize("co_programdata", [False, True])
def test_duong_chi_dinh_uu_tien(tmp_path, monkeypatch, he_dieu_hanh, co_programdata):
    tep = tmp_path / "cau-hinh-uu-tien-DEMO.json"
    tep.write_text('{"phien_ban": 1}', encoding="utf-8")

    def khong_chon_mac_dinh():
        raise AssertionError("Đã chỉ định tệp thì không được chọn đường mặc định.")

    with monkeypatch.context() as patch:
        patch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
        if not co_programdata:
            patch.delenv("PROGRAMDATA")
        patch.setattr(cau_hinh_may.os, "name", he_dieu_hanh)
        # Giữ lớp Path của máy chạy test để chỉ mở tệp DEMO tạm.
        patch.setattr(cau_hinh_may, "Path", type(tmp_path))
        patch.setattr(cau_hinh_may, "_tep_mac_dinh", khong_chon_mac_dinh)
        ket_qua = doc_cau_hinh()
    assert ket_qua == {"phien_ban": 1}


@pytest.mark.parametrize("raw", [
    b"{", b"[]", b"{}", b'{"phien_ban":true}', b'{"phien_ban":1.0}',
    b'{"phien_ban":2}', b'{"phien_ban":1,"khoa_DEMO":"KHONG_LUU"}',
    b'{"phien_ban":1,"phien_ban":1}', b'{"phien_ban":NaN}', b"\xff\xfe",
    b" " * (CAU_HINH_TOI_DA_BYTE + 1),
], ids=["hong", "mang", "thieu", "bool", "float", "sai-ban", "khoa-la", "khoa-lap", "nan", "ma-hoa", "qua-lon"])
def test_cau_hinh_sai_loi_co_dinh(raw, tmp_path, monkeypatch):
    tep = tmp_path / "cau-hinh-DEMO.json"
    tep.write_bytes(raw)
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(tep))
    with pytest.raises(LoiNghiepVu) as exc:
        doc_cau_hinh()
    assert exc.value.ma == "CAU_HINH_MAY_KHONG_HOP_LE"
    assert exc.value.thong_diep == "Cấu hình máy không hợp lệ. Hãy liên hệ quản trị viên."
    assert str(tmp_path) not in str(exc.value) and "KHONG_LUU" not in str(exc.value)


def test_duong_trong_goi_bi_chan_truoc_doc(monkeypatch):
    monkeypatch.setenv("KTT_ENGINE_CAU_HINH", str(THU_MUC_GOI / "engine.json"))
    with pytest.raises(LoiNghiepVu) as exc:
        doc_cau_hinh()
    assert exc.value.ma == "CAU_HINH_MAY_KHONG_HOP_LE"


def test_cau_hinh_schema_khop():
    schema = json.loads((THU_MUC_GOI / "contract/cau_hinh_may.schema.json").read_text(encoding="utf-8"))
    assert schema["required"] == ["phien_ban"] and schema["additionalProperties"] is False
    assert schema["properties"] == {"phien_ban": {"type": "integer", "const": 1}}
