# Mẫu ngăn và cấu hình — NGAN-0

Các engine **CHÉP nguyên hai tệp `ngan.py`, `cau_hinh.py` vào gói Python của mình**;
không import từ repo `_chung`. Hai tệp chỉ dùng thư viện chuẩn, không đọc/ghi tệp,
không gọi mạng. Mỗi tiến trình engine có một ngăn gốc riêng. RAM mất khi dừng.

## Cách dùng

```python
from .ngan import NganBoNho, chon_ngan
from .cau_hinh import doc_cau_hinh

# SDK 2.0: khai_bao là danh sách bảng giống ngan_du_lieu ở đề nghị SDK 2.1.
# Chỉ gắn bản RAM khi SDK chưa cấp ngăn. Không thêm trường vào engine.json 2.0.
if getattr(app, "ngan", None) is None:
    app.ngan = NganBoNho(khai_bao)
ngan = chon_ngan(app)  # Giữ ngăn SDK có sẵn; cảnh báo RAM một lần ra stderr.

# SDK 2.1 cấp viec.ngan đã gắn ngữ cảnh. RAM giả lập bằng view pháp nhân.
ngan_viec = getattr(viec, "ngan", None)
if ngan_viec is None:
    ngan_viec = ngan.cho_phap_nhan(viec.ngu_canh["phap_nhan_id"])
with ngan_viec.lo() as lo:
    kq = lo.lay_hoac_tao("luot_abbyy", {"bam_noi_dung": "bam-DEMO"},
                         {"ma_tuong_quan": "DEMO-1", "so_trang": 1})
# Chỉ đọc kq.gia_tri / row_version / da_tao sau khi thoát with thành công.
cau_hinh = doc_cau_hinh(ngan, schema)  # schema là dict của schema trong gói.
```

`NganBoNho(khai_bao, phap_nhan_id=...)` cũng nhận ngữ cảnh ngay khi tạo.
`cho_phap_nhan(...)` tạo view dùng cùng RAM và cùng khóa luồng. Đây là cách giả
lập ngữ cảnh; phân quyền pháp nhân thật vẫn do Core chịu trách nhiệm.
View đã gắn P chỉ được tạo tiếp view P; chuyển sang Q bị từ chối.

Ngăn gốc hỗ trợ trực tiếp ví dụ §3 của đề nghị SDK 2.1, không cần tạo view:

```python
with ngan.lo() as lo:
    kq = lo.lay_hoac_tao("luot_abbyy",
        {"phap_nhan_id": "DEMO-P", "bam_noi_dung": "bam-DEMO"},
        {"ma_tuong_quan": "DEMO-1", "so_trang": 1})
ban = ngan.doc("luot_abbyy", {"phap_nhan_id": "DEMO-P", "ma_tuong_quan": "DEMO-1"})
trang = ngan.tim("luot_abbyy", loc={"phap_nhan_id": "DEMO-P"})
```

Với bảng `pham_vi: "phap_nhan"`, ngăn gốc lấy `phap_nhan_id` trong `khoa/loc`
cho **từng lệnh**, bắt buộc là chuỗi không rỗng sau khi bỏ khoảng trắng; chỉ truyền
trong `gia_tri` là chưa đủ. View tự điền P khi thiếu; truyền pháp nhân khác P trong
`khoa/loc/gia_tri` đều bị từ chối bằng `NganKhongHopLe`. Một lô trên ngăn gốc có thể
chứa nhiều pháp nhân và bảng phạm vi engine; mỗi lệnh vẫn được cô lập đúng phạm vi.

`chon_ngan(app)` tự gắn RAM vào `app.ngan` nếu có thể. App có `__slots__` không cho
gắn thuộc tính thì hàm vẫn trả ngăn, không gán; caller phải giữ đối tượng trả về và
tái sử dụng. Gọi lại trên app đó sẽ tạo RAM mới nếu app vẫn chưa có `ngan`.

## Quy ước tạm cần SDK 2.1 đối chiếu

- `doc(bang, khoa)` → `None` hoặc `BanGhi(gia_tri, row_version)`; khóa phải khớp
  đúng khóa chính hoặc một ràng buộc duy nhất đã khai. Bảng chưa khai bị từ chối.
