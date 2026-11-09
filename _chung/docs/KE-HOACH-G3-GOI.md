# Kế hoạch G3-GOI — đóng gói năm engine

Ngày khảo sát: 05/11/2026. Nhánh `lat/g3-goi-kh`, HEAD `22b3447800164d4a672c90b5e5747d1b30282087`.

**Đề xuất:** giữ tên Python hiện có, chuyển vật lý sang `engines/<tên>/`, dùng shim package tại đường cũ; đóng gói `e_hoi_ai` làm mẫu. Có **40 lát dự kiến**, mỗi lát tối đa 3 tệp hiện hữu bị sửa nội dung; các lần di chuyển nguyên trạng và tệp mới được kê riêng. Đây là kế hoạch để lead khóa whitelist, chưa phải lệnh thực hiện code.

**Cập nhật CD-098 ngày 06/11/2026:** nhận sáu việc chung **chuyển từ phiếu e_hoi_ai theo CD-098** tại §6.6; lát 1 tách 1a xác minh / 1b nối thêm khi thiếu, các mã 34/13c/38/39/40 tái dùng hàng hiện có, không giao hoặc cộng giờ trùng. Phiếu AI bản 1 chỉ Local, 0 lượt Cloud, 4 lát / 8 giờ chưa gồm phụ thuộc chung. Bảng 40 lát và khảo sát ban đầu dưới đây được giữ làm căn cứ kỹ thuật; phần chuyển theo quyết định mới được ghi riêng, không tự coi đã triển khai. **Không đổi/ghim SDK trong lần sửa tài liệu này; điều kiện candidate/alias tại §6.3 vẫn giữ, bổ sung trạng thái phát hành CRM bên dưới.**

**Thay theo CD-111 ngày 07/11/2026:** 1b-01 **DUYỆT (Anh 21:31)**; 1b-06 **KHÔNG làm đường riêng**, bỏ 1b-07/08 dạng gọi AI giữa chừng. Việc cần AI nối bằng chuỗi Core theo CD-110; hàng 34 **tách engine trích thành các bước chuỗi (chuẩn bị / hậu kiểm), không còn import CongAI trong engine trích**. Căn cứ CD-111 từ handoff DOC-CD111, bản chỉ đạo trong worktree chưa có mục này. SDK **1.5.0 đã phát hành cho CRM** theo QD-TAM-20261107-11 / TRANG-THAI 21:25; engine giữ bản SDK đang ghim, **wheel 1.4.1 vẫn chỉ candidate**. Hướng façade/operation riêng dưới đây chỉ giữ lịch sử có gạch/ghi chú; DOC-CD111 không triển khai mã hoặc đổi version.

**Cập nhật CD-100 ngày 06/11/2026:** [phiếu OCR](PHIEU-ENGINE-e_ocr.md) còn **7 lát / 22 giờ công — ước tính mới**, ngoài nền G3-GOI-17/18/19 **ĐÃ GỘP hôm nay**. Giữ 1/17, 2/18, 3/19, 6/20, 9/OCR-WIN-NT; thêm OCR-NOI/CHON/KETNOI/VUNG/MAY; bỏ lát 11 và VietOCR/dual/màn duyệt điểm khác nhau. Lát 4/5/7/8/10/12 và bài CRM 60 phút **chuyển từ phiếu e_ocr theo CD-100** sang [phiếu nghiệm thu tổng thể](PHIEU-NGHIEM-THU-TONG-THE.md), làm sau, **không chặn OCR xong**. **Mọi ước giờ cũ của phiếu OCR hết hiệu lực**; §6.7 dẫn chiếu dự toán mới và tránh cộng trùng phần chung CD-098. Lát 20 làm theo **khung SDK đã gộp, không chờ SDK cuối**; giữ nguyên giới hạn wheel 1.4.1 candidate ở §6.3. Khi khác với khảo sát cũ bên dưới, áp dụng CD-100 và [quyết định gốc e_ocr](QUYET-DINH-CUOI-e_ocr.md), văn bản gốc thắng.

Không thể nghiệm thu chỉ bằng chuyển 30 tệp: phải tháo các phụ thuộc ngoài SDK, kiểm package độc lập và nối discovery vào registry/runtime hiện có. Đặc biệt, **Mask chưa đủ điều kiện có manifest hợp lệ**; yêu cầu năm manifest cuối kỳ và nguyên tắc không công bố capability chưa kiểm phải được giải quyết bằng gate Mask, không tạo manifest rỗng.

Chọn AI làm mẫu vì đây là engine có manifest/contract/test, lõi chủ yếu stdlib, không nhập module nghiệp vụ, không cần ABBYY hay nguồn Node bên ngoài cho ca mẫu. Mask ít tệp hơn nhưng thiếu capability/manifest và seam khóa; hóa đơn còn reader/Node/Core checker, OCR còn parser ngoài, trích phụ thuộc M4. Đây là đánh giá rủi ro đóng gói từ mã, không phải khẳng định AI đã được nghiệm thu vận hành.

## 1. Căn cứ, phạm vi và độ chắc chắn

- `docs/46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md:484–492`: CD-042 chốt vị trí, nội dung gói, không import chéo, Manager đọc manifest.
- Cùng tệp, CD-058: UI song song, fixture phải ghi “Dữ liệu giả”, mỗi mốc có ảnh và đường mở DEMO.
- **CD-070 mục 1: căn cứ trực tiếp từ handoff của Anh.** Bản chỉ đạo tại HEAD này kết thúc ở CD-063; chưa có nội dung CD-070 để trích dẫn hoặc suy thêm quyết định. Lead đối chiếu bản mới trước khi giao code.
- `docs/47-core/g2/KE-HOACH-LAT-G2-G3.md:215–239`: không có capability đã kiểm thì chưa tạo manifest; G3-GOI chuyển các engine một lần sau G2. §CD-045: quản trị gói và cấu hình engine.
- `docs/47-core/g2/KE-HOACH-NOI-SDK-G2-32.md` §3, §4.2, §5.4–5.5: tái dùng E1/E2/E3/P1, gate OCR/TRICH-4b/READY, UI kèm theo. Đây là kế hoạch cũ; các nhận xét “chưa có tại HEAD” trong tài liệu đó không thay kết quả đọc mã hiện tại.
- `docs/47-core/chuan/CHUAN-CORE-SDK-v1.0.md`: mục Thay đổi v1.1 đã ghi CD-042; §3.8–3.10, §6 quy định manifest, vận hành, contract, KT. Bản hiện tại có thay đổi v1.3; **không ghi đè/lùi về v1.1**.
- `src/kho_tri_thuc/core/contract/{manifest,ky_thuat}.json`: nguồn schema thực thi hiện có. Manifest engine kín, `capability.minItems=1`; không có trường tùy ý `trang_thai=cho` hoặc capability giả.
- `CLAUDE.md` §4 và `docs/46-chuyen-doi-dieu-phoi/NEN-TEST.md` §0: ≤3 tệp sửa, khóa tệp chung, so nền v4 theo ID lỗi/skip. Khi giao từng lát, lead xác nhận nền đang áp dụng; không tự đổi nền theo một dòng trạng thái ở tài liệu khác.

Khảo sát bằng đọc UTF-8 và tìm chuỗi/import trong `src`, `tests`, `tools`; đọc metadata/lock nguồn OCR, Mask, hóa đơn. Không import/chạy các nguồn đó, không gọi mạng/AI/thuế/Junsky/Word COM, không chạy test, PostgreSQL hoặc server. `rg` và `python` không có trong PATH phiên khảo sát; dùng PowerShell và Git đọc nội dung. Không đọc `.env`, `cau_hinh.that.toml`, vùng dữ liệu thật.

## 2. Kiểm kê hiện trạng

Quy ước `E = src/kho_tri_thuc/engines`, `C = src/kho_tri_thuc/core`, `S = src/kho_tri_thuc/sdk_core`, `T = tests`. Cả `E/__init__.py` và `engines/` gốc **chưa tồn tại**. Năm thư mục có **30 tệp tracked: 23 Python, 2 CJS, 4 manifest, 1 contract dự thảo**; chưa có README/CHANGELOG/NGUON/lock/tests riêng bên trong.

### 2.1. Danh sách đầy đủ tệp cần chuyển

| Engine | Tệp hiện có, đường dẫn tương đối dưới `E/<tên>/` | Manifest / contract |
|---|---|---|
| `e_hoi_ai` | `bi_mat.py`, `chay.py`, `dto.py`, `hoi.py`, `nhat_ky.py`, `engine.json` | Manifest `ai.hoi@1`, vào `hoi_ai.v1`, ra `tra_loi_ai.v1`; chưa có `contract/` tại engine. |
| `e_ocr` | `abbyy.py`, `bang.py`, `ban_giao.py`, `chay.py`, `van_ban.py`, `engine.json` | Manifest chỉ `ocr.trich_van_ban@1`: `tham_chieu_tep.v1` → `van_ban_tai_lieu.v1`; `bang.py` có adapter nhưng chưa được manifest quảng bá. Chưa có `contract/`. |
| `e_hoa_don` | `bang_ke.cjs`, `chay.py`, `doc.py`, `phien.py`, `portal.cjs`, `tai.py`, `engine.json` | Manifest chỉ `hoa_don.doc_xml@1`: `tham_chieu_tep.v1` → `hoa_don.v1`; ZIP/bảng kê/tải không tự thành capability đã kiểm. Chưa có `contract/`. |
| `e_mask` | `chay.py`, `vong_doi.py`, `contract/du_thao.json` | **Không có `engine.json`**. Bốn schema HTTP dự thảo, `dang_ky=false`, `kich_hoat=false`, namespace `urn:ktt:du-thao`; không dùng làm contract Core đã duyệt. |
| `e_trich_xuat` | `ai_chung.py`, `chay.py`, `docx.py`, `do_chinh_xac.py`, `quy_trinh.py`, `tham_so.py`, `tich_hop.py`, `engine.json` | `trich.tham_so_hop_dong@1`: `tham_chieu_tep.v1` → `tham_so.v1`. Entry hiện là `kho_tri_thuc.engines.e_trich_xuat.tich_hop.chay_noi`; tên manifest ghi chờ TRICH-4b. Chưa có `contract/`. |

Bốn manifest hiện cùng phiên bản `0.1.0-demo.1`. OCR khai `headless=false`, ngoại lệ `CD-038-ENGINE-3A`; ba manifest kia `headless=true`. Tệp manifest tồn tại không chứng minh engine đang chạy hoặc được phép công bố ready; AI và trích còn các đường báo `contracts=[]`.

### 2.2. Import đi ra và phụ thuộc tải động

Chưa thấy Python import trực tiếp **engine → engine khác** trong 23 tệp; tên `e_ocr` ở phần trích chủ yếu là thông báo/chú thích. Tuy nhiên, các cạnh đi qua thư viện dùng chung vẫn làm gói không độc lập:

| Engine | Import ngoài thư mục, vị trí bằng chứng | Phải xử lý trước gate độc lập |
|---|---|---|
| AI | `bi_mat.py:14–16`: SDK + `tri_thuc.cong_ai`; `dto.py:9`, `hoi.py:10`, `nhat_ky.py:24`: DTO/cổng/bộ ghi từ `tri_thuc.cong_ai`; `chay.py`: SDK. | `tri_thuc/cong_ai.py` dùng `tri_thuc/ai_cuc_bo.py`; cổng có cả `BoGhiPostgres`, lớp đọc khóa tệp và provider Cloud. Tách phần DB ở phía Core; engine chỉ nhận bí mật RAM và ghi nhật ký qua SDK. Không sao chép cổng AI vào trích. |
| OCR | `abbyy.py:25`, `ban_giao.py:26`: `ha_tang.cong_ocr`; `bang.py:33`, `van_ban.py:32`, `ban_giao.py:27`: `ha_tang.primitives`; runtime dùng SDK. | `bang._nhap_parser_nguon` và `van_ban._nhap_parser_nguon`: thêm nguồn từ `KTT_NGUON_OCR`/`D:/GPT/OCR` vào `sys.path`, import `mask_ocr.extraction/layout`. Phải mang closure parser vào gói hoặc wheel nguồn ghim nằm trong gói; không dựa máy có sẵn thư mục nguồn. ABBYY executable/Hot Folder là phụ thuộc triển khai có cấu hình, không chép license/mô hình/dữ liệu thật. |
| Hóa đơn | `doc.py:24–29`: `ha_tang.engine`, `ha_tang.engine_hoa_don`, `ha_tang.primitives`, `nguon.hoa_don_xml`; `tai.py:26–27`: primitives + DTO reader; `chay.py:23`: `nguon.trich6_host.{_doc_dong,env_con}`; `phien.py:19–21`: `core.kiem_tra_goi.KetQuaKiem`, `core.kiem_tra_tien_trinh`, primitives. | Reader còn lazy import `nguon.fixture.Issue` trong phép chuyển tương thích; không mang cả fixture/config nghiệp vụ vào engine. `bang_ke.cjs:16–35` đọc SHA và `require` `D:/Claude/Phan mem download hoa don/src/build.js`; chưa tự đủ. `portal.cjs` là seam DEMO, nguồn thật `CHUA_KIEM`, chưa được phép tự nạp job/portal thật. |
| Mask | `chay.py:20–24`: `nguon.trich6_host.env_con`, **Core launcher** `core.khoi_chay_tai_khoan.{BoKhoiChayTaiKhoan,LoiKhoiChayTaiKhoan}`, SDK; `vong_doi.py`: nội bộ + SDK. | Phụ thuộc `thu_muc_mask/run_privacy.py` bên ngoài. Không chép nguyên nguồn có kho bí mật. Cần gói nguồn sạch/phiên bản ghim hoặc bộ cài phụ thuộc đã kiểm, giao diện launcher SDK; tạo tài khoản/ACL do lead. Nguồn chưa có bằng chứng cấp khóa stdin/handle thì mặc định chặn trước spawn. |
| Trích | `docx.py:17`: `m4.review_goc.trich_xuat.doc_hop_dong`; `tham_so.py:19–21`: `danh_muc`, **quy_trinh nguồn**, `kiem_tra`; `quy_trinh.py`: `cau_truc`, `kiem_tra`, `logic`, lazy `xuat`; `tich_hop.py`: `xlsx_mini`, `cau_truc`, `kiem_tra`, `logic`, lazy `xuat`; `do_chinh_xac.py`: `kiem_tra`, `danh_muc`; `ai_chung.py:13`: `tri_thuc.cong_ai`. | Cấm phụ thuộc module M4 ở đích. Closure cần `doc_hop_dong`, `cau_truc`, `kiem_tra`, `logic`, `xlsx_mini`, `xuat`, `danh_muc/cau_hinh` và catalog XLSX; không chép cả module. Đường `tham_so → quy_trinh` còn kéo `ai_local`, `cloud`, lazy `ocr_abbyy/ai_cloud`; phải bọc lại bằng pipeline đã nối cổng, không vendor các client này để lách kiểm. |

