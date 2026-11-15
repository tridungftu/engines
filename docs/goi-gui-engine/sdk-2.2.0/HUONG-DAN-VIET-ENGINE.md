# Hướng dẫn viết engine — SDK 2.0.0

*Cho người viết engine (các project engine). Đi kèm bản phát hành SDK 2.0.0 tại `D:\Claude\Core\goi-san-sang\sdk-phat-hanh\2.0.0\`.*

## Tóm tắt

- **Hợp đồng phía engine đã khóa ở bản 2.0.0:** phiếu `engine.json` 2.0, API `/api/v1/engine/…`, và SDK. Muốn đổi gì thì phải tăng phiên bản (2.0.1, 2.1.0…) và ghi rõ thay đổi. Engine không tự đổi hợp đồng; thấy thiếu thì báo lead.
- Viết một engine gồm 6 bước: **cài SDK → điền phiếu → viết hàm → tự kiểm bằng Core giả → chạy 3 engine mẫu → nối Core thật.**
- Engine chỉ dùng thư viện chuẩn Python và SDK. Không cần mạng, không cần cơ sở dữ liệu.

## 1. Cài SDK (không cần mạng)

Thư mục phát hành gồm:

| Tệp | Là gì |
|---|---|
| `kho_tri_thuc_sdk-2.0.0-py3-none-any.whl` | Gói SDK (phần module và phần engine) |
| `*.whl.sha256`, `SHA256SUMS.txt` | Mã băm để kiểm gói không bị đổi |
| `HUONG-DAN-VIET-ENGINE.md` | Tệp này |
| `MAU-PHIEU-ENGINE.md` | Giải thích từng trường của phiếu, có phiếu mẫu |
| `engine-demo\` | 3 engine DEMO mẫu |

Cài vào môi trường riêng của project engine (Python 3.11 trở lên):

```
certutil -hashfile kho_tri_thuc_sdk-2.0.0-py3-none-any.whl SHA256
python -m venv .venv
.venv\Scripts\activate
python -m pip install --no-index --no-deps <thư mục phát hành>\kho_tri_thuc_sdk-2.0.0-py3-none-any.whl
python -c "import kho_tri_thuc_sdk; print(kho_tri_thuc_sdk.__version__)"
```

- So kết quả `certutil` với dòng của tệp wheel trong `SHA256SUMS.txt`. Kết quả lệnh cuối phải là `2.0.0`.
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

## 5. Chạy 3 engine DEMO mẫu

```
cd <thư mục phát hành>\engine-demo
python -m kho_tri_thuc_sdk.thu e_demo_doc_tep
python -m kho_tri_thuc_sdk.thu e_demo_chu_hoa
python -m kho_tri_thuc_sdk.thu e_demo_dem_tu
```

Cả 3 phải in `[ĐẠT]`. Ghép theo thứ tự đọc tệp → chữ hoa → đếm từ thì thành quy trình 3 bước (mẫu phiếu mục 5).

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
