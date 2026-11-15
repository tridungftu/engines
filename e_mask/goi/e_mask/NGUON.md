# NGUỒN — gói e_mask, MASK-1…6 và sửa an toàn

Ngày bắt đầu đối chiếu: 14/11/2026. Chỉ DEMO. Lõi nội bộ từ Mask v2; nguồn cũ giữ nguyên. Handler che/mở che hiện đã có nghiệp vụ qua ngăn; các mô tả stub/kho tệp dưới đây là lịch sử từng lát. Trạng thái mới nhất tại mục sửa an toàn ngày 15/11/2026. Đã kiểm bằng Core giả (CoreGia).

## Năm tệp chép vào gói

Đường nguồn tính từ gốc repo; đường đích tính từ thư mục chứa tài liệu này. SHA trước giữ bản nguồn, SHA sau trong bảng privacy phản ánh bản gói hiện tại. Hai cột SHA LF tính sau đổi CRLF thành LF để kiểm trên Linux/Windows; không đổi nội dung ngoài xuống dòng. Test so SHA LF, vì checkout Git có thể đổi xuống dòng. Hai matcher tên chép nguyên byte trong worktree này.

| Đường nguồn | Đích trong gói | SHA trước (byte) | SHA sau (byte) | SHA trước (LF) | SHA sau (LF) | Điều chỉnh |
|---|---|---|---|---|---|---|
| `e_mask/ma-nguon/nguon/privacy/__init__.py` | `e_mask/nguon/privacy/__init__.py` | `ad88cdef05aa5862fb2e34bab1b19bc2e80727e40cabdbe9246133f8e846096f` | `bff7a8d02fd5f38b6876ea7930a2cdbcbbed9e85d2b3b6883005506a92f602c3` | `089a17a5759e62cb2e7a4f160bb88ac248ea4a8e2a507f1c7aad323a123e6845` | `584c0a757e561d88a1d2e624400c3f41908ae59167c7e734c02e19cdaa9cf181` | Ghi rõ phiên bản nguồn 2.7.2 chỉ là thông tin nguồn; không gọi ứng dụng cũ. |
| `e_mask/ma-nguon/nguon/privacy/types.py` | `e_mask/nguon/privacy/types.py` | `c99ab1584d732dd35938d2cca4202129673bb4507ada4ec77a96cea7eaa1141a` | `76e6bae89a5acfad89068a09583d2485d3d4c7010ba6b7730451ac779ffa4698` | `59acab78646831909af6da5d54b292c0ad35929fbbff8b526084853bbf02c562` | `7f81a43ed1f61a8553c73da9499c5fab1c0bb69334f27b40eabfc202b9c3b3e1` | Bỏ Cf/selector trước NFC, ánh xạ về nguyên văn; từ chối nếu không ánh xạ được. |
| `e_mask/ma-nguon/nguon/privacy/core.py` | `e_mask/nguon/privacy/core.py` | `1b0cc53af256f6cfcb3ce2eeebe28eabb574c3b2cf3f82e1bdb4535732876029` | `842a978dafacb1d9e92ebc235917cab15910c66140380f7a695b87fc94255f75` | `287616e854e5c6a59be5a2531638dd5f68dda2df387b0ff778b770da4ff44075` | `80b89e308d02212f42e3bc4ea23fcd60fdd146d2593cf5fe45ec600ccc7df990` | Bỏ mã hóa bảng và xuất TXT/Word/ZIP cùng import liên quan; detector import khi gọi, thiếu thì từ chối. Giữ KnownText/nhóm/vị trí/bảo vệ số/numeric_review; thay bí danh [[...]], giữ mã Junsky, số tự sinh tối thiểu 4 chữ số không cắt; bỏ cụm gốc khỏi lỗi trùng; replace giữ phần NFD chưa thay và verify giữ ranh giới bí danh. MASK-2: numeric_review giữ ranh giới số bằng NUL thay vì nối qua bí danh. |
| `e_mask/ma-nguon/nguon/privacy/company_names.py` | `e_mask/nguon/privacy/company_names.py` | `b3c595c193b3711737846762112654e45d8448fd9b6922903154b1d3d302d958` | `b3c595c193b3711737846762112654e45d8448fd9b6922903154b1d3d302d958` | `56a6b584d2e78161182413df61c6391e21c9c6fa8f64d2c483e5f849fc3a2fb3` | `56a6b584d2e78161182413df61c6391e21c9c6fa8f64d2c483e5f849fc3a2fb3` | Chép nguyên byte; giữ matcher và vị trí tên doanh nghiệp. |
| `e_mask/ma-nguon/nguon/privacy/person_names.py` | `e_mask/nguon/privacy/person_names.py` | `68d77c172b618a309722350af8910cc7323d93f11c6347cbc152dbe4d70aed7a` | `68d77c172b618a309722350af8910cc7323d93f11c6347cbc152dbe4d70aed7a` | `e1b00921cdd1374876eaa13ce9baa3a79eef7cac7614d2b9854621f728054214` | `e1b00921cdd1374876eaa13ce9baa3a79eef7cac7614d2b9854621f728054214` | Chép nguyên byte; giữ gợi ý tên người có nhãn. |

