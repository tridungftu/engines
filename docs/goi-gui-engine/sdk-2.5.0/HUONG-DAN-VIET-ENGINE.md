# Hướng dẫn viết engine — SDK 2.4.0

*Cho người viết engine (các project engine). Cập nhật 20/11/2026 cho SDK 2.4.0 (chờ Anh duyệt phát hành).*

## Tóm tắt

- **SDK 2.4.0 chỉ thêm, giữ tương thích với 2.3.0:** phiếu vẫn dùng `phien_ban_manifest: 2`, API vẫn là `/api/v1/engine/…`. Phần ngăn dữ liệu và cấu hình ở mục 9; thư viện Python ngoài ở mục 10. Engine không tự đổi hợp đồng; thấy thiếu thì báo lead.
- Viết một engine gồm 6 bước: **chuẩn bị SDK để phát triển → điền phiếu → viết hàm → tự kiểm bằng Core giả → chạy engine mẫu → nối Core thật.**
- Engine dùng SDK và có thể kèm thư viện Python ngoài dưới dạng wheel để Core cài offline. Không cần thông tin đăng nhập cơ sở dữ liệu.

## 1. SDK khi phát triển và khi chạy trên Core

Với engine `cuc_bo`, Core tự cấp SDK từ đúng bản Core đang chạy; Admin **không cần cài wheel SDK tay**. Mã engine luôn import `kho_tri_thuc_sdk`, không import dự phòng từ `src` của Core. Các bước cài dưới đây dành cho môi trường phát triển hoặc engine chạy tay ở máy khác.

Thư mục phát hành gồm:

| Tệp | Là gì |
|---|---|
| `kho_tri_thuc_sdk-2.4.0-py3-none-any.whl` | Gói SDK (phần module và phần engine) |
| `*.whl.sha256`, `SHA256SUMS.txt` | Mã băm để kiểm gói không bị đổi |
| `HUONG-DAN-VIET-ENGINE.md` | Tệp này |
| `MAU-PHIEU-ENGINE.md` | Giải thích từng trường của phiếu, có phiếu mẫu |
| `THAY-DOI-2.4.0.md` | Ghi chú thay đổi của phiên bản |
| `engine-demo\` | Các engine DEMO mẫu, có `e_demo_ngan` và `e_demo_thu_vien` |

Cài vào môi trường riêng của project engine (Python 3.11 trở lên):

```
certutil -hashfile kho_tri_thuc_sdk-2.4.0-py3-none-any.whl SHA256
python -m venv .venv
.venv\Scripts\activate
python -m pip install --no-index --no-deps <thư mục phát hành>\kho_tri_thuc_sdk-2.4.0-py3-none-any.whl
python -c "import kho_tri_thuc_sdk; print(kho_tri_thuc_sdk.__version__)"
```

- So kết quả `certutil` với dòng của tệp wheel trong `SHA256SUMS.txt`. Kết quả lệnh cuối phải là `2.4.0`.
- `--no-deps` đủ cho engine vì phần engine của SDK chỉ dùng thư viện chuẩn. Các gói thêm ghi trong wheel (`cryptography`, `jsonschema`) chỉ phần module cần.

## 2. Điền phiếu `engine.json`

Đọc `MAU-PHIEU-ENGINE.md`. Cách nhanh nhất là chép một engine trong `engine-demo\` rồi sửa:
- đổi `ma` thành mã của mình (`e_…`, tối đa 31 ký tự);
- đổi tên thư mục gói Python và `diem_vao`;
- khai các năng lực: nhận gì, trả gì, giới hạn, ô cài đặt bước.

Gói gửi Core **không được có** `__pycache__` hoặc `.pyc`, liên kết tượng trưng, tệp quá lớn. Core từ chối khi cài.

## 3. Viết hàm

```python
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

app = Engine.tu_khai_bao("engine.json")


@app.nang_luc("van_ban.dem_tu@1")
def dem_tu(viec):
    dong = viec.dau_vao["van_ban"].splitlines()
    viec.tien_do(50, "Đang đếm từ")
    return {"loai": "truong", "truong": {"so_tu": sum(len(d.split()) for d in dong),
                                         "so_dong": len(dong)}}


if __name__ == "__main__":
    app.chay()
