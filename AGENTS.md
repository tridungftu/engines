# AGENTS.md — Hướng dẫn cho Codex khi code engine trong repo này

Người đặt yêu cầu: **Anh Dũng** (CFO). Lead điều phối: Claude. Người code: Codex.
Mọi tài liệu, thông báo lỗi, báo cáo bằng **tiếng Việt**; tên mã dùng tiếng Việt không dấu như mã hiện có.

## 1. Đọc trước khi code (theo thứ tự)

1. `docs/goi-gui-engine/API-ENGINE-v1.md` — hợp đồng API v1 + `engine.json` 2.0. **Đã khóa, không được đổi.**
2. `docs/goi-gui-engine/sdk-2.0.0/HUONG-DAN-VIET-ENGINE.md` và `MAU-PHIEU-ENGINE.md`.
3. `_chung/docs/GIAO-CODEX-THU-TU.md` — thứ tự engine, quyết định tạm, phần còn thiếu phía Core.
4. `_chung/docs/LOAI-DU-LIEU-RIENG.md` — loại dữ liệu riêng dùng chung giữa các engine.
5. `<engine>/docs/GIAO-CODEX-<engine>.md` — lát đang được giao.
6. `<engine>/CLAUDE.md`, `<engine>/docs/YEU-CAU-VA-HIEN-TRANG.md`, quyết định cuối của engine.

Khi hai tài liệu mâu thuẫn: **API-ENGINE-v1 + SDK 2.0.0 thắng** về kỹ thuật cổng; **quyết định cuối của engine thắng** về nghiệp vụ. `_chung/docs/YEU-CAU-CHUNG-ENGINE.md` (08/11) là bản trước SDK 2.0, chỉ dùng làm nguyên tắc.

## 2. Môi trường

```bash
python -m venv .venv && . .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install --no-index --no-deps docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl
python -c "import kho_tri_thuc_sdk; print(kho_tri_thuc_sdk.__version__)"   # phải in 2.0.0
sha256sum docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl  # so với SHA256SUMS.txt
```
- Python ≥ 3.11. Máy đích là Windows x64; **test phải chạy được trên Linux** (mock phần Windows: ABBYY Hot Folder, tesseract.exe, ACL).
- Thư viện ngoài SDK: chỉ thêm khi phiếu lát cho phép, ghim trong `requirements.lock`, ghi `NGUON.md`.

## 3. Bố cục mỗi engine (SDK 2.0)

```
<engine>/
├── goi/<ma>/                 ← THƯ MỤC GÓI gửi Core (chỉ chứa thứ cần chạy)
│   ├── engine.json           ← phiếu 2.0
│   ├── README.md
│   ├── demo/                 ← dữ liệu DEMO giả, có nhãn DEMO
│   └── <ma>/                 ← gói Python: __init__.py, chay.py, các mô-đun lõi
├── tests/                    ← test pytest (NGOÀI thư mục gói)
├── ma-nguon/                 ← mã cũ: nguồn để chuyển sang, KHÔNG sửa, KHÔNG xóa
├── tu-core-cu/, tests-tu-core/, shim-kho_tri_thuc/   ← tham chiếu, chỉ đọc
└── docs/
```
- Chuyển mã từ `ma-nguon/` sang `goi/<ma>/<ma>/` (chép rồi sửa). Phần không dùng nữa: ghi vào `docs/VIEC.md` để chuyển `LUU-TRU/` sau, **không xóa**.
- `goi/<ma>/` không được có `__pycache__`, `.pyc`, symlink, tệp lớn.

## 4. Quy tắc cứng (vi phạm = lát không đạt)

1. Chỉ import `kho_tri_thuc_sdk` và thư viện đã ghim. **Không import `kho_tri_thuc.*`**, không dùng kênh socket cũ (`kenh_engine`, `SDKEngine`, `Bootstrap`).
2. Engine **không gọi engine khác**, không kết nối CSDL, không SQL.
3. Không đọc, in, sửa: `.env`, `cau_hinh.that.toml`, `var/plhn-that`, `var/web-that`, `D:\DU-LIEU-KE-TOAN\bi-mat`, thư mục `in/ out/ jobs/ state/` của abbyy-hotfolder.
4. Không ghi khóa, mật khẩu, đường dẫn máy thật vào mã, phiếu, log, test, git.
5. **Chỉ dữ liệu DEMO** (ví dụ "Công ty DEMO Ánh Dương", 1.000.000 VND, 30/10/2026). Không dùng hồ sơ thật.
6. Lỗi cho người dùng: `LoiNghiepVu("MA", "Câu tiếng Việt dễ hiểu.")` — không lộ đường dẫn, khóa, dữ liệu nghiệp vụ. Vượt trần thì từ chối, không cắt ngầm.
7. Nguồn ngoài đã nhận việc mà chưa trả → `raise ChuaRo(ma_tuong_quan)`. Không báo thành công giả.
8. Tiền luôn kèm mã tiền tệ (`{"so": 1000000, "tien_te": "VND"}`); ngày `YYYY-MM-DD` trong dữ liệu.
9. Cloud AI chỉ nhận nội dung đã qua Mask (xem `LOAI-DU-LIEU-RIENG.md`, loại `van_ban_da_che`).
10. **Không sửa** `docs/goi-gui-engine/**`, `_chung/tham-chieu-cong-hien-tai/**`, mã Core. Thiếu gì phía Core/SDK → ghi mục "Cần Core" trong `<engine>/docs/VIEC.md`, làm tiếp bằng lớp bọc tạm như phiếu chỉ dẫn.
11. Không xóa tệp. Không push lên nhánh `main`.

## 5. Cách làm một lát

- Mỗi lát một nhánh `codex/<engine>-<ma-lat>` và một PR; tiêu đề PR: `[<engine>] <mã lát> — <tên lát>`.
- Lát nhỏ: tối đa ~5 tệp mã sửa/thêm (chưa tính test, tài liệu). Vượt thì tách lát và ghi lý do.
- **Điều kiện đạt chung của mọi lát** (chạy và dán kết quả vào PR):
  ```bash
  python -m kho_tri_thuc_sdk.thu <engine>/goi/<ma>      # mọi ví dụ chay_thu_demo [ĐẠT], mã thoát 0
  python -m pytest <engine>/tests -q                    # 0 lỗi; skip phải có lý do
  python <engine>/tests/kiem_doc_lap.py                 # không import kho_tri_thuc.*, không __pycache__ trong goi/
  ```
- Cập nhật `<engine>/docs/VIEC.md` (trạng thái, ngày, mã PR) và `<engine>/goi/<ma>/CHANGELOG.md` (nếu có).
- Mọi kiểm tra trước khi nối Core thật ghi rõ **"đã kiểm bằng Core giả (CoreGia)"**. Không ghi "SẴN SÀNG".

## 6. Báo cáo cuối PR (mẫu)

```
Kết luận: Đạt / Chưa đạt — 1 câu.
Đã làm: …
Kết quả kiểm: kho_tri_thuc_sdk.thu → x/x ĐẠT; pytest → n passed, k skipped (lý do).
Thời gian thực tế: … giờ (ước tính trong phiếu: … giờ).
Lệch khỏi phiếu / quyết định tạm đã dùng: …
Cần Core / Chờ Anh mới phát sinh: …
```
