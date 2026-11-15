# Dữ liệu DEMO

Hai tệp DOCX chỉ chứa dữ liệu giả có nhãn DEMO: Công ty DEMO Ánh Dương,
1.000.000 VND, ngày 2026-10-30. Không có giá trị giao dịch.
Tệp thứ nhất có số tự động, ô rỗng và ô gộp; tệp thứ hai có Track Changes.
Nguồn sinh xác định: `e_trich_xuat/tests/mau_docx.py`, nằm ngoài gói chạy.

Hai DEMO TX-3 hậu kiểm/xuất đang chờ review payload/schema, **chưa khai trong
manifest/runtime**. Fixture ở `e_trich_xuat/tests/mau_tx3.py`: chạy chuẩn bị
TX-2 thật bằng CoreGia để có tệp hồ sơ/băm/kích thước thực, sau đó AI giả →
hậu kiểm → xuất JSON/Excel. Chỉ dữ liệu DEMO, ngăn RAM, 0 Cloud.
Cổng `tests/chay_demo_voi_ngan_gia.py` ngoài gói chạy đủ 5 DEMO và ghi rõ
hai năng lực TX-3 chưa đăng ký; không điền cấu hình ngầm trong engine.
