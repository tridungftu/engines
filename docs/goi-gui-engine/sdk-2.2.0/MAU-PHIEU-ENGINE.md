# Mẫu phiếu engine — `engine.json` 2.0

*Bản 1, 08/11/2026 (W5, lát L2.1). Theo `docs\HOP-DONG-CONG.md` phần (b), (c). Schema máy kiểm: `src\kho_tri_thuc\core\contract\manifest_engine_v2.json`.*

## Tóm tắt

- **Một engine là một thư mục gói, đặt ngoài Core.** Core chỉ đọc phiếu `engine.json` để biết engine **nhận loại dữ liệu gì, trả loại gì, giới hạn ra sao, có ô cài đặt bước nào**. Thêm engine không sửa dòng nào của Core.
- **Viết một engine gồm 3 việc:** (1) điền phiếu; (2) viết mỗi năng lực một hàm Python, chỉ dùng SDK; (3) kèm dữ liệu DEMO để chạy thử.
- **3 engine DEMO** trong thư mục này là mẫu chép lại được: `e_demo_doc_tep` (tệp → văn bản), `e_demo_chu_hoa` (văn bản → văn bản), `e_demo_dem_tu` (văn bản → bộ trường). Ghép theo thứ tự đó thành quy trình 3 bước.

## 1. Thư mục gói

```
e_demo_dem_tu\               ← thư mục gói, tên = mã engine
├── engine.json              ← phiếu đăng ký (mục 2–6)
├── README.md                ← một đoạn mô tả
├── demo\mau.txt             ← dữ liệu DEMO, không dùng dữ liệu thật
└── e_demo_dem_tu\           ← gói Python
    ├── __init__.py
    └── chay.py              ← mã engine (mục 7)
```

Khi cài, Core đọc toàn bộ gói một lần và từ chối gói có liên kết tượng trưng, tệp quá lớn, hoặc tệp biên dịch sẵn (`__pycache__`, `.pyc`). Hãy xóa các thư mục `__pycache__` trước khi gửi gói.

## 2. Phiếu mẫu đầy đủ

```json
{
  "phien_ban_manifest": 2,
  "loai": "engine",
  "ma": "e_demo_dem_tu",
  "ten": "Đếm từ và dòng (DEMO)",
  "phien_ban": "1.0.0",
  "tuong_thich": {"core": ">=2.0.0 <3.0.0", "api": "v1", "sdk": ">=2.0.0 <3.0.0"},
  "che_do_chay": "cuc_bo",
  "diem_vao": {"lenh": ["{python}", "-m", "e_demo_dem_tu.chay"], "thu_muc": "."},
  "nang_luc": [
    {
      "ma": "van_ban.dem_tu@1",
      "ten": "Đếm từ",
      "nhan": ["van_ban"],
      "tra": "truong",
      "truong_ra": [
        {"ma": "so_tu", "ten": "Số từ", "kieu": "so"},
        {"ma": "so_dong", "ten": "Số dòng", "kieu": "so"}
      ],
      "gioi_han": {"ky_tu_toi_da": 1000000, "thoi_han_giay": 60},
      "huy_duoc": true,
      "tham_so": [
        {"ma": "bo_dong_trong", "ten": "Bỏ dòng trống khi đếm", "kieu": "co_khong", "mac_dinh": true,
         "mo_ta": "Bật thì dòng chỉ có khoảng trắng không được tính vào số dòng."}
      ]
    }
  ],
  "loai_du_lieu_rieng": [],
  "tai_nguyen": {"so_viec_dong_thoi": 1},
  "readiness": {"thoi_han_giay": 30},
  "chay_thu_demo": [
    {"nang_luc": "van_ban.dem_tu@1", "ten": "Đếm từ đoạn văn DEMO",
     "dau_vao": {"loai": "van_ban", "van_ban": "Dòng một DEMO\nDòng hai DEMO"}, "tham_so": {}},
    {"nang_luc": "van_ban.dem_tu@1", "ten": "Đếm cả dòng trống (DEMO)",
     "dau_vao": {"loai": "van_ban", "van_ban": "Dòng một DEMO\n\nDòng ba DEMO"},
     "tham_so": {"bo_dong_trong": false}}
  ],
  "bi_mat": [],
  "webhook": null
}
```

