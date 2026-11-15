# Nguồn của gói Đối chiếu

## DC-12 — nguồn và lock offline, 15/11/2026

Không thêm dependency, không tải mạng. Runtime lock giữ nguyên pin/hash
được cấp: SDK 2.2.0 cài wheel repo riêng, Pillow 12.3.0 theo lock OCR;
thư viện chuẩn Python theo PSF. Băm wheel SDK
`0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`
khớp `SHA256SUMS.txt` và lock. Hai hash Pillow ở mục DC-8 bên dưới;
chưa có wheel Pillow trong repo. Mười hai gói test/QA ghim phiên bản
trong `tests/requirements.lock` nhưng chưa có wheel/hash được cấp.
Công cụ máy sạch từ chối mã 2 trước khi tạo venv; không bịa hash wheel.

Font Roboto, Apache 2.0 và NOTICE giữ nguyên theo DC-9. Detector
`sua_tay.py` viết trong repo, không chép model/detector ngoài; băm hiện
hành tại bảng DC-S22-SHA. Từ điển và raster trong tests tự tạo, chỉ DEMO,
không thay nguồn từ điển/detector vận hành được duyệt. Bộ đáp án DC-12,
harness/test và ba công cụ offline viết mới, tái dùng fixture nội bộ
DC-2…11 chỉ trong tests. Không cấp phép mới cho nguồn bên thứ ba.

Nguồn thuật toán chép có sửa: ba đường Trích xuất ở mục DC-2 bên dưới,
băm nguồn gốc và phạm vi chuyển đã ghi tại đó. Hai mẫu NGAN-0 và bốn
schema sao nguyên từ `_chung`, quyền dùng nội bộ theo phiếu; bảng băm
hiện hành bên dưới và test so SHA-256 LF kiểm cả nguồn lẫn bản chép.
SDK nội bộ không có trường giấy phép trong METADATA; cần lead xác nhận
quyền phân phối, không suy thành giấy phép nguồn mở.

<!-- DC-12-METADATA:DAU -->
| Dependency | Nguồn khai trong metadata | Giấy phép | SHA-256 METADATA đã cài |
|---|---|---|---|
| `kho_tri_thuc_sdk==2.2.0` | wheel nội bộ trong repo | Nội bộ; chưa khai SPDX | `6a8ea42619a68c4750b0f17aa1e4b1a2d80270b2ceb6eb7d24fd2f142cea3040` |
| `Pillow==12.3.0` | https://python-pillow.github.io | MIT-CMU | `2c4378001803cfac65809a50722d46e0da4ce8061e717f103e5d52734bab30f5` |
| `pytest==9.1.1` | https://docs.pytest.org/en/latest/ | MIT | `c5d032518012789cabc870d46589aca3aeda36cf9fa4399ee88bda3d10438451` |
| `packaging==26.3` | https://github.com/pypa/packaging | Apache-2.0 OR BSD-2-Clause | `70fdb89fc4d4a9a043bf7372b8972bcc883fddff34ab55e9cf80d73875384763` |
| `pluggy==1.6.0` | https://github.com/pytest-dev/pluggy (mô tả trong METADATA) | MIT | `7438c35ee25a095eb7416f84b461c2d74425c5e734ad54c3912453c65244e01c` |
| `pygments==2.21.0` | https://pygments.org | BSD-2-Clause | `1dde075570136774c706bf0009183a793fe0ee262e4a5590cc6eff8453eedd43` |
| `iniconfig==2.3.0` | https://github.com/pytest-dev/iniconfig | MIT | `40d773f84e4e112f495bbf4f1be9cbd2d456c0aeb6ef5311f75d1bf322f2165b` |
| `colorama==0.4.6` | https://github.com/tartley/colorama | BSD-3-Clause (LICENSE có sẵn) | `7baed29eb50c3b29bdb33ff84e3177bf1bc05784f7685ecdcaa4471c7dd810cc` |
| `jsonschema==4.26.0` | https://github.com/python-jsonschema/jsonschema | MIT | `05b189866ca98a96da3934bf6b83687ced3ff85325273b77e16b705f6d8b26d2` |
| `attrs==26.1.0` | https://github.com/python-attrs/attrs | MIT | `4cd40e690f23bf37cbcad34efd6758e062df1df07c86833f7e3ce95bf1fa38cc` |
| `jsonschema-specifications==2025.9.1` | https://github.com/python-jsonschema/jsonschema-specifications | MIT | `35abd41757f32b4ea24756920ded47b70173d77cbc052a5a6d3ab583b2e8d89d` |
| `referencing==0.37.0` | https://github.com/python-jsonschema/referencing | MIT | `c93b00e6ab1524fd60848376604c189a114374776475c25a31d57be47b29de6a` |
| `rpds-py==2026.6.3` | https://github.com/crate-py/rpds | MIT | `e9deba3569d39352c663fd09d01d53a649c8ab2c28de1c37e80b3e2beaf84926` |
| `pypdfium2==5.13.0` | https://github.com/pypdfium2-team/pypdfium2 | BSD-3-Clause, Apache-2.0, dependency licenses | `77230dd502a7693f2a713566263247dd13f8749b5677f5050f22d19bbe37ceba` |
<!-- DC-12-METADATA:CUOI -->

