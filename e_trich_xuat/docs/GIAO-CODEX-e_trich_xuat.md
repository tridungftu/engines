# Giao Codex — `e_trich_xuat` (Trích thông tin hợp đồng) theo SDK 2.0

*Lập 14/11/2026 (Claude, lead). Ưu tiên 2: giao **sau** Hỏi AI và OCR. Căn cứ: `QUYET-DINH-CUOI-e_trich_xuat.md` (07/11), `PHIEU-ENGINE-e_trich_xuat.md` (CD-111), `YEU-CAU-VA-HIEN-TRANG.md`, chỉ đạo 30/10 câu 1C (độ chính xác trên bộ 37 tham số không thấp hơn bản gốc), `API-ENGINE-v1.md`, `_chung/docs/LOAI-DU-LIEU-RIENG.md`.*

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

Lead nghiêng về **T1(a), T2(b) cho đợt 1 + đề nghị Core làm T2(c), T3(a) có đo, dự phòng (b)**. TX-0 phải đo bằng số, không chọn cảm tính.

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

### TX-1 … TX-6
Lead viết lệnh giao chi tiết **sau khi Anh duyệt `TX-0-THIET-KE.md`**, theo cùng mẫu của `GIAO-CODEX-e_hoi_ai.md`.

## 5. Chờ Anh (giữ từ YEU-CAU-VA-HIEN-TRANG §5, cộng thêm)
- Duyệt TX-0 (T1–T3).
- Tệp ghim `DANH_MUC_THAM_SO.xlsx` cho E6 (đang thiếu).
- Các câu cũ: số mẫu chạy thử KCN (đề xuất 3), giới hạn câu hỏi thêm (đề xuất 5), hỏi lại nhiều vòng (CD-111), nhánh trích bảng.
