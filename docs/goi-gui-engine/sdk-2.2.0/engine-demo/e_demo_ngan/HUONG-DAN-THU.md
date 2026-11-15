# Thử ngăn dữ liệu engine DEMO

Anh dùng Core tập đã được lead cài ngăn engine và SDK 2.2.0; chỉ nhập dữ liệu DEMO.

1. **Cài ngăn:** tại thư mục mã Core đã nhận tool của lead, chạy lệnh dưới đây
   (cú pháp theo phiếu K118D; thay hai đường dẫn bằng đường dẫn tuyệt đối):

   ```powershell
   python -X utf8 tools\cai_ngan_engine.py --goi "<thu-muc-goi>" --ket-noi "<tep-ket-noi-DEMO-do-lead-cap>" --ma k118g-demo
   ```

   `<thu-muc-goi>` là `goi-demo\engine\e_demo_ngan` trong bản mã đã nhận.
   Tool chỉ nhận CSDL DEMO `kho_test_*` / `kho_core_demo_g2_*`; dùng
   `python -X utf8 tools\cai_ngan_engine.py --help` để đối chiếu bản tool lead giao.
   Tool do lead bàn giao riêng; phiếu G không tạo tool và không tự chạy SQL.
   Trong **Quản trị Core → Quản lý engine**, thêm gói trên nếu chưa có,
   rồi **Bật** engine **Đếm lượt gọi theo ngày (DEMO)**.
2. **Chạy:** tạo quy trình có một bước **Đếm lượt gọi** (`dem.goi@1`),
   đầu vào văn bản. Chọn cùng một pháp nhân DEMO, chạy 3 việc mới: số lần
   tăng liên tiếp (ngăn mới trong ngày là 1, 2, 3). Đổi pháp nhân DEMO khác:
   số đếm riêng bắt đầu từ 1. Thử văn bản `DD:CAN-CUOC-DEMO-001` để ghi định danh.
3. **Xem trong pgAdmin:** mở Query Tool của CSDL Core tập, chạy:

   ```sql
   SELECT * FROM eng_e_demo_ngan.dem_goi;
   SELECT * FROM eng_e_demo_ngan.dinh_danh;
   ```

   Đối chiếu ngày, pháp nhân, số lần và `row_version`. `gia_tri` và
   `gia_tri_bam` phải là dữ liệu nhị phân, không thấy định danh bản rõ.
4. **Thử chặn engine khác (lead hỗ trợ):** dùng thẻ engine `e_demo_ngan`
   còn hiệu lực và instance tương ứng, gọi
   `POST /api/v1/engine/e_demo_khac/ngan/dinh_danh/doc` với thân
   `{"khoa":{"gia_tri":"CAN-CUOC-DEMO-001"}}`; header gồm
   `Authorization: Bearer <thẻ-engine>`, `X-KTT-Engine: e_demo_ngan`,
   `X-KTT-Instance: <instance>`, `Content-Type: application/json`.
   Giữ mã engine trong header/thẻ, chỉ đổi mã trên URL: phải nhận **403**,
   mã `KHONG_DU_QUYEN`, không trả dữ liệu. Không chép thẻ vào tài liệu hay ảnh.
5. **Giữ dữ liệu sau khởi động lại:** ghi số lần trong pgAdmin, chờ việc chạy xong,
   khởi động lại Core tập theo cách lead bàn giao, đăng nhập lại, chạy lại SELECT:
   các dòng vẫn còn. Chạy một việc mới cùng pháp nhân trong cùng ngày:
   số lần tăng thêm 1. Không dùng lại việc của phiên trước.

Phần cài PostgreSQL, chặn 403 và khởi động lại là nghiệm thu trên Core tập do
lead/Anh thực hiện; test CoreGia không thay cho các bước này.