## 3. Giải thích từng trường

### 3.1 Danh tính

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `phien_ban_manifest` | có | Luôn là `2`. |
| `loai` | có | Luôn là `"engine"`. |
| `ma` | có | Mã engine, dạng `e_` + chữ thường không dấu, số, gạch dưới (4–31 ký tự). Ví dụ `e_demo_dem_tu`. Không đổi sau khi cài. |
| `ten` | có | Tên tiếng Việt hiện cho người dùng và Admin. |
| `phien_ban` | có | Số phiên bản dạng `1.0.0`. Sửa engine thì tăng số. |
| `tuong_thich` | có | Khoảng phiên bản Core (`core`), API (`api`, luôn `"v1"`), SDK (`sdk`, không bắt buộc) mà engine chạy được. |

### 3.2 Cách chạy

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `che_do_chay` | có | `cuc_bo`: Core tự khởi động engine trên cùng máy. `tu_xa`: engine chạy ở máy khác và tự gọi Core qua mạng có xác thực. |
| `diem_vao` | khi `cuc_bo` | Lệnh Core dùng để chạy engine, **tính trong thư mục gói**. Lệnh phải bắt đầu bằng `{python}` (Python do Core chọn), dạng `["{python}", "-m", "<module>"]` hoặc `["{python}", "<tệp>.py"]`, và tệp đó phải nằm trong gói. `thu_muc` mặc định `"."`. |
| `tai_nguyen.so_viec_dong_thoi` | không (mặc định 1) | Số việc engine làm cùng lúc. |
| `readiness.thoi_han_giay` | không (mặc định 30) | Sau bao nhiêu giây kể từ lúc khởi động mà engine chưa báo sẵn sàng thì Core coi là lỗi. |
| `bi_mat` | không | **Chỉ tên** bí mật engine cần (ví dụ `khoa_dich_vu`). Giá trị do Admin nhập ở Core, không bao giờ ghi vào phiếu. Đợt 1 chưa dùng. |
| `webhook` | không | Chỉ cho `tu_xa`: `{"url": "...", "su_kien": ["viec.co_moi", "viec.huy", "engine.dung"]}`. Để `null` thì engine tự hỏi Core định kỳ, việc vẫn không mất. |

**Engine nhận địa chỉ Core và khóa lúc khởi động như thế nào** (cả `cuc_bo` lẫn `tu_xa` đều gọi API HTTP của Core; `cuc_bo` gọi qua `127.0.0.1`):

1. Core chạy lệnh `diem_vao.lenh` trong thư mục gói, rồi ghi **một dòng JSON** (UTF-8, kết thúc bằng xuống dòng) vào stdin của engine:
   `{"core_url": "http://127.0.0.1:<cổng>", "khoa": "<khóa engine>", "instance": "<mã phiên chạy>"}`
   Core giữ stdin mở hoặc đóng sau dòng đó, tùy Core. SDK chỉ đọc đúng một dòng, rồi báo sẵn sàng và bắt đầu nhận việc. Người viết engine không phải làm gì: `app.chay()` tự đọc.
2. **Chạy tay** (thử, hoặc engine `tu_xa` ở máy khác): đặt biến môi trường `KTT_CORE_URL`, `KTT_ENGINE_KHOA`, và `KTT_ENGINE_INSTANCE` (không bắt buộc, thiếu thì SDK tự đặt).
3. Ràng buộc: `core_url` dùng `http://` chỉ khi là máy cục bộ (`127.0.0.1`, `localhost`, `::1`), máy khác phải `https://`. `khoa` là 16–512 ký tự ASCII, không có khoảng trắng. `instance` là 1–100 ký tự chữ, số, `_ . : -`. Khóa không bao giờ ghi vào phiếu, mã hay nhật ký.

### 3.3 Năng lực (`nang_luc`) — engine làm được việc gì

Một engine có thể có nhiều năng lực. Mỗi năng lực là **một bước** Admin chọn được khi tạo quy trình.

