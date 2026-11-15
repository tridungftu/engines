# VIỆC — danh sách việc duy nhất của project `e_tra_cuu`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| TC-7 | Soạn/kiểm chứng Python và Local, nhãn TC-Q14, mâu thuẫn và phụ thuộc nguồn | Lead giao 15/11/2026, 15:16; sau TC-4/6, 5 giờ ƯỚC TÍNH | Chờ Core — 15/11/2026 | Đúng 4 tệp runtime; 952 passed (138 ca TC-7), 0 skipped; độc lập mã 0, harness 36/36. CLI chuẩn 0/5 CHUA_CAU_HINH/mã 1. Đã kiểm bằng Core giả (CoreGia)/NganBoNho/Local giả theo protocol; 0 Cloud/model thật. Consumer Hỏi AI hiện có với Local giả từ chối khuôn, TC-7 giữ không căn cứ. TC-Q14 đã duyệt, không hỏi lại. PR: **chờ lead mở**; xem biên bản TC-7 và Cần Core dưới. |
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | TC-0: khảo sát pgvector/unaccent/pg_trgm trên PostgreSQL; chọn và đo model vector | — | Chờ làm | Chỉ đọc, DEMO |
| 2 | TC-2 (phần engine): `phan_loai_tai_lieu@1`, `cat_doan@1` | §1.2 | Chờ làm |  |
| 3 | TC-3/TC-4 (phần engine): `phan_tich_cau_hoi@1`, `xep_hang_lai@1`, `soan_tra_loi@1` | §1.2 | Chờ làm |  |
| 4 | Bộ câu hỏi mẫu nhóm 02 và bài đo chất lượng | §1.3 | Chờ làm |  |
| 5 | Kho tài liệu, `loi_tra_cuu`, quy trình nạp/hỏi | TC-1 | Chờ Core |  |
| 6 | 9 câu trả lời sau (đặc tả §15) | — | Chờ Anh |  |
| TC-P | Lập phiếu giao Codex theo SDK 2.0, chỉ tài liệu | Anh giao 15/11/2026; QĐ 15/11 câu 12 | Xong — 15/11/2026 | `GIAO-CODEX-e_tra_cuu.md`: 12 lát TC-0…TC-11, 45 giờ công ƯỚC TÍNH; TC-P 1 giờ ƯỚC TÍNH ngoài tổng; đề xuất loại `ho_so_tra_cuu` ở cuối tài liệu loại chung; PR: **chờ lead mở** |
| TC-0 | Khung SDK 2.0 + Ngan/cấu hình + kiểm độc lập | Lead giao 15/11/2026, 12:17; phiếu TC-0 §4 | Chờ Core — 15/11/2026 | Đã làm đủ phạm vi 5 tệp mã; pytest/độc lập đạt. CLI SDK 2.0 trả 1 vì 0 demo, chưa đạt cổng chung; xem biên bản dưới. PR: **chờ lead mở** |
| TC-1 | Contract hồ sơ và chỗ nối dữ liệu | Lead giao 15/11/2026, 12:36; TC-Q13 đã duyệt chiều 15/11 | Chờ Core — 15/11/2026 | Hoàn thành schema/tài liệu/test trong phạm vi TC-1; 192 passed, độc lập mã 0, CLI mã 1 vì 0 demo. Giữ khung đến TC-2 theo lệnh mới nhất; chưa đạt cổng chung/nghiệp vụ. PR: **chờ lead mở** |
| TC-2 | Nhận JSON, kiểm nguồn/quyền/phạm vi, ghim cấu hình và snapshot Core | Lead giao 15/11/2026, 12:51; phiếu TC-2 §4 | Chờ Core — 15/11/2026 | Đã làm đúng 3 tệp mã; 315 passed, 0 skipped; độc lập mã 0; harness 5/5 ĐẠT. CLI SDK gốc 0/5 ĐẠT, mã 1 do CHUA_CAU_HINH. Đã kiểm bằng Core giả (CoreGia), chưa chứng nhận quyền Core thật. PR: **chờ lead mở** |
| TC-3 | Cắt Điều/Khoản/bảng, giữ nguyên nguồn/offset/vị trí; đóng ba nợ TC-2 | Lead giao 15/11/2026, 13:33; phiếu TC-3 §4 | Chờ Core — 15/11/2026 | Đã làm 3 tệp TC-3 + kiem_dau_vao.py cho nợ TC-2 (4 tệp mã); 457 passed, 0 skipped; độc lập mã 0; harness 9/9 ĐẠT. CLI SDK chuẩn 0/5, mã 1 do CHUA_CAU_HINH. Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật. PR: **chờ lead mở** |
| TC-4 | Chuẩn bị bốn tác vụ Local AI, snapshot/map/khuôn/chuyển tiếp/ngân sách | Lead giao 15/11/2026, 14:11; phiếu TC-4 §4 | Chờ Core — 15/11/2026 | Đã làm đúng 3 tệp mã; 548 passed, 0 skipped; độc lập mã 0, harness 13/13 ĐẠT. CLI chuẩn 0/5 do CHUA_CAU_HINH/mã 1; còn giới hạn SDK chặn tham số trước handler. Đã kiểm bằng Core giả (CoreGia), consumer AI-2/Local giả trong tests, 0 Cloud. PR: **chờ lead mở** |
| TC-5 | Hậu kiểm Local, phân loại tám nhóm/ranh giới và hàng chờ có lý do | Lead giao 15/11/2026, 14:34; phiếu TC-5 §4 | Chờ Core — 15/11/2026 | Đúng 3 tệp runtime; 674 passed (126 TC-5), 0 skipped; độc lập mã 0, harness 24/24 ĐẠT. CLI chuẩn 0/5 CHUA_CAU_HINH/mã 1. Đã kiểm bằng Core giả (CoreGia); giới hạn kiểm metadata của AI-2 giữ kết quả ở hàng chờ, chưa nghiệm thu pipeline/model thật. PR: **chờ lead mở** |

| TC-6 | Hậu kiểm câu hỏi/hàm/ý định/thực thể và xếp hạng Local | Lead giao 15/11/2026, 14:34; sau TC-4, 4 giờ ƯỚC TÍNH | Chờ Core — 15/11/2026 | Đã làm đúng 3 tệp mã; 688 passed, 0 skipped; độc lập mã 0, harness 17/17. CLI chuẩn 0/5 CHUA_CAU_HINH/mã 1. Đã kiểm bằng Core giả (CoreGia), Local giả theo protocol, 0 model/provider thật; chưa chứng nhận RLS. PR: **chờ lead mở** Sau gộp TC-5 ngày 15/11/2026: 814 passed, 0 skipped; harness 28/28; độc lập mã 0; CLI vẫn 0/5 CHUA_CAU_HINH/mã 1; xem biên bản việc gộp dưới đây. |

**Phạm vi sau TC-P (15/11/2026):** các mã TC ở dòng 1–5 của bảng cũ là mã lịch sử từ DAC-TA §14, không phải lát code mới. Dùng bảng §3 của `GIAO-CODEX-e_tra_cuu.md` làm phiếu giao mới: TC-0 = khung SDK 2.0 + Ngan/cấu hình + kiem_doc_lap + KHAI-SDK-2.1; khảo sát PostgreSQL/kho/cache/SDK JS/nạp hàng loạt vẫn thuộc Core. Tại thời điểm TC-P chưa giao hoặc làm TC-0…TC-11; cập nhật TC-0 ở dưới. Tại TC-P không có `ma-nguon/`, `goi/`, `tests/`, quyết định cuối/phiếu riêng trong worktree; không tạo chúng ở TC-P. TC-0 đã tạo goi/tests, tiếp tục không tạo ma-nguon.

**Quyết định cập nhật 15/11 chiều:** TC-Q13 đã duyệt loại `ho_so_tra_cuu`, mở
TC-1; TC-Q01…15 theo cột đề xuất, trừ TC-Q06 tiếp tục **không tự xóa**.
TC-Q14 đã chốt Xanh chỉ Python tầng 1 đủ điều kiện, mọi câu LLM soạn tối đa Vàng.
TC-Q09 là duyệt cách rà nghiệp vụ trước khi chốt danh mục chi tiết, không mặc
nhiên duyệt mọi loại hoặc bật nhựa/điện. Bảng chọn duy nhất tại phiếu §5.2 vẫn
là nơi theo dõi; các dòng “chưa duyệt” trong biên bản TC-P/TC-0 dưới đây là lịch sử.

