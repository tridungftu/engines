# API Core v1 cho engine — kèm SDK 2.0.0

*Bản gửi người viết engine, tách từ hợp đồng cổng của Core ngày 09/11/2026. Phía engine **đã khóa ở SDK 2.0.0**: các bản SDK sau chỉ thêm phần dành cho module, không đổi phần engine; đổi gì phía engine sẽ tăng phiên bản và báo trước.*

**Bộ gửi kèm (thư mục `sdk-2.0.0`):** gói cài `kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` (kiểm bằng `SHA256SUMS.txt`), `HUONG-DAN-VIET-ENGINE.md` (bắt đầu từ đây), `MAU-PHIEU-ENGINE.md`, thư mục `engine-demo` (3 engine mẫu).

**Kiểu dữ liệu dùng trong phiếu:** `van_ban`, `so`, `so_tien` (luôn kèm mã tiền tệ), `ngay`, `co_khong`, `tep`. Mã engine dạng `e_` + chữ thường/số/gạch dưới, tối đa 31 ký tự.

**Quy tắc chung:** engine không gọi engine khác; mọi trung chuyển qua Core. Engine không nhận thông tin đăng nhập CSDL. Một engine = một thư mục gói đặt ngoài Core.

---

## (b) `engine.json` 2.0 — phiếu đăng ký engine

### b.1 Khung
```json
{
  "phien_ban_manifest": 2,
  "loai": "engine",
  "ma": "e_demo_doc_tep",
  "ten": "Đọc tệp thành văn bản (DEMO)",
  "phien_ban": "1.0.0",
  "tuong_thich": {"core": ">=2.0.0 <3.0.0", "api": "v1", "sdk": ">=2.0.0 <3.0.0"},
  "che_do_chay": "cuc_bo",
  "diem_vao": {"lenh": ["{python}", "-m", "e_demo_doc_tep.chay"], "thu_muc": "."},
  "nang_luc": [ … mục b.2 … ],
  "loai_du_lieu_rieng": [],
  "tai_nguyen": {"so_viec_dong_thoi": 1},
  "readiness": {"thoi_han_giay": 30},
  "chay_thu_demo": [ … mục b.4 … ],
  "bi_mat": [],
  "webhook": null
}
```
- `ma`: `^e_[a-z0-9_]{2,29}$` (tối đa 31 ký tự, khớp sổ engine hiện có `loi.engine_dinh_nghia`; chốt trước khi phát hành SDK).
- `che_do_chay`: `cuc_bo` (Core khởi động tiến trình con, cấp cổng, E3) hoặc `tu_xa` (engine máy khác gọi Core qua HTTP có xác thực).
- `diem_vao.lenh`: lệnh chạy **trong thư mục gói**; `{python}` là Python Core chọn. **Không** còn giả định engine nằm trong `kho_tri_thuc.engines.*` (bỏ tiền tố ở `nap_engine.py`, `khoi_chay_engine.py`).
- Engine **không** nhận thông tin đăng nhập CSDL (E5). Engine không import `kho_tri_thuc.*` ngoài SDK.

### b.2 `nang_luc` — nhận gì, trả gì, giới hạn, tham số bước
```json
[{"ma": "van_ban.dem_tu@1",
  "ten": "Đếm từ",
  "nhan": ["van_ban"],
  "tra": "truong",
  "truong_ra": [{"ma": "so_tu", "ten": "Số từ", "kieu": "so"},
                {"ma": "so_dong", "ten": "Số dòng", "kieu": "so"}],
  "gioi_han": {"tep_toi_da_mib": 20, "mime": [], "ky_tu_toi_da": 1000000, "thoi_han_giay": 60},
  "huy_duoc": true,
  "tham_so": [{"ma": "bo_dong_trong", "ten": "Bỏ dòng trống khi đếm", "kieu": "co_khong", "mac_dinh": true}]}]
```
- **Loại dữ liệu** (dùng để Core kiểm khớp chỗ nối): Core có 3 loại gốc: `tep` (tham chiếu tệp trong kho tệp Core), `van_ban` (chuỗi), `truong` (bộ trường có kiểu, khai ở `truong_ra`). Engine có thể khai thêm loại riêng ở `loai_du_lieu_rieng: [{"ma": "...", "ten": "..."}]`; Core chỉ so khớp chuỗi `ma`, không hiểu nghĩa.
- **Quy tắc khớp:** bước 1 nhận `tep` (tệp người dùng tải ở nút). Bước *k* hợp lệ khi `tra` của bước *k−1* nằm trong `nhan` của bước *k*. Quy trình chỉ ghép được vào cột ngăn khi bước cuối `tra: "truong"` hoặc `"van_ban"` (một trường `van_ban`) hoặc `"tep"` (một trường `tep`).
- `truong_ra[].kieu` dùng danh mục kiểu cột chung (`van_ban`, `so`, `so_tien`, `ngay`, `co_khong`, `tep`).
- `tham_so` = ô **Cài đặt bước** trên màn tạo quy trình. Core **vẽ ô từ khai báo** này (YEU-CAU  điểm 2). `kieu`: `van_ban`, `so`, `co_khong`, `chon` (kèm `lua_chon: [{"ma","ten"}]`). Khóa phụ: `mac_dinh`, `bat_buoc`, `mo_ta`, `toi_thieu`, `toi_da`.
- Ràng buộc riêng của engine (ví dụ "chỉ chạy sau bước X") **không** khai cho Core kiểm; engine tự từ chối bằng lỗi có `thong_diep` (YEU-CAU  điểm 3).

