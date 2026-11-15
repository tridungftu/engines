# Thay đổi

## Chưa phát hành — 15/11/2026, TX-6

- Thêm ngoài runtime: công cụ T3 DEMO-1/20/60 × ba ID model, N1 một lần,
  hai `.cmd` ASCII, cổng kiểm venv mới offline Windows/Linux, mẫu nền/biên
  bản và checklist 17:00. Mặc định chạy khô Local giả, 0 mạng/Cloud;
  không chạy `--that`, T3/N1 thật chưa đo/chưa kiểm.
- Kiểm CoreGia hai chuỗi, schema/metadata/snapshot/tệp/tiền/ngày; Node
  KttCore giả; MayChuGia loopback cho tiến trình đọc stdin, hủy/mất ACK.
  Không chứng nhận quyền/TTL/lưu-đóng/ACK của Core thật.
- Ghi riêng C-TX-04/C-TX-06: CLI SDK chuẩn còn 3/5 ĐẠT, exit 1; cổng có
  ngăn/hồ sơ 5/5. Kiểm nguồn E6 gặp CRLF do checkout được báo riêng,
  không đổi tiêu chí/băm nguồn. Kết quả thật tại `../../docs/TX-6-KET-QUA.md`.
- Runtime/manifest/schema/ngăn chung không đổi; giữ lock SDK 2.0.0,
  không dependency runtime mới, không chuyển bộ mặc định/lưu trữ,
  không commit/push. **đã kiểm bằng Core giả (CoreGia)**.

## 0.4.0 — 15/11/2026, TX-3b

- Đăng ký `trich.hau_kiem@1` và `trich.xuat_ket_qua@1` bằng handlers lõi
  TX-3 sẵn có; đầu cuối trả `truong` tĩnh đủ JSON/Excel và ba trường tổng hợp.
- Tạo schema `bang_trich_xuat` theo §4 và bổ sung TX-3-REVIEW đã duyệt;
  chép vào contract của gói, test SHA LF. Offset Unicode, cờ kiểu chưa
  chuyển, dấu `dau_kiem_tam_e6` và `phan_hoi_ai` chỉ kiểm toán ghi rõ.
- Hai DEMO thật trong manifest, kèm bytes hồ sơ trong gói; bỏ phiếu/handlers
  giả trong test. Helper kiểm nạp tệp qua API công khai CoreGia, chỉ đổi
  tham chiếu/băm request, không tự cấu hình engine.
- **đã kiểm bằng Core giả (CoreGia)**: pytest **408 passed, 0 skipped**,
  DEMO có ngăn **5/5 ĐẠT**, kiểm độc lập **ĐẠT**. CLI chuẩn **3/5 ĐẠT,
  exit 1**: `CHUA_CAU_HINH` (C-TX-04) và hậu kiểm thiếu tệp tham chiếu
  (`DANG_CHAY`, C-TX-06). Chưa đạt cổng CLI chung; không nhận E6/N1/Core thật.
- Giữ nguyên nguồn cũ, mẫu ngăn/cấu hình, hai công cụ E6 đang làm TX-4b;
  không thêm dependency, không sửa SDK/Core hoặc bốn schema chung trước đó.


## Chưa phát hành — 15/11/2026, TX-4 chưa kiểm E6 nghiệm thu

- Thêm công cụ/wrapper/test E6 ngoài gói runtime; XLSX thật khớp SHA ghim,
  E1 giữ đúng 37 mã/thứ tự/10 cột nguyên văn, ghi riêng ba băm.
- So bytes bộ/câu hỏi/toàn bộ dòng bảng/phản hồi, báo offset/độ dài/băm;
  chặn nguồn thiếu/sai băm và bản vàng thiếu/chưa được lead chấp nhận.
- Hai DEMO kỹ thuật gồm Track Changes: bộ/văn bản trùng nhưng câu hỏi,
  bảng, phản hồi khác byte; **chưa đạt chẩn đoán**, **chưa kiểm E6 nghiệm thu**.
  Không chuyển bộ/lưu trữ hoặc thay đổi runtime để fallback XD.
- **đã kiểm bằng Core giả (CoreGia)**; 375 test passed, 0 skipped; CLI
  2/3 ĐẠT (C-TX-04), DEMO có ngăn 5/5 ĐẠT. N1/Core thật chưa kiểm.

## Chưa phát hành — 15/11/2026, TX-3 chờ review

- Sửa kiểm độc lập: giá trị phải khớp trọn token/cụm, không cắt số qua dấu
  phân cách/khoảng trắng; strip hai phía như nhau, giữ nguyên văn AI riêng.
- `so_tien.so` chỉ int/chuỗi thập phân chính xác, từ chối float/bool.
- Đóng nợ TX-2: hồ sơ/tài liệu nguồn ≤20 MiB UTF-8; trang ≤2.000/8 MiB,
  cảnh báo ≤200/64 KiB; kiểm trước sao chép/tải, không cắt ngầm. Bỏ bản chép
  toàn văn trong request của hồ sơ, vẫn kiểm băm/đọc được hồ sơ TX-2 cũ.
- Payload đề xuất thêm `don_vi_offset="unicode"`, `kieu_da_chuyen=false`;
  đổi dấu cũ thành `dau_kiem_tam_e6`. `phan_hoi_ai` chỉ kiểm toán, có thể lộ
  nội dung, module không hiển thị mặc định. Không đăng ký năng lực/schema mới.
- Thêm regression test token, typed money round trip, trần byte/số phần tử,
  hồ sơ gọn/cũ và prompt injection; ghi phối hợp AI-2 bao/thoát nội dung.