| Trường | Bắt buộc | Ý nghĩa |
|---|---|---|
| `ma` | có | Dạng `<nhóm>.<việc>@<số>`, ví dụ `van_ban.dem_tu@1`. Đổi cách nhận/trả thì tăng số (`@2`), giữ bản cũ cho quy trình đang dùng. |
| `ten` | có | Tên bước hiện trên màn tạo quy trình và trong Việc của tôi. |
| `nhan` | có | Danh sách loại dữ liệu bước này nhận được (mục 4). Ví dụ `["van_ban"]`. |
| `tra` | có | **Một** loại dữ liệu bước này trả ra. |
| `truong_ra` | khi `tra` là `truong` | Danh sách trường trả ra: `ma`, `ten`, `kieu`. `kieu` dùng chung danh mục kiểu cột của ngăn: `van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`. Admin ghép các trường này vào cột ngăn của module. |
| `gioi_han` | có | Giới hạn **đầu vào**: `thoi_han_giay` (bắt buộc: quá thời gian thì Core coi là lỗi), `tep_toi_da_mib`, `mime` (loại tệp nhận, để trống = không giới hạn), `ky_tu_toi_da`. Vượt giới hạn thì từ chối, không cắt bớt ngầm. |
| `huy_duoc` | không (mặc định `false`) | `true` nếu người dùng hủy được việc đang chạy. |
| `tham_so` | không | Các ô **Cài đặt bước** (mục 3.4). |

### 3.4 Cài đặt bước (`tham_so`)

Core **tự vẽ ô** trên màn tạo quy trình từ khai báo này; không ai phải viết màn riêng cho engine.

| Khóa | Ý nghĩa |
|---|---|
| `ma`, `ten` | Mã (chữ thường không dấu) và nhãn hiện trên màn. |
| `kieu` | `van_ban` (ô chữ), `so` (ô số), `co_khong` (công tắc), `chon` (danh sách, kèm `lua_chon: [{"ma": "...", "ten": "..."}]`). |
| `mac_dinh` | Giá trị khi Admin không đổi; phải đúng kiểu (`co_khong` là `true`/`false`, `so` là số, `chon` là một `ma` trong `lua_chon`). |
| `bat_buoc`, `mo_ta` | Bắt buộc nhập hay không; dòng giải thích nhỏ dưới ô. |
| `toi_thieu`, `toi_da` | Với `so`: giá trị nhỏ/lớn nhất. Với `van_ban`: số ký tự ít/nhiều nhất. |

Ràng buộc riêng của engine (ví dụ "chỉ chạy sau bước X") **không** khai ở đây; engine tự từ chối bằng một câu lỗi tiếng Việt.

## 4. Loại dữ liệu và phong bì

Core chỉ có **3 loại gốc**. Dữ liệu đi giữa các bước luôn nằm trong một "phong bì" có khóa `loai`:

| Loại | Là gì | Phong bì |
|---|---|---|
| `tep` | Một tệp trong kho tệp của Core (bước 1 luôn nhận tệp người dùng tải lên ở nút) | `{"loai": "tep", "tep": {"tep_id": "…", "ten": "a.txt", "mime": "text/plain", "kich_thuoc": 1234}}` |
| `van_ban` | Một chuỗi văn bản | `{"loai": "van_ban", "van_ban": "…"}` |
| `truong` | Một bộ trường có kiểu, đúng như khai ở `truong_ra` | `{"loai": "truong", "truong": {"so_tu": 120, "so_dong": 9}}` |

Giá trị trường theo `kieu`: `van_ban` là chuỗi; `so` là số; `co_khong` là `true`/`false`; `ngay` là chuỗi `"2026-11-08"`; `so_tien` là `{"so": 1500000, "tien_te": "VND"}`; `tep` là đối tượng tệp như trên; `null` nghĩa là không có giá trị.

**Loại riêng:** engine cần loại khác thì khai `"loai_du_lieu_rieng": [{"ma": "bang_tinh", "ten": "Bảng tính"}]`. Core chỉ so khớp mã, không hiểu nghĩa. Phong bì loại riêng: `{"loai": "bang_tinh", "bang_tinh": …}`.

## 5. Quy tắc khớp chỗ nối

Khi Admin xếp các bước thành quy trình, Core kiểm từng chỗ nối:

1. Bước 1 nhận `tep` (tệp người dùng tải ở nút) → `nhan` của bước 1 phải có `tep`.
2. Bước *k* hợp lệ khi `tra` của bước *k−1* nằm trong `nhan` của bước *k*.
3. Quy trình chỉ ghép được vào cột ngăn khi bước cuối trả `truong`, hoặc `van_ban` (thành một trường văn bản), hoặc `tep` (thành một trường tệp).

Ví dụ với 3 engine DEMO:

```
tệp ở nút ─tep→ [Đọc tệp văn bản] ─van_ban→ [Đổi thành chữ hoa] ─van_ban→ [Đếm từ] ─truong→ cột ngăn
                 nhan: tep          nhan: van_ban                  nhan: van_ban
                 tra: van_ban       tra: van_ban                   tra: truong (so_tu, so_dong)
```

Đặt "Đếm từ" trước "Đổi thành chữ hoa" thì **không khớp**: "Đếm từ" trả `truong`, mà "Đổi thành chữ hoa" chỉ nhận `van_ban`. Màn tạo quy trình báo đỏ đúng chỗ nối đó.

## 6. Chạy thử DEMO (`chay_thu_demo`)

Danh sách ví dụ để Admin bấm **Chạy thử DEMO** trong Quản lý engine (Core dựng màn chung từ đây). Mỗi mục: `nang_luc` (mã năng lực đã khai), `ten`, `dau_vao` (phong bì như mục 4), `tham_so` (giá trị cài đặt bước, có thể `{}`).

Với loại `tep`, không ghi `tep_id` mà ghi **đường dẫn trong gói**: `{"loai": "tep", "tep_demo": "demo/mau.txt"}`. Chỉ dùng dữ liệu DEMO.

## 7. Mã Python tối thiểu

```python
# e_demo_dem_tu\e_demo_dem_tu\chay.py
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu

app = Engine.tu_khai_bao("engine.json")      # đọc và kiểm phiếu; phiếu sai thì dừng, báo câu tiếng Việt


@app.nang_luc("van_ban.dem_tu@1")
def dem_tu(viec):
    van_ban = viec.dau_vao["van_ban"]          # phong bì đã kiểm đúng loại khai trong "nhan"
    dong = van_ban.splitlines()
    if viec.tham_so["bo_dong_trong"]:          # Cài đặt bước, đã điền giá trị mặc định
        dong = [d for d in dong if d.strip()]
    viec.tien_do(50, "Đang đếm từ")
    return {"loai": "truong",
            "truong": {"so_tu": sum(len(d.split()) for d in dong), "so_dong": len(dong)}}


if __name__ == "__main__":
    app.chay()                                 # Core khởi động engine bằng lệnh ở "diem_vao"
```

Trong mã nguồn Core (chưa cài gói SDK), dòng import là `from kho_tri_thuc.sdk_core.engine import …`; 3 engine DEMO viết sẵn cả hai cách.

**Đối tượng `viec` mà hàm nhận:**

| Thuộc tính / lệnh | Dùng để |
|---|---|
| `viec.dau_vao` | Phong bì đầu vào (mục 4). |
| `viec.tham_so` | Giá trị Cài đặt bước Admin đã lưu (thiếu thì lấy `mac_dinh`). |
| `viec.ngu_canh` | `viec_id`, `buoc`, `phap_nhan_id`. Không có thông tin đăng nhập. |
| `viec.tien_do(phan_tram, cau)` | Báo tiến độ cho người dùng. Nếu việc đã bị hủy, lệnh này tự dừng hàm. |
| `viec.da_huy`, `viec.kiem_huy()` | `True` khi người dùng đã hủy; `kiem_huy()` tự dừng hàm nếu đã hủy (engine chạy lâu nên gọi thường xuyên). |
| `viec.mo_tep(tep_id)` | Mở tệp đầu vào để đọc byte: `with viec.mo_tep(tep["tep_id"]) as f: du_lieu = f.read()`. |
| `viec.tai_tep_ra(ten, du_lieu, mime)` | Gửi tệp kết quả lên Core, trả đối tượng tệp để đặt vào phong bì `{"loai": "tep", "tep": …}`. |

