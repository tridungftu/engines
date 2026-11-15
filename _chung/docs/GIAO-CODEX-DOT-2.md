# Giao Codex — đợt 2 (15/11/2026): làm lại theo quyết định của Anh và mở lát mới

*Lập 15/11/2026 (Claude, lead). Căn cứ: `QUYET-DINH-ANH-20261115.md`, `DE-NGHI-SDK-2.1.md`. Giờ là **ước tính của lead, chưa đo**.*

## 1. Kết luận

- **Phải làm lại một phần đã gộp:** Hỏi AI, OCR, Mask đang lưu cấu hình và dữ liệu tạm trên đĩa (`cau_hinh_may.py`, `kho_tam.py`). Anh đã chốt **engine không lưu gì trên máy**. Đổi sang **cổng `Ngan`** (viết như đã có ngăn Core, tạm chạy RAM) và **màn cấu hình của engine**.
- **Thứ tự:** NGAN-0 (mẫu chung) → AI-8, OCR-8, MASK-3b song song → MASK-4…6 → các lát mới. TX-0 và HD-P2 là lát tài liệu, giao **ngay, song song**.
- Tổng phần làm lại khoảng **14 giờ** (ước tính): NGAN-0 2, AI-8 4, OCR-8 5, MASK-3b 3. Lát tài liệu: TX-0 3, HD-P2 1.

| Lát | Engine | Nội dung | Phụ thuộc | Giờ (ước tính) |
|---|---|---|---|---:|
| NGAN-0 | chung | Mẫu cổng `Ngan` + `NganBoNho` + bộ test hợp đồng | — | 2 |
| AI-8 | e_hoi_ai | Cấu hình và model phát hiện vào ngăn; màn "Cổng Local AI / Cổng Cloud AI" | NGAN-0 | 4 |
| OCR-8 | e_ocr | Hạn mức, lượt ABBYY, chống trùng, cấu hình vào ngăn; màn cấu hình + hạn mức | NGAN-0 | 5 |
| MASK-3b | e_mask | Kho tạm của MASK-3 chuyển sang cổng `Ngan`; chốt tiền tố MASK… | NGAN-0 | 3 |
| MASK-4…6 | e_mask | Theo `GIAO-CODEX-e_mask.md` (Anh đã duyệt `van_ban_da_che`); MASK-6 màn duyệt danh sách chờ là màn của engine | MASK-3b | theo phiếu Mask |
| TX-0 | e_trich_xuat | Thiết kế, theo hướng Anh chốt | — | 3 |
| HD-P2 | e_hoa_don | Lập phiếu ZIP + bảng kê Excel | — | 1 |

## 2. Quy tắc mới (bổ sung AGENTS.md §4)

- **Không ghi tệp lâu dài nào trên máy engine:** không cấu hình, không sổ, không đệm bền. Tệp tạm của một việc thì xóa trong `finally`.
- Mọi dữ liệu cần giữ đi qua cổng `Ngan` với đúng API ở `DE-NGHI-SDK-2.1.md` §3: `doc`, `tim`, `lo()` gồm `them`/`sua`/`xoa`/`lay_hoac_tao`, xung đột thì `NganXungDot`.
  - `chon_ngan(app)`: nếu SDK có `app.ngan` thì dùng ngăn thật, nếu không thì dùng `NganBoNho`.
  - Khi chạy thật bằng `NganBoNho`, engine in **một lần** cảnh báo ra stderr: "Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng".
- Cấu hình = bản ghi `cau_hinh` trong ngăn, kiểm bằng `cau_hinh.schema.json` trong gói. Thiếu cấu hình thì việc cần cấu hình trả `LoiNghiepVu("CHUA_CAU_HINH", "Engine chưa được cấu hình. Admin vào Quản lý engine › <tên> › Cấu hình.")`.
- **Không khai trường mới** (`ngan_du_lieu`, `cau_hinh`, `giao_dien_quan_tri`) vào `engine.json` khi SDK 2.0.0 còn từ chối. Ghi bản khai dự kiến vào `goi/<ma>/KHAI-SDK-2.1.json` để chép vào phiếu khi có SDK 2.1.
- Màn của engine: `goi/<ma>/ui/*.js`, dùng `KttCore.engine(ma)` theo `DE-NGHI-SDK-2.1.md` §5.
  - Chưa có SDK thật thì test bằng một `KttCore` giả trong `tests/ui/` (Node, không mạng).
  - Không gọi mạng ngoài, không `eval`, không `innerHTML` chưa lọc.
  - Ngày dd/mm/yyyy; tiền có dấu chấm hàng nghìn kèm đơn vị; ẩn mã kỹ thuật.

## 3. Lệnh giao Codex (dán nguyên khối)

