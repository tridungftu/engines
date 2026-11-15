# Nguồn và phụ thuộc — TC-0, 15/11/2026

Gói mới theo phiếu `e_tra_cuu/docs/GIAO-CODEX-e_tra_cuu.md` §1–5,
API-ENGINE-v1 và hai hướng dẫn SDK 2.0.0. Không có lõi cũ tại chỗ để chuyển;
không tạo `ma-nguon/`. Mã khung/schema/test mới viết trong lát TC-0.

| Thành phần | Nguồn nội bộ repo | Phiên bản / SHA-256 |
|---|---|---|
| SDK | `docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | 2.0.0 · `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `e_tra_cuu/ngan.py` | `_chung/mau-ma/ngan.py`, NGAN-0, PR #34 theo lead | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `e_tra_cuu/cau_hinh.py` | `_chung/mau-ma/cau_hinh.py`, NGAN-0, PR #34 theo lead | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |

Hai mẫu chép nguyên bytes bằng Copy-Item, không sửa hoặc import `_chung` ở runtime.
Test so SHA-256 **chỉ đổi CRLF thành LF**, không strip/biên tập.
Băm SDK tính trên wheel nguyên bytes, đã khớp `SHA256SUMS.txt`.

Runtime chỉ thư viện chuẩn Python >=3.11 và SDK 2.0.0; ghim SDK trong
`requirements.lock`. Không thêm thư viện ngoài. Pytest 9.1.1 là công cụ test có
sẵn qua venv `--system-site-packages`, không đóng gói và không phải dependency
runtime. Kiểm thực tế trên Windows/Python 3.13.14; chưa chạy Linux.

SDK và hai mẫu lấy từ bộ nguồn nội bộ được giao. Metadata wheel không khai trường
License; không tự suy diễn giấy phép nguồn ngoài. Lát này không tải/nhúng mã,
mô hình hoặc dữ liệu bên ngoài. Không chép schema của loại chưa duyệt TC-Q13.
Chỉ dữ liệu DEMO trong test, không tài liệu thật; không mạng/Cloud khi kiểm.

## TC-1 — 15/11/2026

TC-Q13 đã duyệt tại `_chung/docs/QUYET-DINH-ANH-20261115-CHIEU.md` câu 5.
Schema mới theo phần TC-P cuối `_chung/docs/LOAI-DU-LIEU-RIENG.md` và phiếu
Tra cứu §2; chi tiết thực thi ở `e_tra_cuu/docs/TC-1-CONTRACT.md`.
Không sửa tài liệu loại chung. Câu “chưa duyệt” phía trên mô tả lịch sử TC-0.

| Bản chép trong `contract/` | Nguồn `_chung/contract/` | SHA-256 sau chỉ đổi CRLF→LF |
|---|---|---|
| `ho_so_tra_cuu.schema.json` | Cùng tên, mới viết TC-1 | `2364deaf44c8fe4923640f77523e5b82c91daca27d90d7c7a6c018921df28ea9` |
| `van_ban_tai_lieu.schema.json` | Cùng tên, giữ nguyên | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `yeu_cau_ai.schema.json` | Cùng tên, giữ nguyên | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
| `tra_loi_ai.schema.json` | Cùng tên, giữ nguyên | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |

Chép nguyên bytes; pytest kiểm cả bytes và SHA-256 LF. Hai mẫu NGAN-0 giữ nguyên.
Chỉ 5 tệp schema nguồn/bản chép trong TC-1, không thay manifest/chay.py hoặc
schema đã khóa. Không thêm dependency, không dùng bộ đọc cấu hình làm validator
chung; bộ đánh giá schema mới và adapter CoreGia chỉ ở tests. Mọi fixture chỉ
DEMO với bytes được nạp vào CoreGia, metadata/băm tính thật, không tải mạng/AI.

## TC-2 — 15/11/2026

Runtime mới/sửa đúng `ho_so.py`, `kiem_dau_vao.py`, `chay.py`; không thêm
dependency. Giữ nguyên bytes hai mẫu NGAN-0 và cả bốn schema đã chép ở TC-1;
test SHA-256 sau CRLF→LF tiếp tục áp dụng. Không sửa nguồn/schema chung/Core/SDK.

