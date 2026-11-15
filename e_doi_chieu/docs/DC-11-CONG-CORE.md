# DC-11 — học lỗi OCR có duyệt, 15/11/2026

**Chỉ DEMO; đã kiểm bằng Core giả (CoreGia), NganBoNho, KttCore giả.**
Chưa nối thao tác quản trị Core thật. Không capability, decorator, route
hay API SDK tự tạo; `chay.py` không gọi tự động lõi học. Không Cloud,
OCR/AI thật, kho JSON hoặc cấu hình trên đĩa. PR: **chờ lead mở**.

## Nguồn tin cậy và Q14

`loi_ocr.de_xuat`/`duyet` là hàm nghiệp vụ chưa đăng ký, chỉ gọi trực tiếp
trong test; `kiem_cap`/`bo_moi` là hàm thuần. Các adapter dưới đây là
**đề nghị C-DC-03, chưa phải API SDK được phát hành**:

- Dùng lại `cong.cap_ngu_canh(viec, ma_luot)` của DC-10. Core cấp quyền
  `xem_doi_chieu` + `de_xuat_loi_ocr`; duyệt cần đồng thời `duyet_loi_ocr`
  và `admin_core`. Người, giờ có múi giờ, pháp nhân/module/lượt do host
  tin cậy cấp. Không dựng quyền hoặc đối tượng `cong` từ JSON/UI.
- Đề nghị `cong.cap_bo_q14(viec)` trả `BoQ14`: bộ chứng minh từ/cặp có
  giấy phép đã duyệt, băm, mã phê duyệt và chứng nhận sạch định danh.
  Host phải xác minh phê duyệt/thu hồi. Dataclass, băm hoặc mã phê duyệt
  **không tự chứng minh quyền/an toàn**, không dựng từ payload người dùng.
- Q14 là nguồn căn cứ riêng; cặp được chứng nhận vô nghĩa rõ ràng mới
  được học. Vắng mục trong từ điển hữu hạn không đủ chứng minh. Bộ căn
  cứ không tự trở thành từ điển đang chạy DC-7. Fixture chỉ DEMO, chưa
  thay nguồn sạch/băm/giấy phép lead cần trình theo Q14.
- Đọc lại báo cáo/snapshot/tệp qua DC-10 `_doc`, kiểm băm và tổng hợp;
  lấy cặp token tại vị trí đã ghim. Không nhận chữ/số đếm/nhãn tin cậy
  từ UI. Chỉ xác nhận `loi_ocr` đúng nguồn/module; có xác nhận mâu thuẫn
  thì từ chối. Cấm cặp thuê/thuế, lãi/lại… cả hai chiều, vùng bảo vệ/quy
  tắc cứng, số/mã, nhiều token và cặp chưa rõ nghĩa. Quét lại vùng bảo
  vệ trên toàn token vì diff có thể chỉ là một dấu.

## Đếm, duyệt và snapshot

- `loi_ocr_de_xuat`: phạm vi pháp nhân, khóa băm cặp/căn cứ/Q14, thêm
  `noi_dung` JSON trong chuỗi ≤64 KiB theo SDK 2.2. Quá trần từ chối
  `DC_QUA_GIOI_HAN`, không cắt lịch sử. Tham chiếu xác nhận/lượt/điểm/băm
  nằm trong đề xuất; không lưu toàn văn. Cần thiết kế tiếp nếu vượt trần.
- Đếm một vị trí theo băm lượt + kết quả + điểm. Gửi lại, mất ACK hoặc
  nhiều người xác nhận cùng điểm không cộng hai. Bản đầu từ chối gom
  chứng cứ khác module, chờ Core review quyền xuyên module trước khi nới.
- `viec.cau_hinh.hoc_loi_ocr`: `so_lan` nguyên dương, `phien_ban`,
  `nguon_do`, `ma_phe_duyet`; **không mặc định**. Thiếu thì không học/duyệt.
  Số 1/2 trong tests là ngưỡng giả để kiểm biên, không là số đo vận hành.
  Form giới hạn giữ nguyên ngưỡng Core đã cấp, không tự tạo/sửa ngưỡng.
