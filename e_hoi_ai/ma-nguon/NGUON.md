# Nguồn và phụ thuộc Hỏi AI — e_hoi_ai

## K3 — cấu hình Local thống nhất, 08/11/2026

Nguồn sự thật là `cau_hinh_schema` trong `engine.json`. Hồ sơ Admin và
settings launcher dùng cùng ba trường: `model_phat_hien`, `quy_tac_model`
và nhóm kết nối `local_ai` (`enabled`, `url`, tùy chọn `model`,
`timeout_seconds`, trạng thái kết nối). Hai danh sách vẫn bắt buộc;
`local_ai` có thể chưa khai khi chưa cấu hình máy. Nếu đã khai nhóm này
thì bắt buộc `enabled` và `url`. URL đầy đủ có đường dẫn
`/v1/chat/completions`; kiểm bằng hàm có sẵn của `ai_cuc_bo`, chỉ
loopback/RFC1918/Tailscale. Không dò DNS hoặc mạng trong bước đọc/lưu.

Admin ánh xạ DTO `models/quy_tac` sang hai danh sách chuẩn khi lưu;
không lưu DTO vào `local_ai`. Tên hiển thị `ten` là metadata tùy chọn
của model/quy tắc. Giữ scope `module/function`, cờ `bat` và các model dự
phòng sau mục đầu mà màn hiện chưa sửa. Model mới tắt mặc định; model
mất giữ lại với trạng thái `chua_ro`. DTO chỉ trả nhãn máy đã che,
không công bố cả một phần IP. Địa chỉ chỉ nằm trong cấu hình nhập Admin
và seam tin cậy, không đưa vào trạng thái hoặc thông báo lỗi.

Cấu hình Admin cũ `local_ai.models/quy_tac/dia_chi` bị chặn với câu
“Cần lưu lại cấu hình máy AI cục bộ theo mẫu hiện hành trước khi tiếp tục.”
Không tự bỏ trường hoặc ghi đè dữ liệu cũ. Settings runtime cũ cùng hai
danh sách chuẩn được đọc khi model thiếu metadata phần mềm/thời điểm;
không bịa metadata, không nới kiểm lúc Admin ghi. Envelope `cong_ai` cũ
chỉ nhận tên trường đã có trong lõi cổng để giữ seam bí mật; Cloud vẫn
bị khóa trước readiness. Khóa lạ trong cấu hình chuẩn bị từ chối trước
worker/Local transport. `chay_tu_core` dùng cùng bước đọc với `chay`.

Lead cần cài/đăng ký manifest mới qua quy trình gói hiện có để schema
đã ghim khớp hồ sơ. Lát này không sửa CSDL/migration và không nghiệm thu
máy AI thật. Không đổi SDK, phụ thuộc, capability hoặc contract.

## AI-LAT3 — 08/11/2026

Gói dùng mã nội bộ đã có; không chép nguồn ngoài, thêm thư viện hoặc tạo
client AI mới. `lib/cong_ai.py` và `lib/ai_cuc_bo.py` là lõi cổng dùng chung
đã chuyển vào engine ở G3-GOI-06; bridge tại `tri_thuc` dùng cùng module.
DTO, adapter và nhật ký dùng lại lõi này. Nhật ký qua SDK, phần lưu CSDL
thuộc Core. Không cần import `tri_thuc`, module nghiệp vụ hoặc engine khác.

Manifest hiện hành: `0.1.1-demo.1`, capability `ai.hoi@1`, đầu vào
`hoi_ai.v2`, đầu ra `tra_loi_ai.v2`. `pyproject.toml` dùng dạng PEP 440
`0.1.1.dev1`; runtime đọc phiên bản trực tiếp từ `engine.json` trong gói.
Readiness vẫn kiểm model Local trước khi báo sẵn sàng, không lấy phiên
bản từ cấu hình Core. Đọc tối đa 64 KiB + 1 byte để phát hiện vượt hạn;
chỉ parse manifest không vượt 64 KiB. Thiếu tệp, lỗi đọc/UTF-8/JSON,
thiếu hoặc sai phiên bản đều chặn readiness bằng lỗi hữu hạn
`AI_GOI_HONG_PHIEN_BAN`: “Gói Hỏi AI hỏng phiên bản.” Không công bố sẵn
sàng hoặc tạo worker/cổng AI khi lỗi; vẫn thu hồi tài nguyên bootstrap.
Contract bundle và ví dụ DEMO giữ nguyên.

### Phụ thuộc và giấy phép

Đo bằng `importlib.metadata` trong runtime được handoff cấp, CPython
**3.13.14 / Windows x64**, ngày **08/11/2026**. Không cài/nâng gói.

