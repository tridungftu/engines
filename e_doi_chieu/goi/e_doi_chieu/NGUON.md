# Nguồn của gói Đối chiếu

## DC-8 — 15/11/2026 · 0.4.8 chưa phát hành

- `anh.py`, `sua_tay.py` viết mới trong lát DC-8; `chay.py` chỉ thêm khối
  đăng ký DC-8 riêng. Tái dùng kiểm snapshot/băm/quyền/giới hạn của `ho_so.py`
  trong cùng gói. Không sửa `quy_tac.py`, `tien_chu.py`, nguồn OCR hoặc
  `ma-nguon/`; không chép detector/model từ ngoài workspace.
- Dependency runtime bổ sung duy nhất: **Pillow 12.3.0**. Chép nguyên ba dòng
  phiên bản/hash từ `e_ocr/goi/e_ocr/requirements.lock` sang lock của engine;
  test so nguyên đoạn. SHA-256 wheel Windows x64 CPython 3.13:
  `0847a763afefb695bc912d7c131e7e0632d4edc1d8698f58ddabec8e46b8b6d3`;
  Linux x86_64 CPython 3.13:
  `1cca606cd25738df4ed873d5ad46bbdb3d83b5cbca291f6b4ff13a4df6b0bbe8`.
  Không chép các dependency PDF/OCR khác. Nguồn phân phối đã ghim theo lock
  OCR; dự án Pillow, giấy phép chính **MIT-CMU**, kiểm từ metadata/LICENSE
  của bản 12.3.0 có sẵn. Thư viện native đi kèm wheel có giấy phép riêng
  trong LICENSE của distribution; engine không vendor hay tải thêm chúng.
- Môi trường kiểm dùng Pillow 12.3.0 có sẵn qua venv system-site-packages;
  không có wheel Pillow trong repo để cài lại/hash wheel tại đây. Hai hash
  trên là nguồn pin của OCR, **không khẳng định đã kiểm wheel cài máy sạch**.
  Runtime từ chối phiên bản Pillow khác; kiểm máy sạch/offline bằng wheel
  đúng hash và kiểm Linux vẫn là phần cần lead thực hiện trước phát hành.
- `tests/demo_sua_tay.py` tự dựng raster và đáp án từ nội dung DEMO, nét
  polyline/ellipse bằng Pillow; chữ dùng `ImageFont.load_default(size=22)`
  đóng gói sẵn trong Pillow, không đọc font máy hoặc phân phối tệp TTF mới.
  Hộp OCR/nguồn loại trừ là fixture giả. Không có hồ sơ khách hàng, ảnh
  scanner/OCR thực hoặc nhãn do model tạo. Bộ 12 ca có 11 raster khác nhau.
- `cong-cu/do_sua_tay_demo.py` và `.cmd` viết mới, ngoài gói runtime; đo pixel
  thật và chấm file export DEMO của Core, không gọi AI/engine khác/mạng.
  Adapter CoreGia và detector giả chỉ trong tests, không được dùng tính
  accuracy. Báo cáo `DC-8-SO-DO-DEMO.json`: TP=3, FP=0, FN=3; Local vision
  chưa đo để null. Chi tiết giới hạn/phương pháp tại `docs/DC-8-KHAO-SAT.md`.
- Hai bản chép NGAN-0 và bốn schema giữ nguyên; test so SHA-256 LF tiếp tục
  chạy. API/SDK 2.0.0 không đổi; chỉ mở thêm năng lực vào manifest SDK 2.0.

SHA-256 hiện hành DC-8, bytes UTF-8 sau CRLF→LF; bảng các lát cũ bên dưới
là lịch sử. Đường tương đối từ thư mục gói, trừ mục có tiền tố `repo:`:

| Tệp | SHA-256 LF |
|---|---|
| `e_doi_chieu/anh.py` | `2358268bca79589385e904909ab32d5bdaa43d3ebf5097776698e91a0c5f7dbe` |
| `e_doi_chieu/sua_tay.py` | `29a63bdfa9306c748a6a6bc4808f85206dfc69e9f94d816c52c6a22d369528d0` |
| `e_doi_chieu/chay.py` | `e2dd667fd9f7d104d38daea9c0f6d5206344f0a65a77e26894fc9d69e303fda0` |
| `engine.json` | `98408586a788d3db1c79478a7e157fce3c9858a96cec6c1ebbd2e18d8db379ee` |
| `requirements.lock` | `7f3beb0824f3d20e086b4c3d27c9b84d65b456fe05a3232d042a804de06b3d07` |
| `repo: e_doi_chieu/cong-cu/do_sua_tay_demo.py` | `5e1dba3361a9136b9bd55031580de852385a57461cc6aa4ebc754895730713a1` |
| `repo: e_doi_chieu/cong-cu/DO-SUA-TAY-DEMO.cmd` | `4c75fafea6907dcdb989e8f6ed6f2ddbf7405afa81bc992be0a247008c63440c` |
| `repo: e_doi_chieu/tests/demo_sua_tay.py` | `557cd576de4f5966ab00fa0baefefaf075e98916bc6c2abe8e1b21019ea3d52f` |
| `repo: e_doi_chieu/docs/DC-8-SO-DO-DEMO.json` | `684e3ce25e28c37ae4135eb516b32ee7bb07fc15a9ec59064c29791a81d799f2` |

## DC-4 — 15/11/2026

`can_chinh.py`, `so_chu.py` viết mới trong lát DC-4; dùng cấu trúc/ánh xạ
DC-2/DC-3 của chính gói. Thuật toán LIS bằng `bisect`, so cụm nhỏ bằng
`difflib.SequenceMatcher` của Python, tắt autojunk; Unicode bằng
`unicodedata`. Không chép mã/thư viện/từ điển/font ngoài workspace,
không thêm dependency hoặc tải mạng. Ba tệp runtime của lát gồm thêm/sửa
`can_chinh.py`, `so_chu.py`, `chay.py`; manifest là metadata SDK 2.0.

Fixture PDF/PNG/Word trong test đều sinh bằng thư viện chuẩn từ nội dung
DEMO, không phải hồ sơ khách hàng hoặc phép đo OCR/render thật. Adapter
Core cấp tệp con và liên kết phân trang chỉ ở tests; runtime không có
cờ DEMO/bỏ quyền. Quy ước C-DC-05 đang chờ Core, ghi ở README/VIEC.

Băm hiện hành DC-4 dưới đây là SHA-256 UTF-8 sau CRLF→LF; các bảng DC-2/
DC-3 bên dưới là lịch sử của những lát đó. Mẫu NGAN-0 và schema giữ nguyên.

| Tệp trong gói | SHA-256 LF |
|---|---|
| `e_doi_chieu/can_chinh.py` | `39b084ae09adc8785051fbbb95238281b0f305e4a5370f5856c65263f0ada76e` |
| `e_doi_chieu/so_chu.py` | `c3e0661cae053cfba6bcee6b1be910d8ae3c465ab700620f57d7953bb64ad5b5` |
| `e_doi_chieu/chay.py` | `32a19143c20539cbc05831329571b7ba8e41931d8d1831df6e34c30683aaafb7` |
| `engine.json` | `8dcdce863ff77b726b8a2fc48b3ae8a4c6f0e84f43e0942c1469be3cdc9057e1` |

- SDK runtime: `kho_tri_thuc_sdk` 2.0.0, wheel nội bộ tại
  `docs/goi-gui-engine/sdk-2.0.0/`; API v1 giữ nguyên.
- `e_doi_chieu/ngan.py`, `cau_hinh.py`: chép nguyên mẫu NGAN-0 tại
  `_chung/mau-ma/`, test so SHA-256 sau chuẩn hóa CRLF→LF. Không sửa bản chép.
- Bốn schema dữ liệu: nguồn `_chung/contract/`, bản chép cùng thư mục phiếu,
  test so SHA-256 LF. Ba schema chung đã khóa giữ nguyên; schema
  `ho_so_doi_chieu` theo DC-P và DC-Q17 duyệt chiều 15/11/2026.
- DC-1 không chép thuật toán từ OCR/Trích xuất; chỉ khảo sát mã có sẵn trong
  workspace, dẫn nguồn tại `docs/DC-1-KHAO-SAT.md` của project engine.