- `tim(bang, loc=None, gioi_han=100, tiep=None)` → `TrangNgan(danh_sach, tiep)`;
  phần tử là `BanGhi`, lọc bằng so sánh bằng, trần 500. Phân trang theo khóa chính
  JSON, cursor gắn bảng/bộ lọc/pháp nhân. Không cam kết snapshot giữa các trang.
- Lô tối đa 100 lệnh; chỉ ghi khi thoát `with`, tất cả hoặc không gì cả.
  `them` nhận khóa chính; `lay_hoac_tao` nhận khóa chính hoặc khóa duy nhất,
  giá trị tạo phải đủ khóa chính và mọi ràng buộc duy nhất. Có rồi trả bản cũ.
- Khóa chính và từng ràng buộc `duy_nhat` có chỉ mục riêng theo bảng/pháp nhân.
  Commit dùng overlay dữ liệu và chỉ mục của lô, kiểm hết rồi áp dưới cùng khóa
  luồng; không sao chép toàn kho. Đầu vào, bản ghi đọc và kết quả vẫn là bản sao.
- So sánh theo giá trị JSON: `1` bằng `1.0`, `True` khác cả hai; áp dụng cả khóa,
  unique, lọc và JSON lồng nhau. Thứ tự thuộc tính object không ảnh hưởng; thứ tự
  phần tử array có ảnh hưởng. `None` trong trường `duy_nhat` **bị coi là trùng**,
  không có ngoại lệ kiểu SQL NULL. Thiếu trường unique thì yêu cầu không hợp lệ.
  Chỉ nhận JSON hữu hạn; chuỗi hoặc tên thuộc tính chứa surrogate lẻ không mã hóa
  được UTF-8 bị từ chối bằng `NganKhongHopLe`.
- `sua` là bản vá, giữ các trường chưa gửi; không đổi khóa chính/pháp nhân.
  `sua` và `xoa` bắt buộc `row_version` dạng số nguyên dương. Phiên bản không
  tái sử dụng sau xóa/tạo lại; phải coi là giá trị opaque, không tự tăng ở engine.
- Kết quả lệnh có `ban_ghi`, `gia_tri`, `row_version`, `da_tao`. Xóa trả ảnh trước
  xóa cùng phiên bản mới. Lỗi `NganXungDot` có mã `NGAN_XUNG_DOT`,
  `thu_lai_duoc=True`; lỗi đầu vào là `NganKhongHopLe`. Engine đổi lỗi sang
  `LoiNghiepVu(exc.ma, exc.thong_diep, thu_lai_duoc=exc.thu_lai_duoc)` tại biên SDK.
- Cấu hình là bản duy nhất ở bảng `cau_hinh`, khóa `{}`, giá trị trực tiếp là dict
  cấu hình. Bảng này được cấp sẵn, có thể khai lại với `khoa: []`, phạm vi engine.
  Thiếu bản ghi → `None`, engine trả `CHUA_CAU_HINH` cho việc cần cấu hình.
  Default được điền trên bản sao; không ghi ngược ngăn. Cấu hình sai →
  `CauHinhKhongHopLe` (đổi sang `LoiNghiepVu` tương tự).
  `doc_cau_hinh(ngan, schema)` chỉ trả dict hoặc `None`, **không trả `row_version`**;
  khi cần CAS, dùng `ngan.doc("cau_hinh", {})` để lấy phiên bản cùng bản ghi.
  Schema cấu hình trong gói nên khai `additionalProperties: false` ở gốc, chỉ
  cho phép các trường cấu hình đã khai, tránh nhận nhầm trường hệ thống.

## API cuối cùng cho AI-8 / OCR-8 / MASK-3b

