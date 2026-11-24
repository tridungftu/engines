## 0.13.0 — 24/11/2026 — AI-13 (PR: chờ lead mở)

- Thêm `ai.hoi_theo_prompt@1`: prompt của module nguyên văn, nối tài liệu bằng một dòng trống, một message user, không system prompt hay khung của engine. Phong bì yeu_cau_ai được ưu tiên; cảnh báo riêng khi tham số bước bị bỏ qua.
- Trả câu trả lời nguyên văn, JSON đã kiểm schema, model/lý do chọn; nội dung gửi chỉ trả khi bật công tắc. Khuôn gửi qua API, không bọc hoặc chép vào prompt; sai khuôn gửi lại cùng yêu cầu tối đa một lần. Giữ ngân sách context AI-9, kiểm hủy và phân loại lỗi Local/ChuaRo; nhật ký không có nội dung.
- Giữ nguyên ba năng lực cũ; tên hai năng lực hỏi–đáp ghi rõ khung trích dẫn để tương thích. Thêm hai DEMO, cập nhật quyết định, README/NGUON/băm/kiểm kê; không thêm thư viện hay đổi khoảng SDK. Cloud qua Mask: lát sau, do quy trình Core nối Mask → Hỏi AI → Mask.
- Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; CLI chuẩn còn nợ cấu hình DEMO từ AI-11. Chưa kiểm Core/model thật; chi tiết kết quả tại VIEC.md.

## 0.12.1 — 22/11/2026

- UI-AI-1, UI-AI-2: màn Máy AI và màn Cổng Cloud AI (Tạm khóa). Theo `_chung/docs/GIAO-CODEX-UI-CAU-HINH.md`; không đổi xử lý việc. Màn chờ Core mở cửa D/D2/E/F mới hiện trong Core.

## UI-AI-2 — 22/11/2026 (PR: chờ lead mở; giữ manifest 0.12.0)

- Thêm màn Cổng Cloud AI theo ảnh mẫu, luôn Tạm khóa: nhà cung cấp/model/tỷ lệ kiểm/nút kiểm Cloud bị khóa; không có đường bật/gọi Cloud hoặc thao tác Python mới.
- Két Core dự kiến: đọc metadata, nhập key kiểu mật khẩu, lưu/xóa với CAS riêng tăng đơn điệu; chỉ hiện bốn ký tự cuối, không hiện lại bản rõ. Xóa ô nhập ngay khi gửi; lỗi ghi/mất phản hồi khóa ghi tới khi tải lại. Thiếu cổng Core thì khóa két.
- Nhật ký gửi ra ngoài báo rõ chờ cửa Core; không dựng lịch sử rỗng giả. Khai dự kiến D/F tại KHAI-SDK-2.1.json, không đổi engine.json hoặc schema xử lý việc. Schema hiện có đã đủ title/description/examples mọi cấp, có kiểm hồi quy.
- Test Node không mạng tích hợp pytest; ảnh Chrome DEMO rộng/hẹp/lỗi/CAS. Đã kiểm bằng Core giả (CoreGia), chưa nối Core/Cloud thật; CLI SDK độc lập vẫn có nợ cấu hình DEMO từ AI-11.

## UI-AI-1 — 21/11/2026 (PR: chờ lead mở; giữ manifest 0.12.0)

- Màn Máy AI theo ảnh mẫu: IP/cổng, trạng thái kiểm, nút kiểm/tìm/cập nhật model; bảng sửa và sắp quy tắc/model dự phòng, Nâng cao, lưu CAS và tải lại khi tranh chấp. Không thêm tùy chọn làm đổi xử lý việc; Cloud giữ trạng thái cũ.
- Thêm ba hàm quản trị Python độc lập dùng discovery/bảo vệ mạng hiện có; chỉ GET metadata, cập nhật catalog trong Core. Tự tìm tối đa 16 địa chỉ đã biết, không quét subnet, không ghi catalog khi chưa chọn máy. Khai D/E dự kiến tại KHAI-SDK-2.1.json; chưa đăng ký vào manifest/SDK.
- Schema có nhãn, diễn giải và mẫu tiếng Việt ở mọi cấp; URL chỉ HTTP khớp runtime. Kiểm bằng Node/KttCore giả, CoreGia + Local HTTP giả; ảnh DEMO rộng/hẹp/lỗi kèm tài liệu. Đã kiểm bằng Core giả (CoreGia); CLI chuẩn vẫn có nợ cửa cấu hình DEMO/Local giả từ AI-11.