Bảng metadata chỉ đọc từ distribution có sẵn, không truy cập các URL.
Băm METADATA **không phải băm wheel**, không được dùng làm hash pip.
Giấy phép native kèm Pillow/pypdfium2 theo LICENSE/NOTICE distribution;
engine không vendor thêm chúng. pypdfium2 chỉ QA PDF tùy chọn, không
import runtime. Node 24.18.0 chỉ công cụ test UI, không đóng gói.
Không đưa font máy, model Local hoặc từ điển thật vào gói; nguồn chưa
cấp không được thay bằng fixture rồi coi là đã kiểm.

## DC-11 — 15/11/2026

- `loi_ocr.py`, `ui/loi_ocr.js`, SQL 003 viết mới theo phiếu DC-11;
  dùng lại lõi DC-7/DC-10 tại chỗ, chỉ SDK 2.2.0/thư viện chuẩn. Không
  thêm dependency, nguồn tải mạng, từ điển/font/model thật hoặc Cloud.
- DC-11-CH thêm schema ngưỡng không mặc định và giữ ngưỡng đã duyệt trong
  màn cấu hình cũ. Màn mới chỉ đọc, không API quản trị chưa phát hành.
- Chỉ tái dùng fixture `DEMO-tu-dien-dc7.json` trong tests: Q14/giấy phép/
  phê duyệt và ngưỡng đều giả để kiểm giao thức, chưa thay nguồn sạch
  lead cần trình. Hai mẫu NGAN-0 giữ nguyên và so băm LF trong tests.
- Băm các tệp mới/đổi và kiểm kê bytes thực được cập nhật ở bảng hiện
  hành bên dưới và `sql/kiem_ke.json`. Chưa chạy migration trên CSDL thật.

## DC-10 — 15/11/2026

- Hai màn JS và `xac_nhan.py` viết mới theo phiếu DC-10, Q01–04 đã duyệt
  chiều 15/11; `chay.py` chỉ thêm adapter nội bộ không decorator/API giả.
  Dùng SDK 2.2.0 + thư viện chuẩn, không thêm dependency/mạng/Cloud.
  UI dựng chữ bằng DOM/textContent, font kế thừa, bố cục hai cột chuyển
  một cột ở màn hẹp. Node 24.18.0 chỉ kiểm UI giả không mạng.
- `tham_chieu_ngan_0/ngan.py` và `cau_hinh.py` chép nguyên mẫu
  `_chung/mau-ma/` theo yêu cầu lead, chỉ đối chiếu LF và kiểm RAM trong
  phần DC-10-NGAN0, không import vào runtime SDK 2.2.0. Test so SHA-256
  sau chuẩn hóa CRLF→LF; mẫu gốc không sửa. Bảng SHA hiện hành ở cuối.