```python
NganBoNho(khai_bao=(), *, phap_nhan_id=None)
chon_ngan(app)
Ngan.doc(self, bang, khoa) -> BanGhi | None
Ngan.tim(self, bang, loc=None, gioi_han=100, tiep=None) -> TrangNgan
Ngan.lo(self) -> LoNgan
Ngan.cho_phap_nhan(self, phap_nhan_id) -> Ngan
LoNgan.__enter__(self)
LoNgan.__exit__(self, loai_loi, loi, vet)
LoNgan.them(self, bang, khoa, gia_tri) -> KetQuaLenh
LoNgan.sua(self, bang, khoa, gia_tri, *, row_version) -> KetQuaLenh
LoNgan.xoa(self, bang, khoa, *, row_version) -> KetQuaLenh
LoNgan.lay_hoac_tao(self, bang, khoa, gia_tri) -> KetQuaLenh
BanGhi(gia_tri: dict, row_version: int)
TrangNgan(danh_sach: list[BanGhi], tiep: str | None)
doc_cau_hinh(ngan, schema)
```

`KetQuaLenh()` có các property `ban_ghi`, `gia_tri`, `row_version`, `da_tao`, chỉ
đọc sau commit thành công. Ngoại lệ không nhận tham số: `NganXungDot()`,
`NganKhongHopLe()`, `CauHinhKhongHopLe()`; cùng có `ma/thong_diep/thu_lai_duoc`.

Bộ kiểm schema hỗ trợ schema boolean, `type` đơn (7 kiểu JSON Schema),
`properties`, `required`, `additionalProperties`, `items`, `default`, `enum`,
`const`, `pattern`, `minLength/maxLength`, `minimum/maximum`,
`exclusiveMinimum/exclusiveMaximum`, `minItems/maxItems`, `uniqueItems`,
`minProperties/maxProperties`; cho phép các annotation `$schema`, `$id`,
`$comment`, `title`, `description`, `examples`. Từ khóa khác (kể cả `$ref`,
`format`, `oneOf`) bị từ chối, không tải schema từ mạng. `pattern` dùng Python `re`.

## Kiểm và so băm

Trong test của engine, so **cả hai tệp** với bản chung:

```python
from hashlib import sha256

for ten in ("ngan.py", "cau_hinh.py"):
    assert sha256((goi_python / ten).read_bytes()).digest() == sha256(
        (goc_repo / "_chung" / "mau-ma" / ten).read_bytes()).digest()
```

Thêm factory vào `tests/conftest.py::CAC_BAN_NGAN` để chạy cùng hợp đồng cho bản
SDK sau này (adapter chuẩn hóa kết quả/ngoại lệ nếu cần). Mỗi factory nhận danh
sách khai báo, tạo ngăn độc lập và hỗ trợ view pháp nhân. Không sửa ca hợp đồng.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'
.venv/Scripts/python -m pytest _chung/mau-ma/tests -q --basetemp=.pytest-tmp
.venv/Scripts/python _chung/mau-ma/tests/kiem_doc_lap.py
```

Trên Linux dùng `.venv/bin/python` và đặt hai biến môi trường tương đương.
Pytest 9.1.1 có sẵn được dùng qua venv `--system-site-packages`, không tải mạng
hoặc thêm dependency runtime. SDK 2.0.0 cài offline, SHA-256 khớp `SHA256SUMS.txt`.

## Trạng thái

- **15/11/2026 — NGAN-0: đã làm và kiểm bản RAM; PR: chờ lead mở.** Không sửa engine.
- Bộ test và kết quả cuối ghi tại `../docs/VIEC.md`; kiểm đồng thời gồm lấy hoặc
  tạo, CAS và 8 luồng × 50 vòng cùng khóa. Test hiệu năng 3000 `them` đơn lẻ +
  200 `lay_hoac_tao` tại 3000 hàng chạy mặc định, bắt buộc dưới 2 giây.
- SDK DEMO: **đã kiểm bằng Core giả (CoreGia)**. Hợp đồng ngăn kiểm trực tiếp
  trên `NganBoNho`; CoreGia/MayChuGia 2.0 chưa có ngăn, chưa kiểm ngăn Core thật.
- Chưa có lưu bền, TTL, migration, HTTP, kiểm toán và sự kiện đổi cấu hình;
  phần này chờ Core/SDK 2.1, xem “Cần Core” trong `../docs/VIEC.md`.