**Báo lỗi:**
- `raise LoiNghiepVu("TEP_KHONG_DOC_DUOC", "Tệp không phải văn bản UTF-8. Hãy lưu lại dưới dạng .txt UTF-8.")` — câu thứ hai hiện cho người dùng, mã thứ nhất nằm trong "Chi tiết hỗ trợ". Thêm `thu_lai_duoc=True` nếu thử lại có thể được.
- `raise ChuaRo("<mã tương quan>")` — nguồn bên ngoài đã nhận việc nhưng chưa trả lời. Core giữ lượt, không báo thành công giả.
- Lỗi khác (lỗi lập trình) SDK tự đổi thành câu chung "Engine gặp lỗi khi xử lý", không lộ chi tiết kỹ thuật.

**SDK tự lo** (người viết engine không phải viết): nhận việc, gia hạn giữ việc, dừng khi bị hủy, gửi lại khi mất mạng với cùng khóa chống trùng (tối đa 3 lượt), đổi ngoại lệ thành lỗi chuẩn, từ chối đầu vào sai `nhan`/`gioi_han`/`tham_so` trước khi gọi hàm, kiểm kết quả đúng `tra` và `truong_ra`.

## 8. Tự kiểm trước khi gửi

Không cần Core thật — SDK có **Core giả trong bộ nhớ**:

```python
from kho_tri_thuc_sdk.thu import CoreGia
from e_demo_dem_tu.chay import app

kq = CoreGia().chay_thu(app, "van_ban.dem_tu@1", {"loai": "van_ban", "van_ban": "Một hai\n\nBa"})
print(kq["trang_thai"], kq["ket_qua"])   # XONG {'loai': 'truong', 'truong': {'so_tu': 3, 'so_dong': 2}}
```

(Thư mục gói phải nằm trong `sys.path` để import được `e_demo_dem_tu.chay`.)

Hoặc chạy mọi ví dụ `chay_thu_demo` của một gói: `python -m kho_tri_thuc_sdk.thu <thư mục gói>` (trong mã nguồn Core: `python -m kho_tri_thuc.sdk_core.thu <thư mục gói>`). Lệnh in `[ĐẠT]`/`[LỖI]` cho từng ví dụ. Phiếu sai thì in từng câu lỗi tiếng Việt.

## 9. Engine không được làm

1. Gọi engine khác (mọi trung chuyển đi qua Core).
2. Kết nối CSDL hay chạy SQL; engine không nhận mật khẩu CSDL.
3. Import `kho_tri_thuc.*` ngoài SDK.
4. Ghi bí mật vào phiếu, mã hay nhật ký.
5. Dùng dữ liệu thật để chạy thử.
6. Báo lỗi bằng câu kỹ thuật, lộ đường dẫn, khóa hay dữ liệu nghiệp vụ.

## 10. Các điểm đã chốt (hợp đồng bản 1.2, 08/11/2026)

Các điểm mẫu phiếu bản 1 tạm chọn, nay lead đã chốt thành hợp đồng (`docs\HOP-DONG-CONG.md` b.5, c.2):

1. Trường bắt buộc: `phien_ban_manifest`, `loai`, `ma`, `ten`, `phien_ban`, `tuong_thich` (`core`, `api`), `che_do_chay`, `nang_luc`, và `diem_vao` khi `cuc_bo`. Mỗi năng lực bắt buộc `ma`, `ten`, `nhan`, `tra`, `gioi_han.thoi_han_giay`; `truong_ra` chỉ có khi `tra` là `truong`.
2. `gioi_han` áp cho **đầu vào** của bước.
3. Giá trị trong phong bì `truong`: `so_tien` = `{"so": …, "tien_te": "VND"}`, `ngay` = `"YYYY-MM-DD"`, không có giá trị = `null`. Phong bì loại riêng = `{"loai": "<ma>", "<ma>": …}` (mục 4).
4. Dạng `webhook` = `{"url", "su_kien": []}` (mục 3.2).
5. Tên gói SDK khi cài là `kho_tri_thuc_sdk`; trong mã nguồn Core là `kho_tri_thuc.sdk_core`.
6. Engine `cuc_bo` cũng dùng API HTTP qua loopback; địa chỉ Core và khóa nhận như mục 3.2. SDK 2.0 không có đường socket.