```

Đối tượng `viec` có các thành phần sau (chi tiết ở mục 7 của mẫu phiếu):

| Thành phần | Dùng để |
|---|---|
| `dau_vao` | Phong bì dữ liệu vào |
| `tham_so` | Giá trị ô cài đặt bước, đã điền mặc định |
| `ngu_canh` | Thông tin việc |
| `tien_do(%, câu)` | Báo tiến độ; tự dừng hàm khi việc bị hủy |
| `kiem_huy()` | Dừng hàm nếu việc đã bị hủy |
| `mo_tep(tep_id)` | Đọc tệp vào |
| `tai_tep_ra(tên, bytes, mime)` | Gửi tệp kết quả lên Core |

## 4. Tự kiểm bằng Core giả (không cần Core thật)

```
python -m kho_tri_thuc_sdk.thu <thư mục gói>
```

- Lệnh kiểm phiếu, rồi chạy mọi ví dụ `chay_thu_demo` trên Core giả trong bộ nhớ.
- Mỗi ví dụ in `[ĐẠT]` hoặc `[LỖI]`. Phiếu sai thì in từng câu lỗi tiếng Việt.
- Mã thoát: `0` là mọi ví dụ đều đạt.

Trong test tự viết của project engine:

```python
from kho_tri_thuc_sdk.thu import CoreGia
kq = CoreGia().chay_thu(app, "van_ban.dem_tu@1", {"loai": "van_ban", "van_ban": "Một hai\nBa"})
assert kq["trang_thai"] == "XONG"
```

`CoreGia` còn giả lập được hủy việc (`huy`), mất phản hồi để kiểm gửi lại (`gay_mat_xac_nhan`), và tệp vào/ra (`them_tep`, `doc_tep`). `MayChuGia` là máy chủ HTTP giả trên máy cục bộ, để thử đường HTTP thật.

## 5. Chạy 4 engine DEMO mẫu

```
cd <thư mục phát hành>\engine-demo
python -m kho_tri_thuc_sdk.thu e_demo_doc_tep
python -m kho_tri_thuc_sdk.thu e_demo_chu_hoa
python -m kho_tri_thuc_sdk.thu e_demo_dem_tu
python -m kho_tri_thuc_sdk.thu e_demo_ngan
```

Cả 4 phải in `[ĐẠT]`. Ghép theo thứ tự đọc tệp → chữ hoa → đếm từ thì thành quy trình 3 bước (mẫu phiếu mục 5). `e_demo_ngan` minh họa ngăn, CAS, trường bí mật và cấu hình.

## 6. Chạy engine thật nối Core

- **Engine `cuc_bo`:** Core tự chạy lệnh `diem_vao` trong thư mục gói, rồi ghi một dòng `{"core_url", "khoa", "instance"}` vào stdin. `app.chay()` tự đọc dòng này, báo sẵn sàng và nhận việc. Người viết engine không phải làm gì thêm.
- **Chạy tay** (thử với Core thật, hoặc engine `tu_xa` ở máy khác): đặt các biến môi trường dưới đây, rồi chạy `python -m <gói>.chay` trong thư mục gói.
  - `KTT_CORE_URL`
  - `KTT_ENGINE_KHOA`: Admin chép từ màn Quản lý engine.
  - `KTT_ENGINE_INSTANCE`: không bắt buộc.
- `http://` chỉ dùng cho máy cục bộ; máy khác phải dùng `https://`. Khóa engine không bao giờ ghi vào phiếu, mã, nhật ký hay git.
- **SDK tự lo:** nhận việc, gia hạn, dừng khi bị hủy, gửi lại tối đa 3 lượt với cùng khóa chống trùng, kiểm kết quả đúng phiếu.

## 7. Báo lỗi

- `raise LoiNghiepVu("MA_LOI", "Câu tiếng Việt cho người dùng.", thu_lai_duoc=False)`: câu hiện cho người dùng, mã nằm trong "Chi tiết hỗ trợ".
- `raise ChuaRo("<mã tương quan>")`: nguồn bên ngoài đã nhận việc nhưng chưa trả lời. Không báo thành công giả.
- Lỗi khác: SDK đổi thành câu chung "Engine gặp lỗi khi xử lý việc này." Chi tiết kỹ thuật chỉ in ra nhật ký của engine.
- Vượt giới hạn trong phiếu thì Core từ chối, không cắt bớt ngầm. Quá thời hạn bước thì Core cắt việc.

## 8. Engine không được làm

