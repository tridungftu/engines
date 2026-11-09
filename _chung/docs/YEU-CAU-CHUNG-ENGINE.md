# YÊU CẦU CHUNG CHO MỌI ENGINE — Cổng gắn engine vào Core (API · SDK · webhook thống nhất)

*Lập ngày 08/11/2026 theo yêu cầu của Anh Dũng.* Mọi project engine trong `D:\Claude\Engines\<engine>` **phải đọc tài liệu này trước** tài liệu riêng của engine.

**Căn cứ:**
- Anh chốt 08/11: "Có cổng gắn engine vào CORE với API, SDK, webhook thống nhất". Core khoảng 100 cửa chung, engine gắn vào bằng khai báo (G14, `D:\Claude\Core\docs\YEU-CAU-CORE.md`, Phụ lục A).
- Chỉ đạo chuỗi engine 07/11 (`PHIEU-ENGINE-chuoi`, mục A).
- TL 55 §10–12 (chuẩn engine), TL 54 §2 (engine không giữ dữ liệu).
- Tài liệu tham chiếu trong `_chung\docs\`: `PHIEU-NOI-ENGINE-THAT.md`, `KS-KENH-ENGINE-THAT.md`.

**Quy ước:** tên route, thao tác và sự kiện ở đây là **đề xuất**. Lead Core chốt tên cuối, nhưng **không được đổi nguyên tắc**.

**Ký hiệu hiện trạng** (đối chiếu mã Core commit `755edd10`, ngày 08/11):
- ✅ có và đã dùng
- 🟡 có một phần hoặc còn riêng cho từng engine
- ❌ chưa có

---

## 0. Kết luận

1. **Một cổng, một bộ thao tác, ba cách dùng:**
   - **API**: bộ thao tác engine ↔ Core. Chạy được trên hai đường truyền:
     - đường **cục bộ**: kênh socket hiện có, dùng khi engine chạy cùng máy, do Core khởi động;
     - đường **HTTP(S)**: dùng khi engine ở máy khác, như máy Local AI hay máy ABBYY.
   - **SDK Python**: bọc API. Người viết engine chỉ viết hàm `xu_ly(viec)`, không cần biết đường truyền.
   - **Webhook / sự kiện**: Core báo cho engine (có việc mới, hủy, dừng, đổi cấu hình) và cho module (việc đã nhận, tiến độ, xong, lỗi, chưa rõ).
   - Cả ba dùng **cùng phong bì, cùng mã lỗi, cùng cách xác thực**.
2. **Engine gắn vào Core chỉ bằng khai báo `engine.json`.** Core không có dòng mã nào mang tên engine:
   - không `if ma_engine == 'e_...'`;
   - không route, màn, bảng SQL hay hàm SDK riêng cho một engine.
3. **Engine không gọi engine.** Core điều phối theo chuỗi do Anh khai: engine báo xong thì Core đẩy kết quả sang bước kế.
4. **Engine không có mật khẩu CSDL.** Mọi dữ liệu đi qua thao tác của cổng. Dữ liệu engine cần giữ lâu dài (ví dụ bảng bí danh của Mask) nằm trong **ngăn của engine** do Core tạo và quản.
5. **Hiện trạng:**
   - Đã có: kênh cục bộ (nhận việc, đọc đầu vào, đọc tệp, gia hạn, ghi kết quả, kết thúc), SDK cơ bản, bộ khởi động engine con (K2).
   - Chưa có: API HTTP, webhook, bộ cài engine từ thư mục/gói riêng (K1), cấu hình/nhật ký/tiêu thụ việc thống nhất (K3–K5).
   - **Core vẫn chứa mã riêng cho Hỏi AI, OCR, Mask** (mục 9). Đây là lý do engine từng nằm trong Core và là việc phải làm đầu tiên của lead Core.

## 1. Sơ đồ

```
 Module ──(gửi việc: tệp + loại + tham số)──► CORE ──────────────────────────────┐
   ▲                                            │ Bộ điều phối chuỗi (dịch vụ lõi) │
   │ sự kiện viec.* / kết quả vào ngăn module   │ Hàng việc · Lease · Kết quả tạm  │
   └────────────────────────────────────────────┤ Kho tệp · Bí mật · Nhật ký       │
                                                └──────┬───────────────▲───────────┘
                                webhook (đánh thức,    │               │ API v1 (cục bộ / HTTP)
                                hủy, dừng, cấu hình)   ▼               │ nhận việc · đọc · tiến độ ·
                                                ┌──────────────────────┴──┐ gia hạn · nộp kết quả · lỗi
                                                │ ENGINE (gói riêng)      │
                                                │ SDK: chỉ viết xu_ly()   │
                                                └─────────────────────────┘