### NGAN-0 — Mẫu cổng ngăn dùng chung
```
Đọc AGENTS.md, _chung/docs/QUYET-DINH-ANH-20261115.md, _chung/docs/DE-NGHI-SDK-2.1.md, _chung/docs/GIAO-CODEX-DOT-2.md.
Làm lát NGAN-0:
1. Tạo _chung/mau-ma/ngan.py: lớp Ngan (giao diện), NganBoNho (RAM, khóa luồng), NganXungDot, chon_ngan(app). API đúng DE-NGHI-SDK-2.1.md §3: doc(bang, khoa), tim(bang, loc, gioi_han, tiep), lo() → them/sua/xoa/lay_hoac_tao, nguyên tử cả lô, CAS theo row_version, ràng buộc duy nhất, pham_vi "phap_nhan" (lọc theo phap_nhan_id truyền vào). Chỉ thư viện chuẩn.
2. Tạo _chung/mau-ma/cau_hinh.py: doc_cau_hinh(ngan, schema) đọc bản ghi "cau_hinh", điền mặc định, kiểm schema (bộ kiểm JSON Schema tối thiểu, không thêm thư viện), thiếu → None.
3. _chung/mau-ma/tests/: bộ test hợp đồng chạy được cho mọi bản Ngan (tham số hóa): lô thành công/thất bại toàn phần, CAS lệch, lay_hoac_tao hai luồng đồng thời chỉ tạo một bản, phạm vi pháp nhân không đọc chéo.
4. README ngắn: các engine CHÉP hai tệp này vào gói của mình, test so băm với bản _chung.
Không sửa engine nào trong lát này.
```

### AI-8 — Hỏi AI: cấu hình và model trong ngăn, màn Cổng AI
```
Làm lát AI-8 cho e_hoi_ai (đọc GIAO-CODEX-DOT-2.md §2).
1. Chép _chung/mau-ma/ngan.py, cau_hinh.py vào gói; test so băm.
2. Bỏ cau_hinh_may.py khỏi đường chạy engine (KHÔNG xóa tệp; ghi VIEC.md để chuyển LUU-TRU). Cấu hình local_ai (url, timeout_giay), quy_tac_model đọc từ ngăn qua cau_hinh.py; cau_hinh.schema.json trong gói. Thiếu → CHUA_CAU_HINH.
3. Model phát hiện (AI-3) ghi vào bảng ngăn model_phat_hien (lay_hoac_tao theo id_model); chọn model đọc từ đây + đệm RAM 5 phút.
4. goi/e_hoi_ai/ui/cau_hinh.js: một màn hai phần "Cổng Local AI" (địa chỉ máy, thời hạn, trạng thái, danh sách model phát hiện, model chọn cho từng mẫu mã prompt, nút Lưu) và "Cổng Cloud AI" (hiện trạng thái "Chưa áp dụng ở bản 1", không có nút bật). Dùng KttCore.engine("e_hoi_ai").cau_hinh/.ngan.
5. KHAI-SDK-2.1.json: ngan_du_lieu (cau_hinh, model_phat_hien), cau_hinh, giao_dien_quan_tri.
6. Công cụ AI-7 giữ tham số dòng lệnh --url, không đọc tệp cấu hình.
Test: CoreGia + NganBoNho có cấu hình DEMO; thiếu cấu hình → CHUA_CAU_HINH; tests/ui bằng KttCore giả (lưu, CAS xung đột hiện câu lỗi tiếng Việt). Cổng DEMO chay_demo_voi_local_gia.py nạp cấu hình qua ngăn thay vì KTT_ENGINE_CAU_HINH. 0 lượt Cloud.
```

### OCR-8 — OCR: hạn mức, lượt và cấu hình trong ngăn, màn cấu hình
```
Làm lát OCR-8 cho e_ocr (đọc GIAO-CODEX-DOT-2.md §2; giữ nguyên hành vi phương án B của OCR-4).
1. Chép _chung/mau-ma/ngan.py, cau_hinh.py vào gói; test so băm.
2. Thay kho_tam.py bằng cổng Ngan (KHÔNG xóa tệp cũ; ghi VIEC.md). Bảng: han_muc_ngay (pham_vi engine, khoa ngay), luot_abbyy (pham_vi phap_nhan, khoa ma_tuong_quan, duy_nhat [phap_nhan_id, bam_noi_dung]). Giữ trang + ghi lượt trong MỘT lô nguyên tử (đóng luôn nợ OCR-4 số 1: khe đua giữa đọc trạng thái và giữ lượt). Chống trùng = lay_hoac_tao theo duy_nhat.
3. Cấu hình abbyy.*, tesseract.* đọc từ ngăn; bỏ cau_hinh_may.py khỏi đường chạy.
4. goi/e_ocr/ui/cau_hinh.js: thư mục vào/ra Hot Folder, thời hạn, hạn mức 30 ngày, đường Tesseract, ngôn ngữ; phần xem: trang đã dùng/còn lại trong 30 ngày, ABBYY bật/tắt (từ bản ghi trạng thái engine ghi định kỳ vào ngăn), các lượt "chưa rõ" đang treo.
5. KHAI-SDK-2.1.json tương ứng.
Test: toàn bộ test OCR-4/OCR-5 chạy lại trên NganBoNho; hai việc cùng tệp đồng thời → chỉ một lần gửi ABBYY; CAS xung đột khi giữ trang → thử lại không trừ hai lần; tests/ui bằng KttCore giả.
```

