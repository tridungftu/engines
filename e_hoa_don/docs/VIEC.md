# VIỆC — danh sách việc duy nhất của project `e_hoa_don`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

Các dòng 0–5 giữ dấu vết phiếu cũ, không tự mở các lát mở rộng. Phần SDK 2.0 được giao trong HD-P chỉ gồm XML; điều kiện chờ Anh/Core theo phiếu giao mới.

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| 0 | Đọc `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` và `docs\YEU-CAU-VA-HIEN-TRANG.md`; lập kế hoạch lát có giờ ước tính; trình Anh | — | Chờ làm | Kế hoạch phải đối chiếu 3 yêu cầu bắt buộc |
| 1 | Xin Anh **quyết định cuối** cho phiếu (9 lát, 29 giờ công ước tính) | — | Chờ Anh |  |
| 2 | G3-GOI-25: nguồn Node bảng kê trong gói | HD-2 | Chờ Anh | Quyền chép nguồn |
| 3 | HD-CONG-BO: mẫu ZIP/bảng kê | HD-5 | Chờ Anh |  |
| 4 | HD-NOI-PHIEN, HD-WIN: phiên Windows/Chromium thật | HD-3, 4 | Chờ Anh | Tài khoản Windows |
| 5 | HD-NOI-CORE, HD-GIAO-DIEN, HD-SO-TIEN, G3-GOI-26, HD-TONG | HD-6…10 | Chờ làm |  |
| 6 | HD-P — Lập phiếu giao Codex SDK 2.0 cho phần đọc XML đã rõ | HD-P | Xong — 14/11/2026 | `GIAO-CODEX-e_hoa_don.md`: 5 lát HD-0…HD-4, tổng 15 giờ **ước tính**, chưa triển khai; ZIP/bảng kê/tải và thử máy thật **chờ Anh chốt**. Chỉ tài liệu, không tạo `goi/`, không sửa `ma-nguon/`. PR: **chờ lead mở**. |
| 7 | HD-0 — Khung SDK 2.0 + XML DEMO thật + kiểm độc lập | HD-0 | Xong — 14/11/2026 (mốc giao việc) | Kiểm thực tế 15/11/2026: SDK 1/1 DEMO ĐẠT, pytest 63 passed/0 skipped, kiểm độc lập mã 0; đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật. PR: **chờ lead mở**. |

HD-P không thay quyết định cuối của Anh cho phiếu 9 lát/29 giờ cũ. Bản giao mới dùng `hoa_don.doc_xml@2` vì đổi phong bì nhận/trả, không tự chuyển quy trình `@1`. Không cần thêm/đổi loại dữ liệu riêng: dùng `tep` → `truong` + tệp JSON chi tiết. Các câu Q1–Q8 và điều kiện mở lát tiếp theo ở `GIAO-CODEX-e_hoa_don.md` §5.2.

Kiểm HD-P ngày 14/11/2026: regex theo đầu bài trích đủ **5/5 khối lệnh §4**, dòng mở khối là ba backtick trơn; khớp 5 mã lát HD-0…HD-4 và tổng 4 + 3 + 3 + 3 + 2 = **15 giờ ước tính**; `git diff --check` mã 0, phạm vi đúng hai tệp tài liệu. Ba lệnh kiểm engine AGENTS.md §5 **không áp dụng** theo đầu bài chỉ tài liệu. Chưa chạy kiểm chức năng engine hoặc CoreGia trong HD-P; các lệnh kiểm trong phiếu là yêu cầu của lát tương lai.

## Cần Core (chuyển lead Core qua Anh)
- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

### Bổ sung HD-P — 14/11/2026