| Thành phần | Phiên bản đã đo | Lý do | Giấy phép theo metadata |
|---|---|---|---|
| Python / stdlib | 3.13.14 | JSON, HTTP Local, socket, threading và tài nguyên trong gói | PSF |
| `kho_tri_thuc.sdk_core` | Core cấp từ mã hiện có | Bootstrap, lease, chữ ký, bàn giao và nhật ký | Mã nội bộ; không suy giấy phép nguồn mở |
| `cryptography` | 49.0.0 | SDK kiểm chữ ký Ed25519 | Apache-2.0 OR BSD-3-Clause |
| `cffi` | 2.0.0 | Bắc cầu từ cryptography trên CPython | MIT |
| `pycparser` | 3.0 | Bắc cầu từ cffi trên CPython | BSD-3-Clause |

Engine không có import bên thứ ba trực tiếp. Ba pin trong
`requirements.lock` là closure của SDK trên môi trường đã đo; không là
lệnh phát hành hoặc ghim SDK. `jsonschema`/`referencing` ở phía Core;
engine chỉ nhận hàm kiểm schema. Không cần `openai`, `anthropic`,
`requests`, `httpx`, `psycopg` hoặc mô hình nằm trong gói.

**Yêu cầu SDK Python >=1.5.0**, do Core cấp qua namespace
`kho_tri_thuc.sdk_core`. Đây là mức tương thích tối thiểu, không phải
lệnh đổi SDK đang ghim hoặc tự cài wheel. Wheel SDK **1.4.1 chỉ là
candidate**, theo `docs/47-core/g3/KE-HOACH-G3-GOI.md` §6.3; không dùng
làm artifact phát hành đáp ứng yêu cầu trên. `pyproject.toml` ghi yêu cầu
này ở chú thích; giữ `dependencies = []` vì SDK do Core cấp, chưa có mẫu
khai dependency wheel đã duyệt. Mẫu OCR tại `README.md`/`NGUON.md` chưa
nêu mức >=1.5.0 và chưa có `pyproject.toml`; không sửa gói OCR trong lát này.

Runtime test không có metadata wheel SDK hoặc `setuptools`; chưa
build/cài/kiểm wheel độc lập. Mã nguồn `sdk_core/__init__.py` tại worktree
tự khai `1.5.0`; đây là nền đang được test, chưa chứng minh artifact phát
hành. Lead đối chiếu wheel SDK đã duyệt và alias trước khi cài gói sạch.

### Môi trường sạch và giới hạn kiểm

1. Lead cấp SDK Python >=1.5.0 đã duyệt, tương thích với Core; không lấy
   wheel candidate làm bản phát hành. Môi trường chỉ có engine mà thiếu
   SDK chưa chạy được.
2. Đối chiếu ba pin trong `requirements.lock` với runtime trước khi
   chuẩn bị môi trường. Tệp không có wheel hash; không dùng
   `--require-hashes`. Build backend `setuptools>=65` đã có từ mốc trước,
   chưa cài trong runtime này và không thuộc lock runtime.
3. Cấu hình build chỉ gom hai package engine/lib, manifest, contract,
   bài test và tài liệu; không gom mã Core/SDK/tri_thuc hoặc dữ liệu.
   Khai báo này chưa thay cho bằng chứng build/cài wheel thật.
4. Core cấp bootstrap, cấu hình Local, quy tắc model, hàm kiểm schema và
   bộ ghi qua RAM/SDK. Không tự đọc cấu hình thật hoặc tệp khóa. Đường
   tương thích ở lõi cổng dùng chung còn tồn tại; runtime bản 1 khóa
   Cloud, chỉ Local. Không cần khóa Cloud/Mask để kiểm bản 1.
5. Chạy test thuần/mock với Python/PYTHONPATH trong handoff. Kết quả
   mock không chứng minh Local AI thật, PostgreSQL, Windows ACL hoặc
   wheel độc lập đã được nghiệm thu; các ca này do lead thực hiện.

`README.md` hiện còn mô tả mốc chuyển vị trí/v1; tài
liệu hiện hành về dependency và contract là mục AI-LAT3 này cùng
`engine.json`. README ngoài danh sách sửa của lát này.

### Tập tệp hiện hành và SHA-256

Mốc nguồn nội bộ vòng 3: HEAD
`499e60ddd9ee823da90476d019708a44aafa6af4`. Đường gốc của từng hàng là
`engines/e_hoi_ai/<tệp trong gói>` tại mốc này; đích hiện hành vẫn ở
cùng đường dẫn. Bảng dưới ghi bytes hiện hành sau sửa vòng 4, khác với
lịch sử chuyển vị trí ở phần sau. Không thay băm nguồn lịch sử.

