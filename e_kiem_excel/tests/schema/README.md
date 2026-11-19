# Schema kết quả EX-2 — chờ lead duyệt trong PR

`toan_ven.schema.json` dùng JSON Schema Draft 2020-12, bám phiếu §5.1.
Schema khóa kết quả K1–K7; EX-3 mở phần K8 và trình lead duyệt cùng thay đổi
tương ứng. Không đổi hợp đồng API/SDK.

- `phien_ban = 1` là số nguyên định danh cấu trúc. Mọi giá trị số nghiệp vụ,
  số đếm, tỷ lệ trong tệp JSON là **chuỗi thập phân**. Các trường đếm trong
  phong bì SDK vẫn là `int` theo §4.3.
- `gia_tri` là giá trị ô hoặc tổng giá trị liên quan theo thuật toán nguồn;
  có thể là chuỗi số, chữ, boolean hoặc null. Không suy số tiền hay đơn vị
  từ một giá trị ô tùy ý. EX-1 chưa có trường tiền xác định; hàm `so_tien`
  kiểm riêng qua CoreGia, chưa rõ tiền tệ trả cả trường null.
- Mỗi bảng có tên trường, đủ cột của bảng gốc. `o` là `Sheet!A1`;
  riêng phát hiện có thể trỏ tới một sheet, `Workbook` hoặc `[n]` như mã gốc.
- `k1_so_ten_loi` và `k4_khac_ban_hien` giữ thông tin có trong mã gốc nhưng
  ví dụ rút gọn §5.1 chưa liệt kê. K4 giữ tối đa 300 ô khác/cặp như nguồn.
- `k1_lien_ket_ngoai[].ten_tep` chỉ chứa tên tệp; `so_cong_thuc = "0"`
  phân biệt liên kết không có công thức đang dùng. Không mở nguồn liên kết.
- K2 và K7 lấy nhóm theo bộ module; không bộ thì Chưa phân nhóm.
- `o_dich`: ô thực dùng hoặc null; `bo_nhom`: `{ten_bo,bam}` hoặc null.
  Băm SHA-256 JSON UTF-8 với sort_keys/ensure_ascii=False/separators=(",",":").
- `k7_cay` giữ đủ chín cột nguồn: cap, ten, o, cong_thuc, gia_tri, loai, nhom,
  tai_lieu, ghi_chu; thêm boolean `la` cho Nhập tay/Nhóm nhập tay. `cap` là
  chuỗi số; `nhom = null` ở nút không phân nhóm; o có thể là dải/file ngoài/rỗng.
- `k8_nguon` rỗng và `tep_bao_cao` null, chờ EX-3; `canh_bao` ghi rõ.
- Không xuất khóa nội bộ `_ngoai`. Ngày/giờ có sẵn trong ô dùng ISO.
- UTF-8, trần 20 MiB kiểm theo byte trong lúc mã hóa; vượt thì từ chối.

Pytest kiểm toàn bộ dữ liệu DEMO bằng bộ kiểm stdlib cho tập từ khóa đã dùng,
có ca cố ý sai kiểu số và thiếu cột để kiểm từ chối. Không thêm dependency runtime.