1. Gọi engine khác. Mọi trung chuyển đi qua Core.
2. Kết nối cơ sở dữ liệu hay chạy SQL.
3. Import `kho_tri_thuc.*` của Core. Chỉ dùng `kho_tri_thuc_sdk`.
4. Ghi bí mật hay khóa vào phiếu, mã, nhật ký.
5. Dùng dữ liệu thật để chạy thử. Chỉ dùng DEMO.
6. Báo lỗi bằng câu kỹ thuật, lộ đường dẫn, khóa hay dữ liệu nghiệp vụ.

## 9. Ngăn dữ liệu và cấu hình (SDK 2.2)

Mẫu đầy đủ trong repo: `goi-demo\engine\e_demo_ngan\`; trong bộ phát hành: `engine-demo\e_demo_ngan\`. Phiếu, SQL 001/002, kiểm kê băm, schema cấu hình và mã engine phải đi cùng nhau. Engine chỉ gọi SDK; Core cài SQL trong schema `eng_<ma>` và giữ kết nối CSDL.

### 9.1 Đọc, tìm và ghi lô

`app.ngan` dùng cho bảng phạm vi `engine`, sau khi engine đã kết nối Core. Trong hàm năng lực, dùng `viec.ngan`: SDK tự gửi `X-KTT-Viec` bằng `viec.id` (id lượt đang giữ), Core lấy pháp nhân từ lượt đó. Bảng `dem_goi` của mẫu có phạm vi `phap_nhan`, vì vậy phải dùng `viec.ngan`; không truyền pháp nhân tùy ý.

Ví dụ với bảng `dinh_danh` của mẫu (dùng trong lúc engine đã kết nối):

```python
with app.ngan.lo() as lo:
    lo.them("dinh_danh", {"gia_tri": "CAN-CUOC-DEMO-001", "bi_danh": "DEMO-001"})
ket_qua = lo.ket_qua  # list[KetQuaLenh]: id, row_version, da_tao
ban_ghi = app.ngan.doc("dinh_danh", {"gia_tri": "CAN-CUOC-DEMO-001"})
trang = app.ngan.tim("dinh_danh", loc={"bi_danh": "DEMO-001"}, gioi_han=100)
```

| Lời gọi | Kết quả / ràng buộc |
|---|---|
| `doc(bang, khoa, *, gom_het_han=False)` | `BanGhi` có `.id`, `.gia_tri` (dict), `.row_version`, hoặc `None`. |
| `tim(bang, *, loc=None, sap_xep=None, gioi_han=100, tiep=None, gom_het_han=False)` | `Trang` có `.danh_sach` (list `BanGhi`) và `.tiep`. `loc` so bằng; `gioi_han` từ 1–500. Truyền lại `.tiep` để lấy trang sau. |
| `lo()` | Gửi khi ra khỏi `with` bình thường; ngoại lệ trong `with` thì không gửi. Một lệnh lỗi thì cả lô không ghi. |
| `lo.them(bang, gia_tri)` | Tạo mới, đủ trường bắt buộc. |
| `lo.sua(bang, khoa, gia_tri, *, row_version)` | Sửa một phần; bắt buộc CAS bằng phiên bản vừa đọc. |
| `lo.lay_hoac_tao(bang, khoa, gia_tri)` | Có bản ghi theo khóa thì trả bản cũ (`da_tao=False`), chưa có thì tạo từ khóa và giá trị. |

Mỗi lô có tối đa **100 lệnh**. SDK sinh khóa chống trùng cho từng lô; gửi lại do lỗi đường truyền giữ nguyên khóa và nội dung. Không có thao tác xóa được phép; gọi xóa bị từ chối bằng `NGAN_KHONG_XOA`.

### 9.2 CAS và thử lại có giới hạn

Hai lượt cùng sửa thì phiên bản cũ nhận HTTP **409 `NGAN_XUNG_DOT`**, SDK ném `NganXungDot` (`thu_lai_duoc=True`). Phải **đọc lại, tính lại**, rồi tạo lô mới; không gửi mãi giá trị tính từ bản cũ. Mẫu dưới đây rút từ `e_demo_ngan\chay.py`, tối đa 5 lần thử lại sau lần đầu:

```python
from datetime import datetime, timedelta, timezone
from kho_tri_thuc_sdk.engine import NganXungDot