SDK cũng có ranh giới cần hiểu: `S/engine.py:11` import `core.viec.GiuViec`; wheel hiện do `tools/dong_goi_sdk.py` dựng với tên import **`kho_tri_thuc_sdk`**, chuyển client Core sang `_core`. Engine đang dùng **`kho_tri_thuc.sdk_core`**. Không thể chỉ đổi import hàng loạt: `SDKEngine`, `GiuViec`, `KenhCore`, `MaBiMat` có kiểm kiểu/danh tính. Phải chứng minh tương thích trước khi coi engine tách ra chạy độc lập.

### 2.3. Ai đang dùng engine / bề mặt regression

Tìm toàn bộ `src`, `tests`, `tools` theo năm tên, rồi phân biệt import với chuỗi/chú thích. **Không tìm thấy static import trực tiếp `kho_tri_thuc.engines.*` từ mã production ngoài `E`** trong phạm vi này. Core nhận runtime qua provider/pins, không import trực tiếp năm module ở đây. Các đối tượng consumer đáng giữ:

| Engine | Test trực tiếp import engine hoặc kiểm manifest/nguồn | Consumer khác và test gián tiếp |
|---|---|---|
| AI | `test_g3_ai_1a`, `1b`, `2`, `4a`, `4b`, `5a`, `5b`; `test_bm_kenh` | `tri_thuc.cong_ai` được dùng bởi `ha_tang/engine_cong.py`, `m9/hoi_dap_vay.py`, `m4/review_goc/trich_xuat/{cloud,ai_cloud}.py` và engine trích. `tri_thuc.ai_cuc_bo` còn dùng ở `de_xuat/engine.py`, `giao_dien/operations.py`. Regression: `test_cong_ai`, `test_cong_ai_nhat_ky`, `test_ai0_khoa_cloud`, `test_ai1_local_ai_lan`, `test_ai4a_kiem_xac_suat`, `test_xs3_cong`, `test_v11`, các `test_m9_*hoi_dap*`, `test_m9_so_du_snapshot`. |
| OCR | `test_g3_ocr_2`, `3`, `4a`, `4b`, `5a`, `5b` | Consumer cũ của `ha_tang.cong_ocr` phải giữ shim; regression `test_cong_ocr`, `test_m9_ocr_hot_folder`. `test_g2_32a`, `test_g2_33`, UI và công cụ tài khoản dùng mã engine/khai báo, không phải import adapter. |
| Hóa đơn | `test_g3_hd_1`, `2a`, `3a`, `3b`, `g3_hd_2b.cjs`, `g3_hd_2c.cjs` | Consumer cũ gọi `ha_tang.engine_hoa_don`/`nguon.hoa_don_xml`: `test_xs3_hoa_don`, các test reader hóa đơn, `test_l11_k2`; không nhầm chuỗi cột có chữ “hoa_don” trong `k2/kho_so_luong.py` thành import engine. `test_g2_33`, `33b` kiểm tài khoản/process. |
| Mask | `test_g3_mask_1`, `5`, `5b`, `6` | Công cụ tài khoản, `test_g2_33`, UI chứa mã. `ha_tang/dich_sqlite_pg.py` có `_mask` trong tên helper, không phải import engine Mask. |
| Trích | `test_g3_trich_1a`, `1b`, `3a`, `3b`, `4a`, `noi`; `test_g3_ai_6` | `test_g3_ai_6` kiểm AST, closure import, expectedFailure và **số dòng** nguồn; thay đường dẫn không được nới allowlist để che client cũ. Regression M4 phải chạy nếu chuyển sở hữu helper nguồn; không sửa bộ nguồn M4 chỉ vì đóng gói. |

Tên đầy đủ các test viết tắt ở bảng là `tests/<tên>.py`; riêng hai test hóa đơn Node giữ đuôi `.cjs`. Test dùng import `from ... import chay as ...` và patch globals nên shim chỉ `from ... import *` không đủ.

Các điểm đọc file cứng phải sửa cùng lần chuyển tương ứng:

- `test_g3_ai_2.py:316`, `test_g3_ocr_2.py:83`, `test_g3_hd_3a.py:145`: manifest dưới `src/.../engines`.
- `test_g3_ai_1a.py:61`: AST bắt đúng import DTO từ `kho_tri_thuc.tri_thuc.cong_ai`; khi đổi chủ sở hữu phải sửa locator này cùng lát, vẫn kiểm DTO cùng identity, không tự tạo client/class/cổng khi import.
- `test_g3_mask_1.py:18`: cả thư mục contract/manifest theo đường cũ.
- `test_g3_ai_6.py:33` và các bảng cạnh/số dòng: thư mục engine trích.
- `g3_hd_2b.cjs:12`, `g3_hd_2c.cjs:10,224`: `require/require.resolve` đường CJS cũ.
- `test_g3_trich_3a.py:139`, `test_g3_trich_noi.py:389`: manifest cạnh `module.__file__` — phải giữ bố cục này ở đích.
- Các test sinh tiến trình con thường đặt `PYTHONPATH=src` hoặc tự thêm `src`: shim phải hoạt động ở cả cha/con, không phụ thuộc cwd hoặc môi trường của shell cha.

UI/công cụ có chuỗi tên engine: `C/ui/{engine,van_hanh}.js`, `tests/{g2_31b1,g2_31b2,ui_engine}.cjs`, `tools/tao_tai_khoan_core.ps1`; `C/ui/engine.js:13–14` hiện có nhãn bốn engine, thiếu AI. **Màn dùng capability này khác màn Quản lý engine** ở `C/ui/quan_tri.js`; không thay một màn rồi báo đã sửa màn kia.

**Module CRM ngoài repo:** có `D:/Claude/Phan mem ho tro ke toan/Module/crm`. Đã tìm trên các tệp tracked `backend`, `frontend`, `tests`, `tools`, `module.json` bằng Git read-only với `safe.directory` chỉ cho lệnh, không sửa cấu hình. Chỉ thấy chú thích `backend/chay.py:305` so sánh launcher với OCR, không thấy import engine hoặc đường `engines/e_*`. Không kết luận cho tệp untracked/build, worktree CRM khác hoặc dependency đóng sẵn; `.sdk` có vùng không đọc được và không phải phạm vi mã nguồn cần quét. Không sửa repo CRM trong G3-GOI nếu chưa có handoff riêng.

### 2.4. Phụ thuộc thư viện và nguồn ghim

| Thành phần | Bằng chứng đọc được | Cách ghim đích |
|---|---|---|
| Python chung / SDK | Repo yêu cầu Python ≥3.11; SDK nguồn `1.4.1`. Repo có `cryptography==49.0.0`, `openpyxl~=3.1`. | Ghim wheel SDK đã build/test và thư viện thực dùng trong từng môi trường. `~=3.1` là khoảng được Anh duyệt CD-059, **không phải exact lock**. Ghi lock resolved riêng sau kiểm runtime, không tự nâng bản. |
| AI | Các adapter và `cong_ai`/`ai_cuc_bo` chủ yếu stdlib; crypto thuộc SDK, không cần thêm OpenAI/Anthropic SDK. | Không thêm `openai`, `anthropic`, requests/httpx vì đóng gói. Tách DB driver khỏi phụ thuộc engine; Local luôn có, Cloud tiếp tục qua cổng hiện hữu + Mask v2 và kiểm còn sót. |
| OCR | Khảo sát nguồn cũ ghi `local-mask-ocr 2.1.0`, lock `defusedxml==0.7.1`, `pymupdf==1.28.2`; `extraction/layout` dùng hai thư viện này, lazy `runtime` dùng Tesseract. Theo CD-100: **ưu tiên `D:\GPT\OCR\abbyy-hotfolder`**, dự phòng `D:\GPT\OCR\mask_ocr` **chỉ Tesseract (vie+eng)**. | Kiểm lock với đúng subset, không tự nâng/thêm thư viện. TUYỆT ĐỐI KHÔNG chép `in\`, `out\`, `jobs\`, `state\` của abbyy-hotfolder (có khóa API — không đọc, không in, không commit); không chép VietOCR/mô hình riêng/dual. ABBYY/Tesseract/model ghim theo cài đặt được phép, không chép license/bí mật. |
| Hóa đơn Python | Reader XML/ZIP/Decimal và adapter chủ yếu stdlib; native Job/socket dùng `ctypes` Windows. | SDK + thư viện thực dùng, không thêm XML parser thay reader đang chạy. Không dùng pip freeze của toàn ứng dụng để dựng lock engine. |
| Hóa đơn Node | `hoadon-downloader 1.0.0`; package.json dùng range, lock v3 resolved: `adm-zip 0.5.18`, `dotenv 16.6.1`, `exceljs 4.4.0`, `express 4.22.2`, `fast-xml-parser 4.5.7`, `playwright 1.62.1`. | Đây là dependency **toàn dự án nguồn**, không khẳng định engine cần tất cả. Mang closure `build.js`/helper sạch và subset thật cần; giữ lock/integrity, Node và Chromium revision. Không chạy postinstall tải browser hoặc đọc dotenv trong worker. Portal thật vẫn chờ seam. |
| Mask | `requirements-api-lock.txt` nguồn gồm FastAPI `0.141.1`, Pydantic `2.13.5`, Uvicorn `0.53.0`, cryptography **`50.0.1`**, python-docx `1.2.0`, lxml `6.1.1`, pywin32 `312` và dependency bắc cầu. Pyproject nguồn chỉ có cấu hình test/lint. | Không trộn lock Mask với Core đang cryptography49. Tách venv/process hoặc chốt bản tương thích có test; ghi rõ nguồn Mask là dependency được cài riêng, hoặc bundle sạch nếu được phép. Không chép kho khóa/danh mục thật. |
| Trích | `xlsx_mini` thuần stdlib; `xuat.py` lazy dùng openpyxl. `doc_hop_dong.py` còn nhánh PDF lazy `pdfplumber/pypdf`, nhưng wrapper hiện chặn PDF/COM. | Không cài thư viện của nhánh bị chặn để làm xanh giả. Gói trích chỉ DOCX/XML + xuất đã cho phép; openpyxl exact resolved cần lead đo/chốt. Catalog XD 37 mã có SHA riêng, không thay bằng hash code. |

SHA thực đo ở HEAD cho các nguồn sẽ cần tách sở hữu (không phải chứng nhận runtime):

| Tệp | SHA-256 |
|---|---|
| `src/kho_tri_thuc/tri_thuc/cong_ai.py` | `42158bafbf1334ee3e9563d131163365e4d10707e7f454e96939c2ec4d4c05e2` |
| `src/kho_tri_thuc/ha_tang/cong_ocr.py` | `7f1df3f28c8c5685f0e2da82993a257823ada2ad0d4bf0129b860d0921a157ed` |
| `src/kho_tri_thuc/nguon/hoa_don_xml.py` | `d8ef5593c740258cef117cdf14229dd351205f2efbf976d3c9a24843d85f1329` |

Mã đang khai các SHA nguồn lịch sử: `docx.NGUON_SHA256=bbe8d957...`, `quy_trinh.NGUON_SHA256=a76e95a5...`, `ai_chung.NGUON_SHA256=5ee214ea...`, `bang_ke.SHA256_NGUON=ca7fe35c...`; đây là giá trị đọc từ mã, chưa đối chiếu tất cả nguồn ngoài trong lát này. `tham_so.py` phân biệt SHA nguồn gốc và bản repo; catalog có SHA `05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd`. `do_chinh_xac.py` còn ghim scorer gốc ngoài repo khác bản scorer M4; giữ cả hai provenance, không thay bằng “hash mới” để vượt gate.

## 3. Thiết kế đích và tương thích

### 3.1. Bố cục và quyền sở hữu

```text
engines/
  e_hoi_ai/                    # tương tự bốn engine còn lại
    engine.json
    __init__.py               # marker thuần, không I/O/đăng ký khi import
    chay.py, dto.py, ...       # tên và API hiện có giữ nguyên
    lib/                      # lõi thuộc riêng engine, nếu cần
    vendor/                   # chỉ nguồn sạch cần thiết, có provenance
    contract/
      schemas.json            # bundle offline, gồm closure $ref đã dùng
      vi_du.json              # ví dụ DEMO vào/ra + ca âm dùng trong test
    tests/
      test_doc_lap.py
    pyproject.toml            # distribution riêng, package-data đầy đủ
    requirements.lock         # exact resolved; không bí mật/đường máy thật
    NGUON.md
    README.md
    CHANGELOG.md