Tám tệp trong `demo/` là dữ liệu giả mới tạo cho TC-2: nguồn văn bản Công ty
DEMO Ánh Dương, phong bì OCR DEMO, danh mục DEMO và năm JSON yêu cầu. Không phải
đáp án hoặc số đo chất lượng đã được nghiệp vụ nghiệm thu. Tên/metadata/băm
của tệp con nằm trong JSON yêu cầu, băm bytes chính xác từng yêu cầu ở
`engine.json.chay_thu_demo`. Không đổi Unicode hoặc canonical hóa để chữa băm.

Harness test nạp ba tệp con theo thứ tự gốc → OCR → danh mục bằng API
`CoreGia.them_tep`; vì vậy ba ID `tep-1/tep-2/tep-3` trong DEMO thực sự trỏ
bytes đã tải vào kho RAM đó. Có kiểm lại bytes/metadata/băm trước chạy; runtime
không hardcode các ID hoặc nạp dữ liệu này. SDK CLI gốc thiếu ngăn/cấu hình/
quyền tệp con; không diễn giải các ID như nguồn có sẵn ở Core thật.

Adapter `CoreGiaTepCon`/`CuaNguonGia` và dữ liệu cấu hình chỉ trong tests ngoài
gói; không đưa vào runtime. Đã kiểm bằng Core giả (CoreGia), mạng ngoài/Cloud=0;
chưa chứng nhận RLS thật hoặc Linux. Quyền/ghép nguồn/vòng đời/ACK chờ C-TC-02/03,
ngăn/cấu hình CLI chờ C-TC-01, log/lỗi trần/lease SDK chờ C-TC-05.

## TC-3 — 15/11/2026

`cat_doan.py`, `vi_tri.py` viết mới bằng thư viện chuẩn Python, theo phiếu
TC-3, `TC-1-CONTRACT.md` §3–5 và DAC-TA §3.4/8/9; không lấy thuật toán/mã hoặc
dependency bên ngoài. Sửa `chay.py` đăng ký handler cắt và `kiem_dau_vao.py`
đóng ba nợ TC-2 do lead giao. Tổng **4 tệp mã**, dưới trần khoảng 5 tệp/lát.
Không có nguồn cũ tại chỗ, không sửa Core/SDK/engine khác hoặc contract chung.

Các map bảng/ô và `hang_tieu_de` là quy ước snapshot trong phần mở sẵn có của
`van_ban_tai_lieu` v1; không sửa schema. Phép chiếu TAB + LF/CRLF được kiểm đúng
chuỗi nguồn trước khi tạo offset, không đoán hộp/ô/tiêu đề. Kiểu nguồn khác
chưa có map cần adapter Core cấp, ghi C-TC-02/03 và L-TC-01 trong VIEC.

Giữ nguyên hai mẫu NGAN-0 và bốn schema, tiếp tục so băm CRLF→LF với các giá trị
ở bảng trên. SDK 2.0.0 từ wheel offline, băm vẫn khớp SHA256SUMS.txt. Không
thêm dependency; `requirements.lock` giữ nguyên. Phiên bản 0.1.0 còn nội bộ.

Test/harness mới dùng dữ liệu tự tạo DEMO: Điều/Khoản xuyên trang/trang rỗng,
bảng ô gộp/ô rỗng và tiêu đề lặp, NFC/NFD/emoji, 1.000.000 VND, 2026-10-30.
Không dùng tài liệu thật hoặc model. Bản adapter quyền Core chỉ trong tests;
seam ghim phong bì/metadata và quyền xuyên bước chưa là API Core thật.

Kiểm hồi quy đầu trên checkout Windows phát hiện Git auto-CRLF làm lệch bytes
DEMO nguồn so với SHA đã ghim. `e_tra_cuu/.gitattributes` cố định LF cho demo/*;
bytes LF hiện tại khớp nguyên bytes HEAD và băm đã đăng ký, không sửa băm hay
canonical hóa trong runtime để bỏ qua sai nguồn. Đã kiểm bằng Core giả (CoreGia),
AI/Cloud=0; chưa kiểm Linux/RLS/Core thật/UI/chất lượng model.
