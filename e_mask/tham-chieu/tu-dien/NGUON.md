# Nguồn từ điển nhận diện — e_mask

*Lead chép ngày 15/11/2026 từ Mask v2 gốc trên máy Anh (thư mục `Mask file v2/privacy/data/`, chỉ đọc), theo QUYET-DINH-ANH-20261115 câu 9. **Chờ Anh xem danh sách trước khi gộp.***

| Tệp | Dòng | SHA-256 bản gốc | SHA-256 bản trong repo | Đã lọc |
|---|---:|---|---|---|
| `common_acronyms.txt` | 4 | `c6da5573a6ed71214dee1b0e04a830b2a72a5b8dbbb1a26ec5083920eb9b8c6b` | `920f0952f2584ece4c37d5419c073cd6f60cf151da3b38b1e68fdd6a2bb24f4e` | Bỏ `HSBC` |
| `leftover_allowlist.txt` | 67 | `ec276b1042a72c745081ef032bf20f1082ec35ab5a5fec44ffe6a825d0a9b502` | giống bản gốc | Không bỏ gì |
| `vn_places.txt` | 80 | `d31936260f58ff3f296994cf4fc5ceca87f5f5df0c89ca11da37330945b3402e` | `e991d899a1fa2265082e871715a653c9ca4fd7ed233a8d3951fb80b7a2d41847` | Bỏ `Á Châu`, `Sông Đà` |
| `vn_surnames.txt` | 53 | `6ec090044a9809f2e06afa962a0c23483119b5454a60a649291687e07717849d` | giống bản gốc | Không bỏ gì |

## Cách lọc

- Đọc hết 204 dòng. Không có tên đối tác, tên người cụ thể, mã số thuế, số tài khoản hay địa chỉ chi tiết.
- Bỏ 3 mục **trùng tên tổ chức có thể là đối tác**: `HSBC` (ngân hàng), `Á Châu` (trùng tên ngân hàng Á Châu), `Sông Đà` (trùng tên tổng công ty xây dựng). Ba mục này nằm trong danh sách "bỏ qua, không che", nên nếu giữ lại thì tên tổ chức đó sẽ lọt qua. Bỏ đi thì Mask chỉ gợi ý che thêm, an toàn hơn.
- Bốn tệp đều là danh sách "không phải định danh" (viết tắt, cụm thông dụng, địa danh dễ nhầm tên người) và danh sách họ người Việt để gợi ý. Không có tệp tên riêng đối tác.
