# Giao Codex — thứ tự engine, quyết định tạm và phần còn thiếu phía Core

*Lập 14/11/2026 (Claude, lead). Căn cứ: chỉ đạo của Anh 14/11 ("giao Codex code từng engine, ưu tiên Hỏi AI và OCR, sau đó Trích xuất"); `docs/goi-gui-engine/API-ENGINE-v1.md`; SDK 2.0.0 (đã cài thử, 3 engine mẫu chạy `[ĐẠT]` trên Core giả ngày 14/11).*
*Mọi số giờ trong các phiếu giao Codex là **ước tính của lead, chưa đo**.*

## 1. Kết luận

- **Thứ tự:** `e_hoi_ai` → `e_ocr` → `e_trich_xuat`. Sau đó (chưa giao): `e_mask` → `e_doi_chieu` → `e_tra_cuu` → `e_hoa_don` (chờ quyết định cuối).
- Hỏi AI và OCR **độc lập với nhau**, có thể giao Codex song song. Trích xuất cần loại dữ liệu chung của hai engine trên, nên giao sau, bắt đầu bằng lát thiết kế.
- Mỗi engine được **viết lại lớp vỏ theo SDK 2.0** (HTTP, `@app.nang_luc`), **giữ và chuyển lõi nghiệp vụ** từ `ma-nguon/`. Mã cũ dùng kênh socket + `kho_tri_thuc.sdk_core` không chạy được với Core 2.0.
- Tổng giờ ước tính: Hỏi AI ~24 giờ, OCR ~27 giờ, Trích xuất lát thiết kế 3 giờ (phần còn lại ước sau khi Anh duyệt thiết kế).

## 2. SDK 2.0 đợt 1 chưa có gì — và cách Codex làm tạm

SDK 2.0 đợt 1 **chưa có**: kênh cấu hình tới engine (`san-sang` trả `cau_hinh: {}`, `Engine` không đưa ra), bí mật, ngăn dữ liệu engine, lượt bền giữ/chốt/đọc (đợt 2, migration 135), nhật ký kỹ thuật, màn trạng thái engine.