## Đoạn mã tham chiếu trong repo

Ngoài năm tệp trên, chỉ đọc các đoạn sau; không mang thêm mô-đun vào gói:

- `e_mask/ma-nguon/nguon/privacy/detectors.py` — SHA byte: `b184b163d1b1f9c17fce2fe00f443b39b54d3894c8e4b054d0482f58a0a41ce0`; SHA LF: `793419cc7e649947040dd0abd1be2d76a02a038f8f92580bf56fb44cf64f5039`. Chép nguyên ba regex MONEY_NEAR, MONEY, DATE vào core.py để bảo vệ số mà không nạp detector/tài nguyên.
- `e_mask/ma-nguon/che_van_ban.py` — SHA byte: `0d8427b52e24d58abd12c036eecb55fb00dc71c125bc103cca814df387602244`; SHA LF: `f390dc60df977b768e1bcede3ec90ba63f20d0d79cd36507313c7ecd1c9221cd`. Tham khảo nguyên tắc _nfc_vi_tri, bản dò NFC trả khoảng vị trí gốc; hiện thực chuan_hoa_vi_tri trong types.py, dùng None cho ánh xạ đồng nhất.
- `e_mask/ma-nguon/kho_bo_nho.py` — SHA byte: `587b72a8a6b3ddea29aa12175fa877e994486a2719cca74b7fedb71336b54e22`; SHA LF: `e02c9582872cc289fe0e46683f81ca9c0a3c9a3e8d1a4db38b2eb874079c7d62`. Đối chiếu khuôn bí danh 1–100 ký tự và họ tiền tố MASKCT/MASKCN/MASKDC/MASKMST/MASKTK/MASKKHAC; không chép kho DEMO vào gói.

## Giới hạn và quyết định tạm

- Chỉ dùng thư viện chuẩn Python và SDK 2.0.0; không thêm thư viện chạy. Đã tách import cryptography/python-docx, encrypt_mapping/decrypt_mapping, make_docx/export_document/export_bundle khỏi bản chép. Hiện vật nguồn vẫn giữ để lead xem xét lưu trữ sau.
- `suggest` chỉ là gợi ý thủ công có trần 500 dòng; không dùng làm bộ che tự động. `suggest`, `dau_vet` và `verify(known=...)` chưa có detector sẽ báo lỗi nội bộ cố định, không trả kết quả kiểm giả. Detector/hậu kiểm đầy đủ thuộc MASK-2.
- Khuôn bí danh bọc `[[...]]`, mã bên trong tối đa 100 ký tự theo lõi văn bản cũ. Mã Junsky do danh mục cấp được giữ nguyên, không đánh lại số. Mã tự sinh nội bộ dùng họ MASK theo nhóm, tối thiểu bốn chữ số, nối tiếp số lớn nhất đã dùng theo tiền tố không phân biệt hoa thường; số vượt khuôn bị từ chối. Đây chỉ là helper DEMO, không cấp mã chung có giao dịch; kho cấp mã ở MASK-3.
- Họ tiền tố MASK còn chờ lead xác nhận không trùng Junsky thật. Không có bằng chứng danh mục thật; không tự đổi mã Junsky. Cổng chưa dùng helper này để phát hành bí danh.
- normalize giữ NFC và quy tắc ký tự điều khiển cũ. Bản dò có ánh xạ để matcher/replace nhận NFC/NFD nhưng giữ nguyên phần chưa thay của chuỗi gốc; vị trí tính theo chỉ số ký tự Python trong đầu vào.
- numeric_review đối chiếu chuỗi số sau thay theo danh sách đã chấp nhận. Đây chưa phải hậu kiểm tiền/ngày độc lập đầy đủ; không dùng để xác nhận an toàn Cloud.
- Lỗi trùng không chứa cụm gốc. Cổng vẫn chỉ trả LoiNghiepVu CHUA_LAM tiếng Việt cố định từ MASK-0; khi nối lõi ở lát sau phải ánh xạ PrivacyError sang mã/câu cố định theo phiếu, không dùng str(lỗi).
- Không chạy nguồn ngoài, bộ nhận dạng, dịch vụ hoặc AI. Không có kho bảng ánh xạ/tệp tài liệu trong gói.