Bao phủ toàn bộ mã Python (kể cả `lib/`), manifest, contract và cấu hình
đóng gói/lock. Không đưa tests, cache hoặc tài liệu Markdown vào tập băm;
không tự băm `NGUON.md`. SHA-256 tính trên bytes thực, không chuẩn hóa
CRLF/LF. Khi thay tệp nguồn phải cập nhật đúng hàng và chạy lại kiểm băm.

| Tệp trong gói | SHA-256 hiện hành (bytes) | Thay đổi so mốc vòng 3 |
|---|---|---|
| `__init__.py` | `1cdfdc6b30ae154d8fe0c5091055d0dc8277b53ca43a0264b12c7c31c77bd7c7` | Giữ nguyên byte so mốc vòng 3. |
| `bi_mat.py` | `ea7344bbc32d26a82b6ac3587710a0e2aae10e00cdcb302623b95cf4f695335c` | Giữ nguyên byte so mốc vòng 3. |
| `chay.py` | `35a5a1a2428e1f4f0f71751244fa715c80729b8dcc4b63edd83043f97ec908af` | K3: đọc cấu hình theo manifest, kiểm địa chỉ trước readiness; giữ vòng nhận việc K2. |
| `contract/schemas.json` | `ca3e7fb96043751abe923a380e59253a19f6c02bdc14eb78b9b6d0a981c56c4e` | Giữ nguyên byte so mốc vòng 3. |
| `contract/vi_du.json` | `df0689d78588b67bc4a7b87d11321f1348c14c88b089b807d90587ef2417d215` | Giữ nguyên byte so mốc vòng 3. |
| `dto.py` | `998528300abbf72492bfbc606c6514fec7fa0e2a75a5a5cbef631ab57bb09bc6` | Giữ nguyên byte so mốc vòng 3. |
| `engine.json` | `a5aa2a42998fab634200e008fe3cece1643acc7e7e4ceef22e6aefb16c761c80` | K3: khai báo nhóm kết nối Local và tên hiển thị, giữ cấu hình đóng. |
| `hoi.py` | `12e24522145a243a5e007bb7a468bcbb82a75f1c21ac179f68f8124bd82cbbba` | Giữ nguyên byte so mốc vòng 3. |
| `lib/__init__.py` | `4228a5f0a36854e0660e9dba4963c7aa87b081f39541243965fe9fd5994c6b3e` | Giữ nguyên byte so mốc vòng 3. |
| `lib/ai_cuc_bo.py` | `06bc8c6e4037766a674f1da93f0bacfa1397eb0d8c5f8d53d8cdb298767a5e49` | Giữ nguyên byte so mốc vòng 3. |
| `lib/cong_ai.py` | `1d35ee32bcc70621b8aababaf77508296c8cc94a93977f04a99d1aa8ab17f571` | Giữ nguyên byte so mốc vòng 3. |
| `nhat_ky.py` | `d5ff7860d28e3f918125a7083b8bfa3930c28563d7bc7d907f7d08fb88084761` | Giữ nguyên byte so mốc vòng 3. |
| `pyproject.toml` | `718d6c83f6b4d5151be18b800335852e83beb318542201e7e6c94c1bb49c72d9` | Sửa vòng 4: ghi yêu cầu SDK tối thiểu. |
| `requirements.lock` | `57dc04188c126c4458630e928f1e179bcf87373efd5c150b4cd6eef104cc710b` | Giữ nguyên byte so mốc vòng 3. |

## Nguồn chuyển vị trí ban đầu — G3-GOI-01

Chuyển nội bộ từ HEAD nguồn `c11719b8` (nền nhánh lat/g3-goi-01), nguyên trạng nội dung (git rename):

| Đường gốc | Đích | Ghi chú |
|---|---|---|
| src/kho_tri_thuc/engines/e_hoi_ai/bi_mat.py | engines/e_hoi_ai/bi_mat.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoi_ai/chay.py | engines/e_hoi_ai/chay.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoi_ai/dto.py | engines/e_hoi_ai/dto.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoi_ai/hoi.py | engines/e_hoi_ai/hoi.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoi_ai/nhat_ky.py | engines/e_hoi_ai/nhat_ky.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_hoi_ai/engine.json | engines/e_hoi_ai/engine.json | nguyên trạng |
| src/kho_tri_thuc/core/contract/ky_thuat.json (3 schema) | engines/e_hoi_ai/contract/schemas.json | trích hoi_ai.v1, tra_loi_ai.v1, chung.v1; nội dung đồng nhất |

Các hàng trên là lịch sử chuyển vị trí; nội dung runtime/contract đã
được cập nhật ở các lát sau, không coi là bản byte-identical hiện tại.