src/kho_tri_thuc/engines/e_hoi_ai/
    __init__.py               # shim source checkout, không bản sao nghiệp vụ
```

Hóa đơn giữ `bang_ke.cjs`, `portal.cjs` cạnh code Python và có `package.json`, `package-lock.json` khi closure Node đã ghim. Gói nguồn OCR/Mask có thể nằm `vendor/` hoặc wheel nguồn dưới thư mục engine theo quyết định lead; không dựa vào đường tuyệt đối của máy phát triển. Binary/model/license lớn là điều kiện cài đặt ghi trong README, không coi gói tự đủ đồng nghĩa mang cả hệ điều hành, DB hay bí mật.

Một implementation cho mỗi năng lực: cổng AI thuộc AI, cổng OCR thuộc OCR, parser hóa đơn thuộc hóa đơn, helper trích thuần thuộc trích; helper kỹ thuật dùng chung đưa vào SDK với import tương thích. Core giữ DB, registry, KT, launcher thật, cấp bí mật, lease/ACK, cổng và quyền. Engine không nhập Core server để kiểm môi trường; nhận giao diện SDK/provider được Core cấp. Thư viện đã chuyển sở hữu để lại bridge tại đường cũ cho consumer cũ, không tồn tại hai bản thuật toán hoạt động.

`NGUON.md`: bảng đường gốc, commit/phiên bản, SHA-256 đầy đủ **của từng tệp nguồn thực mang vào**, vị trí đích, nguyên trạng hay có sửa, lý do/sự khác biệt. File chuyển nội bộ ghi HEAD nguồn; file vendor ghi nguồn độc lập và bản repo riêng nếu khác. Không tạo manifest hash/freeze hay bản sao repo ngoài yêu cầu này. Không đổi SHA nguồn lịch sử khi chỉ đổi import ở adapter.

`README.md` khoảng một trang: làm gì, capability thực có, entry/cách Core khởi động, dependency, tài khoản Windows theo **mã hồ sơ**, ngoại lệ đã duyệt, trạng thái CHUA_KIEM. Không ghi credential/tên người dùng thật. `CHANGELOG.md` ghi phiên bản đóng gói và thay đổi seam; thay code/gói làm đổi package hash thì phải tạo version/pins mới theo chính sách lead, không thay ruột của gói đã ghim.

### 3.2. Chọn shim giữ namespace, không đổi tên package engine

| Phương án | Lợi / bất lợi | Kết luận |
|---|---|---|
| Giữ `kho_tri_thuc.engines.<tên>`; shim `__init__.py` đặt `__path__` sang thư mục gốc engine | Giữ submodule, relative import, class identity, patch globals, entry trong manifest. Cần kiểm bố cục wheel và resolver đường dẫn. | **Chọn.** Ít thay đổi nhất vì năm thư mục hiện là namespace package, chưa có API ở `__init__.py`. |
| Đổi sang `ktt_engine_*`, re-export từng module / alias `sys.modules` | Distribution rõ nhưng nhiều wrapper, dễ nạp hai lần, khác class identity/monkeypatch, entry/pins cùng đổi. | Không cần cho CD-042. Chỉ xem lại nếu packaging thực nghiệm chứng minh namespace cũ không dùng được. |
| Thêm repo root/engine vào `sys.path`, `.pth`, hoặc sao chép implementation tại đường cũ | Dễ thử tại máy phát triển nhưng phụ thuộc thứ tự/cwd, khó kiểm import chéo, có thể nạp sai bản. | Không chọn làm cơ chế đóng gói. |

Chi tiết phương án chọn:

1. Một lần `git mv` mỗi tệp từ `E/<tên>/` sang `engines/<tên>/`; **không đổi logical module name**. Shim cũ chỉ xác định một thư mục đích tin cậy rồi đặt `__path__`; không `import *`, không nạp config/bí mật/engine khác, không sửa `sys.path` toàn cục.
2. Resolver source dựa vị trí shim/repo, không `Path.cwd()`, không lấy URL/path từ request. Mất gói → lỗi rõ; không lùi sang bản code cũ hoặc một thư mục engine bất kỳ. Test import từ cwd khác và tiến trình con `PYTHONPATH=src`.
3. `module.__file__` của submodule nằm tại `engines/<tên>/<module>.py`, do đó manifest cạnh `chay/tich_hop` vẫn dùng được. Test đọc đường cứng chuyển sang đích; không để manifest bản sao ở src. `__init__.py` đích chỉ marker, không có side effect cần shim phải thực thi lại.
4. Distribution riêng dự kiến `ktt-engine-<tên-không-e_>`; cấu hình setuptools map package `kho_tri_thuc.engines.<tên>` vào thư mục engine, bao cả `lib/vendor`, JSON/CJS/catalog/lock/README/NGUON/tests cần thiết. Namespace cha không được một wheel engine chiếm bằng `__init__.py`. Core wheel **loại `kho_tri_thuc.engines*` của source shim** để không hai distribution cùng sở hữu đường `__init__.py`; source checkout vẫn giữ shim.
5. Khi cài thật, wheel engine sở hữu namespace package của nó trong cùng môi trường chạy được Core duyệt. Core không import implementation khi discovery; chỉ runtime sau gate mới nạp entry. Nếu runtime riêng, SDK + bundle engine được cài trong venv riêng và Core cấp đường executable từ hồ sơ đã duyệt.
6. SDK wheel bổ sung namespace tương thích `kho_tri_thuc.sdk_core` → public `kho_tri_thuc_sdk`, **cùng một object cho submodule/DTO trong một process**; source checkout vẫn dùng SDK nguồn hiện tại. Bridge chỉ thuộc phân phối SDK, engine không tự dựng bản SDK hoặc alias Core server. Gate bắt buộc chứng minh đối tượng từ bootstrap và concrete channel khớp kiểu; không bỏ `isinstance`/kiểm lease để làm xanh. Nếu bridge không đạt, lead khóa lát SDK riêng trước khi đi tiếp, không lén đổi cả Core.

### 3.3. Tháo dependency, không viết lại engine

- **AI:** chuyển lõi stdlib `cong_ai`/`ai_cuc_bo` thành sở hữu AI. Tách `BoGhiPostgres` về phía Core, để đường legacy tái xuất tương thích. Adapter AI chỉ dùng bộ ghi qua Core hiện có, bí mật từ bootstrap RAM. Các lớp provider hiện có chỉ được giữ trong cổng AI trung tâm với gate Mask; không tạo client AI mới trong trích hay bất kỳ engine khác.
- **OCR (CD-100):** nền chuyển `CongOCR` và bridge `ha_tang.cong_ocr`, parser nguồn/adapter/giữ bảng 17–19 đã gộp. Ưu tiên mã sạch `D:\GPT\OCR\abbyy-hotfolder`; `D:\GPT\OCR\mask_ocr` chỉ Tesseract (vie+eng), PDF có chữ, DOCX, giữ bảng, xuất Word, hàng chờ/chống trùng. Giấy phép **“phần mềm nội bộ, dùng nội bộ tập đoàn”** đã chốt. TUYỆT ĐỐI KHÔNG đọc/in/chép/commit `in\`, `out\`, `jobs\`, `state\` của abbyy-hotfolder (có khóa API), không chép VietOCR/mô hình riêng/review dual; không xóa mã cũ. Dùng lại parser/adapter, không dò nguồn ngoài gói hoặc chèn sys.path. Bổ sung OCR-NOI để lớp chữ ABBYY → kết quả chung, không OCR lại ảnh nền; OCR-VUNG dùng `crop_quad`. Lead khóa whitelist mã sạch cần thêm ở lát triển khai, không giao lại 17–19 nguyên trạng.
- **Hóa đơn:** reader XML giữ nguyên thuật toán/Decimal/raw-ref; chuyển sở hữu và shim. `InvoiceIssue.as_issue()` phải tiếp tục trả Issue mới, cùng kiểu mà consumer legacy dùng. Tách dataclass Issue bốn trường thuần sang SDK kỹ thuật, `nguon.fixture` re-export cùng lớp; reader import SDK, không nhập cả fixture/Config vào package. Tách bảng ánh xạ/trạng thái thuần khỏi `ha_tang.engine_hoa_don` trước khi adapter dùng, không để vòng import reader ↔ wrapper. Kiểm môi trường và tài khoản thật ở Core, engine chỉ nhận kết quả/SDK interface.
- **Mask:** Core implementation của launcher vẫn ở Core; public SDK chỉ chứa interface/lỗi/DTO cần dùng, engine nhận provider tin cậy. Vòng đời và điều kiện chặn hiện tại phải giữ. Việc gói nguồn Mask sạch và capability đã kiểm là dependency riêng, không được bịa capability trong lát move.
- **Trích:** mang các helper thuần từ M4 vào gói trích bằng nguồn ghim; consumer M4 đang dùng bản nguồn riêng không bị sửa khi chưa có handoff tách sở hữu. Không duy trì hai cổng AI/OCR: nhánh legacy `tham_so` phải dùng pipeline đã bọc với cổng chung thay vì nạp `quy_trinh` nguồn kéo client cũ. Helper vendor nguyên trạng có thể được bọc bằng seam như `_boc_ham` hiện có; bản có sửa ghi hash nguồn và patch riêng.
- ~~**AI cho trích:** cần façade SDK/port do Core cấp, giữ DTO/cờ `chi_cuc_bo`, không import implementation AI từ engine khác. `EngineModule` hiện dành cho module, **không mặc nhiên dùng nó trong engine**. Chốt wire/binding nếu chưa có cửa engine→Core cho năng lực phụ; không thêm HTTP/RPC tổng quát hoặc copy `CongAI` sang trích. Đây là gate thiết kế ở §6, không được đánh dấu đã có chỉ vì tên hàm tồn tại.~~ **Thay theo CD-111:** trích chỉ chuẩn bị đầu vào và hậu kiểm kết quả ở hai bước; Core xếp bước Hỏi AI ở giữa theo CD-110. Không engine nào gọi engine khác; không thêm façade/operation AI riêng. Bước Hỏi AI dùng cổng chung, ép Local bản 1, không giữ transaction khi chờ AI, lỗi/mất kết nối không chuyển Cloud; kiểm quyền/pháp nhân/lease bằng kênh việc chuẩn.

### 3.4. Contract tự đủ và nguồn ghim

Mỗi package có `contract/schemas.json` bundle offline gồm schema capability đang công bố và closure `$ref` (thường có `chung.v1`), `vi_du.json` gồm ví dụ vào/ra DEMO. Sao chép bản contract công bố từ Core là **bản phân phối có cùng ID/version/hash**, không tạo chủ sở hữu contract mới. Test kiểm resolver không tải mạng, schema/example/ca âm, parity với sổ Core và manifest. Schema nghiệp vụ mới hoặc đổi nghĩa/version phải qua Anh theo quy tắc dự án.

Mask trước gate chỉ có `du_thao.json`; chưa coi bộ này là contract đã đăng ký. Bốn engine khác không tự quảng bá thêm bảng OCR, ZIP/bảng kê, tải hóa đơn, hoặc đường PDF trực tiếp của trích vì đã thấy file adapter. **CD-100 chốt bổ sung `ocr.trich_vung@1` vào OCR v1** (OCR-VUNG: dùng lại `crop_quad`, trả chữ + cờ nghi ngờ); chỉ công bố sẵn sàng khi có contract/test/bằng chứng. `ocr.trich_bang@1`, hóa đơn giấy và bảng kê để sau, không phải điều kiện xong OCR v1.

## 4. Engine Manager và giao diện

### 4.1. Tái dùng Core hiện có

- `C/kiem_tra_goi.py:139–140` biết chọn `engine.json` trong gói; chưa phải bộ discovery thư mục.
- `C/dich_vu_engine.py`: router pins bất biến → registry/contract/HoSoChay/KT/lease/runtime; không quét thư mục, không spawn. Giữ nguyên chức năng này.
- `C/chay_core.py:553–563`: composition root hiện nhận `ghim_engine`, `loai_viec`, `ho_so_runtime`, `doc_kt`; thiếu provider trả lý do `ENGINE_CHUA_*`. Discovery cần ghép ở đây, không ép router tự tìm code.
- `C/routes_quan_tri.py`: danh sách quản trị đọc registry đã cài, kiểm phiên/Admin, con trỏ HMAC; `_BO_PHAN` kín, trạng thái vận hành `stopped/starting/ready/busy/dang_dung/failed/thu_hoi`. Không có trường “giả/thật/chờ”; không trả tùy ý vào response hiện hành.
- `C/ui/quan_tri.js:245–330`: dùng danh sách và `/ten` từ API, có xử lý rỗng, nút Thêm engine chưa mở. Dùng màn này làm gốc, không dựng trang quản lý thứ hai.

### 4.2. Discovery và đăng ký

Tạo `C/nap_engine.py` làm bộ đọc thuần: lấy `thu_muc_engines` từ composition/config tin cậy; quét **một cấp** `*/engine.json`, đọc UTF-8, kiểm schema, mã trùng, version, mã/thư mục nhất quán, entry trong gói, đường dẫn/symlink không thoát root, closure contract/hash. Không import entry, không đọc bí mật, không mở DB/port khi quét. Không có danh sách năm đường code hardcode trong Core.

Nguồn discovery → kiểm gói đã có → đăng ký/snapshot đã duyệt trong registry → hồ sơ runtime/pins mới. Đọc manifest **không đồng nghĩa tự cài/bật**, không cấp quyền hay sửa CSDL trong GET. Gói sai được báo chờ/lỗi có lý do; không một phần capability được chạy. Xử lý thay version theo drain/ACK và công tắc, không thay pins của việc đang chạy. Thiếu manifest, như Mask hiện tại, là thiếu bằng chứng, không bỏ qua im lặng ở báo cáo kiểm gói.

Các bài kiểm quan trọng: root đổi vị trí/cwd, thứ tự danh sách ổn định, manifest hỏng/thiếu/đọc lỗi, trùng mã/version, đường dẫn lạ, capability chưa đủ KT, discovery không import/spawn, file đổi giữa kiểm và dùng, package hash/pins lệch, TAT không tự bật, restart không mất trạng thái đã duyệt.

### 4.3. Đúng năm dòng và “giả / thật / chờ”

Tách **nguồn dữ liệu trình diễn/triển khai** khỏi **trạng thái process**: “Thật · Đang dừng” là hợp lệ; “có manifest” không đủ hiện “Thật · Sẵn sàng”. Thật ở đây là adapter/runtime nối thật trên DEMO, không phải dữ liệu sản xuất. Một engine có thể XML đã nối nhưng tải thuế còn chờ; chi tiết phải ghi theo capability.

| Nhãn | Điều kiện hiển thị | Điều không được suy |
|---|---|---|
| **Dữ liệu giả** | Fixture UI hoặc adapter giả, banner rõ ở màn/hàng tương ứng | Không ghi vào registry thật, không coi ready/KT đạt. |
| **Chờ** | Chưa cài/thiếu manifest, SDK, tài khoản, adapter, phép đo hoặc bằng chứng | Không tạo capability giả để đủ số dòng. Nêu lý do tiếng Việt. |
| **Thật** | Snapshot đã cài/KT, adapter và nguồn runtime được máy chủ xác minh | Không đồng nghĩa process đang ready, không đồng nghĩa mọi capability của engine đã đạt. |

**Mốc sớm CD-058:** cùng lúc làm mẫu AI, nâng màn quản trị bằng fixture đủ năm dòng; kiểm luồng Quản trị Core → Quản lý engine → chi tiết capability/lý do → quay lại. Fixture nằm trong test/nhánh trình diễn được chọn rõ, mặc định không ghi gì; không bấm thử cổng thuế/Cloud thật.

**API cần chốt:** danh sách hiện tại chỉ thể hiện bộ phận đã cài và DTO không có nguồn triển khai/lý do chờ. Đề xuất version response quản trị bổ sung inventory (dự kiến/phát hiện/đã cài) với trường nguồn, lý do, thông tin KT; dòng chưa cài không được gán UUID, row_version hoặc quyền thao tác giả. Catalog “năm engine dự kiến” là **dữ liệu cấu hình đã duyệt** ở `engines/du_kien.json`, chỉ tên/mã/mô tả, không code path/capability/credential; Manager vẫn khám phá capability từ `*/engine.json`. Mở rộng này phải được lead đối chiếu chuẩn API và trình Anh nếu vượt quyết định đã chốt; schema và route cùng version, giữ response cũ cho caller cũ. Không lén thêm field vào `_BO_PHAN` kín.

Catalog cho phép Mask hiện “Chờ” trong giai đoạn giữa, nhưng **không miễn điều kiện cuối kỳ: có năm manifest hợp lệ**. Nếu không duyệt inventory mới, giữ UI fixture mốc sớm và chỉ hoàn thành yêu cầu năm dòng API sau gate Mask cùng đăng ký đủ năm engine. Lead chọn nhánh trước lát 12; không phát hành giả định API chưa được duyệt.

Mốc cuối: nguồn UI từ API/snapshot tin cậy, đúng năm mã duy nhất của bộ gói này, không nhân dòng do nhiều version; chi tiết giữ version đang dùng và bản chờ nâng cấp. Discovery vẫn tổng quát, không chặn engine thứ sáu chỉ để ép test bằng năm. Lead kiểm trên môi trường chỉ có bộ năm engine, chụp ảnh và ghi đường mở tại cổng DEMO được cấp. Không khởi động server/PG trong worker.

## 5. Chia lát triển khai

### 5.1. Quy ước đếm tệp và cổng gộp

Các hàng dưới là **40 lát**, không giao việc cho agent khác từ worker. Lead khóa đường dẫn trước giao, dùng nhánh từ nền tích hợp mới nhất; không giao trùng lát engine/SDK/UI đang chạy. `P = engines`, nên `P/<tên> = engines/<tên>`; ký hiệu `B(P)` trong hàng move là bộ tệp mới chuẩn đặt trong thư mục engine của hàng đó.

- **S**: tệp hiện hữu sửa nội dung, kể cả tệp vừa `git mv` rồi sửa. Tối đa 3 mỗi hàng. Tệp mới ở một lát trước thành hiện hữu ở lát sau và được tính S bình thường.
- **M**: di chuyển nguyên trạng, ghi riêng số lượng/bộ nguồn ở §2.1. M không miễn S nếu thay nội dung. Bridge tạo lại tại đường cũ được kê **N**, nhưng lead kiểm diff rename để tránh giấu sửa mã.
- **N**: tệp mới, liệt kê cụ thể hoặc tập nguồn đã định danh; không wildcard cho phép worker chép cả dự án. N không tính vào giới hạn “tệp SỬA” của handoff, nhưng vẫn phải được whitelist. Nếu lead giới hạn cả tệp mới, tách phần tài liệu/contract thành lát con trước giao và cập nhật số lát.
- Bộ N chuẩn **B(P)** ở lần move: `__init__.py`, `pyproject.toml`, `README.md`, `CHANGELOG.md`, `NGUON.md`, `contract/schemas.json`, `contract/vi_du.json`, `tests/test_doc_lap.py`, cộng shim `E/<tên>/__init__.py`. Riêng Mask chưa tạo schemas/ví dụ công bố cho tới gate 28, vẫn giữ bản nháp M. Lock chỉ tạo khi đã có căn cứ resolved, không ghim số đoán.
- Mỗi lát gộp phải chạy regression liên quan; bước move chưa đạt tự đủ được ghi là **mốc chuyển vị trí**, không nghiệm thu cả engine. Không gộp trạng thái import hỏng để chờ lát sau sửa. Nếu dependency cần làm trước move mới giữ xanh, lead đảo thứ tự trong cùng nhóm, không bỏ test.
- Toàn bộ thay đổi byte-exact/hash-sensitive phải được test trước/sau; một lỗi sửa hai lần chưa xong thì dừng báo lead. Không tạo quy trình kiểm riêng hay freeze.

### 5.2. Hàng đợi lát, tệp và test

Mã test ở cột cuối tham chiếu bộ §5.3. `thuần` bao gồm mock/AST/offline và socketpair/process giả khi môi trường cho phép, không có dịch vụ ngoài; các ca Windows thật và PG ghi riêng.

| # / Mã | Việc, tệp S ≤3 | M / N được phép đề xuất | Phụ thuộc và test |
|---|---|---|---|
| 01 · GOI-AI-MAU | Chuyển AI làm mẫu, giữ namespace. **S(1):** `T/test_g3_ai_2.py` đổi đường manifest. | **M(6):** toàn bộ `E/e_hoi_ai` ở §2.1 → P. **N:** B(P), contract lấy đúng bản Core đã công bố. | Đầu tiên, sau lead xác nhận G2 đủ để bắt đầu G3-GOI. AI + test import/manifest mẫu, thuần; chưa gọi AI. |
| 02 · GOI-UI-GIA | Màn năm engine/lý do chờ có banner. **S(1):** `C/ui/quan_tri.js`. | **N:** `T/g3_goi_quan_tri.cjs` (fixture và test DOM); không thêm fixture production vào registry. | Song song 01; ADMIN/UI thuần, dùng chức năng quản trị đã có. Lead xem mốc sớm ngay, không chờ backend xong. |
| 03 · GOI-SDK-TUONG-THICH | Bridge namespace trong wheel SDK và kiểm identity. **S(2):** `tools/dong_goi_sdk.py`, `T/test_md_2.py` cập nhật kỳ vọng wheel/bridge theo version nguồn. | **N:** `T/test_g3_goi_sdk.py`; bridge chỉ là nội dung wheel do builder tạo, không chép SDK vào engine. | 01; SDK thuần/wheel, bootstrap/lease/type parity. Không đổi public ABI nếu chưa có gate; ghi riêng lệch version test có sẵn trước lát. |
| 04 · GOI-SDK-HAM-THUAN | Đưa helper kỹ thuật dùng chung vào SDK. **S(3):** `ha_tang/primitives.py`, `ha_tang/engine.py`, `nguon/trich6_host.py` dưới `src/kho_tri_thuc`. | **N:** `S/primitives.py`, `S/engine_legacy.py`, `S/tien_trinh_phu.py`, `T/test_g3_goi_ham_thuan.py`. Nguồn cũ giữ bridge; chỉ lấy helper env/dòng, không mang host/SQL vào SDK. | 03; SDK + test primitives/legacy engine/host thuần, class/exception identity. Không thay thuật toán tiền/hash. |
| 05 · GOI-SDK-KHUNG | Interface launcher/DTO kiểm gói ở SDK, implementation Core giữ nguyên. **S(3):** `C/khoi_chay_tai_khoan.py`, `C/kiem_tra_goi.py`, `T/test_g2_33b.py`. | **N:** `S/ho_so_engine.py`, `T/test_g3_goi_ho_so.py`. | 03; SDK/WIN mock; Windows thật do lead, CHUA_KIEM nếu chưa chạy. Không đổi ACL/tài khoản. |
| 06 · GOI-AI-LOI | Tách lõi cổng, adapter DB giữ phía Core. **S(3):** `tri_thuc/cong_ai.py`, `tri_thuc/ai_cuc_bo.py` dưới src (bridge sau chuyển), `P/e_hoi_ai/bi_mat.py` dùng lõi mới. | **N:** `P/e_hoi_ai/lib/{__init__,cong_ai,ai_cuc_bo}.py`, `C/nhat_ky_ai_legacy.py`, `T/test_g3_goi_ai_loi.py`. Chuyển có chỉnh nên tính S nguồn; không M nguyên trạng. | 03–04; AI + consumer cũ thuần. Core bridge tái xuất cả API cũ, globals patch phải tới cùng module; kiểm không import DB từ package AI. |
| 07 · GOI-AI-ADAPTER | **S(3):** `P/e_hoi_ai/{dto,hoi}.py` đổi sang lõi trong gói/SDK, `T/test_g3_ai_1a.py` đổi locator AST DTO, giữ kiểm identity/không client. | Không N ngoài danh sách. | 06; AI/BM thuần, Local-only, canary/Mask guard. |
| 08 · GOI-AI-NHAT-KY | **S(2):** `P/e_hoi_ai/nhat_ky.py`, `P/e_hoi_ai/tests/test_doc_lap.py`. | Không N. | 07; AI5a/5b, ACK/retry/idempotency, snapshot/statistics thuần. PG audit cuối do lead. |
| 09 · GOI-AI-GHIM | Chốt nguồn/lock mẫu. **S(3):** `P/e_hoi_ai/{NGUON,README,CHANGELOG}.md`. | **N:** `P/e_hoi_ai/requirements.lock`. | 08 và **SDK cuối ở 34**; AI + package độc lập đã build thuần. SDK pin là bản có bridge đã kiểm; không tự ghi số version tương lai. Hàng ghim chạy sau các nhóm code, không chặn nhóm move tiếp theo. |
| 10 · GOI-EM-DOC | Discovery không kích hoạt. **S(0).** | **N:** `C/nap_engine.py`, `T/test_g3_goi_nap.py`. | 01; DISC thuần với thư mục/JSON DEMO, chưa import implementation. Thiết kế tổng quát ngay, không chờ đủ năm thư mục mới viết test. |
| 11 · GOI-EM-NOI | Ghép discovery với registry/runtime hiện có. **S(2):** `C/chay_core.py`, `C/nap_engine.py`. | **N:** `T/test_g3_goi_manager.py`. | 03,10; DISC/E2 thuần; PG đăng ký/pins/KT do lead sau đủ gói. Không sửa router pins để bỏ gate. |
| 12 · GOI-ADMIN-HOP-DONG | Khóa schema inventory/phân biệt dữ liệu giả/thật/chờ theo §4.3. **S(1):** `docs/47-core/chuan/CHUAN-CORE-API-v1.0.md` (chỉ phụ lục version mới, không sửa nghĩa response cũ). | **N:** `C/contract/quan_tri_engine.json`, `engines/du_kien.json`, `T/test_g3_goi_inventory_schema.py`. | 10; gate lead/API ở §6; CONTRACT thuần. Nếu không duyệt inventory mở rộng, hoãn hàng này và 13 tới khi có năm manifest; không triển khai API suy đoán. |
| 13 · GOI-ADMIN-NOI | Route/version inventory đọc snapshot tin cậy. **S(2):** `C/routes_quan_tri.py`, `C/ung_dung.py`. | **N:** `T/test_g3_goi_inventory_api.py`. | 11–12; ADMIN thuần/WSGI và PG opt-in do lead. Admin/CSRF/phân trang/không lộ đường dẫn. |
| 14 · GOI-UI-API | **S(3):** `C/ui/quan_tri.js`, `C/ui/engine.js`, `T/g3_goi_quan_tri.cjs`. | Không N. | 02,13; ADMIN/UI thuần, bỏ hardcode danh sách phát hiện, có tên AI, đúng màn quản trị; không ép engine sử dụng cũng có quyền Admin. |
| 15 · GOI-OCR-MOVE | **S(1):** `T/test_g3_ocr_2.py` đường manifest. | **M(6):** bộ OCR §2.1 → P. **N:** B(P). | Sau mẫu vị trí 01 và bridge 03; OCR thuần, parser nguồn có thể còn CHUA_KIEM, không coi đã độc lập. Không chờ 09 để tránh vòng phụ thuộc khóa SDK. |
| 16 · GOI-OCR-CONG | Chuyển sở hữu `CongOCR`. **S(1):** `src/kho_tri_thuc/ha_tang/cong_ocr.py` bridge. | **N:** `P/e_ocr/lib/{__init__,cong_ocr}.py`, `T/test_g3_goi_ocr_cong.py`. | 04,15; OCR + consumer `test_cong_ocr`, M9 thuần. Giữ khóa file/timeout/ACK/cancel. |
| 17 · GOI-OCR-NGUON | **ĐÃ GỘP 06/11/2026**, mã `270f2af0`, lead `72e8c390`. Nền parser ghim, không sys.path nguồn. **S(0)** trong lát đã giao. | Bộ nguồn đã giao: `P/e_ocr/vendor/__init__.py`, `P/e_ocr/vendor/mask_ocr/{__init__,extraction,layout,common,runtime}.py`, LICENSE nội bộ, `T/test_g3_goi_ocr_nguon.py`. Giấy phép CD-100: “phần mềm nội bộ, dùng nội bộ tập đoàn”. | T; không giao lại. Theo CD-100 ưu tiên abbyy-hotfolder, chỉ nhánh Tesseract của mask_ocr; phần cầu nối bổ sung ở §6.7, whitelist do lead khóa riêng. TUYỆT ĐỐI KHÔNG chép/đọc/in `in\`, `out\`, `jobs\`, `state\` của abbyy-hotfolder. |
| 18 · GOI-OCR-ADAPTER | **ĐÃ GỘP 06/11/2026**, mã `cb51ae4e`, lead `15ebff47`. **S(3):** `P/e_ocr/{abbyy,ban_giao,van_ban}.py`, chỉ SDK/lõi nội bộ/parser ghim. | Không N. | 16–17; T, OCR2/4b/5a/5b thuần; không giao lại. ABBYY thật ở OCR-WIN-NT. |
| 19 · GOI-OCR-BANG | **ĐÃ GỘP 06/11/2026**, mã `406eddce`, lead `66dfdd61`. **S(2):** `P/e_ocr/bang.py`, `P/e_ocr/tests/test_doc_lap.py`. | Không N. | 18; T, giữ ô trống/ô gộp/vị trí bảng Word; không giao lại, không thêm capability trích bảng. |
| 20 · GOI-OCR-GHIM | **S(3):** `P/e_ocr/{NGUON,README,CHANGELOG}.md`. | **N:** `P/e_ocr/requirements.lock`. | Theo CD-100: sau 19 và các bổ sung OCR ở §6.7, **làm theo khung SDK đã gộp, không chờ SDK cuối/34**. T; ghim thư viện/nguồn, kiểm và hướng dẫn môi trường sạch. Không đổi version SDK hoặc ghim wheel 1.4.1 candidate (§6.3); chốt wheel phát hành chung xử lý riêng ở 34. |
| 21 · GOI-HD-MOVE | **S(3):** `T/test_g3_hd_3a.py`, `T/g3_hd_2b.cjs`, `T/g3_hd_2c.cjs` đổi đường file. | **M(7):** bộ hóa đơn §2.1 → P. **N:** B(P). | 01,03; HD thuần + Node giả. Không cần giữ CJS wrapper cũ vì không thấy consumer production require đường cũ trong phạm vi khảo sát. |
| 22 · GOI-HD-READER | Chuyển reader và giữ phép đổi fixture qua DTO SDK. **S(3):** `src/kho_tri_thuc/nguon/hoa_don_xml.py` bridge, `src/kho_tri_thuc/nguon/fixture.py` tái xuất Issue, `S/engine_legacy.py` thêm đúng dataclass Issue gốc. | **N:** `P/e_hoa_don/lib/{__init__,hoa_don_xml}.py`, `T/test_g3_goi_hd_reader.py`. | 04,21; HD + `test_hoa_don_xml`/XS3 và consumer fixture thuần, identity DataError/Issue/Decimal/DTO/raw bytes. `as_issue()` vẫn tạo object mới; không kéo Config vào package. |
| 23 · GOI-HD-ANH-XA | Tách mapping thuần, cập nhật adapter. **S(3):** `src/kho_tri_thuc/ha_tang/engine_hoa_don.py`, `P/e_hoa_don/doc.py`, `P/e_hoa_don/tai.py`. | **N:** `P/e_hoa_don/lib/trang_thai.py`. | 22; HD1/2a/XS3, nhóm reader thuần. Enum/ngoại lệ phải cùng identity qua SDK; không tạo enum thứ hai. |
| 24 · GOI-HD-PHIEN | **S(3):** `P/e_hoa_don/chay.py`, `P/e_hoa_don/phien.py`, `P/e_hoa_don/tests/test_doc_lap.py` bỏ import Core/nguon. | Không N. | 04–05,23; HD3a/3b thuần/WIN mock. KT thật do Core cấp, mặc định CHUA_KIEM; không tự tin cậy caller. |
| 25 · GOI-HD-NODE | Bỏ require nguồn tuyệt đối, dùng closure sạch. **S(2):** `P/e_hoa_don/bang_ke.cjs`, `P/e_hoa_don/portal.cjs`. | **N:** `P/e_hoa_don/vendor/build.js`, `P/e_hoa_don/vendor/config.js`, `P/e_hoa_don/package.json`, `P/e_hoa_don/package-lock.json`, `P/e_hoa_don/tests/nguon.cjs`. Hai file vendor là tập đề xuất tối thiểu, chỉ giao sau lead kiểm closure build thực; thêm file cần whitelist riêng. | 21; HD Node giả, hash/money/PDF provenance; không nạp server/dotenv/portal thật, không postinstall/thuế. Gate nguồn/giấy phép trước bundle. |
| 26 · GOI-HD-GHIM | **S(3):** `P/e_hoa_don/{NGUON,README,CHANGELOG}.md`. | **N:** `P/e_hoa_don/requirements.lock`. | 24–25,34; HD package độc lập, Node lock/integrity; Windows/Chromium thật vẫn lead xác minh. |
| 27 · GOI-MASK-MOVE | **S(1):** `T/test_g3_mask_1.py` đường contract. | **M(3):** bộ Mask §2.1 → P. **N:** B(P) trừ schemas/ví dụ công bố; **không tạo engine.json** ở hàng này. | 01,03; MASK thuần, vẫn “Chờ”. |
| 28 · GOI-MASK-CAP | Đưa manifest vào gói **sau khi** capability/adapter nguồn đạt. **S(1):** `T/test_g3_mask_1.py` cập nhật kỳ vọng đúng bằng chứng mới, giữ test reject capability rỗng. | **N:** `P/e_mask/engine.json`, `P/e_mask/contract/{schemas,vi_du}.json`. Không sửa bản nháp để giả đã duyệt. | Gate **MASK-2/nguồn cấp khóa/contract đã duyệt** do lead xác nhận; chưa đạt thì hàng này chờ, chưa đủ năm gói. CONTRACT/MASK thuần; kiểm nguồn/Windows thật do lead. |
| 29 · GOI-MASK-KHUNG | **S(3):** `P/e_mask/chay.py`, `P/e_mask/vong_doi.py`, `P/e_mask/tests/test_doc_lap.py` dùng SDK interface/helper. | Không N. | 04–05,27; MASK5/5b/6 thuần, chặn trước spawn, RAM/Job/drain. Có thể làm trước 28, không mở khóa nguồn thật. |
| 30 · GOI-MASK-GHIM | **S(3):** `P/e_mask/{NGUON,README,CHANGELOG}.md`. | **N:** `P/e_mask/requirements.lock`, `P/e_mask/nguon/PHU-THUOC.md` ghi phương án bundle sạch hoặc cài riêng/version/SHA được chốt. | 28–29,34 và quyết định nguồn Mask. Không coi PHU-THUOC.md thay mã/adapter thiếu; gate độc lập phải có package nguồn sạch thực dùng, lead mở whitelist nguồn cụ thể trước giao. |
| 31 · GOI-TRICH-MOVE | **S(1):** `T/test_g3_ai_6.py` cập nhật root engine và locator AST, giữ ý nghĩa các kiểm. | **M(8):** bộ trích §2.1 → P. **N:** B(P). | 01,03; TRICH/AI6 thuần; thay tọa độ không xóa test vi phạm. |
| 32 · GOI-TRICH-NGUON | Closure Review thuần. **S(0).** | **N:** `P/e_trich_xuat/vendor/__init__.py`, `P/e_trich_xuat/vendor/review/{__init__,doc_hop_dong,cau_truc,kiem_tra,logic,xlsx_mini,xuat,danh_muc,cau_hinh}.py`, `.../DANH_MUC_THAM_SO.xlsx`, `T/test_g3_goi_trich_nguon.py`. | 31; TRICH/nguồn thuần; catalog bị ignore có thể thiếu worktree, lead cấp bản đúng SHA, không lấy dữ liệu thật. Không vendor AI/Cloud/COM launcher. |
| 33 · GOI-TRICH-THUAN | **S(3):** `P/e_trich_xuat/docx.py`, `P/e_trich_xuat/tham_so.py`, `P/e_trich_xuat/do_chinh_xac.py` dùng nguồn nội bộ, bỏ dependency pipeline client cũ. | Không N. | 32; TRICH1a/4a, ngữ nghĩa chấm/37 mã/provenance thuần. Đường legacy dùng adapter pipeline, không import `quy_trinh` nguồn có client riêng. |
| 34 · GOI-TRICH-AI-SDK | **Tách engine trích thành các bước chuỗi (chuẩn bị / hậu kiểm), không còn import CongAI trong engine trích.** ~~Tháo import cổng AI implementation khỏi trích; khóa version SDK đóng gói. **S(3):** `P/e_trich_xuat/ai_chung.py`, `P/e_trich_xuat/quy_trinh.py`, `S/__init__.py` tăng version do lead chọn sau kiểm tương thích.~~ **Thay theo CD-111:** lead khóa lại whitelist cho tách bước, tận dụng xử lý thuần đã có; không tăng version SDK trong lát tài liệu này. | ~~**N:** `S/ai_engine.py`, `T/test_g3_goi_ai_port.py`.~~ **Thay theo CD-111:** không tạo port riêng. Tệp/test của thiết kế cũ không còn là quyền triển khai; lead giao lại theo phạm vi chuỗi đã duyệt. | ~~Gate façade/wire AI ở §6; chỉ DTO/port ở SDK; transport thiếu có handoff riêng; chốt exact SDK phát hành chung sau hàng này.~~ **Thay theo CD-111:** 05,07,22,33 và bước Hỏi AI đủ contract/runtime/binding; Core kiểm khớp ra/vào và điều phối chuẩn bị → Hỏi AI → hậu kiểm. Giữ TRICH1b/AI6, kiểm wheel/alias/identity độc lập và Local-only; không operation gọi AI giữa chừng. SDK 1.5.0 đã phát hành riêng cho CRM (§6.3); bản chung cho engine do lead chốt riêng. **Không chặn OCR-20 làm nguồn/lock thư viện/hướng dẫn theo khung đã gộp**; không ghim candidate. |
| 35 · GOI-TRICH-RUNTIME | **S(3):** `P/e_trich_xuat/chay.py`, `P/e_trich_xuat/tich_hop.py`, `P/e_trich_xuat/tests/test_doc_lap.py`. | Không N. | 18,34 và ~~cổng AI qua SDK đã nối~~ **thay theo CD-111: bước Hỏi AI trong chuỗi Core đã nối**; TRICH3a/3b/noi, OCR→DOCX provenance/ACK thuần. Giữ chờ ready khi phép đo thiếu. |
| 36 · GOI-TRICH-HOI-QUY | **S(3):** `T/test_g3_ai_6.py`, `T/test_g3_trich_1a.py`, `T/test_g3_trich_3b.py` cập nhật closure/nguồn sau tách. | **N:** `P/e_trich_xuat/tests/test_nguon.py`. | 33–35; TRICH/AI6 thuần, không miễn vi phạm bằng expectedFailure mới. TRICH-4b/READY là gate đã có, **không giao lại phép đo** trong đóng gói. |
| 37 · GOI-TRICH-GHIM | **S(3):** `P/e_trich_xuat/{NGUON,README,CHANGELOG}.md`. | **N:** `P/e_trich_xuat/requirements.lock`. | 36; package độc lập thuần. Lead giữ gate TRICH-4b/READY/độ chính xác trước kích hoạt thật. |
| 38 · GOI-KIEM-DOC-LAP | Loại shim khỏi Core wheel, kiểm đủ năm package/không chéo. **S(1):** `pyproject.toml` gốc. | **N:** `T/test_g3_goi_doc_lap.py`. | 09,20,26,30,37; SDK/DISC/CONTRACT + năm package thuần. Không tạo tool kiểm riêng; dùng unittest/bộ kiểm Core sẵn có. |
| 39 · GOI-EM-NGHIEM-THU | Kiểm discovery→registry→UI và runtime pins cuối. **S(3):** `T/test_g3_goi_manager.py`, `T/test_g3_goi_inventory_api.py`, `T/g3_goi_quan_tri.cjs`. | Không N. | 11–14,38; thuần/WSGI/JS; **PG/WIN/browser do lead**, không worker khởi động dịch vụ. Môi trường bộ năm engine; Mask thiếu hoặc còn CHUA_KIEM bắt buộc thì chưa đạt phát hành. |
| 40 · GOI-TAI-LIEU | **S(3):** `docs/47-core/chuan/CHUAN-CORE-SDK-v1.0.md`, `docs/47-core/g2/KE-HOACH-LAT-G2-G3.md`, `docs/46-chuyen-doi-dieu-phoi/XEM-GIAO-DIEN-CORE.md`. | Không N trong worker; ảnh thực do lead tạo theo quyền/đợt DEMO đã giao. | 39; đối chiếu tài liệu/UTF-8 thuần. Ghi layout/shim/phiên bản mới, không lùi chuẩn. Lead bổ sung ảnh + đường mở đã quan sát, không ghi sẵn “đạt”. |

Các đường `ha_tang/...`, `tri_thuc/...`, `nguon/...` không có prefix ở cột S đều nằm dưới `src/kho_tri_thuc/`. File vendor mới chưa đọc đủ closure/giấy phép hoặc ~~transport AI mới chưa có wire~~ **thay theo CD-111: đầu vào/ra bước chuỗi chưa được chốt** **là điều kiện lead phải khóa trước giao**, không phải quyền cho worker tự thêm file.

### 5.3. Bộ test và phân loại thực thi

| Mã | Thuần/offline/mock worker chạy trong lát code tương lai | PG / môi trường thật do lead |
|---|---|---|
| **AI** | `test_g3_ai_{1a,1b,2,4a,4b,5a,5b}`, `test_bm_kenh`; consumer `test_cong_ai`, `test_ai0_khoa_cloud`, `test_ai1_local_ai_lan`, `test_ai4a_kiem_xac_suat`, `test_xs3_cong`; test package mới. Không gọi AI thật. | `test_cong_ai_nhat_ky` tách nhóm PG khi có DSN; test Local/Mask thật chỉ theo phạm vi lead đã được phép. Test vận hành Windows không có bằng chứng thì CHUA_KIEM. |
| **OCR** | `test_g3_ocr_{2,3,4a,4b,5a,5b}`, `test_cong_ocr`, `test_m9_ocr_hot_folder`; parser/vendor DEMO thật trong package, transport OCR giả. | ABBYY/Hot Folder dưới đúng tài khoản; E1/E2/K1 trên PG cho provenance/lease/ACK. Không suy từ socket giả thành ca vận hành thật. |
| **HD** | `test_g3_hd_{1,2a,3a,3b}`, `test_xs3_hoa_don`, `test_hoa_don_xml` và consumer fixture hiện có; `node tests/g3_hd_2b.cjs`, `node tests/g3_hd_2c.cjs` với Node giả. | Windows Job/socket/profile/ACL, Node/Chromium thật tách riêng; **không gọi cổng thuế** trong G3-GOI. L11/K2 PG chỉ nếu consumer reader/identity bị tác động. |
| **MASK** | `test_g3_mask_{1,5,5b,6}`, test SDK launcher mock; không chạy `run_privacy.py` nguồn thật. | Tài khoản/ACL/Job, stdin/handle khóa, restart/hạn lượt che trên môi trường đã duyệt. Thiếu gate nguồn thì chờ, không đánh dấu đạt. |
| **TRICH** | `test_g3_trich_{1a,1b,3a,3b,4a,noi}`, `test_g3_ai_6`; parser/catalog/pipeline qua AI giả. | TRICH-4b và READY theo lát đã có, đúng scorer/model/catalog/bộ DEMO đã duyệt. Không mở hồ sơ thật hoặc tự gọi AI để lấy số đo. |
| **SDK** | `test_md_2` (wheel hiện có), `test_g3_goi_sdk`, `test_g3_goi_ham_thuan`, `test_g3_goi_ho_so`; `test_g2_33`, `33b` nhóm thuần/mock. Kiểm class/module identity và consumer cũ; version hardcode cũ trong test_md_2 phải được đo trước/sau, không suy là lỗi mới của đóng gói. | Ca tài khoản Windows thật do lead. SDK/Core lease/ủy nhiệm thật trong nhóm PG E1/E2/E3. |
| **DISC / CONTRACT** | Test mới `test_g3_goi_nap`, `test_g3_goi_manager`, `test_g3_goi_doc_lap`; `test_g2_17` và bộ contract hiện có. Meta-schema `$ref` offline; thiếu jsonschema là CHUA_KIEM. | Registry/contract/pins/KT/HoSoChay dưới vai ứng dụng thật ở CSDL test do lead cấp. Không đăng ký vào CSDL Anh đang xem bằng fixture. |
| **ADMIN/UI** | `test_ui_core_3`, `test_ui_engine`, `g2_31b1.cjs`, `g2_31b2.cjs`, `ui_engine.cjs`, `g3_goi_quan_tri.cjs`, WSGI inventory mới; 401/403/503/phiên đổi/phân trang/name-safe. | Admin đăng nhập, đúng năm engine, chi tiết trạng thái/capability, tải lại/restart, ảnh trên browser DEMO do lead. Không tự cài CRM vào 8790. |

Không có `KHO_PG_DSN_TEST/psycopg` trong test G3 trực tiếp đã khảo sát; các skip ở đó chủ yếu schema, nguồn, Windows/Node. Các test Core E1/E2/E3 (`test_g2_32_e1/e2/e3`) có PG opt-in rõ, worker chỉ chạy nhóm thuần. Các test Windows sinh process/socket giả được gọi là kiểm runtime cục bộ, không gọi là kiểm tài khoản thật.

Lệnh mẫu dùng **bộ chạy sẵn có**, chỉ áp cho lát code sau này; `<python-runtime>` do lead cấp, không giả định `python` trong PATH:

```powershell
& <python-runtime> -X utf8 tools/chay_test_theo_module.py . --module test_g3_ai_2 --gioi-han 180 --ra <nhat-ky-ngoai-repo>/ai.json
# Lặp --module cho bộ test tương ứng; không --pg-demo trong worker.
# Bộ chạy bỏ biến KHO_*/PG* của tiến trình con theo cơ chế hiện có.
node tests/g3_hd_2b.cjs
node tests/g3_hd_2c.cjs
node tests/g3_goi_quan_tri.cjs
```

Package test độc lập phải chạy tại cwd ngoài repo với **chỉ SDK wheel + đúng một package engine/dependency ghim**, không thêm repo/src hay engine khác vào PYTHONPATH. Dùng môi trường kiểm gói chuẩn, không sao chép repo/freeze. `tests/test_doc_lap.py` tự tạo dữ liệu DEMO trong RAM hoặc dùng mẫu sạch đi kèm package; không import `tests.test_g2_*` từ repo. Test gốc vẫn ở `T/`, chạy regression qua shim; phần test nguồn phù hợp được chạy qua engine trong package để chứng minh adapter, không chỉ so tên hàm.

Gate độc lập phải có ca import mọi public module/lazy export, nhận việc giả qua SDK, contract vào/ra, hash nguồn thay sai bị chặn; trace/AST cả import tương đối, importlib và CJS require. Quét toàn gói không import `kho_tri_thuc.core`, `m4`, `nguon`, `ha_tang`, `tri_thuc`, hoặc engine khác; chỉ namespace SDK tương thích được phép. Vô tình cùng prefix `kho_tri_thuc` không được coi là SDK.

Mỗi lần chạy ghi đạt/tổng/ERROR/FAIL/skip/treo và ID lỗi. So nền v4 cộng đo trước/sau tại cùng revision/môi trường cho test thêm sau nền; theo dõi skip mới và expectedFailure/unexpectedSuccess, không xóa kiểm để có số xanh. C0/C1 mới còn CHUA_KIEM vẫn chặn phát hành, dù regression không thêm lỗi.

### 5.4. Thứ tự và khóa tệp chung

Chuỗi mẫu kỹ thuật: **01 → 03 → 04/05 → 06 → 07 → 08**. Màn 02 đi cùng 01; 10 phát triển từ mẫu; 11–14 nối API sau gate. Sau mốc mẫu vị trí/bridge 01–03 có thể xếp OCR, hóa đơn, Mask, trích thành nhóm riêng; trích cần OCR/SDK AI nhưng phần nguồn thuần không cần chờ UI cuối. Không giao lại TRICH-4b/READY hoặc MASK-2 nếu lead đã có lát đang làm.

**Khóa SDK và lock không theo số hàng tăng đơn thuần:** hoàn tất các thay đổi SDK ở 04/05/22/34 → build/test wheel SDK version mới → chốt các hàng ghim 09/26/30/37 và SDK phát hành chung → 38. **Riêng OCR-20 theo CD-100 làm theo khung SDK đã gộp, không chờ SDK cuối/34**: ghim nguồn/thư viện và hướng dẫn môi trường sạch; không ghim wheel 1.4.1 candidate. Chốt wheel SDK phát hành ở 34 vẫn thuộc nghiệm thu tổng thể, không chặn OCR xong. Các build trước 34 chỉ là candidate kiểm kỹ thuật, không ghi đè/phát hành wheel SDK 1.4.1 đã có; không ghim engine vào một wheel cùng version nhưng khác nội dung. Như vậy hàng ghim AI không chặn move trích/hóa đơn, tránh vòng phụ thuộc.

**38 → 39 → 40** là cổng đóng gói chung. 39 còn phụ thuộc mốc 28 (Mask manifest), package nguồn Mask thực dùng, ~~façade AI~~ **thay theo CD-111: tích hợp bước Hỏi AI trong chuỗi Core** và các KT áp dụng; nếu chưa đủ, báo mốc một phần, không chốt G3-GOI XONG.

**Tệp chung cứng theo CLAUDE.md §4:** không lát nào ở bảng dự kiến sửa `giao_dien/server.py`, `ha_tang/pg_migrations.py`, `giao_dien/assets/app.js`, `index.html`, `style.css`, `crm_g.*`, `giao_dien/m4.py` hoặc nhóm `m4/*`. Nếu phát sinh nhu cầu đụng các file này, dừng mở whitelist và đánh dấu khóa chung trước giao, không mở rộng ngầm. Đọc/vendor một tập helper M4 ở 32 không phải quyền sửa M4.

**Khóa điều phối bổ sung** dù không nằm danh sách cứng: `C/ui/quan_tri.js` (02→14), `C/chay_core.py` (11), `C/ung_dung.py`/`C/routes_quan_tri.py` (13), builder SDK (03), `ha_tang/primitives.py`/`engine.py` (04), gateway AI legacy (06), root pyproject (38), tài liệu chuẩn (12/40), test AST trích (31→36). Lead giữ một chủ tệp ở một thời điểm, đối chiếu các lát CD-060/SDK đang chạy. Không gọi đây là quyền tự sửa `TRANG-THAI.md` trong worker.

## 6. Điểm lead / Anh cần chốt và rủi ro

| Điểm | Đề xuất / người chốt / điều kiện dừng |
|---|---|
| Đối chiếu CD-070, nền Core và công việc đang chạy | Lead lấy bản chỉ đạo mới và trạng thái lát. Handoff này đã cho phép lập kế hoạch; không cần hỏi lại mục tiêu năm engine. Chỉ xác nhận phần chuẩn mới ảnh hưởng thiết kế trước giao code. |
| Tên package Python | Lead chọn giữ namespace cũ + shim `__path__`; không cần xin Anh đổi tên nghiệp vụ. Phải thử wheel isolated và Core wheel không sở hữu trùng file. Thất bại thì dừng gate SDK/packaging, trình phương án khác có diff cụ thể. |
| SDK namespace / class identity | Lead khóa cơ chế bridge, version SDK mới và kiểm bootstrap/client-Core DTO. Không coi đổi chuỗi import là đủ. Đây là prerequisite kỹ thuật, không hạ kiểm kiểu/lease/quyền. |
| ~~Cổng AI từ trích qua SDK~~ **Bước Hỏi AI trong chuỗi Core** | ~~Lead đối chiếu wire đã duyệt; nếu chưa có operation/binding đúng phạm vi thì trình Anh phần API/contract mới. Lát 34 chỉ port, không giả transport đã có; transport phát sinh phải có handoff nhỏ riêng, có thể làm số lát tăng. Không dùng RPC tổng quát hoặc clone cổng AI.~~ **Thay theo CD-111:** 1b-01 đã duyệt, không xin operation riêng; 34 tách trích chuẩn bị / hậu kiểm, Core điều phối bước Hỏi AI giữa hai bước theo CD-110. Lead chốt contract từng bước và whitelist; phiếu chuỗi sửa vẫn cần duyệt trước mở lát mới. |
| Mask và năm manifest | Lead xác minh adapter/capability nào đã có đủ test, contract nào đã duyệt; Anh chốt contract nghiệp vụ mới nếu cần. Tới lúc đó chỉ hiện Chờ, không tạo capability rỗng/giả. Thiếu gate này thì chưa đạt mục tiêu cuối kỳ. |
| Mask tự đủ đến mức nào | Hai phương án: bundle nguồn sạch/version/SHA và dependency của nó trong gói, hoặc gói engine kèm dependency nguồn cài riêng được quản lý/ghim. Lead kiểm quyền phân phối, tập file sạch, khóa/danh mục ngoài gói; trình Anh nếu “tự đủ” cần ngoại lệ cài riêng. `PHU-THUOC.md` đơn thuần không giải quyết được thiếu nguồn. |
| Inventory API và catalog dự kiến | Lead ưu tiên version quản trị riêng ở endpoint đã có, giữ caller cũ; Anh duyệt nếu vượt chuẩn. Catalog chỉ dữ liệu dự kiến giúp hiện Mask Chờ, không thay manifest/capability. Không duyệt mở rộng thì chờ đủ năm manifest/registry trước nối UI cuối. |
| Thư viện ghim thật | Lead đo đúng Python/Node/Chromium/ABBYY/model thực dùng. Giữ range openpyxl đã duyệt ở root, tạo lock exact của từng engine sau test. Mask crypto50 khác Core49: ưu tiên tách môi trường, không nâng Core đồng loạt. Các số lock nguồn ở §2.4 không phải chứng cứ đã cài/đạt. |
| Nguồn độc lập / license / closure | Lead khóa tập OCR/Mask/Node/Review trước handoff vendor. Dò lazy imports, đường tuyệt đối, resource/catalog. Không có bằng chứng phân phối thì giữ chờ thay vì chép cả dự án. Không sửa nguồn lịch sử để đổi SHA cho qua test. |
| Tài khoản Windows | OCR/Mask/hóa đơn có yêu cầu phiên/Job/ACL riêng. Bản hiện tại còn CHUA_KIEM ở nhiều nhánh; lead chạy ca âm dưới đúng tài khoản, Anh chốt thay đổi hệ thống chưa được phép. DEMO cùng tài khoản không chứng minh triển khai thật đạt. |
| Độ chính xác trích và gate ready | Giữ TRICH-4b/READY hiện hành. Đổi vị trí/package/nguồn có ảnh hưởng hash hoặc parser phải đo lại theo cùng phương pháp khi cần; kết quả thấp hơn gốc dừng báo Anh. Không dùng mock làm số đo. |
| Hash/version/pins và rollback | Manifest/code/source đổi làm đổi hash; lead cấp version/pins mới, giữ drain/ACK và version việc cũ. Rollback về bản đã ghim tương thích, không đổi thư mục đang chạy/ghi đè package cũ. Không migration mới chỉ để chuyển file nếu registry hiện có đủ. |
| Tệp chung / quy mô lát | Lead khóa các tệp §5.4 và whitelist M/N/S; một hàng có nhiều N nguồn cần cân nhắc tách trước giao. **40 là số lát dự kiến với ranh giới tệp sửa đã nêu**, chưa tính các lát tiền đề Mask/~~AI transport~~ **thay theo CD-111: tích hợp bước chuỗi**/giấy phép chưa tồn tại; không cam kết tiến độ khi gate này chưa rõ. |