# Trong hàm năng lực nhận viec:
khoa = {"ngay": datetime.now(timezone(timedelta(hours=7))).date().isoformat()}
SO_LAN_THU_LAI = 5
for lan in range(SO_LAN_THU_LAI + 1):
    viec.kiem_huy()
    try:
        with viec.ngan.lo() as lo:
            lo.lay_hoac_tao("dem_goi", khoa, {"so_lan": 0})
        ban_ghi = viec.ngan.doc("dem_goi", khoa)
        so_lan = int(ban_ghi.gia_tri["so_lan"]) + 1
        with viec.ngan.lo() as lo:
            lo.sua("dem_goi", khoa, {"so_lan": so_lan},
                   row_version=ban_ghi.row_version)
        break
    except NganXungDot:
        if lan == SO_LAN_THU_LAI:
            raise
```

`giu_toi_da_ngay` trong phiếu (mẫu: 90) đặt lại `het_han_luc` khi tạo hoặc sửa. Hết hạn chỉ **ẩn** khỏi đọc/tìm, Core không tự xóa dòng. Đọc lại bằng `viec.ngan.doc("dem_goi", khoa, gom_het_han=True)` hoặc `tim(..., gom_het_han=True)`.

### 9.3 Trường bí mật và cấu hình

`dinh_danh.gia_tri` khai `bi_mat: true`: engine ghi bản rõ, Core mã hóa và tìm theo đúng giá trị qua băm. Đọc/tìm trả `gia_tri: null` (Python: `None`) kèm `gia_tri_da_ma_hoa: true`; không trả bản mã hay cột băm. **Không có đường Core giải mã hộ engine** (CĐ-36). Mask trả **bí danh hoặc mã tham chiếu**; bản rõ chỉ người có quyền xem qua cửa Xem dữ liệu của Core.

Cấu hình theo `cau_hinh.schema` của gói, không chứa bí mật. `app.cau_hinh` là dict đã kiểm và điền mặc định khi kết nối; `viec.cau_hinh` là bản chụp lúc nhận việc. Mẫu dùng `tien_to` (mặc định `"DEMO"`) để tạo bí danh:

```python
# Trong hàm năng lực của e_demo_ngan:
bi_danh = f'{viec.cau_hinh.get("tien_to", "DEMO")}-{viec.id}'
```

Ví dụ bổ sung dùng cùng trường `tien_to` của mẫu, đăng ký trước `app.chay()`:

```python
tien_to_hien_tai = "DEMO"

@app.khi_doi_cau_hinh
def doi_cau_hinh(cau_hinh_moi):
    global tien_to_hien_tai
    tien_to_hien_tai = cau_hinh_moi.get("tien_to", "DEMO")

