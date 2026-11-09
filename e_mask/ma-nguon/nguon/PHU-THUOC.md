# Phụ thuộc nguồn — Che định danh (Mask)

Ngày kiểm kê: **06/11/2026 — MASK-1 / CD-101**. Lõi nguồn nội bộ **2.7.2**, chép theo Quyết định cuối e_mask §2.1 lát 1. Kiểm giấy phép **thư viện bên thứ ba**, không đặt lại gate giấy phép nguồn nội bộ đã duyệt. Đây là kiểm kê, không phải lock/bộ cài hoặc chứng nhận engine độc lập.

## 1. Phạm vi và bằng chứng

- Closure đã chép: 11 tệp `.py` trong `privacy/`; danh sách/SHA nguồn và đích/điều chỉnh ở [NGUON.md](../NGUON.md). Không đọc lock, cấu hình, danh mục, bảng đối chiếu, khóa hoặc tài nguyên `data/` nguồn ngoài.
- Quét import các tệp đã chép; các import nội bộ được đổi sang tương đối. Không dùng FastAPI, Pydantic, Uvicorn, portalocker, pywin32 hoặc thư viện nhận dạng trong closure này. Module Excel chỉ dùng stdlib và lõi, không import openpyxl.
- Đối chiếu `pyproject.toml` Core và metadata/giấy phép thư viện đã có trong Python `D:\KTT-CD060-DEMO\python313\python.exe`, bổ sung deps Core đúng đường dẫn handoff `var/app-runtime/app-runtime-20261019-092310-807/deps`. Deps bổ sung chỉ thấy metadata psycopg, psycopg-binary, tzdata; các thư viện lõi dưới đây được Python nền cung cấp. Không cài/nâng/hạ thư viện, không gọi mạng.
- Pin nguồn ngoài dưới đây là **bằng chứng lịch sử** trong [kế hoạch G3-GOI §2.4](../../../docs/47-core/g3/KE-HOACH-G3-GOI.md), chưa tái đọc lock nguồn. Phiên bản cài thực tế là kết quả `importlib.metadata` trong môi trường test hiện tại, không suy thành pin phát hành.

## 2. Phụ thuộc thực tế của lõi đã chép

| Thư viện | Mã sử dụng/quan hệ | Nguồn (pin lịch sử) | Core khai báo / đã cài | Đối chiếu |
|---|---|---|---|---|
| cryptography | `core.py`: AESGCM, Scrypt (helper mã hóa/giải mã bảng cũ) | 50.0.1 | Core exact 49.0.0 / **49.0.0** | **Lệch exact pin**. Import được; chưa chứng minh tương thích đầy đủ với bộ nguồn 50. Không nâng Core. |
| python-docx | `core.py`: Document, Pt để dựng/kiểm DOCX mới | 1.2.0 | crm-docgen exact 1.2.0 / **1.2.0** | Trùng; phụ thuộc này hiện ở optional group, không mặc định được bảo đảm khi chỉ cài Core tối thiểu. |
| lxml | Qua python-docx, yêu cầu `>=3.1.0` | 6.1.1 | crm-docgen exact 6.1.3 / **6.1.3** | **Lệch exact pin lịch sử**; bản Core đáp ứng yêu cầu python-docx. Không đổi thư viện. |
| typing_extensions | Qua python-docx, yêu cầu `>=4.9.0` | Chưa đối chiếu exact pin nguồn | Không ghim riêng / **4.15.0** | Đáp ứng giới hạn đã đọc; chưa có lock engine. |
| cffi | Qua cryptography trên CPython, yêu cầu `>=2.0.0` | Chưa đối chiếu exact pin nguồn | Không ghim riêng / **2.0.0** | Đáp ứng giới hạn metadata Core. |
| pycparser | Qua cffi trên CPython | Chưa đối chiếu exact pin nguồn | Không ghim riêng / **3.0** | Có trong môi trường; chưa có lock engine. |

Các module còn lại dùng stdlib (`re`, `unicodedata`, `io`, `zipfile`, XML, dataclasses, pathlib…). `detectors`/`leftovers` còn cần tài nguyên văn bản chưa được phép chép: thiếu từ điển thì lỗi, không hạ kiểm tra sang kết quả an toàn giả. Xem NGUON §3.

## 3. Giấy phép thư viện bên thứ ba

Đã đọc metadata và các LICENSE hiện có trong `*.dist-info/licenses/` của Python nền, không dựa riêng vào tên package. Chưa sao chép bộ license vào gói vì ngoài whitelist lát này. Giữ notice/điều kiện/miễn trừ khi đóng gói theo license thực tế của artifact được chọn; đây chưa là nghiệm thu phân phối wheel.

