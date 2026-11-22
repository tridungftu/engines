# SDK 2.5.0 — ghi chú thay đổi (dự thảo 20/11/2026, chờ Anh duyệt)

Bản này **chỉ thêm, tương thích ngược với 2.4.0**. Đối chiếu CĐ-43 mục (1),
M4, W6–W8, G14 và lát L2.3/L4.2: hàm nhận của nút biết cả việc kết thúc lỗi.

## Module dùng được gì mới

- `SU_KIEN` đăng ký thêm `quy_trinh.loi` theo cùng cách `quy_trinh.xong`.
  Hàm nhận có chữ ký `(sdk, su_kien)`. Payload gồm `su_kien`, `viec_id`,
  `ma_loi`, `thong_diep` tiếng Việt an toàn; không chuyển log nội bộ.
- Dùng lại route, binding, quyền ủy nhiệm và kênh ký của nút.
  SDK chuyển lỗi trực tiếp, không đọc kết quả hoặc tệp của việc chưa XONG.
  Module không đăng ký hàm nhận lỗi vẫn trả nhận no-op.
- Core giữ biên nhận và giới hạn giao thông báo 5 lần, giãn cách tăng dần;
  không tự chạy lại việc. Cần áp migration **200** do lead cấp, chỉ thêm/thay hàm,
  không đổi bảng, không sửa 145/136 hay bộ áp migration.
- `CoreGia.phat_su_kien_quy_trinh` phát XONG/LOI theo trạng thái việc thử,
  dùng cùng hàm xử lý SDK; giữ chống trùng, giới hạn 5 lần, không chạy lại engine.
  Mỗi lời gọi thử giao một lần, không chờ thời gian giãn cách thật.

## Tài liệu và đóng gói

- `HUONG-DAN-VIET-MODULE.md` hướng dẫn đăng ký, lưu lỗi theo `viec_id`, dừng polling
  và hiện mã trong “Chi tiết hỗ trợ”.
- Module `demo_ket_qua_nut` **1.0.2** có hàm nhận lỗi; giữ nguyên ngăn và contract,
  cập nhật kiểm kê. Ca thử dùng tệp sai UTF-8 để engine báo lỗi.
- SDK 2.5.0 và các test ghim phiên bản do lead cập nhật trước lát này.
  Công cụ phát hành hiện có tự kèm tệp ghi chú này.

## Kiểm chứng và phát hành

Test kiểm đường giao Core, ủy nhiệm, lỗi tạm, SDK no-op, CoreGia,
module ghi LOI và màn dừng polling. Test PG riêng kiểm áp 200 hai lần,
ACL web/PUBLIC, việc LOI, trần 5 lần, chống trùng và hành vi XONG.
Kết quả test thuần ghi tại `var/codex-kiem.json`.

**lead chạy PG, review-lat và bấm thử trên Core thử; trình Anh duyệt trước khi phát hành 2.5.0.**
Phiếu này không commit, không phát hành.

## Lưu ý khi áp migration 200
- Sau khi áp 200, các việc **đã kết thúc lỗi từ trước** của nút mà chưa từng được giao sẽ được Core giao `quy_trinh.loi` **một lượt** cho hàm nhận của nút (mỗi việc tối đa 5 lần như sự kiện xong). Module thật nên chịu được sự kiện của việc cũ (tra không thấy dòng thì bỏ qua hoặc báo `VIEC_CHUA_GAN`).
- `ma_loi` trong sự kiện có dạng mã chữ hoa (`^[A-Z][A-Z0-9_]{0,79}$`); mã sai dạng được thay bằng `LOI_NOI_BO`. Module chỉ đưa `ma_loi` vào "Chi tiết hỗ trợ", câu hiện cho người dùng lấy từ `thong_diep`.