- `sql/002_xac_nhan.sql`: viết mới, chỉ ALTER thêm ba cột trong schema
  `eng_e_doi_chieu`; không SQL lúc chạy. Gói 0.8.0 chưa phát hành, dữ
  liệu phiên bản 2. Migration không thay cho ACL hoặc kiểm toán bền.
- `KHAI-SDK-2.1.json` là bản khai màn/quyền **mới** đang đề nghị, không
  khôi phục khai ngăn/cấu hình tạm của DC-S22. Các adapter C-DC-03/04
  được mô tả riêng tại `../../docs/DC-10-CONG-CORE.md`, chưa có binding
  thật. Đã kiểm bằng Core giả (CoreGia); ngăn RAM không chứng minh bền.

## DC-9 — 15/11/2026

- `tong_hop.py`, `bao_cao.py` viết mới trong lát DC-9, `chay.py` mở rộng;
  chỉ SDK 2.2.0, thư viện chuẩn và Pillow 12.3.0 đã ghim ở DC-8. Không
  cài/tải thư viện mạng, không thêm dependency runtime. PDF 1.4 gồm trang
  ảnh JPEG do Pillow dựng/nén; writer xref ghi offset byte thực trong RAM.
- `tai_nguyen/font/Roboto-Regular.ttf`: chép nguyên tài nguyên phân phối
  offline của **CustomTkinter 5.2.2**, đường tương đối trong distribution
  `customtkinter/assets/fonts/Roboto/Roboto-Regular.ttf`. Không dùng font
  hệ điều hành, không dò thư mục font Windows hoặc đường cấu hình máy.
  Nguồn upstream: <https://github.com/TomSchimansky/CustomTkinter/tree/v5.2.2/customtkinter/assets/fonts/Roboto>;
  nguồn họ font: <https://github.com/googlefonts/roboto>.
  Metadata font: **Roboto Regular, Version 2.137; 2017**, Copyright 2011
  Google Inc. All Rights Reserved.; `nameID=13` ghi **Apache License 2.0**,
  `nameID=14` ghi <http://www.apache.org/licenses/LICENSE-2.0>.
  Font nguyên bản **168.260 bytes**, SHA-256
  `319cff6e7a31f0f2a41c475dca42890aa5d19fe16017e2290f8c1d4e14f76481`.
  Giữ copyright/metadata; đóng kèm `NOTICE.txt` và toàn văn Apache 2.0
  (`LICENSE-APACHE-2.0.txt`, bản chuẩn có sẵn offline từ pip vendored
  packaging). Không thêm CustomTkinter/pip/reportlab vào runtime engine.
- Engine kiểm băm font và cmap; NFC khi hiển thị dấu tổ hợp. Ký tự ngoài
  cmap được biểu diễn rõ `[U+XXXX]`, không hiện ô vuông hoặc bỏ ký tự;
  JSON giữ nguyên mọi Unicode/bytes nguồn. Test tiếng Việt không có fallback.
- QA render dùng **pypdfium2 5.13.0** có sẵn offline, chỉ trong công cụ
  `tests/kiem_pdf_dc9_demo.py`, không trong engine/pytest bắt buộc.
  Bộ test tạo dữ liệu DEMO bằng CoreGia; fixture upstream giả để kiểm
  bảng quyết định không phải số đo detector/OCR. Không gọi Cloud.

## DC-S22 — 15/11/2026 · 0.7.1 chưa phát hành