## Dependency và môi trường kiểm

- Checkout lúc bắt đầu chưa có MASK-0; khôi phục đúng 10 tệp e_mask từ commit `c3e68148b5db837912a40ea39aa4539f53c3fca0` bằng đọc Git object vào worktree. Không đổi Git index, không commit/push. Lead cần đồng bộ dependency khi mở PR; tập mã MASK-1 chỉ gồm năm tệp nêu trên.
- `.venv` cài SDK offline từ wheel trong repo, SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`, khớp SHA256SUMS; SDK in 2.0.0. Dùng --system-site-packages để dùng pytest 9.1.1 có sẵn làm công cụ kiểm, không cài thêm thư viện ngoài SDK. Test import riêng dùng -I -S -B để chứng minh năm tệp chỉ cần thư viện chuẩn.
- Đặt PYTHONDONTWRITEBYTECODE=1 và PYTHONUTF8=1 khi chạy ba lệnh kiểm; gói không có tệp biên dịch.

## Bổ sung MASK-2 — 14/11/2026

Chỉ năm tệp mã chạy thay đổi: `nguon/privacy/{detectors,leftovers,core}.py`, `che_van_ban.py`, `tai_nguyen.py`. Bảng MASK-1 phía trên cập nhật SHA đích core.py theo bản hiện tại; nguồn cũ giữ nguyên. Ba bản chép bổ sung:

| Đường nguồn | Đích trong gói | SHA trước (byte) | SHA sau (byte) | SHA trước (LF) | SHA sau (LF) | Điều chỉnh |
|---|---|---|---|---|---|---|
| `e_mask/ma-nguon/nguon/privacy/detectors.py` | `e_mask/nguon/privacy/detectors.py` | `b184b163d1b1f9c17fce2fe00f443b39b54d3894c8e4b054d0482f58a0a41ce0` | `af46757cdc72c4841ae49dbc3472423eed2aca6936db65074485fe868c471b8e` | `793419cc7e649947040dd0abd1be2d76a02a038f8f92580bf56fb44cf64f5039` | `c252cc424c43bae0b832902006ba558702b4ff6add09e51604f921032a023a00` | Bỏ đường data mặc định; nạp whitelist, cache có thu hồi; kiểm đủ bốn nguồn cả khi không khớp mẫu. |
| `e_mask/ma-nguon/nguon/privacy/leftovers.py` | `e_mask/nguon/privacy/leftovers.py` | `36c43a45c06bd321a5296860ff3e93d31bd7c99af080db42c56cfd259df190e7` | `928277ea2ff26bd2815f423c18628ee9b74fb7aa80642dc7e67335deaeaab744` | `978f8e4dcf0155e2ae1b6c3b3f9ef23085416239e4327ebdef7f48a76144a163` | `ca7611b817a22927f5d33b55bae6f601461ccacaa88c97c2f43ffd3f45b8ab72` | Nạp allowlist qua nguồn được whitelist; giữ lớp quét hậu kiểm nguồn. |
| `e_mask/ma-nguon/che_van_ban.py` | `e_mask/che_van_ban.py` | `0d8427b52e24d58abd12c036eecb55fb00dc71c125bc103cca814df387602244` | `93f1c505b399d0a6f5186160f25b8194afb2bd89ebf5c07d696891dadd36cfac` | `f390dc60df977b768e1bcede3ec90ba63f20d0d79cd36507313c7ecd1c9221cd` | `14e9c626e8f4de6d603ea9b6af4ca51694a433376514f6a070f500ddab3ee63d` | Giữ trần, matcher, hậu kiểm độc lập, Counter tiền/ngày, chặn chuỗi chưa kiểm hết; chỉ ẩn token đúng khuôn, giữ dấu vết ngoặc hỏng, ranh giới mã và kiểm tiền/ngày khi mở. |

`tai_nguyen.py` viết mới bằng thư viện chuẩn: `nap_cau_hinh` chỉ nhận cấu hình nội bộ tin cậy `{tai_nguyen: {<tên>: {duong_dan, sha256}}}` cho đúng bốn nguồn. Đường tuyệt đối ngoài gói, tệp thường, UTF-8 và SHA-256 khớp; đọc trọn snapshot rồi mới dùng, cấu hình lỗi thu hồi snapshot/cache cũ. Mặc định không có whitelist, luôn `MASK_THIEU_TAI_NGUYEN`; không dò thư mục, tải nguồn, tạo từ điển hoặc dùng fixture làm fallback. SHA do lead cung cấp, không do đầu vào công việc tự khai. Kênh cấu hình máy MASK-0 vẫn giữ schema rỗng: chưa nối nạp whitelist vào adapter khi chưa được lead cấp nguồn sạch; hàm nạp này chỉ là giao diện nội bộ cho adapter sau.

`tests/ho_tro_kho_demo.py` chép từ `ma-nguon/kho_bo_nho.py`, chỉ đổi import về gói mới, không nằm trong gói chạy. Tận dụng toàn bộ test_che_van_ban.py, tự chứa fixture DEMO, bỏ import engines/tests/tools/Core cũ; test không chứng minh giao dịch/quyền Core thật. Kho được bên tin cậy tiêm; lõi không tự cấp quyền hoặc mã yêu cầu. Port/transport vận hành thuộc MASK-3; hai handler vẫn là stub.

Giới hạn được giữ: 500.000 ký tự đầu vào, 500 định danh đã biết, giá trị tối đa 300, nhóm tối đa 20 và phải thuộc danh mục nhóm. Detector tìm 501 cụm vẫn quét và che cả 501, không đi qua suggest/validate_rules có trần danh sách. Chuỗi liền quá dài được đánh dấu chưa kiểm đủ, không cắt đầu vào và không công bố văn bản; ba chuỗi hiệu năng 500.000 ký tự giữ ngưỡng xử lý 5 giây, tiến trình con 12 giây.

Khi còn sót/lỗi detector/chưa kiểm đủ/đổi tiền-ngày, kết quả nội bộ chặn văn bản. ThieuTaiNguyen mang mã cố định `MASK_THIEU_TAI_NGUYEN`; adapter sau ánh xạ cờ hậu kiểm sang `LoiNghiepVu` mã `MASK_DINH_DANH_CHUA_DAT` hoặc `MASK_TIEN_NGAY_THAY_DOI`, dùng câu cố định và không dùng str(lỗi)/cụm gốc. Chưa thay mẫu 1–4 hay phong bì Core.

Heuristic không bảo đảm phát hiện tên người viết thường không nhãn. Ca DEMO minh họa giới hạn được giữ trong test; từ vựng DEMO ít và test đạt không chứng minh đủ điều kiện Cloud. Bốn tài nguyên sạch vẫn chờ lead whitelist, Cloud chưa bật. Những mô tả “chưa có detector” ở phần MASK-1 là lịch sử; MASK-2 đã có mã detector nhưng chưa có nguồn vận hành sạch.

## Bổ sung MASK-3 — 14/11/2026

Chỉ bốn tệp mã chạy mới. Không thêm dependency ngoài thư viện chuẩn và SDK 2.0.0; hai handler vẫn là stub, việc nối nghiệp vụ thuộc MASK-5. Chỉ DEMO, đã kiểm bằng Core giả (CoreGia) và port kho/quyền giả. Không có transport kho/danh tính mặc định, không có kho tên gốc trên đĩa hoặc kho RAM vận hành.

| Tệp trong gói Python | Nguồn / điều chỉnh | SHA-256 đích (byte và LF giống nhau tại bàn giao) |
|---|---|---|
| `e_mask/kho_qua_core.py` | Chuyển nguyên tắc snapshot/nhật ký/chốt từ `e_mask/ma-nguon/kho_qua_core.py`; giữ hai thao tác port nội bộ và toàn bộ 11 vector cũ. Bỏ phụ thuộc cổng thế hệ trước, thêm nguồn quyền tin cậy, mã opaque, dấu chống trùng và đối soát chốt chưa rõ. | `5914a2818f0ff8bad6aa217dcd7e9ef466c116d51670fa35a7cd3cb017f0d86e` |
| `e_mask/kho_tam.py` | Viết mới theo phiếu §2.4: thư mục dữ liệu ngoài gói, khóa tệp đa tiến trình, ghi tạm/fsync/replace, schema đóng chỉ băm/mã trạng thái; lỗi thì dừng. | `f59171f0094a6093a338a9894a0695f6ce8d2a2d66f4acd1769714c1555714f5` |
| `e_mask/kho_dinh_danh.py` | Viết lớp ghép port/quyền cho protocol Kho có sẵn; kiểm kết quả trước chốt và sau đọc lại, không có vòng gửi kết quả riêng. | `c23be50fd1d64a32f142a1a9eb5b870f624e667f4640387cb8f05fd76e5766a4` |
| `e_mask/quyen_yeu_cau.py` | Viết port danh tính/quyền; thiếu nguồn xác minh thì từ chối, không suy từ tham số/đầu vào/pháp nhân. | `4f44b32ec0c89ee40023dbd38502e9615f3522aaf648b9b15bb4b3c00cd17a4c` |

Nguồn `ma-nguon/kho_qua_core.py` giữ nguyên: SHA byte `2dd5c5f3ea64711a31f17265ba4e3b75a17e136258ae94c157cf2e6bb91dee15`; SHA LF `3608e50f82c76cde036afcc309bc4f01656e1a0cb4a17679ba9c7e106a547c78`. KhoBoNho từ nguồn cũ đã được MASK-2 chép ra helper test, nay tập trung tại `tests/ho_tro_core_gia.py`; helper `ho_tro_kho_demo.py` chỉ chuyển tiếp import. Fixture quyền/kho, máy chia sẻ RAM cho hai tiến trình và adapter SDK thử nghiệm đều ngoài gói chạy. Mã nguồn gốc giữ nguyên, không xóa/di chuyển.

Port này chưa công bố API ngăn mới. Core cần cấp mã ổn định theo việc/bước, kiểm phiên/module/người/tài liệu/vùng, quyền và lease tại snapshot/chốt/đọc lại, cùng CAS/duy nhất/ghi lô nguyên tử phía kho. Kho tạm chỉ băm mã và nội dung, không lưu nhật ký chứa cụm gốc hay kết quả; `ChuaRo` chỉ khi bên kho đã nhận chốt chưa trả, giao lại hỏi nguồn trước. Phần gửi lại kết quả thuộc SDK. Tiền tố cấp alias tại MASK-3 tập trung trong `TIEN_TO_TU_SINH`; còn chờ xác nhận họ MASK không trùng Junsky thật. Không đổi helper/matcher thuộc các lát lõi trước.


## Bổ sung MASK-3b → MASK-6 — 15/11/2026

Các mô tả stub/chờ tài nguyên/kho tệp ở các mục trên là lịch sử bàn giao. Handler hiện dùng ngăn và tài nguyên sạch đã duyệt theo lệnh giao mới nhất. Hai bản ngan.py, cau_hinh.py viết tạm bằng thư viện chuẩn theo đặc tả SDK 2.1 vì mẫu NGAN-0 đang làm song song; lead thay nguyên tệp khi gộp, hai test so SHA tạm skip. Không thêm dependency chạy.

Bốn từ điển chép nguyên byte từ e_mask/tham-chieu/tu-dien/ vào e_mask/tu_dien/. Nguồn là Mask v2 nội bộ đã được lead lọc sạch; ghi chú chờ duyệt trong bản nguồn là lịch sử, lệnh giao mới nhất xác nhận Anh đã duyệt. Gói không chứa danh mục đối tác thật. Nạp kiểm SHA bằng SHA256.json, test so byte với bản tham chiếu.

| Tệp | SHA-256 nguồn và bản gói |
|---|---|
| `common_acronyms.txt` | `920f0952f2584ece4c37d5419c073cd6f60cf151da3b38b1e68fdd6a2bb24f4e` |
| `leftover_allowlist.txt` | `7074f53c296bd7be258610335adc270879eccb2db63fa412c7a9088b077aea4b` |
| `vn_places.txt` | `e991d899a1fa2265082e871715a653c9ca4fd7ed233a8d3951fb80b7a2d41847` |
| `vn_surnames.txt` | `b9fc76e5fa1ebb6abca7f4bc7c58d0dd9ecffc992e642a21958449080b2aaad1` |

Kho mới giữ nguyên nguyên tắc snapshot/chốt của MASK-3, chuyển thành adapter API ngăn chung; dùng dòng CAS bảo vệ năm bảng. Chỉ dấu/băm/số đếm và định danh cần che được giữ; không cache tài liệu hoặc kết quả AI. Cổng quyền vẫn là port được bên tích hợp tin cậy cấp. Tệp kho_tam.py/cau_hinh_may.py giữ nguyên làm hiện vật, không được handler import; lead xét lưu trữ sau.

Schema van_ban_da_che tạo theo phần đã duyệt của sổ loại riêng, chép nguyên byte vào gói; hai schema van_ban_tai_lieu/tra_loi_ai chép từ sổ chung, không sửa nguồn. Test so SHA cả ba. Bản khai chờ 2.1 độc lập phiếu 2.0. Màn duyệt viết bằng JavaScript chuẩn, chỉ gọi KttCore, Node dùng riêng cho kiểm với bản giả. Công cụ chuyển DEMO chỉ nhận danh sách giả tích hợp sẵn, không đọc danh mục thật.

Đã kiểm bằng Core giả (CoreGia) và KttCore giả; chưa kiểm Core thật, Linux thực tế hoặc Cloud. CLI SDK chuẩn chưa được tiêm quyền Mask nên từ chối xử lý; adapter DEMO có port nằm ngoài gói. Trần 100 lệnh/lô và trần kỹ thuật JSON 4 MiB được ghi ở README; băm nội bộ chưa có khóa HMAC từ Core.

## Nối ngăn chung NGAN-0 — 15/11/2026

Đã nối ngăn chung NGAN-0 (PR chung #34 đã gộp). Mục này cập nhật các ghi chú chờ mẫu/skip ở các lần bàn giao trước: hai tệp mẫu đã do lead chép, phiên này giữ nguyên, không sửa `_chung/**`. Khai báo RAM lấy từ `KHAI-SDK-2.1.json/ngan_du_lieu`, đổi tên bảng từ `ma` sang `bang` đúng hợp đồng chung; không đổi engine.json 2.0. Không thêm thư viện chạy. Các test an toàn MASK-5 giữ nguyên hành vi và xanh; không gọi Cloud.

**Quy ước SHA-256 LF:** tính trên `read_bytes().replace(b'\r\n', b'\n')`, không bỏ BOM/khoảng trắng hoặc đổi ký tự khác. Đây là băm hiện tại thay cho số băm lịch sử của các tệp cùng tên. Test so mẫu và từ điển dùng cùng quy ước. NGUON.md tự mô tả nên không tự ghi băm chính nó.

| Tệp (từ gốc repo) | SHA-256 LF |
|---|---|
| `e_mask/cong-cu/chuyen_danh_muc_demo.py` | `3ffb0fad8b709bde45371aee785b3d5a9d7da8540e328e8a21c83b2c0fd56db3` |
| `e_mask/docs/VIEC.md` | `785ff02e4203c088307c3a086621ea2e38f39da2fbbb570d015eda7564e7375c` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `abae2f86b71dcb1b452f067014e41e1895205994a1168cf4a5806d89e4f74d43` |
| `e_mask/goi/e_mask/KHAI-SDK-2.1.json` | `db2ca7378f08d4d5c9fd60d77d79b403c4c1f9b8ea80a5f26e796c5349306cb5` |
| `e_mask/goi/e_mask/README.md` | `2c5bd3abd44733826a15bba70b307dab7fd6906021cf8d4351d3caee78103683` |
| `e_mask/goi/e_mask/e_mask/chay.py` | `346ff1d95734f7d52c78cac53e209e726b75fdf682ec43f763279f4eab637959` |
| `e_mask/goi/e_mask/e_mask/kho_ngan.py` | `dd7f47f871a8b1bced793855a79a9a98b66a6c11d6559a8112d99f3b39d7f67b` |
| `e_mask/goi/e_mask/e_mask/kho_qua_core.py` | `ead192d13252dab309692c1f7e95ebbf3100930a73a1f2ed9ced051a03c292c3` |
| `e_mask/tests/chay_demo.py` | `edbfe964c6d628435a068ca2965189c617964cd913c69d7b3e8dbc16a06ef58c` |
| `e_mask/tests/test_mask_3b.py` | `96ef2c819123429b6e0e20f9d1a1d97ae48fc73249198843eca8912d9bf98c48` |
| `e_mask/tests/test_mask_4_6.py` | `cc4345889d8d7cc51d95d8c4a44d1ae5997e79fa269c18c9d41c6ed461de77b8` |

Hai mẫu chung được giữ nguyên, kiểm đối chiếu nguồn → bản gói sau chuẩn hóa LF:

| Nguồn | Bản gói | SHA-256 LF của cả hai |
|---|---|---|
| `_chung/mau-ma/ngan.py` | `e_mask/goi/e_mask/e_mask/ngan.py` | `2a2d7468e034717c93e15385833209026c56e59b6007e23c538d4a31125947e0` |
| `_chung/mau-ma/cau_hinh.py` | `e_mask/goi/e_mask/e_mask/cau_hinh.py` | `7fa55d80426ddfe67359009b1a8cde02ef2a85984ad0bad9658442cec75e2252` |

Đã kiểm bằng Core giả (CoreGia): cổng thay thế trong tests đạt 2/2 DEMO; CLI SDK chuẩn chặn thiếu nguồn quyền. Pytest 280 passed, 190 subtests passed, 0 skipped; kiểm độc lập đạt. RAM không bền qua khởi động lại, quyền/ngăn thật vẫn chờ Core.

## Sửa an toàn theo kiểm độc lập — 15/11/2026

Mục này cập nhật trạng thái hiện tại; số băm ở bảng nguồn privacy phía trên được làm mới theo bản gói. Không sửa nguồn trong ma-nguon, mẫu chung hoặc hai bản ngan.py/cau_hinh.py trong gói. Chỉ thư viện chuẩn và SDK 2.0.0; không thêm dependency.

- `nguon/privacy/types.py`: dùng bảng Unicode của Python (category Cf) và các variation selector, tạo bộ quét một lần trong RAM. Bỏ ký tự vô hình trước NFC và giữ khoảng ký tự nguyên văn; không ánh xạ được thì từ chối. Không duy trì whitelist Cf thủ công.
- `che_van_ban.py`, `phong_bi.py`: dùng chung ánh xạ, dò bổ sung tên qua tab/xuống dòng; bỏ mọi ký tự vô hình trên đầu ra, kiểm chặn phong bì, giữ đối chiếu tiền/ngày. Mã Junsky đã duyệt giữ nguyên khi khớp tên.
- `kho_qua_core.py`, `kho_ngan.py`, `chay.py`: bí danh tạm riêng mỗi yêu cầu, không nhận tham chiếu chéo, giữ chính thức; gộp cụm chờ và đếm gặp đúng. Lỗi ngăn/port thành câu cố định, bỏ chuỗi ngoại lệ gốc; giữ hủy/ChuaRo/CAS. Chốt không nhận bản che không đạt.
- Ba hiện vật `kho_tam.py`, `cau_hinh_may.py`, `schemas/cau_hinh_may.schema.json` chuyển nguyên nội dung từ gói sang `e_mask/LUU-TRU/mask_truoc_ngan/` theo đúng cấu trúc con. Gói không còn mô-đun/schema này. Test lịch sử nạp qua `tests/ho_tro_luu_tru.py`, không đưa thư mục lưu trữ vào đường chạy engine. SHA LF đối chiếu với blob gốc của cả ba tệp.
- `git mv` bị sandbox chặn Git index ngoài worktree; dùng Move-Item để giữ nguyên tệp. Lead stage rename khi commit. Không commit/push. Kiểm độc lập đã thêm chặn mã đọc biến cấu hình máy và import mô-đun lưu trữ.

Các test hồi quy dùng đúng ví dụ định danh DEMO do lead cung cấp; kiểm Cf toàn bộ bảng Unicode, selector ngoài BMP, NFD/NBSP/tab/xuống dòng, MST/STK, quyền alias và stdout/stderr. Hai yêu cầu độc lập có alias tạm khác nhau là thay đổi có chủ ý theo lệnh sửa an toàn, thay kỳ vọng cũ dùng chung alias. Vector trong ma-nguon giữ nguyên; fixture bổ sung quyền sở hữu rõ ràng cho các ca tái dùng của chính yêu cầu đó.

SHA-256 hiện tại bên dưới tính sau chuẩn hóa CRLF thành LF, không băm chính NGUON.md. Kết quả chạy thật và giờ thực tế ở báo cáo sửa an toàn trong e_mask/docs; đã kiểm bằng Core giả (CoreGia).

<!-- SHA-SUA-AN-TOAN -->

| Tệp (từ gốc repo) | SHA-256 LF |
|---|---|
| `.gitignore` | `ce73ac75f2132332709576302ce0e8b848d232780636db3da15bf4deb3dfe275` |
| `e_mask/LUU-TRU/mask_truoc_ngan/cau_hinh_may.py` | `282258c946f3d1dc9562f00a3c3d5aa89113372c670b62a2d43726b57adcb0b2` |
| `e_mask/LUU-TRU/mask_truoc_ngan/kho_tam.py` | `f59171f0094a6093a338a9894a0695f6ce8d2a2d66f4acd1769714c1555714f5` |
| `e_mask/LUU-TRU/mask_truoc_ngan/schemas/cau_hinh_may.schema.json` | `111673c65f54ad9b866e08b4f300871bbc3f6faf2cc2309a060aa3e9a2ae45d1` |
| `e_mask/docs/VIEC.md` | `785ff02e4203c088307c3a086621ea2e38f39da2fbbb570d015eda7564e7375c` |
| `e_mask/goi/e_mask/CHANGELOG.md` | `abae2f86b71dcb1b452f067014e41e1895205994a1168cf4a5806d89e4f74d43` |
| `e_mask/goi/e_mask/README.md` | `2c5bd3abd44733826a15bba70b307dab7fd6906021cf8d4351d3caee78103683` |
| `e_mask/goi/e_mask/e_mask/chay.py` | `346ff1d95734f7d52c78cac53e209e726b75fdf682ec43f763279f4eab637959` |
| `e_mask/goi/e_mask/e_mask/che_van_ban.py` | `55cdceed15cd9d0988abf1211f66b3290522860fa36621b8b1e440d15d227104` |
| `e_mask/goi/e_mask/e_mask/kho_ngan.py` | `dd7f47f871a8b1bced793855a79a9a98b66a6c11d6559a8112d99f3b39d7f67b` |
| `e_mask/goi/e_mask/e_mask/kho_qua_core.py` | `ead192d13252dab309692c1f7e95ebbf3100930a73a1f2ed9ced051a03c292c3` |
| `e_mask/goi/e_mask/e_mask/nguon/privacy/types.py` | `7f81a43ed1f61a8553c73da9499c5fab1c0bb69334f27b40eabfc202b9c3b3e1` |
| `e_mask/goi/e_mask/e_mask/phong_bi.py` | `8d1393bba2fbd278fcd22a469b9b76c55acb7c2627109b4998c4af1f45f97661` |
| `e_mask/tests/ho_tro_core_gia.py` | `98319448372a4269b43fdacd8b482febbbf6e4cacc11ca3b8a978906dd871cfe` |
| `e_mask/tests/ho_tro_luu_tru.py` | `54f9c2a6965da00325337e64d828b279646f39bd32dd3730b724a8a1f665d64a` |
| `e_mask/tests/kiem_doc_lap.py` | `8557adb5389495692f34d1d15b162a68968d4a54aa5b2ce53ce896f86b8045ab` |
| `e_mask/tests/test_kho_tam.py` | `dbf436f6312d2399b4be012f041ab53bdd24fea18ee0acb132a1412a9c5a843d` |
| `e_mask/tests/test_mask_0.py` | `700940273d7165f5cdd3e7021c2e5a15097013de22092f213bc8b829304c798c` |
| `e_mask/tests/test_mask_3.py` | `25049167381885f975a068b2c5c891098fa9d2da24733d9bff8ccdc3d3298c80` |
| `e_mask/tests/test_mask_3b.py` | `96ef2c819123429b6e0e20f9d1a1d97ae48fc73249198843eca8912d9bf98c48` |
| `e_mask/tests/test_mask_4_6.py` | `cc4345889d8d7cc51d95d8c4a44d1ae5997e79fa269c18c9d41c6ed461de77b8` |
| `e_mask/tests/test_sua_an_toan.py` | `c85beeb506055e65303ce302546300054792f588e9325f3174b02940d6cb4413` |
| `e_mask/docs/BAO-CAO-SUA-AN-TOAN-MASK-3b-6.md` | `b670eaf9a1199dfaff23dc20045e15219f88cf7f455189872f58347671b3cc7d` |
| `e_mask/docs/KET-QUA-KIEM-SUA-AN-TOAN-MASK-3b-6.txt` | `4b232e449470aeb2b5d91e27d7772a93b105d28e8ae6344d3700c37961c6c24d` |
