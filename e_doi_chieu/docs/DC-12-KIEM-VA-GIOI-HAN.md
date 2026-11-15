# DC-12 — kiểm toàn tuyến DEMO và giới hạn, 15/11/2026

PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia). Chỉ DEMO,
0 lượt Cloud/OCR/AI thật; không commit/push. Runtime, manifest và phiên
bản gói 0.9.0 giữ nguyên. Không phát hiện lỗi lớn cần mở lát runtime mới.

## Cách chạy và phạm vi bằng chứng

Chạy tại gốc repo, bằng venv Python 3.11 trở lên có SDK 2.2.0/Pillow
12.3.0 và công cụ test đã ghim. Đặt `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` trước khi chạy:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_doi_chieu/goi/e_doi_chieu
.venv/Scripts/python -m pytest e_doi_chieu/tests -q
.venv/Scripts/python e_doi_chieu/tests/kiem_doc_lap.py
.venv/Scripts/python e_doi_chieu/tests/chay_demo_voi_core_gia.py
node --test e_doi_chieu/tests/ui/*.test.mjs
```

CLI SDK chuẩn: **1/1 DOCX DEMO sạch**, không cần máy AI, ngăn cấu hình
hay adapter riêng. Đây là độ phủ của `chay_thu_demo`, không phải DEMO
toàn nghiệp vụ. Không khai ID tệp con chưa tải hoặc cờ DEMO trong runtime.

Harness: **10 ca chuỗi** = 8 ca có đáp án độc lập + 1 ca quét ảnh có
vết + 1 ca OCR lại đủ căn cứ giả. Có đường đủ cả 7 năng lực của engine:
đọc DOCX qua SDK → tệp JSON cặp → nhận cặp → so → quét ảnh → yêu cầu AI
→ Core/Local giả → trả lời AI → hậu kiểm → trường/JSON/PDF. Mỗi tệp đã
thật sự nạp vào kho RAM CoreGia qua `them_tep`/`tai_tep_ra` trước khi dùng.
Không sửa snapshot để giả kết quả của đường toàn chuỗi.

CoreGia điều phối 7 lượt Local giả trong 10 ca. Ca chỉ có quy tắc quyết
định thì dùng nhánh không AI, không tạo trả lời giả để ghép chuỗi. OCR
và metadata ảnh/tọa độ là fixture tổng hợp, không phải nguồn máy thật.
Ngăn trên chuỗi là `viec.ngan` SDK 2.2.0; mẫu `NganBoNho` nguyên bản
chỉ được nạp/kiểm riêng trong harness, không thay cổng runtime.

| Nhóm kiểm | Bằng chứng / giới hạn |
|---|---|
| Đủ/sai dẫn chứng Local | Tệp cặp đến báo cáo cuối; câu bịa không được chấp nhận, giữ Cần xem/chưa kiểm đủ |
| Năm kết luận | Ma trận quyết định DC-9; upstream đo/duyệt giả, không tính là phép đo chất lượng toàn tuyến |
| Thiếu detector/ảnh/tọa độ | Gọi capability quét qua CoreGia; lỗi rõ, không có kết quả sạch |
| Hủy/mất lease | Ba bước chuẩn bị AI/hậu kiểm/xuất; không nộp kết quả; mất lease không báo kết thúc |
| Mất ACK/CAS/chống trùng | Lỗi ở tệp/ngăn/kết quả/kết thúc, gửi lại không nhân đôi lượt/báo cáo |
| Quyền giả/snapshot tự băm | Khác pháp nhân, mất quyền và sửa rồi băm lại bị từ chối |
| Xác nhận/học OCR | DC-10/11: hai người, CAS nguyên tử, chỉ thêm, duyệt/Q14 giả; chưa kiểm nhật ký bền |
| Lỗi nguồn | Bắt trực tiếp `LoiNghiepVu` và kết quả CoreGia cho `DC_SAI_NGUON`, `DC_QUA_GIOI_HAN`, `CHUA_CAU_HINH`, `DC_OCR_KHONG_DOC_DUOC` |
| HTTP loopback | Tiến trình Python mới, `app.chay()` đọc một dòng stdin; MayChuGia phục vụ tải DOCX/nộp/kết thúc, có xác thực và khóa chống trùng; không vá SDK |
| Không lưu máy | Chặn mở tệp ghi, chương trình ngoài/mạng trong test toàn chuỗi; cấu hình/ngăn và tệp gốc/snapshot/báo cáo chỉ qua CoreGia/RAM |
| Schema/mẫu | So băm LF cả ba schema chung, schema hồ sơ và hai mẫu NGAN-0; nguồn/bản chép giữ nguyên |
| UI | KttCore/DOM giả trên Node; chưa xác nhận thao tác trên trình duyệt Core thật |

## Đáp án và mẫu số

Nguồn: `tests/fixtures/DEMO-dap-an-dc12.json`, tự soạn từ văn bản giả;
đáp án khai quy tắc kỳ vọng độc lập với kết quả máy. Một ca cài một thay
đổi nghiệp vụ đã biết; một thay đổi có thể sinh nhiều điểm edit script.

| Chỉ tiêu trong bộ văn bản giả | Số đếm |
|---|---:|
| Thay đổi Nghiêm trọng bắt được / đã cài | **5/5** |
| Sửa thật bị ẩn thành nhiễu / sửa thật đã cài | **0/8** |
| Điểm máy được giữ lại trong JSON/PDF của 8 ca | **12** |
| Điểm máy Nghiêm trọng trong 8 ca | **7** |

Năm thay đổi Nghiêm trọng: tiền, ngày, thêm phủ định, xóa khoản/Điều,
đổi tên bên ký thuê/thuế. Ba sửa thật còn lại: thuê/thuế ngoài vùng bảo
vệ, màu xanh/đỏ, hợp/hộp. Local giả cố đề nghị `nhieu_ocr` nhưng không
ẩn được sửa thật. Kiểm toàn bộ điểm so chữ của năm ca nghiêm trọng giữ
mức Nghiêm trọng; điểm kiểm tiền nội bộ thiếu bằng chữ có thể giữ Cần xem.
Hai điểm kiểm nội bộ đó cũng được giữ trong 12 điểm, không tính thêm vào
mẫu số 8 sửa thật. Nhánh OCR lại giả có đáp án “nhiễu” được kiểm riêng,
không trộn vào mẫu số sửa thật. Không có skip ở bài đo này.

Các số trên không chứng minh accuracy trên tài liệu khác. Detector thật
vẫn có kết quả DC-8 trước đó TP=3, FP=0, FN=3 trên bộ raster riêng;
DC-12 không thay hay nâng kết quả đó. Bộ 10 ca không chứng minh recall
detector, chất lượng OCR/Local hoặc ngưỡng vận hành. Hồ sơ toàn chuỗi
thiếu đo vẫn là `chua_doi_chieu_duoc`, `da_kiem_du=false`, giữ chặn.

## Công cụ máy sạch, chỉ cài offline

```text
e_doi_chieu\cong-cu\KIEM-MAY-SACH.cmd
sh e_doi_chieu/cong-cu/kiem-may-sach.sh
```

Hai wrapper là ASCII, mặc định chạy khô. Truyền `--wheelhouse <thư mục
wheel đã cấp>`; `--cai` chỉ tạo venv mới khi đủ wheel đúng phiên bản,
SHA-256 và tag nền tảng. Không ghi đè venv có sẵn. Venv sạch không dùng
system-site-packages; pip `--isolated --no-index --no-deps --no-compile`.
SDK luôn lấy wheel repo riêng, so `SHA256SUMS.txt` và runtime lock. Không
tải mạng hoặc dò nguồn máy thật. Sau cài chạy CLI DEMO, pytest, harness,
Node và kiểm độc lập. `--chi-runtime` chỉ cài/kiểm runtime, không tính
pytest/UI/harness là đạt.

**Kết quả hiện tại: chưa kiểm máy sạch.** Wheel SDK có sẵn và băm đúng.
Repo không có wheel Pillow 12.3.0 đúng hai hash đã được phép (Windows x64
CPython 3.13 / Linux x86_64 CPython 3.13); 12 gói test/QA đã ghim phiên
bản nhưng chưa có wheel/hash được cấp. Công cụ từ chối mã 2, không tạo
venv hay tự tải. Cần lead cấp wheel/hash đúng phiên bản đang khóa; không
suy hash wheel từ bản đã cài. Nguồn/giấy phép/băm metadata bản đã cài ở
NGUON.md chỉ phục vụ kiểm kê, không thay hash wheel để cài máy sạch.

Môi trường chạy kiểm lần này: Windows x64, Python 3.13.14, venv riêng
`--system-site-packages` để dùng đúng Pillow 12.3.0/pytest 9.1.1 có sẵn,
SDK 2.2.0 cài offline từ repo; Node 24.18.0. Đây không phải kết quả cài
máy sạch. `.cmd` đã chạy khô trên Windows; `.sh` mới kiểm nội dung ASCII,
chưa chạy Linux. Không có tuyên bố đã kiểm Linux.

## Chưa kiểm / Cần Core và lead

- C-DC-01/02: ngăn bền/RLS/lease thực, ghép cặp/quyền tệp con và vòng đời
  tệp xuyên bước; điều phối Local/OCR vùng và nhánh không AI trên Core thật.
- C-DC-03/04: danh tính/quyền/xác nhận chỉ-thêm, hai người, nhật ký bền,
  CAS thật và mapping chặn/mở hiệu lực, thông báo của module.
- C-DC-05/07: provenance OCR vùng/phân trang/ảnh/tọa độ và chuyển tiếp
  Hỏi AI thật. Chỉ adapter giả trong tests, không đưa vào runtime.
- C-DC-06: nợ SDK về log ngoài handler, lease/trần sâu; DC-12 không vá SDK.
- L-DC-01/Q14/Q15/DC-13: wheel/hash offline, từ điển có giấy phép/duyệt,
  ngưỡng được đo/duyệt, detector/scan/model thật. Anh tự chạy phép đo thật.
- Trình duyệt Core thật và kết quả vận hành thật: chưa kiểm. Không có
  câu Chờ Anh mới; các quyết định đã duyệt chiều 15/11 tiếp tục áp dụng.

## Băm bằng chứng DC-12

SHA-256 LF cho văn bản; JSON số đo chỉ có dữ liệu DEMO/đếm, không ID tệp hay khóa.

| Tệp tương đối engine | SHA-256 LF |
|---|---|
| `tests/chay_demo_voi_core_gia.py` | `a47bca0acb9ee2c5e49b2289a3f822bbd61abcb22ff00fe56f4386a77fda3a50` |
| `tests/test_dc12.py` | `34ad72ab3f75600511fd1ce16917489d366fd2cd740d8d9c10ced3ba6179df7e` |
| `tests/fixtures/DEMO-dap-an-dc12.json` | `d0aadc510999e07edacd89b41fc1a6b8c25b1a62bc512cd8bb99b872ebe9ad0a` |
| `cong-cu/kiem_may_sach.py` | `9389a13a1beef6bc720449bf1cc40fda7d6c3294b774da5c25e461e4ffd3e99d` |
| `cong-cu/KIEM-MAY-SACH.cmd` | `1fa542b9e5dd64e887d14b371236f65a39b91850ea7d49d5f0729c4de8f48df6` |
| `cong-cu/kiem-may-sach.sh` | `19ffca631f52be5fea67abb1f11670bf8ee18bc4373833820fca4c86d7684936` |
| `docs/DC-12-SO-DO-DEMO.json` | `95c4c7da6f57c8de97a61dccce1e261f5ce4334d59590401ce0b4b9cd86a368b` |

## Kết quả kiểm cuối

CLI SDK **1/1 ĐẠT**; pytest **1090 passed, 0 skipped** trong **235.12 giây**
(gồm **33 ca DC-12**); kiểm độc lập mã **0**; harness **10/10 ca chuỗi**
và **4/4 lỗi nguồn**; Node **29/29**, 0 skip. Các lệnh kiểm engine/harness/UI
đều mã 0. Wrapper CMD chạy khô mã **2** vì thiếu wheel/hash đúng thiết kế,
không tính là đã kiểm máy sạch. Gói kiểm kê **46 tệp** khớp bytes/SHA-256.

Thời gian thực tế: **22:18–22:39:25 ngày 15/11/2026 (UTC+7), khoảng 0.36 giờ**, so với **3 giờ ƯỚC TÍNH**.
