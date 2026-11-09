# NGUON — e_hoa_don

Lịch sử chuyển nội bộ từ nhánh lat/g3-goi-21 (nền hop-nhat-20261023).
Các dòng “nguyên trạng” ghi mốc chuyển vị trí; thay đổi tiếp theo ở lát 22–25
và SHA hiện tại được ghi riêng bên dưới, không khẳng định mọi tệp còn nguyên byte từ lát 21:

| Đường gốc | Đích | Ghi chú |
|---|---|---|
| src/kho_tri_thuc/engines/e_hoa_don/bang_ke.cjs | engines/e_hoa_don/bang_ke.cjs | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoa_don/chay.py | engines/e_hoa_don/chay.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoa_don/doc.py | engines/e_hoa_don/doc.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoa_don/engine.json | engines/e_hoa_don/engine.json | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoa_don/phien.py | engines/e_hoa_don/phien.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoa_don/portal.cjs | engines/e_hoa_don/portal.cjs | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoa_don/tai.py | engines/e_hoa_don/tai.py | nguyên trạng |
| src/kho_tri_thuc/core/contract/ky_thuat.json (3 schema) | engines/e_hoa_don/contract/schemas.json | trích chung.v1, tham_chieu_tep.v1, hoa_don.v1; nội dung đồng nhất |
| src/kho_tri_thuc/nguon/hoa_don_xml.py | engines/e_hoa_don/lib/hoa_don_xml.py | chuyển G3-GOI-22; SHA gốc d8ef5593c740258cef117cdf14229dd351205f2efbf976d3c9a24843d85f1329 (CRLF; dạng LF 37a0fab378c25aa69686d80b1f4c541b1d3a95e7fe2943d96d4aa41139aec53e); SHA mới 00f7ca777b65f3434bd89efc8a618709531bcf3d143bf45dc5cb35245c2ca3af (CRLF; dạng LF 2a757150d69ef24d7369621b22f6c25895867005ca167655813c91700e600f2b); sửa 2 import sang SDK + giữ __module__ legacy 'kho_tri_thuc.nguon.hoa_don_xml' cho mọi lớp |
| src/kho_tri_thuc/ha_tang/engine_hoa_don.py (phần ánh xạ) | engines/e_hoa_don/lib/trang_thai.py | tách G3-GOI-23: hằng trạng thái, bảng ANH_XA_MA_DATAERROR_HOA_DON / ANH_XA_NGOAI_LE_HOA_DON, hàm _trang_thai_xml/_trang_thai_zip chép nguyên thân; TrangThaiEngine lấy từ SDK (không định nghĩa lại); SHA mới 66a24f1afe6a8771713c1ed1344e2f5b86f33aa4ce88f0952b037f068209b3f8 (LF); hash bằng chứng trước = sau |

SHA-256 nguồn Node của lát 25 và nguồn hiện tại đo ở lát 26 được ghi bên dưới.
Mã băm toàn gói phát hành còn chờ các điều kiện SDK/độc lập, không thay bằng SHA từng tệp.

## G3-GOI-25 — phần nguồn Node xuất bảng kê

**Quyền dùng theo CD-096 A1, 06/11/2026 13:52:** "phần mềm nội bộ, Anh xác nhận 06/11/2026, chỉ dùng nội bộ".

Nguồn gốc: `D:\Claude\Phan mem download hoa don`, gói **hoadon-downloader 1.0.0**.
Chỉ đọc nguồn khi đóng gói; không sửa/xóa tệp bên ngoài repo. Xác nhận A1 cũng áp dụng
cho `D:\GPT\OCR\mask_ocr` (local-mask-ocr 2.1.0), nhưng lát hóa đơn này không chép nguồn OCR.
Không tự đặt LICENSE mới; `package.json` của phần Node đóng gói có `private: true`.

