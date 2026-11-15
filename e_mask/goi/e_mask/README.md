# e_mask — Che định danh văn bản

MASK-3b, MASK-4, MASK-5, MASK-6 đã được kiểm bằng Core giả (CoreGia) với port quyền DEMO được tiêm ngoài gói. Hai năng lực che/mở che văn bản đã có handler; phần tệp Word/Excel/PDF chưa được công bố. Không gọi Cloud hoặc engine khác.

Mọi trạng thái đi qua `Ngan`: định danh, bí danh tạm, danh sách chờ, mã yêu cầu, dấu gặp/chống trùng. Chốt trong một lô có CAS chung; xung đột trả `MASK_XUNG_DOT`, thử lại được. Khi SDK chưa có ngăn thật, `chon_ngan(app)` dùng RAM và cảnh báo một lần. Khởi động lại mất dữ liệu RAM. Hai tệp `kho_tam.py`, `cau_hinh_may.py` chỉ giữ làm hiện vật lịch sử, không nằm trên đường chạy handler.

Nguồn quyền/mã yêu cầu phải do Core tin cậy cấp. `tao_app(ngan=..., quyen=...)` dành cho bên tích hợp; không nhận port hay danh tính từ dữ liệu việc. Thiếu nguồn quyền, engine trả `MASK_NGU_CANH_CHUA_XAC_MINH`. CLI SDK chuẩn chưa tiêm nguồn này nên hai ví dụ sẽ bị chặn, không báo thành công giả.

Chạy DEMO có port tin cậy, từ thư mục repo:

```text
.venv/Scripts/python e_mask/tests/chay_demo.py
```

Linux dùng Python trong môi trường tương ứng. Đặt `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` trước khi kiểm gói. Adapter DEMO chỉ ở `tests/`, không có chế độ mở kho giả trong gói.

Bốn từ điển sạch đã được lead cấp theo lệnh giao 15/11, nằm tại `e_mask/tu_dien/`; kiểm SHA khi nạp. Thiếu/sai SHA bị chặn. Test so băm với nguồn tham chiếu ngoài gói; test so băm `ngan.py`, `cau_hinh.py` tạm skip “chờ NGAN-0 gộp”.

Trần văn bản 500.000 ký tự, danh sách đã biết 500 mục, giá trị 300 ký tự, nhóm 20 ký tự. Không cắt ngầm. Lô ngăn hiện tối đa 100 lệnh: nếu toàn bộ thay đổi vượt mức này, từ chối cả việc; cần Core hỗ trợ giao dịch lớn để xử lý nhiều cụm. JSON tệp đầu vào tạm có trần kỹ thuật 4 MiB, chưa phải trần tệp nghiệp vụ đã được Anh chốt. Không dùng trần đầu vào làm trần đầu ra.

Màn `ui/duyet_dinh_danh.js` gọi `KttCore.engine("e_mask").ngan`; Core phải kiểm `admin_core` khi đọc/ghi và nạp màn. Duyệt/từ chối giữ bí danh tạm còn tham chiếu; dọn dùng cùng CAS với che/mở che. Màn đã kiểm bằng Node/KttCore giả, chưa kiểm trong trình duyệt Core thật. Khai báo chờ SDK 2.1 nằm trong `KHAI-SDK-2.1.json`, không mở rộng phiếu 2.0.

Heuristic còn giới hạn nhận diện tên viết thường không nhãn; test DEMO không chứng nhận đủ điều kiện Cloud. Xem `NGUON.md` và báo cáo bàn giao trong `e_mask/docs/`. Chỉ dùng thư viện chuẩn và SDK 2.0.0.