### 6.1. Điều kiện bắt buộc cho lát nối thật 13 và 39 (Opus review lát 11, 05/11/2026)

Lát 11 đã gộp nhưng chưa bật (chưa nơi nào truyền `thu_muc_engines`). Trước khi lát 13/39 truyền root thật, phải xong:

1. **`__pycache__` trong gói làm lệch hash** (`nap_engine.py`, `_snapshot`): chặn `__pycache__` với lý do rõ ràng và buộc mọi launcher tắt ghi bytecode; không loại `.pyc` khỏi hash.
2. **Root phải trùng `__path__` của shim** `kho_tri_thuc.engines.<ma>`; ghi rõ giới hạn "kiểm đĩa lúc điều phối, không chứng thực mã đã nạp".
3. **Chỉ đọc thư mục gói được ghim** mỗi lượt gọi, không quét lại toàn root.
4. **Ghi log phía máy chủ loại lý do cố định** (lệch hash / lệch danh tính / lỗi đọc), không kèm đường dẫn; xem lại 503 + `Retry-After` cho lỗi không tự hết.

Để sau, ghi vào 13/39: một root cho mọi pin (bật root khi `e_trich_xuat` chưa chuyển thì pin của nó bị chặn); discovery chạy trước kiểm cấu hình và ném `LoiGoi` thay `LoiCauHinh`; thiếu ca manager cho tệp mới/ẩn sau duyệt và junction; `ma_bam_goi` khi đăng ký pins phải dùng đúng `_snapshot` cùng thư mục (gồm `tests/`, README, `.cjs`).