Hai tệp mã nguồn cần cho xuất bảng kê/PDF là `src/build.js` và `config.js`.
`vendor/build.js` chỉ đổi `require('../config')` thành `require('./config')` cho đúng vị trí;
`vendor/config.js` giữ nguyên nội dung các hằng công khai của nguồn. Không đổi thuật toán,
không đưa dữ liệu hóa đơn, tài khoản, profile hoặc cấu hình triển khai vào gói.
`bang_ke.cjs` nạp nguồn tương đối với `__dirname` và kiểm cả hai tệp trước khi require.
`portal.cjs` chỉ bỏ đường dẫn máy phát triển trong chú thích; giữ seam DEMO, nguồn tải thật
vẫn `CHUA_KIEM`. Không chép/nạp `job.js`, `portal.js`, `server.js`, `.env` hoặc dotenv.

SHA-256 tính trên bytes UTF-8, không chuẩn hóa Unicode. Các nguồn gốc dưới đây dùng LF.
Git hiện có `core.autocrlf=true`, nên ghi riêng SHA của bản LF và bản CRLF để kiểm sau
checkout; loader chỉ chấp nhận đúng hai mã băm đã ghim cho từng tệp nguồn.

| Tệp trong gói | Nguồn gốc (tương đối từ thư mục nguồn trên) | Phiên bản | SHA-256 gốc | SHA-256 bản gói LF | SHA-256 bản gói CRLF |
|---|---|---|---|---|---|
| `vendor/build.js` | `src/build.js` | 1.0.0 | `ca7fe35cafe7c802d5ebe7506db9fd7a1294552d833569306f03b1a03976f209` | `5664548e0f08936e6b15536dc4ec23bd55a04417d6c66ef439362415a16ab3d5` | `6e7b23e937b40740817b94e629647f8080e089cf66f57cca9561ea9a0d9ab614` |
| `vendor/config.js` | `config.js` | 1.0.0 | `48cb8cb1b0253cd4a5110f1628150053a0372a00b3503f359a01849281f90b02` | `48cb8cb1b0253cd4a5110f1628150053a0372a00b3503f359a01849281f90b02` | `35c86b295812793e98dd0ed65b3b34f247b1b67cb318e0e2d7fded0f1a57c3df` |
| `package.json` | `package.json` (trích ba dependency đã ghim; bỏ scripts/server, thêm private) | 1.0.0 | `843ba6700bd366aa2ba75ccc3151a2cd624c9608b6dbfc9cfeeb22ea6add5809` | `653457b71454e7e9e60375b9228f23388255866569b700ce96c75b204e25160d` | `afa506011a502855f7e5da980d7e165ff4d7ccfb5efabda2526c018112fd37b6` |
| `package-lock.json` | `package-lock.json` (trích closure cần dùng, giữ metadata/integrity của từng entry) | lockfile v3, 1.0.0 | `b71b23c4d29601acfb382379adae0a1b2dd251dfa62fa9e7278b910c496c423c` | `a03edb1857cdecedfe0e76970b5abf528eb07cb28f9b1110fa5ae236a3a80850` | `5ff1388fc6f17987883e7be3323cf69e43bc65493d571f1cd15634a24e3fd9dc` |

Phụ thuộc trực tiếp giữ đúng bản trong lock nguồn: **exceljs 4.4.0**,
**fast-xml-parser 4.5.7**, **playwright 1.62.1**. Closure có 102 entry thư viện,
kể cả phụ thuộc tùy chọn `fsevents 2.3.2` chỉ dành cho Darwin; giữ nguyên version,
resolved, integrity và license metadata của các entry nguồn. Không đưa `express`,
`dotenv`, `adm-zip` vào gói. Không cài thêm thư viện, chạy postinstall hoặc tải browser.

Môi trường kiểm thuần: Node **v24.18.0**. Catalog `playwright-core 1.62.1`
ở nguồn ghi Chromium/Chromium headless shell **revision 1234**, bản **151.0.7922.34**;
đây là metadata phụ thuộc, chưa phải bằng chứng Chromium đã cài/chạy trong engine.
Các bài Excel dùng ExcelJS thật ghi/đọc XLSX trong RAM, parser strict Python thật;
Chromium giả. Bài `tests/nguon.cjs` nạp closure tại vị trí giả trong RAM, chặn mọi
đường đọc ngoài gói, mock cả ba thư viện và kiểm SHA khớp bảng này.
Chưa kiểm tải thuế/phiên Windows thật; ghim cuối và triển khai thuộc lát sau.
Không thay đổi SDK; wheel 1.4.1 vẫn chỉ là candidate theo kế hoạch §6.3.