## 0.12.0 — 15/11/2026 — AI-12 (PR: chờ lead mở)

- Tương thích nguyên khuôn bốn tác vụ Tra cứu và DC-6: metadata/phân loại/nhãn/điểm/cờ kiểm theo schema; giá trị trích vẫn kiểm bằng chứng, câu trích đúng offset, tiền cùng số và mã tiền. Không import/gọi engine khác.
- Đề xuất annotation `$comment` tùy chọn tại sổ loại chung §8; adapter nội bộ trên bản sao schema cho producer chưa có annotation. Khuôn khác giữ kiểm bảo thủ; không tự miễn mọi enum/const.
- Câu tổng hợp được diễn đạt lại nhưng không bịa số; giữ từng vị trí trích lặp. Chuyển tiếp/băm/khuôn gửi Local không đổi; Cloud vẫn tắt. Thêm fixture DEMO độc lập TC/DC và các ca âm; đã kiểm bằng Core giả (CoreGia), chưa kiểm Core/model thật. CLI SDK vẫn thiếu cửa cấu hình DEMO/Local giả đã ghi AI-11.

## 0.11.0 — 15/11/2026 — AI-11

- Chuyển SDK 2.2.0: cấu hình snapshot của việc, ngăn SDK trực tiếp, bỏ fallback RAM và bảng cấu hình; hook làm mới đệm khi đổi cấu hình.
- Khai catalog/cấu hình/migration trong engine.json; SQL tạo bảng riêng, kiểm kê toàn gói; api lưu JSON dạng văn bản, thứ tự model đọc số.
- Chuyển nguyên bản cổng tạm/bản khai 2.1 vào LUU-TRU/AI-11 ngoài gói; giữ ca hành vi, đổi môi trường sang CoreGia 2.2.0.
- CLI SDK thu chưa có cửa cấp cấu hình DEMO/Local giả: chưa đạt nghiệm thu AI-11; hồi quy API chính thức chỉ là bằng chứng bổ sung, đã kiểm bằng Core giả (CoreGia).

## AI-10 — 15/11/2026 (PR: chờ lead mở)

- Phân loại lỗi transport và phản hồi Local sau khi bắt đầu POST là `ChuaRo`; lỗi kết nối chắc chắn trước gửi vẫn cho thử lại. Áp dụng chung cho ba năng lực, Cloud vẫn tắt.
- Kiểm bằng server socket thô và Core giả (CoreGia); chi tiết tại `e_hoi_ai/docs/VIEC.md`.

## 0.5.0 — AI-9 — 15/11/2026 (PR: chờ lead mở)

- Thêm `ai.hoi_mask_cuc_bo@1`, kiểm profile Local đã duyệt, băm prompt/khuôn/đoạn và span nguyên văn Unicode; giữ từng lần tên lặp, nhận rỗng đúng khuôn, không tạo thực thể giả.
- Tái dùng bộ kiểm schema, chọn model/ngăn và provider trong gói; giữ nguyên `_kiem_tra_loi` hỏi–đáp cũ. Không import/gọi Mask hoặc engine khác, không thêm dependency hay lưu runtime xuống đĩa.
- POST Local theo dõi giai đoạn gửi: connect lỗi trước gửi được thử lại; mất phản hồi/timeout sau gửi hoặc 202 truyền nguyên `ChuaRo`, không retry/fallback. Kiểm hoàn tất cả hai API cho mọi handler; giữ trần JSON/byte/độ sâu và bảo vệ mạng cũ.
- AI-9 kiểm budget body/context/đầu ra; thiếu metadata context thì từ chối. Thêm fixture Local HTTP + CoreGia, kiểm hủy/mất lease, Cloud 0 lượt, và hồi quy hỏi–đáp/công cụ AI-7. Giữ ba DEMO manifest; bộ chạy test có thêm ca AI-9 với snapshot RAM thật.
- Đã kiểm bằng Core giả (CoreGia); kết quả thật và giới hạn CLI ghi trong `e_hoi_ai/docs/VIEC.md`. Chưa đo model/Core thật, chưa đo mục tiêu 0 lọt hoặc bật Cloud. Lead commit/mở PR; không commit/push trong lát.