### 6.2. Điều kiện cho lát 33/35 từ lát 32 (05/11/2026)

Vendor Review có hai tệp **rút gọn** (không nguyên byte): `cau_hinh.py` (bỏ khóa Cloud/máy AI/ghi cấu hình, TL 48) và `doc_hop_dong.py` (bỏ chuyển `.doc` qua Word COM/LibreOffice). Khi lát 33 chuyển import sang vendor:

1. Tệp `.doc` sẽ ném `ValueError('CAN_CHUYEN_DOC_NGOAI_ENGINE')`; chuyển `.doc` → `.docx` phải do adapter ngoài engine (tài khoản Windows riêng), không đưa COM vào gói.
2. `.docx` có Track Changes trước đây có thể đi qua Word, nay luôn đọc bằng Python: **phải đo lại độ chính xác trích theo đúng phương pháp cũ** (§6 "Độ chính xác trích"); thấp hơn gốc thì dừng, báo Anh.
3. Catalog `DANH_MUC_THAM_SO.xlsx` không vào git (luật `*.xlsx`); lead quyết cách cấp đúng SHA `05846a2a…1bcd` vào `vendor/review/`.

### 6.3. Điều kiện từ lát 04 (Opus review, 05/11/2026)

**Cập nhật trạng thái theo CD-111:** SDK **1.5.0 đã phát hành cho CRM** (QD-TAM-20261107-11, TRANG-THAI 07/11/2026 21:25). Chỉ CRM ghim 1.5.0; các engine giữ bản đã ghim. Bản CRM chưa giải quyết alias `ha_tang.*` ở mục 3, phải kiểm CRM không pickle/không đọc type hints lớp legacy. Bản phát hành này không chứng minh kênh Hỏi AI/chuỗi hoặc SDK chung cho engine đã nghiệm thu. **Wheel 1.4.1 phía dưới vẫn chỉ candidate, không phát hành/ghim**; DOC-CD111 không đổi SDK. Ghi chú “tới khi lát 34 tăng version” ở mục 1 là điều kiện lịch sử của bản chung, không phải yêu cầu trì hoãn hay làm lại phát hành CRM.