## G3-GOI-26 — hồ sơ ghim nguồn, chưa ghim phát hành

Đo ngày **06/11/2026**, sau commit nguồn Node `64c41046` và helper phiên SDK
`0ff99c11`. Lát 26 chỉ sửa `NGUON.md`, `README.md`, `CHANGELOG.md` và thêm
`requirements.lock`; không sửa byte mã nguồn, vendor, manifest hoặc Node lock.
Quyền dùng và các SHA nguồn gốc/lát 25 ở trên giữ nguyên.

### Nguồn Python, adapter và dữ liệu phân phối hiện tại

Các bản LF/CRLF dưới đây tính trên UTF-8 không BOM, không chuẩn hóa Unicode.
Chỉ thay cặp xuống dòng để đo hai dạng checkout, không viết lại tệp nguồn.
Đây là hồ sơ SHA nguồn, không bổ sung cơ chế loader hoặc danh sách loại trừ hash.

| Tệp tương đối trong gói | SHA-256 bản LF | SHA-256 bản CRLF |
|---|---|---|
| `__init__.py` | `a9bb093f6afb43de99e33dddd8885750a067aee5a9b53b656c7ac806d18775b4` | `3b052b04250841c014fb7ead1d4e19a666773cff0414bfd6a17c0aa386fec51f` |
| `bang_ke.cjs` | `99dea0ecf2b991bca7107d2b179078585359a936ac187856bb89563d3cbb9445` | `9e88fa02e0d18ba816bb54a31eac6e79d1c3cc9f6c95d1d08b8ce232c4ea807f` |
| `chay.py` | `075d6e44b68bc8c2b2f9c21d6d46933d0d5f02f605d920debefb01c169d2c43d` | `968aebcc4fb99056aace95286df368549b515b8c133e5f3edd2502eec5ecde5a` |
| `doc.py` | `4ce7dcb5ec02a62c4bc762c2ffa8a52359cbb9bd65f9ad2bb8e7313a74bd0d8b` | `a66dea667d2690f790c42e7684548d4015299a4dcb86f318bd36854df59dd5a9` |
| `engine.json` | `737a9ce413a96b275c5fcf95a66c1bb7d67b6147d0e1750d5352ac100c65d9f7` | `35698bf97a2f3ed684e04b14ad8bf1f2314097df7260d0a6a5a42ed9b7fc8a20` |
| `phien.py` | `2026b4ad75ae681776334c2b1dc29c7b0c595b2ea6d8bf25cbb24a0c59e9e3f5` | `c4d76da687b0de5f1c2092b66fc95ec82a5916fedabdd52bdd44daa882c3c996` |
| `portal.cjs` | `c01183b0f4e11875105ed1c1bd1303b5ceb3e83d65b4131e95622343517c6675` | `1006bd8b0c7997d83ebbc63565679b5ae104daba2d854b606f31b52c41b1411e` |
| `tai.py` | `2de529a58dbd76e20e979aa2da7a4dd84f46e649dae798b40dee283b7559c285` | `c64fc0893d083c69af7fee0da061a5a521c4e36a919d19dabbd993c15dfda14b` |
| `contract/schemas.json` | `f6e8077b84c616e2722f1343fdf3cff9156987c5fea45725262742562db1245a` | `bdd408a044dc305ef0b387cbf3af81538806c9e2d8d3f239eb2a954f5a1ff314` |
| `contract/vi_du.json` | `48bade2452a17c11f2122608f97e2b18a1d4f6041a02998c541108b491c31716` | `78baffe2eff3e76c35c4551566774f8eaacbdfd6e9d1364fef57fca4d7c11dcd` |
| `lib/__init__.py` | `1fc87e9290eda4499af98c17dc3e4e096b715b5a518d87e2b61b03d6a042a4fe` | `2e0579e3514a37d48df5ab69101fe08cd47b68a5dc4c3c2826829997992f7507` |
| `lib/hoa_don_xml.py` | `2a757150d69ef24d7369621b22f6c25895867005ca167655813c91700e600f2b` | `00f7ca777b65f3434bd89efc8a618709531bcf3d143bf45dc5cb35245c2ca3af` |
| `lib/trang_thai.py` | `66a24f1afe6a8771713c1ed1344e2f5b86f33aa4ce88f0952b037f068209b3f8` | `d1cacb693a5b74c987605f08f9c8f2f89978cb4b8e4a1a6cb4ed73807f59ae82` |
| `tests/test_doc_lap.py` | `f78d6785ca05c8ce9f28ce563793b712334fad86ee606a37ad372c80da3518b8` | `925ff24563c9d58989825c4fe32ded8e76410346d203879a498b0075974b0911` |
| `tests/nguon.cjs` | `d3a0edcecb20956060af5ea9cb3a7285cf91a829ff91d205c2894f9ff87506db` | `c8688b4ff645bc7ae26ddc7c5015a92234204db97dad94e6efc7fe4c8b7485a5` |
| `pyproject.toml` | `9e21d1db801318b01aadb605cbbcaab334da097bb1d7077dbd85a32d0e465389` | `dc2f6fc898da5936bb682056649afc1be5f42039b609474c7c09d11bb154daa4` |