Chuyển cổng ngăn/cấu hình theo SDK 2.2.0 và mẫu `e_demo_ngan` trong repo;
SQL viết mới cho đúng bốn bảng đã khai, chỉ CREATE TABLE trong schema
`eng_e_doi_chieu`, không kết nối CSDL lúc chạy. Không thêm dependency
runtime ngoài SDK 2.2.0 và Pillow 12.3.0 đã ghim từ DC-8. Wheel SDK có
SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`,
khớp `docs/goi-gui-engine/sdk-2.2.0/SHA256SUMS.txt`.

`ngan.py`, `cau_hinh.py`, `KHAI-SDK-2.1.json` lưu nguyên bytes tại
`e_doi_chieu/LUU-TRU/DC-S22/`, không còn thuộc gói chạy; không tiếp tục
test so băm với mẫu NGAN-0. Bốn schema loại dữ liệu chung vẫn giữ nguyên
và được test so SHA LF. Khuôn DC-6 thêm `$comment` theo §8 loại chung,
khớp profile DC-6 trong Hỏi AI-12; không đổi schema chung/API hoặc loại.

Test dùng ngăn/cấu hình của CoreGia 2.2.0, provider Local/nguồn DEMO.
`tests/ngan_demo.py` chỉ giao việc DEMO qua SDK để sửa ngăn giữa các lượt,
không tự triển khai kho/CAS. Mã Hỏi AI AI-11/AI-12 chỉ nạp trong test
tích hợp từ nội dung `origin/main` `12ed8db`; runtime không import engine
khác. 0 Cloud; chưa đo model/OCR/Core thật. Dependency test đã ghim tại
`e_doi_chieu/tests/requirements.lock`; môi trường offline dùng dependency
đã cài đúng bản qua system-site-packages, không tải mạng.

`quy_tac.py` thêm `functools.lru_cache` của thư viện chuẩn cho tối đa
128 cụm tiền trong cùng lượt quét, không đệm cấu hình/lưu bền. Giữ ngưỡng
test hiệu năng cũ và kiểm từng vị trí có bản giá trị riêng, không chia sẻ
dict đầu ra. Bộ kiểm đầy đủ sau chuyển: 898 passed, 0 skipped.

Bảng sau là SHA hiện hành sau CRLF→LF; các bảng lát cũ là lịch sử.
`sql/kiem_ke.json` dùng bytes/SHA thực của mọi tệp gói, gồm NGUON,
trừ chính kiểm kê. Tệp Word DEMO giữ nguyên bytes, không chuẩn hóa.

<!-- DC-S22-SHA:DAU -->
| Tệp hiện hành | SHA-256 LF |
|---|---|
| `.gitattributes` | `36f5046d7b9e6c15c3d77263f4918fa7997bebfbf79f3a4f3b954da607cd4eed` |
| `cau_hinh.schema.json` | `e38e7414afacb2b1abc8fa1e01e28c130213686d79ea3f3d71d7873f5ab39b87` |
| `CHANGELOG.md` | `7ce1aeb3b742ffdc83f5a4ffaa38b084eeedc14d06ec91bcba140f3440950d0d` |
| `demo/DEMO-ban-chot.docx` | `e086e49c1dfad0cdfc702ab141a9de6123cbd123e4c7110df975b673e194bcaa` |
| `demo/README.md` | `c55d1d9bb7381dd821b4a4c1fea1b129af974ae3c7f83acf35de6ef45fac64bf` |
| `e_doi_chieu/__init__.py` | `a427fe739dab3a98c108b79f40f7a53328d504300979b71ccc900892064948b3` |
| `e_doi_chieu/anh.py` | `2358268bca79589385e904909ab32d5bdaa43d3ebf5097776698e91a0c5f7dbe` |
| `e_doi_chieu/bao_cao.py` | `9cc4c1941d0512b8e97d1f7af845f029edcbe852c1e1b3fb3bbf20f33b38b965` |
| `e_doi_chieu/can_chinh.py` | `39b084ae09adc8785051fbbb95238281b0f305e4a5370f5856c65263f0ada76e` |
| `e_doi_chieu/cau_truc.py` | `ddde14383f97bf5c1fa1a2161aed7db8f3ea1e36004c16350a2db52018c2d333` |
| `e_doi_chieu/chay.py` | `13bd8314c7247bbc545de5d3566d26abad4271e7ba840314b1aa71bd7f899a4f` |
| `e_doi_chieu/chuan_bi_ai.py` | `82b8f8d2363ee3746aed14e1cbf4c1c4a290c7d6b92cfcd46eac456aab7de8ae` |
| `e_doi_chieu/chuan_hoa.py` | `a427053b5465450e838c274589d7d4b91fa86f69817414854a16cce2028bfe1b` |
| `e_doi_chieu/doc_docx.py` | `7e63532c8ae2358ccc1b90a1bb65cb85e83c5c743fb3d8d9287fb2ed3cce3945` |
| `e_doi_chieu/hau_kiem_ai.py` | `a9dab45b42db79b3779ceabd903602a7a63eb2493d9f344e12db3059a715e030` |
| `e_doi_chieu/ho_so.py` | `13441efae45cca90d2cbc2c4dabd7f5f4c4e2e2240ce96f12cd25ced1531e0e0` |
| `e_doi_chieu/lech_dau.py` | `6c82cf3d41622ca038a0ea9ab5df12edb2b93224a1e99b7c07a37a32e81ec26f` |
| `e_doi_chieu/loi_ocr.py` | `0febad2a5274f63853827cfbf05596d7f280a28ea4124b62913788ee96b87e43` |
| `e_doi_chieu/quy_tac.py` | `e937c98d97a31a9f6f8e8e79e68a0c76efdda5fb5c0880a19418e81e08138a76` |
| `e_doi_chieu/so_chu.py` | `f6045c6494422bb842c638d90f378e8e95d66ad3d0996fff9d365814779f5038` |
| `e_doi_chieu/sua_tay.py` | `29a63bdfa9306c748a6a6bc4808f85206dfc69e9f94d816c52c6a22d369528d0` |
| `e_doi_chieu/tien_chu.py` | `d0aba9de44269b62fe1a1506780b3a3459c1a462a9fc9988b502ad6a8d48224d` |
| `e_doi_chieu/tong_hop.py` | `c619b98e82b4db5887ad06d0058877425d2132edcff1428c9533fc855f71cfd0` |
| `e_doi_chieu/tu_dien.py` | `4ac5ec887ae9a732f2a69675ae69b9b28801a583b4310cb5986830e8ca874481` |
| `e_doi_chieu/vi_tri.py` | `0efdfb41d3cc56e857ab74e49c8f8cbaa7f0d075267581f60ffb33232d148a97` |
| `e_doi_chieu/xac_nhan.py` | `f56a2ce8328332c9411ebfd41a7847534fef415c55f7239cafeb14c76120613a` |
| `engine.json` | `7a08e144ea442c148c38d37663005c0eba397b1f549a156e123fc5b09703d139` |
| `ho_so_doi_chieu.schema.json` | `9114bf674c4d16189050eb3130453838b7bc1c2c22f6208a05e866df84adf776` |
| `KHAI-SDK-2.1.json` | `bc9806d3c4feb276f2a629d6ad63caaf57a2360de5225e9ce49555b802b735ca` |
| `README.md` | `3f6b9d01f66269b04c00d7e9aab760173aa861c51075bf704929ba9592d77d18` |
| `requirements.lock` | `68ddd023dd5f4610cea4f5aa63fbe91a9915c3b0fde10661edecb430e9f4bc4f` |
| `sql/001_tao_ngan.sql` | `e71934770ec9664fa902782bd849a4a1d375e428602cff959691154ddb5f5f8e` |
| `sql/002_xac_nhan.sql` | `276c8e0b24218e5396a27d6f2a2a678be5732b7e9e4890cfd5cf3bbb0eb0f540` |
| `sql/003_hoc_loi_ocr.sql` | `20ed90ae25b46186083335537607afe2dc75e80e0cbd074432f247c3b7fe7efa` |
| `tai_nguyen/font/LICENSE-APACHE-2.0.txt` | `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` |
| `tai_nguyen/font/NOTICE.txt` | `fcf0001da8c1ec45413c63edac12b85680d4ef0311559c15350a190dc810e92f` |
| `tai_nguyen/font/Roboto-Regular.ttf` | `319cff6e7a31f0f2a41c475dca42890aa5d19fe16017e2290f8c1d4e14f76481` |
| `tham_chieu_ngan_0/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |
| `tham_chieu_ngan_0/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `tra_loi_ai.schema.json` | `5ff270d3b997c5d5498be0f2b29cd851ad06cf8dbff81dab571b8eaaf97ca76f` |
| `ui/cau_hinh.js` | `a3afcf83fb4f97ecf8838113776446e170904251d2ad2788d087986304b0bdbc` |
| `ui/ket_qua.js` | `1c46bacb03091f777e7c7930bb511e160c5e11a9492680d0a87a65f4450030be` |
| `ui/loi_ocr.js` | `cab2e90b69e256d910039989e794d5584443b03d34a145bb060f471b3192dc7c` |
| `van_ban_tai_lieu.schema.json` | `81a4e0852004e3fac5ee7e2ed23d07b5d704decaeecc2bce170dafd56042b977` |
| `yeu_cau_ai.schema.json` | `36933e5ec293ff8eed64350a47df37e719f1fadd615e67b37b5a3891b7756d4d` |
<!-- DC-S22-SHA:CUOI -->

## DC-7 — 15/11/2026 · 0.7.0 chưa phát hành

Viết mới `lech_dau.py`, `tu_dien.py` theo DC-f/DAC-TA §4 và phiếu
DC-7; `chay.py` nối sau so DC-5 và hậu kiểm DC-6. Chỉ ba tệp runtime,
không đổi validator/lõi DC-5/DC-6, API hoặc schema chung. Dùng thư viện
chuẩn/SDK 2.0.0 đã ghim, không thêm dependency hoặc mã engine khác.
Nguồn từ điển thật có giấy phép **chưa được cấp DC-Q14**. Không tải mạng,
model, từ điển hoặc bộ OCR. Pillow đang ghim từ DC-8 chỉ được helper test
dùng tạo raster/crop DEMO; runtime DC-7 kiểm ảnh bằng hàm đã có.

`tests/fixtures/DEMO-tu-dien-dc7.json` tự soạn: sáu cặp có nghĩa cùng
một chứng nhận lỗi DEMO hơp→hợp. Không chứa tên/hồ sơ thật, không là từ
điển tiếng Việt đầy đủ hoặc nguồn vận hành được duyệt. Không đóng gói
fixture vào runtime. Test tải lên CoreGia, ghim bytes/phien_ban/nguon/
giay_phep trong bộ và mã/băm trong cấu hình Ngan; không fallback tự nạp.
Không có mục không đủ chứng minh vô nghĩa, kể cả AI/OCR cùng đồng ý.

`tests/demo_lech_dau.py` và `tests/test_dc7.py` tái dùng bộ DEMO DC-3…6,
CoreGia + adapter quyền/manifest OCR giả; tất cả tọa độ/kết quả/ảnh phục
vụ kiểm giao thức. Không đo quality OCR/Local AI/scan thật. Adapter chỉ
ở tests, không được nhập vào runtime. Ngưỡng trong bộ test có nhãn DEMO;
DC-Q15 và contract OCR vùng C-DC-05 vẫn mở. Hai mẫu NGAN-0 và bốn schema
nguồn/bản chép giữ nguyên, được test so băm LF trong bộ tổng.

Đã kiểm bằng Core giả (CoreGia). Quét token 500.000 ký tự: chuỗi lặp
tiếng Việt/tiền (80.000 token) **0,1363 giây**; một token dài **0,0911
giây**. Test hủy giữa token dài và ngưỡng <2 giây đạt. Chỉ số đo riêng
bộ quét trên máy này, không là tốc độ toàn tuyến hoặc quality OCR.

SHA-256 UTF-8 sau CRLF→LF (bảng lát cũ phía dưới giữ làm lịch sử):

| Tệp | SHA-256 LF |
|---|---|
| `e_doi_chieu/lech_dau.py` | `73fa13f993102c1f55666489b2b8c4cd890e58478882308ee2649e55107d4d3d` |
| `e_doi_chieu/tu_dien.py` | `4ac5ec887ae9a732f2a69675ae69b9b28801a583b4310cb5986830e8ca874481` |
| `e_doi_chieu/chay.py` | `2be74ff56cf10f4d3dcaa7bb656173ef0ef504a9fb80302b42b9697baa0a6d92` |
| `engine.json` | `4242039b8140e88eadf448b00899336cefa38a08ceecc7a6121e14e500842a4c` |
| Repo: `tests/fixtures/DEMO-tu-dien-dc7.json` | `099578cf973f00a5b4bb07d314717cbfc6a86424684dcd763e1a5cf57433ca26` |
| Repo: `tests/test_dc7.py` | `c246e51809fbc9c9f148bad1c9d370a63aefdcc6443b4ca02ce943d72a3e4063` |

## DC-6 — 15/11/2026 · 0.6.0 chưa phát hành

`chuan_bi_ai.py`, `hau_kiem_ai.py` viết mới theo phiếu DC-6, DAC-TA §5.2,
API-ENGINE-v1 và loại dữ liệu chung §2.2–2.3. `chay.py` chỉ thêm khối
đăng ký/import hai handler. Tái dùng nội bộ kiểm tệp/băm/JSON/phong bì
của `ho_so.py`, edit script/giới hạn của `so_chu.py`, kiểm bất biến/quy
tắc của DC-5. Không sửa các lõi đó, DC-8, mã Core hoặc `ma-nguon/`.
Không nguồn ngoài/dependency mới; chỉ thư viện chuẩn và SDK 2.0.0.

Nguyên văn, snapshot, yêu cầu và kết quả chỉ ở Core/RAM; chỉ mục chống
trùng qua đúng API mẫu NGAN-0. Hai tệp `ngan.py`, `cau_hinh.py` và bốn
schema chung giữ nguyên, test so SHA-256 sau CRLF→LF. Không tải model,
từ điển, dữ liệu, wheel hoặc tài nguyên từ mạng. SDK 2.0.0 cài offline
vào `.venv`; wheel có SHA-256
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`,
khớp `SHA256SUMS.txt` trong repo.

