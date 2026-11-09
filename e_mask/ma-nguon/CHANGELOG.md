# CHANGELOG — e_mask

## Chưa phát hành — MASK-J8 (07/11/2026)

- Có vòng nhận việc: chờ khi hàng rỗng, xử lý xung đột tối đa ba lượt, kết thúc lỗi đúng trạng thái và dừng an toàn; mất xác nhận không kết thúc sai việc. Commit: `0a470d88`, `87d93e75`.
- Đối soát mất xác nhận phía Core là **J8b chưa làm**; màn chạy thử còn chờ phiếu [PHIEU-MASK-CHAY-THU-DEMO.md](../../docs/47-core/g3/PHIEU-MASK-CHAY-THU-DEMO.md), chưa nghiệm thu luồng trên Core DEMO.

## Chưa phát hành — MASK-3E-BS (07/11/2026)

- Đọc cụm chờ dạng object, giữ nhóm có thẩm quyền khi tái dùng bí danh; từ chối toàn bộ snapshot nếu cụm chờ sai cấu trúc hoặc nguồn. Commit: `088a4afb`, `85d34d9a`.
- Đã kiểm bằng mock/vector; chưa xác nhận luồng PostgreSQL hoặc màn chạy thử.

## Chưa phát hành — MASK-3E (07/11/2026)

- Nối việc che/mở che từ tham chiếu qua kho Core, đồng bộ nhật ký và bí danh dùng chung; mất xác nhận gửi lại cùng kết quả tối đa ba lượt. Commit: `9cab6bdb`, `3e14874b`, `d3a058a9`.
- Engine không truy cập CSDL trực tiếp; kiểm adapter bằng mock/vector chưa chứng minh đối soát mất xác nhận phía Core đã có.

## Chưa phát hành — MASK-3C (07/11/2026)

- Ghi nhận gặp lại cụm chưa có bí danh chính thức, chống đếm lặp theo mã yêu cầu và cụm chuẩn hóa; có khóa và rollback trong kho bộ nhớ. Commit: `03d5971a`.
- Kho bộ nhớ chỉ dùng DEMO/test; kết quả này chưa xác nhận tính nguyên tử phía PostgreSQL.

## Chưa phát hành — MASK-3A (07/11/2026)

- Che/mở che văn bản, chặn gửi khi còn sót định danh, giữ tiền/ngày; bổ sung dò trường có nhãn, bí danh hỏng và xử lý chuỗi dài. Commit: `e5f61260`, `c724b141`, `c301cf40`, `4a7de561`, `00c0c399`.
- Tối đa 500.000 ký tự; bí danh chưa mở giữ yêu cầu đang xử lý, tài nguyên detector sạch và luồng thực còn chờ kiểm.

## Chưa phát hành — MASK-2 (07/11/2026)

- Thêm kho định danh–bí danh và danh sách chờ, quyền/rào DEMO; công cụ chuyển danh mục có chạy thử, chỉ báo số đếm, chuẩn hóa chữ Việt và khoảng trắng. Commit: `c8ef19c1`, `5a1f007d`.
- Quyền và rào dữ liệu cần lead kiểm PostgreSQL; chưa tuyên bố nghiệm thu kho thật từ test thuần/mock.

## Chưa phát hành — MASK-1 (07/11/2026)

- Đưa 11 module lõi Mask v2 vào gói, tách OCR và giữ che Word/Excel; ghi nguồn, SHA và kiểm kê phụ thuộc, thay ví dụ chưa xác minh bằng số giả. Commit: `4f9e8f22`.
- Không mang cấu hình/dữ liệu nguồn; còn thiếu tài nguyên dò định danh sạch và lệch phiên bản phụ thuộc, không nâng thư viện hoặc đổi SDK.

## Chưa phát hành — G3-GOI-30 (06/11/2026, chỉ tài liệu theo CD-086)

- Bổ sung nguồn Mask file v2, giới hạn bằng chứng version/SHA và tình trạng chưa có giấy phép phân phối ghi nhận.
- Thêm `nguon/PHU-THUOC.md`: phụ thuộc thực dùng của khung, thư viện tiến trình nguồn theo khảo sát repo; phân biệt cryptography Mask 50.0.1 với Core 49.0.0 và đề xuất tách môi trường.
- Ghi hai phương án bundle nguồn sạch/cài riêng được ghim: chờ Anh chọn; làm rõ `sys.executable` và helper `env_con` vẫn là điểm lead cần xử lý trước nghiệm thu độc lập.
- Cập nhật README theo import hiện tại sau lát 29. Giữ Mask **Chờ**, không tạo lock/manifest/capability, không đổi version SDK hoặc ghim wheel 1.4.1 candidate.

## 0.1.0-demo.1 (G3-GOI-27, 05/11/2026)
- Chuyển nguyên trạng `chay.py`, `vong_doi.py`, `contract/du_thao.json` từ `src/kho_tri_thuc/engines/e_mask/` sang `engines/e_mask/` (git mv, không đổi nội dung).
- Thêm shim namespace tại đường cũ, `__init__.py` marker, tài liệu và test độc lập.
- Không tạo `engine.json`, `contract/schemas.json`, `contract/vi_du.json`.
