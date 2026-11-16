# Giao Codex — `e_kiem_excel` (Kiểm và đọc file Excel) theo SDK 2.2.0

*Lập 16/11/2026 (Claude, lead). Anh đồng ý tiến hành 16/11; Q1–Q3 áp đề xuất. Căn cứ: `PHIEU-ENGINE-e_kiem_excel.md` (bản đã chỉnh, Phụ lục C), `AGENTS.md`, SDK 2.2.0.*

## 1. Kết luận
- **7 lát, 29 giờ công (ước tính, chưa đo).** EX-0 → EX-1 → EX-2 → EX-3 là đường chính; EX-4 làm song song sau EX-0; EX-5 sau EX-4; EX-6 cuối.
- **Không viết lại thuật toán.** Chép từ `e_kiem_excel/ma-nguon/` theo bảng phiếu §3.1–3.2, chỉ sửa ở các điểm phiếu ghi.
- **Thước đo đúng:** kết quả `excel.toan_ven@1` khớp `python e_kiem_excel/ma-nguon/toan_ven.py <DEMO>` (mức, mã kiểm, ô) và cây K7. Mọi chỗ lệch phải liệt kê trong PR để lead duyệt.

| Lát | Nội dung | Phụ thuộc | Giờ (ước tính) |
|---|---|---|---:|
| EX-0 | Khung gói, ghim, DEMO có `<v>`, nhận diện tệp, trần, đo bộ nhớ | — | 4 |
| EX-1 | `SoDo`, tham chiếu, K1–K6, schema `tep_json` | EX-0 | 6 |
| EX-2 | K7 + bộ nhóm | EX-1 | 4 |
| EX-3 | Báo cáo Excel + K8 | EX-2 | 4 |
| EX-4 | `doc_bang` khuôn `xay_dung_klgt` | EX-0 | 4 |
| EX-5 | Khuôn `tong_quat` | EX-4 | 4 |
| EX-6 | Ghim nguồn, máy sạch, số đo, `thoi_han_giay` | tất cả | 3 |
| | **Tổng** | | **29** |

## 2. Lệnh giao Codex từng lát (dán nguyên khối)

### EX-0 — Khung gói, DEMO và trần an toàn
```
Đọc AGENTS.md, e_kiem_excel/CLAUDE.md, e_kiem_excel/docs/PHIEU-ENGINE-e_kiem_excel.md (đủ, cả Phụ lục C), e_kiem_excel/ma-nguon/NGUON.md.
Làm lát EX-0 cho e_kiem_excel:
1. Tạo e_kiem_excel/goi/e_kiem_excel/ theo AGENTS.md §3, khung từ docs/goi-gui-engine/sdk-2.2.0/engine-demo/e_demo_doc_tep và mẫu bọc nhật ký/lỗi của e_hoa_don/goi/e_hoa_don/e_hoa_don/chay.py.
2. engine.json 2.0 đủ 2 năng lực theo phiếu §4.1, §4.2, §4.3, Phụ lục B: đủ truong_ra, tham_so (khuon có lua_chon; tham số chữ có toi_da), gioi_han (tep_toi_da_mib tạm 20, thoi_han_giay tạm 120), huy_duoc true. Hàm năng lực tạm raise LoiNghiepVu("CHUA_LAM", ...).
3. requirements.lock ghim openpyxl, et_xmlfile, defusedxml có hash (mẫu e_ocr/goi/e_ocr/requirements.lock); NGUON.md ghi nguồn, giấy phép, SHA-256.
4. nhan_dien.py: kiểm đuôi .xlsx/.xlsm + chữ ký ZIP; .xls (OLE) → TEP_KHONG_HO_TRO; kiểm tổng dung lượng giải nén, số entry, số ô (đếm thẻ <c theo luồng) → VUOT_GIOI_HAN; chạy TRƯỚC khi gọi openpyxl.
5. tests/demo/sinh_demo.py: tự ghi XML .xlsx bằng zipfile, ô công thức có cả <f> và <v> (giá trị tự tính); nhãn "Công ty DEMO Ánh Dương", số tiền giả. Bộ tệp: mỗi K1–K8 ít nhất một dấu hiệu cài sẵn + 1 tệp sạch + 1 tệp cố ý thiếu <v> + 1 tệp có thực thể XML lồng nhau + 1 tệp .xls giả (chữ ký OLE) + 1 bảng KL xây dựng cho doc_bang. tests/demo/dap-an.json (phát hiện kỳ vọng), tests/demo/bam-fixture.json (SHA). Không cần LibreOffice.
6. tests/do_bo_nho.py: đo đỉnh bộ nhớ (tracemalloc + RSS) khi openpyxl nạp 2 lần (data_only False/True) tệp DEMO 5, 10, 20 MiB; ghi bảng vào VIEC.md và đề xuất tep_toi_da_mib, trần ô, trần giải nén.
7. tests/kiem_doc_lap.py, conftest.py, kiem_may_sach.sh, KIEM-MAY-SACH.cmd theo mẫu e_hoa_don/tests/.
8. Ghi vào VIEC.md: Core gán mime gì khi tải .xlsx (đọc API-ENGINE-v1/SDK; chưa rõ thì ghi "Cần Core xác nhận").
Đạt: 3 lệnh AGENTS.md §5; test tệp .xls, bom nén, thực thể XML bị từ chối đúng mã lỗi. Không sửa ma-nguon/.
```