Reader giữ bridge `kho_tri_thuc.nguon.hoa_don_xml` và tên module legacy của các
lớp để hash bằng chứng không đổi. Ánh xạ dùng enum SDK cùng identity với adapter
cũ. Lát 24 chỉ đổi nơi lấy `_doc_dong`, `KetQuaKiem`, `text_id`; hai import
`nguon.trich6_host.env_con` và `core.kiem_tra_tien_trinh.kiem_tra_tien_trinh`
vẫn là ngoại lệ đã ghi trong test, chưa đạt closure chỉ-SDK.

### Phụ thuộc và giới hạn của bằng chứng

- Python đo regression **3.13.14**, Node **v24.18.0**. Reader dùng stdlib;
  SDK candidate có metadata `cryptography==49.0.0`, `jsonschema>=4.18,<5`,
  chưa phải exact closure được duyệt cho engine. Không lấy lock toàn ứng dụng.
- Node lock/integrity đã có ở lát 25; test `tests/nguon.cjs` kiểm đủ 102 entry,
  SHA nguồn/metadata và chặn nguồn bị đổi trước require. `tests/g3_hd_2b.cjs`
  kiểm ExcelJS thật trong RAM và PDF Chromium giả; không kiểm Chromium thật.
- `requirements.lock` chỉ là hồ sơ CHUA_KIEM, chưa có dòng cài đặt. Không ghim
  SDK 1.4.1, không ghi version SDK tương lai hoặc hash wheel chưa đo.
- `pyproject.toml` chưa cấu hình packages/package-data, dependencies còn rỗng.
  Test package trong repo hiện có kiểm tĩnh/identity với Core; không chứng minh
  cài wheel hoặc chạy độc lập ngoài repo bằng SDK wheel.
- Lead cần chốt SDK cuối ở G3-GOI-34, giao xử lý ngoại lệ import/build ngoài
  whitelist này, kiểm package độc lập G3-GOI-38 rồi mới khóa Python và tính
  `ma_bam_goi` theo cơ chế Core hiện có trên toàn gói (gồm docs/lock/tests/CJS).
  Không dùng bảng SHA này thay pin registry, không bỏ `__pycache__` khỏi hash.
- Windows Job/socket/profile/ACL, nguồn job/portal, Chromium thật và kiểm
  registry/quyền/phiên bản còn thuộc lead; trạng thái thật vẫn CHUA_KIEM.
  Quy trình kiểm thuần và quay về bản ghim tương thích: [README.md](README.md).