### MASK-3b — Mask: kho tạm sang cổng ngăn
```
Làm lát MASK-3b cho e_mask (đọc GIAO-CODEX-DOT-2.md §2, QUYET-DINH-ANH-20261115.md câu 2, 8).
1. Chép _chung/mau-ma/ngan.py, cau_hinh.py vào gói; test so băm.
2. Port kho của MASK-3 nối vào cổng Ngan (không ghi tệp JSON trên đĩa). Bảng ngăn: dinh_danh, bi_danh_tam, cho_duyet, ma_yeu_cau, dau_gap (pham_vi engine); chốt alias/hàng chờ/đếm gặp trong một lô nguyên tử; CAS xung đột → MASK_XUNG_DOT thu_lai_duoc.
3. Tiền tố tự sinh chốt: MASKCT, MASKCN, MASKDC, MASKMST, MASKTK, MASKKHAC, MASKTAM; test không trùng mẫu mã Junsky DEMO.
4. KHAI-SDK-2.1.json tương ứng.
Sau MASK-3b: làm tiếp MASK-4, MASK-5, MASK-6 theo GIAO-CODEX-e_mask.md (van_ban_da_che đã duyệt; MASK-6 màn duyệt danh sách chờ đặt ở goi/e_mask/ui/, dùng KttCore.engine("e_mask").ngan). Từ điển nhận diện: chờ lead đặt bản sạch (mục 4), chưa có thì dùng fixture DEMO và ghi rõ.
```

### TX-0 — Trích xuất (giao ngay)
```
Dùng lệnh TX-0 trong e_trich_xuat/docs/GIAO-CODEX-e_trich_xuat.md §4, thêm định hướng Anh chốt 15/11:
T1 bộ tham số qua Cài đặt bước (van_ban JSON + băm); T2 kết quả trả loại riêng bảng + tệp Excel, module tự ghép cột, đồng thời ghi đề nghị Core "trường do tham số quyết định"; T3 đo thật bằng số. Thêm mục: bảng ngăn engine cần (nếu có) theo DE-NGHI-SDK-2.1.md, và E6 dùng tệp DANH_MUC_THAM_SO.xlsx lead đặt tại e_trich_xuat/tham-chieu/ (mục 4).
```

### HD-P2 — Hóa đơn: phiếu ZIP + bảng kê Excel
```
Làm lát HD-P2 cho e_hoa_don (chỉ tài liệu). Anh chốt 15/11: XML là mốc 1; mở ZIP + bảng kê Excel; PDF và tải cổng thuế để sau.
Bổ sung vào e_hoa_don/docs/GIAO-CODEX-e_hoa_don.md các lát HD-5… cho: (a) hoa_don.doc_zip@1: báo cáo từng tệp trong gói (thứ tự, tên, băm, đọc được/lỗi/không hỗ trợ/trùng), không gọi "đầy đủ" khi có tệp lỗi; (b) hoa_don.bang_ke_xlsx@1: XLSX giữ chuỗi tiền chính xác + mã tiền tệ, số hóa đơn giữ số 0 đầu; dùng nguồn Node hay Python thì so sánh và đề xuất, ghi quyền nguồn (CD-096 A1). Mỗi lát có lệnh giao, giờ ước tính, điều kiện đạt; không lưu gì trên máy (GIAO-CODEX-DOT-2.md §2). Cập nhật VIEC.md: Q1 Q2 Q3 đã chốt.
```

## 4. Việc của lead trên máy Anh (Codex không làm được vì cần ổ D:)

1. Chép `DANH_MUC_THAM_SO.xlsx` từ `D:\Claude\Ho tro review ho so xay dung\review_xaydung` (chỉ đọc) vào `e_trich_xuat/tham-chieu/`; ghi SHA-256 vào `e_trich_xuat/tham-chieu/NGUON.md`; xác nhận tệp chỉ là danh mục tham số.
2. Chép 4 từ điển nhận diện từ `D:\GPT\Phan mem Mask file\Mask file v2`, lọc bỏ mọi tên riêng đối tác, đặt vào `e_mask/tham-chieu/tu-dien/` + SHA-256; **trình Anh xem danh sách trước khi gộp**.
3. Chuyển `e_mask/docs/PHIEU-MASK-CHAY-THU-DEMO.md` sang trạng thái "Bỏ — 15/11/2026" (không xóa tệp).