### EX-1 — `SoDo`, hàm tham chiếu, K1–K6
```
Làm lát EX-1 cho e_kiem_excel (đọc phiếu §3.1, §4.1, §4.3, §5.1).
1. Chép toan_ven.py dòng 42–50, 144–229 → tham_chieu.py; 54–142 (SoDo) → so_do.py, nạp từ bytes (BytesIO), self.ngoai chỉ giữ tên tệp, bỏ thư mục; nfc/bo_dau/so/num (master_hd 43–72) → chuan_hoa.py, num trả Decimal.
2. Chép KiemTra.__init__, them, k1…k6 (toan_ven 262–515) → kiem_tra.py; __init__ nhận SoDo + tham số bước; k6 bỏ chữ "HĐ" viết cứng; viec.kiem_huy() giữa các kiểm.
3. Nối excel.toan_ven@1 tạm chạy K1–K6, trả truong_ra (K7/K8 để trống/null), tep_json theo §5.1 qua viec.tai_tep_ra. Số trong JSON là chuỗi thập phân; số tiền theo §4.3.
4. Chốt schema tep_json (JSON Schema trong tests/schema/) — lead duyệt trong PR.
5. tests/test_tuong_duong.py: kiểm SHA ma-nguon/*.py, chạy toan_ven.py gốc (import từ ma-nguon trong test) và engine trên cùng DEMO; so phát hiện K1–K6 (mức, mã, ô). Lệch → liệt kê trong PR, không tự "sửa cho khớp".
Test thêm: Decimal ≥ 10^9, số âm, số lẻ → so_tien.so đúng dạng SDK nhận; tệp lỗi → TEP_HONG không lộ traceback.
```

### EX-2 — K7 cây truy vết và bộ nhóm
```
Làm lát EX-2 cho e_kiem_excel (phiếu §4.1, §4.1.1, Phụ lục A).
1. Chép k7_cay_truy_vet (toan_ven 516–604) + LABELS/tim_so_tong_hop (master_hd 730–765, số dạng Decimal) → kiem_tra.py, doc_bang.py.
2. Ô đích: o_dich (kiểm dạng Sheet!A1, sai → THAM_SO_KHONG_HOP_LE) → không có thì tìm theo nhan_o_dich_json → không có cả hai thì một mục "Kiểm soát".
3. bo_nhom.py: đọc và kiểm bo_nhom_json theo §4.1.1 (từ khóa chứa chuỗi, "=tu" khớp nguyên từ, "#" = một hoặc nhiều chữ số; không nhận regex; trần 30 nhóm/200 từ khóa/32 KiB). Không có bộ → lá "Chưa phân nhóm", so_ngoai_nhom = null.
4. Fixture: Phụ lục A đặt ở tests/demo/bo_nhom_review_ttkl.json (thuộc module, không vào goi/).
5. Test tương đương: với Phụ lục A, cây K7 và nhóm từng lá khớp toan_ven.py gốc trên DEMO. Đo và báo riêng hai chỗ lệch Phụ lục A ghi (nhóm 6 xét nhãn dòng; dai|rong|cao).
```

