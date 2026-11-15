"""Soạn DEMO từ bảng tác giả, không đọc đầu ra engine để tạo bản vàng.

Chỉ chạy thủ công khi lập bộ nguồn; E6/pytest không tự ghi lại fixture.
Thư viện chuẩn; ZIP cố định thời gian, không cần Word hoặc mạng.
"""

from pathlib import Path
import json
import sys
from xml.sax.saxutils import escape

sys.dont_write_bytecode = True
from mau_docx import CT, goi_docx, p, W_NS
from kiem_e6 import ENGINE, bam_bytes, json_bytes, kiem_nguon, tao_snapshot
from mau_tx3 import ts_demo


# Giá trị và câu căn cứ do tác giả tự soạn trước phép đo. Không dump kết quả.
# Câu nào có {} thì thay bằng đúng giá trị được tác giả chọn.
NOI_DUNG = [
    ("TC-01", "DEMO-XD-001", "Số: {}."),
    ("TC-02", "2026-10-30", "Ngày ký hợp đồng: {}."),
    ("TC-03", "Thi công nhà kho DEMO", "Gói thầu: {}."),
    ("TC-04", "Khu công nghiệp DEMO Sao Mai", "Dự án: {}."),
    ("TC-05", "Lô DEMO A khu DEMO Bình Minh", "Địa điểm: {}."),
    ("TC-06", "Công ty DEMO Ánh Dương", "Bên A là {} (bên giao thầu)."),
    ("TC-07", "Công ty DEMO Mây Trắng", "Bên B là {} (bên nhận thầu)."),
    ("TC-08", "2026-11-01", "Hiệu lực hợp đồng bắt đầu từ {}."),
    ("TC-09", "Thi công xây dựng", "Phạm vi công việc thuộc loại Thi công xây dựng: xây nhà kho DEMO."),
    ("TT-01", "trọn gói", "Loại hợp đồng là {}."),
    ("TT-02", "1.100.000 VND", "Giá trị hợp đồng là {}, đã gồm thuế GTGT."),
    ("TT-03", "Có", "Giá trị hợp đồng đã gồm VAT hay chưa: Có, đã gồm thuế GTGT."),
    ("TT-04", "10%", "Thuế suất GTGT là {}."),
    ("TT-05", "KL nghiệm thu thực tế", "Cơ sở thanh toán khối lượng: {}."),
    ("TT-10", "20% giá trị sau VAT", "Tỷ lệ tạm ứng là {}."),
    ("TT-11", "Thu hồi từ đợt đầu, mỗi đợt 25% số tạm ứng, hết sau 4 đợt", "Cách thu hồi tạm ứng: {}."),
    ("TT-12", "220.000 VND, hiệu lực đến khi thu hồi hết tạm ứng", "Bảo lãnh tạm ứng: {}."),
    ("TT-20", "90% giá trị nghiệm thu mỗi đợt", "Tỷ lệ thanh toán mỗi đợt là {}."),
    ("TT-21", "10%", "Tỷ lệ giữ lại mỗi đợt được ghi trực tiếp là 10%, không tính theo công thức."),
    ("TT-22", "15 ngày làm việc kể từ khi nhận đủ hồ sơ hợp lệ", "Thời hạn thanh toán: {}."),
    ("TT-30", "95% giá trị quyết toán", "Tỷ lệ thanh toán khi quyết toán là {}."),
    ("TT-31", "5% giá trị quyết toán", "Tỷ lệ bảo lãnh bảo hành là {}."),
    ("TT-32", "12 tháng kể từ ngày nghiệm thu hoàn thành", "Thời hạn bảo hành: {}."),
    ("TT-33", "110.000 VND, hiệu lực đến nghiệm thu hoàn thành", "Bảo lãnh thực hiện hợp đồng: {}."),
    ("TT-40", "Chỉ điều chỉnh khi hai bên ký phụ lục bằng văn bản", "Điều kiện điều chỉnh giá: {}."),
    ("TT-41", "Biến động vượt 5% so với giá gốc DEMO ngày 2026-10-01", "Ngưỡng biến động để điều chỉnh giá: {}."),
    ("TT-42", "Khối lượng phát sinh chỉ thi công sau phụ lục được hai bên ký", "Cách xử lý khối lượng phát sinh: {}."),
    ("TT-50", "120 ngày kể từ ngày khởi công 2026-11-02", "Tiến độ thực hiện hợp đồng: {}."),
    ("TT-51", "8% giá trị phần công việc vi phạm chất lượng", "Mức phạt vi phạm chất lượng tối đa là {}."),
    ("TT-52", "0,02% giá trị giai đoạn mỗi ngày trong 7 ngày chậm đầu tiên", "Phạt chậm tiến độ giai đoạn mức 1: {}."),
    ("TT-53", "0,04% giá trị giai đoạn mỗi ngày từ ngày chậm thứ 8", "Phạt chậm tiến độ giai đoạn mức 2: {}."),
    ("TT-54", "0,05% giá trị phần công việc chậm hoàn thành mỗi ngày", "Phạt Bên B chậm hoàn thành tổng tiến độ: {}."),
    ("TT-55", "8% giá trị phần nghĩa vụ vi phạm", "Trần tổng mức phạt không quá {}."),
    ("TT-56", "Khấu trừ tiền phạt vào đợt thanh toán kế tiếp sau biên bản xác nhận", "Cách khấu trừ tiền phạt: {}."),
    ("TT-60", "Biên bản nghiệm thu; Bảng xác nhận khối lượng; Hóa đơn DEMO", "Hồ sơ thanh toán mỗi đợt: {}."),
    ("TT-61", "Biên bản hoàn thành; Bảng quyết toán; Hóa đơn DEMO", "Hồ sơ quyết toán: {}."),
    ("TT-62", "3 bộ", "Số lượng hồ sơ thanh toán phải nộp là {}."),
]