`tests/test_dc6.py` dùng DOCX/PDF/PNG/văn bản DEMO của bộ DC-3…5 và tự
dựng phản hồi Local giả. Điều phối/Core/quyền và nguồn OCR đều giả,
không đo chất lượng model. Riêng test handler Hỏi AI-2 tham khảo mã
`e_hoi_ai/goi/e_hoi_ai/e_hoi_ai/hoi_yeu_cau.py` hiện có, chỉ import trong
tests; provider giả chặn mạng/Cloud. Không import/gọi engine khác trong
runtime hoặc sửa engine Hỏi AI. Test chứng minh giữ chuyển tiếp/băm và
đường thiếu căn cứ/ChuaRo; nợ metadata phân loại C-DC-07 ghi ở VIEC.

SHA-256 hiện hành UTF-8 sau CRLF→LF (các bảng lát trước là lịch sử):

| Tệp | SHA-256 LF |
|---|---|
| `e_doi_chieu/chuan_bi_ai.py` | `ce9e650e8e49b9a669a2a9fdc1c2c9164cc46390b03e6afd5ccfa517112096df` |
| `e_doi_chieu/hau_kiem_ai.py` | `4d2c994ce7066bf1a61f143e4d838c7b61378af82f6adaeca0e950b330229fd4` |
| `e_doi_chieu/chay.py` | `e654431fdd7173a4e1db0e4a2df942069f923801ee5631db1a3b6c17b6ed4c93` |
| `engine.json` | `0bfafdc1550405313b48fd4066b8448cc77f8f7548a39e42d2326fa7ff645d8c` |
| Repo: `e_doi_chieu/tests/test_dc6.py` | `5ed55b425d889d76bfa4889a64ca5fd69824168a502d977f76b0de2a341e92d1` |