### b.3 Phong bì dữ liệu giữa các bước
Đầu vào một bước = đầu ra bước trước (bước 1: tệp ở nút):
```json
{"loai": "van_ban", "van_ban": "…"}                                   
{"loai": "tep", "tep": {"tep_id": "…", "ten": "a.txt", "mime": "text/plain", "kich_thuoc": 1234}}
{"loai": "truong", "truong": {"so_tu": 120, "so_dong": 9}}
```
Kèm theo mọi lượt: `tham_so` (giá trị Cài đặt bước đã lưu), `ngu_canh` (`viec_id`, `buoc`, `phap_nhan_id`, không có thông tin đăng nhập).

### b.4 `chay_thu_demo` — Chạy thử DEMO chung (E6)
```json
[{"nang_luc": "van_ban.dem_tu@1", "ten": "Đếm từ đoạn văn DEMO",
  "dau_vao": {"loai": "van_ban", "van_ban": "Dòng một DEMO\nDòng hai DEMO"}, "tham_so": {}},
 {"nang_luc": "tep.doc_van_ban@1", "ten": "Đọc tệp DEMO", "dau_vao": {"loai": "tep", "tep_demo": "demo/mau.txt"}}]
```
Core dựng màn Chạy thử chung từ khai báo này (chỉ Admin). `tep_demo` là đường dẫn **trong gói**. Chỉ dữ liệu DEMO.

### b.5 SDK engine 2.0 (L2.1)
```python
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, ChuaRo
app = Engine.tu_khai_bao("engine.json")

@app.nang_luc("van_ban.dem_tu@1")
def xu_ly(viec):                      # viec.dau_vao, viec.tham_so, viec.tien_do(%, câu), viec.mo_tep(tep_id)
    return {"loai": "truong", "truong": {"so_tu": 3, "so_dong": 2}}

app.chay()                            # tự chọn kênh cục bộ hoặc HTTP theo che_do_chay / biến Core cấp
```
Tên gói khi cài là `kho_tri_thuc_sdk`; trong mã nguồn Core là `kho_tri_thuc.sdk_core`. Engine ngoài Core import `kho_tri_thuc_sdk`. **Các điểm đã chốt:** trường bắt buộc như `MAU-PHIEU-ENGINE.md` mục 10.1; `gioi_han` áp cho đầu vào của bước; giá trị trong phong bì `truong`: `so_tien` = `{"so": …, "tien_te": "VND"}`, `ngay` = `"YYYY-MM-DD"`, không có giá trị = `null`; phong bì loại riêng = `{"loai": "<ma>", "<ma>": …}`; `webhook` = `{"url", "su_kien": []}`. Schema máy kiểm: `core\contract\manifest_engine_v2.json`. SDK tự lo: vòng nhận việc, gia hạn, kiểm `huy` để dừng, gửi lại với cùng `Idempotency-Key`, đổi ngoại lệ thành phong bì lỗi, kiểm `tra`/`truong_ra`. Có **Core giả trong bộ nhớ** (`kho_tri_thuc_sdk.thu`) để engine test không cần Core. Bỏ hàm riêng của một engine trong `sdk_core\engine.py` (lượt "chưa rõ" thành chung, c.2 thao tác 9).

---

## (c) API engine `/api/v1/engine/…` và thông báo