def soan_ca(track=False):
    vals, quotes = {}, {}
    for ma, v, khuon in NOI_DUNG:
        if track and ma == "TC-01":
            v = "DEMO-XD-002"
        if track and ma == "TT-02":
            v = "2.200.000 VND"
        if track and ma == "TT-12":
            v = "440.000 VND, hiệu lực đến khi thu hồi hết tạm ứng"
        if track and ma == "TT-33":
            v = "220.000 VND, hiệu lực đến nghiệm thu hoàn thành"
        vals[ma], quotes[ma] = v, khuon.format(v)
    return vals, quotes


def tao_docx(vals, quotes, track):
    parts = [p("Hợp đồng thi công nhà kho DEMO", '<w:pPr><w:pStyle w:val="Title"/></w:pPr>'),
             p("DEMO - Dữ liệu hư cấu hoàn toàn để kiểm thử E6, không có giá trị giao dịch.")]
    for ma, _, _ in NOI_DUNG[:7]:
        parts.append(p(quotes[ma]))
    # Một Điều đủ ngắn, giúp nguồn cũ gửi cùng toàn văn theo nhóm.
    parts.append(p("Điều 1. Nội dung và điều kiện hợp đồng DEMO"))
    for ma, _, _ in NOI_DUNG[7:]:
        if track and ma == "TT-02":
            cu = soan_ca(False)[1][ma]
            parts.append('<w:p><w:del w:id="1" w:author="DEMO" w:date="2026-10-30T00:00:00Z">'
                         '<w:r><w:delText>' + escape(cu) + '</w:delText></w:r></w:del>'
                         '<w:ins w:id="2" w:author="DEMO" w:date="2026-10-30T00:00:00Z">'
                         '<w:r><w:t>' + escape(quotes[ma]) + '</w:t></w:r></w:ins></w:p>')
        else:
            parts.append(p(quotes[ma]))
    parts.append('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
                 '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>')
    styles = f'''<w:styles xmlns:w="{W_NS}"><w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="100"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="30"/><w:color w:val="000000"/></w:rPr></w:style></w:styles>'''
    rel = '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    ct = CT.replace("</Types>", '<Override PartName="/word/styles.xml" '
                    'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>')
    return goi_docx("".join(parts), styles=styles,
                    them={"word/_rels/document.xml.rels": rel, "[Content_Types].xml": ct})