### EX-3 — Báo cáo Excel và K8
```
Làm lát EX-3 cho e_kiem_excel (phiếu §3.1, §4.1).
1. Chép k8_nguon_kl, _lech, _nguon (toan_ven 605–736) — chỉ chạy khi kiem_nguon_kl = true; dùng doc_bang.tim_bang_chi_tiet của gói (lát EX-4 chưa xong thì chép trước hàm này từ master_hd 629–728, RuntimeError → LoiNghiepVu("KHONG_TIM_THAY_BANG", ...)).
2. Chép chay/_xep_lai (737–762) và kiểu ô + _sheet + ghi (764–866) → bao_cao.py, ghi bằng openpyxl vào BytesIO, đủ các sheet như toan_ven.py; ô tiền kèm đơn vị hoặc để trống khi chưa rõ. Tải bằng viec.tai_tep_ra.
3. Đủ truong_ra §4.1. chay_thu_demo: (1) kiểm có bộ nhóm, (2) kiểm không bộ nhóm.
Test: báo cáo mở lại được bằng openpyxl, đủ tên sheet; K8 khớp đáp án và toan_ven.py gốc; tắt công tắc thì không có sheet K8.
```

### EX-4 — `excel.doc_bang@1` khuôn `xay_dung_klgt`
```
Làm lát EX-4 cho e_kiem_excel (phiếu §3.2, §4.2, §4.3, §5.2).
1. doc_bang.py: _hdr_text, tim_bang_chi_tiet, khoa (master_hd 629–728) giữ nguyên công thức khoa; tim_so_tong_hop (741–765) bằng Decimal, bỏ lọc abs(v) > 1 bằng float.
2. excel.doc_bang@1 với khuon = xay_dung_klgt: trả truong_ra §4.2 + tep_json §5.2. tien_te (ISO 3 chữ hoa) có thì gắn; không có và file không ghi đơn vị → gia_tri_* = null, tien_te_chua_ro = true; tuyệt đối không tự gán VND.
3. Cảnh báo: thành tiền ≠ KL × đơn giá, ô số dạng chữ, dòng trùng khóa. Dừng ở dòng "Cộng".
4. chay_thu_demo ví dụ thứ 3: đọc bảng KL DEMO.
Test: khớp đáp án DEMO và khớp kết quả tim_bang_chi_tiet/tim_so_tong_hop gốc (sau khi đổi float→Decimal, liệt kê lệch làm tròn); không thấy bảng → KHONG_TIM_THAY_BANG.
```

### EX-5 — Khuôn `tong_quat`
```
Làm lát EX-5 cho e_kiem_excel (phiếu §4.2).
khuon = tong_quat đọc theo khuon_cot_json {phien_ban, cot[{ma, tu_khoa, bat_buoc, kieu}], dong_dung}; cùng quy tắc từ khóa với bo_nhom.py (dùng chung mã, không chép lại); sai cấu trúc/vượt trần → THAM_SO_KHONG_HOP_LE. Sinh thêm 2 mẫu bảng DEMO khác nhau (bảng giá thành, bảng báo giá) và đáp án.
```

### EX-6 — Ghim nguồn, cài sạch, số đo
```
Làm lát EX-6 cho e_kiem_excel.
1. Rà requirements.lock chỉ còn thư viện thật dùng; NGUON.md đủ đường cũ → mới (toan_ven/master_hd dòng nào → tệp nào trong gói) + SHA-256 mọi tệp gói; đóng gói bằng _chung/cong-cu/dong_goi.py.
2. kiem_may_sach.sh chạy trong CI Linux Python 3.11; KIEM-MAY-SACH.cmd cho Windows (Anh chạy, Codex không chạy).
3. Đo thời gian + đỉnh bộ nhớ của 2 năng lực trên DEMO 1/5/10/20 MiB; đề xuất thoi_han_giay và tep_toi_da_mib cuối; ghi VIEC.md.
4. Cập nhật VIEC.md, phiếu §6 bằng số đo thật; ghi "đã kiểm bằng Core giả (CoreGia)".
```
