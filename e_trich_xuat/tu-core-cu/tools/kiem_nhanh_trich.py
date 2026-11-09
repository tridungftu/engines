"""LHD-01: so/chấm kết quả đã có, không chạy pipeline, AI, COM hay CSDL.

Lead chạy sau khi tạo hai kết quả trên cùng DOCX, model và cấu hình Local.
Không tự tìm hợp đồng/đáp án, chuyển DOC, gọi lại engine hay sửa đầu vào.
Điều kiện thực của lượt chạy do lead xác nhận; công cụ không suy từ máy.

Ví dụ (các đường dẫn và nội dung đều DEMO; đặt PYTHONPATH theo handoff):
  python -X utf8 -B tools/kiem_nhanh_trich.py \
    --dap-an DAP_AN_DEMO.tsv --tep-nguon DEMO.docx \
    --ket-qua-goc DEMO_KET_QUA.json --ket-qua-engine DEMO-phan-hoi.json \
    --cau-truc-goc DEMO-goc_cau_truc.json \
    --cau-truc-engine DEMO-engine_cau_truc.json \
    --nguon-goc DEMO-quy_trinh.py DEMO-danh_muc.py DEMO-kiem_tra.py \
    --nguon-engine DEMO-tich_hop.py --phien-ban-goc DEMO-goc \
    --phien-ban-engine DEMO-engine --model DEMO-Local \
    --cau-hinh '{"cloud": false, "ra_lai": true, "tham_so_them": []}'

Nguồn gốc: đúng thứ tự quy_trinh.py, danh_muc.py, kiem_tra.py; nguồn engine:
pipeline trước, các tệp mã liên quan sau. Cấu hình JSON chung được khai báo
cho cả hai lượt chạy (không phải tệp cấu hình thật). stdout chỉ số tổng hợp
và mã tham số lệch/mức quan trọng. --ra tùy chọn lưu báo cáo chỉ gồm số,
cờ và SHA-256, không chứa đường dẫn, giá trị, dẫn chứng, model/cấu hình.
Không ghi đè báo cáo cũ. Không in lỗi gốc vì có thể chứa dữ liệu đầu vào.
Mã thoát: 0 đạt §6.4; 1 lệch/chưa đo đủ; 2 lỗi đầu vào hoặc không chấm được.
--lan-do 2 dùng sau khi lead chạy lại engine một lần; không tự chạy lại.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from kho_tri_thuc.engines.e_trich_xuat import do_chinh_xac as do
from kho_tri_thuc.m4.review_goc.trich_xuat import danh_muc, kiem_tra


def _khong_trung_cap(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("JSON có khóa trùng.")
        result[key] = value
    return result


def _json(text):
    def invalid(_):
        raise ValueError("JSON có số không hợp lệ.")
    return json.loads(text, object_pairs_hook=_khong_trung_cap, parse_constant=invalid)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _co_gia_tri(value):
    return isinstance(value, str) and bool(value.strip())


def _doc_cau_truc(path, codes):
    data = _json(Path(path).read_text(encoding="utf-8-sig"))
    if (not isinstance(data, dict) or not _co_gia_tri(data.get("file"))
            or not isinstance(data.get("phieu_kiem_tra"), dict)
            or not data["phieu_kiem_tra"]
            or not isinstance(data.get("cau_truc"), list) or not data["cau_truc"]
            or not isinstance(data.get("vi_tri_tham_so"), list)):
        raise ValueError("Thiếu cấu trúc tất định.")
    ids = set()
    for row in data["cau_truc"]:
        fields = ("id", "dieu", "tieu_de_dieu", "khoan", "tieu_de_khoan", "noi_dung")
        if (not isinstance(row, dict) or any(not isinstance(row.get(k), str) for k in fields)
                or not row["id"] or row["id"] in ids):
            raise ValueError("Dòng cấu trúc không hợp lệ.")
        ids.add(row["id"])
    seen = set()
    for row in data["vi_tri_tham_so"]:
        if not isinstance(row, dict):
            raise ValueError("Vị trí tham số không hợp lệ.")
        code = row.get("ma")
        if not isinstance(code, str) or code not in codes or code in seen:
            raise ValueError("Mã vị trí không hợp lệ.")
        seen.add(code)
        for key in ("vi_tri", "row_ids"):
            items = row.get(key)
            if (not isinstance(items, list) or len(items) > 3
                    or any(not isinstance(x, str) for x in items)):
                raise ValueError("Danh sách vị trí không hợp lệ.")
        if (len(row["vi_tri"]) != len(row["row_ids"])
                or not set(row["row_ids"]) <= ids):
            raise ValueError("Vị trí không thuộc cấu trúc.")
    if seen != codes:
        raise ValueError("Thiếu mã vị trí tham số.")
    return data


def kiem_nhanh(*, dap_an, tep_nguon, ket_qua_goc, ket_qua_engine,
               cau_truc_goc, cau_truc_engine, nguon_goc, nguon_engine,
               phien_ban_goc, phien_ban_engine, model, cau_hinh, lan_do=1):
    """Báo cáo allowlist; mọi nội dung hợp đồng chỉ dùng nội bộ để so/chấm.

    Hai JSON cấu trúc so nguyên nội dung, gồm phiếu, thứ tự Điều/Khoản và
    ba ứng viên; chỉ bỏ khác biệt định dạng JSON/thứ tự khóa object.
    Thiếu đáp án/kết quả không được tính là đúng hoặc khớp (kể cả cả hai
    cùng thiếu). Chưa đủ phép đo thì không kết luận đạt.
    """
    if (type(lan_do) is not int or lan_do not in (1, 2)
            or len(nguon_goc) != 3 or not nguon_engine
            or Path(tep_nguon).suffix.lower() != ".docx"):
        raise ValueError("Thiếu điều kiện kiểm nhanh.")
    if (not isinstance(cau_hinh, dict) or cau_hinh.get("cloud", True) is not False
            or cau_hinh.get("ra_lai") is not True or cau_hinh.get("tham_so_them") != []):
        raise ValueError("Cần Local, rà lại bật và không có tham số hỏi thêm.")
    config = json.dumps(cau_hinh, ensure_ascii=False, sort_keys=True, allow_nan=False)
    codes = {p[0] for p in danh_muc.MAC_DINH}
    structures = [_doc_cau_truc(p, codes) for p in (cau_truc_goc, cau_truc_engine)]
    # JSON phân biệt false/0 và true/1; phép == của Python thì không.
    same_structure = (json.dumps(structures[0], sort_keys=True, ensure_ascii=False)
                      == json.dumps(structures[1], sort_keys=True, ensure_ascii=False))
    # Kiểm JSON chặt trước khi bộ chấm đọc, không cho khóa trùng bị ghi đè.
    for path in (ket_qua_goc, ket_qua_engine):
        _json(Path(path).read_text(encoding="utf-8-sig"))
    common = dict(dap_an=dap_an, tep_nguon=tep_nguon, model=model, cau_hinh=cau_hinh)
    original = do.do_chinh_xac(ket_qua=ket_qua_goc, nguon=nguon_goc[0],
                              phien_ban_nguon=phien_ban_goc, **common)
    engine = do.do_chinh_xac(ket_qua=ket_qua_engine, nguon=nguon_engine[0],
                            phien_ban_nguon=phien_ban_engine, **common)
    gold_count = sum(_co_gia_tri(r["dap_an"]) for r in original["tham_so"])
    matches = compared = 0
    differences, regressions = [], []
    levels = {p[0]: p[5] for p in danh_muc.MAC_DINH}
    for a, b in zip(original["tham_so"], engine["tham_so"]):
        available = _co_gia_tri(a["gia_tri"]) and _co_gia_tri(b["gia_tri"])
        same = bool(available and kiem_tra.giong_nhau(a["gia_tri"], b["gia_tri"]))
        compared += int(available)
        matches += int(same)
        code = a["ma"]
        if not same:
            differences.append({"ma": code, "muc": levels[code], "chua_so": not available})
        if levels[code] == 3 and a["dat"] == 1 and b["dat"] != 1:
            regressions.append(code)
    enough = (gold_count > 0 and compared == len(codes)
              and all(r["tong_hop"]["da_do"] == gold_count for r in (original, engine)))
    not_worse = (engine["tong_hop"]["dat"] is not None
                 and original["tong_hop"]["dat"] is not None
                 and engine["tong_hop"]["dat"] >= original["tong_hop"]["dat"])
    passed = enough and same_structure and not_worse and not regressions
    def counts(report):
        return {"dung": report["tong_hop"]["dat"], "sai": report["tong_hop"]["sai"],
                "chua_do": report["tong_hop"]["chua_do"]}
    return {
        "tong_ma": len(codes), "co_dap_an": gold_count,
        "goc": counts(original), "engine": counts(engine),
        "cau_truc_khop": same_structure, "khop": matches,
        "khac": compared - matches, "chua_so": len(codes) - compared,
        "lech": differences, "giam_muc_3": regressions,
        "du_phep_do": enough, "dat": passed, "lan_do": lan_do,
        "can_chay_lai": not passed and lan_do == 1,
        "dung": not passed and lan_do == 2,
        "sha256": {
            "hop_dong": original["tep_nguon"]["sha256"],
            "dap_an": original["dap_an"]["sha256"],
            "ket_qua_goc": original["ket_qua"]["sha256"],
            "ket_qua_engine": engine["ket_qua"]["sha256"],
            "cau_truc_goc": _sha(cau_truc_goc), "cau_truc_engine": _sha(cau_truc_engine),
            "nguon_goc": [_sha(p) for p in nguon_goc],
            "nguon_engine": [_sha(p) for p in nguon_engine],
            "cau_hinh": hashlib.sha256(config.encode("utf-8")).hexdigest(),
            "dieu_kien": hashlib.sha256(json.dumps(
                [phien_ban_goc, phien_ban_engine, model], ensure_ascii=False).encode("utf-8")).hexdigest(),
            "cong_cu_cham": original["cach_cham"]["cong_cu"]["sha256"],
            "nguon_cham": original["cach_cham"]["sha256"],
        },
    }


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # argparse mặc định có thể in đường dẫn/nội dung tham số không hợp lệ.
        self.exit(2, "Lỗi: thiếu hoặc sai tham số; xem --help.\n")


def main(argv=None):
    parser = _Parser(description="So/chấm kết quả đã có; chỉ in số và mã tham số lệch.",
                     allow_abbrev=False)
    for name in ("dap-an", "tep-nguon", "ket-qua-goc", "ket-qua-engine",
                 "cau-truc-goc", "cau-truc-engine", "phien-ban-goc",
                 "phien-ban-engine", "model", "cau-hinh"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--nguon-goc", nargs=3, required=True,
                        help="quy_trinh.py danh_muc.py kiem_tra.py, theo thứ tự")
    parser.add_argument("--nguon-engine", nargs="+", required=True, help="pipeline trước")
    parser.add_argument("--lan-do", type=int, choices=(1, 2), default=1)
    parser.add_argument("--ra", help="báo cáo chỉ số/mã băm mới; không ghi đè")
    args = vars(parser.parse_args(argv))
    output = args.pop("ra")
    try:
        args["cau_hinh"] = _json(args["cau_hinh"])
        report = kiem_nhanh(**args)
        if output:
            with Path(output).open("x", encoding="utf-8") as stream:
                json.dump(report, stream, ensure_ascii=False, indent=2, allow_nan=False)
                stream.write("\n")
    except Exception:
        print("Không chấm được: kiểm tra đầu vào và điều kiện chạy.", file=sys.stderr)
        return 2
    print(f"Tham số có đáp án: {report['co_dap_an']}/{report['tong_ma']}")
    for key, label in (("goc", "Gốc"), ("engine", "Engine")):
        stats = report[key]
        # Không dùng 0 thay cho số chưa đo.
        measured = stats["dung"] is not None
        print(f"{label}: đúng {stats['dung'] if measured else 'chưa đo'}; "
              f"sai {stats['sai'] if measured else 'chưa đo'}; chưa đo {stats['chua_do']}")
    print(f"Cấu trúc trùng: {int(report['cau_truc_khop'])}")
    print(f"Khớp: {report['khop']}; khác: {report['khac']}; chưa so: {report['chua_so']}")
    for row in report["lech"]:
        print(f"{row['ma']}: mức {row['muc']}; chưa so {int(row['chua_so'])}")
    print(f"Giảm ở mức 3: {len(report['giam_muc_3'])}; đủ phép đo: {int(report['du_phep_do'])}")
    print(f"Đạt: {int(report['dat'])}; lần đo: {report['lan_do']}; "
          f"cần chạy lại: {int(report['can_chay_lai'])}; dừng: {int(report['dung'])}")
    return 0 if report["dat"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
