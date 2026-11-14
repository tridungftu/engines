# NGUỒN — gói e_mask, MASK-1

Ngày bắt đầu đối chiếu: 14/11/2026. Chỉ DEMO. Lõi nội bộ từ Mask v2; nguồn cũ giữ nguyên. Cổng của MASK-0 vẫn trả `CHUA_LAM`; chưa hoàn tất nghiệp vụ che/mở che, chưa kích hoạt vận hành. Đã kiểm bằng Core giả (CoreGia).

## Năm tệp chép vào gói

Đường nguồn tính từ gốc repo; đường đích tính từ thư mục chứa tài liệu này. SHA-256 trước/sau tính trên byte thực tế tại lần bàn giao. Hai cột SHA LF tính sau đổi CRLF thành LF để kiểm trên Linux/Windows; không đổi nội dung ngoài xuống dòng. Test so SHA LF, vì checkout Git có thể đổi xuống dòng. Hai matcher tên chép nguyên byte trong worktree này.

| Đường nguồn | Đích trong gói | SHA trước (byte) | SHA sau (byte) | SHA trước (LF) | SHA sau (LF) | Điều chỉnh |
|---|---|---|---|---|---|---|
| `e_mask/ma-nguon/nguon/privacy/__init__.py` | `e_mask/nguon/privacy/__init__.py` | `ad88cdef05aa5862fb2e34bab1b19bc2e80727e40cabdbe9246133f8e846096f` | `584c0a757e561d88a1d2e624400c3f41908ae59167c7e734c02e19cdaa9cf181` | `089a17a5759e62cb2e7a4f160bb88ac248ea4a8e2a507f1c7aad323a123e6845` | `584c0a757e561d88a1d2e624400c3f41908ae59167c7e734c02e19cdaa9cf181` | Ghi rõ phiên bản nguồn 2.7.2 chỉ là thông tin nguồn; không gọi ứng dụng cũ. |
| `e_mask/ma-nguon/nguon/privacy/types.py` | `e_mask/nguon/privacy/types.py` | `c99ab1584d732dd35938d2cca4202129673bb4507ada4ec77a96cea7eaa1141a` | `334e5fcf3f9e7e7c03514017fb6825f1db217560e70c76328216e4777ed89a83` | `59acab78646831909af6da5d54b292c0ad35929fbbff8b526084853bbf02c562` | `334e5fcf3f9e7e7c03514017fb6825f1db217560e70c76328216e4777ed89a83` | Giữ normalize/Extracted/PrivacyError; thêm bản dò NFC kèm khoảng ký tự gốc cho NFD; lỗi nội bộ không đưa thẳng ra cổng. |
| `e_mask/ma-nguon/nguon/privacy/core.py` | `e_mask/nguon/privacy/core.py` | `1b0cc53af256f6cfcb3ce2eeebe28eabb574c3b2cf3f82e1bdb4535732876029` | `35f67fc5f4a5cbc76c4aa2f5ab75f86ffd1510cef924a21ae1e12d2af912ff2b` | `287616e854e5c6a59be5a2531638dd5f68dda2df387b0ff778b770da4ff44075` | `35f67fc5f4a5cbc76c4aa2f5ab75f86ffd1510cef924a21ae1e12d2af912ff2b` | Bỏ mã hóa bảng và xuất TXT/Word/ZIP cùng import liên quan; detector import khi gọi, thiếu thì từ chối. Giữ KnownText/nhóm/vị trí/bảo vệ số/numeric_review; thay bí danh [[...]], giữ mã Junsky, số tự sinh tối thiểu 4 chữ số không cắt; bỏ cụm gốc khỏi lỗi trùng; replace giữ phần NFD chưa thay và verify giữ ranh giới bí danh. |
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