```

**Nguyên tắc kéo trước, đẩy sau:**
- Việc luôn được engine **kéo** qua API (`nhan_viec`, có lease).
- Webhook chỉ để **đánh thức** và báo hủy/dừng. Webhook mất thì việc không mất: engine vẫn kéo được theo chu kỳ.

## 2. Khai báo engine — `engine.json` (phiên bản manifest 2, đề xuất)

| Trường | Bắt buộc | Nội dung | Hiện trạng |
|---|---|---|---|
| `ma`, `ten`, `phien_ban` (SemVer), `tuong_thich_core` | ✔ | Mã `e_<ten>`; tên hiển thị tiếng Việt; khoảng Core tương thích | ✅ có ở manifest 1 |
| `capability[]` | ✔ | Mỗi năng lực có: `ma` (`<nhom>.<viec>@<so>`), `dau_vao` và `dau_ra` (tham chiếu contract JSON Schema), `loai_du_lieu_vao`/`loai_du_lieu_ra` (để Core kiểm khớp bước khi khai chuỗi), `thoi_han_giay`, `huy_duoc` | 🟡 mới có tên capability, chưa khai kiểu vào/ra để kiểm chuỗi |
| `che_do_chay` | ✔ | `cuc_bo` (Core khởi động tiến trình con) hoặc `tu_xa` (engine ở máy khác, gọi Core qua HTTP) | ❌ chỉ có cục bộ |
| `diem_vao` | cục bộ | Lệnh chạy trong gói, ví dụ `python -m <goi>.chay` | 🟡 đang giả định nằm trong `kho_tri_thuc.engines.*` |
| `webhook` | từ xa | URL nhận sự kiện từ Core; danh sách sự kiện muốn nhận | ❌ |
| `cau_hinh_schema` | | JSON Schema cấu hình. Core tự dựng màn cấu hình trong **Quản lý engine**, không viết màn riêng | 🟡 có ở `e_hoi_ai`; màn hiện là màn riêng |
| `bi_mat[]` | | **Chỉ tên** bí mật cần, ví dụ `khoa_abbyy`. Giá trị do Admin nhập ở Core; engine đọc theo tham chiếu | 🟡 `kenh_bi_mat.py` |
| `ket_noi_ngoai[]` | | Máy/địa chỉ engine được gọi ra (máy Local AI, máy ABBYY). Ngoài danh sách thì chặn. Cloud: chỉ được khai khi chuỗi có bước Mask đứng trước | 🟡 có trường, chưa ép |
| `ngan_du_lieu[]` | | Bảng engine cần giữ lâu dài: migration trong gói, bảng thường, không JSONB. Core tạo trong schema `eng_<ma>` | ❌ (Mask đang dùng bảng riêng trong `loi*`) |
| `giao_dien_quan_tri` | | Gói giao diện riêng của engine, hiện trong ô engine ở Quản lý engine, nạp giống giao diện module | ❌ (đang là JS riêng trong Core) |
| `chay_thu_demo` | | Bộ ví dụ DEMO theo contract. Core dựng **màn Chạy thử chung** từ schema (chỉ Admin) | ❌ (mỗi engine một màn riêng trong Core) |
| `tai_nguyen`, `readiness`, `thu_hoi`, `ban_giao_ket_qua` | ✔ | Số việc đồng thời, RAM/CPU đề xuất; cách báo sẵn sàng; drain; Core xác nhận trước khi giải phóng | ✅ có ở manifest 1 |

## 3. API v1 — engine gọi Core

Mỗi lệnh gửi kèm: danh tính phiên bản engine (`engine_instance`), `request_id` và khóa chống trùng (`idempotency_key`) với lệnh ghi.

**Lỗi chung:** `{ma, thong_diep, request_id, thu_lai_duoc}`. Thông điệp bằng tiếng Việt, không chứa dữ liệu nghiệp vụ.

| # | Thao tác | HTTP đề xuất | Kênh cục bộ hiện có | SDK | Hiện trạng |
|---:|---|---|---|---|---|
| 1 | Đăng ký phiên bản engine (từ xa) / báo sẵn sàng | `POST /api/v1/engine/{ma}/san-sang` | readiness lúc khởi động | `sdk.san_sang()` | 🟡 chỉ cục bộ |
| 2 | Nhận việc (lease, chờ dài ≤ 30 giây) | `POST /api/v1/engine/{ma}/viec/nhan` | `nhan_viec` | vòng lặp trong `chay()` | ✅ cục bộ |
| 3 | Đọc đầu vào theo contract | `GET /api/v1/engine/viec/{id}/dau-vao` | `doc_dau_vao` | `viec.dau_vao` | ✅ |
| 4 | Đọc tệp (luồng, theo `tep_id`) | `GET /api/v1/engine/viec/{id}/tep/{tep_id}` | `mo_doc` | `viec.mo_tep()` | ✅ |
| 5 | Báo tiến độ (%, bước, câu ngắn) | `POST …/viec/{id}/tien-do` | — | `viec.tien_do()` | ❌ |
| 6 | Gia hạn lease / nhịp sống | `POST …/viec/{id}/gia-han` | `heartbeat` | tự động trong SDK | ✅ |
| 7 | Nộp kết quả (tạm giữ ở Core tới khi module lưu hoặc đóng việc) | `PUT …/viec/{id}/ket-qua` | `ghi_ket_qua` | `return` trong `xu_ly` | ✅ |
| 8 | Kết thúc: `XONG` / `LOI` / `CHUA_RO` / `HUY` | `POST …/viec/{id}/ket-thuc` | `ket_thuc` | ngoại lệ SDK → mã lỗi | 🟡 `CHUA_RO` đang riêng OCR |
| 9 | Lượt bền "chưa rõ" (giữ / chốt / đọc lượt, dùng khi bên ngoài đã nhận việc nhưng chưa trả, như ABBYY) | `POST …/luot-ben` | `ocr_giu_luot` / `ocr_chot_luot` / `ocr_doc_luot` | `viec.giu_luot()`… | 🟡 **riêng OCR → phải thành chung** |
| 10 | Đọc cấu hình đang áp dụng | `GET /api/v1/engine/{ma}/cau-hinh` | hồ sơ chạy | `sdk.cau_hinh` | 🟡 |
| 11 | Đọc bí mật theo tham chiếu (không ghi log) | `GET /api/v1/engine/{ma}/bi-mat/{ten}` | `kenh_bi_mat` | `sdk.bi_mat(ten)` | 🟡 |
| 12 | Đọc/ghi **ngăn của engine** (theo khai báo `ngan_du_lieu`) | `POST /api/v1/engine/{ma}/ngan/{bang}/…` | đường riêng `goi_mask` | `sdk.ngan(bang)` | 🟡 **riêng Mask → phải thành chung** |
| 13 | Ghi nhật ký kỹ thuật (không nội dung nhạy cảm) | `POST /api/v1/engine/{ma}/nhat-ky` | — | `sdk.ghi_nhat_ky()` | ❌ (nhật ký bền K4 chưa có) |

## 4. Core gọi engine

| Việc | Cục bộ | Từ xa | Hiện trạng |
|---|---|---|---|
| Khởi động / dừng có drain | Core chạy và dừng tiến trình con | webhook `engine.dung` → engine nhận nốt việc đang làm rồi dừng | 🟡 K2 launcher cục bộ; chưa có từ xa |
| Kiểm sức khỏe | readiness qua kênh | `GET <webhook>/suc-khoe` | 🟡 |
| Hủy việc | `viec.huy` qua kênh | webhook `viec.huy`; engine thấy ở lần gia hạn kế tiếp, kể cả khi mất webhook | ❌ chưa xác minh |
| Đánh thức | không cần | webhook `viec.co_moi` | ❌ |

## 5. Webhook và sự kiện (một chuẩn cho engine, module và hệ thống ngoài)

**Phong bì:**
```
{su_kien, phien_ban:1, id, luc (ISO, +07:00), nguon:"core", ma_engine?, ma_module?, viec_id?, buoc?, tham_chieu{...}}
```
- **Chỉ mang tham chiếu** (mã việc, mã kết quả, mã tệp). Không mang nội dung tài liệu, cụm gốc hay bí mật.
- **Ký số:** HMAC-SHA256 trên `luc + "." + body`, đặt ở header `X-KTT-Chu-Ky`. Lệch giờ quá 5 phút thì từ chối. Khóa ký riêng cho từng đích và đổi được.
- **Chống trùng:** bên nhận bỏ qua `id` đã xử lý.
- **Gửi lại:** khi không nhận 2xx, gửi lại sau khoảng 1 phút, 5 phút, 30 phút, 2 giờ; tối đa 24 giờ. Quá hạn thì vào hàng "gửi hỏng", hiện ở Quản lý engine để Admin bấm gửi lại.
- **Danh mục sự kiện tối thiểu:**
  - Core → engine: `viec.co_moi`, `viec.huy`, `engine.dung`, `engine.cau_hinh_doi`.
  - Core → module và người theo dõi: `viec.da_nhan`, `viec.tien_do`, `viec.buoc_xong`, `viec.xong`, `viec.loi`, `viec.chua_ro`, `viec.huy`, `engine.san_sang`, `engine.ngung`.
- **Đường vào bên trong Core:** module nhận qua bus `su_kien` hiện có. Webhook là cùng sự kiện đó gửi ra HTTP cho đích đã đăng ký.
- **Hiện trạng:** ❌ chưa có webhook. Bus `su_kien` 🟡 có (`core/su_kien.py`), chưa có danh mục `viec.*` thống nhất.

## 6. SDK Python (gói `kho_tri_thuc_sdk`, hiện ở bản 1.5.1)

**Người viết engine chỉ cần viết** (giao diện SDK đề xuất, chưa có):
```python
from kho_tri_thuc_sdk.engine import Engine, LoiNghiepVu, ChuaRo