- Chưa đưa từ điển, detector, model, font hoặc dependency ngoài SDK/thư viện
  chuẩn vào runtime. Nguồn/phiên bản/giấy phép/băm cần lead cấp ở lát sau.
- Công cụ kiểm: pytest 9.1.1 có sẵn qua venv system-site-packages; bộ kiểm
  tập con schema dùng thư viện chuẩn (từ DC-3 có ở runtime cho hai schema
  đã ghim, không phải triển khai đầy đủ JSON Schema). Không tải gói/mạng.

## DC-2 — 15/11/2026

Chuyển có sửa từ nguồn nội bộ đã được phép tái dùng theo phiếu DC-2:

| Nguồn tương đối từ repo | Đích tương đối trong gói | Phần chuyển và sửa |
|---|---|---|
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `e_doi_chieu/doc_docx.py` | Kiểm ZIP/XML và adapter bytes SDK; thay toàn bộ Accept All bằng từ chối sửa đổi/comment, quét mọi XML, kiểm quan hệ/kiểu phần; thêm kiểm EOF/CRC thật, đọc cả story phụ, không cảnh báo rồi bỏ nội dung |
| Cùng nguồn trên | `e_doi_chieu/cau_truc.py` | Numbering, đoạn/bảng lồng, ô trống/gộp, offset; kiểm nghiêm node/thuộc tính, không bỏ qua vùng lạ; không chuyển hàm Accept All |

Nguồn gốc của thuật toán TX-1 là `e_trich_xuat/ma-nguon/docx.py` và
`e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py`, theo NGUON.md của
Trích xuất. Không sửa các nguồn hoặc import engine khác. Không thêm
dependency/giấy phép bên thứ ba; SDK 2.0.0 và thư viện chuẩn Python.

SHA-256 dưới đây tính trên bytes UTF-8 đổi CRLF→LF cho mã nguồn, không đổi
nội dung khác. DOCX/wheel băm nguyên bytes:

| Nguồn | SHA-256 |
|---|---|
| `e_trich_xuat/goi/e_trich_xuat/e_trich_xuat/docx.py` | `4290748070f8d5a8deee8a051c9ccdb384b1cb3ee8780e833d2781e5f84f1653` |
| `e_trich_xuat/ma-nguon/docx.py` | `84b5662856ecf2742360077012377f913698a917e1fd4a4a08f87568e1af6a5b` |
| `e_trich_xuat/ma-nguon/vendor/review/doc_hop_dong.py` | `1a73354377cd5a13aaa9c45254756d54099796150c7ad798ef26cff5e86c556f` |
| SDK `kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892` |
| `demo/DEMO-ban-chot.docx` | `e086e49c1dfad0cdfc702ab141a9de6123cbd123e4c7110df975b673e194bcaa` |

DEMO tạo xác định bằng `tao_goi`/`table_demo` trong `e_doi_chieu/tests/test_dc2.py`;
nội dung hoàn toàn giả, không có nguồn tài liệu khách hàng. Test đối chiếu
bytes fixture với DEMO đóng gói, so nguyên văn/offset, không chỉ kiểm status.

## SHA-256 bản chuyển DC-2

Băm mã nguồn sau CRLF→LF; không gồm NGUON.md.

| Tệp trong gói | SHA-256 |
|---|---|
| `e_doi_chieu/doc_docx.py` | `7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945` |
| `e_doi_chieu/cau_truc.py` | `ddde14383f97bf5c1fa1a2161aed7db8f3ea1e36004c16350a2db52018c2d333` |
| `e_doi_chieu/chay.py` | `0544a6a7dae1cca5a0331383349d7d5c781500f6b1fd4bf8c63820b1aeaf4246` |

## DC-3 — 15/11/2026

- `ho_so.py`, `chuan_hoa.py`, `vi_tri.py`: viết trong lát này bằng thư viện
  chuẩn Python và SDK 2.0.0; tái dùng trực tiếp bộ đọc/kiểm ZIP của DC-2
  trong cùng gói. Không import/gọi engine khác, không thêm dependency.