1. **Wheel SDK 1.4.1 candidate:** từ lần gộp lát 04, `tools/dong_goi_sdk.py` gom cả 3 tệp mới vào wheel cùng version 1.4.1 nhưng khác nội dung. Mọi wheel 1.4.1 dựng sau mốc này chỉ là **candidate**: không phát hành, không ghim engine, cho tới khi lát 34 tăng version.
2. **Lát 16 và 22 — bước đầu bắt buộc:** thêm ca subprocess `python -I` import ĐẦU TIÊN lần lượt `kho_tri_thuc.ha_tang.primitives`, `kho_tri_thuc.ha_tang.engine`, `kho_tri_thuc.nguon.trich6_host`, `kho_tri_thuc.core.viec` (mỗi cái một tiến trình sạch), vì `ha_tang.primitives` nay kéo `sdk_core/__init__` → các module `core.*` (rủi ro import vòng khi khởi tạo dở).
3. **Lát 16, 22, 34 — engine chạy độc lập từ wheel:** `__module__` của các lớp SDK mang tên legacy `kho_tri_thuc.ha_tang.*` (bắt buộc vì hash `_chuan_hoa` dùng tên module), nên khi chỉ có wheel thì `pickle` các lớp này và `typing.get_type_hints(KetQuaXuLy)` lỗi. Lát 34 phải bảo đảm wheel có alias `kho_tri_thuc.ha_tang.{primitives,engine}` hoặc engine không pickle/không đọc type hints các lớp này.
4. **Lát 22:** dataclass `Issue` thêm vào `engine_legacy` phải giữ `__module__` gốc như 6 lớp hiện có, nếu không hash có `Issue` đổi.
5. Để sau (lát 34): chuyển chú thích `ENV_GIU` sang `sdk_core/tien_trinh_phu.py`; alias công khai cho `_bat`, `_doc_dong`; rà chính sách riêng dự án trong SDK (`CODEX_NO_DELETE_FILES` trong `ENV_GIU`, `local_business_date` cố định UTC+07).