- Các dòng cổng ở trên là yêu cầu lịch sử; API v1/SDK 2.0.0 đã khóa theo bộ gửi engine hiện tại. Việc nối/vận hành Core thật chưa được kiểm trong HD-P. Không lấy mô tả socket/SDK cũ làm hợp đồng triển khai mới.
- Cấu hình máy: SDK đợt 1 chưa đưa `cau_hinh` cho engine; dùng lớp JSON ngoài gói theo `GIAO-CODEX-THU-TU.md` §2. XML thuần không cần cấu hình, không bị chặn vì thiếu tệp.
- Context nguồn/profile/company/raw binding: cần cửa chung do Core kiểm quyền theo pháp nhân; SDK hiện chỉ có `viec_id`, `buoc`, `phap_nhan_id`. Đợt XML truyền `context=None`, giữ lý do ứng viên và `can_kiem_tra=true`, không giả định danh/semantic digest hoặc đọc company từ cấu hình máy.
- Kho tệp và chuyển bản: SDK không cam kết `tep_id` là UUID. Gói XML dùng tham chiếu SDK; lead/Core giữ bản/quy trình `@1`, chuyển sang `@2` bằng khai báo khi được giao. Cần kiểm quyền tệp đầu vào/ra và lưu theo pháp nhân trên Core thật; CoreGia không thay bằng chứng này.
- Bí mật theo tên, ngăn engine/CAS, lượt bền #10 và trạng thái chờ nhập: chỉ chặn phần tải sau khi Anh chốt; không cần cho XML thuần. Không tự dựng pipe bí mật/socket/SQL để bù SDK, không lưu nội dung XML/cookie/profile vào sổ JSON tạm.
- Test cũ tham chiếu corpus/golden XML không nằm trong bộ mã nguồn hiện tại: cần lead bàn giao fixture DEMO có hash nếu yêu cầu chứng minh tương thích toàn bộ corpus. Đợt XML tự dựng DEMO có đáp án độc lập, không tuyên bố đã chạy golden cũ khi thiếu dữ liệu.

### Bàn giao HD-0 — mốc 14/11/2026, kiểm thực tế 15/11/2026

Kết luận: Đạt phạm vi HD-0 XML bằng Core giả (CoreGia), chưa nghiệm thu Core thật. Đúng 5 tệp runtime trong `goi/e_hoa_don/e_hoa_don/`; 18 trường SDK, một DEMO qua bộ đọc strict thật, cấu hình JSON ngoài gói và hai schema, README/CHANGELOG/NGUON/lock. Không sửa `ma-nguon/`, Core, SDK hay tài liệu API; không commit/push. PR: **chờ lead mở**; tiêu đề đề nghị `[e_hoa_don] HD-0 — Khung SDK 2.0 và XML DEMO`.

Kết quả thật trên Windows, Python 3.13.14 + SDK 2.0.0; ba lệnh đều dùng `-B`:

| Lệnh | Kết quả | Mã thoát |
|---|---|---:|
| `.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don` | 1/1 DEMO [ĐẠT] | 0 |
| `.venv\Scripts\python -B -m pytest e_hoa_don/tests -q` | 63 passed in 0.82s, 0 skipped | 0 |
| `.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py` | [ĐẠT] AST/lazy/dynamic, cây gói, import/DEMO trong tiến trình sạch | 0 |

QA thêm: schema Draft 2020-12 khớp báo cáo thật; wheel SDK đúng SHA phát hành. Không đọc cấu hình máy thật, mọi test cấu hình ở thư mục DEMO tạm; chặn network trong test. Pytest 9.1.1 dùng bản có sẵn, chép offline vào venv. Chưa chạy Linux, bài máy sạch HD-4, Core thật/quyền tệp theo pháp nhân hay corpus/golden cũ.

Thời gian thực tế: 0.243 giờ (00:55:00–01:09:33, 15/11/2026, UTC+07; ước tính trong phiếu: 4 giờ).

Lệch khỏi phiếu: không mở rộng phạm vi nghiệp vụ. Báo cáo thêm `van_de_phep_chieu` để giữ mã/locator vấn đề khi chiếu đầu hóa đơn/tiền, `chi_tiet_nguon` vẫn đúng `ra_json(InvoiceReadResult)`. Dùng quyết định tạm đã giao: JSON cấu hình ngoài gói; handler `context=None`, `can_kiem_tra=true`, định danh/semantic digest null; trần báo cáo 32 MiB là giới hạn đề xuất chưa đo trên corpus lớn.

Cần Core / Chờ Anh mới phát sinh: không có. Giữ các mục HD-P: context tin cậy, quyền tệp vào/ra và kênh cấu hình máy. Chưa nghiệm thu Core thật. ZIP/bảng kê/tải và chuyển quy trình `@1` không thuộc HD-0; không tự mở các lát đó.

Phần cũ không đưa vào gói để lead xét `LUU-TRU/` sau: vỏ `ma-nguon/chay.py` socket/SDKEngine/Bootstrap, vòng UUID/cấp tham chiếu và contract `.v1` cũ, bridge/shim/Core cũ; `tai.py`, `phien.py`, Node/portal/bảng kê/vendor chỉ tham chiếu cho phạm vi đang chờ. **Giữ nguyên toàn bộ tệp cũ, chưa chuyển hoặc xóa**.
