# Nguồn và phụ thuộc — TC-0, 15/11/2026

## TC-7 — Sửa sau kiểm độc lập KHÔNG ĐẠT, 15/11/2026

Căn cứ bốn lỗi lead giao lúc 15:52, phiếu TC-7, TC-7-KIEM-CHUNG và quyết
định TC-Q14 đã duyệt. Vòng sửa chỉ thay `kiem_chung.py`, `tra_loi.py`; đọc
và giữ nguyên `bang_chung.py`, `chay.py`. Chỉ dùng thư viện chuẩn/SDK và
mô-đun cùng gói, không mã/thuật toán/dependency bên ngoài hoặc mạng.

Ngữ pháp giới hạn mới dùng thực thể/nhãn gần nhất trước giá trị trong
đoạn/ô đã kiểm. Các nhãn cạnh tranh và hậu tố đơn vị là quy tắc Python tự
viết cho lát này, không là schema/registry hoặc chính sách mới của Core.
Không rõ thì không căn cứ; trạng thái cần duyệt ở tầng 2/3 chỉ Vàng với
lý do/cảnh báo, không làm nhẹ lỗi giá trị/quan hệ/nguồn. Chi tiết ranh giới
và việc quote số/tiền phải đủ ngữ cảnh ở `docs/TC-7-KIEM-CHUNG.md`.

258 ca test mới là dữ liệu DEMO tự tạo, có bytes/metadata/băm thật nạp
CoreGia, không hồ sơ hoặc provider thật. Tổng 1210 passed, 0 skipped;
harness 36/36, độc lập mã 0; CLI chuẩn 0/5 CHUA_CAU_HINH/mã 1. Đã kiểm
bằng Core giả (CoreGia), NganBoNho/Local giả; 0 Cloud/model thật. Giữ
nguyên `_chung/**`, hai mẫu NGAN-0, bốn schema, DEMO đã ghim và
requirements.lock. Không sửa Core/SDK/engine khác; PR: **chờ lead mở**.

Bảng mới nhất dưới đây tính SHA-256 **chỉ thay CRLF→LF**, giữ nguyên
Unicode/khoảng trắng; gồm cả sáu tệp sửa/thêm ngoài NGUON.md. Không tự băm
NGUON.md vì tệp chứa chính bảng băm. Bảng của các lần gộp bên dưới giữ làm
lịch sử, không thay bảng mới nhất này.

| Tệp (từ gốc repo) | SHA-256 LF sau sửa TC-7 |
|---|---|
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/kiem_chung.py` | `2dc177ae26f99bcd2180f724164c236bbfd99db183ca1d640d12c942d09dffff` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/tra_loi.py` | `9925a6ac867fd09c25a3a096baba78f125a3440a6d43c170e96d0cfc41de8752` |
| `e_tra_cuu/tests/test_kiem_chung_tc_7.py` | `bd265c9b968c3a7b6f048b8d692fb759f4be3ab3ec0a087a6ac4b3cd6215793b` |
| `e_tra_cuu/docs/TC-7-KIEM-CHUNG.md` | `33f161e2540361614deca2d670480ec3f4d3489056aaa2f5bbe520504f7a5dd3` |
| `e_tra_cuu/docs/VIEC.md` | `0bf42c434172447398cbfa741faa47668f8aea1e10065eba596b50f87d58f3c6` |
| `e_tra_cuu/goi/e_tra_cuu/CHANGELOG.md` | `9f2c630b31951c326aba02804f69bc76c5b7746b88661537bca53cb7fb62076b` |

## TC-5 — 15/11/2026

Viết mới `phan_loai.py`, `quy_tac_nhom.py` và thêm đăng ký trong `chay.py`:
đúng 3 tệp runtime, chỉ thư viện chuẩn/SDK và mô-đun cùng gói. Căn cứ phiếu
TC-5, DAC-TA §3.2–3.7, TC-1-CONTRACT và quyết định 15/11 chiều; không sửa
API/manifest/schema/mẫu NGAN-0/requirements hoặc mã Hỏi AI/Core/nguồn cũ.

Bộ quy tắc/ngưỡng/dấu hiệu/quan hệ trong `tests/ho_tro_tc_5.py` tự tạo và chỉ
DEMO. Không đặt chính sách hoặc bộ nghiệp vụ mặc định vào runtime. Runtime
mở tài nguyên Core theo ref+băm đã ghim trong cấu hình ngăn. So khớp dấu hiệu
Python có giới hạn, không tuyên bố đã đo độ chính xác/pháp nhân hoặc model.

Tests dùng CoreGia có thật, NganBoNho và adapter quyền/tệp con riêng tests;
consumer AI-2 0.5.0 dùng Local giả trong một ca kiểm nối, giữ nguyên phản hồi
không căn cứ/hàng chờ. Không engine TC import/gọi Hỏi AI. Harness thêm 11 ca
phân loại/hàng chờ, tổng 24/24. Đã kiểm bằng Core giả (CoreGia), 0 Cloud/AI
thật; chưa kiểm Linux/Core/RLS/model thật. Kết quả thật ở VIEC.md.

## TC-4 — 15/11/2026

Viết mới `chuan_bi_ai.py`, `ngu_canh_ai.py` bằng thư viện chuẩn theo TC-4,
TC-1-CONTRACT, hợp đồng loại chung và mẫu chuyển tiếp AI-2/TX-0/DC-P; sửa
`chay.py` đăng ký handler. Đúng 3 tệp mã. Không dependency hoặc nguồn bên ngoài.
Tái dùng bộ đọc/kiểm miền TC-2 và API SDK; không sửa Core/SDK/mẫu chung/nguồn cũ.
Hai mẫu NGAN-0, bốn schema và requirements.lock giữ nguyên, test băm LF.

