# demo_ho_so — Hồ sơ DEMO (gói module DEMO)

Gói module DEMO đặt **ngoài Core**, viết theo `D:\Claude\Core\docs\HOP-DONG-CONG.md` phần (a) bản 1.5 (a.10), dùng để nghiệm thu cổng module: cài vào Core chỉ bằng gói này, **không sửa dòng nào của Core**. Chỉ dữ liệu DEMO.

## Gói khai báo gì (`module.json`, `phien_ban_manifest: 2`)
- **Quyền** (`quyen`): `ho_so.xem`, `ho_so.lap`. Động từ chỉ thuộc danh mục Core; Core tự gắn tiền tố mã module khi nạp.
- **Hành động** (`hanh_dong`): `GET /ho-so` (danh sách hồ sơ) và `GET /ho-so/{id}` (xem một hồ sơ), quyền `ho_so.xem`, thao tác SDK `ngan.doc`. Core dựng route `/api/v1/module/demo_ho_so/...`.
- **Câu lỗi** (`ma_loi`): `HO_SO_KHONG_TIM_THAY`, `HO_SO_MA_KHONG_HOP_LE`, mỗi mã có `thong_diep` tiếng Việt.
- **Ngăn** (`du_lieu.ngan`): `ho_so` với cột `ten_ho_so`, `noi_dung` (văn bản), `so_tu`, `so_dong` (số), `tep_goc` (tệp). Core tự thêm cột chuẩn và dựng bảng khi cài.
- **Contract** (`contract.cong_bo`): một contract `demo_ho_so_ho_so` v1 (một dòng hồ sơ). Cơ chế ghim của Core ghim mọi hành động vào contract công bố duy nhất này.
- **Nút** (`nut`): `doc_tep` "Đọc tệp" ở phần Tổng quan, thao tác đầu là tải tệp `text/plain` tối đa 1 MiB, kết quả vào ngăn `ho_so`, quyền `ho_so.lap` (nút tạo bản ghi mới). Gắn quy trình vào nút và ghép trường vào cột là việc của Admin trên màn Core.
- **Sự kiện** `quy_trinh.xong`: backend thêm một dòng vào `ho_so` theo bảng `ghep`. Tệp đã tải (`tep_nut`) ghi vào `tep_goc`, tên tệp ghi vào `ten_ho_so`; cột nào Admin đã ghép tường minh thì lấy giá trị ghép.

## Tệp trong gói
| Tệp | Vai trò |
|---|---|
| `module.json` | Phiếu module 2.0 |
| `KIEM-KE.json` | Kiểm kê byte và SHA-256 của mọi tệp trong gói (trừ chính nó) |
| `backend/chay.py` | Điểm vào Core gọi (`backend.diem_vao` = `backend.chay`) |
| `backend/xu_ly.py` | Hàm xử lý theo `hanh_dong.ma` (chỉ đọc ngăn của mình) và hàm nhận `quy_trinh.xong` |
| `frontend/chinh.js`, `chinh.css` | Màn: danh sách hồ sơ và chỗ đặt nút `data-ktt-nut="doc_tep"` |
| `schema/*.json` | Schema đầu ra hai hành động (draft 2020-12) |
| `contract/*.json` | Mô tả, schema và ví dụ của contract công bố |
| `demo/ho_so_mau.txt` | Tệp văn bản DEMO để thử nút "Đọc tệp" |

## Lệnh
- Tạo lại kiểm kê sau khi sửa bất kỳ tệp nào: `python -X utf8 goi-demo\module\tao_kiem_ke.py goi-demo\module\demo_ho_so`
- Chỉ kiểm, không ghi: thêm `--kiem`.
- Test thuần (không Core, không CSDL): `.\test.ps1 -Module test_goi_demo_module`

## Còn thiếu để cài vào Core
Bộ kiểm gói bản nháp của W3 đã nhận gói (kiểm tĩnh). Còn chờ cửa chung và SDK 2.0 phía module gộp vào main:
1. **Thao tác SDK `ngan.*` chưa có trong Core:** bản nháp W3 từ chối khi ghim launch (`CD060_SDK_DUNG_CHUA_HO_TRO`).
2. **`ngan.them` cho hàm nhận sự kiện chưa có chỗ khai:** `sdk_dung` chỉ nằm trong từng `hanh_dong`, mà gói không có hành động ghi nào. Gói chưa khai `ngan.them` để khỏi cấp quyền ghi cho hành động `GET`. Cần chốt chỗ khai, ví dụ thêm khóa `sdk_dung` cho `nut`.
3. **Tên điểm vào SDK chưa chốt:** gói dùng tên đề xuất `module_runtime.chay_theo_khai_bao(XU_LY, su_kien=SU_KIEN, loi_nghiep_vu=...)`.
4. **`ngan(...).doc` chưa có tham số sắp xếp:** gói đọc hết các trang rồi tự sắp xếp, giới hạn 50 trang × 200 dòng.
