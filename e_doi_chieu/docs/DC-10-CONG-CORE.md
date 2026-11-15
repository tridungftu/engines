# DC-10 — adapter chờ Core, 15/11/2026

Đã kiểm bằng Core giả (CoreGia), NganBoNho và KttCore/DOM giả trên Node.
**Chưa tích hợp Core thật**, chưa kiểm trình duyệt Core, lưu bền, RLS/quyền
thật, đồng hồ thật, CSP hoặc trạng thái hiệu lực module. Các tên adapter
dưới đây là **đề nghị binding**, không phải API/SDK đã được phát hành.
Không thêm route, HTTP server, decorator, capability hoặc event riêng.

## C-DC-01: nạp màn và cấu hình

- Hai module JS `ui/cau_hinh.js`, `ui/ket_qua.js` export default, nhận
  phần tử gốc và `KttCore`; mỗi màn chỉ đọc phần dữ liệu của mình.
- `KHAI-SDK-2.1.json` mới chỉ khai màn/quyền đề nghị. Không khôi phục bản
  khai ngăn tạm đã lưu trữ tại `LUU-TRU/DC-S22`; không thêm khóa màn vào
  `engine.json`. Manifest vẫn phiên bản 2, dùng SDK 2.2.0.
- Màn cấu hình dùng `.cau_hinh.doc()` và `.luu(gia_tri, phien_ban_cau_hinh)`.
  CAS phía Core là token riêng, không nhầm chuỗi `phien_ban_cau_hinh` trong
  nội dung bộ kiểm. Core kiểm schema; UI kiểm kiểu/trần số giống schema.
  Xung đột hoặc mất phản hồi đều khóa lưu tới khi người dùng tải lại;
  không tự ghi đè hoặc tự đọc lại rồi gửi nội dung cũ.
- Giữ nguyên bảy trường ghim của bộ chuẩn hóa/từ điển/detector; không
  cho sửa mã/băm từ form giới hạn. Chưa có bộ thì hiện hướng dẫn và khóa
  lưu. Core/lead cần cấp bộ đã duyệt trước; không tạo bộ/ngưỡng mặc định.
  Ngưỡng OCR kém tiếp tục `null`. Không thêm cấu hình máy OCR/Local AI.
- Cần Core xác nhận cơ chế loader, quyền Admin sửa cấu hình, nội dung
  trả/ACK/CAS và CSP. Node giả không chứng minh loader/CSP thật.

## C-DC-03: nguồn quyền và giao dịch xác nhận

Python có ba adapter trong `chay.py`: `doc_ket_qua`, `xac_nhan`,
`gui_yeu_cau_module`. **Không đăng ký bằng `@app.nang_luc`** và không
giả lập `@app.thao_tac_quan_tri` chưa có. Thiếu `cong` thì từ chối bằng
`DC_CHUA_CO_CONG_XAC_NHAN` hoặc `DC_CHUA_CO_CONG_MODULE`.

Host Core phải cấp đối tượng `cong` bằng code tin cậy, qua binding chung;
không dựng từ JSON UI, tham số bước, hồ sơ hoặc metadata caller tự khai:

| Thành phần adapter đề nghị | Trách nhiệm |
|---|---|
| `cong.cap_ngu_canh(viec, ma_luot)` | Trả `NguCanhXacNhan` từ phiên đăng nhập, giao quyền module và đồng hồ Core. Ghim pháp nhân/module/lượt, danh tính/tên hiển thị, giờ ISO có múi giờ, quyền và tập điểm được xác nhận. Engine đối chiếu ngữ cảnh việc. |
| Quyền `xem_doi_chieu` | Đọc đúng hồ sơ và nhật ký. Mọi tệp mở lại bằng `viec.mo_tep`; mất quyền báo cáo cũ thì gửi lại cũng bị từ chối. |
| Quyền `xac_nhan_doi_chieu` | Người phụ trách được module giao; người nộp không tự có quyền (Q02). Không suy quyền từ Admin ngăn. |
| Quyền `duyet_thay_doi_nghiem_trong` | Người thứ hai có thẩm quyền, khác người đầu cho thay đổi Nghiêm trọng đã thống nhất (Q03). |

Payload UI chỉ nhận `ma_luot`, `ma_diem`, `ma_yeu_cau`, `row_version`,
`lua_chon`, `noi_dung_dung`, `ly_do`. Trường người/giờ/quyền thêm vào bị
từ chối. Nội dung đúng bắt buộc cho `thay_doi_da_thong_nhat`; lý do bắt
buộc cho `khong_anh_huong`. Bốn lựa chọn không đổi mức/kết quả máy.

Đọc báo cáo DC-9 từ lượt `da_xuat` trong ngăn, kiểm băm JSON/PDF và quyền,
mở lại snapshot upstream ghim và nguồn, tính lại tổng hợp rồi so báo cáo.
Không nhận kết quả/số đếm/pháp nhân do UI gửi. Nhật ký gắn băm kết quả.

Trong **một lô**: `them(xac_nhan)` và `sua(luot_doi_chieu, row_version=…)`
giữ nguyên `trang_thai=da_xuat` để tăng phiên bản CAS. Nhật ký không có
đường sửa/xóa. Mã yêu cầu duy nhất theo pháp nhân; gửi lại cùng nội dung,
phiên bản gốc và người nhận cùng receipt, không thêm lần hai. Dùng lại mã
cho người/nội dung khác bị từ chối. Không tự tăng hoặc đoán row_version.

Hai người tranh cùng phiên bản: một lô thắng, lô kia rollback cả nhật ký,
trả đúng `DC_XUNG_DOT`, câu Việt đã giao và `thu_lai_duoc=True`. Người
thua tải lại rồi gửi xác nhận mới, cả hai bản ghi được giữ. Cùng mã đua
nhau thì đọc receipt đã chốt. Sau mất ACK, UI gửi lại đúng mã/nội dung.