# Khi đang xử lý việc, có thể đọc cấu hình hiện tại của engine:
# tien_to = app.cau_hinh.get("tien_to", "DEMO")
```

Callback nhận một dict khi SDK nhận thấy `phien_ban_cau_hinh` mới hơn trong phản hồi nhận việc, đọc lại cấu hình rồi gọi hàm; không phải thông báo đẩy tức thời. Giá trị lúc khởi động đọc từ `app.cau_hinh`, callback không thay bước khởi tạo đó.

### 9.4 SQL của gói và kiểm kê băm

**Không dùng `json`/`jsonb` trong `eng_*`.** Mỗi ngăn là bảng thường; dữ liệu chi tiết tách thành cột hoặc bảng. Ngoại lệ JSON cho cấu hình nằm trong Core, không phải ngăn nghiệp vụ.

SQL 001 do gói tự viết phải có các cột chuẩn sau; không khai lại chúng trong `truong[]`:

| Cột | Khai báo SQL |
|---|---|
| `id` | `uuid PRIMARY KEY` |
| `phap_nhan_id` | `uuid NOT NULL` nếu phạm vi `phap_nhan`; `uuid` cho phạm vi `engine` (Core giữ `NULL`). |
| `row_version` | `bigint NOT NULL DEFAULT 1` |
| `tao_luc` | `timestamptz NOT NULL DEFAULT now()` |
| `sua_luc`, `het_han_luc` | `timestamptz` cho phép `NULL` |
| `viec_id` | `uuid` cho phép `NULL` |

Kiểu nghiệp vụ phải khớp phiếu: `van_ban` → `text`; `so` → `numeric`; `so_tien` → `numeric(20,2)` cùng `<ma>_tien_te text`; `ngay` → `date`; `thoi_diem` → `timestamptz`; `co_khong` → `boolean`. Trường `bi_mat` chỉ dùng `van_ban`, lưu bằng hai cột `bytea`: `<ma>` và `<ma>_bam`. Cột bắt buộc và cột kèm tương ứng phải `NOT NULL`. `duy_nhat` phải có UNIQUE khớp SQL; trường bí mật dùng cột băm trong UNIQUE.

Chuỗi SQL bắt đầu `001_…sql`, tăng liên tục, không lỗ số. Mẫu `001_tao_ngan.sql` tạo hai bảng và `UNIQUE (phap_nhan_id, ngay)`; nâng gói từ 1.0.0 lên 1.1.0 giữ nguyên byte tệp 001, thêm `002_them_cot.sql`:

```sql
ALTER TABLE eng_e_demo_ngan.dem_goi ADD COLUMN ghi_chu text;
COMMENT ON COLUMN eng_e_demo_ngan.dem_goi.ghi_chu IS 'Ghi chú bổ sung khi nâng gói DEMO';
```

Đồng thời thêm `ghi_chu` vào phiếu, đặt `du_lieu.goi_migration.phien_ban_du_lieu: 2`, cập nhật kiểm kê `sql/kiem_ke.json`: `phien_ban` trùng phiên bản gói, mỗi tệp có `duong_dan` tương đối từ gốc gói, `bytes`, `sha256` của byte thật; kiểm kê gồm mọi tệp của gói trừ chính nó. Xem cấu trúc đầy đủ ở mục 11 của mẫu phiếu. Không sửa migration đã áp; Core chỉ chạy số mới và đối chiếu băm số cũ.

**Bộ duyệt `kiem_sql_ngan.py` chỉ cho bốn dạng lệnh:**

| Cho phép | Giới hạn |
|---|---|
| `CREATE TABLE <schema>.<bang> (...)` | Bảng đã khai; cột có `NOT NULL`, `DEFAULT`, `PRIMARY KEY`, `UNIQUE`, `REFERENCES <schema>.<bang>(id)`; cuối danh sách có thể thêm `PRIMARY KEY (...)`, `UNIQUE (...)`. |
| `ALTER TABLE <schema>.<bang> ADD COLUMN ...` | Chỉ thêm cột; cột mới có `NOT NULL` hoặc `PRIMARY KEY` phải kèm `DEFAULT`. |
| `CREATE [UNIQUE] INDEX [ten] ON <schema>.<bang> [USING btree] (...)` | Chỉ danh sách tên cột, không biểu thức hay chỉ mục một phần. |
| `COMMENT ON TABLE ... IS '...'`, `COMMENT ON COLUMN ... IS '...'` | Chỉ chuỗi văn bản, trên bảng đã khai. |

- Kiểu được duyệt: `uuid`, `text`, `bigint`, `integer`, `numeric`, `boolean`, `date`, `timestamptz`, `bytea`. `numeric(p,s)` nhận `p` 1–1000, `s` −1000–1000. Qua duyệt tĩnh vẫn phải khớp kiểu phiếu khi cài.
- `DEFAULT` chỉ nhận hằng chữ/số, số có dấu, `true`/`false`/`null`, `now()`, `gen_random_uuid()` (hai hàm có thể thêm `pg_catalog.`).
- **Cấm mọi lệnh ngoài bốn dạng trên:** gồm `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`, `DROP`, `DO`, tạo function/trigger/schema, `GRANT`/`REVOKE`, `SET`/`RESET`, `COPY`, `CALL`. Cấm `ALTER` đổi kiểu, bỏ/đổi tên cột, thêm ràng buộc riêng.
- Các tập cấm trong code: kiểu `json`, `jsonb`, `serial`, `bigserial`; ràng buộc `check`, `generated`, `identity`, `constraint`, `collate`, `deferrable`; tùy chọn `inherits`, `partition`, `tablespace`, `with`, `unlogged`, `temp`, `temporary`, `where`, `include`, `using` ngoài vị trí `USING btree` của chỉ mục. `CONCURRENTLY` và `IF NOT EXISTS` ở chỉ mục cũng bị chặn.
- Bảng luôn ghi đủ schema được cấp và phải có trong `ngan_du_lieu[]`. Tối đa 256 KiB UTF-8 và 200 lệnh mỗi tệp. Không nhận dollar-quote, chuỗi tiền tố `E`/`U&`, dấu `;` trong chuỗi, thoát nháy bằng backslash, chú thích khối lồng nhau hay ký tự điều khiển ngoài tab/CR/LF.
- Mã lỗi duyệt: `SQL_CU_PHAP`, `SQL_LENH_CAM`, `SQL_KIEU_CAM`, `SQL_RANG_BUOC_CAM`, `SQL_NGOAI_SCHEMA`, `SQL_BANG_CHUA_KHAI`. Duyệt tĩnh không thay hậu kiểm cấu trúc CSDL lúc cài.

### 9.5 Thử ngăn bằng CoreGia

Từ thư mục gói `e_demo_ngan` (gói Python của mẫu nằm trong đường import), với SDK 2.2.0 đã cài:

```python
from kho_tri_thuc_sdk.thu import CoreGia
from e_demo_ngan.chay import app