| Thư viện/bản đã kiểm | Giấy phép và bằng chứng local | Việc còn giữ khi đóng gói |
|---|---|---|
| cryptography 49.0.0 | `cryptography-49.0.0.dist-info/licenses/{LICENSE,LICENSE.APACHE,LICENSE.BSD}`: chọn Apache-2.0 **hoặc** BSD-3-Clause | Giữ thông báo và điều kiện tương ứng; đối chiếu license artifact 50.0.1 nếu lead chọn môi trường riêng. Không tự suy license bản chưa kiểm. |
| python-docx 1.2.0 | `python_docx-1.2.0.dist-info/licenses/LICENSE`: MIT | Giữ copyright và nội dung cho phép/miễn trừ. |
| lxml 6.1.3 | `lxml-6.1.3.dist-info/licenses/{LICENSE.txt,LICENSES.txt}`: BSD-3-Clause; có thành phần ElementTree/CPython (PSF) và tài nguyên có điều kiện riêng | Giữ notice; đọc đầy đủ license của artifact thực đóng gói, không gắn BSD cho mọi thành phần. Closure không dùng isoschematron/lxml.html hay test-runner GPL được LICENSES.txt nhắc tới. |
| cffi 2.0.0 | Metadata: MIT; `cffi-2.0.0.dist-info/licenses/LICENSE` mở đầu **MIT No Attribution** kèm ngoại lệ theo tệp | Giữ bản LICENSE đi cùng artifact; không gom mọi phần vào một nhãn MIT chung. |
| pycparser 3.0 | `pycparser-3.0.dist-info/licenses/LICENSE`: BSD-3-Clause | Giữ copyright/điều kiện/miễn trừ, không dùng tên tác giả bảo chứng. |
| typing_extensions 4.15.0 | Metadata: PSF-2.0; `typing_extensions-4.15.0.dist-info/licenses/LICENSE` chứa lịch sử và các điều khoản Python | Giữ nguyên license/notices của bản phân phối được chọn. |

**Thành phần native/bundled:** `lxml LICENSES.txt` liệt kê zlib (zlib), iconv (LGPL-2.1), libxml2/libxslt/libexslt (MIT/ngoại lệ theo tệp). Điều này là căn cứ phải rà wheel thực tế, không khẳng định wheel Windows hiện tại có đủ mọi thành phần đó. `cryptography`/cffi cũng có thành phần native (OpenSSL/Rust/libffi tùy artifact); chưa kiểm trọn tập notice/license/version của binary. Lead giữ bước rà artifact cuối, gồm nghĩa vụ LGPL nếu có iconv; không kết luận chỉ MIT/BSD là đủ. MASK-1 không chép binary hoặc thư viện bên thứ ba.

## 4. Thư viện của server cũ — không đưa vào closure lõi

| Thư viện | Pin nguồn lịch sử | Python Core hiện có | Ý nghĩa |
|---|---|---|---|
| FastAPI | 0.141.1 | 0.141.1, metadata MIT | `server.py` không chép. |
| Pydantic | 2.13.5 | 2.13.4, metadata MIT | Lệch pin lịch sử; API Core lát sau phải chốt, không tự nâng. |
| Uvicorn | 0.53.0 | 0.53.0, metadata BSD-3-Clause | Không chạy server. |
| portalocker | Chưa có exact pin trong căn cứ repo | Không cài | Kho tệp cũ không chép; chưa kiểm license artifact chưa có. |
| pywin32 | 312 | 312, metadata PSF | Không import/chạy Word COM; không cần cho lõi đã chép. |
| openpyxl | Không import trong lõi đã chép | Core `~=3.1` / 3.1.5, metadata MIT | Thư viện Core sẵn có; không thêm hoặc dùng để viết lại lõi Excel. |

Chỉ metadata license được ghi cho các thư viện ngoài closure; không coi đây là kiểm license đầy đủ của server hoặc toàn môi trường. Phụ thuộc FastAPI bắc cầu không thuộc lõi giữ lại và chưa được đóng gói trong MASK-1.

## 5. Lệch phiên bản và cách xử lý cần lead chốt

1. Exact pin lịch sử Mask `cryptography==50.0.1` và Core `==49.0.0` không thể đồng thời thỏa trong một môi trường. `lxml==6.1.1` cũng khác pin Core `==6.1.3`; ghi nhận khác biệt không có nghĩa đã chứng minh API lỗi.
2. Quyết định mới bỏ môi trường riêng **có điều kiện**. Do đã thấy lệch pin, lead quyết định kiểm tương thích lõi trên deps Core hoặc dùng phụ thuộc riêng cho tiến trình Mask khi đóng gói. Không quay lại yêu cầu cài ngoài theo đường dẫn máy phát triển; nguồn sạch đã ở trong gói. Không sửa launcher/venv/lock hoặc nâng thư viện chung trong MASK-1.
3. Test import và Word/Excel DEMO trên deps Core không thay bộ kiểm tương thích đầy đủ của cryptography 50. Helper mã hóa bảng cũ chưa được tích hợp vì bảng mới nằm ở CSDL Core không mã hóa cột; lead chốt phạm vi helper còn cần trước pin cuối.
4. Không đổi/ghim wheel **SDK 1.4.1 candidate** (kế hoạch G3-GOI §6.3). SDK cuối thuộc lát 34.

## 6. Phần khung và trạng thái còn chờ

`engines/e_mask/chay.py` và `vong_doi.py` không sửa: còn phụ thuộc SDK, helper `env_con` ngoài SDK và launcher `run_privacy.py` nguồn ngoài. Không coi 11 module import được là khung đã chạy độc lập. Contract cũ vẫn dự thảo; lát sau cập nhật theo 8 mẫu trao đổi/mã yêu cầu đã duyệt, không đăng ký/kích hoạt trong MASK-1.

Nguồn OCR/client/AI/kho cục bộ không chép. Tài nguyên detector chưa có whitelist; Word giữ bố cục/mở che và phần Excel còn thiếu được báo ở [NGUON §4](../NGUON.md). Chưa có bằng chứng vận hành thật, CSDL, quyền, Cloud hoặc bài nghiệm thu tổng thể; trạng thái engine vẫn **Chờ tích hợp/kiểm chứng**.
