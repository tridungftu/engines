# Giao Codex — `e_trich_xuat` (Trích thông tin hợp đồng) theo SDK 2.0

*Lập 14/11/2026 (Claude, lead). Ưu tiên 2: giao **sau** Hỏi AI và OCR. Căn cứ: `QUYET-DINH-CUOI-e_trich_xuat.md` (07/11), `PHIEU-ENGINE-e_trich_xuat.md` (CD-111), `YEU-CAU-VA-HIEN-TRANG.md`, chỉ đạo 30/10 câu 1C (độ chính xác trên bộ 37 tham số không thấp hơn bản gốc), `API-ENGINE-v1.md`, `_chung/docs/LOAI-DU-LIEU-RIENG.md`.*

**Cập nhật 15/11/2026:** `QUYET-DINH-ANH-20261115.md` câu 5 giao TX-0 ngay, chốt T1(a), hướng T2(b) + đề nghị T2(c), T3 đo thật bằng số; câu 7 chốt nguồn XLSX cho E6. Bản nháp TX-0 (PR #4) được sửa trong `TX-0-THIET-KE.md`, PR cập nhật: **chờ lead mở**. Chỉ tài liệu/phép đo, chưa giao code TX-1. Quy tắc engine không lưu gì trên máy, ngăn RAM tạm và màn cấu hình của engine theo đợt 2 thắng các chỉ dẫn tạm cũ.

## 1. Kết luận

- **Bắt đầu bằng lát thiết kế TX-0 (3 giờ, ước tính), trình Anh duyệt rồi mới code.** Lý do: phiếu 2.0 có 3 chỗ chưa khớp với mô hình "bộ tham số thuộc module" (mục 2). Code ngay thì có thể phải làm lại.
- Sau TX-0: **6 lát code, khoảng 26 giờ công (ước tính sơ bộ, chưa đo)**. Phiếu cũ 53 giờ gồm cả việc của module (C1, C2, C4) và Core (C3), các việc đó không thuộc Codex ở đây.
- Chuỗi đích (Core điều phối, engine không gọi AI):
  ```
  tệp ──► [ocr.doc_tai_lieu@1 | trich.doc_docx@1] ─van_ban_tai_lieu─► [trich.chuan_bi@1] ─yeu_cau_ai─►
          [ai.hoi_theo_yeu_cau@1] ─tra_loi_ai─► [trich.hau_kiem@1] ─► bảng kết quả về module
  ```
- **Điều kiện mở TX-1:** Hỏi AI xong AI-2 (`ai.hoi_theo_yeu_cau@1`, khuôn trả lời) và OCR xong OCR-1 (`van_ban_tai_lieu`).

## 2. Ba câu TX-0 phải trả lời

| # | Chỗ chưa khớp | Phương án để TX-0 so sánh |
|---|---|---|
| T1 | **Bộ tham số đi vào việc bằng đường nào?** Phiếu 2.0 chỉ có `tham_so` của bước (kiểu `van_ban`, `so`, `co_khong`, `chon`) | (a) `tham_so` `bo_tham_so_json` (van_ban) + `bam_bo_tham_so`, module ghi khi Admin kích hoạt bộ; (b) bộ là một tệp, cần Core cho bước nhận 2 đầu vào (chưa có) |
| T2 | **`truong_ra` phải tĩnh**, nhưng mỗi loại hợp đồng (xây dựng 37 trường, KCN…) có trường khác nhau | (a) một năng lực hậu kiểm cho mỗi loại (`trich.hau_kiem_xay_dung@1`…); (b) trả loại riêng `bang_trich_xuat` + tệp Excel, module tự ghép cột; (c) Core bổ sung "trường do tham số quyết định" (Cần Core điểm 5) |
| T3 | **Một bước chỉ gọi AI một lần**, bộ 37 tham số có thể vượt ngữ cảnh model | (a) một lượt với khuôn gồm mọi trường (đo trên Qwen3 8B / gpt-oss 20B); (b) mở rộng `yeu_cau_ai` cho nhiều câu hỏi trong một việc (đổi loại dùng chung, Anh duyệt); (c) module khai nhiều bước hỏi theo nhóm trường |

**Anh đã chốt 15/11:** T1(a), hướng T2(b) cho đợt 1 + ghi đề nghị Core **“trường do tham số quyết định”** T2(c), T3 phải đo thật bằng số. T3(a) là phương án thử, chưa có số đo model thật thì không kết luận sức chứa đạt; dự phòng (b)/(c) phải trình riêng. Payload `bang_trich_xuat` và bước xuất tĩnh vẫn cần review chi tiết, không coi toàn bộ nháp là đã duyệt.

## 3. Các lát

| Lát | Nội dung | Yêu cầu | Phụ thuộc | Giờ (ước tính) |
|---|---|---|---|---:|
| TX-0 | Thiết kế: trả lời T1–T3, phiếu `engine.json` nháp, đo ngữ cảnh | TX-2, 3, 5 | AI-2, OCR-1 (chỉ cần tài liệu) | 3 |
| TX-1 | Khung gói + `trich.doc_docx@1` (Word không qua OCR, xử lý Track Changes không dùng Word COM) | TX-15, TX-12 | TX-0 duyệt | 4 |
| TX-2 | `trich.chuan_bi@1`: kiểm bộ + hash, lập `yeu_cau_ai` có khuôn, đưa bộ/hash vào `chuyen_tiep` | TX-2, 3, 4, 17 | TX-1, AI-2 | 5 |
| TX-3 | `trich.hau_kiem@1`: kiểm trích dẫn, trường thiếu, quy tắc logic (`vendor/review/logic.py`), lập bảng + ô cần xem lại | TX-3, 5 | TX-2 | 5 |
| TX-4 | E6: so từng byte bộ 37 tham số xây dựng (cần tệp ghim `DANH_MUC_THAM_SO.xlsx`) | TX-7 | TX-2 | 3 |
| TX-5 | Đưa E1 (kiểm Excel bộ tham số) thành thư viện để module dùng lại; U1a/U1b chỉ bàn giao mã, không đặt trong engine | TX-8, 14 | TX-0 | 3 |
| TX-6 | DEMO + N1 đo độ chính xác một lần (không thấp hơn bản gốc) + ghim, máy sạch | TX-12, 13; câu 1C | TX-3, TX-4 | 6 |
| | **Tổng sau TX-0** | | | **26** |

Bảng trên là ước tính giao ban đầu. Thiết kế cập nhật 15/11 §8 đề xuất **37 giờ** (8/7/8/4/3/7), thêm ngăn/màn cấu hình vào TX-1; lead review/tách lát trước khi giao code.

Ngoài phạm vi Codex: C1/C2/C4 (màn quản lý bộ tham số trong module CRM, M4), C3 (Core giữ tạm kết quả), LHD-02b bộ KCN (chờ người nghiệp vụ duyệt), TX-18 hỏi lại nhiều vòng (CD-111, chưa duyệt).

## 4. Lệnh giao Codex

### TX-0 — Thiết kế (chỉ tài liệu + phép đo, không code engine)
```
Đọc AGENTS.md, _chung/docs/GIAO-CODEX-THU-TU.md, _chung/docs/LOAI-DU-LIEU-RIENG.md, e_trich_xuat/docs/GIAO-CODEX-e_trich_xuat.md, QUYET-DINH-CUOI-e_trich_xuat.md, PHIEU-ENGINE-e_trich_xuat.md, YEU-CAU-VA-HIEN-TRANG.md.
Làm lát TX-0 cho e_trich_xuat:
1. Đọc mã ma-nguon/ (tich_hop.py, quy_trinh.py, tham_so.py, docx.py, ai_chung.py, do_chinh_xac.py, vendor/review/*) và lập bảng: mô-đun → giữ / chép có sửa / bỏ, ứng với chuan_bi, hau_kiem, doc_docx.
2. Trả lời T1, T2, T3 (mục 2) bằng bảng so sánh: ưu/nhược, việc phải làm ở engine/module/Core, rủi ro. Với T3: đếm token ước lượng (ký tự/4, ghi rõ là ước lượng) của prompt + tài liệu DEMO + khuôn 37 trường; so với ngữ cảnh khai của Qwen3 8B, gpt-oss 20B, Gemma (ghi nguồn số liệu ngữ cảnh, không có nguồn thì ghi "chưa rõ").
3. Viết e_trich_xuat/docs/TX-0-THIET-KE.md: kết luận trước, phiếu engine.json 2.0 nháp (các năng lực, nhan/tra, tham_so, truong_ra hoặc loại riêng), câu trình Anh chốt, giờ ước tính từng lát TX-1…TX-6 cập nhật.
4. Nếu đề xuất loại riêng mới (bang_trich_xuat) hoặc đổi yeu_cau_ai: viết đề xuất bổ sung vào cuối _chung/docs/LOAI-DU-LIEU-RIENG.md, đánh dấu "ĐỀ XUẤT TX-0, chờ Anh".
Không tạo goi/, không sửa ma-nguon/. PR chỉ có tài liệu.
```

Bổ sung bắt buộc theo quyết định 15/11: T1 dùng `van_ban` JSON + băm trong Cài đặt bước; T2 bảng loại riêng + Excel, module tự ghép cột và Cần Core “trường do tham số quyết định”; T3 báo số đếm thực, token ước lượng ghi rõ, số model thật thiếu ghi chưa đo. Thêm bảng ngăn engine cần, phạm vi/khóa/CAS/thời hạn theo `DE-NGHI-SDK-2.1.md`, cùng màn cấu hình `goi/e_trich_xuat/ui/` dùng `KttCore.engine`; không tạo gói ở TX-0. E6 dùng `e_trich_xuat/tham-chieu/DANH_MUC_THAM_SO.xlsx` do **lead sẽ đặt** theo đợt 2 §4, có SHA-256 trong `tham-chieu/NGUON.md` và xác nhận không dữ liệu thật; chưa có thì không bịa nội dung.

### TX-1 … TX-6
Lead viết lệnh giao chi tiết **sau khi Anh duyệt `TX-0-THIET-KE.md`**, theo cùng mẫu của `GIAO-CODEX-e_hoi_ai.md`.

## 5. Phần còn mở sau quyết định 15/11
- Review chi tiết payload/schema bảng, bước xuất tĩnh và dự toán cập nhật TX-0; không hỏi lại lựa chọn T1/T2 đã chốt.
- T3: chờ số đo model thật để quyết định một lượt hay chia lượt, không lấy token ký tự/4 làm bằng chứng runtime.
- Lead sẽ đặt `e_trich_xuat/tham-chieu/DANH_MUC_THAM_SO.xlsx` + NGUON/SHA-256 cho E6 (hiện thiếu); nguồn đã được Anh chốt, không phải câu hỏi xin nguồn lại.
- Các câu cũ: số mẫu chạy thử KCN (đề xuất 3), giới hạn câu hỏi thêm (đề xuất 5), hỏi lại nhiều vòng (CD-111), nhánh trích bảng.
