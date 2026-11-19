# Nguồn và giấy phép — EX-6, 19/11/2026

Trạng thái hiện hành: đủ EX-0…EX-6; các mục EX-0…EX-5 dưới đây là lịch sử
chuyển mã theo từng lát. Bảng tổng hợp và SHA-256 hiện hành ở cuối tệp.

Chỉ dùng dữ liệu DEMO giả. EX-1 chuyển thuật toán từ nguồn đã ghim dưới đây;
không sửa nguồn tham chiếu và không thêm dependency runtime.

| Nguồn | Phiên bản / giấy phép | Phần dùng / SHA-256 wheel |
|---|---|---|
| [openpyxl trên PyPI](https://pypi.org/project/openpyxl/3.1.5/) | 3.1.5 / MIT | Nạp hai workbook công thức/giá trị trong RAM; `5282c12b107bffeef825f4617dc029afaf41d0ea60823bbb665ef3079dc79de2` |
| [et_xmlfile trên PyPI](https://pypi.org/project/et-xmlfile/2.0.0/) | 2.0.0 / MIT | Dependency openpyxl; `7a91720bc756843502c3b7504c77b8fe44217c85c537d85037f0f536151b2caa` |
| [defusedxml trên PyPI](https://pypi.org/project/defusedxml/0.7.1/) | 0.7.1 / PSF License | openpyxl tự chọn bộ phân tích chống thực thể; `a352e7e428770286cc899e2542b6cdaedb2b4953ff269a210103ec58f6198a61` |
| SDK trong `docs/goi-gui-engine/sdk-2.2.0/` | 2.2.0 / nội bộ | `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` |

Tên wheel: `openpyxl-3.1.5-py2.py3-none-any.whl`,
`et_xmlfile-2.0.0-py3-none-any.whl`, `defusedxml-0.7.1-py2.py3-none-any.whl`.
Metadata nguồn lấy từ API JSON PyPI theo đúng phiên bản; wheel tải qua mirror
`https://mirrors.aliyun.com/pypi/` vì máy không tải được từ files.pythonhosted.org.
Mỗi wheel đã đối chiếu SHA-256 với metadata PyPI trước khi cài offline.
Wheel dùng cho test nằm ngoài gói, trong `.venv/banh/`, không đưa vào git.

Khung tham khảo trong repo engines, commit `0e759eff098979891720c8a057c6a5fd03b25ddb`
được phiếu engine ghim (nội bộ):

- `docs/goi-gui-engine/sdk-2.2.0/engine-demo/e_demo_doc_tep/`: bố cục, cổng nhận `tep`;
  bỏ hoàn toàn nhánh import Core trong mẫu.
- `e_hoa_don/goi/e_hoa_don/e_hoa_don/chay.py`: mẫu `_ghi()` chỉ ghi mã cố định,
  bọc lỗi giới hạn và đọc tệp có trần.
- `kho_tri_thuc_sdk/engine.py` trong wheel đã ghim: đối chiếu `_lam()` để bọc
  chuẩn hóa MIME tại cổng; không chép lại vòng xử lý và không sửa SDK.
- `e_hoa_don/tests/`: ý tưởng AST/import độc lập, CoreGia, cách ly test, cài sạch.
- `e_ocr/goi/e_ocr/requirements.lock`: cú pháp ghim wheel có hash.

Mã tham chiếu nghiệp vụ chỉ đọc, repo `tridungftu/review_xaydung`, commit
`1bed645ed56a36a59995afe1617af9dec83b8d82` (giấy phép nội bộ theo `ma-nguon/NGUON.md`):
`toan_ven.py` SHA-256 `a97396de2be4cecfb060cd52689f4eec648f7904a7fd132089e10e3c897f6023`;
`master_hd.py` SHA-256 `7c82daf635be14153599fb65a1059100c71b0b19a8a057e781187023688ae124`.
EX-0 chỉ đọc điều kiện K1–K8 để cài dấu hiệu DEMO. Script XML và bộ chặn
là mã mới nội bộ. Bảng chuyển EX-1:

| Nguồn đã ghim | Đích trong gói | Điều chỉnh |
|---|---|---|
| `toan_ven.py` 42–50, 144–229 | `e_kiem_excel/tham_chieu.py` | Giữ nguyên hằng và hàm, dời import |
| `toan_ven.py` 54–142 | `e_kiem_excel/so_do.py` | BytesIO; tên tệp ngoài bỏ thư mục; TEP_HONG; đóng workbook |
| `toan_ven.py` 262–515 | `e_kiem_excel/kiem_tra.py` | Nhận SoDo/tham số; K2 chưa phân nhóm; tổng bằng Decimal; K6 bỏ tài liệu nghiệp vụ viết cứng |
| `master_hd.py` 43–72 | `e_kiem_excel/chuan_hoa.py` | Giữ quy tắc chữ/dấu phân cách; so/num trả Decimal hữu hạn; thêm so_tien theo SDK |

K7/K8, bộ nhóm module và phần trích hợp đồng không được chuyển trong EX-1.
Điều phối K1–K6, kiểm hủy, mã hóa/schema JSON và tải kết quả là lớp bọc mới.
Test kiểm SHA-256 sau chuẩn hóa CRLF→LF trong RAM, rồi import mã gốc
chỉ trong test tương đương. Không gọi mã tham chiếu từ runtime.

SHA-256 fixture ở `tests/demo/bam-fixture.json` ngoài gói; sinh lại bằng
`python -B e_kiem_excel/tests/demo/sinh_demo.py`. Kiểm kê SHA mọi tệp gói thực hiện EX-6.

## EX-4 — chuyển mã đọc bảng, 18/11/2026

Nguồn `master_hd.py`, commit/SHA-256 đã ghim ở trên, không sửa tệp nguồn:

| Dòng nguồn | Vào gói | Điều chỉnh |
|---|---|---|
| 43–51, 62–71 | `doc_bang.py`: `_nfc`, `_bo_dau`, `_num` | Hàm riêng tư theo phân công; lead gộp vào `chuan_hoa.py` sau EX-1. `_num` dùng Decimal, bỏ bool và số không hữu hạn |
| 629–728 | `doc_bang.py`: `_hdr_text`, `tim_bang_chi_tiet`, `khoa` | Giữ cách tìm cột, chấm điểm, nhóm, công thức khóa và hậu tố; kiểm hủy giữa vòng lặp; lỗi qua `LoiNghiepVu` |
| 730–765 | `doc_bang.py`: `LABELS`, `tim_so_tong_hop` | Decimal; bỏ ngưỡng `abs(v) > 1`; nhận thêm số dạng chữ qua `_num` kèm cảnh báo khi xuất |

Phần tạo phong bì/JSON, kiểm tham số, nhận đơn vị tiền và cảnh báo là mã mới nội bộ
bám phiếu §4.2–4.3, §5.2. Không thêm dependency, không mạng, không ghi tệp trên máy.
`chay.py` chỉ nối `excel.doc_bang@1`; helper đọc chung thêm trả bytes đã kiểm,
không đổi hành vi năng lực toàn vẹn. Kiểm kê SHA-256 toàn gói để EX-6 thực hiện.

## EX-5 — khuôn tổng quát, 18/11/2026

`doc_tong_quat.py` là mã mới nội bộ theo phiếu §4.2. Không thêm dependency.
`doc_bang.py` nay import trực tiếp `nfc/bo_dau/num` từ `chuan_hoa.py` của EX-1,
không còn ba bản helper riêng EX-4; không sửa hàm nào trong `chuan_hoa.py`.

`bo_nhom.py` lấy nguyên tệp đang triển khai của EX-2 để gói này tự chạy độc lập,
không viết lại matcher. SHA-256 bytes lúc nhận: `319f034694ab3dacf4c8ea6f628ddecb80a5e67ffdb67d681c804d3b50488255`.
EX-5 import `doc_json`, `kiem_tu_khoa`, `khop_tu_khoa(tu, van_ban)` từ đúng module
này. Lead giữ một tệp chung khi gộp EX-2/EX-5; không cần hai bản thuật toán.
Hai DEMO mới do `tests/demo/sinh_tong_quat.py` sinh bằng OOXML/ZIP tất định,
ghép vào script sinh chung và bảng băm fixture; dữ liệu/đáp án đều giả.

## EX-2 — cây truy vết và bộ nhóm, 18/11/2026

| Nguồn đã ghim | Đích | Điều chỉnh |
|---|---|---|
| `toan_ven.py` 516–604 | `kiem_tra.py`: `k7_cay_truy_vet` | Giữ thứ tự/nút/dải/mẫu/đại diện; ô đích và phân nhóm theo tham số; tổng Decimal; hủy và từ chối vượt trần |
| `toan_ven.py` 750–762 | `kiem_tra.py`: `_xep_lai` | Giữ cách hạ mức liên kết ngoài theo cột cây; câu mô tả dùng ô đích chung |
| `master_hd.py` 741–765 | `kiem_tra.py`: `_tim_o_dich` | Cùng vùng quét/số đầu bên phải; dùng danh sách nhãn module thay LABELS; giữ số 0/nhỏ qua num Decimal |
| Phiếu §4.1.1 | `bo_nhom.py` | Mã mới kiểm JSON/bộ nhóm và so từ khóa; `#` dùng bảng trạng thái không backtracking; không chạy regex do module cung cấp |
| `toan_ven.py` 231–260 → Phiếu Phụ lục A | Fixture ngoài gói | Bộ Review TTKL chỉ nằm trong tests/demo; không chép nhóm/tài liệu nghiệp vụ vào runtime |

`LABELS/tim_so_tong_hop` Decimal đã có ở EX-4 trong `doc_bang.py` (bảng trên).
EX-2 giữ nguyên tệp này và năng lực đọc bảng theo phân công EX-5; không tạo bản
LABELS thứ hai. Hàm tìm ô đích riêng cần nhãn tùy biến nên chuyển cùng thuật toán
quét với helper Decimal dùng chung của EX-1. K2 phân nhóm số gõ tay; K6 lấy tài liệu
từ bộ nhóm. K7 trước K6, sau cùng `_xep_lai`, đúng thứ tự nguồn.

Khác biệt có chủ đích: đổi tên Ngoài 7 nhóm thành Ngoài nhóm; Phụ lục A nhóm 6
xét cả nhãn dòng; giới hạn 14 tầng/12 mẫu từ chối thay vì cắt ngầm. Thêm trần
100.000 nút, 250.000 ô/dải, 500.000 lượt đọc ô để chặn mở rộng workbook từ tham chiếu.
Tổng Decimal đặt precision theo toán hạng, không làm tròn mặc định ở chữ số thứ 28.
Không sửa nguồn đã ghim, không thêm dependency. Số đo lệch/test ở docs/VIEC.md.

## EX-3 — K8 và báo cáo Excel, 19/11/2026

| Nguồn đã ghim | Đích | Điều chỉnh |
|---|---|---|
| `toan_ven.py` 605–736 | `kiem_tra.py`: `k8_nguon_kl`, `_lech`, `_nguon` | Dùng `doc_bang.tim_bang_chi_tiet` EX-4; bật theo tham số; Decimal; kiểm hủy; không chép nội dung exception vào phát hiện |
| `toan_ven.py` 737–762 | `kiem_tra.py`: `chay`, `_xep_lai` | Bổ sung K8 có điều kiện vào điều phối EX-2; giữ xếp mức/cột cây nguồn |
| `toan_ven.py` 764–866 | `bao_cao.py`: kiểu ô, `_sheet`, `ghi` | Giữ sheet, cột, màu, độ rộng, freeze panes; BytesIO; tiền có đơn vị/để trống; công thức dạng chuỗi; không ghi đĩa |

Dùng lại hàm `_tim_tien_te` sẵn có của EX-4 để nhận đơn vị rõ ràng, không tạo
mã nhận diện tiền tệ thứ hai. Báo cáo nhận bản sao bảng để định dạng không làm
đổi dữ liệu kiểm/JSON. Phần nối tải báo cáo trong `chay.py`, schema và test
là mã nội bộ theo phiếu §4.1/§5.1. Không sửa `doc_bang.py`, `bo_nhom.py`,
`excel.doc_bang@1`, mã nguồn tham chiếu hoặc SDK.

Khác nguồn: vượt đường truy nguồn 8 tầng từ chối `VUOT_GIOI_HAN` thay vì trả
`Khác` với đường bị dừng; ô báo cáo quá 32.767 ký tự từ chối thay vì để openpyxl
cắt ngầm. Thiếu bảng/cột KL vẫn là một phát hiện Kiểm soát K8, không coi là
đã kiểm đủ nguồn. Tiền K8 giữ cách `round` từng dòng của nguồn; Decimal tránh
mất chữ số của float. Không thêm dependency; kiểm kê SHA toàn gói thuộc EX-6.

## EX-6 — tổng hợp nguồn hiện hành và kiểm kê

Đường nguồn tính từ repo `review_xaydung` tại commit `1bed645ed56a36a59995afe1617af9dec83b8d82`;
bản chép chỉ đọc ở `e_kiem_excel/ma-nguon/`. Đường đích tính từ gốc gói.
SHA nguồn ở đầu tệp tính với LF đúng git; test chỉ đổi CRLF→LF trong RAM khi
đối chiếu bản tham chiếu trên Windows, không sửa nguồn.

| Nguồn cũ / dòng | Đích trong gói | Nội dung |
|---|---|---|
| `toan_ven.py` 42–50, 144–229 | `e_kiem_excel/tham_chieu.py` | Hằng, tách tham chiếu, mẫu công thức, so sánh |
| `toan_ven.py` 54–142 | `e_kiem_excel/so_do.py` | SoDo, hai workbook, nhãn/cột/ô gộp; nạp BytesIO |
| `toan_ven.py` 262–515 | `e_kiem_excel/kiem_tra.py` | KiemTra và K1–K6; Decimal, nhóm/tài liệu từ tham số |
| `toan_ven.py` 516–604 | `e_kiem_excel/kiem_tra.py` | K7; tham số ô đích và bộ nhóm module |
| `toan_ven.py` 605–736 | `e_kiem_excel/kiem_tra.py` | K8, _lech, _nguon; chỉ bật khi được yêu cầu |
| `toan_ven.py` 737–762 | `e_kiem_excel/kiem_tra.py` | chay, _xep_lai; điều phối và hủy |
| `toan_ven.py` 764–866 | `e_kiem_excel/bao_cao.py` | Kiểu ô, _sheet, ghi; báo cáo vào RAM |
| `master_hd.py` 43–72 | `e_kiem_excel/chuan_hoa.py` | nfc, bo_dau, so, num; Decimal hữu hạn |
| `master_hd.py` 629–728 | `e_kiem_excel/doc_bang.py` | _hdr_text, tim_bang_chi_tiet, khoa |
| `master_hd.py` 730–765 | `e_kiem_excel/doc_bang.py` | LABELS, tim_so_tong_hop; Decimal, giữ số nhỏ/0 |
| `master_hd.py` 741–765 | `e_kiem_excel/kiem_tra.py` | _tim_o_dich chuyển cách quét; nhãn nhận từ module |
| `toan_ven.py` 231–260 | Ngoài gói: fixture Phụ lục A | Không mang 7 nhóm nghiệp vụ viết cứng vào engine |
| `toan_ven.py` 1–41, 867–887 | Không chuyển | Import/CLI cũ thay bằng cổng SDK |
| `master_hd.py` 1–42, 74–627, 767–1234 | Không chuyển | Import/AI/hợp đồng/master/CLI cũ không thuộc engine |
| Phiếu §4.1.1 | `e_kiem_excel/bo_nhom.py` | Mã mới: kiểm bộ nhóm và matcher chung |
| Phiếu §4.2 | `e_kiem_excel/doc_tong_quat.py` | Mã mới: khuôn tổng quát, dùng chung matcher |
| API v1/SDK 2.2.0 và mẫu Hóa đơn đã ghim | `e_kiem_excel/chay.py`, `e_kiem_excel/__init__.py` | Mã nối SDK, kiểm hủy, trả tệp và bọc MIME |
| Phiếu §6 và thư viện chuẩn Python | `e_kiem_excel/nhan_dien.py` | Mã mới: chặn ZIP/XML/ô/vùng trước openpyxl |
| Phiếu/SDK và công cụ DEMO nội bộ | `engine.json`, `README.md`, `CHANGELOG.md`, `requirements.lock`, `NGUON.md`, `demo/*.xlsx` | Metadata, hướng dẫn, dependency và dữ liệu giả |

Rà lock EX-6: giữ đúng **openpyxl 3.1.5, et_xmlfile 2.0.0, defusedxml 0.7.1**.
`openpyxl.xml.functions` dùng `et_xmlfile.xmlfile` khi không có lxml;
`openpyxl.xml.DEFUSEDXML` phải là true trong tiến trình cô lập. Cài sạch
không có lxml/numpy/pandas. SDK cài riêng từ wheel nội bộ đã ghim, pytest
chỉ là công cụ test ngoài gói. Kiểm dependency sau cài dùng `pip check`, chỉ cho
phép thiếu đúng `cryptography`/`jsonschema` của **phần module SDK** theo hướng
dẫn cài wheel `--no-deps`; không cài hai gói này vào engine. Mọi lỗi khác làm
script thất bại; kiểm thêm phiên bản ba thư viện và cờ DEFUSEDXML.

EX-6 bổ sung lớp ghi worksheet vào BytesIO ở `bao_cao.py`, dựa trên
`openpyxl 3.1.5` (MIT), `openpyxl/writer/excel.py: ExcelWriter.write_worksheet`
và `openpyxl/worksheet/_writer.py: WorksheetWriter(out=...), read, close`.
`wb.save(BytesIO)` mặc định của thư viện vẫn tạo XML tạm; lớp con giữ dữ liệu
và quan hệ sheet nhưng đổi XML sang RAM, đóng stream trong finally. Test hồi
quy chặn `create_temporary_file`, mở lại đủ 15 sheet/K8. Phiên bản gói 0.1.1.

SHA dưới đây là **bytes nguyên trạng**, không chuẩn hóa khi kiểm; `.gitattributes`
đã khóa LF cho tệp chữ trong gói và binary cho XLSX. Không thể ghi SHA của
toàn bộ chính `NGUON.md` vào nội dung của nó. SHA nguyên trạng **mọi tệp, gồm
NGUON.md**, nằm ở `e_kiem_excel/tests/demo/bam-goi.json` ngoài gói và
`.dong-goi-thu/KIEM-KE-EX6.json` cạnh ZIP thử. Công cụ
`tests/kiem_bam_goi.py` kiểm đủ tập tên, số bytes và SHA, từ chối tệp thừa/thiếu.

Lệnh tái lập: `python -B e_kiem_excel/tests/kiem_bam_goi.py --cap-nhat --dong-goi-thu`.
ZIP thử gọi trực tiếp bộ kiểm/tạo ZIP của `_chung/cong-cu/dong_goi.py`,
đọc bytes worktree vì Codex không được commit. Sau khi lead commit, tạo bản
phát hành bằng CLI `python -B _chung/cong-cu/dong_goi.py --engine e_kiem_excel
--ref HEAD --nhan EX-6 --ra <thu_muc_moi_ngoai_repo>`; CLI chỉ đọc bytes đã
commit nên **không dùng CLI tại HEAD cũ để gọi đó là gói EX-6**.

<!-- BAT-DAU-SHA256-EX6 -->

| Tệp trong gói | Bytes | SHA-256 |
|---|---:|---|
| `CHANGELOG.md` | 3513 | `b58f09a60c517d454ce51b89f897a240ba0a6a2670e98e09b8a490b9e0ff3029` |
| `demo/bang-kl-DEMO.xlsx` | 4508 | `9e14f6142c32faedf1ca60a01f64a43cd3004b237cea27373ea2383d2f66d0ab` |
| `demo/bao-gia-DEMO.xlsx` | 2048 | `ac25a7b8e36cd0fa0e5c9e67f04d23c19afbde654c21d029beb83f66ec9cffb2` |
| `demo/gia-thanh-DEMO.xlsx` | 1811 | `010ffccbb70784a09fab3247a39e5c23425d335e9421fd50305216c16d6226bf` |
| `demo/K1-K8-DEMO.xlsx` | 4831 | `e6da3f0932bffe5e2451a2dcb65261d24682bc1b1cb937fb211af4f8809743cb` |
| `demo/sach-DEMO.xlsx` | 1438 | `20a53e89a4a5cb22e58879b4fa7b82a2e47e24f9914944ee3c4d831c7851da6b` |
| `e_kiem_excel/__init__.py` | 73 | `263ee64fdff5df021cfd6a2fcf0788675b784c3aa86cc7982914690a1d51c4b1` |
| `e_kiem_excel/bao_cao.py` | 12602 | `735ae0dafabace05c7aab838de0c4d21e907d85185524b9870a222fab4c422e6` |
| `e_kiem_excel/bo_nhom.py` | 5910 | `63ed37b33c4c2663e8aa90d0cd19643bcda3e5ef25cad21ea9b9ebabe22fcd0e` |
| `e_kiem_excel/chay.py` | 4372 | `10eeb3c7d53f28f8d2a0b4b877daf2470165072b50ba69d17765decd39c7c9a2` |
| `e_kiem_excel/chuan_hoa.py` | 1459 | `808cf278993e87c6b019567bb77907bf45b642b2ff717144aadb26b0529b0bf8` |
| `e_kiem_excel/doc_bang.py` | 13973 | `040db8dcf22494b52f897f0ef833fae735d6c7545d487b533be21f98cb7f64f2` |
| `e_kiem_excel/doc_tong_quat.py` | 8997 | `3375d048ed6be7662f91157c44de28111e8ca58324dd6816be4bd801a94b1ca1` |
| `e_kiem_excel/kiem_tra.py` | 40753 | `bcea7d28bb6abd008df98b886d8fb5aa900b794975ae3da4dc6b6cf4e550cd0f` |
| `e_kiem_excel/nhan_dien.py` | 6696 | `9365db7e0b5094b7defa4761a00d621fe119a53c0db5a90d2f69d201c2abb6a7` |
| `e_kiem_excel/so_do.py` | 4802 | `5be9894b22ff44c1ac3b55f8230b0aaf2f0e25f8d5381839c504fe7a801ba25b` |
| `e_kiem_excel/tham_chieu.py` | 3712 | `820b34509482de02dde7fe3f2643ad0ee3afa09c17832ee03ddaf3755f19f19f` |
| `engine.json` | 8885 | `ccdfe2e252dd94f97425773fdfeab705aa29dce38248674f80f97bb316a410d3` |
| `README.md` | 5951 | `1fe66edd93ac09749fca4de59eb57f57461c72c363b86de894ae48e5497258ff` |
| `requirements.lock` | 631 | `d82a377d03f0489bbfaccaa739373b000b45dd519b749a585edec90874dc99ec` |

<!-- KET-THUC-SHA256-EX6 -->