## DC-5 — 15/11/2026

Sửa theo kiểm độc lập lead: bỏ regex wildcard nối chữ số với đơn vị;
quét token có kiểm hủy, tách lần quét số khỏi lần kiểm đơn vị để không
quét lại hậu tố số dài. Rà toàn bộ regex của hai tệp: không còn `.*`/`.+`;
regex phân cách trong `doc_so` chỉ nhận tối đa 200 ký tự, các nhóm còn
lại có dấu phân cách tách biệt hoặc chiều dài hữu hạn. Không thêm nguồn
ngoài/dependency. Phiên bản thuật toán `DC-5-2` tránh dùng lại kết quả cũ.

Parser giới hạn toàn cụm tiền chữ **64 từ**, giữ nguyên văn và Cần xem
khi vượt. Ngữ pháp bổ sung nghìn tỷ (số nguyên dưới 10^15), linh/lẻ sau
hàng lớn, cách đọc năm/lăm và hàng trăm đọc gọn. Ngoặc chữ ngay sau một
số tiền duy nhất cùng dòng/ô được kiểm kể cả không có nhãn. Bộ test
hiệu năng sinh chuỗi DEMO trong RAM; tiến trình con có timeout để chặn
test hồi quy ReDoS treo pytest. Số đo chỉ cho bộ quét tiền/đặc trưng,
adapter offset đồng nhất; không phải thời gian toàn tuyến Core/OCR.

