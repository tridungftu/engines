# Chuyển engine sang SDK 2.2.0 (15/11/2026)

*Lập: Claude (lead), 15/11/2026. Căn cứ: `docs/goi-gui-engine/sdk-2.2.0/THAY-DOI-2.2.0.md` (Anh duyệt phát hành 15/11/2026), mẫu `docs/goi-gui-engine/sdk-2.2.0/engine-demo/e_demo_ngan/`. Giờ là **ước tính**.*

## 1. Kết luận

- SDK 2.2.0 có **ngăn thật của Core** (`app.ngan`/`viec.ngan`) và **cấu hình thật** (`app.cau_hinh`/`viec.cau_hinh`, `@app.khi_doi_cau_hinh`). Bỏ ngăn RAM tạm `_chung/mau-ma/ngan.py` + `cau_hinh.py` khỏi đường chạy; dùng SDK trực tiếp. Test dùng `CoreGia` của SDK 2.2.0 (đã có ngăn trong bộ nhớ cùng ngữ nghĩa Core thật, `dat_cau_hinh`, `gay_xung_dot_ngan`, `xem_ngan`).
- Thứ tự: 4 engine đã xong code trước (Hỏi AI, OCR, Hóa đơn, Trích xuất) để đóng gói nghiệm thu; Mask, Đối chiếu, Tra cứu chuyển khi xong lát đang làm.

## 2. Khác biệt phải sửa so với cổng tạm

| Cổng tạm (`_chung/mau-ma`) | SDK 2.2.0 | Việc phải làm |
|---|---|---|
| Bảng phạm vi pháp nhân: `phap_nhan_id` nằm trong `khoa`/`loc` | Core điền pháp nhân **từ việc**; bảng pháp nhân **bắt buộc** gọi qua `viec.ngan`; `khoa` không chứa `phap_nhan_id` | Bỏ `phap_nhan_id` khỏi khóa/lọc; mọi truy cập bảng pháp nhân qua `viec.ngan` trong hàm năng lực |
| Có `xoa` | **Không có lệnh xóa**; dòng quá `giu_toi_da_ngay` bị ẩn khỏi `doc`/`tim` (đọc lại bằng `gom_het_han=True`) | Thay mọi `xoa`/dọn bằng khai `giu_toi_da_ngay` hoặc đánh dấu trạng thái |
| Cấu hình = bản ghi `cau_hinh` trong ngăn, `doc_cau_hinh()` | `app.cau_hinh` (đã kiểm theo `cau_hinh.schema` của gói, điền mặc định), `viec.cau_hinh` (bản chụp lúc nhận việc) | Đọc cấu hình từ `viec.cau_hinh`; bỏ bảng `cau_hinh` khỏi ngăn; thiếu cấu hình bắt buộc → `CHUA_CAU_HINH` như cũ |
| Khai báo dự kiến ở `KHAI-SDK-2.1.json` | Khai thật trong `engine.json`: `ngan_du_lieu[]`, `cau_hinh.schema`, `du_lieu.goi_migration`; `tuong_thich.sdk` `">=2.2.0 <3.0.0"` | Chuyển khai báo vào `engine.json`; chuyển `KHAI-SDK-2.1.json` vào `LUU-TRU/` của engine (không xóa) |
| Không có SQL | Có bảng ngăn thì gói **phải** có `sql/NNN_*.sql` tạo bảng trong schema `eng_<ma>` + `sql/kiem_ke.json` (bytes + SHA256 mọi tệp gói, trừ chính kiểm kê), theo đúng mẫu `e_demo_ngan` (cột hệ thống `id, phap_nhan_id, row_version, tao_luc, sua_luc, het_han_luc, viec_id`) | Viết SQL theo mẫu; **chỉ** CREATE/ALTER trong `eng_<ma>`, không đụng schema khác, không dữ liệu |
| Trường bí mật: chưa có | `bi_mat: true` → Core mã hóa, tìm theo băm; đọc ra `None` + cờ `<ma>_da_ma_hoa`; đường giải mã **chờ Anh duyệt** | Chỉ Mask dùng; Mask chưa chuyển tới khi có đường giải mã (mở che cần bản rõ) |

## 3. Quy tắc AGENTS.md cập nhật

- Quy tắc 2 ("không SQL"): **ngoại lệ duy nhất** là `sql/` migration của ngăn riêng engine theo SDK 2.2.0 (chỉ schema `eng_<ma>`, có kiểm kê). Engine vẫn không kết nối CSDL, không gửi SQL lúc chạy.
- Quy tắc 12: cổng ngăn là `viec.ngan`/`app.ngan` của SDK 2.2.0; không dùng `_chung/mau-ma/ngan.py` trong gói đã chuyển.

## 4. Lát chuyển (mỗi engine một lát, chạy song song được vì khác thư mục)

| Lát | Engine | Bảng ngăn hiện có (cổng tạm) | Ước tính | Độ khó |
|---|---|---|---:|---|
| AI-11 | e_hoi_ai | `cau_hinh` → `viec.cau_hinh`; `model_phat_hien` (engine) | 2 | vua |
| OCR-9 | e_ocr | `cau_hinh` → `viec.cau_hinh`; `han_muc_ngay` (engine, dọn → `giu_toi_da_ngay`), `luot_abbyy` (pháp nhân), `trang_thai_engine` | 4 | kho |
| HD-9 | e_hoa_don | không có ngăn; chỉ nâng `tuong_thich.sdk`, chạy lại | 0,5 | de |
| TX-7 | e_trich_xuat | `cau_hinh` → `viec.cau_hinh`; bảng ngăn TX (nếu có) | 2 | vua |

Mỗi lát xong khi: cài wheel 2.2.0 (SHA khớp `SHA256SUMS.txt`), `python -m kho_tri_thuc_sdk.thu goi/<ma>` **ĐẠT toàn bộ** (dùng `dat_cau_hinh` của CoreGia nếu DEMO cần cấu hình — CLI chuẩn phải đạt, không còn cổng thay thế), pytest xanh, kiểm độc lập mã 0, `sql/kiem_ke.json` khớp, màn `ui/` dùng `KttCore.engine(ma)` không đổi hành vi.