### 6.4. Giấy phép nguồn — cập nhật OCR theo CD-100 ngày 06/11/2026

- **OCR, lát 17–20: ĐÃ MỞ CHẶN.** Anh đã chốt được chép mã cần thiết để dùng nội bộ, giấy phép **“phần mềm nội bộ, dùng nội bộ tập đoàn”**. Nhận xét thiếu LICENSE của khảo sát 05/11 là lịch sử, không còn là lý do giữ 17–20 chờ. Git xác nhận **17/18/19 ĐÃ GỘP 06/11/2026** (bằng chứng ở §5.2); 20 làm theo khung SDK đã gộp, không chờ SDK cuối.
- **Nguồn OCR:** ưu tiên `D:\GPT\OCR\abbyy-hotfolder`; `D:\GPT\OCR\mask_ocr` chỉ nhánh Tesseract (vie+eng). TUYỆT ĐỐI KHÔNG chép `in\`, `out\`, `jobs\`, `state\` của abbyy-hotfolder (có khóa API — không đọc, không in, không commit), không VietOCR/mô hình riêng/review dual, không xóa mã cũ. Whitelist nguồn sạch do lead khóa trước từng lát bổ sung.
- **FineReader Corporate:** còn chờ Anh xác nhận giấy phép dùng tự động nhiều người qua máy chủ **trước khi chuyển ABBYY lên máy chủ**; không lấy việc này chặn code/mock OCR hiện tại. Thử thật trên máy hiện tại chờ Anh cho phép kết nối tạm có khóa; Anh tự chuyển PDF/DOCX trong `in\`/`out\` vào lưu trữ.
- **Lát 25 (hóa đơn Node):** quyền/closure `build.js`/`config.js` là phạm vi riêng; quyết định OCR không tự cấp quyền cho nguồn hóa đơn. Trạng thái khảo sát 05/11 không dùng để suy trạng thái hôm nay; lead đối chiếu handoff/log hóa đơn trước khi giao tiếp, không mở lại blocker OCR.

### 6.5. Lát 13/13b: phần "nối thật" chuyển sang 13c/39 (Opus review 06/11/2026)

Lát 13/13b chỉ thêm route kiểm kê + provider registry; KHÔNG truyền `thu_muc_engines` (main() không truyền). Bốn điều kiện §6.1 (chặn `__pycache__`, root trùng `__path__` shim, chỉ đọc thư mục gói ghim, log loại lý do cố định ở tầng nạp) **chưa có trong `nap_engine.py`** → mọi việc bật thư mục gói thật thuộc lát **13c** (hoặc 39), không được bật trước khi xong bốn điều kiện. Để sau ghi cho 13c: kiểm quyền kiểm kê dò hết các pháp nhân (hiện dừng ở pháp nhân đầu, hướng sai là từ chối); so `ma_bam_goi` registry với mã băm gói tìm thấy trước khi dùng manifest.

### 6.6. Các việc chuyển từ phiếu e_hoi_ai theo CD-098

**Nguồn:** [CD-098](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md) và [Quyết định cuối e_hoi_ai](QUYET-DINH-CUOI-e_hoi_ai.md) §2–§3 ngày 06/11/2026; **văn bản gốc thắng khi có khác biệt**. Hai nguồn mới được đọc ở thư mục dự án chính do worktree AI-PHIEU chưa có bản cập nhật. Các việc dưới đây **chuyển từ phiếu e_hoi_ai theo CD-098**, ghi lại nội dung/điều kiện và dự toán lịch sử tại mốc `4f180f92`, trừ điều chỉnh đã chốt cho lát 1. **Giờ cũ hết hiệu lực; dự toán điều phối hiện hành của cùng sáu việc chung xem §6.7 và phiếu nghiệm thu tổng thể**, không cộng trùng. Đây là phụ thuộc dùng chung, không còn tính trong 8 giờ bản 1 của phiếu AI.

Quy ước kiểm theo phiếu nguồn: **T** = test thuần nhanh + review chéo Codex; **N** = T + PostgreSQL đầy đủ + Opus cho thay đổi nhạy cảm; **M** = lead thử trên giao diện DEMO/máy được phép. Riêng AI-KENH, CD-098 chốt **N chỉ khi 1b đổi quyền hoặc CSDL**. Worker chỉ chạy thuần/mock, không chạy/dừng PG hay server.

| Lát gốc ở phiếu AI | Việc chuyển sang G3-GOI | Phụ thuộc / điều kiện trước giữ từ phiếu | Giờ ước lịch sử (hết hiệu lực) | Kiểm | Mã / phạm vi |
|---|---|---|---:|---|---|
| 1 → 1a/1b | ~~Kiểm kênh AI chuẩn và nối phần thiếu để engine trích gọi qua Core, đúng quyền và phạm vi~~ **Thay theo CD-111:** hoàn tất bước Hỏi AI trong chuỗi Core; 1b-01 DUYỆT (Anh 21:31), 1b-06 không làm đường riêng, bỏ 1b-07/08 dạng cũ | ~~Lead đối chiếu wire đã duyệt; Anh duyệt API mới nếu cần.~~ Dùng hàng việc/lease chuẩn, nguồn và quyền đã xác minh; không dựng kênh thứ hai. Giữ rào Local/transaction/mất kết nối cho bước Hỏi AI | 4 cho 1a+1b nếu cần (lịch sử, không dùng lại làm tổng) | T; N chỉ khi 1b đổi quyền/CSDL | AI-KENH; xem [xác minh cập nhật](AI-KENH-1A-XAC-MINH.md) |
| 2 | ~~Chốt SDK cuối, tháo việc engine trích import thẳng lõi AI và kiểm tương thích gói~~ **Thay theo CD-111:** tách trích chuẩn bị / hậu kiểm trong chuỗi, không import CongAI; giữ kiểm tương thích gói | AI-KENH; G3-GOI-05/07/22/33 đã gộp; không mở operation riêng. SDK 1.5.0 đã phát hành cho CRM, bản ghim engine chưa đổi | 4 (lịch sử; lead ước lại khi khóa tệp) | T | G3-GOI-34; wheel có alias/identity đúng, kiểm độc lập |
| 11 | Hoàn tất rào chắn nạp thư mục engine thật và quyền kiểm kê | G3-GOI-11/13/13b đã gộp; đủ §6.1 và phần nợ §6.5 | 4 | N | G3-GOI-13c; chặn bytecode, đúng root, đọc gói ghim, log lý do cố định |
| 12 | Chứng minh năm gói chạy độc lập, không dựa vào mã repo hoặc engine khác | G3-GOI-09/20/26/30 **đầy đủ**/37; Mask có manifest hợp lệ | 3 | T | G3-GOI-38 |
| 13 | Nghiệm thu phát hiện→đăng ký→đúng bản ghim→màn quản lý và vòng đời thật | 13c, 38; Windows/ready từng engine đủ | 3 | N + M | G3-GOI-39 |
| 15 | Cập nhật hướng dẫn, ảnh và điều kiện vận hành theo kết quả thật | 39 và bài cuối của các engine | 1 | T | G3-GOI-40, phần cuối chưa làm |
| | **Tổng sáu việc chung — lịch sử CD-098** | Giờ cũ hết hiệu lực, dự toán mới ở §6.7; không cộng trùng mã hiện có | **19** | | |

**Tách lát 1 bắt buộc theo quyết định gốc:**

| Bước | Nội dung và đầu ra | Điều kiện làm / mức kiểm |
|---|---|---|
| **1a — xác minh (lịch sử đã có kết luận)** | ~~Chỉ đọc, đối chiếu kênh/wire/transport đã duyệt để trích gọi AI qua Core đúng quyền và phạm vi. Kết luận đủ hay thiếu, chỉ rõ phần thiếu để lead khóa handoff~~ **Thay theo CD-111:** giữ bằng chứng thiếu contract/runtime/binding trong báo cáo 1a; không dùng thiếu operation riêng làm yêu cầu mở transport | Làm trước; T. Không tự thêm API, transport hoặc đổi quyền/CSDL trong bước xác minh |
| **1b — nối phần còn thiếu** | Chỉ nối phần 1a xác nhận còn thiếu bằng chuẩn có sẵn; không dựng kênh thứ hai, không clone cổng AI hoặc tạo RPC tổng quát. ~~Nếu thiếu API mới thì Anh duyệt trước~~ **Thay theo CD-111:** 1b-01 đã duyệt; 06 không làm đường riêng; 07/08 không còn lát gọi AI giữa chừng, các yêu cầu còn cần áp vào bước Hỏi AI | ~~**Chỉ làm khi 1a thấy thiếu**~~ 1a đã kết luận thiếu; T, **N chỉ khi đổi quyền hoặc CSDL**. Giữ kiểm quyền và tương thích; 1b-01 duyệt không đồng nghĩa triển khai xong |

Quỹ **4 giờ** là ước lượng cũ chung cho AI-KENH, chưa đo; không tự chia thêm giờ hoặc mặc nhiên triển khai 1b. Lead cập nhật phần giờ thực cần sau kết luận 1a. Các hàng 34/13c/38/39/40 là phần tiếp của hàng đã có, không tạo bản sao hay cộng thêm lần nữa vào tổng G3-GOI.

~~**Thứ tự phục vụ bản 1 AI cũ:** [lát 10 — Chạy thử DEMO](PHIEU-ENGINE-e_hoi_ai.md) làm đầu tiên, chỉ Admin, giao diện mẫu song song back end → **1a → 1b nếu thiếu → 34 → lát 3 (G3-GOI-09) → lát 8 sau khi Anh kê khai model → lát 14** (bài cuối khoảng 40 phút).~~ **Thay theo CD-111:** hoàn tất lát 10 và 1b-01/02/04/05/09/CD-106 theo phụ thuộc → lát 3 → 8 → 14. Model đã kê khai theo CD-106; chỉ còn thử kết nối/model thật. 34 tách trích để tích hợp chuỗi, không là tiền đề operation riêng của Hỏi AI. Lát 3 vẫn do phiếu AI theo dõi, tương ứng hàng 09 ở §5.2, không giao trùng. Tổng **19 giờ là dự toán lịch sử CD-098, hết hiệu lực; quỹ chung hiện hành 22 giờ tại §6.7**. Toàn phạm vi dự toán Hỏi AI so mốc 21:25 ước lại **36–44 giờ** ở [phiếu AI §2.1.1](PHIEU-ENGINE-e_hoi_ai.md#211-việc-còn-lại-và-ước-lại-giờ-theo-cd-111), không cộng thêm quỹ chung. Bản 1 chỉ thực hiện gate Local; không bắt chờ nghiệm thu Cloud hoặc đủ năm gói.

**Các gate chung vẫn giữ:** 13c theo §6.1/§6.5 → 38 theo đủ gói/nguồn/contract → 39 → phần cuối 40. Mask thiếu thì chưa nghiệm thu đủ năm gói; đây là ranh giới đóng gói chung, không mở Cloud ở bản 1 AI. SDK wheel 1.4.1 vẫn chỉ candidate theo §6.3; lát 34 và việc chốt phiên bản cuối do lead xử lý trong handoff code riêng.

**Không chuyển sang G3-GOI:** lát 7 gộp vào bài test cuối AI; AI-3, lát 5+9 gộp, lát 6 và AI-DINH-TUYEN thuộc bản 2 phiếu AI. Bỏ AI-PROMPT: prompt thuộc gói module, mỗi function một prompt có mã/phiên bản, engine kéo đúng prompt; thiếu prompt từ chối có lý do. Admin module sửa prompt của module mình, Admin Core sửa tất cả, việc sửa làm trong module. Vector `ai.nhung_vector@1` thuộc e_tra_cuu; hàng chờ/thông báo thuộc CE/HC. Bảy câu schema Mask thuộc phiếu Mask.

### 6.7. OCR theo CD-100: engine độc lập trước, tổng thể sau

**Nguồn:** [CD-100](../../46-chuyen-doi-dieu-phoi/CHI-DAO-TU-ANH.md) cuối tệp chỉ đạo và [Quyết định cuối e_ocr](QUYET-DINH-CUOI-e_ocr.md) §1–§5, **văn bản gốc thắng khi khác**. Worktree OCR-PHIEU chưa có hai nguồn mới: đã đọc CD-100 từ `hop-nhat-20261023`, quyết định gốc từ thư mục dự án chính, không chép thêm nguồn vào worktree.

**GIỮ** lát gốc 1/G3-GOI-17, 2/-18, 3/-19 (**ĐÃ GỘP 06/11/2026**), 6/-20 và 9/OCR-WIN-NT. **THÊM** các lát dưới đây, dùng tối đa mã sẵn có; đây là kế hoạch, chưa phải bằng chứng đã triển khai. Bảng 40 hàng cũ không tính các mã mới này; lead khóa tệp riêng trước giao, không tự mở whitelist từ phiếu tài liệu.

| Lát thêm/giữ | Nội dung cần có | Phụ thuộc / kiểm | Giờ còn lại — ước tính |
|---|---|---|---:|
| OCR-NOI | Lớp chữ PDF ABBYY “text under image” → cấu trúc chung mask_ocr; không OCR lại ảnh nền | Sau 1; T | 3 |
| OCR-KETNOI | Máy chủ Core gọi ABBYY máy hiện tại, có khóa, chỉ địa chỉ máy chủ Core; khóa lưu két bí mật, không git/log/chat, log không khóa/đường dẫn | Sau 1; N; code/mock trước, không tự mở mạng/tường lửa hay đọc/ghi két | 4 |
| OCR-VUNG | `ocr.trich_vung@1`, dùng lại `crop_quad`, trả chữ + cờ nghi ngờ | Sau 1; T | 3 |
| OCR-CHON | ABBYY trước; tự chuyển mask_ocr khi hết **5.000 trang/30 ngày**, máy ABBYY tắt, ABBYY lỗi/quá giờ. Kết quả ghi nguồn; màn Quản lý engine có đã dùng/còn lại + trạng thái máy ABBYY | Sau OCR-NOI; T + M, UI song song back end | 3 |
| 6 / G3-GOI-20 | Ghim nguồn/thư viện, hướng dẫn môi trường sạch theo khung SDK đã gộp | Sau nền và các bổ sung trên; T; **không chờ SDK cuối**, không ghim candidate §6.3 | 2 |
| 9 / OCR-WIN-NT | ABBYY thật trên **máy hiện tại (tạm)**, PDF DEMO; chuẩn bị `.cmd` ASCII + hướng dẫn theo CD-065/087 | Sau 6; N + M; **chờ Anh cho phép kết nối tạm có khóa**, không tự đổi tường lửa/mạng | 3 |
| OCR-MAY | Bộ DEMO giả + đúng **9 ca** quyết định gốc §5 qua màn Chạy thử DEMO/Quản lý engine, chỉ Admin, trình duyệt thật theo CD-099; mỗi ca ảnh + log, phút thực tế | Chạy cuối, **hằng ngày và trước báo xong**; T + M | 4 |
| **Tổng OCR còn lại — ước tính mới** | 10 lát = 3 đã gộp (0 giờ làm lại) + 7 còn lại | Gồm lần OCR-MAY đầu, không tính chờ/sửa lỗi/lượt chạy lặp | **22** |

**Thứ tự §3 quyết định gốc:** **1 → 2 → 3**; song song sau 1: **OCR-NOI, OCR-KETNOI, OCR-VUNG**; **OCR-CHON sau OCR-NOI**; **lát 6 → lát 9 → OCR-MAY**. Lead quyết số lát song song khi bắt đầu; phạm vi đã chốt, không đứng chờ duyệt lại. Giới hạn kết nối thật chỉ chặn phần cần phép, các phần được phép vẫn làm.

**BỎ** lát 11 thử qua CRM, thay bằng OCR-MAY; bỏ VietOCR/dual/màn duyệt điểm khác nhau. **CHUYỂN** lát 4 (AI-KENH), 5 (G3-GOI-34), 7 (13c), 8 (38), 10 (39), 12 (phần cuối 40) và bài **60 phút qua CRM** sang [PHIEU-NGHIEM-THU-TONG-THE.md](PHIEU-NGHIEM-THU-TONG-THE.md), ghi **“chuyển từ phiếu e_ocr theo CD-100”**. Làm sau, **không chặn OCR xong**; các mã chung dùng lại §6.6, không giao/cộng giờ trùng. **Mọi ước giờ cũ của phiếu OCR hết hiệu lực**: dự toán mới cho cùng sáu việc chung **22 giờ**, thêm bài CRM **1 giờ**, tổng **23 giờ — ước tính**, thay quỹ 19 giờ lịch sử khi điều phối cùng phạm vi; không cộng 19 + 22. Giờ engine OCR 22 tính riêng; không cộng lại chúng khi tổng hợp các phiếu.

**ĐỂ SAU** khi xong engine: `ocr.trich_bang@1`, hóa đơn giấy, bảng kê, chuyển ABBYY lên máy chủ. Khi chuyển máy chạy lại OCR-MAY **ca 2, 5, 8**. Ngưỡng đúng/sai của nhánh dự phòng do Anh chốt sau lần đo đầu ca 4, không tự đặt ngưỡng. Phần chưa kiểm ghi rõ, không báo đạt thay.

**Việc chờ Anh (☑ đề xuất, không chặn code):** ☑ xác nhận FineReader Corporate cho tự động nhiều người trước chuyển máy chủ; ☑ cho phép kết nối tạm có khóa trên máy hiện tại trước lát 9 (lead chuẩn bị `.cmd` ASCII + hướng dẫn); ☑ **Anh tự chuyển** PDF ở `abbyy-hotfolder\in\` và DOCX ở `out\` vào lưu trữ. Worker không mở các thư mục bị cấm. Lát OCR-PHIEU chỉ sửa ba tài liệu, không tạo/chạy `.cmd`, không đổi SDK hay hệ thống.

## 7. Tiêu chí hoàn thành và báo cáo của lát khảo sát

G3-GOI chỉ hoàn thành khi đủ năm thư mục có manifest hợp lệ, mã/adapter/nguồn ghim/contract/tests/docs/lock; package độc lập không đọc repo/module/engine khác; Core đọc manifest từ root cấu hình, đăng ký/ghim đúng và giữ runtime/KT; test đường cũ vẫn dùng cùng implementation; Quản lý engine hiện đúng năm dòng với nguồn dữ liệu và trạng thái trung thực. Mỗi capability ready phải có bằng chứng tương ứng, các ngoại lệ/tài khoản còn chờ ghi rõ; không đánh đồng “đã đóng gói mã” với “được chạy thật”.

**Ranh giới CD-100:** tiêu chí trên là nghiệm thu đóng gói/tổng thể, thực hiện sau. OCR có tiêu chí engine độc lập ở [phiếu OCR mục 5](PHIEU-ENGINE-e_ocr.md); SDK cuối, năm gói, chuỗi CE/HC hoặc CRM còn thiếu không chặn OCR xong. Chỉ báo engine đạt khi đúng 9 ca OCR-MAY có bằng chứng; không suy rằng tổng thể đã đạt.

Mốc nghiệm thu UI do lead: `http://127.0.0.1:8790` nếu còn là cổng được cấp, đăng nhập theo hướng dẫn DEMO có sẵn → Quản trị Core → Quản lý engine → chi tiết từng engine; ảnh mốc fixture và mốc API thật riêng, ghi giờ/nguồn dữ liệu/lý do chờ trong `XEM-GIAO-DIEN-CORE.md`. Chưa mở/quan sát được thì ghi CHUA_KIEM, không tạo ảnh hoặc kết quả giả.

**Kết quả G3-GOI-KH:** chỉ tạo tài liệu này; không sửa/di chuyển mã, không commit. Khảo sát static xong trong phạm vi đọc được. **Test runtime: 0 chạy; lỗi mới so nền: chưa đo, không kết luận xanh.** Kiểm tài liệu: đường dẫn nguồn, số tệp, ranh giới S/M/N, UTF-8 và phạm vi git diff. Các điều kiện cần lead/Anh chốt nằm §6; không có hành động triển khai được thực hiện từ kế hoạch này.