def main():
    dm, _ = kiem_nguon()
    assert [r["ma"] for r in dm.cac_dong] == [r[0] for r in NOI_DUNG]
    goc = ENGINE / "tham-chieu/e6"
    goc.mkdir(parents=True, exist_ok=True)
    manifest = {"phien_ban": 2, "nhan": "DEMO", "chap_nhan_lead": "chờ lead", "cac_ca": []}
    for track in (False, True):
        ten = "DEMO-track-changes" if track else "DEMO-thuong"
        vals, quotes = soan_ca(track)
        # Bản vàng được viết TRƯỚC khi gọi bất cứ pipeline nào.
        vang = {"nhan": "DEMO", "nguon": "Tác giả soạn từ chính câu hợp đồng DEMO, không từ đầu ra engine.",
                "gia_tri": vals, "can_cu": quotes}
        docx = tao_docx(vals, quotes, track)
        # Nền text do tác giả biết trước: không lấy kết quả doc_docx để soạn vàng.
        text = "\n".join(["Hợp đồng thi công nhà kho DEMO",
            "DEMO - Dữ liệu hư cấu hoàn toàn để kiểm thử E6, không có giá trị giao dịch.",
            *list(quotes.values())[:7], "Điều 1. Nội dung và điều kiện hợp đồng DEMO",
            *list(quotes.values())[7:]])
        moi = {ma: {"gia_tri": v, "don_vi": None, "ghi_chu": None,
                    "trich_dan": [{"cau": quotes[ma], "bat_dau": text.index(quotes[ma]),
                                   "ket_thuc": text.index(quotes[ma]) + len(quotes[ma])}]}
               for ma, v in vals.items()}
        # Chín lượt nhóm cố định theo danh mục; giữ cùng câu trả lời nghiệp vụ.
        groups = []
        for r in dm.tham_so:
            if not groups or groups[-1][0] != r["nhom"] or len(groups[-1][1]) == 8:
                groups.append((r["nhom"], []))
            groups[-1][1].append(r["ma"])
        cu = {"tim_vi_tri": [], "hoi_trich": [
            [{"ma": ma, "gia_tri": vals[ma], "don_vi": "", "ghi_chu": "",
              "trich_dan": quotes[ma], "dieu_khoan": "Điều 1"} for ma in mas]
            for _, mas in groups]}
        ts = ts_demo(tao_snapshot(dm, "DEMO-m3" if track else "DEMO-crm"),
                     prompt="Chỉ trích từ hợp đồng DEMO, giữ nguyên giá trị và dẫn chứng.",
                     ngan_sach_token_vao=100000)
        case = {"ma": ten, "loai": "track_changes" if track else "thuong"}
        for k, suffix, raw in (("vang", "vang.json", json_de_doc(vang)),
                               ("docx", "docx", docx),
                               ("ai", "ai.json", json_de_doc({"cu": cu, "moi": moi})),
                               ("tham_so", "tham-so.json", json_de_doc(ts))):
            name = ten + "." + suffix
            ghi_nguon(goc / name, raw)
            case[k] = {"tep": name, "bam": bam_bytes(raw)}
        manifest["cac_ca"].append(case)
    ghi_nguon(goc / "chap-nhan.json", json_de_doc(manifest))
    print("Đã soạn hai hợp đồng DEMO và bản vàng trước phép đo; chờ lead duyệt.")


def json_de_doc(v):
    return (json.dumps(v, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def ghi_nguon(path, raw):
    """Không ghi đè nguồn/bản vàng đã đóng băng, kể cả manifest đã duyệt."""
    if path.exists():
        if path.read_bytes() != raw:
            raise ValueError("Nguồn DEMO đã tồn tại và khác nội dung soạn; phải review riêng, không ghi đè.")
    else:
        path.write_bytes(raw)


if __name__ == "__main__":
    main()
