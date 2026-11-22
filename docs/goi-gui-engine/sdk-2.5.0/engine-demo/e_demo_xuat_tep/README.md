# Engine xuất tệp DEMO

Năng lực `tep.xuat_thong_ke@1`: nhận `text/plain` UTF-8 (có thể có BOM), tối đa 5 MiB;
trả `tep` với `ket-qua.json` (`application/json`). JSON gồm `so_dong`, `so_tu`, `dong_dau`.
Đếm mọi dòng theo `splitlines()` (kể cả dòng trống), từ theo khoảng trắng;
tệp rỗng trả 0 dòng, 0 từ, dòng đầu rỗng. Dấu xuống dòng cuối không tạo dòng phụ.

Chỉ dùng SDK: `viec.tai_tep_ra(...)` nộp bytes qua `POST viec/{id}/tep`, rồi trả
`{"loai":"tep","tep":...}` để Core ghi nhận tệp ra khi bước XONG.
Tự kiểm: `python -B -m kho_tri_thuc_sdk.thu <thư-mục-gói>`.
Phiếu có `chay_thu_demo` và `demo/mau.txt`. Khuôn engine không dùng kiểm kê riêng.

Lead thêm `e_demo_xuat_tep` vào `ENGINE_DEMO` trong công cụ đóng gói SDK khi phát hành;
phiếu K140 không sửa công cụ đó. Dùng cùng module `demo_ket_qua_nut` trên Core thử.

- 1.0.1: Dòng đầu `LOI-DEMO` chủ động báo lỗi để kiểm thử quy trình.