- Đủ ngưỡng chỉ `cho_nguong` → `cho_duyet`. DC-7 không đọc đề xuất. Admin
  duyệt kiểm lại Q14/ngưỡng và mọi nguồn/xác nhận, CAS đề xuất/các lượt.
  **Một Ngan.lo** đổi trạng thái, ghi người/giờ/mã yêu cầu/phiên bản trước
  và thêm bộ mới. Xung đột rollback cả lô, `DC_XUNG_DOT`,
  `thu_lai_duoc=True`. Gửi lại cùng yêu cầu/người trả receipt; tranh phiên
  bản một bên thắng, bên kia tải lại.
  Tối đa 98 lượt nguồn để chừa hai lệnh đề xuất/bộ trong trần 100 lệnh
  SDK; vượt thì từ chối, không cắt ngầm hoặc chia giao dịch duyệt.
- `loi_ocr_da_duyet`: phạm vi engine, bộ một cặp tương thích `TuDien`,
  khóa cặp + phiên bản từ băm nội dung/căn cứ. Chỉ thêm/lấy bộ trùng,
  không sửa phiên bản; nội dung có sẵn khác thì từ chối. Bộ chỉ có token
  vô danh, băm căn cứ/Q14 và mô tả cố định; không người, pháp nhân,
  mã hồ sơ/điểm/xác nhận hoặc đoạn văn. Người/giờ ở đề xuất pháp nhân.
- Core ghép/xuất bộ thành tệp Core và ghim mã/phiên bản/băm cho **việc
  mới**, như DC-7. Không tự cập nhật cấu hình/snapshot lượt cũ. Bộ mới
  trong ngăn chưa đổi kết quả máy; chưa nối đường phát hành bộ thật.

## Màn chỉ đọc và phần bắt buộc trước vận hành thật

`ui/loi_ocr.js` dùng `KttCore.engine("e_doi_chieu").ngan.tim`, phân trang,
textContent; không ghi ngăn/thao tác quản trị/nút duyệt/mạng ngoài/eval.
Host chỉ nạp cho Admin, gắn view đúng pháp nhân từ phiên Core và đặt
`{nguCanhDaGan: true}` sau khi gắn. Cờ chỉ chặn đọc khi UI chưa khởi tạo,
**không thay phân quyền/pháp nhân phía Core**. Màn chỉ đọc danh mục của
mình. Thiếu quyền/ngữ cảnh có câu Việt cố định, không lộ lỗi kỹ thuật.

**Bắt buộc:** Q14 nguồn sạch/băm/giấy phép/bộ cặp được duyệt; số đo và
ngưỡng được phê duyệt; C-DC-03 chung có thao tác quản trị, quyền/người/giờ
tin cậy, kiểm quyền tại commit, CAS/chống trùng/nhật ký bền. Cấm ngăn
Admin tổng quát cho UI/người dùng ghi đề xuất, xác nhận hoặc kho đã duyệt
để vượt cổng. SQL 003 chỉ thêm cột, chưa tạo ACL/kiểm toán, chưa chạy DB
thật. Cần review loader/CSP/màn, RLS/khởi động lại và phát hành bộ mới.
Chưa kiểm Core thật, Linux, trình duyệt Core hoặc chất lượng từ điển thật.

Lỗi: `DC_CAP_DOI_NGHIA`, `DC_KHONG_DU_CAN_CU`, `DC_XUNG_DOT`; câu Việt
cố định không chứa cặp từ/đường máy; dùng lại lỗi quyền/nguồn DC-10.

## Chia phạm vi thay đổi

- **DC-11:** `loi_ocr.py`, `ui/loi_ocr.js`, ghi chú `chay.py`, SQL 003
  (4 tệp mã; manifest/bản khai màn là metadata).
- **DC-11-CH:** schema cấu hình + hai dòng giữ ngưỡng ở `ui/cau_hinh.js`
  (2 tệp). Tách vì tổng vượt khoảng 5 tệp; nếu thiếu, form cũ làm mất
  ngưỡng đã duyệt khi lưu giới hạn. Không thêm form sửa ngưỡng.

Không sửa ma-nguon/Core/SDK/schema chung/mẫu NGAN-0. Hai bản chép NGAN-0
hiện có giữ nguyên, test băm LF; runtime dùng viec.ngan. Không commit/push.