| Thiếu | Quyết định tạm cho Codex (Anh đổi được) | Khi Core có thì |
|---|---|---|
| Cấu hình máy (địa chỉ Local AI, quy tắc chọn model, thư mục Hot Folder ABBYY…) | Lớp `cau_hinh_may.py` trong mỗi gói: đọc tệp JSON **ngoài gói**, đường dẫn từ biến `KTT_ENGINE_CAU_HINH`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\<ma>\cau_hinh.json`. Có JSON Schema trong gói; thiếu tệp → engine vẫn khởi động, việc cần cấu hình trả `LoiNghiepVu` "chưa cấu hình". **Không chứa bí mật.** | Đổi nguồn sang `cau_hinh` Core cấp, giữ nguyên schema |
| Bí mật (khóa Cloud AI, khóa cầu nối ABBYY) | Không đọc bí mật ở đợt 1. Cloud AI: khung có, **tắt**. ABBYY: chỉ dùng Hot Folder trên **cùng máy** (Core đợt 1 chạy loopback), chưa dùng cầu nối có khóa | Đọc theo tên ở `bi_mat[]` |
| Dữ liệu engine cần giữ (sổ hạn mức ABBYY, dấu chống trùng, nhật ký lượt "chưa rõ") | Lớp `kho_tam.py`: tệp JSON trong **thư mục dữ liệu engine** (`KTT_ENGINE_DU_LIEU`, mặc định `%PROGRAMDATA%\KhoTriThuc\engines\<ma>\du-lieu\`), ghi nguyên tử (ghi tệp tạm rồi đổi tên) + khóa tệp. **Chỉ lưu băm, mã, số đếm — không lưu nội dung tài liệu.** | Chuyển sang ngăn engine (thao tác ngăn có CAS) |
| Lượt bền "chưa rõ" | `raise ChuaRo(ma_tuong_quan)`; engine tự ghi `ma_tuong_quan` vào `kho_tam` để lần giao lại hỏi lại nguồn ngoài trước khi gửi lại | Thao tác #10 `luot-ben` giu/chot/doc |
| Nhật ký | In nhật ký kỹ thuật ra **stderr** (không nội dung tài liệu, không khóa). Nguồn gốc (model, nguồn đọc, phiên bản engine, băm đầu vào) đưa **vào kết quả** | Thao tác nhật ký của Core |
| Màn Cổng Local AI / hạn mức ABBYY | Không làm giao diện. Chỉ làm năng lực + Chạy thử DEMO (Core dựng màn chung) | Thẻ "Trạng thái" dựng từ khai báo |

**Không làm tạm:** không tự dựng màn hình, không mở cổng HTTP riêng trong engine, không lưu nội dung tài liệu trên đĩa ngoài thư mục tạm của việc (xóa sau việc).

## 3. Cần Core (gửi lead Core qua Anh)

1. `Engine` đưa `cau_hinh` từ `san-sang` cho hàm năng lực (ví dụ `viec.cau_hinh` / `app.cau_hinh`), kèm `cau_hinh_schema` trong phiếu để Core dựng form.
2. Bí mật theo tên (`bi_mat[]`) đọc được từ engine.
3. Ngăn dữ liệu engine có: ghi theo lô nguyên tử, ghi có điều kiện (`row_version`), ràng buộc duy nhất / "lấy hoặc tạo".
4. Lượt bền #10 (giu/chot/doc) — đã hẹn đợt 2.
5. **`truong_ra` động:** bộ tham số trích xuất thuộc module, số trường thay đổi theo loại hợp đồng; phiếu 2.0 bắt `truong_ra` tĩnh. Cần cách khai "trường do tham số bước quyết định" hoặc chấp nhận kết quả dạng loại riêng + tệp Excel.
6. Trần độ dài giá trị `tham_so` kiểu `van_ban` (prompt dài, bộ tham số JSON).
7. Thẻ "Trạng thái" engine (`trang_thai_schema`) để thay màn Cổng Local AI, hạn mức ABBYY.

## 4. Chờ Anh (không chặn Codex — Codex làm theo quyết định tạm ở mục 2)

| # | Câu | Lead đề xuất |
|---|---|---|
| Q1 | Cho phép cấu hình máy tạm bằng tệp JSON ngoài gói (mục 2) tới khi Core cấp cấu hình? | Đồng ý |
| Q2 | Cho phép OCR giữ tạm sổ hạn mức, dấu chống trùng, nhật ký lượt "chưa rõ" trong thư mục dữ liệu engine (chỉ băm/mã/số đếm)? Đây là lệch tạm khỏi nguyên tắc "dữ liệu lâu dài nằm trong ngăn" | Đồng ý, có hạn: tới khi Core có ngăn |
| Q3 | Duyệt tên 4 loại dữ liệu riêng dùng chung: `van_ban_tai_lieu`, `yeu_cau_ai`, `tra_loi_ai`, `van_ban_da_che` | Đồng ý (TL 55 §11.4: contract mới cần Anh duyệt) |
| Q4 | Cloud AI chỉ nhận loại `van_ban_da_che` (chỉ Mask tạo ra) → Core tự chặn quy trình đặt Cloud mà không có Mask đứng trước | Đồng ý |

## 5. Lead làm gì trong lúc Codex code

- Review từng PR theo `AGENTS.md` mục 5 (chạy lại `kho_tri_thuc_sdk.thu` + pytest), đối chiếu quyết định cuối của engine.
- Gom "Cần Core" mới phát sinh, trình Anh mỗi buổi 17:00.
- Lát cần máy thật (Local AI qua Tailscale, ABBYY trên máy hiện tại): Codex chỉ soạn công cụ chạy khô + tệp `.cmd` ASCII; **Anh tự chạy**, lead đọc kết quả.