app = Engine.tu_khai_bao("engine.json")

@app.nang_luc("ocr.trich_van_ban@1")
def xu_ly(viec):            # viec.dau_vao đã kiểm theo schema
    viec.tien_do(30, "Đang đọc trang 1/3")
    ...
    return ket_qua           # SDK kiểm schema đầu ra rồi nộp

app.chay()                   # tự chọn kênh cục bộ hoặc HTTP theo che_do_chay
```

**SDK tự lo:**
- vòng nhận việc, gia hạn lease, dừng an toàn (drain);
- gửi lại khi mất xác nhận (tối đa 3 lượt, cùng `idempotency_key`);
- đổi ngoại lệ thành mã lỗi;
- kiểm schema vào/ra;
- xác thực webhook (với engine từ xa);
- lượt bền "chưa rõ" (`ChuaRo`).

**Bộ thử độc lập** `kho_tri_thuc_sdk.thu`: Core giả trong bộ nhớ, để mỗi project engine test **không cần Core thật**.

**Hiện trạng:**
- 🟡 `sdk_core/engine.py` (167 dòng) có `doc_dau_vao`, `mo_doc`, `ghi_ket_qua`, `heartbeat`.
- Nhưng cũng có `ocr_giu_luot`, `ocr_chot_luot`, `ocr_doc_luot` **riêng cho OCR** (vi phạm G14).
- ❌ chưa có `Engine.tu_khai_bao`, `nang_luc`, `tien_do`, đường HTTP, bộ Core giả.

## 7. Hợp đồng dữ liệu dùng chung (dùng lại trước, chỉ thêm khi thiếu)

- **Đã có:** `tham_chieu_tep.v1`, `van_ban_tai_lieu.v1`, `du_lieu_bang.v1`, `tham_so.v1`, `noi_dung_da_che.v1`, `tra_loi_ai.v1` và `hoi_ai.v2` / `tra_loi_ai.v2`.
- **Quy tắc cho contract mới:**
  - JSON Schema;
  - tên `<ten>.v<so>`;
  - Anh duyệt trước khi kích hoạt (TL 55 §11.4);
  - đổi không tương thích thì lên số mới, giữ bản cũ cho việc đang chạy.
- **Kết quả nào cũng có:** `nguon_doc`/`model`, `phien_ban_engine`, `bam_dau_vao`, `trich_dan` (nếu có), `canh_bao[]`. Tiền luôn kèm đơn vị tiền tệ.

## 8. Quy tắc bắt buộc cho mọi engine

1. **Không gọi engine khác**, kể cả qua HTTP. Cần bước trước hoặc sau thì khai trong chuỗi ở module.
2. **Không mật khẩu CSDL, không SQL.** Dữ liệu lâu dài nằm trong ngăn của engine, đi qua thao tác 12.
3. **Cloud chỉ qua Mask.** Không ra internet ngoài `ket_noi_ngoai`. Bản 1 Hỏi AI chỉ dùng Local.
4. **"Chưa rõ" là trạng thái chung:** nguồn ngoài đã nhận mà chưa trả thì báo `CHUA_RO`, không báo thành công giả. Core giữ lượt bền; lần sau chốt bằng cùng mã tương quan.
5. **Lỗi bằng tiếng Việt dễ hiểu.** Không lộ đường dẫn, khóa hay định danh. Vượt trần thì từ chối, không cắt ngầm.
6. **Chạy thử chỉ bằng dữ liệu DEMO**, qua màn Chạy thử chung (chỉ Admin). Không dùng dữ liệu thật trong test.
7. **Gói độc lập:**
   - ghim thư viện (`requirements.lock`) và có `NGUON.md` (nguồn, giấy phép, SHA-256);
   - cài được trên máy sạch;
   - **không import `kho_tri_thuc.*` ngoài SDK**.
8. **Giao diện ẩn thông tin kỹ thuật.** Phiên bản và cấu trúc chỉ hiện ở phần thông tin engine trong Quản lý engine.

## 9. Vì sao engine vẫn nằm trong Core — và việc của lead Core

| Nguyên nhân | Chỗ trong mã Core (`ma-nguon-core\src\kho_tri_thuc\`) | Phải đổi thành |
|---|---|---|
| Bộ nạp và bộ khởi động **ép engine nằm trong gói Core** | `core/nap_engine.py:99` và `core/khoi_chay_engine.py:77`: `prefix = 'kho_tri_thuc.engines.' + ma` | Nạp gói engine từ thư mục/gói riêng (K1b). Bỏ tiền tố cố định |
| Kênh engine có nhánh riêng từng engine | `core/kenh_engine.py`: `doc_function_chay_thu_hoi_ai` (dòng 45), `_XungDotLuotMask`, `goi_mask` (310), `DauVaoMask`, `la_chay_thu_hoi_ai` (519), kiểm Hỏi AI (830–932), `_nguon_ocr`/`_ocr` (1047–1190), `_mask` (1190–1268) | Thao tác chung: lượt bền (9), ngăn engine (12), kiểm schema theo contract khai báo |
| Dịch vụ engine có nhánh Hỏi AI | `core/dich_vu_engine.py:129–240` (`nguon_hoi_ai`, schema `hoi_ai.v2`); `core/chay_core.py:635–650`; `core/ho_so_module.py:76` (`doc_hoi_ai`, `ham_hoi_ai`) | "Nguồn đầu vào từ khai báo module" chung (prompt là tham số của module, theo GAN-QUY-TRINH) |
| Kênh module gắn kho riêng | `core/kenh_module.py:964–969` (`if hs.ma_engine == 'e_mask'` / `'e_ocr'`) | Bỏ; dùng ngăn engine và lượt bền chung |
| Route, màn, SQL riêng | `core/mask.py` (import `engines.e_mask`, **đã hỏng** khi chuyển engine ra), `kho_mask.py`, `routes_mask.py`, `ocr_doi_chieu.py`, `routes_ocr_doi_chieu.py`; `routes_quan_tri.py:540–626, 1207–1222, 1646` (`e_hoi_ai/local`, `from ..tri_thuc import ai_cuc_bo` **đã hỏng**); `ung_dung.py:48–49, 84–102, 1572–1574`; `ui/chay_thu_hoi_ai.js`, `chay_thu_mask.js`, `ocr_doi_chieu.js`, `danh_muc_trich_mau.js` (+ ô mở màn trong `quan_tri.js`, `index.html`); SQL 113, 117–120 (Mask), 126, 130, 131 (OCR), 129 (AI), 108 `danh_muc_trich` (kho bộ tham số trích ở Core — Anh đã bỏ hướng này 07/11, cần migration bù LHD-C1-BU) | Màn chạy thử chung, màn cấu hình dựng từ schema, giao diện quản trị engine nạp từ gói, ngăn engine |
| SDK có hàm riêng OCR | `sdk_core/engine.py:85–137` | Lượt bền chung |
| Mã thế hệ cũ K2 gọi engine trích #6 | `nguon/trich6_host.py`, `trich_chung_6.py`, `trich_hop_dong_6.py` (dùng bởi `core/tien_trinh.py`, `giao_dien/server.py`, `k2/*`, `m4/*`, `m2/*`) | Chuyển `_JobWindows` / `_doc_dong` sang tiện ích chung; phần trích để project `e_trich_xuat` |
| Test Core dùng engine thật làm mẫu | `tests/test_bm_kenh.py`, `test_g2_32_e1.py`, `test_khoi_chay_engine.py`, `test_module_phu_thuoc.py` | Dùng engine giả `e_mau` |

**Đã xử lý ngày 08/11:**
- Mã engine, test riêng, công cụ và `.cmd` riêng đã chuyển sang `D:\Claude\Engines\<engine>\`.
- Các tệp phía Core ở bảng trên được **sao** sang `Engines\<engine>\tu-core-cu\phia-core\` để tham chiếu. Bản trong Core **vẫn để nguyên** để Core còn khởi động được. Lead Core gỡ khi đã có cửa chung thay thế.
- Thư mục rỗng `engines\` đã chuyển vào `D:\Claude\Core\LUU-TRU\20261108-tach-engine\`.

## 10. Nghiệm thu cổng engine (điều kiện "SẴN SÀNG")

1. **Engine mẫu `e_mau`** viết bằng SDK, nằm ở thư mục riêng ngoài Core. Cài qua Quản lý engine, không sửa dòng mã Core nào.
2. Chạy **một việc cục bộ** và **một việc từ xa qua HTTP** (máy khác hoặc cổng khác). Cả hai cho cùng kết quả, cùng nhật ký.
3. Webhook `viec.co_moi` đánh thức engine từ xa. Tắt webhook thì engine vẫn kéo được việc. `viec.huy` dừng đúng việc.
4. Khai một **chuỗi 2 bước** gồm `e_mau` và một engine thật (ví dụ `e_hoi_ai`) trong module DEMO. Core kiểm khớp kiểu vào/ra. Kết quả về đúng ngăn module.
5. Thêm **engine thứ hai** chỉ bằng khai báo: chuỗi chạy được, không sửa bộ điều phối và không sửa engine cũ.
6. **Bài quét G14:** tìm trong mã nguồn Core các tên `e_hoi_ai|e_ocr|e_mask|e_trich_xuat|e_hoa_don|e_tra_cuu|e_doi_chieu` và các tiền tố capability (`ai.`, `ocr.`, `mask.`, `trich.`, `hoa_don.`) → **0 kết quả**, ngoài dữ liệu DEMO của test.
7. Kiểm trên **trình duyệt thật trong khung Core**, có ảnh từng bước.

## 11. Câu cần Anh chốt (không chặn việc)

| # | Câu | Đề xuất |
|---|---|---|
| E1 | Engine từ xa xác thực bằng khóa (token) theo phiên bản engine kèm danh sách IP được phép (như OCR-KETNOI), hay dùng chứng thư hai chiều (mTLS)? | Khóa + IP cho v1; mTLS khi đưa ra máy chủ |
| E2 | Webhook ra **hệ thống ngoài tập đoàn** có cần không? | Chưa mở ở v1; chỉ đích nội bộ đã đăng ký |
| E3 | Thời hạn Core giữ kết quả tạm khi module chưa lưu | 7 ngày, sau đó chuyển lưu trữ và báo module |