### c.1 Xác thực
- Khi cài, Core cấp cho mỗi engine một **khóa engine** (ngẫu nhiên 32 byte), lưu trong **két bí mật** của Core (không vào CSDL dạng rõ, không vào nhật ký). Engine `cuc_bo` nhận khóa qua stdin/handle lúc Core khởi động (cơ chế bí mật hiện có). Engine `tu_xa`: Admin chép khóa một lần từ màn Quản lý engine.
- Mọi lời gọi: `Authorization: Bearer <khóa engine>`, `X-KTT-Engine: <ma>`, `X-KTT-Instance: <mã phiên chạy>`. Lệnh ghi thêm `Idempotency-Key`.
- Engine chỉ thấy việc của chính mình; gọi `viec/{id}` của engine khác → 404.
- Engine ở máy khác: bắt buộc HTTPS khi lên máy chủ (đợt 1 chạy cùng máy, loopback).

### c.2 Thao tác (engine gọi Core)

| # | Thao tác | HTTP | Thân gửi → trả về |
|---:|---|---|---|
| 1 | Báo sẵn sàng | `POST /api/v1/engine/{ma}/san-sang` | `{instance, phien_ban, nang_luc[]}` → `{cau_hinh}` |
| 2 | Nhận việc (kéo, có hạn giữ, chờ ≤ 30 giây) | `POST /api/v1/engine/{ma}/viec/nhan` | `{cho_toi_da_giay}` → `200 {viec:{id, nang_luc, dau_vao, tham_so, ngu_canh, han_giu, lan_thu}}` hoặc `204` |
| 3 | Đọc đầu vào (khi lớn, không gửi kèm ở #2) | `GET /api/v1/engine/viec/{id}/dau-vao` | → phong bì b.3 |
| 4 | Tải tệp vào | `GET /api/v1/engine/viec/{id}/tep/{tep_id}` | → luồng byte |
| 5 | Tải tệp ra | `POST /api/v1/engine/viec/{id}/tep` | byte + `X-KTT-Ten-Tep`, `Content-Type` → `{tep_id}` |
| 6 | Gia hạn | `POST /api/v1/engine/viec/{id}/gia-han` | `{han_giu_giay}` → `{han_giu, huy: true/false}` (tín hiệu hủy đi kèm, không phụ thuộc webhook) |
| 7 | Báo tiến độ | `POST /api/v1/engine/viec/{id}/tien-do` | `{phan_tram, cau}` |
| 8 | Nộp kết quả | `PUT /api/v1/engine/viec/{id}/ket-qua` | phong bì b.3 → `{da_luu: true}` (ghi bền trước) |
| 9 | Kết thúc | `POST /api/v1/engine/viec/{id}/ket-thuc` | `{trang_thai: "XONG"\|"LOI"\|"CHUA_RO"\|"HUY", loi?:{ma, thong_diep, thu_lai_duoc}, ma_tuong_quan?}` |
| 10 | Lượt bền "chưa rõ" (chung mọi engine) | `POST /api/v1/engine/{ma}/luot-ben` | `{thao_tac: "giu"\|"chot"\|"doc", ma_tuong_quan, …}` |

- **Không mất, không trùng (E4):** việc chỉ chuyển "xong" khi #8 đã ghi bền rồi #9 mới xác nhận. Hết hạn giữ mà không gia hạn → Core trả việc về hàng chờ (tăng `lan_thu`). `Idempotency-Key` lặp → Core trả kết quả lần đầu.
- **Đường cục bộ:** engine `cuc_bo` **cũng dùng API HTTP này qua loopback** (`127.0.0.1`, cổng Core); Core khởi động tiến trình engine và chuyển địa chỉ Core + khóa engine qua stdin/handle. Như vậy mọi engine dùng **một đường truyền, một bộ thao tác, một cách xác thực**. Kênh socket cũ (`kenh_engine.py`) giữ nguyên cho mã đang dùng, **không mở rộng**, SDK 2.0 không cần đường socket. Ngăn dữ liệu engine, bí mật theo tham chiếu, nhật ký kỹ thuật: để sau đợt 1.

**Chốt bổ sung c.2 (theo SDK  đã gộp):**
1. **Khởi động engine `cuc_bo`:** Core chạy `diem_vao.lenh` trong thư mục gói (`{python}` = Python Core chọn) rồi **ngay lập tức** ghi một dòng JSON UTF-8 kết thúc bằng xuống dòng vào stdin: `{"core_url": "http://127.0.0.1:<cổng>", "khoa": "<khóa engine>", "instance": "<mã phiên chạy>"}`. Chạy tay: biến môi trường `KTT_CORE_URL`, `KTT_ENGINE_KHOA`, `KTT_ENGINE_INSTANCE`. `http://` chỉ cho `127.0.0.1`/`localhost`/`::1`; máy khác bắt buộc `https://`. Khóa 16–512 ký tự ASCII; `instance` khớp `[A-Za-z0-9_.:-]{1,100}`.
2. **Tên tệp ra:** header `X-KTT-Ten-Tep` mã hóa **percent-encoding UTF-8**.
3. **Mất quyền giữ việc:** Core trả **409 `MAT_LEASE`** ở `gia-han`/`tien-do`/`ket-qua`/`ket-thuc`; engine dừng việc, không nộp, không báo kết thúc. (SDK cũng coi 404/410 như vậy.)
4. **Gửi lại:** khi lỗi mạng, 429, 5xx, hoặc thân lỗi có `thu_lai_duoc: true`; tối đa **3 lượt gửi lại** (4 lần gửi) cùng `Idempotency-Key`.
5. **Hạn giữ:** engine xin 60 giây, gia hạn mỗi 20 giây. Core có thể trả `han_giu` ngắn hơn; SDK đợt 1 chưa đọc (ghi nợ).
6. **Trả lời:** `tien-do` → `{huy: true|false}` (như `gia-han`); `san-sang` → `{cau_hinh: {}}` (đợt 1 rỗng).
7. **Quá thời hạn bước** (`gioi_han.thoi_han_giay`): **Core** cắt (đánh dấu việc lỗi `QUA_THOI_HAN`, thu lease), SDK không tự cắt được.
8. **Lượt bền "chưa rõ"** (#10): đợt 1 engine chỉ báo `CHUA_RO` + `ma_tuong_quan` ở `ket-thuc`; giữ/chốt/đọc làm ở đợt 2 cùng migration 135.
9. **Phiên bản SDK:** một số chung `2.0.0` ở `sdk_core\__init__.py` ( nâng); hằng `PHIEN_BAN_SDK_ENGINE` trong `engine.py` sẽ đọc từ đó.
10. **`mo_tep`:** đợt 1 đọc cả tệp vào bộ nhớ, trần `tep_toi_da_mib`; đọc theo luồng để sau.
- Bản Core giả có máy chủ HTTP loopback cùng đường dẫn: `sdk_core\thu.py` `MayChuGia` — ** dùng làm bản đối chiếu** khi viết API thật.

### c.3 Core gọi engine
| Việc | Cục bộ | Từ xa |
|---|---|---|
| Khởi động / dừng có drain | Core chạy/dừng tiến trình con do chính Core quản lý | thông báo `engine.dung` |
| Kiểm sẵn sàng | readiness qua kênh | `GET <webhook>/suc-khoe` |
| Hủy việc | cờ `huy` ở #6 + thông báo `viec.huy` | như cục bộ |
| Đánh thức | thông báo `viec.co_moi` | như cục bộ |

### c.4 Thông báo (sự kiện) — một chuẩn cho engine và module
**Phong bì:**
```json
{"su_kien": "viec.co_moi", "phien_ban": 1, "id": "uuid", "luc": "2026-11-08T16:00:00+07:00", "nguon": "core",
 "ma_engine": "…?", "ma_module": "…?", "viec_id": "…?", "buoc": 2, "tham_chieu": {"ket_qua_id": "…"}}
```
- Chỉ mang **tham chiếu** (mã việc, mã kết quả, mã tệp). Không mang nội dung tài liệu, bí mật.
- **Danh mục:**
  - Core → engine: `viec.co_moi` (có việc), `viec.huy` (hủy), `engine.dung`.
  - Engine → Core: hoàn tất / lỗi = thao tác #8 + #9 (không cần webhook ngược).
  - Core → module / người theo dõi: `viec.da_nhan`, `viec.tien_do`, `viec.buoc_xong`, `quy_trinh.xong` (kèm `tham_chieu.ket_qua_id` và bảng ghép), `quy_trinh.loi`, `viec.huy`.
- **Đường đi:** module trong cùng Core nhận qua bus `su_kien` hiện có. Đích HTTP (engine `tu_xa`, hệ thống nội bộ đã đăng ký): `POST` JSON, ký **HMAC-SHA256** trên `luc + "." + body` ở header `X-KTT-Chu-Ky`; lệch giờ quá 5 phút thì bên nhận từ chối.
- **Gửi lại:** không nhận 2xx thì gửi lại sau 1 phút, 5 phút, 30 phút, 2 giờ; tối đa 24 giờ; quá hạn vào hàng "gửi hỏng" (Admin bấm gửi lại). **Bên nhận bỏ qua `id` đã xử lý** (không xử lý trùng). Webhook mất thì việc không mất: engine vẫn kéo theo chu kỳ (c.2 #2).

---