Test/harness dùng fixture DEMO tự tạo, bytes thực nạp CoreGia và cấu hình
NganBoNho; mở rộng bốn ca chuẩn bị. Consumer `hoi_yeu_cau.py`/`khuon_json.py`
của Hỏi AI có thật chỉ được import trong tests ngoài gói; provider Local giả
không mạng, không thay consumer/runtime engine khác. Đã kiểm bằng Core giả
(CoreGia); chưa kiểm model/Cloud/Core/RLS thật hoặc Linux. Kết quả ở VIEC.md.

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

## TC-6 và việc gộp TC-5 — 15/11/2026

TC-6 viết mới `cau_hoi.py`, `xep_hang.py`, đăng ký trong `chay.py`, theo phiếu
TC-6 và TC-1-CONTRACT. Chỉ thư viện chuẩn/SDK, không nguồn hoặc dependency mới.
Các seam phân giải câu hỏi/allowlist/binding là quy ước adapter CoreGia, cần
Core/lead review; không là API SDK mới hoặc số đo chất lượng model thật.

Việc gộp giữ nguyên bốn mô-đun nghiệp vụ và hai bộ test TC-5/TC-6; chỉ hợp nhất
đăng ký/handler, danh sách stub, harness và tài liệu. Hai biên bản cũ và hai
mục CHANGELOG giữ nguyên số liệu lịch sử (17/17 TC-6, 24/24 TC-5); kết quả
sau gộp là 814 passed, 0 skipped, harness 28/28 và độc lập mã 0. Đã kiểm bằng
Core giả (CoreGia), 0 Cloud/model/provider thật; CLI chuẩn vẫn 0/5 lỗi
CHUA_CAU_HINH/mã 1, C-TC-01 đã ghi trong VIEC; chưa kiểm Core/RLS/Linux thật.

Bảng kiểm sau gộp dưới đây tính SHA-256 **chỉ thay CRLF→LF**, giữ nguyên
Unicode/khoảng trắng. Gồm sáu tệp giải xung đột và bốn mô-đun nghiệp vụ được
giữ lại; không tự băm NGUON.md vì tệp này chứa chính bảng băm. Hai mẫu NGAN-0,
bốn schema, DEMO và dependency giữ nguyên các băm/nguồn đã ghi phía trên.

| Tệp (từ gốc repo) | SHA-256 LF sau gộp |
|---|---|
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/chay.py` | `13e3033d7e8d3232c36d30229bb28f7eb958ee6b880a5773c59aa9f5bf03d411` |
| `e_tra_cuu/tests/chay_demo_voi_core_gia.py` | `d16feb580d37ac7fbf8ed72280588c905e2790e62f322c2ceeb0c84fd7676012` |
| `e_tra_cuu/tests/test_tc_2.py` | `93a5723fc29927e7d3684d0913693defe37b701f40c41f41ace6906cbab5a084` |
| `e_tra_cuu/goi/e_tra_cuu/README.md` | `69e301a02aeed82aa1918d429682dc45846865333043794175a4fca6298b64ec` |
| `e_tra_cuu/goi/e_tra_cuu/CHANGELOG.md` | `9c8d962bf1a5525c9670f7063f75d80a325ad6efc5aacf1ce1935101ba97c1de` |
| `e_tra_cuu/docs/VIEC.md` | `af235c956873d24782bb68ddccea6e66c4b3d95737bdb3265d41593982c84cda` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/phan_loai.py` | `9e36a2a06d3b97613ec7d07237c6d9abb76039526adcd16758579e502d561632` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/quy_tac_nhom.py` | `aa787e8fef6cca744c777a3bf820350f5947a40cadfc3b15db2f9cc9a271c793` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/cau_hoi.py` | `c58c2aa90d1784933960d39d5797a7e575642475d45e12f3372ee8784e08c50f` |
| `e_tra_cuu/goi/e_tra_cuu/e_tra_cuu/xep_hang.py` | `6d062ebd1bbd67cd554d7d7f1404caa6ddc05d1860692446d1f20358e9018c02` |

## TC-9 — 15/11/2026

Viết mới `ui/cau_hinh.js`, `ui/trang_thai.js`, `trang_thai.py`, bổ sung seam
thuần trong `chay.py` theo phiếu TC-9; đúng 4 tệp mã, không nguồn/dependency
bên ngoài. Hai mẫu NGAN-0 và bốn schema tiếp tục giữ nguyên, test SHA-256 LF.
Các băm TC-6 ở bảng trên là lịch sử tại thời điểm gộp, không là băm hiện tại
của chay/README/CHANGELOG/VIEC đã cập nhật qua TC-7…9.

UI dùng ES module/DOM/Intl có sẵn, chỉ KttCore của chính engine. Node
24.18.0 chạy test không mạng/không npm. Tên quyền xem theo pháp nhân và hình
dạng phản hồi KttCore là đề nghị chờ Core đối chiếu; chưa phải SDK thật.
Fixture báo cáo/cấu hình/bài đo đều DEMO trong RAM, CoreGia tạo tệp+băm thật;
không dùng nguyên văn/câu hỏi trong bản ghi dot_kiem. Không sửa Core/SDK,
nguồn cũ hoặc requirements.lock. Chưa kiểm trình duyệt thật/Linux/lưu bền.
