# Bàn giao TX-5 cho module

Thư mục này ở ngoài gói runtime. `snapshot.py` là helper thuần; module tự quản kho, chọn bộ, prompt, lịch sử và quyền. Không sao chép E1; cài SDK 2.0.0 từ wheel đã ghim. Không tự chuyển bộ 37: E6 chưa được nghiệm thu.

## Nguồn và nơi tiếp nhận

| Nguồn hiện có | Module tiếp nhận |
|---|---|
| `kho_tri_thuc_sdk.danh_muc_tham_so`: `doc_danh_muc`, `kiem_tra_danh_muc`, `khac_biet`, `tao_mau_excel` | Backend module nhận bytes Excel, gọi E1; lưu phiên bản bất biến và lựa chọn trong kho module. E1 giữ dòng ngừng dùng; nhãn `luon_cloud` không cho phép gọi Cloud. |
| `e_trich_xuat/tu-core-cu/phia-core/danh_muc_trich_mau.js` U1a, đối chiếu `e_trich_xuat/tests-tu-core/danh_muc_trich_mau.cjs` | Màn module: loại, chọn Excel, kiểm/nạp, xem dòng, lịch sử và so sánh; thay nguồn RAM giả bằng backend module. Dùng textContent, kiểm quyền phía server. |
| Cùng JS, U1b: chạy thử và hộp kích hoạt | Màn module gửi việc thử, hiển thị tiến độ, dẫn chứng, khác biệt; module quyết định kích hoạt. Nguồn hiện chỉ mô phỏng; không xem là UI đã nối. |

Admin module quản bản riêng và kích hoạt theo quyền module. Admin Core xem/sửa theo quyền Core được cấp; không thêm quyền Kích hoạt ở Core. Màn người dùng ẩn phiên bản/hash. Không đưa UI này vào `goi/e_trich_xuat/ui/`, vốn chỉ cấu hình engine. Không chuyển nguyên SQL Core cũ; module chịu trách nhiệm thiết kế lưu trữ, kiểm quyền, chống đua và kiểm toán của mình.

## Cách dùng

```python
from snapshot import tao_snapshot
from kho_tri_thuc_sdk.engine import LoiNghiepVu

try:
    tham_so = tao_snapshot(excel_bytes_demo, module="module_demo",
                           loai_hop_dong="DEMO", phien_ban_bo="v1")
except LoiNghiepVu as exc:
    # Hiển thị exc.thong_diep an toàn; không log dòng, ô, đường dẫn hay hồ sơ.
    print(exc.thong_diep)
else:
    tham_so.update(prompt="Chỉ trích nội dung DEMO có căn cứ.",
                   ma_prompt="prompt_demo", phien_ban_prompt="v1",
                   ma_truong_can_trich_json="[]", yeu_cau_them_json="[]",
                   ngan_sach_token_vao=8000)
    # Module gửi bản sao tham_so cho từng việc qua cổng Core khi được hỗ trợ.
```

Bytes Excel sai cột/ô/mã trùng trả `BO_THAM_SO_KHONG_HOP_LE`; quá trần Excel/giải nén/snapshot/200 dòng hoạt động trả `VUOT_GIOI_HAN`. Không log chi tiết ngoại lệ E1. Danh mục hợp lệ giữ nguyên kết quả E1 gồm 10 cột theo thứ tự và các quy tắc. `bam_tep_goc` là SHA-256 bytes Excel, `ma_bam_noi_dung` là SHA-256 nội dung 10 cột theo E1 (không tiền tố), `bam_bo_tham_so` là SHA-256 bytes JSON đầy đủ (có tiền tố). Ba giá trị khác mục đích; không thay thế nhau. Module giữ cả chuỗi JSON và hash như cặp bất biến, không tự chuẩn hóa lại. Thiếu/sai hash phải từ chối; tuyệt đối không fallback XD.

Module chọn bản của chính mình trước mỗi việc, ghim snapshot, metadata và prompt riêng vào việc; đổi bộ về sau không sửa việc cũ hoặc cấu hình quy trình chung. Core cần xác thực module/pháp nhân, cấp quyền và xác nhận cổng tham số theo từng việc (C-TX-01); hash không chứng minh quyền. Kiểm so sánh qua `khac_biet` trên hai kết quả `doc_danh_muc`, chạy thử và kích hoạt do module thực hiện. Không lưu kho bộ vào ngăn engine; `NganBoNho` chỉ giả cấu hình engine trong kiểm thử. Kết quả tiền và ngày của việc phải giữ kiểu và giá trị đã có; helper không chuyển đổi chúng.

Test `tests/test_tx5_ban_giao.py` dùng dữ liệu DEMO RAM, đối chiếu E1 trực tiếp và CoreGia + ngăn cấu hình giả. Đây không chứng minh module đã cài, Core thật đã nối, hay E6 đạt. Không mạng, không AI thật, 0 Cloud.