`quy_tac.py`, `tien_chu.py` viết mới trong workspace theo DAC-TA §5.1,
DC-g và phiếu DC-5. Chỉ dùng thư viện chuẩn Python/SDK 2.0.0; không tải
mạng, chép từ điển/model/font hoặc thêm dependency. `chay.py` chỉ đổi
import handler tại khối DC-5 riêng, giữ đăng ký API hiện có.

Tái dùng nội bộ `so_chu.py`/`can_chinh.py`/`ho_so.py`/`chuan_hoa.py` của
DC-3/DC-4, không sửa chúng. Vòng giữ/chốt lượt DC-5 chuyển từ quy ước
DC-4 vào coordinator riêng để giữ phạm vi đúng ba tệp và không tạo hai
snapshot trung gian. Không import runtime engine khác hoặc mã Core.

Ngữ pháp số tiếng Việt được cài hữu hạn trong `tien_chu.py`, không phải
từ điển mua ngoài hay chứng nhận xử lý mọi cách viết. Bản không phân
tích đủ luôn giữ cần xem/chưa đủ kiểm. Bộ, tệp DOCX/PDF/PNG và phản hồi
AI đề xuất trong tests đều DEMO; OCR/ảnh/quyền/ngăn do CoreGia/adapter
giả, không là số đo OCR/Core/model thật.

SHA-256 hiện hành UTF-8 sau CRLF→LF (các bảng lát trước là lịch sử):

| Tệp trong gói | SHA-256 LF |
|---|---|
| `e_doi_chieu/quy_tac.py` | `11e9163fb90842dd35ff51d605f8a44918742efb23f55c285bb47a3e4f892291` |
| `e_doi_chieu/tien_chu.py` | `d0aba9de44269b62fe1a1506780b3a3459c1a462a9fc9988b502ad6a8d48224d` |
| `e_doi_chieu/chay.py` | `821f0c57ea9bfb980f146231ce5ac201b32bf6fd3a3ef8e323ddb812ac42f591` |
| Repo: `e_doi_chieu/tests/test_dc5.py` | `a90501217248846257fb6c471d831206cee5c192e23272dd7c3af45107c6f2c0` |

Hai bản chép NGAN-0 và mọi schema chung giữ nguyên; test so băm LF vẫn
đạt. SDK offline/wheel/phiên bản và giấy phép nguồn giữ theo DC-4 bên dưới.
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