**Kiểm TC-P:** theo ngoại lệ riêng của lát chỉ tài liệu, không áp dụng ba lệnh engine AGENTS.md §5 khi chưa có gói/tests. Kiểm 12/12 khối lệnh §4 bằng regex Anh yêu cầu (fence mở ``` trơn), đủ TC-0…TC-11, không trùng, tổng giờ bảng = 45; `git diff --check` không lỗi. SDK 2.0.0 cài offline trong `.venv`, SHA-256 wheel khớp SHA256SUMS.txt. Chỉ kiểm tài liệu và đọc mã SDK, **chưa chạy engine/CoreGia**. Không commit/push; không tạo `goi/`, không sửa nguồn cũ.

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Bổ sung từ TC-P — 15/11/2026

- **C-TC-01:** SDK 2.1 ngăn/cấu hình/UI và CLI/CoreGia nạp cấu hình/tệp DEMO. Mẫu NGAN-0 đã có; TC-0 chép nguyên hai tệp, so băm CRLF→LF; RAM không phải lưu bền. Cấu hình đúng khóa `{}`; không `cau_hinh_may`/`kho_tam` cũ.
- **C-TC-02:** cửa chung ghép nguồn nhiều bước và cấp quyền tệp con xuyên bước/ACK, điều phối nhánh OCR/Local/TX. Runtime thiếu thì từ chối; không tự gọi engine/CSDL/đường máy. Chưa chứng minh runner 2.0 có fan-in.
- **C-TC-03:** danh mục/hàm/bằng chứng duyệt và ngữ cảnh thời điểm/quyền tin cậy; RLS pháp nhân + nhóm + người trước khi nguồn tới engine/AI. Băm/cờ tự khai không chứng minh quyền. Phạm vi M9/07 chỉ Local do Core thực thi; test CoreGia không chứng nhận quyền thật.
- **C-TC-04:** Kho tài liệu/pgvector/tìm lai/cache và hết hạn khi nguồn/duyệt/công bố/quyền đổi, K5/ba tầng/SDK JS thuộc Core. Engine chỉ trả kết quả/nguồn/thực thể/cờ; không lập kho thứ hai hoặc tuyên bố cache/K5 đã lưu.
- **C-TC-05:** SDK log an toàn, giới hạn loại riêng, lease/lỗi trần. Đã đọc wheel: `Viec.mo_tep` dùng trần tệp chung của bước; phiếu khai 20 MiB và tự kiểm JSON chính 1 MiB, không sửa private SDK. Tách trần từng tệp chỉ là đề nghị SDK sau này, không cần lách cổng hiện tại.

- **L-TC-01/02:** lead giao bổ sung embedding Local của Hỏi AI, nguồn vị trí/bảng OCR, Trích xuất trường mục tiêu và adapter bằng chứng đã duyệt; phân định dịch vụ Kho tài liệu theo G14, cấp bộ câu hỏi/đáp án DEMO nghiệp vụ. TC không sửa các engine khác.
- Chi tiết cửa/chặn/làm tạm: phiếu §5.1. Đề xuất `ho_so_tra_cuu` **chưa duyệt**, không tạo schema ở TC-P. Chưa có số đo model/context/chất lượng hay kiểm Core thật; công cụ thử thật ở lát cuối TC-11 do Anh tự chạy.

### Bổ sung từ TC-2 — 15/11/2026

- **C-TC-01:** nay có 5 `chay_thu_demo` thật, không còn 0 demo. CLI SDK gốc
  chạy 5 ví dụ đều `CHUA_CAU_HINH`/mã 1 vì chưa có cửa nạp ngăn/cấu hình.
  `tests/chay_demo_voi_core_gia.py` nạp NganBoNho + cấu hình DEMO và đạt 5/5;
  đề nghị lead review cổng bổ sung theo phiếu §2.5. Không thay kết quả CLI chuẩn.
- **C-TC-02/03:** seam `app.cua_nguon.doc_quyen(viec_id)` mới ở biên dependency,
  **chưa phải API SDK/Core thật**. Chỉ tests gắn adapter cấp giấy độc lập theo
  việc/request/task, ngữ cảnh và từng ref/nguồn; runtime thiếu cửa trả rõ
  `TC_CHUA_CO_CUA_CORE`. Cần Core đối chiếu quyền sống mỗi lần mở tệp, dữ liệu
  danh mục/hàm/duyệt/hiệu lực, cấp tệp con xuyên bước và vòng đời/ACK snapshot.
  Giấy cấp/băm/cờ caller không chứng nhận RLS thật. Định dạng seam ở README.
- **C-TC-05:** manifest 20 MiB; engine tự chặn JSON chính 1 MiB, 20 MiB/tệp con,
  tổng 64 MiB, quy đổi lỗi đọc 413 và kiểm sâu loại riêng. Tệp con 20 MiB đã
  chạy bằng `Viec.mo_tep` thật trên adapter CoreGia; không sửa trần/private SDK.
  Biên handler giữ hủy/mất lease/ChuaRo, chặn lỗi bất ngờ chứa dữ liệu trước
  traceback SDK. Log/lỗi/lease ở tầng SDK ngoài handler vẫn cần Core/SDK xử lý.
- Không phát sinh câu hỏi mới cần Anh. TC-Q06 tiếp tục không tự xóa. Không
  triển khai kho/chỉ mục/cache/SQL/AI hoặc phần Core/engine khác để bù cửa thiếu.

### Bổ sung từ TC-4 — 15/11/2026

- **C-TC-01:** CLI SDK gốc vẫn thiếu cấu hình/ngăn/tệp con xuyên bước, 0/5
  `CHUA_CAU_HINH`, mã 1. Harness bổ sung nay 13/13, không thay cổng chuẩn;
  cần lead review §2.5, không tự nạp DEMO ở runtime để làm xanh.
- **C-TC-02/03:** Core ghim nguyên phong bì `dau_vao` vào giấy cấp cho bước
  chuẩn bị; giữ scope/ngữ cảnh/quyền sống của snapshot/gốc/OCR xuyên bước và
  ACK/vòng đời tệp kể cả việc hủy. Snapshot `cho_ai` ghim toàn nguồn/danh mục/
  cấu hình/prompt/khuôn/ngữ cảnh/map; chuyển tiếp chỉ ref/băm. Core chọn nhánh
  bỏ AI cho tầng 1 Python hoặc thiếu bằng chứng; không dựng phản hồi AI giả.
- **C-TC-05 / SDK 2.1 §7.3:** SDK kiểm required/enum/độ dài tham số trước
  handler. Thiếu hẳn prompt/tác vụ, tác vụ ngoài enum hoặc quá trần khai báo
  trả `CAI_DAT_BUOC_KHONG_HOP_LE`, chưa thể đạt mã riêng THIEU_PROMPT/
  TC_SAI_GIAI_DOAN/ngân sách ở cửa SDK. Handler kiểm đúng mã nghiệp vụ;
  prompt trắng qua SDK trả THIEU_PROMPT. Giữ nguyên manifest/private SDK.
- **L-TC-01, C-TC-02/04:** Hỏi AI/Core thực thi Local-only; kiểm token/context
  thật theo model được chọn, giới hạn đầu ra/reasoning. TC-4 chỉ đo ký tự/
  bytes, token thực null/chưa đo; không coi đủ context hoặc chất lượng thật.
  TC-5…7 phải tự kiểm quote/map/nguồn/thực thể/đơn vị, không tin riêng cờ
  AI-2; chữ nhãn kỹ thuật trong ngữ cảnh không là bằng chứng nguồn.

### Bổ sung từ TC-5 — 15/11/2026

Theo các mã cửa và **một bảng chọn duy nhất** của phiếu §5; không lập bảng
câu hỏi mới. Anh đã duyệt hướng TC-Q02/03/09/10/11 theo cột đề xuất ngày
15/11 chiều. TC-Q09 vẫn yêu cầu rà danh mục chi tiết trước áp dụng thật;
không coi đã bật nhựa/điện hoặc đã đo ngưỡng. TC-Q06 giữ **không tự xóa**.
Không phát sinh câu cần Anh quyết mới trong TC-5.

| Mã ở phiếu §5 | Cần Core / lead và bằng chứng TC-5 | Làm tạm / giới hạn |
|---|---|---|
| C-TC-01/05 | CLI 2.0 chưa nạp Ngan/cấu hình/tệp con; chạy thật vẫn 0/5 CHUA_CAU_HINH, mã 1 | Harness ngăn/quyền giả 24/24, cần lead review cổng §2.5; không thay kết quả CLI hoặc sửa SDK |
| C-TC-02/03 | Cấp nguyên yêu cầu AI độc lập phản hồi và provenance `nguon_ai` theo việc; tệp snapshot/gốc/OCR/bộ quy tắc phải có quyền sống xuyên bước và ACK/vòng đời | Seam tests `doc_quyen` thêm `yeu_cau_ai`, `nguon_ai`; thiếu trả TC_CHUA_CO_CUA_CORE. Tự dựng lại request/hash/map/khuôn, không tin caller/model/cờ đã lọc |
| C-TC-03, L-TC-02 | Core cấp bộ quy tắc ghim theo ref+băm cấu hình: bên ký/CP–TNHH, dấu hiệu loại, quan hệ đối tượng/công trình/tài sản, phạm vi phép đo; danh mục trạng thái đúng | Bộ miền phiên bản 1 mô tả ở README, kiểm đóng bằng Python; chỉ fixture DEMO, không có bộ nghiệp vụ mặc định. So khớp dấu hiệu không là nghiệm thu ngữ nghĩa/accuracy thật |
| L-TC-01, C-TC-02 | AI-2 0.5.0 kiểm mọi lá `du_lieu` như giá trị phải ở nguyên văn: mã/điểm/offset/boolean phân loại bị DU_LIEU_NGOAI_TRICH_DAN dù quote nguồn đúng | Ca nối consumer thật/Local giả giữ nguyên `khong_thay_can_cu`; TC-5 trả hàng chờ THIEU_CAN_CU. Lead Hỏi AI/Core cần rà phân biệt metadata và giá trị nghiệp vụ; không sửa Hỏi AI hoặc làm phản hồi thành công giả |
| C-TC-04 | Core duyệt/xếp/chuyển cả bộ/ghi nhật ký và tạo K5; kiểm quyền pháp nhân/nhóm/người | TC-5 chỉ đề xuất, luôn can_duyet; không ghi ngăn/cây kho/danh mục/K5. CoreGia không chứng nhận RLS hoặc nghiệp vụ đã kích hoạt |

### Bổ sung từ TC-6 — 15/11/2026

- **C-TC-01:** CLI chuẩn chạy đủ 5 ví dụ nhưng 0/5 ĐẠT, `CHUA_CAU_HINH`,
  mã 1. Cổng bổ sung §2.5 nay 17/17 DEMO; cần lead review, không thay cổng
  chuẩn và không tự nạp cấu hình DEMO vào runtime.
- **C-TC-02/03:** Core cấp `dau_vao` nguyên phản hồi Local và quyền sống của
  snapshot/gốc/OCR xuyên bước. TC-6 tái dựng nguyên yêu cầu TC-4, đối chiếu
  băm/prompt/khuôn/map/tác vụ/ngữ cảnh. Cửa này vẫn chỉ adapter CoreGia;
  runtime thiếu trả `TC_CHUA_CO_CUA_CORE`.
- **C-TC-03 — quy ước phân giải cần lead/Core review:** giấy cấp ngoài payload
  có `phan_giai_cau_hoi={bam_cau_hoi,thuc_the,y_dinh,can_lam_ro,ham}`. Core
  cấp danh mục thực thể đúng quyền/đủ câu hỏi, bộ ý định có cụm từ/cờ thời điểm;
  binding tham số thực thể/ngữ cảnh/tập giá trị, ý định được phép cho từng
  hàm, trạng thái module và mốc công bố. Định dạng chi tiết và giới hạn ở
  README gói. Chưa là API Core/SDK thật, không tin model tự khai metadata.
  Kiểm literal bảo thủ: thiếu/đa nghĩa cần làm rõ, chưa chứng minh hiểu ngữ
  nghĩa tổng quát hoặc chất lượng AI. Core phải đánh dấu tham chiếu chưa
  phân giải; thiếu căn cứ không chọn bừa hợp đồng/khoản vay.
- **C-TC-03/04:** RLS pháp nhân/nhóm/người phải lọc trước ứng viên vào engine/
  AI; giả lập lọc/tệp con không chứng minh RLS thật. Module chưa chạy hiển
  thị chờ, Core chọn tầng 2; engine chỉ đề xuất hàm. Câu có 0 ứng viên rẽ
  nhánh từ hồ sơ `da_nhan` không AI. Xếp hạng ghim cờ thời điểm Core, xuất
  nguyên tập nguồn/thực thể/phạm vi/hàm/phiên bản/mốc cho Core quản cache;
  câu thời điểm không tái dùng bản đầu, TC-Q06 tiếp tục không tự xóa.
- **C-TC-05/L-TC-01:** log an toàn/lease/ACK và token/context/model thật vẫn
  chờ Core/Hỏi AI; TC-6 không sửa SDK hoặc chạy model/provider thật. Các
  bộ đếm token TC-4 giữ null/chưa đo, không thay bằng số giả.
- Không phát sinh câu cần Anh quyết định thêm; không mở Core/SQL/kho/cache
  hoặc sửa TC-5 (phan_loai.py/quy_tac_nhom.py).

### TC-0 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng kiểm chung AGENTS.md §5** — đã hoàn thành khung được
lead giao, nhưng CLI SDK 2.0.0 trả mã 1 khi `chay_thu_demo=[]` theo yêu cầu TC-0.
PR: **chờ lead mở**; không commit/push.

Đã làm đúng 5 tệp mã: `__init__.py`, `chay.py`, `ngan.py`, `cau_hinh.py`,
`cau_hinh.schema.json`. Metadata/tài liệu: engine.json 2.0, KHAI-SDK-2.1.json,
README/CHANGELOG/NGUON/requirements.lock. Không tạo ma-nguon; không sửa nguồn cũ,
Core/SDK, mẫu chung, hợp đồng chung hoặc phiếu giao.

- Hai mẫu chép nguyên bytes; SHA-256 sau CRLF→LF khớp (xem NGUON).
- Một ngăn RAM được gắn khi thiếu app.ngan; giữ ngăn SDK có sẵn, cảnh báo RAM
  stderr đúng một lần. Không cấu hình/sổ/cache bền hoặc mạng ngoài/Cloud.
- Cấu hình qua ngăn khóa {}; thiếu không tạo default; sai trả lỗi Việt an toàn.
  Default chỉ trên bản sao; ngưỡng chưa đo không tự có số đẹp; schema cấm trường thừa.
- Stub nội bộ nhận tep JSON → khai truong.trang_thai van_ban, luôn CHUA_LAM,
  không nộp kết quả giả. Không có quy trình người dùng phụ thuộc stub.
- KHAI-SDK-2.1 có cau_hinh/dot_kiem, khóa/unique/phạm vi/trường và hai màn dự kiến;
  chưa triển khai UI (TC-9), không đưa khóa SDK 2.1 vào manifest.
- Stub và cổng cấu hình **đã kiểm bằng Core giả (CoreGia)**. Handler kiểm cấu hình
  chỉ trong tests, runtime stub giữ nguyên. Hợp đồng CAS/unique/rollback, hai luồng
  lấy hoặc tạo, pháp nhân từng lệnh, không đọc/cursor chéo kiểm trực tiếp bằng
  NganBoNho; không gọi đó là ngăn của CoreGia 2.0 hoặc chứng nhận RLS thật.
- Bộ quét AST phát hiện import Core/engine khác, socket/kênh cũ, bytecode/liên kết,
  mã thoát 0/1; symlink được kiểm bằng giả lập cờ, chưa tạo symlink Windows thật.
- Test chặn kết nối mạng; kiểm điểm vào gọi app.chay khi chưa cấu hình, không ghi
  bền. Môi trường Windows/Python 3.13.14, pytest 9.1.1 có sẵn qua venv, SDK 2.0.0
  cài offline, wheel khớp SHA256SUMS. Chưa chạy Linux/Core thật/UI/nghiệp vụ.

Kết quả thật lần kiểm cuối, PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1:

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát: 1

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
.......................................................................  [100%]
71 passed in 0.28s
Mã thoát: 0; 0 skipped

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát: 0
```

0/0 ví dụ = **chưa kiểm nghiệp vụ**, không diễn giải thành 0/0 ĐẠT.
Phiếu được SDK kiểm hợp lệ khi nạp, pytest cũng kiểm trực tiếp `kiem_phieu=[]`.
Đã đọc `thu.main` của wheel xác nhận nhánh không có demo trả 1, không phải lỗi
cấu hình, handler hoặc lỗi phiếu. `git diff --check` không lỗi.
Lượt kiểm đầu chỉ lấy mã thoát của lệnh cuối PowerShell nên đã báo nhầm cả ba
mã 0 trong cập nhật tiến độ; đã sửa và ghi riêng mã của từng lệnh như trên.

**Lệch / quyết định tạm:** không đổi phạm vi runtime. Dùng RAM NGAN-0 theo quyết
định 15/11, giữ 0 demo theo TC-0. Có mâu thuẫn mốc thay stub: lệnh TC-0/Anh ghi
TC-1, phiếu TC-1 mục 4 giữ khung tới TC-2. Không sửa phiếu gốc; lead cần thống nhất
mốc trước giao lát sau, stub bắt buộc thay trước phát hành. TC-Q13 vẫn chặn loại mới.

**Cần Core bổ sung C-TC-01:** CLI SDK 2.0.0 đang trả 1 cho khung 0 demo hợp lệ.
Đề nghị bản SDK sau có chế độ kiểm phiếu/khung 0 demo rõ ràng, tách khỏi nghiệm thu
nghiệp vụ; lead review ngoại lệ TC-0 nếu cần. Không tự sửa SDK/AGENTS hay thêm demo
thành công giả. Các phụ thuộc C-TC-01…05 và L-TC-01/02 từ TC-P vẫn giữ nguyên;
chưa có ngăn bền/CAS/quyền/cấu hình/UI Core thật. Chưa phát sinh câu nghiệp vụ mới
cần Anh ngoài bảng TC-Q01…15 hiện có.

**Thời gian thực tế TC-0:** bắt đầu 15/11/2026 12:17 theo lead; kết thúc 15/11/2026 12:30:13 (UTC+07:00), khoảng 0.22 giờ; phiếu 3 giờ **ƯỚC TÍNH**. Thời gian gồm đọc tài liệu, cài venv offline, triển khai, kiểm và báo cáo; không phải số đo vận hành engine.

### TC-1 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng chung AGENTS.md §5** — đã hoàn thành phạm vi contract
TC-1 được giao; CLI SDK 2.0.0 vẫn trả 1 khi 0 demo. Không coi là nghiệp vụ đạt.
PR: **chờ lead mở**; không commit/push.

Đã làm:

- Tạo schema nguồn `ho_so_tra_cuu` theo TC-Q13 đã duyệt, bản chép gói và ba bản
  chép schema chung nguyên trạng: **đúng 5 tệp schema nguồn/bản chép**.
  SHA-256 chỉ chuẩn hóa CRLF→LF và nguyên bytes đều khớp 4/4 cặp; NGUON có băm.
- `TC-1-CONTRACT.md`: required/enum/trần/phong bì một đầu vào, snapshot riêng
  năm tác vụ, tám năng lực để TC-2 triển khai, chuyển trạng thái/summary,
  canonical JSON/băm bytes, map Unicode nguồn/AI, ngữ cảnh và quyền Core tin cậy,
  lỗi Việt cố định. Băm/tep_id/cờ caller không thay quyền, không có `nhan_2`.
- Nêu rõ bộ đọc `cau_hinh.py` không phải validator chung cho `$ref/oneOf/type`
  mảng. Không thêm dependency. Python kiểm miền thực ở TC-2…7; mô hình TC-1 và
  bộ đánh giá giới hạn schema mới chỉ ở tests, không handler/runtime chung.
- DEMO nạp bytes thật vào kho RAM CoreGia, tính metadata/băm thật; kiểm bảng
  task/stage, ref/băm/size/config/danh mục sai, số đoạn/ứng viên lệch, hoán vị
  thiếu/thêm/trùng/đổi nguồn, pháp nhân giả khác ngữ cảnh, offset Unicode,
  JSON nghiêm và trần. Tổng bytes quá trần mô phỏng bộ đếm, không tạo tệp lớn.
- Khung/lỗi hiện có **đã kiểm bằng Core giả (CoreGia)** qua các test TC-0 giữ
  nguyên. Contract là mô hình test, không chứng nhận handler TC-2…8 hoặc RLS
  thật. Không Core/AI thật, không mạng/Cloud; chưa chạy Linux/UI/máy thật.
- Giữ nguyên manifest/chay.py và 0 demo theo lệnh Anh/lead mới nhất. TC-2 thay
  đồng thời manifest/stub `kiem_khung` trước phát hành; không còn cần hỏi mốc.
  Hai mẫu ngăn/config, schema nguồn đã khóa, ma-nguon/Core/SDK đều không sửa.
  Không tệp cấu hình/sổ/cache bền: dữ liệu cần giữ qua Ngan, snapshot qua Core.

Môi trường: venv `.venv` trong worktree, Python 3.13.14, SDK 2.0.0 cài offline
`--no-index --no-deps`; SHA-256 wheel khớp SHA256SUMS. Pytest 9.1.1 có sẵn qua
`--system-site-packages`, không tải hoặc thêm dependency runtime.

Kết quả thật lần kiểm cuối (`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`):

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát: 1 — 0 demo, chưa kiểm nghiệp vụ, không ghi 0/0 ĐẠT.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
........................................................................ [ 37%]
........................................................................ [ 75%]
................................................                         [100%]
192 passed in 0.83s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát: 0.
```

Lượt pytest đầu có 4 lỗi do test đưa schema vào bộ đọc khi ngăn chưa có cấu
hình (hàm trả None trước kiểm schema). Đã sửa fixture test nạp bản ghi DEMO,
không sửa mẫu dùng chung; lần cuối không lỗi. `git diff --check` không lỗi.

**Lệch khỏi phiếu / quyết định tạm:** không mở phạm vi. Giữ 0 demo/khung đúng
lệnh TC-1 mới nhất, không làm demo thành công giả để đổi mã CLI. Mẫu Ngan RAM
theo quyết định 15/11; schema được tạo sau khi xác minh duyệt TC-Q13 chiều 15/11.

**Cần Core / Chờ Anh:** giữ **C-TC-02** ghép nguồn/quyền tệp con/vòng đời/ACK,
**C-TC-03** dữ liệu/ngữ cảnh/danh mục/hàm/bằng chứng/quyền tin cậy và RLS trước AI,
**C-TC-05** log an toàn/kiểm loại riêng/lỗi trần/lease. Runtime thiếu cửa phải từ
chối, adapter chỉ ở tests. **C-TC-01** CLI khung 0 demo trả 1/ngăn thật còn tồn
tại; không sửa SDK. Không phát sinh câu hỏi cần Anh; TC-Q06 giữ không tự xóa.

**Thời gian thực tế TC-1:** 15/11/2026 12:36–12:49 (UTC+07:00), khoảng **0,22
giờ**, so với **3 giờ ƯỚC TÍNH** của phiếu. Gồm đọc, cài venv, schema/tài liệu,
test và báo cáo; không phải phép đo hiệu năng/chất lượng nghiệp vụ.

### TC-2 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng chuẩn AGENTS.md §5** — đã hoàn thành phạm vi TC-2,
harness nhận đủ năm tác vụ DEMO đạt; CLI SDK gốc vẫn thiếu ngăn/cấu hình.
Đã kiểm bằng Core giả (CoreGia), **chưa chứng nhận quyền Core thật**.
PR: **chờ lead mở**; nhánh `codex/e_tra_cuu-tc-2`; không commit/push.

**Đã làm:**

- Đúng **3 tệp mã runtime**: `ho_so.py`, `kiem_dau_vao.py`, `chay.py`.
  Manifest đăng ký tám năng lực/bốn loại đã duyệt, bỏ stub nội bộ `kiem_khung`;
  bảy handler chưa triển khai luôn `LoiNghiepVu CHUA_LAM`, không thành công giả.
- Nhận `tep` JSON bằng `viec.mo_tep`, băm bytes chính xác trước parse;
  JSON chính ≤1 MiB, manifest 20 MiB cho tệp con. Khóa trùng, NaN/Infinity/
  overflow, UTF-8/surrogate hỏng, URL/đường máy/base64 và cờ caller bị từ chối.
  Không đọc môi trường/tệp cấu hình để cho DEMO qua.
- Năm cấu trúc tác vụ; ref chỉ mở khi Core cấp, kiểm metadata/kích thước/băm/
  phiên bản, giữ nguyên phong bì OCR và quan hệ băm gốc/toàn văn. Pháp nhân lấy
  từ ngu_canh; quyền/module không suy từ prompt. Giấy cấp ràng buộc ngoài JSON,
  không có adapter test trong runtime. Khác pháp nhân/phạm vi/quyền chưa xác
  thực → `TC_CHUA_CO_CUA_CORE` theo lệnh TC-2 mới nhất; sai băm → `TC_SAI_NGUON`.
- Kiểm 20 MiB/tệp con, tổng 64 MiB, 500000 ký tự/60 trang, câu hỏi 4000,
  hàm 100, tổng mục danh mục 1000, ứng viên 50; ngân sách cấu hình chỉ giảm.
  Không cắt ngầm. Tầng 1 không mở lại gốc/OCR theo QĐ-4; tầng 2–3 đối chiếu
  đoạn với nguồn/phiên bản/băm/offset khi nhận, chưa soạn câu trả lời nghiệp vụ.
- Cấu hình và row_version từ **một lần đọc** nhất quán; điền default trên bản
  sao, thiếu → CHUA_CAU_HINH, lỗi mẫu đổi câu Việt an toàn. Snapshot đầy đủ lên
  Core bằng tai_tep_ra; hồ sơ ≤64 KiB chỉ ref/băm/tóm tắt, ket_qua=null ở bước
  nhận. Giữ ChuaRo/hủy/mất lease; lỗi bất ngờ trong handler không lộ dữ liệu
  qua traceback SDK. Không câu hỏi/toàn văn trong log.
- Dữ liệu/cấu hình chỉ Ngan/kho Core, RAM mất khi dừng và cảnh báo rõ. Không
  cache/sổ/tệp cấu hình hoặc tệp tạm runtime trên máy; không cần dọn tạm local.
  Tệp upload còn treo khi mất ACK do vòng đời kho Core quản, chờ C-TC-02.
- Năm ví dụ DEMO có bytes/metadata/băm thật; harness nạp ba tệp con DEMO từ gói,
  NganBoNho/cấu hình và giấy cấp quyền giả theo từng việc rồi chạy cùng ví dụ.
  Hai mẫu NGAN-0 và bốn cặp schema giữ nguyên, test so băm LF tiếp tục đạt.
  Không sửa ma-nguon/Core/SDK/tài liệu loại chung hoặc thêm dependency.

**Kết quả kiểm thật lần cuối** (`PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`):

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng
[LỖI] Nhận DEMO — Phân loại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Cắt đoạn: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Phân tích câu hỏi: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Xếp hạng lại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Soạn trả lời tầng 1: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
Engine e_tra_cuu 0.1.0: có ví dụ chạy thử DEMO chưa đạt.
Mã thoát: 1; 0/5 ĐẠT. Test qua CoreGia SDK gốc xác nhận cả 5 mã CHUA_CAU_HINH.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 68%]
........................................................................ [ 91%]
...........................                                              [100%]
315 passed in 2.39s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát: 0.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng
[ĐẠT] Nhận DEMO — Phân loại
[ĐẠT] Nhận DEMO — Cắt đoạn
[ĐẠT] Nhận DEMO — Phân tích câu hỏi
[ĐẠT] Nhận DEMO — Xếp hạng lại
[ĐẠT] Nhận DEMO — Soạn trả lời tầng 1
5/5 DEMO ĐẠT; mạng ngoài/Cloud=0.
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát: 0.
```

315 tests gồm hồi quy TC-0/1 và handler TC-2: năm yêu cầu hợp lệ; sai băm bytes/
metadata/phiên bản; JSON chính đúng/quá 1 MiB trước parse; tệp con >1 MiB đến
**đúng 20 MiB** đọc được; >20 MiB bị từ chối; bốn nguồn thực 17 MiB/tệp vượt
tổng 64 MiB; JSON OCR >1 MiB; JSON nghiêm cả chính/con; không quyền/khác pháp
nhân/module/nhóm/người/phạm vi; OCR rỗng/quá chữ/quá trang; trần danh mục/hàm/
câu hỏi/ứng viên/đầu ra; nguồn/offset ứng viên sai; cấu hình thay ngay sau đọc
vẫn ghim đúng bản+version; hủy trong ba mốc đọc; mất lease trước upload/nộp;
mất ACK tệp/kết quả/kết thúc 1 hoặc 3 lần chỉ ghi một lần cùng idempotency key;
mất ACK hết lượt không tự báo XONG; ChuaRo không thành XONG; lỗi adapter bất
ngờ không lộ nội dung log. Mạng ngoài/Cloud=0, không AI/Core thật.

Lượt kiểm đầu đã phát hiện 14 lỗi fixture TC-0 còn đăng ký một handler trên
manifest tám năng lực và 2 lỗi setup do ID parametrized quá dài trên Windows.
Đã sửa fixture test cô lập đúng năng lực và đặt ID ngắn, không sửa SDK/mẫu.
Lần kiểm cuối như trên không lỗi/skip. Không dùng số test thay chất lượng tra cứu.

Môi trường: Windows, Python 3.13.14, pytest 9.1.1 có sẵn qua venv
`--system-site-packages`; SDK 2.0.0 cài offline `--no-index --no-deps`, SHA-256
wheel khớp SHA256SUMS.txt. Chưa chạy Linux, UI, RLS/Core thật hoặc đo model.

`git diff --check` không lỗi; đối chiếu cuối xác nhận hai mẫu/bốn schema nguyên
trạng, 5 băm DEMO khớp, không bytecode; tệp lớn nhất gói 23472 bytes.

**Thời gian thực tế:** 15/11/2026 12:51–13:25:19 (UTC+07:00), khoảng **0,57 giờ**.
Phiếu **4 giờ ƯỚC TÍNH**; thời gian gồm
đọc/triển khai/kiểm/tài liệu, không phải phép đo hiệu năng hoặc giờ chờ Core.

**Lệch khỏi phiếu / quyết định tạm:** không mở phạm vi. RAM theo quyết định
15/11; adapter quyền/tệp con chỉ tests như lệnh giao. Cổng bổ sung 5/5 ĐẠT
không thay CLI chuẩn 0/5; cần lead review §2.5, không sửa AGENTS/SDK để đổi
điều kiện. Khác pháp nhân dùng mã TC_CHUA_CO_CUA_CORE theo lệnh TC-2, giữ
mô hình test TC-1 như bằng chứng lịch sử. Bản 0.1.0 còn nội bộ, chưa phát hành.

**Cần Core / Chờ Anh:** C-TC-01 ngăn/cấu hình/CLI; C-TC-02 ghép nguồn/quyền
tệp con/xuyên bước/vòng đời/ACK; C-TC-03 ngữ cảnh/dữ liệu/quyền Core thật;
C-TC-05 an toàn SDK ngoài handler/loại riêng/lỗi trần/lease. Chưa chứng nhận
quyền Core thật; không phát sinh câu hỏi cần Anh, TC-Q06 giữ không tự xóa.

### TC-3 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng chung AGENTS.md §5** — hoàn thành phần TC-3 được giao
và ba nợ TC-2, **đã kiểm bằng Core giả (CoreGia)**. CLI SDK chuẩn vẫn lỗi
`CHUA_CAU_HINH`/mã 1 theo giới hạn phiếu §2.5; không thay bằng kết quả harness.
Nhánh `codex/e_tra_cuu-tc-3`; PR: **chờ lead mở**; không commit/push.

**Đã làm:**

- `cat_doan.py`, `vi_tri.py`, `chay.py`: đăng ký `tra_cuu.cat_doan@1`, chỉ nhận
  hồ sơ `cat_doan/da_nhan`; kiểm lại snapshot/băm bytes/phiên bản/quyền sống
  từng tệp và metadata Core, trả cùng loại `da_cat_doan`. Giữ nguyên phong bì
  `van_ban_tai_lieu`, tách băm bytes gốc và băm UTF-8 toàn văn. Cấu hình và
  row_version lấy bản Ngan đã ghim, không đọc lại bản hiện tại giữa chuỗi.
- Cắt Điều/Khoản rồi câu/khối/xuống dòng/trang, ghép tới mục tiêu; không cắt
  từng N ký tự. Mã ổn định theo nguồn/phiên bản/offset/bản thuật toán. Đơn vị
  không chia an toàn vượt 8000 → `TC_KHONG_CAT_DUOC`; quá số đoạn/ngân sách →
  `TC_QUA_GIOI_HAN`, không bỏ đuôi hoặc nộp kết quả dở.
- Bảng giữ hàng/cột, ô gộp/ô rỗng, tiêu đề do nguồn khai, map từng ô. Dùng
  offset tường minh hoặc phép chiếu TAB + LF/CRLF khớp toàn bộ nguồn; không
  kiểm được map thì từ chối. Tiêu đề lặp là `ngu_canh_lap`, đoạn tổng hợp có
  offset tổng null và map từng phần. Vùng `noi_dung` phủ toàn văn đúng một
  lần, kể cả khoảng trắng/trang rỗng/cuối tài liệu. Giữ dấu/NFC/NFD, tiền/ngày.
- Hộp chỉ lấy từ khối/ô nguồn ở đúng cấp; không tạo confidence/hộp bao hoặc
  mượn hộp bảng cho ô. DOCX chưa render giữ `so_trang=0,trang=[]`, vị trí đoạn
  null. Nhóm/loại/hiệu lực/tình trạng duyệt giữ từ metadata tin cậy, không
  nâng phân loại đề xuất thành đã duyệt. Snapshot/danh sách đoạn gửi bằng
  `tai_tep_ra`, `so_doan=len(doan)`; hủy theo cụm, tiến độ không có nội dung.
- `kiem_dau_vao.py` đóng nợ TC-2: regex đường dẫn/URL/base64 chỉ ở khóa và
  định danh/tham chiếu, không chặn câu hỏi/quote/giá trị hợp lệ; object
  metadata/ứng viên/bằng chứng/mục danh mục từ chối trường thừa (loại văn bản
  chung vẫn cho phần mở); luồng đọc ngắn đọc tiếp tới EOF/trần và đóng handle.
- Bổ sung test/harness và hướng dẫn README/CHANGELOG/NGUON. Cố định LF cho DEMO
  có băm bytes bằng `.gitattributes` cục bộ; nội dung LF bằng nguyên bytes
  HEAD, không đổi băm hoặc chữa nguồn ở runtime. Giữ nguyên mẫu NGAN-0/schema/
  requirements.lock; chỉ thư viện chuẩn + SDK. Không chỉ mục/vector/cache/AI,
  không lưu bền hoặc tạo tệp tạm nên không có tệp tạm cần dọn.

**Kết quả kiểm thực** trên Windows, Python 3.13.14, pytest 9.1.1 qua venv
`--system-site-packages`; SDK 2.0.0 cài offline `--no-index --no-deps`, SHA-256
wheel khớp SHA256SUMS.txt. Không tải mạng hoặc thêm dependency.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
[LỖI] Nhận DEMO — Phân loại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Cắt đoạn: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Phân tích câu hỏi: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Xếp hạng lại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Soạn trả lời tầng 1: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
Engine e_tra_cuu 0.1.0: có ví dụ chạy thử DEMO chưa đạt.
0/5 ĐẠT; mã thoát 1; mã lỗi mỗi ca CHUA_CAU_HINH.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
457 passed in 9.17s
0 failed, 0 skipped; mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
[ĐẠT] Nhận DEMO — Phân loại
[ĐẠT] Nhận DEMO — Cắt đoạn
[ĐẠT] Nhận DEMO — Phân tích câu hỏi
[ĐẠT] Nhận DEMO — Xếp hạng lại
[ĐẠT] Nhận DEMO — Soạn trả lời tầng 1
[ĐẠT] DOCX DEMO không trang
[ĐẠT] Điều/Khoản DEMO xuyên trang rỗng
[ĐẠT] Bảng DEMO ô gộp/trống
[ĐẠT] Bảng DOCX DEMO không trang
9/9 DEMO ĐẠT; mạng ngoài/AI/Cloud=0 (không có provider trong harness).
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát 0.
```

Cả CLI/harness đều có cảnh báo mẫu ngăn ra stderr một lần: “Đang lưu tạm
trong bộ nhớ; khởi động lại sẽ mất hạn mức/dấu chống trùng”. CLI không tự nạp
cấu hình DEMO để làm xanh. Harness giữ năm ví dụ nhận của manifest và bốn ca
nhận → cắt bổ sung, Core cấp snapshot/tệp con cho việc kế tiếp.

457 tests gồm 315 hồi quy và 142 ca TC-3/nợ TC-2: Điều/Khoản xuyên trang,
tiêu đề trùng/trang rỗng/đuôi; bảng gộp ngang/dọc/ô rỗng/tiêu đề lặp, phép
chiếu LF/CRLF và DOCX không trang; source/map/hộp sai bị từ chối; Unicode
NFC/NFD/emoji, quote/offset lát Python, tái dựng đủ nguồn; đơn vị đúng 8000
và 8001 ký tự, Điều dài chia được theo câu, hàng bảng không chia an toàn;
5001 đoạn và trần cấu hình thấp hơn; trần snapshot kết quả; sửa băm/nguồn/
phiên bản/config/metadata, thiếu quyền/pháp nhân/cửa Core; hủy lúc đọc/cắt,
mất lease/ACK, ChuaRo; log không chứa nội dung, 0 AI/Cloud/ghi đĩa. Ba nợ
TC-2 có kiểm nội dung hợp lệ/traversal/khóa thừa và đọc ngắn 1/7/97 bytes.
Không lấy số test làm độ chính xác nghiệp vụ hoặc bằng chứng RLS thật.

Lượt đầu TC-3 phát hiện regex Khoản chưa nhận dấu chấm sau số; đã sửa và kiểm
lại xuyên trang. Hồi quy TC-0 còn coi cắt đoạn là stub; chuyển kiểm stub sang
`xuat_ket_qua` chưa triển khai. Baseline trước sửa có 314 passed/1 failed do
auto-CRLF DEMO; đã sửa quy tắc checkout, không đổi tiêu chí/băm cho test qua.

**Lệch khỏi phiếu / quyết định tạm:** 4 tệp mã thay vì 3 do lead giao thêm
`kiem_dau_vao.py` để đóng nợ TC-2, vẫn trong trần khoảng 5. Thêm metadata
`.gitattributes` cho DEMO; không mở năng lực mới ngoài TC-3. RAM và seam Core
giả theo phiếu; cổng bổ sung không thay CLI chuẩn. Bản 0.1.0 chưa phát hành.

**Cần Core (bổ sung TC-3):**

- **C-TC-01:** ngăn/cấu hình/CLI SDK thật; cổng chuẩn còn chưa đạt, cần lead
  review cổng bổ sung §2.5. Không đổi AGENTS/API/SDK để làm xanh.
- **C-TC-02/03:** Core phải ghim nguyên phong bì bước trước vào giấy cấp
  `dau_vao`, cung cấp `metadata_core` tin cậy, cùng scope và quyền sống từng
  snapshot/gốc/OCR xuyên bước/vòng đời/ACK. Seam này mới kiểm bằng adapter
  tests, chưa là API SDK đã phát hành. Ref/băm/cờ caller không thay quyền.
- **C-TC-02/03, L-TC-01:** nguồn bảng ngoài phép chiếu TAB + LF/CRLF phải có
  map Unicode tường minh cho khối và từng ô, kể cả ô trống; nguồn cấp nhãn
  hàng tiêu đề. DOCX có cấu trúc dùng phần mở `khoi`, giữ phong bì không trang.
  Chưa có map kiểm được thì từ chối, không tự viết reader/render/OCR mới.
- **C-TC-05:** an toàn log/loại riêng/lease ngoài handler còn thuộc SDK/Core.
  Chưa kiểm Linux, Core/RLS thật, UI, model hoặc chất lượng nghiệp vụ.

**Chờ Anh mới phát sinh:** không có; TC-Q06 giữ **không tự xóa**.

**Kiểm bàn giao:** `git diff --check` mã 0; 6/6 cặp mẫu/schema băm LF khớp,
5/5 băm yêu cầu DEMO khớp; nguồn DEMO LF bằng nguyên bytes HEAD. Không có
bytecode/liên kết trong gói; tệp lớn nhất 25137 bytes. Tất cả thay đổi thuộc
`e_tra_cuu/` trong worktree này; không sửa ma-nguon/Core/SDK hoặc contract chung.

**Thời gian thực tế TC-3:** bắt đầu 15/11/2026 **13:33** theo lead; kết thúc
kiểm bàn giao **14:09:46 (UTC+07:00)**, khoảng **0,61 giờ**. Phiếu **4 giờ
ƯỚC TÍNH**. Gồm đọc tài liệu, tạo venv/cài SDK offline, triển khai, kiểm và
tài liệu; không phải thời gian vận hành hoặc đo chất lượng model.

### TC-4 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng CLI chuẩn; đã hoàn thành triển khai và kiểm phạm vi
TC-4 bằng Core giả (CoreGia).** Trạng thái **Chờ Core**, PR: **chờ lead mở**.
Không ghi nghiệm thu Core/RLS/model thật. TC-Q06 giữ **không tự xóa**.

**Đã làm:** đúng 3 tệp runtime `chuan_bi_ai.py`, `ngu_canh_ai.py`, `chay.py`:

- Kiểm task/stage, tham số module, nguồn/băm/phiên bản/tóm tắt và cấu hình đã
  ghim; không đọc cấu hình mới giữa chuỗi. Mở snapshot/gốc/OCR bằng `mo_tep`,
  so giấy cấp `dau_vao`, request/task/ngữ cảnh và từng nguồn. Thiếu cửa tin
  cậy từ chối, không coi băm/prompt/cờ payload là quyền.
- Dựng đủ bốn khuôn/ngữ cảnh Local, mã vùng nguồn/ứng viên/hàm, map Unicode
  ngữ cảnh → nguồn và chuỗi snapshot. Phân loại chỉ chọn mã Core; phân tích
  dùng hàm/phiên bản/schema tham số; ref nội bộ chuyển gốc riêng mỗi hàm,
  đóng thuộc tính chưa khai, không tải mạng. Xếp hạng đủ tập mã đúng một lần,
  điểm đúng thang. Soạn tầng 2–3 có khẳng định/nguồn/câu trích; không model
  tạo quyền/duyệt/Xanh. Tầng 1 Python hoặc không bằng chứng từ chối chuẩn bị
  để Core đi nhánh bỏ AI, không yêu cầu/phản hồi giả.
- Snapshot `cho_ai` tải Core giữ tác vụ/nguồn/danh mục/cấu hình/prompt/phiên
  bản/khuôn/ngữ cảnh chính xác/map/băm UTF-8 và số đo ký tự/bytes. Token thực
  null, trạng thái `chua_do`. Chuyển tiếp đúng tám trường ref/băm/metadata,
  mẫu bình thường ≤4 KiB; không toàn văn/danh mục/câu hỏi dài. Consumer AI-2
  giữ nguyên chuyển tiếp và không đưa vào prompt provider.
- Trần ngữ cảnh/khuôn/chuyển tiếp/số hàm/danh mục/ứng viên được kiểm theo cấu
  hình ghim; vượt trả TC_QUA_NGAN_SACH_AI, không cắt/batch/Cloud. Giữ nguyên
  Unicode/NFC/NFD/CRLF/emoji; nhãn kỹ thuật không là chứng cứ. Map câu hỏi/
  mô tả hàm chỉ tới snapshot, `ma_nguon=null`, không giả nguồn tài liệu.
- Bổ sung 91 ca TC-4 và bốn mẫu harness; cập nhật hồi quy TC-2 để chỉ kiểm
  stub chưa làm. Consumer AI-2 có thật trong test, app test giữ nguyên khai
  báo năng lực `ai.hoi_theo_yeu_cau@1`; provider Local giả do CoreGia điều
  phối, không HTTP/model thật. Không sửa Hỏi AI hoặc import nó trong gói TC.
- Mọi dữ liệu cần giữ qua Ngan/tệp Core; không tệp tạm hay lưu bền trên máy.
  Không thêm dependency, giữ nguyên schema/mẫu NGAN-0/manifest/requirements.
  README/NGUON/CHANGELOG đã cập nhật; không sửa nguồn cũ/Core/SDK/mẫu chung.

**Kết quả kiểm thực:** Windows, Python 3.13.14, pytest 9.1.1, venv
`--system-site-packages`; SDK 2.0.0 cài wheel offline `--no-index --no-deps`,
SHA-256 khớp SHA256SUMS.txt. Biến môi trường PYTHONUTF8/PYTHONDONTWRITEBYTECODE=1.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
[LỖI] Nhận DEMO — Phân loại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Cắt đoạn: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Phân tích câu hỏi: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Xếp hạng lại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Soạn trả lời tầng 1: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
Engine e_tra_cuu 0.1.0: có ví dụ chạy thử DEMO chưa đạt.
0/5 ĐẠT; mã thoát 1, CHUA_CAU_HINH. Không đổi kết quả CLI chuẩn.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
548 passed in 8.27s
0 failed, 0 skipped; mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
[ĐẠT] Nhận DEMO — Phân loại
[ĐẠT] Nhận DEMO — Cắt đoạn
[ĐẠT] Nhận DEMO — Phân tích câu hỏi
[ĐẠT] Nhận DEMO — Xếp hạng lại
[ĐẠT] Nhận DEMO — Soạn trả lời tầng 1
[ĐẠT] DOCX DEMO không trang
[ĐẠT] Điều/Khoản DEMO xuyên trang rỗng
[ĐẠT] Bảng DEMO ô gộp/trống
[ĐẠT] Bảng DOCX DEMO không trang
[ĐẠT] Chuẩn bị AI DEMO — phan_loai
[ĐẠT] Chuẩn bị AI DEMO — phan_tich_cau_hoi
[ĐẠT] Chuẩn bị AI DEMO — xep_hang_lai
[ĐẠT] Chuẩn bị AI DEMO — soan_tra_loi
13/13 DEMO ĐẠT; mạng ngoài/lượt provider/Cloud=0 (không có provider trong harness).
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát 0.
```

Cảnh báo mẫu RAM ra stderr: “Đang lưu tạm trong bộ nhớ; khởi động lại sẽ mất
hạn mức/dấu chống trùng”. Test toàn bộ gồm 457 hồi quy + 91 ca TC-4: bốn
khuôn/ngữ cảnh, map/quote khứ hồi và nguyên văn trùng ở nhiều ứng viên, UTF-8/
NFC/NFD/emoji/CRLF; prompt thiếu/trắng/sai task/băm/snapshot/cấu hình/nguồn/
quyền, injection bất hoạt, giới hạn số lượng và byte thật. Ngữ cảnh **đúng
100000 ký tự đạt, thêm 1 từ chối**; khuôn dưới 32768 ký tự nhưng quá 32768
bytes UTF-8 bị từ chối; khuôn tại trần bytes và thấp hơn 1 byte; mã yêu cầu
opaque Unicode kiểm byte chuyển tiếp. Có hủy lúc đọc/dựng/trước/sau tải,
mất lease/ACK, ChuaRo không nộp XONG giả, không ghi tệp trên máy. Local giả
trả đúng metadata và ChuaRo được Core giữ CHUA_RO; 0 Cloud/mạng. Không lấy
số test hoặc fixture injection làm số đo chất lượng/chống injection model thật.

**Lệch khỏi phiếu / quyết định tạm:** đúng 3 tệp mã; RAM/seam tin cậy trong
tests theo phiếu. Giữ nguyên manifest/API/SDK; giới hạn mã lỗi tham số tại
cửa SDK nêu ở C-TC-05 bên trên, không che bằng test handler. Khuôn chỉ nhận
tập từ khóa AI-2 hỗ trợ, ref nội bộ không đệ quy; schema ngoài tập từ chối.
Không chạy AI thật/Linux/Core thật, chưa đo token/context hay chất lượng.

**Cần Core / Chờ Anh:** C-TC-01/02/03/05, L-TC-01 và Core điều phối nhánh/
Local/context như mục “Bổ sung từ TC-4”. Không phát sinh câu chờ Anh; TC-Q06
giữ không tự xóa. Lead review cổng bổ sung §2.5 và mở PR.

**Kiểm bàn giao:** `git diff --check` mã 0; 6/6 cặp mẫu/schema khớp SHA-256
sau CRLF→LF, 5/5 băm yêu cầu DEMO khớp bytes. Không bytecode/liên kết trong
gói; tệp lớn nhất 25137 bytes. Chỉ thay đổi trong `e_tra_cuu/` tại worktree
`codex/e_tra_cuu-tc-4`; không commit/push.

**Thời gian thực tế TC-4:** bắt đầu **15/11/2026 14:11** theo lead; kết thúc
kiểm bàn giao **14:32:43 (UTC+07:00)**, khoảng **0,36 giờ**; phiếu **4 giờ
ƯỚC TÍNH**. Gồm đọc tài liệu, cài venv/SDK offline, triển khai, kiểm và tài
liệu; không gồm thời gian chờ Core/model thật hay đo chất lượng thực tế.

### TC-5 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng CLI chuẩn; đã hoàn thành triển khai và kiểm phạm vi
TC-5 bằng Core giả (CoreGia).** Trạng thái **Chờ Core**, PR: **chờ lead mở**.
Không ghi nghiệm thu Core/RLS/model thật. TC-Q06 giữ **không tự xóa**.

**Đã làm:** đúng 3 tệp runtime `phan_loai.py`, `quy_tac_nhom.py`, `chay.py`:

- Đăng ký hậu kiểm `tra_cuu.phan_loai_tai_lieu@1`, nhận `tra_loi_ai`, xuất
  `ho_so_tra_cuu` với `da_phan_loai` hoặc `cho_phan_loai`. Cloud từ chối
  TC_CHI_LOCAL; lệch nguồn/request/task/prompt/version/model/chuyển tiếp/băm
  TC_SAI_NGUON; sai khuôn/quote/offset TC_AI_SAI_KHUON. Câu lỗi Việt cố định,
  không nội dung nguồn/path/khóa, không XONG rỗng khi lỗi.
- Mở snapshot/gốc/OCR/bộ quy tắc qua Core; kiểm bytes/băm/phiên bản/quyền
  nguồn, cấu hình ngăn đã ghim. Dựng lại ngữ cảnh/map/đoạn/khuôn/request
  canonical và băm AI-2. Tự kiểm cả quote ngoài và căn cứ từng quyết định,
  Unicode code point/offset gốc, không tin riêng kiem_trich_dan.dat.
- Bộ quy tắc Core cấp bằng ref+băm cấu hình, không bộ mặc định trên máy:
  danh mục/nhóm/loại/trạng thái/đối tượng, dòng bên ký, CP/TNHH và quan hệ
  công trình/tài sản. Chọn mã snapshot; thiếu/bên ký khác/hỗn hợp/ngoài phạm
  vi/chưa đo/sai phạm vi phép đo đều chờ. Điểm model không là xác suất đã
  hiệu chỉnh; mọi quyết định vẫn cần Core duyệt.
- Áp thứ tự 04 cho công trình/thiết bị lắp/vật tư cấp/sửa chữa có thông tin;
  thuê máy thi công vẫn 03; quy chế thưởng phạt người lao động 07, quy chế
  khác 08. Vật tư/sửa chữa thiếu thông tin công trình không suy 03 vì thiếu
  BOQ. Có tài sản/công trình Core cấp dù không dự án vẫn đề xuất 04; nhựa/
  điện chờ kích hoạt, loại ngừng nhận mới chờ. Model cố chọn loại bị loại
  khỏi enum là sai khuôn; Python nhận diện loại đó với lựa chọn null thì
  trả hàng chờ đúng lý do. Gốc 08 cho phép loại/đối tượng null, không tạo
  loại/thư mục. Không nhận diện được loại không tự ép 08.
- Phụ lục đổi nhóm hoặc bản chất loại: chỉ đề nghị chuyển cả bộ khi có mã
  bộ/quan hệ Core và căn cứ, luôn chờ. Không tự ghi ngăn, cây kho, danh mục,
  K5 hoặc nhật ký; Core sở hữu duyệt/xếp/chuyển. Chỉ snapshot được tải Core,
  không tệp tạm/cấu hình/sổ/cache bền trên máy.
- Thêm 126 ca TC-5, harness thêm 11 ca (8 nhóm + 3 hàng chờ) và giữ toàn bộ
  hồi quy. Test consumer AI-2 0.5.0 có thật với một provider Local giả do
  CoreGia điều phối ghi đúng giới hạn metadata của upstream và hàng chờ,
  không sửa Hỏi AI. Không import engine khác trong gói TC.
- Cập nhật README/NGUON/CHANGELOG và trạng thái một bảng chọn phiếu §5.2;
  không thêm dependency/schema, không sửa ma-nguon/Core/SDK/mẫu chung.

**Kết quả kiểm thực:** Windows, Python 3.13.14, pytest 9.1.1, venv
`--system-site-packages`; SDK 2.0.0 cài wheel offline `--no-index --no-deps`,
SHA-256 `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`
khớp SHA256SUMS.txt. PYTHONUTF8/PYTHONDONTWRITEBYTECODE=1, mọi lệnh Python -B.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
[LỖI] Nhận DEMO — Phân loại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Cắt đoạn: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Phân tích câu hỏi: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Xếp hạng lại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Soạn trả lời tầng 1: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
Engine e_tra_cuu 0.1.0: có ví dụ chạy thử DEMO chưa đạt.
0/5 ĐẠT; mã thoát 1, CHUA_CAU_HINH. Chưa đạt cổng chuẩn, không thay kết quả CLI.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
674 passed in 18.56s
0 failed, 0 skipped; mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
[ĐẠT] Nhận DEMO — Phân loại
[ĐẠT] Nhận DEMO — Cắt đoạn
[ĐẠT] Nhận DEMO — Phân tích câu hỏi
[ĐẠT] Nhận DEMO — Xếp hạng lại
[ĐẠT] Nhận DEMO — Soạn trả lời tầng 1
[ĐẠT] DOCX DEMO không trang
[ĐẠT] Điều/Khoản DEMO xuyên trang rỗng
[ĐẠT] Bảng DEMO ô gộp/trống
[ĐẠT] Bảng DOCX DEMO không trang
[ĐẠT] Chuẩn bị AI DEMO — phan_loai
[ĐẠT] Chuẩn bị AI DEMO — phan_tich_cau_hoi
[ĐẠT] Chuẩn bị AI DEMO — xep_hang_lai
[ĐẠT] Chuẩn bị AI DEMO — soan_tra_loi
[ĐẠT] Phân loại DEMO — 01
[ĐẠT] Phân loại DEMO — 02
[ĐẠT] Phân loại DEMO — 03
[ĐẠT] Phân loại DEMO — 04
[ĐẠT] Phân loại DEMO — 05
[ĐẠT] Phân loại DEMO — 06
[ĐẠT] Phân loại DEMO — 07
[ĐẠT] Phân loại DEMO — 08
[ĐẠT] Hàng chờ DEMO — ngưỡng chưa đo
[ĐẠT] Hàng chờ DEMO — vật tư thiếu công trình
[ĐẠT] Hàng chờ DEMO — nhựa chưa bật
24/24 DEMO ĐẠT; mạng ngoài/lượt provider/Cloud=0 (không có provider trong harness).
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát 0.
```

Cảnh báo RAM ra stderr đúng mẫu: “Đang lưu tạm trong bộ nhớ; khởi động lại
sẽ mất hạn mức/dấu chống trùng”. Test TC-5 riêng **126 passed in 4.83s**;
tổng 548 hồi quy + 126 TC-5 = 674, không skip. Các ca có nguồn/băm/bytes thật
trong kho RAM CoreGia; test chặn mạng, số liệu/nhận diện/ngưỡng đều DEMO.
Không lấy số test làm accuracy hoặc đo hiệu chỉnh thực tế. Ca nối consumer
AI-2 thật giữ nguyên phản hồi `khong_thay_can_cu` do kiểm mọi lá metadata,
TC-5 đưa chờ THIEU_CAN_CU; 0 Cloud/AI thật trong toàn bộ bài kiểm.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** đúng 3 tệp runtime, ngăn và seam
Core giả theo phiếu. Bộ quy tắc miền 1 qua ref cấu hình được mô tả trong README
để lead/Core review dữ liệu thực; không thêm loại dữ liệu hoặc cổng SDK mới.
Không sửa API/manifest/schema/SDK để làm xanh CLI. Chưa kiểm Linux, Core/RLS,
model/token/context/chất lượng thật; chưa kích hoạt danh mục/ngưỡng nghiệp vụ.

**Cần Core / Chờ Anh mới phát sinh:** chi tiết tại bảng “Bổ sung từ TC-5” ở
mục Cần Core và bảng chọn duy nhất phiếu §5.2. Cần cấp nguyên yêu cầu/provenance
AI độc lập, quyền tệp/bộ quy tắc xuyên bước, rà bộ dấu hiệu/quan hệ/phạm vi bài
đo; lead Hỏi AI/Core rà lỗi coi metadata phân loại là giá trị nguyên văn.
C-TC-01/02/03/04/05 và L-TC-01/02 vẫn chờ. Không có câu hỏi mới cần Anh;
TC-Q06 không tự xóa. PR **chờ lead mở**, không commit/push.

**Kiểm bàn giao:** `git diff --check` mã 0; 6/6 cặp mẫu/schema khớp SHA-256
sau chỉ đổi CRLF→LF. Không bytecode/liên kết trong gói; tệp lớn nhất 25318
bytes. Chỉ thay đổi trong `e_tra_cuu/` tại worktree `codex/e_tra_cuu-tc-5`;
không sửa cau_hoi.py/xep_hang.py của TC-6, không commit/push.

**Thời gian thực tế TC-5:** bắt đầu **15/11/2026 14:34** theo lead; kết thúc
kiểm bàn giao **15:05:04 (UTC+07:00)**, khoảng **0,52 giờ**. Phiếu **4 giờ
ƯỚC TÍNH**. Gồm đọc tài liệu, tạo venv/cài SDK offline, triển khai, kiểm và
tài liệu; không gồm chờ Core hoặc đo/nghiệm thu nghiệp vụ/model thật.

### TC-6 — biên bản bàn giao ngày 15/11/2026

**Kết luận: Chưa đạt cổng kiểm chung AGENTS.md §5** — TC-6 đã hoàn thành
trong phạm vi adapter CoreGia, nhưng CLI SDK chuẩn 0/5 ĐẠT/mã 1 do thiếu
cấu hình Ngan. PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia), không
chứng nhận RLS/Core/AI thật; không commit/push.

**Đã làm:** đúng ba tệp mã `cau_hoi.py`, `xep_hang.py`, `chay.py`:

- `tra_cuu.phan_tich_cau_hoi@1`: Local → `da_phan_tich`; kiểm cùng snapshot/
  nguồn/băm/prompt/tác vụ/chuyển tiếp và căn cứ câu hỏi. Thực thể giữ đúng
  mã/loại/giá trị, kể cả 0 đầu; VAY-A/B không trùng theo ngữ nghĩa. Ý định và
  tập thực thể bám danh mục Core ngoài payload, không để model tự cấp quyền.
  Mơ hồ đánh dấu cần làm rõ và bỏ hàm, không chọn bừa hợp đồng/khoản vay.
- Cờ thời điểm từ câu hỏi/ý định Core; “tháng này” lấy mốc Core có múi giờ,
  kiểm cả tháng nhuận và mốc khác năm, không dùng đồng hồ máy/model. Giữ
  bằng chứng Unicode code point, không đổi NFD/NFC hoặc số 0 đầu.
- Hàm đúng allowlist tên/phiên bản/schema/ý định/binding tham số/phạm vi.
  Từ chối SQL/code/URL/khóa thừa kể cả object con/schema mở. Không bỏ tham
  số thực thể/ngữ cảnh để mở rộng phạm vi. Module chưa chạy ghi chờ/không
  khả dụng, Core chọn tầng 2; không thực thi hàm hay trả dữ liệu tầng 1 giả.
- `tra_cuu.xep_hang_lai@1`: Local → `da_xep_hang`; đủ đúng tập mã, mỗi mã
  một lần, điểm hữu hạn trong thang ghim. Điểm giảm, tie giữ thứ tự tập gốc
  Core. Giữ nguyên ứng viên/nội dung/vị trí/nguồn/phiên bản, không top-k.
  0 ứng viên chặn nhánh chuẩn bị AI sau kiểm nguồn, Core rẽ nhánh không AI.
- Snapshot kết quả chỉ tải Core, kiểm ACK/hủy. Xuất nguyên tập nguồn phụ
  thuộc/thực thể/phạm vi/hàm/phiên bản/mốc cho downstream/cache; điểm chỉ
  sắp thứ tự, không độ tin cậy được duyệt. Token thực vẫn null/chưa đo.
- Không tệp tạm hoặc lưu bền/cấu hình/cache/chỉ mục/nhật ký trên máy. Cấu
  hình giữ snapshot Ngan, hai mẫu NGAN-0 và bốn schema giữ nguyên. Không
  sửa ma-nguon, Core, SDK hoặc mã TC-5; không thêm dependency.

**Kết quả kiểm thực:** Windows, Python 3.13.14, pytest 9.1.1, venv
`--system-site-packages`; SDK 2.0.0 cài offline `--no-index --no-deps`,
SHA-256 wheel khớp SHA256SUMS.txt. PYTHONUTF8/PYTHONDONTWRITEBYTECODE=1.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
[LỖI] Nhận DEMO — Phân loại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Cắt đoạn: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Phân tích câu hỏi: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Xếp hạng lại: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
[LỖI] Nhận DEMO — Soạn trả lời tầng 1: "Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình."
Engine e_tra_cuu 0.1.0: có ví dụ chạy thử DEMO chưa đạt.
0/5 ĐẠT; CHUA_CAU_HINH; mã thoát 1.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
688 passed in 18.10s
0 failed, 0 skipped; mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
[ĐẠT] Nhận DEMO — Phân loại
[ĐẠT] Nhận DEMO — Cắt đoạn
[ĐẠT] Nhận DEMO — Phân tích câu hỏi
[ĐẠT] Nhận DEMO — Xếp hạng lại
[ĐẠT] Nhận DEMO — Soạn trả lời tầng 1
[ĐẠT] DOCX DEMO không trang
[ĐẠT] Điều/Khoản DEMO xuyên trang rỗng
[ĐẠT] Bảng DEMO ô gộp/trống
[ĐẠT] Bảng DOCX DEMO không trang
[ĐẠT] Chuẩn bị AI DEMO — phan_loai
[ĐẠT] Chuẩn bị AI DEMO — phan_tich_cau_hoi
[ĐẠT] Chuẩn bị AI DEMO — xep_hang_lai
[ĐẠT] Chuẩn bị AI DEMO — soan_tra_loi
[ĐẠT] Câu hỏi VAY-A DEMO
[ĐẠT] Câu hỏi VAY-B DEMO
[ĐẠT] Mã giữ 0 đầu DEMO
[ĐẠT] Xếp hạng tie giữ toàn nguồn DEMO
17/17 DEMO ĐẠT; mạng ngoài/lượt provider/Cloud=0 (không có provider trong harness).
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát 0.
```

Cảnh báo RAM ra stderr đúng mẫu: “Đang lưu tạm trong bộ nhớ; khởi động lại
sẽ mất hạn mức/dấu chống trùng”. Test gồm **548 hồi quy + 140 ca TC-6**:
thực thể A/B/AB/0007/007/mơ hồ, ý định/thời điểm/Unicode, hàm lạ/sai version/
SQL/code/URL/kiểu/schema/ref/nested/khóa thừa/ràng buộc/ngữ cảnh/module chưa
chạy; đổi/trùng/thiếu/thêm mã, NaN/Infinity/bool/điểm ngoài thang/thang khác,
tie, 0/50/51 ứng viên/ngân sách; hai nguồn và thu quyền, khác pháp nhân/
nhóm 07/Cloud, nguồn/prompt/băm/chuyển tiếp/snapshot/khuôn/map/quote giả;
hủy theo cụm/từng ứng viên/trước/sau upload, mất lease/ACK/ChuaRo và chặn ghi
đĩa/mạng. Ca lọc giả trước ứng viên chỉ kiểm adapter, không chứng nhận RLS.

**Lệch khỏi phiếu / quyết định tạm:** đúng ba tệp mã. Mã chung hậu kiểm/khuôn
đặt trong `cau_hoi.py` để `xep_hang.py` tái dùng trong phạm vi ba tệp. Bổ sung
quy ước metadata phân giải tại seam chưa phát hành (README và Cần Core),
thiếu metadata từ chối rõ. Đây là kiểm literal bảo thủ; chưa đo semantic
accuracy/model/context, chưa kiểm Core thật hoặc Linux. Test TC-2 chỉ bỏ
hai handler TC-6 khỏi danh sách stub CHUA_LAM; không bỏ ca hồi quy nghiệp vụ.

**Cần Core / Chờ Anh:** C-TC-01/02/03/04/05 và L-TC-01 như mục bổ sung
TC-6. Core/lead review metadata phân giải/allowlist/binding, cấp quyền sống/
RLS trước AI, trạng thái module/thời điểm và nhánh không AI. Lead review
cổng bổ sung §2.5 rồi mở PR. Không phát sinh câu hỏi mới cần Anh; TC-Q06
tiếp tục không tự xóa.

**Kiểm bàn giao:** `git diff --check` mã 0; 6/6 cặp mẫu/schema SHA-256 LF
khớp, 5/5 băm yêu cầu DEMO khớp bytes. Không bytecode/liên kết trong gói;
tệp lớn nhất 27044 bytes. Mọi thay đổi trong worktree này, nhánh
`codex/e_tra_cuu-tc-6`; không commit/push.

**Thời gian thực tế TC-6:** bắt đầu **15/11/2026 14:34** theo lead; kết thúc **15:06:11 (UTC+07:00)**, khoảng **0,54 giờ**; phiếu **4 giờ ƯỚC TÍNH**. Gồm đọc tài liệu, cài venv/SDK offline, triển khai, kiểm và tài liệu; không gồm chờ Core/model thật hoặc đo chất lượng thực tế.

### TC-6 — biên bản việc gộp TC-5 ngày 15/11/2026

**Kết luận: Đạt việc gộp; chưa đạt cổng kiểm chung AGENTS.md §5** vì CLI SDK
chuẩn vẫn thiếu cấu hình (C-TC-01 đã có). Trạng thái TC-6: **Chờ Core —
15/11/2026**. PR: **chờ lead mở**. Đã kiểm bằng Core giả (CoreGia).

**Đã làm:** giải đủ sáu tệp xung đột; giữ handler phân loại TC-5 và hai handler
câu hỏi/hàm/xếp hạng TC-6, lỗi riêng từng lát, nhánh 0 ứng viên và hai stub
soạn/xuất. Giữ nguyên test TC-5/TC-6 và mọi hàm test TC-2; harness gọi cả hai
bộ DEMO. README hợp nhất hành vi hiện tại, CHANGELOG và VIEC giữ nguyên hai
biên bản gốc cùng số liệu/thời gian lịch sử. NGUON cập nhật SHA-256 CRLF→LF.
Không sửa mã nghiệp vụ bốn mô-đun, Core/SDK, engine khác hoặc dependency.

**Kết quả kiểm thực:** venv Windows/Python 3.13.14, SDK 2.0.0 (wheel khớp
SHA256SUMS.txt), pytest 9.1.1; PYTHONUTF8/PYTHONDONTWRITEBYTECODE=1.

```text
.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q --basetemp=.pytest-tmp
814 passed in 43.27s
0 failed, 0 skipped; mã thoát 0.
Gồm 548 hồi quy + 126 ca TC-5 + 140 ca TC-6; hai tệp test lát giữ nguyên bytes LF.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
28/28 DEMO ĐẠT; mạng ngoài/lượt provider/Cloud=0 (không có provider trong harness).
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát 0; gồm đủ 11 ca phân loại/hàng chờ và 4 ca câu hỏi/xếp hạng.

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát 0.

.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
5/5 ví dụ lỗi CHUA_CAU_HINH; 0/5 ĐẠT; mã thoát 1.
Cả năm báo: Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình.
```

**Thời gian thực tế việc gộp:** bắt đầu **15/11/2026 15:07**, kết thúc
**15:15:27 (UTC+07:00)**, khoảng **0.14 giờ**. Phiếu TC-6 ước tính
**4 giờ** cho triển khai; không có dự toán riêng cho việc gộp. Giờ code TC-6
trước đó giữ nguyên trong biên bản gốc, không cộng nhầm vào việc gộp.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** chỉ việc gộp theo lệnh lead;
không thay đổi kiến trúc/nghiệp vụ. Giữ ngăn RAM và adapter CoreGia đã có.
Không commit/push hoặc merge --continue. Index merge nằm ngoài writable root
của phiên này; lead cần git add các tệp đã giải trước khi kết thúc merge.

**Cần Core / Chờ Anh mới phát sinh:** không có. C-TC-01/02/03/04/05 và các
mục lead đã ghi ở cả hai lát vẫn giữ nguyên; CLI chuẩn chưa đạt, chưa kiểm
Core/RLS/AI thật hoặc Linux. Không phát sinh câu cần Anh quyết thêm.

## Cần Core — bổ sung TC-7, 15/11/2026

- **C-TC-01/02/05:** giữ khoảng trống CLI §2.5: chạy thật cả 5 ví dụ chuẩn
  đều `CHUA_CAU_HINH`, mã 1; harness bổ sung đạt 36/36 với NganBoNho và
  quyền/tệp con giả. Chờ lead review cổng bổ sung, không sửa SDK để làm xanh.
- **C-TC-03:** cần binding trường/thực thể/đơn vị/hiệu lực/quote/offset đã xác
  thực do Core cấp ngoài payload ở `doc_quyen(viec_id).kiem_chung_tra_loi`.
  Profile ghim băm dữ liệu, tập trường câu hỏi, ngưỡng đo đã duyệt và mốc
  công bố/duyệt của bằng chứng. Tầng 1 cần quote/locator lưu cùng trường đã
  duyệt để tuân QĐ-4, không đọc ngược gốc/OCR. Metadata caller không thay
  profile. Đặc tả/seam và giới hạn tại `TC-7-KIEM-CHUNG.md`; **chưa phải API
  SDK thật**, thiếu cửa thì lỗi. Ngưỡng trong test chỉ DEMO, không kích hoạt
  nhóm thật hoặc thay ngưỡng từ phép đo được duyệt TC-Q15.
- **C-TC-04:** Core thực thi dừng tầng, RLS/quyền mọi nguồn, cache/hết hạn và
  K5 theo tập nguồn/phiên bản/mốc công bố/duyệt/thực thể/phạm vi/cờ thời điểm.
  TC-7 chỉ đề nghị K5 và cờ chưa lưu/chưa duyệt; adapter tầng 3 trong test
  không chứng minh OCR/TX hoặc ba tầng thật đã chạy.
- **L-TC-01 / lead Hỏi AI:** test nối **consumer Hỏi AI hiện có + Local giả**
  xác nhận `khong_thay_can_cu/kiem_trich_dan.dat=false`; kiểm mọi lá metadata
  và văn bản theo khuôn như giá trị nguyên văn đang chặn đường này, như
  giới hạn TC-5 đã ghi. TC-7 giữ không căn cứ, không sửa response để qua
  cổng. Cần lead review phân biệt metadata/binding và giá trị nghiệp vụ;
  nhánh Local đạt trong harness là fixture **theo protocol**, chưa xác nhận
  đường consumer/model thật trả lời thành công. Không sửa engine Hỏi AI.
- **TC-Q14 đã duyệt:** đã cập nhật cùng bảng chọn duy nhất ở phiếu §5.2.
  Không phát sinh câu hỏi cần Anh; TC-Q06 tiếp tục không tự xóa. Không sửa
  `_chung/docs/LOAI-DU-LIEU-RIENG.md`, Core, SDK hoặc nguồn cũ.

## Biên bản bàn giao TC-7 — 15/11/2026

**Kết luận: Chưa đạt cổng chuẩn** — đã hoàn thành và kiểm phạm vi TC-7 bằng
Core giả; CLI chuẩn vẫn lỗi thiếu cấu hình/ngăn của SDK 2.0. PR: **chờ lead mở**.

**Đã làm:** đúng bốn tệp runtime `tra_loi.py`, `kiem_chung.py`, `bang_chung.py`,
`chay.py`. Hai đường Python/Local, kiểm snapshot/quyền/prompt/chuyển tiếp/băm,
quote/offset/nguồn/phiên bản/vị trí, từng trường/thực thể/giá trị/đơn vị/hiệu
lực. Không khớp một phần `5` trong `5.000.000`, không lấy số của khoản vay B
cho A. Tiền nguyên/Decimal kèm mã tiền tệ, ngày ISO, giữ mã số 0 đầu. Thiếu
căn cứ/sai quan hệ thì xóa câu đề xuất và khẳng định, trả câu không số/nhãn null.
Thiếu ngưỡng/duyệt/hiệu lực/trường có lý do để Core quyết tầng tiếp.

TC-Q14 áp theo quyết định chiều: chỉ Python tầng 1 đủ điều kiện Xanh, có
LLM/văn bản mới chờ duyệt tối đa Vàng. Mâu thuẫn hiện hành giữ hai nguồn/giá
trị và cờ cần duyệt; bản hết hiệu lực không giả thành mâu thuẫn hiện hành.
Xuất phụ thuộc nguồn/cache và đề nghị K5, không tạo cache/duyệt/K5, không
ghi đĩa hoặc tệp tạm. Sau upload báo tiến độ/kiểm hủy để không nộp khi Core
đã hủy. Nguồn lỗi/thiếu quyền/chưa rõ/mất lease/ACK sai không XONG giả.

**Kết quả kiểm thực:** Windows, Python 3.13.14, pytest 9.1.1; venv riêng
`--system-site-packages`, SDK 2.0.0 cài wheel offline, SHA-256 khớp
`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`.
Hai mẫu NGAN-0 và schema không đổi; bộ test so băm CRLF→LF chạy trong hồi quy.
Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_tra_cuu/goi/e_tra_cuu
[LỖI] Nhận DEMO — Phân loại: Engine chưa được cấu hình.
[LỖI] Nhận DEMO — Cắt đoạn: Engine chưa được cấu hình.
[LỖI] Nhận DEMO — Phân tích câu hỏi: Engine chưa được cấu hình.
[LỖI] Nhận DEMO — Xếp hạng lại: Engine chưa được cấu hình.
[LỖI] Nhận DEMO — Soạn trả lời tầng 1: Engine chưa được cấu hình.
Thông điệp đầy đủ chung: Engine chưa được cấu hình. Admin vào Quản lý engine › Tra cứu tài liệu › Cấu hình.
0/5 ĐẠT; 5 lỗi CHUA_CAU_HINH; mã thoát 1.

.venv/Scripts/python -B -m pytest e_tra_cuu/tests -q
952 passed in 21.65s
0 failed, 0 skipped; mã thoát 0 (814 hồi quy + 138 TC-7).

.venv/Scripts/python -B e_tra_cuu/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập; không import cấm, bytecode hoặc liên kết.
Mã thoát 0.

.venv/Scripts/python -B e_tra_cuu/tests/chay_demo_voi_core_gia.py
36/36 DEMO ĐẠT; mạng ngoài/lượt provider/Cloud=0 (không có provider trong harness).
Đã kiểm bằng Core giả (CoreGia); chưa chứng nhận quyền Core thật; ngăn RAM mất khi dừng.
Mã thoát 0 (28 ca nền + 8 ca TC-7).
```

138 ca TC-7 gồm hai đường/nhiều tầng giả, money/date/Decimal/số lớn/0 đầu,
quote bịa/offset Unicode/UTF-16/trang giả/trang có thật nhưng sai đoạn,
nhầm trường/thực thể/tiền tệ/đơn vị/tiền với tỷ lệ, chuyển ngày khai rõ,
chưa duyệt/hết hiệu lực/ngưỡng thấp/thiếu ngưỡng/ngoài trường, văn bản mới,
hai nguồn mâu thuẫn/AI giấu một bên, không căn cứ không số, metadata/Cloud/
hủy/mất lease/ChuaRo/ACK/gửi lại/quá trần, không ghi đĩa/mạng thật. Test
consumer Hỏi AI thật trong repo với Local **giả** được đếm riêng là ca từ
chối đúng, không là ca pipeline trả lời thành công. Toàn bộ **đã kiểm bằng
Core giả (CoreGia)**; chưa kiểm Linux/Core/RLS/model thật hoặc chất lượng
nghiệp vụ, không công bố ba tầng thật đã chạy.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** trong bốn tệp runtime, thêm lớp
bọc chuẩn bị AI tầng 1 vì TC-4 trước đó chỉ mở AI tầng 2/3. Chỉ Core cấp đủ
profile thì mới mở; không có profile vẫn từ chối như TC-4. Để kiểm chứng
được ngữ nghĩa, câu AI chỉ nhận mẫu xác định, chưa hỗ trợ diễn giải tự do.
Profile/binding/ngưỡng đo là seam C-TC-03 tạm cần Core review; ngăn vẫn dùng
mẫu nguyên trạng. Chi tiết tại `TC-7-KIEM-CHUNG.md` và README trong gói.
Không thêm dependency, không sửa nguồn cũ/Core/SDK/schema chung, không commit/push.

**Cần Core / Chờ Anh mới phát sinh:** cụ thể hóa C-TC-03/profile và nhánh AI
tầng 1; ghi giới hạn consumer Hỏi AI nêu trên. Không có quyết định mới chờ
Anh. Cổng CLI và quyền/ba tầng/K5/cache thật vẫn chờ C-TC-01…05/lead.

**Thời gian thực tế TC-7:** bắt đầu **15/11/2026 15:16**, kết thúc chốt
biên bản **15/11/2026 15:48:29 (UTC+07:00)**, khoảng **0.54 giờ**;
ước tính trong phiếu **5 giờ**. Đây là thời gian thực trong phiên, không phải
phép đo hiệu năng/model hoặc ước tính lại khối lượng triển khai thật.