- Lõi hậu kiểm từng ô và xuất JSON/Excel theo đề xuất; chưa đăng ký runtime/schema.
- Kiểm snapshot/offset/logic theo loại, giữ dấu legacy và nguyên văn AI riêng; không tự chuyển kiểu hoặc tính TT-21.
- Hai tệp trong RAM, text không thành công thức, kiểm trần trước escape, không cắt; hủy/lỗi/mất ACK không nộp thiếu/trùng.
- Hai DEMO đề xuất chỉ đăng ký trong phiếu RAM của test; cổng có ngăn **5/5 ĐẠT**, CLI chuẩn vẫn **2/3 ĐẠT, exit 1, CHUA_CAU_HINH** (C-TX-04).
- **đã kiểm bằng Core giả (CoreGia)**; chờ lead/Anh review tại **../../docs/TX-3-REVIEW.md**. Linux/Core thật/E6/N1 chưa kiểm; không đổi nguồn cũ/Core/SDK/dependency.

## 0.3.0 — 15/11/2026, TX-2

- Thêm `trich.chuan_bi@1`: nhận snapshot theo việc, SHA-256 đúng bytes UTF-8
  trước parse; JSON nghiêm, kiểm đủ 10 cột/quy tắc qua E1 SDK, giữ dòng ngừng
  dùng/thứ tự; không tra bộ hoặc mặc định XD.
- Danh sách con giữ thứ tự, rỗng lấy mọi mã đang dùng; chỉ nhận hỏi thêm `[]`.
  Prompt bắt buộc của module; một request v1 đủ mã, khuôn 2020-12 `$defs`,
  nguyên văn và offset Unicode, không đổi loại chung thành batch.
- Chặn snapshot 64 KiB/200 dòng đang dùng, prompt 20.000 ký tự, toàn văn
  500.000 ký tự, khuôn 32 KiB; ngân sách mặc định 16.000 không vượt trần
  cấu hình ngăn, giữ phiên bản. Không cắt ngầm; token vẫn chỉ là ước lượng.
- Hồ sơ JSON trong RAM tải lên Core, gồm snapshot/vị trí/yêu cầu/cấu hình
  đã ghim; chuyển tiếp gọn chỉ metadata/tham chiếu/băm, trần 64 KiB.
- Sửa lọc log TX-1: chỉ che nội dung lỗi việc/traceback, giữ mã lỗi SDK;
  chặn khởi động khi SDK khác 2.0.0 hoặc chữ ký hai hook thay đổi.
- Thêm schema chung nguyên byte, DEMO TX-2, cổng DEMO có NganBoNho;
  **đã kiểm bằng Core giả (CoreGia)**: pytest **164 passed, 0 skipped**,
  độc lập **exit 0**, DEMO có ngăn **3/3 ĐẠT**. CLI SDK chuẩn **2/3 ĐẠT,
  exit 1**, TX-2 `CHUA_CAU_HINH`; ghi C-TX-04, không tự tạo cấu hình.
- Đóng nợ mô tả DOCX từ chối cả tài liệu với vMerge continue có chữ,
  dòng không ô hoặc lệch gridSpan; trần tỷ lệ giải nén **200:1**.
- Chưa kiểm Linux/Core thật, ACL/vòng đời tệp hoặc context model thật;
  giữ C-TX-01/02/04 và A-TX-01. Không sửa Core/SDK/nguồn cũ; **0 Cloud**.

## 0.2.0 — 15/11/2026, TX-1

- Đã nối ngăn chung NGAN-0 (PR #34), giữ nguyên `ngan.py`/`cau_hinh.py`;
  hai test so SHA-256 chuẩn hóa CRLF→LF chạy bắt buộc, không skip.
- RAM nhận khai báo bảng từ `KHAI-SDK-2.1.json/ngan_du_lieu`; cấu hình dùng
  khóa `{}`, dict trực tiếp, giữ snapshot và phiên bản từ cùng một lần đọc.
  Đổi ngoại lệ ngăn/cấu hình chung thành `LoiNghiepVu`, giữ cờ thử lại.
- Test dùng `KetQuaLenh`/`TrangNgan`, phạm vi pháp nhân trong khóa/bộ lọc
  hoặc view; kiểm schema DOCX bằng jsonschema có sẵn của SDK, chỉ trong test.
- Tạo gói SDK 2.0 độc lập, chỉ công bố `trich.doc_docx@1` và hai DOCX DEMO.
- Chuyển lõi Accept All/Numbering sang bytes trong RAM; giữ thứ tự khối,
  ô rỗng/gộp, vị trí Unicode, băm gốc; không tạo trang/hộp giả.
- Chặn vượt giới hạn tệp/ZIP/XML/nội dung, lỗi tiếng Việt, hỗ trợ hủy.
- Cổng ngăn RAM tạm có lô nguyên tử/CAS/duy nhất/pháp nhân; cấu hình chỉ
  qua ngăn, seam giữ snapshot; còn chờ API SDK 2.1 thật.
- Màn cấu hình qua KttCore, khai SDK 2.1 riêng, kiểm bằng Node/KttCore giả.
- Phạm vi kiểm: **đã kiểm bằng Core giả (CoreGia)** trên Windows;
  chưa chạy Linux hoặc nối Core thật. Không AI/OCR thật, 0 Cloud.

## TX-5 — 15/11/2026

Bàn giao ngoài runtime helper chuyển E1 thành snapshot cùng hướng dẫn U1a/U1b cho module; không thay engine runtime hoặc đăng ký năng lực. Kiểm chi tiết và giới hạn CLI/Core tại `docs/VIEC.md`.