core = CoreGia(app.phieu, thu_muc_goi=app.thu_muc_goi)
core.dat_cau_hinh(app.ma, {"tien_to": "DEMO"})
core.gay_xung_dot_ngan("dem_goi", so_lan=1)
kq = core.chay_thu(app, "dem.goi@1",
                   {"loai": "van_ban", "van_ban": "DD:CAN-CUOC-DEMO-001"})
assert kq["trang_thai"] == "XONG"
assert kq["ket_qua"]["truong"]["so_lan"] == 1
assert len(core.xem_ngan(app.ma, "dinh_danh")) == 1
assert app.cau_hinh["tien_to"] == "DEMO"
ban_ghi = app.ngan.doc("dinh_danh", {"gia_tri": "CAN-CUOC-DEMO-001"})
assert ban_ghi.gia_tri["gia_tri"] is None
```

`CoreGia` thử ngữ nghĩa lô nguyên tử, CAS, duy nhất, pháp nhân, hết hạn và trường bí mật trong bộ nhớ; không cài hay thực thi SQL. `xem_ngan(ma_engine, bang)` dành riêng cho test, xem được cả dòng hết hạn và bản rõ DEMO; không dùng nó thay API đọc của engine. Có thể thử đường HTTP bằng `MayChuGia`. Kiểm việc cài/nâng SQL trên PostgreSQL DEMO do lead thực hiện riêng.

## 10. Thư viện Python ngoài (SDK 2.4.0)

Gói có phụ thuộc ngoài SDK khai trong `engine.json`:

```json
"tuong_thich": {"core": ">=2.0.0 <3.0.0", "api": "v1", "sdk": ">=2.4.0 <3.0.0"},
"phu_thuoc_python": {"lock": "requirements.lock", "wheels": "wheels"}
```

- `requirements.lock` **chỉ ASCII**, không BOM, không khai coding. Mỗi dòng thư viện đúng dạng `ten==ban --hash=sha256:<64 ký tự hex thường>`. Ghim đủ phụ thuộc trực tiếp và gián tiếp; không URL, marker, tham số pip, nối dòng bằng `\` hay chú thích giữa dòng. Có thể để dòng trống hoặc dòng chú thích ASCII riêng, không chứa khai coding.
- `wheels/` chỉ chứa `.whl` khớp tên, phiên bản và SHA-256 trong lock; mỗi thư viện một wheel, không thừa hoặc thiếu, không chứa sdist hay thư mục con. Chọn wheel phù hợp Python và hệ điều hành máy chạy engine.
- Cấm tên `kho_tri_thuc*`, kể cả cách viết tương đương bằng dấu `-` hoặc `.`: đây là vùng tên dành riêng cho Core và SDK. Không kèm wheel SDK trong phụ thuộc.
- Core kiểm tĩnh trước khi cài, sau đó cài offline từ bản wheel đã kiểm và lock sạch vào **`<gói đã cài>.thu-vien`**, thư mục riêng cạnh gói, không sửa cây gói đã băm và không cài vào Python chung. Không tự tạo `thu-vien/` trong gói để thay cho bước này.
- **SDK do Core cấp**, Admin không cần cài wheel SDK tay. Engine import `kho_tri_thuc_sdk`; SDK đứng trước thư viện riêng trên PYTHONPATH. Core kiểm khoảng `tuong_thich.sdk` trước khi nhận gói.

Mẫu đầy đủ: `e_demo_thu_vien/` kèm `ktt-demo-thu-vien` 1.0.0 thuần Python. Chạy `python -B -X utf8 e_demo_thu_vien/tao_wheel_demo.py` để dựng lại wheel tất định và đối chiếu băm với lock. Trên Core thử: nhập gói → Xem trước thư viện → Duyệt cài → Bật → Chạy thử DEMO; không cần pip tay. Khi tự thử bằng CoreGia trên máy phát triển, tác giả chuẩn bị SDK và phụ thuộc trong môi trường thử riêng trước; CoreGia không cài phụ thuộc.