Một người không được xác nhận điểm đó lần hai bằng mã khác. Quyết định
khác nhau giữa các người giữ trạng thái cần xử lý; không chọn bản ghi
cuối để đè trước. `ban_ky_sai` của cặp hiện tại luôn giữ chặn, cần bản ký
mới/phụ lục và đối chiếu cặp mới. Q04: vùng sửa tay là điểm bắt buộc như
Nghiêm trọng; không đọc chữ tay tự động.

**Core phải thực thi** chỉ-thêm/ACL và kiểm lại quyền trong giao dịch khi
commit, chống trùng/lease/thu hồi quyền, kiểm toán bền và rollback. API
ngăn Admin tổng quát phải cấm UI ghi `xac_nhan` hoặc sửa lượt để lách
cổng này. SQL 002 chỉ thêm ba cột; **không phải** cơ chế ACL/chỉ-thêm.
Không có binding đã được Core review thì không bật xác nhận thật.

### Adapter trình duyệt đề nghị

Host gọi `ketQua(goc, KttCore, {ma_luot, cua})`, với `ma_luot` và `cua`
do khung Core cấp. Màn đọc `.ngan.doc("luot_doi_chieu", {ma_luot})` để
ghim token; các thao tác tiếp theo chỉ qua đối tượng `cua`:

| Hàm | Ý nghĩa |
|---|---|
| `cua.doc_ket_qua({ma_luot,row_version})` | Binding tới adapter đọc đã kiểm nguồn/quyền, trả báo cáo + nhật ký + tập quyền/điểm được Core cấp. Phiên bản khác thì từ chối/tải lại. |
| `cua.xac_nhan(yeu_cau)` | Chuyển qua C-DC-03, không qua `.ngan.ghi_lo`; chỉ ACK `da_luu=true` và cùng mã yêu cầu mới hiện đã lưu. |
| `cua.hien_tep(tham_chieu, phan_tu)` | Core kiểm quyền từng tệp, băm/hộp/hệ tọa độ và tự dựng ảnh vùng/PDF. Màn không gán URL/src/href từ hồ sơ. Thiếu ảnh/hộp thì hiện rõ, không bịa crop. |
| `cua.gui_yeu_cau_module({ma_luot})` | Binding C-DC-04 ở dưới, không đổi hiệu lực ngay trong UI. |

Có cửa xem mà chưa có cửa xác nhận hoặc chưa có quyền thì xem được hai
cột/nhật ký, **không có nút Lưu xác nhận**. Cả cửa xem thiếu thì chỉ hiện
lỗi Việt/tải lại, không tự mở tệp hoặc dựng URL. Nhiễu OCR ẩn mặc định,
có nút xem và bộ lọc; ảnh mở qua Core ở ngay cột bản ký. Nguyên văn dùng
`textContent`/`mark`, giữ chính xác bằng chứng; ngày của metadata/nhật ký
hiện dd/mm/yyyy theo UTC+7, tiền có đơn vị. Không sửa ngày trong câu
nguyên văn để tránh làm khác chứng cứ. Không có mạng ngoài, eval, HTML
chưa lọc, localStorage hoặc sessionStorage. Nút/ô nhập có focus rõ; bố
cục hai cột chuyển thành một cột ở màn hẹp, dùng font kế thừa từ Core.

## C-DC-04: yêu cầu module và hiệu lực

`dieu_kien_module` chỉ lập bằng chứng đề nghị, không cập nhật hiệu lực.
Phải đủ kiểm bắt buộc, mọi điểm Nghiêm trọng/Cần xem/vùng sửa tay có
xác nhận hợp lệ, không mâu thuẫn và không `ban_ky_sai`. Điểm Nghiêm trọng
chọn đã thống nhất cần cùng nội dung/quyết định, hai người khác nhau và
có người duyệt cấp hai. Nguyên văn máy và cờ đề nghị chặn máy giữ nguyên.

`cong.gui_yeu_cau_module(viec, yeu_cau)` nhận pháp nhân/module/lượt,
row_version, băm kết quả, điều kiện và mã chống trùng; người nhận là
`nguoi_nop_va_nguoi_phu_trach` theo quyền Core (Q01). Thiếu cổng thì lỗi;
đã gọi nhưng thiếu ACK thì `ChuaRo`, không giả đã nhận. Core phải kiểm
phiên bản/quyền và **tính lại** từ hồ sơ/nhật ký khi áp dụng; không tin
boolean đề nghị như quyền mở chặn. Core/module giữ dữ liệu tầng 1, việc
theo dõi bản ký sai, quy trình gửi đúng người và trạng thái hiệu lực.

## Phạm vi và nguồn

Năm tệp triển khai có logic: hai JS, `xac_nhan.py`, `chay.py` và migration
`002_xac_nhan.sql` (chỉ soạn, chưa chạy trên DB). Để tuân yêu cầu lead
chép nguyên NGAN-0, phần **DC-10-NGAN0** tách riêng hai bản chép nguyên
trong `tham_chieu_ngan_0/`, chỉ test/đối chiếu SHA-256 sau CRLF→LF, không
import trong runtime. `NganBoNho` được adapter test chuẩn hóa chữ ký
`them` và ngoại lệ sang SDK 2.2, không sửa mẫu. Không đưa ngăn RAM vào
đường chạy thật hoặc tuyên bố RAM là nhật ký đã bền. Không thêm dependency,
schema loại dữ liệu, Cloud, đĩa bền, công cụ máy thật, commit/push.