- Test cặp dùng DOCX từ generator DEMO DC-2, PDF một trang có xref do test
  tạo và PNG grayscale thực do test dựng; OCR/phân quyền là adapter giả
  ghi rõ trong `tests/test_dc3.py`, không phân phối trong gói runtime.
- Test parser ảnh còn đọc hai tệp DEMO đã có của OCR:
  `e_ocr/goi/e_ocr/demo/DEMO-1-trang.jpg` và `DEMO-1-trang.png`.
  Chỉ dùng bytes fixture để kiểm PNG/JPEG; không chạy hoặc import OCR.
- Không cấp bộ quy tắc/từ điển/detector thật trong lát này. Bộ JSON DEMO
  chỉ kiểm hợp đồng ghim băm/cấu hình và phép chuẩn hóa, không thay phê duyệt
  nguồn nghiệp vụ. Chi tiết quy ước tại README; Cần Core tại VIEC.md.
- Băm `chay.py` ở bảng DC-2 là ảnh lịch sử của DC-2; tệp đã được mở rộng
  handler nhận cặp/lớp bọc lỗi an toàn trong DC-3. Hai bản chép NGAN-0 và
  bốn schema dữ liệu tiếp tục giữ nguyên, test so băm LF.

## DC-3 — sửa theo kiểm độc lập lead, 15/11/2026

Sửa trong worktree theo 6 điểm lead giao; không chép nguồn mới, không tải
mạng hoặc thêm dependency. Ba tệp runtime sửa: `ho_so.py`, `chuan_hoa.py`,
`chay.py`; `vi_tri.py` đã đọc/kiểm và giữ nguyên. Bổ sung hạn giữ vào schema
cấu hình/bản khai ngăn dự kiến, không đổi hợp đồng API v1/SDK 2.0 hoặc
`engine.json` 0.3.0 chưa phát hành. `_chung/**`, hai mẫu `ngan.py` và
`cau_hinh.py`, bốn schema dữ liệu tiếp tục nguyên bản, test so băm LF đạt.

Fixture hiệu năng sinh trong test: 60 trang, 100 dòng lề DEMO/trang, mỗi
dòng có nút khối và nút dòng (12.000 nút); không dữ liệu thật và không phải
số đo chất lượng OCR. Có test hủy ở lúc lập chỉ mục/duyệt/gom vùng bỏ.
Hai bảng chuẩn hóa dùng đủ 14 cặp cần phân biệt và 7 cặp bằng nhau theo
bộ ghim, kiểm lại sự khác biệt khi tắt từng quy tắc. Các ca lease/CAS/
phục hồi tệp vẫn dùng CoreGia, NganBoNho và adapter tệp con DEMO trong tests.

SHA-256 **hiện hành**, chuẩn hóa CRLF→LF trên bytes UTF-8, không đổi nội
dung khác; đường dẫn tương đối từ thư mục gói, trừ dòng test ghi từ repo:

| Tệp | SHA-256 LF |
|---|---|
| `e_doi_chieu/ho_so.py` | `f0360c89d29af6a655935f48350552e200c6227604d12e84a940d0a214830e88` |
| `e_doi_chieu/chuan_hoa.py` | `a427053b5465450e838c274589d7d4b91fa86f69817414854a16cce2028bfe1b` |
| `e_doi_chieu/vi_tri.py` (giữ nguyên) | `0efdfb41d3cc56e857ab74e49c8f8cbaa7f0d075267581f60ffb33232d148a97` |
| `e_doi_chieu/chay.py` | `77896e602d97029b07b8fd1f9cfcc235a012b77d3c6f729e796752a90c3d70e4` |
| `cau_hinh.schema.json` | `e9febae882011886023f8d5efb3d7465b4b22dcb15bcc543ae8238f11015916a` |
| `KHAI-SDK-2.1.json` | `bacf0508ef7fef6c4ce7565dddc7535df9b5604da86bddba2c98a592949a333e` |
| Repo: `e_doi_chieu/tests/test_dc3.py` | `55618c6e0cd46695719a71ca31e34d633213750e5e8a485157bfb60bc411e6ab` |
