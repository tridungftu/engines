# SDK 2.2.0 — ghi chú thay đổi (phát hành 15/11/2026, Anh duyệt)

Bản này **chỉ thêm, tương thích ngược** với 2.0.0, 2.1.1, 2.1.2. Đây là lô 2 của CĐ-33/34/35: ngăn dữ liệu và cấu hình của engine. Anh duyệt phát hành ngày 15/11/2026.

## Engine dùng được gì mới
- **`app.ngan` / `viec.ngan`**: đọc, tìm, ghi lô vào ngăn riêng của engine (bảng thường trong schema `eng_<ma>` do Core cất).
  - `app.ngan.doc(bang, khoa)` trả về bản ghi hoặc `None`.
  - `app.ngan.tim(bang, loc=…, gioi_han=…)` trả về một trang kết quả.
  - `with app.ngan.lo() as lo:` gom lệnh `them` / `sua(…, row_version=…)` / `lay_hoac_tao`, tối đa 100 lệnh. Gửi một lần khi ra khỏi `with`; một lệnh lỗi thì không lệnh nào được ghi.
  - Hai việc sửa cùng lúc thì một bên nhận `NganXungDot` (`thu_lai_duoc=True`) để thử lại.
  - Trong hàm năng lực dùng `viec.ngan` để Core biết pháp nhân và việc. Bảng phạm vi pháp nhân bắt buộc gọi trong việc.
- **Không có lệnh xóa.** Dòng quá `giu_toi_da_ngay` chỉ bị ẩn khỏi `doc`/`tim`; truyền `gom_het_han=True` để đọc lại.
- **Trường `bi_mat`** (dành cho Mask):
  - Core mã hóa khi ghi và tìm được theo đúng giá trị (qua băm);
  - khi đọc ra, trường này trả `None` kèm cờ `<ma>_da_ma_hoa`. Đường giải mã cho engine chờ Anh duyệt.
- **Cấu hình:**
  - `app.cau_hinh` là cấu hình đã kiểm theo `cau_hinh.schema` của gói và đã điền mặc định;
  - `viec.cau_hinh` là bản chụp lúc nhận việc;
  - `@app.khi_doi_cau_hinh` được gọi khi Admin đổi cấu hình.
- **`app.hang_cho()`** trả `{so_viec_cho, so_viec_dang_chay}`.
- **Phiếu `engine.json`** có thêm khai báo (đều tùy chọn): `ngan_du_lieu[]`, `du_lieu.goi_migration` (thư mục SQL + kiểm kê có băm, giống gói module), `cau_hinh.schema`. Mẫu đầy đủ: `engine-demo\e_demo_ngan\`.

## Core giả (`kho_tri_thuc_sdk.thu`)
- `CoreGia` có ngăn trong bộ nhớ, **cùng ngữ nghĩa Core thật**: lô nguyên tử, CAS, duy nhất, phạm vi pháp nhân, hết hạn, không xóa, trường bí mật.
- Thêm `gay_xung_dot_ngan`, `xem_ngan`, `dat_cau_hinh`. `MayChuGia` phục vụ cùng đường HTTP.

## Đã kiểm
- Cài wheel này vào môi trường Python sạch, chạy `python -m kho_tri_thuc_sdk.thu` cho 4 engine DEMO (`e_demo_chu_hoa`, `e_demo_dem_tu`, `e_demo_doc_tep`, `e_demo_ngan`): **đều đạt**.
- Chạy thật trên Core tập 8818 (CSDL DEMO): engine `e_demo_ngan` đếm 1→5 qua 5 lần chạy, qua cả nâng bản gói 1.0.0 → 1.1.0 và khởi động lại Core.
- Test SDK `test_sdk_220_ngan` (29 ca, qua bộ nhớ và HTTP, có ca hai việc tranh nhau đúng một lần thử lại) cùng các bộ SDK cũ đều xanh.

Mã nguồn: main `e4f8f2c`.