## AI-8 — 15/11/2026 (chờ lead mở PR)

- Cấu hình Local/quy tắc model đọc từ ngăn; thiếu trả CHUA_CAU_HINH. Ngừng dùng cau_hinh_may.py, giữ nguyên tệp để chuyển LUU-TRU.
- Đã nối ngăn chung NGAN-0 (PR #34); giữ nguyên hai tệp mẫu và bật test so băm chuẩn LF. Khởi tạo RAM từ khai báo bảng trong KHAI-SDK-2.1.json, dùng TrangNgan/KetQuaLenh và cho_phap_nhan đúng API chung.
- Chuyển NganXungDot/NganKhongHopLe/CauHinhKhongHopLe thành lỗi nghiệp vụ tại biên SDK; giữ thử lại CAS model có giới hạn. Kiểm thêm catalog phân trang trên 500 model và khởi động gói độc lập.
- Model phát hiện ghi/đọc qua ngăn theo id_model; giữ cache RAM 5 phút và kiểm metadata trước khi gửi nội dung.
- Màn Cổng Local AI/Cổng Cloud AI dùng KttCore giả để kiểm lưu và CAS. Cloud tắt; manifest 2.0 giữ nguyên, khai dự kiến ở KHAI-SDK-2.1.json.
- Cổng DEMO nạp cấu hình RAM, không tạo tệp cấu hình. Đã kiểm bằng Core giả (CoreGia); xem VIEC.md cho kết quả cuối.

# Thay đổi

## AI-4 — 14/11/2026 — DEMO và kiểm khởi động (trên gói 0.4.0)

- Mở rộng `chay_thu_demo` thành ba ca DEMO: tiền/ngày có căn cứ, câu không có đáp án, yêu cầu có khuôn tiền kèm VND/ngày ISO.
- Bộ chạy Local giả gọi trực tiếp `CoreGia().chay_thu_demo(app)`; cấu hình tạm nằm dưới `tests/`. Đây là cổng đạt thay lệnh SDK thu riêng cần máy AI.
- Thêm kiểm đáp án và cổng lỗi/rỗng; chạy tiến trình thật nhận stdin qua `MayChuGia` HTTP loopback cho cả hai năng lực, xác thực và nộp kết quả trước kết thúc; 0 lượt Cloud.
- Đã kiểm bằng Core giả (CoreGia); kết quả kiểm AI-4 ghi ở `e_hoi_ai/docs/VIEC.md`. Không sửa lõi Local/Cloud hoặc hợp đồng SDK/API.

## 0.4.0 — 14/11/2026 — Gộp AI-2 và AI-3

- Giữ phát hiện/chọn model, cache, lý do chọn và bảo vệ mạng AI-3 cùng toàn bộ xử lý khuôn AI-2.
- `_kiem_model` trả loại API từ catalog đã kiểm khả dụng; không thêm GET để chọn cách gửi khuôn.
- Luồng hỏi theo yêu cầu truyền kiểm hủy vào bộ chọn model trước khi gọi mạng.
- Hợp nhất tài liệu hai lát, cập nhật SHA-256; kết quả kiểm việc gộp ghi trong `e_hoi_ai/docs/VIEC.md`.

## 0.3.0 — 14/11/2026 — AI-2

- Nối `ai.hoi_theo_yeu_cau@1`: nhận `yeu_cau_ai`, trả đủ phong bì `tra_loi_ai`, nguồn gốc và vị trí trích dẫn.
- Truyền khuôn phản hồi chứa `du_lieu` và trích dẫn qua Ollama `/api/chat` (`format`) hoặc OpenAI-compatible (`response_format.json_schema`).
- Kiểm tập con JSON Schema 2020-12 offline bằng thư viện chuẩn, từ chối từ khóa chưa hỗ trợ; sai khuôn chỉ hỏi lại một lần rồi trả `AI_TRA_SAI_KHUON`.
- Giữ nguyên `chuyen_tiep` theo byte JSON chuẩn hóa, không gửi Local; từ chối vượt trần 64 KiB/32 KiB trước mạng.
- Giữ hậu kiểm trích dẫn AI-1, bổ sung đối chiếu dữ liệu có kiểu; kiểm lỗi Local, hủy và chống nộp trùng với 0 lượt Cloud.
- Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; kết quả kiểm cuối ghi trong `e_hoi_ai/docs/VIEC.md` của repo. Chưa kiểm Core thật hoặc model thật.

## 0.3.0 — 14/11/2026 — AI-3

- Thêm mô-đun `chon_model.py`: phát hiện Ollama, LM Studio native v1/v0, OpenAI-compatible từ API; giữ ID và thứ tự nguồn, không xếp hạng model.
- Catalog trong bộ nhớ 300 giây; kiểm khả dụng mới mỗi lượt và trước POST, không dùng model đã biến mất hoặc metadata chỉ rõ từ xa/chưa tải/không phải LLM.
- Chọn theo tham số ưu tiên, quy tắc prompt và dự phòng có thứ tự, rồi model khả dụng đầu tiên; không có model trả lỗi có thể thử lại.
- Thêm trường `ly_do_chon_model` vào kết quả hỏi tài liệu và phiếu gói. Không thay SDK/API/Core; giữ điểm nối để AI-2 dùng chung.
- Đã kiểm bằng Core giả (CoreGia): SDK thu 1/1 ĐẠT; pytest 176 passed, 0 skipped; kiểm độc lập mã 0; Cloud 0 lượt. Chưa kiểm Linux/Core thật/model thật.

## 0.2.0 — 14/11/2026 — AI-1

- Chuyển lõi Local, DTO và adapter từ mã cũ; nối `ai.hoi_tai_lieu@1` qua SDK 2.0.
- Giữ chặn DNS/proxy/redirect, chỉ dùng IP loopback/LAN/Tailscale và kiểm model trước khi gửi tài liệu.
- Kiểm trích dẫn nguyên văn, giá trị thuộc trích dẫn và số liệu thuộc nguồn; hạ kết quả sai kèm cảnh báo.
- Prompt thiếu/rỗng trả `THIEU_PROMPT`; Local lỗi trả `LOCAL_AI_KHONG_SAN_SANG` có thể thử lại; 0 lượt Cloud.
- Thêm tiến độ, kiểm hủy, nhật ký metadata ra stderr và DEMO tối thiểu qua HTTP Local giả.
- Đã kiểm bằng Core giả (CoreGia): SDK thu 1/1 ĐẠT; pytest 141 passed, 0 skipped; kiểm độc lập mã 0. Chưa chạy thực tế trên Linux, Core thật hoặc model thật.

## 0.1.0 — 14/11/2026 — AI-0

- Dựng khung SDK 2.0.0 với hai năng lực tạm trả `CHUA_LAM`.
- Thêm ba contract dữ liệu dùng chung và schema cấu hình máy.
- Đọc JSON ngoài gói, cho phép khởi động khi thiếu cấu hình.
- Đã kiểm bằng Core giả (CoreGia); chưa có DEMO hỏi AI thành công (AI-4).
## AI-6 — 14/11/2026 (khung, giữ nguyên manifest 0.4.0)

- Tách provider Local sang `nha_cung_cap.py`; giữ import tương thích tại `cong_ai.py`. Thêm provider Cloud Anthropic/OpenAI nhận khóa qua constructor, không đọc env/tệp/đĩa.
- Thêm `cloud.hoi_cloud` chỉ nhận phong bì đã che, fail-closed khi còn sót hoặc chưa kiểm tiền/ngày; giữ mã mở che trong kết quả nội bộ. Cloud bị khóa cứng `BAT_CLOUD = False` ở cả hàm và provider.
- Không sửa `engine.json`, không đăng ký năng lực Cloud. Mọi kiểm Cloud bằng giả trong RAM; hai năng lực bản 1 được chặn cả khởi tạo/gọi provider Cloud. Đã kiểm bằng Core giả (CoreGia).
