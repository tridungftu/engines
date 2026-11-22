# VIỆC — danh sách việc duy nhất của project `e_hoi_ai`

Trạng thái dùng một trong: **Chờ làm / Đang làm / Chờ Anh / Chờ Core / Xong** (ghi ngày và bằng chứng).

| # | Việc | Mã yêu cầu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| AI-12 | Tương thích khuôn TC bốn tác vụ và DC-6; tách metadata/giá trị trích | Lệnh lead 15/11/2026 17:08; AI-2 | Chờ Core — 15/11/2026 | Phần AI-12 đạt 5/5 fixture; pytest 637 passed, 0 skipped (63 ca AI-12); DEMO 3/3 + AI-9 1/1, độc lập mã 0, kiểm kê 27/27 khớp. CLI chuẩn 0/3 CHUA_CAU_HINH/mã 1, nợ AI-11. Đã kiểm bằng Core giả (CoreGia); đề xuất annotation ở sổ loại chung §8 chờ lead duyệt. PR: **chờ lead mở**. |
| AI-11 | Chuyển ngăn/cấu hình và gói sang SDK 2.2.0 | CHUYEN-SDK-2.2 §2, §4 | Chờ Core — 15/11/2026 | Phần chuyển đổi xong; đã kiểm bằng Core giả (CoreGia). Pytest 574 passed, 0 skipped; độc lập mã 0; kiểm kê SQL 26/26 khớp. CLI SDK thu 0/3, mã 1: thiếu cửa cấu hình DEMO/Local giả; không thay cổng nghiệm thu. PR: **chờ lead mở**. |
| AI-10 | Đóng nợ phân loại lỗi Local sau POST từ kiểm độc lập AI-9 | AI-8; AI-9 | Xong — 15/11/2026 | Đã kiểm bằng Core giả (CoreGia) và socket Local giả; pytest 568 passed, 0 skipped; DEMO 3/3 và AI-9 1/1, SDK thu qua cổng Local giả 3/3; kiểm độc lập đạt. CLI SDK thu độc lập 0/3 do thiếu cấu hình ngăn RAM. PR: **chờ lead mở**. |
| AI-8 | Cấu hình/model vào ngăn, màn Cổng Local AI/Cổng Cloud AI | AI-10, AI-11; quyết định 15/11 | Xong — 15/11/2026, đã kiểm bằng Core giả (CoreGia); đã nối ngăn chung NGAN-0 | pytest 370 passed, 0 skipped; SDK thu qua cổng DEMO 3/3; kiểm độc lập mã 0; so băm hai tệp chung đạt. PR: **chờ lead mở** |
| 0 | Đọc tài liệu bắt buộc; đối chiếu kế hoạch lát AI-0 đã giao | — | Xong — 14/11/2026 | Phạm vi, kiến trúc và cách triển khai theo `GIAO-CODEX-e_hoi_ai.md` và lệnh giao của Anh |
| 1 | Đóng gói độc lập theo cổng chung: bỏ shim, chỉ import SDK, build/cài wheel trên máy sạch | AI-13 | Đang làm — 14/11/2026 | Khung AI-0 xong; ghim đầy đủ và kiểm máy sạch thuộc AI-5 |
| 2 | Chạy thử DEMO khai trong phiếu; màn cấu hình/trạng thái Local/Cloud dùng cửa chung của Core | AI-10, 11, 12 | Đang làm — 14/11/2026 | AI-4 xong phần engine: ba DEMO đã kiểm bằng Core giả (CoreGia); màn chung/phân quyền Admin chờ nghiệm thu Core thật. Bản cũ chỉ tham chiếu ở `tu-core-cu\phia-core\` |
| 3 | Tự phát hiện model trên máy AI qua Tailscale, chọn theo module/function | AI-10 | Đang làm — 14/11/2026 | Lõi AI-3 xong, đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; thử máy AI/Tailscale thật thuộc AI-7, màn quản trị chờ Core |
| 4 | Lát 8: thử thật gpt-oss 20B, Qwen3 8B, Gemma; Local lỗi phải báo rõ, 0 Cloud | AI-14, AI-8 | Chờ làm | Công cụ ở `tu-core-cu\tools\` |
| 5 | Ghép Core khi có cổng chung K1–K5 → bài test cuối 40 phút | AI-18 | Chờ Core |  |
| 6 | Bản 2: công tắc Cloud theo module, qua Mask, đo độ chính xác, kiểm xác suất | AI-21…26 | Chờ (bản 2) |  |
| AI-0 | Khung SDK 2.0, phiếu 2 năng lực, schema chung, cấu hình máy và kiểm độc lập | AI-13 (phần khung) | Xong — 14/11/2026 (tiêu chí riêng AI-0) | Đã kiểm bằng Core giả (CoreGia); pytest 57 passed, 0 skipped; kiểm độc lập mã 0. Tại mốc AI-0 cổng DEMO chưa đạt; đã bổ sung ở AI-1. PR: **chờ lead mở** |
| AI-1 | Hỏi tài liệu chỉ Local, khung trích dẫn, hậu kiểm Python, lỗi/thử lại, hủy và chống nộp trùng | AI-1…5, 7, 8 | Xong — 14/11/2026 | Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; SDK thu 1/1 ĐẠT; pytest 141 passed, 0 skipped; kiểm độc lập mã 0; provider Cloud 0 lượt. Chưa chạy thực tế trên Linux/Core thật/model thật. PR: **chờ lead mở** |
| AI-2 | Hỏi theo yêu cầu, khuôn JSON, chuyển tiếp nguyên vẹn và trần byte | AI-3, 5; phục vụ TX-3 | Xong — 14/11/2026 | Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; SDK thu 1/1 ĐẠT; pytest 238 passed, 0 skipped (97 ca mới AI-2); kiểm độc lập mã 0; provider Cloud 0 lượt. Chưa kiểm thực tế Linux/Core thật/model thật. PR: **chờ lead mở** |
| AI-3 | Tự phát hiện API/model, cache 5 phút, chọn ưu tiên và dự phòng theo mã prompt | AI-10 | Xong — 14/11/2026 | Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; SDK thu 1/1 ĐẠT; pytest 176 passed, 0 skipped; kiểm độc lập mã 0; Cloud 0 lượt. PR: **chờ lead mở** |
| AI-6 | Tách provider và khung Cloud chưa khai phiếu | AI-21…24 (khung) | Xong — 14/11/2026 | Đã kiểm bằng Core giả (CoreGia); SDK thu 1/1 ĐẠT, pytest 334 passed, 0 skipped, độc lập mã 0. Cloud chỉ giả trong RAM, manifest giữ nguyên. PR: **chờ lead mở** |
| AI-4 | Ba DEMO, cổng Local giả gọi CoreGia và test tiến trình nhận stdin qua MayChuGia | AI-12, AI-18 (phần engine) | Xong — 14/11/2026; đã kiểm bằng Core giả | Cổng DEMO thay SDK thu: 3/3 ĐẠT; kiểm thêm SDK thu có Local giả 3/3 ĐẠT; pytest 283 passed, 0 skipped; kiểm độc lập mã 0; Cloud 0 lượt. Chưa kiểm Linux/Core thật/model thật. PR: **chờ lead mở** |
| AI-5 | Ghim ph? thu?c, ngu?n v? c?i m?y s?ch | AI-13 | ?ang l?m ? 14/11/2026 | Hai k?ch b?n offline ??t 3/3 DEMO tr?n Windows; workflow Linux ?? th?m, ch? lead push ?? CI ch?y. ?? ki?m b?ng Core gi? (CoreGia). PR: **ch? lead m?** |

| Gộp AI-2/AI-3 | Giải xung đột merge origin/main vào nhánh AI-2 | AI-2, AI-3 | Xong — 14/11/2026 | Gói 0.4.0; đã kiểm bằng Core giả (CoreGia); SDK thu 1/1 ĐẠT; pytest 278 passed, 0 skipped; độc lập mã 0. PR: chờ lead; nội dung đã giải xung đột, Git index chờ lead stage do quyền ghi |

| AI-7 | Công cụ thử Local thật bằng DEMO | AI-14, AI-8 | Đang làm — 14/11/2026 | Đã kiểm bằng Core giả (CoreGia), Local giả và mock; chưa có AI-4 trên nhánh, tạm dùng ca manifest AI-1; Anh tự chạy máy thật. PR: **chờ lead mở** |

| AI-9 | Nhận diện thực thể theo span chỉ Local, profile MASK-2c và transport theo trạng thái gửi | Sau AI-8; profile lead duyệt 15/11 | Xong phạm vi giả lập — 15/11/2026 | Đã kiểm bằng Core giả (CoreGia); 560 passed, 0 skipped; DEMO 3/3 cũ + 1/1 AI-9; SDK CLI độc lập 0/3 do thiếu cấu hình. Chưa đo model/Core thật. PR: **chờ lead mở** |

| UI-AI-2 | Cổng Cloud AI Tạm khóa; két metadata/CAS; nhật ký chờ Core | Phiếu UI §4 | Chờ Core — 22/11/2026; phần UI đã kiểm bằng Core giả (CoreGia) | PR: **chờ lead mở**. Không commit/push; chi tiết bàn giao ngay dưới. CLI chuẩn vẫn lỗi thiếu cấu hình DEMO có từ AI-11. |

### Bàn giao UI-AI-2 — 22/11/2026

**Kết luận:** Phần UI đã kiểm bằng Core giả (CoreGia); chưa đạt đầy đủ AGENTS.md §5 vì CLI SDK độc lập còn lỗi cấu hình DEMO từ AI-11. PR: **chờ lead mở**; nhánh `codex/e_hoi_ai-ui-ai-2`, không commit/push.

**Đã làm:** màn `ui/cloud.js` theo ảnh mẫu, Tạm khóa; provider/model/tỷ lệ kiểm/nút kiểm Cloud bị khóa. Két chỉ qua `.bi_mat` của `KttCore.engine('e_hoi_ai')`: đọc metadata, nhập password, lưu/xóa dùng CAS riêng tăng cả khi xóa; chỉ hiện bốn ký tự cuối. Xóa ô key ngay trước gửi; lỗi hoặc phản hồi chưa xác nhận đều khóa ghi đến tải lại. Không có nút hiện key, không lưu key vào cấu hình/ngăn/tệp/log. Thiếu cổng Core thì khóa két, không báo đã lưu giả.

Cho phép chuẩn bị key trong két nếu Core hỗ trợ, trong khi mọi đường gửi/kiểm Cloud vẫn khóa. Không cần thao tác Python quản trị Cloud. Nhật ký chưa có cửa Core nên khóa nút xem và nêu chưa xác minh lịch sử; không dựng số lượt hay danh sách rỗng giả. Không đổi `engine.json`, Python xử lý việc hoặc schema. Schema Local đã đủ title/description/examples mọi cấp từ UI-AI-1; thêm kiểm đệ quy bảo toàn. Vì manifest không đổi nên không cần sinh lại danh mục engine.

21 ca Node mới, tổng 45 ca Máy AI + Cloud: đọc/lưu/xóa, lỗi nhập/rỗng/quá trần, CAS lưu/xóa, lỗi đọc/ghi/thiếu API, metadata sai, chặn thao tác song song, không lộ bản rõ. Các nút kiểm thành công/thất bại của Máy AI giữ hồi quy; nút kiểm Cloud bị khóa, không giả lập thành công một lượt gửi Cloud.

Ảnh chụp Chrome headless dựng chính màn gói với KttCore giả, CSP chặn mạng: `docs/anh-ui-ai-2/cloud-ai-rong.png` (1160×1480), `cloud-ai-hep.png` (390×2100), `cloud-ai-loi.png`, `cloud-ai-cas.png`. Đã xem cả bốn ảnh; không tràn ngang. HTML DEMO tự chứa và kịch bản dựng/chụp ngoài gói, dựng lại bằng `node e_hoi_ai/tests/ui/chup_anh_cloud_demo.mjs`.

CHANGELOG/README/NGUON và kiểm kê 30 tệp được cập nhật. SDK 2.2.0 wheel offline có SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp SHA256SUMS. Phụ thuộc pytest đúng `tests/requirements.lock` được sao offline từ bản cùng phiên bản đã cài trên máy vào `.venv`; không thêm dependency chạy.

**Kết quả kiểm thực tế:** đã kiểm bằng Core giả (CoreGia), KttCore giả và Local HTTP giả; chưa kiểm Core thật/Cloud thật/model thật hoặc thực thi lại trên Linux. Trên PowerShell dùng `$env:PYTHONUTF8='1'` để in tiếng Việt và cờ `-B` giữ gói không có bytecode.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[LỖI] Hỏi số tiền và ngày thanh toán DEMO: Engine chưa được cấu hình.
[LỖI] Hỏi người bảo lãnh không có trong tài liệu DEMO: Engine chưa được cấu hình.
[LỖI] Trích tiền và ngày theo khuôn DEMO: Engine chưa được cấu hình.
=> 0/3 ĐẠT; CHUA_CAU_HINH; exit 1.

.venv/Scripts/python -B -m pytest e_hoi_ai/tests -q
=> 663 passed, 0 skipped in 184.51s (0:03:04); exit 0.

.venv/Scripts/python -B e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
=> exit 0.

node --test e_hoi_ai/tests/ui/cau_hinh.test.mjs e_hoi_ai/tests/ui/cloud.test.mjs
=> 45 passed, 0 failed, 0 skipped; exit 0.

.venv/Scripts/python -B e_hoi_ai/tests/chay_demo_voi_local_gia.py
=> 3/3 DEMO + 1/1 AI-9 ĐẠT; exit 0 (bổ sung, không thay CLI chuẩn).

node e_hoi_ai/tests/ui/chup_anh_cloud_demo.mjs
=> 4/4 ảnh rộng/hẹp/lỗi/CAS ĐẠT kiểm DOM, không tràn ngang; exit 0.

git diff --check
=> exit 0.
```

Lượt pytest đầu có 661 passed, 2 lỗi băm do tài liệu gói cập nhật khi đang kiểm; đã sinh lại NGUON/kiểm kê và chạy lại toàn bộ trên gói chốt. Không thêm skip.

**Lệch khỏi phiếu / quyết định tạm:** cửa F chưa có chữ ký SDK phát hành, hợp đồng metadata/CAS đề xuất trong KHAI chỉ kiểm bằng giả. Nhật ký chờ Core; không thêm bảng ngăn/route riêng hoặc máy giả vào runtime để làm xanh CLI. Schema đã đủ hướng dẫn nên không sửa dư thừa. Không phát sinh thao tác quản trị Python cho lát này.

**Cần Core / Chờ Anh mới phát sinh:** xem ba mục UI-AI-2 ngay dưới; không có câu hỏi mới chặn Anh. CLI thiếu cấu hình DEMO là nợ cũ.

**Thời gian thực tế:** 22/11/2026 07:02–07:20 (Asia/Saigon), khoảng 0,30 giờ; ước tính phiếu UI §4: 3 giờ.

## Cần Core (chuyển lead Core qua Anh)

- **UI-AI-2 — 22/11/2026:** cửa D nạp `ui/cloud.js` cho Admin Core; cửa F két theo tên `khoa_api_anthropic`, chỉ trả metadata và bốn ký tự cuối. Hợp đồng đề xuất `.bi_mat.trang_thai/.luu/.xoa`, CAS phiên bản riêng tăng cả khi xóa, lỗi 409 `BI_MAT_XUNG_DOT`, kiểm quyền/phạm vi engine và kiểm toán: xem `KHAI-SDK-2.1.json`. SDK 2.2.0 chưa cấp, không thêm vào engine.json. Thiếu cửa thì màn khóa thao tác, không báo đã lưu giả.
- **UI-AI-2 — nhật ký:** cần cửa đọc nhật ký gửi ra ngoài chung có quyền/pháp nhân, phân trang; chỉ metadata ngày, provider/model, kết quả/chi phí có đơn vị, không nội dung/key. Hiện khóa nút xem và báo chưa xác minh lịch sử, không tạo bảng riêng hoặc tự ghi sổ engine. Không phát sinh thao tác quản trị Python Cloud, không bật gọi Cloud.
- **UI-AI-2 — cổng kiểm chung:** CLI `python -m kho_tri_thuc_sdk.thu` vẫn tạo CoreGia mới không cấu hình Local DEMO, trả `CHUA_CAU_HINH` 0/3 như AI-11/UI-AI-1. Cần cửa cấu hình DEMO/Local giả được SDK hỗ trợ; không đổi SDK, handler hoặc manifest để báo xanh giả. Bộ `chay_demo_voi_local_gia.py` chỉ là bằng chứng bổ sung.

- **AI-9 — 15/11/2026:** cần cửa chung chứng thực nguồn `ai.hoi_mask_cuc_bo@1`/Local của từng phản hồi gắn đúng người/module/tài liệu/pháp nhân, yêu cầu và snapshot; không tin `nha_cung_cap`/băm caller tự khai. Core giữ bytes JSON chuẩn toàn yêu cầu để Mask kiểm `bam_dau_vao`; băm snapshot/profile/bản che phải đối chiếu bytes thật có quyền. AI-9 chỉ tái tính được prompt/khuôn/đoạn và gốc khi một đoạn; không tự tạo chứng cứ thay Core.
- **AI-9 — điều phối:** Core lập/ghim/lặp kế hoạch đoạn, overlap/đủ phủ, giữ mọi yêu cầu/phản hồi, ghép tập cuối và chứng thực phần thêm `tap_phan_hoi`; có deadline toàn chuỗi/hủy/mất lease/ChuaRo, không tự giao lại POST chưa rõ. Cần kho snapshot/tệp con với quyền mở xuyên bước và vòng đời tới khi hậu kiểm/chốt xong, cơ chế bền chống lặp/ACK qua SDK 2.1. Không viết route Core riêng hoặc coi CoreGia là nghiệm thu các quyền này.
- **AI-9 — trước dùng thật:** lead xác nhận server chạy model tại chỗ và chặn egress Cloud; private IP/metadata local không chứng minh server không chuyển tiếp. Cần đo tokenizer/context/đầu ra trên model thật; tạm AI-9 chỉ gửi khi server khai context đang dùng, byte budget bảo thủ còn đủ 8192 token đầu ra. Thiếu trường context ở server → từ chối trước gửi, không coi là đã đo sức chứa. Chưa đo chất lượng/0 lọt; thuộc MASK-2c-4. Cửa Cloud sau này phải kiểm chứng cứ hậu kiểm Mask gắn băm bản cuối và chặn đường lớp 1 cũ; Cloud vẫn tắt cứng.

- **AI-8 — 15/11/2026:** cần SDK 2.1 cấp `app.ngan`/`viec.ngan`, ngăn hệ thống cấu hình, schema/CAS và nạp màn module qua `KttCore.engine`. Khai dự kiến ở `goi/e_hoi_ai/KHAI-SDK-2.1.json`, không đổi manifest 2.0. Với SDK 2.0 chưa thể cấu hình/lưu bền qua Core thật; RAM khởi động lại sẽ rỗng.
- **AI-8 — đối chiếu NGAN-0: đã đóng ngày 15/11/2026.** Đã nối ngăn chung NGAN-0 sau PR #34; hai tệp mẫu trong gói giữ nguyên, test so băm chuẩn LF đã bật. `cau_hinh` khóa `{}` chứa trực tiếp cấu hình; `tim` trả `TrangNgan`, lô trả `KetQuaLenh`; không sửa `_chung/**`. Phần bảng chữ ký và quyết định tạm trong bàn giao AI-8 ban đầu bên dưới chỉ còn giá trị lịch sử; xem bàn giao nối ngăn ở cuối tệp.
- **AI-8 — màn quản trị:** Core cần xác nhận cách nạp ES module xuất hàm mặc định `(goc, KttCore)`. Trình duyệt giả dùng `cau_hinh.doc()` → `{cau_hinh, phien_ban_cau_hinh}`, `luu(gia_tri, phien_ban_cau_hinh)` → phiên bản mới; `ngan.tim(bang, {loc, gioi_han, tiep})`. Phần giá trị/phiên bản này chưa được đặc tả đầy đủ ở SDK trình duyệt phát hành; cần đối chiếu khi nối. Chưa có thao tác discovery quản trị nên màn chỉ hiện kết quả kiểm gần nhất khi xử lý việc.
- **AI-8 thay quyết định tạm cũ:** các mục AI-0…AI-3 dưới đây nói đọc JSON ngoài gói chỉ còn giá trị lịch sử; đường chạy hiện tại đã bỏ hoàn toàn cách đó.


- AI-6 (14/11/2026), bản 2: Core cần cấp bí mật theo tên trong `bi_mat[]` qua kênh bộ nhớ SDK; engine không tự đọc khóa từ env/tệp/đĩa. Cần công tắc Cloud theo từng module, mặc định tắt; **M9 và nhóm 07-Nhân sự luôn chỉ Local**. Cần điều phối Mask → Cloud → mở che, bảo đảm chỉ nội dung đã che ra ngoài. Không thêm năng lực/loại Cloud hoặc tên bí mật vào manifest ở AI-6.
- AI-6, bản 2: cần **ngăn dữ liệu engine** để giữ số đếm/độ chính xác Local theo function, lịch kiểm xác suất **20% → 10% → 5%**, không về 0; dưới 90% quay lại 20%. Chưa làm định tuyến hoặc đo thật ở lát khung này; giữ Cloud tắt đến khi có các cửa chung của Core và Mask.

- Cổng engine chung: API HTTP v1, webhook, bộ cài engine từ thư mục/gói riêng (bỏ tiền tố `kho_tri_thuc.engines.`), K1–K5.
- Màn Chạy thử chung và màn cấu hình dựng từ schema; nạp giao diện quản trị của engine.
- Gỡ mã riêng của engine này khỏi Core (danh sách: `_chung\docs\YEU-CAU-CHUNG-ENGINE.md` mục 9).

- AI-0 (14/11/2026): vẫn cần kênh `cau_hinh` từ `san-sang` tới hàm năng lực và form cấu hình từ schema theo `_chung/docs/GIAO-CODEX-THU-TU.md` §3. Chưa sửa phiếu/API/SDK đã khóa; tạm đọc JSON ngoài gói bằng `KTT_ENGINE_CAU_HINH`. Không phát sinh điểm chặn Core/SDK mới.
- AI-1 (14/11/2026): vẫn cần cấu hình và nhật ký kỹ thuật chung từ Core. Ghi nợ SDK chung: cho phép engine xác định mã lỗi khi thiếu tham số bắt buộc; áp trần nội dung văn bản bên trong loại riêng. Tạm giữ `prompt.bat_buoc=true` với sentinel `mac_dinh=""` để engine tự trả `THIEU_PROMPT`, và tự kiểm trần 500.000 ký tự cho `van_ban_tai_lieu.van_ban` cùng prompt. Không sửa hợp đồng SDK/API hoặc mã Core; không có điểm chặn mới.
- AI-2 (14/11/2026): không phát sinh yêu cầu Core/SDK mới. Tiếp tục tự kiểm phong bì loại riêng, trần byte khuôn/chuyển tiếp và trần prompt/tài liệu do SDK chưa kiểm sâu loại riêng. Tạm dùng cấu hình JSON ngoài gói như AI-1; không đổi schema chung hay API/SDK đã khóa.
- AI-3 (14/11/2026): không phát sinh yêu cầu Core/SDK mới. Tiếp tục dùng cấu hình JSON ngoài gói và nhật ký metadata như AI-0/AI-1. Catalog chỉ ở bộ nhớ; màn quản trị/catalog dùng chung chờ kênh cấu hình và thẻ trạng thái của Core. Phiếu gói bổ sung `ly_do_chon_model` trong `truong_ra` theo mẫu 2.0 hiện có, không thay hợp đồng SDK/API.
- AI-4 (14/11/2026): không phát sinh yêu cầu Core/SDK mới. Màn Chạy thử chung, quyền Admin, hàng việc/quyền pháp nhân/lịch sử và bài cuối 40 phút tiếp tục chờ Core thật. Cổng đạt riêng dùng `chay_demo_voi_local_gia.py` theo phiếu; `MayChuGia` chỉ kiểm HTTP loopback của SDK, không xác nhận vận hành Core thật.

## Bàn giao AI-0 — 14/11/2026

**Kết luận:** Đạt ba tiêu chí riêng AI-0 (phiếu hợp lệ, pytest xanh, kiểm độc lập mã 0). **Cổng DEMO chung theo AGENTS.md §5 chưa đạt** vì hai năng lực còn tạm trả `CHUA_LAM`; không công bố hỏi AI thành công.

**PR:** chờ lead mở. Nhánh: `codex/e_hoi_ai-ai-0`. Không commit/push.

### Đã làm

- Chép khung SDK từ `engine-demo/e_demo_dem_tu` vào `goi/e_hoi_ai/`; thay tên và bỏ nhánh import Core của mẫu. Chỉ 3 tệp Python chạy trong gói (`__init__.py`, `chay.py`, `cau_hinh_may.py`). Phiếu 2.0 phiên bản khung `0.1.0`: đúng hai năng lực, tham số prompt thuộc module, giới hạn 500.000 ký tự/600 giây, 1 việc đồng thời, không khai Cloud.
- Tạo ba schema Draft 2020-12 ở `_chung/contract/`, chép nguyên byte vào gói. Test so SHA-256 từng cặp. Có mô tả `dong`/`tu`/`nghi_ngo` tùy chọn, ô trống/ô gộp, schema trả lời và chuyển tiếp. Kiểm dung lượng UTF-8 32/64 KiB và quan hệ nghiệp vụ thuộc AI-2/các lát kiểm trích dẫn.
- Bộ đọc cấu hình ngoài gói có schema, chấp nhận UTF-8/BOM, không ghi lại cấu hình, thiếu tệp không làm engine chết; cấu hình sai/không đọc được chuyển thành lỗi nghiệp vụ an toàn. Từ chối tệp trong gói, trường lạ, số không hữu hạn, URL chứa thông tin đăng nhập/query/fragment.
- Bộ kiểm độc lập quét toàn bộ `goi/`, từ chối chuỗi Core bị cấm, bytecode, symlink/junction và mục không kiểm được; trả mã 0/1.
- Test sao gói ra ngoài repo, chạy Python `-I -S -B` chỉ thêm đường dẫn SDK cài trong venv và gói sao chép: đọc phiếu, thiếu cấu hình vẫn khởi động, sau đó đọc được cấu hình hợp lệ bằng schema trong gói.
- Không sửa `ma-nguon/`, gói SDK tham chiếu hoặc mã Core. Không chuyển/xóa tệp cũ. Không gọi mạng hay AI thật.

### Kết quả kiểm thật

Môi trường: Windows, Python 3.13.14, `.venv` trong worktree. SDK 2.0.0 cài từ wheel với `--no-index --no-deps`; SHA-256 trùng bản phát hành (`a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`). Venv dùng `--system-site-packages` để chạy pytest 9.1.1 đã có sẵn, không tải mạng. Gói chạy chỉ dùng SDK và thư viện chuẩn; test cách ly `-S` không nạp thư viện từ Python hệ thống. Chưa chạy bộ test trên Linux; các phần phụ thuộc symlink/junction được giả lập để test chạy đa nền tảng.

Đã đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; riêng pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
Phiếu chưa có ví dụ chay_thu_demo.
Mã thoát: 1; 0 ví dụ (không có ví dụ [ĐẠT]).

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
.........................................................                [100%]
57 passed in 0.84s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

`Engine.tu_khai_bao` đọc phiếu không lỗi (test riêng). CoreGia kiểm 3 dạng đầu vào của hai năng lực, cả 3 trả `LOI/CHUA_LAM`, không có kết quả. **Đã kiểm bằng Core giả (CoreGia)**; chưa kiểm Core thật hoặc model thật.

QA bổ sung bằng bộ kiểm `jsonschema` có sẵn trên máy phát triển: cả 4 schema hợp lệ Draft 2020-12; ba phong bì DEMO hợp lệ, ca sai phiên bản/loại bị bác. Thư viện này không phải phụ thuộc của gói/bộ pytest lưu trong repo.

### Lệch khỏi phiếu / quyết định tạm

- Theo phạm vi AI-0, giữ hai hàm tạm `CHUA_LAM`; `chay_thu_demo=[]`, nên SDK thu mã 1. Không tạo năng lực phụ hoặc giả kết quả thành công để làm xanh cổng chung. Các ví dụ hỏi AI và bộ chạy Local giả thuộc AI-4 theo phiếu giao.
- Dùng cấu hình JSON ngoài gói theo quyết định tạm của lead; chưa thêm trường cấu hình vào manifest 2.0 đã khóa. Phiên bản khung là `0.1.0`; chưa phát hành bản nghiệp vụ 1.0.0.
- Không có câu Chờ Anh mới phát sinh.

### Thời gian thực tế

Bắt đầu **14/11/2026 22:18** (theo lead); kết thúc kiểm và ghi bàn giao **14/11/2026 22:33:22 +07:00**: **0.26 giờ** (thời gian đồng hồ, gồm đọc tài liệu, dựng gói và kiểm). Ước tính trong phiếu AI-0: **2 giờ**.

## Bàn giao AI-1 — 14/11/2026

**Kết luận:** Đạt lát AI-1 và ba cổng kiểm trên môi trường Windows hiện có. **Đã kiểm bằng Core giả (CoreGia)** và máy Local HTTP giả trên loopback; chưa xác nhận thực tế trên Linux, Core thật hoặc model thật.

**PR:** chờ lead mở. Nhánh: `codex/e_hoi_ai-ai-1`. Tiêu đề đề nghị: `[e_hoi_ai] AI-1 — Hỏi tài liệu, chỉ Local`. Không chạy git commit/push.

### Đã làm

- Dùng lại khung AI-0. Chuyển phần lõi cần dùng từ `ma-nguon/lib/cong_ai.py`, `lib/ai_cuc_bo.py`, `dto.py`, `hoi.py` sang gói độc lập. Đúng 5 tệp Python chạy được thêm/sửa: `chay.py`, `cong_ai.py`, `ai_cuc_bo.py`, `dto.py`, `hoi.py`; không vượt cỡ lát. Gói phiên bản `0.2.0`.
- `ai.hoi_tai_lieu@1` nhận hai loại đầu vào đã khai; prompt thuộc module. Ghép khung bắt buộc trích nguyên văn, lấy câu trả lời từ trích dẫn; không có thông tin thì trả `không thấy căn cứ`.
- Kiểm Python: trích dẫn nằm đúng từng ký tự trong tài liệu, giá trị thuộc trích dẫn tương ứng, token số đầy đủ thuộc nguồn. Một mục không đạt thì hạ toàn bộ `co_can_cu=false`, trả cảnh báo cố định và không đưa câu trả lời bịa vào kết quả. Cảnh báo nằm trong `tra_loi` để giữ nguyên bốn trường đầu ra tĩnh; chỉ giữ câu trích đã kiểm hợp lệ.
- Local HTTP dùng IP trực tiếp, không DNS/proxy/redirect/HTTPS; chỉ loopback/RFC1918/Tailscale. Đích Tailscale phải có nguồn Tailscale và socket được ghim nguồn. Kiểm `/v1/models` cùng metadata Ollama `/api/tags` nếu có trước khi gửi nội dung; từ chối model từ xa/Cloud.
- Lấy URL và timeout từ `cau_hinh_may`; chọn model từ tham số ưu tiên hoặc quy tắc đầu tiên khớp mã prompt. Model thiếu/không sẵn sàng, lỗi mạng/HTTP, timeout, phản hồi hỏng hoặc vượt trần đều trả `LOCAL_AI_KHONG_SAN_SANG`, có thể thử lại. Chưa làm discovery/dự phòng thuộc AI-3.
- Báo tiến độ trước/sau Local, kiểm hủy trước mạng và giữa các lần đọc metadata. Lượt hủy không nộp kết quả. SDK xử lý mất xác nhận kết quả bằng cùng Idempotency-Key, không gọi AI lại, Core chỉ ghi một lần.
- Mỗi lượt ghi stderr đúng sáu metadata: mã/phiên bản prompt, model, lý do chọn, ms, kết quả kiểm; không ghi prompt, tài liệu, câu trả lời, URL hoặc nội dung lỗi nguồn.
- Test dùng Local HTTP giả trên `127.0.0.1`, CoreGia, provider Cloud giả có bộ đếm và hàng rào mạng: cấm DNS và mọi kết nối ngoài loopback. Các đường thành công, thiếu căn cứ, bịa dẫn chứng/số liệu, thiếu prompt, Local tắt/lỗi/model thiếu, hủy, gửi lại xác nhận đều có **0 lượt Cloud**.
- Ghi nguồn cũ → mới và SHA-256 trong `NGUON.md`; cập nhật README, CHANGELOG và phiếu DEMO tối thiểu. Chỉ SDK và thư viện chuẩn, không thêm dependency.

### Kết quả kiểm thật

Môi trường: Windows x64, Python 3.13.14, `.venv` trong worktree; SDK **2.0.0** cài bằng `--no-index --no-deps` từ wheel trong repo. SHA-256 wheel trùng `SHA256SUMS.txt`: `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Venv dùng `--system-site-packages` để dùng pytest 9.1.1 sẵn có; không tải mạng.

Đã đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
Chạy: python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
Engine e_hoi_ai 0.2.0: mọi ví dụ chạy thử DEMO đều đạt.
[ĐẠT] Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; 1 lượt Local.
Mã thoát: 0; SDK thu 1/1 ĐẠT.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
........................................................................ [ 51%]
.....................................................................    [100%]
141 passed in 5.11s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

Lệnh SDK được gọi thật trong tiến trình con với cấu hình DEMO ngoài gói và Local HTTP giả đang chạy; không đổi handler engine thành hàm giả. Các test hủy xác nhận `HUY` và không có kết quả; test `gay_mat_xac_nhan("ket_qua")` xác nhận hai lần gửi cùng khóa, **một lần ghi kết quả**, **một lần gọi Local**.

Giới hạn môi trường: không có WSL/Linux, Docker hoặc Podman; Git Bash không phải Linux. Bộ test không dùng API chỉ dành riêng Windows ở đường Local, nhưng **chưa chạy thực tế trên Linux**. Không chạy model/Local thật hoặc Core thật.

### Lệch khỏi phiếu / quyết định tạm đã dùng

- Đưa lên trước từ AI-4 **một ví dụ DEMO và bộ chạy Local giả tối thiểu** để cổng SDK thu có ca thật chạy và mã thoát 0 ngay ở AI-1. AI-4 vẫn làm bộ DEMO đầy đủ, HTTP Core giả và các phần còn lại theo phiếu.
- `prompt` có sentinel mặc định rỗng để SDK không chặn trường hợp thiếu bằng mã lỗi chung. Engine vẫn bắt buộc có nội dung prompt; không có prompt nghiệp vụ mặc định.
- Giữ và siết phép kiểm giá trị thuộc câu trích của mã cũ: không chấp nhận diễn giải ngoài nguyên văn. Đây là kiểm bằng quy tắc bảo thủ, chưa chứng minh suy luận ngữ nghĩa; câu đúng nhưng diễn đạt lại có thể bị hạ.
- Hủy giữa HTTP không cưỡng bức cắt socket đang chờ; SDK tiếp tục gia hạn/nhận cờ hủy, engine bỏ kết quả khi HTTP trả về hoặc hết timeout. Không chuyển Cloud.
- `ai.hoi_theo_yeu_cau@1` vẫn `CHUA_LAM`, đúng phạm vi AI-2. Chọn dự phòng/tự phát hiện model thuộc AI-3.
- Mã cũ `ma-nguon/chay.py`, `bi_mat.py`, phần Mask/Cloud/cấu hình Core cũ và chức năng chọn đối tác không đưa sang AI-1; giữ nguyên để lead quyết định chuyển `LUU-TRU/` sau các lát liên quan. Không sửa/xóa mã nguồn cũ, schema chung, tài liệu SDK hoặc mã Core.
- Cần Core/SDK đã ghi ở mục trên; không có câu Chờ Anh mới phát sinh. PR: **chờ lead mở**.

### Thời gian thực tế

Bắt đầu **14/11/2026 22:34** (theo lead); kết thúc kiểm và ghi bàn giao **14/11/2026 22:53:49 +07:00**: **0.33 giờ** (thời gian đồng hồ, gồm đọc tài liệu, chuyển lõi, test và bàn giao). Ước tính trong phiếu AI-1: **5 giờ**.

## Bàn giao AI-2 — 14/11/2026

**Kết luận:** Đạt lát AI-2 và ba cổng kiểm trên Windows/Python 3.13.14. **Đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả; chưa kiểm Core thật, model thật hoặc thực tế trên Linux.

**PR:** chờ lead mở. Nhánh: `codex/e_hoi_ai-ai-2`. Tiêu đề đề nghị: `[e_hoi_ai] AI-2 — Hỏi theo yêu cầu và khuôn trả lời`. Không chạy git commit/push.

### Đã làm

- Nối `ai.hoi_theo_yeu_cau@1`, nhận `yeu_cau_ai` và trả đủ `tra_loi_ai` theo schema chung; prompt thuộc yêu cầu, metadata nguồn gốc, băm phong bì đầu vào, vị trí trích dẫn và cảnh báo. Không sửa ba schema chung hoặc bản sao trong gói.
- Khi có khuôn, gửi schema phản hồi chung chứa `du_lieu` đúng khuôn module và `truong` chứa dẫn chứng AI-1. Ollama dùng `/api/chat` với `format`; OpenAI-compatible dùng `response_format` kiểu `json_schema`. `$ref` nội bộ được chuyển gốc khi bọc, không thay khuôn gốc. Không khuôn thì `du_lieu=null`.
- Bộ kiểm JSON Schema tối thiểu tự viết, offline, chỉ dùng thư viện chuẩn; hỗ trợ cấu trúc lồng, kiểu, required, enum/const, giới hạn object/array/string/number, tổ hợp và `$ref` nội bộ không vòng. Từ khóa chưa hỗ trợ (`pattern`, `format`, `unevaluatedProperties`...), reference ngoài và vòng tham chiếu bị từ chối trước mạng; tập hỗ trợ và giới hạn ghi rõ trong README. Sai khuôn hỏi lại đúng một lần, vẫn sai trả `AI_TRA_SAI_KHUON`.
- Giữ nguyên `chuyen_tiep` bằng so byte JSON chuẩn hóa; không gửi trường này sang Local hoặc nhật ký. Kiểm biên UTF-8 đúng 64 KiB/32 KiB và vượt một byte; vượt trần từ chối, không cắt ngầm.
- Giữ hậu kiểm trích dẫn/số từ AI-1, thêm kiểm giá trị trong `du_lieu` có căn cứ. Dữ liệu đúng khuôn nhưng sai dẫn chứng bị hạ trạng thái kèm cảnh báo; dữ liệu giữ khuôn để bước sau xét `kiem_trich_dan` và `trang_thai`.
- Thiếu prompt, Local lỗi, hủy, gửi lại kết quả và nhật ký metadata theo AI-1; 0 lượt provider Cloud ở mọi ca Local HTTP của AI-2. Test chặn DNS/mạng ngoài, model remote và redirect native Ollama.
- Đúng **5 tệp Python chạy** thêm/sửa: `chay.py`, `cong_ai.py`, `ai_cuc_bo.py`, `hoi_yeu_cau.py`, `khuon_json.py`. `chay.py` chỉ thêm import và nối handler; `engine.json` chỉ tăng phiên bản gói `0.2.0` → `0.3.0`. Không sửa mã nguồn cũ, cấu hình/model lựa chọn của AI-3 hoặc Core.

### Kết quả kiểm thật

Môi trường `.venv` trong worktree, Python 3.13.14; SDK 2.0.0 cài từ wheel bằng `--no-index --no-deps`, SHA-256 khớp `SHA256SUMS.txt`. Venv dùng `--system-site-packages` cho pytest 9.1.1 đã có sẵn; không tải mạng. Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
Chạy nguyên lệnh trong tiến trình con:
  python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
Engine e_hoi_ai 0.3.0: mọi ví dụ chạy thử DEMO đều đạt.
[ĐẠT] Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; 1 lượt Local.
Mã thoát: 0; 1/1 ĐẠT.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
238 passed in 11.65s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

97 ca mới AI-2; SDK DEMO 1 ca kế thừa AI-1, không thay handler bằng hàm giả. QA riêng bằng `Draft202012Validator` sẵn trên máy phát triển: 656 cặp schema/dữ liệu khớp bộ kiểm độc lập; hai kết quả thực có/không khuôn qua Local giả + CoreGia hợp lệ contract `_chung/contract/tra_loi_ai.schema.json`. Công cụ QA không phải phụ thuộc của gói hoặc pytest lưu trong repo. `git diff --check` không lỗi.

### Lệch khỏi phiếu / quyết định tạm đã dùng

- Không đổi phạm vi AI-2. Chọn bộ kiểm tối thiểu tự viết theo phương án được phiếu cho phép; không công bố hỗ trợ toàn bộ Draft 2020-12. Khuôn chỉ nhận kiểu ngoài object không thể tạo `du_lieu` hợp lệ với contract chung; vẫn kiểm và báo `AI_TRA_SAI_KHUON` sau một lần hỏi lại.
- Bọc khuôn module trong phản hồi có dẫn chứng để giữ quy tắc AI-1; chỉ dữ liệu ở `du_lieu` phải đúng khuôn module. Trích dẫn luôn được kiểm kể cả khi `bat_buoc_trich_dan=false`, theo quyết định bản 1. Kiểm giá trị có kiểu chỉ chuẩn hóa tiền nhóm nghìn và ngày; phép kiểm bảo thủ có thể hạ kết quả diễn giải đúng về nghĩa.
- Tiếp tục dùng JSON cấu hình ngoài gói như quyết định tạm AI-1. Không thêm thư viện runtime; nguồn và SHA-256 đã cập nhật trong `NGUON.md`.
- Điểm cần giữ khi gộp AI-3: `CongAI.chon_model` không bị sửa; provider Local có thêm tham số tùy chọn `khuon`; `_kiem_model` trả `"ollama"` khi xác minh được metadata Ollama để chọn endpoint structured output. AI-3 có thể dùng kết quả discovery thay giá trị trả này khi gộp.
- Cần Core / Chờ Anh mới phát sinh: **không**. Không xóa hoặc chuyển lưu trữ tệp nào.

### Thời gian thực tế

Bắt đầu **14/11/2026 22:55** (theo lead); kết thúc kiểm và ghi bàn giao **14/11/2026 23:12:09 +0700**: **0.29 giờ** (thời gian đồng hồ). Ước tính trong phiếu AI-2: **4 giờ**.

## Bàn giao AI-3 — 14/11/2026

**Kết luận: Đạt** lát AI-3 và ba cổng kiểm trên Windows. **Đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả trên loopback; chưa kiểm Linux, Core thật hoặc model thật.

**PR:** chờ lead mở. Nhánh `codex/e_hoi_ai-ai-3`, dựng trên AI-1. Tiêu đề đề nghị: `[e_hoi_ai] AI-3 — Tự phát hiện và chọn model Local`. Không chạy git commit/push.

### Đã làm

- Viết `chon_model.py` riêng: probe cùng IP/cổng theo thứ tự `/api/tags` → `/api/v1/models` → `/api/v0/models` → `/v1/models`, kiểm cấu trúc và giữ nguyên ID/thứ tự nguồn. Loại phần mềm tương ứng `ollama`, `lm_studio`, `openai_compatible`; không suy loại từ tên/cổng, không ghim tên hoặc xếp hạng chất lượng model.
- Catalog bất biến trong bộ nhớ 300 giây theo URL gốc, tối đa 64 endpoint, không lưu đĩa. Lỗi discovery trả `None`, không cache lỗi; lượt hỏi không có model nhận `LOCAL_AI_KHONG_SAN_SANG`, `thu_lai_duoc=true`. Không gọi discovery lúc khởi động.
- Chọn mỗi lượt: tham số `model_uu_tien` khả dụng → duyệt các quy tắc khớp `ma_prompt` theo thứ tự cấu hình, xét `uu_tien` rồi `du_phong` → model khả dụng đầu tiên theo danh sách nguồn. Kết quả và log có lý do chọn.
- Metadata mới được đọc từ API đã nhận diện trước chọn và trước POST; không kéo dài TTL discovery. Model biến mất giữa hai lượt được bỏ qua ngay khi cache còn hạn; biến mất sau khi chọn thì từ chối trước gửi nội dung, không tự gửi lại POST. API cũ lỗi thì phát hiện lại. Catalog rỗng hợp lệ không rơi xuống API khác. Loại model từ xa, không phải LLM hoặc metadata chỉ rõ chưa tải.
- Dùng lại toàn bộ rào IP/LAN/Tailscale, chặn DNS/proxy/redirect, trần phản hồi và kiểm hủy từ AI-1. Không đổi cấu hình chung theo model được chọn; không thêm thư viện.
- Đúng 5 tệp Python chạy được thêm/sửa: `chon_model.py`, `ai_cuc_bo.py`, `cong_ai.py`, `dto.py`, `hoi.py`. `chay.py` không sửa, `hoi.py` chỉ thay hai dòng để báo tiến độ trước discovery và truyền kiểm hủy. AI-2 dùng lại `CongAI.chon_model(..., kiem_huy=...)`; lớp `KetQuaAI` vốn đã có `ly_do_chon_model`.
- Bổ sung `ly_do_chon_model` vào đầu ra hỏi tài liệu và `truong_ra` của phiếu gói; phiên bản `0.3.0`. Cập nhật README, CHANGELOG, nguồn và SHA-256. Không sửa mã cũ, Core, schema chung hoặc bộ SDK tham chiếu.

### Kết quả kiểm thật

Môi trường: `.venv` trong worktree, Windows/Python 3.13.14; SDK 2.0.0 cài từ wheel trong repo bằng `--no-index --no-deps`. SHA-256 wheel trùng `SHA256SUMS.txt`: `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Venv dùng `--system-site-packages` để dùng pytest 9.1.1 có sẵn; không tải mạng.

Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
Chạy: python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
Engine e_hoi_ai 0.3.0: mọi ví dụ chạy thử DEMO đều đạt.
[ĐẠT] Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; 1 lượt Local.
Mã thoát: 0; SDK thu 1/1 ĐẠT.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
........................................................................ [ 40%]
........................................................................ [ 81%]
................................                                         [100%]
176 passed in 29.50s
Mã thoát: 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

Lệnh SDK thu chạy thật trong tiến trình con với Local HTTP giả và cấu hình DEMO ngoài gói, giữ nguyên handler engine. 35 test mới (AI-1 có 141 → AI-3 có 176): từng kiểu API/native v0, cache và TTL, cách ly endpoint, lỗi metadata/trần phản hồi và phục hồi, ưu tiên/dự phòng/wildcard/không khớp, model biến mất giữa lượt và trước POST, đổi API, remote/embedding/chưa tải, metadata trùng, hủy, không DNS/redirect và 0 lượt Cloud. Các test AI-1 tiếp tục đạt. `git diff --check` không lỗi.

### Lệch khỏi phiếu / quyết định tạm đã dùng

- Cache catalog/loại API 5 phút nhưng vẫn đọc metadata mới mỗi lượt và trước POST. Trade-off: thêm GET để xác nhận khả dụng, tránh dùng model đã biến mất trong cửa sổ cache; không gửi tài liệu ở các GET.
- Thêm trường tĩnh `ly_do_chon_model` vào phiếu gói để Core nhận được lý do chọn theo yêu cầu AI-3; bốn trường cũ giữ nguyên. Không sửa hợp đồng API/SDK 2.0 đã khóa. Lead lưu ý khi gộp phiếu phiên bản với AI-2.
- Cấu hình JSON ngoài gói và nhật ký stderr theo quyết định tạm hiện có. Không mở rộng `ai.hoi_theo_yeu_cau@1` ở nhánh này (thuộc AI-2).
- Cần Core / Chờ Anh mới phát sinh: không có. Chưa chạy model thật, Tailscale thật, Linux hoặc Core thật; việc thử máy thật thuộc AI-7.

### Thời gian thực tế

Bắt đầu **14/11/2026 22:55** (theo lead); kết thúc kiểm và ghi bàn giao **14/11/2026 23:06:29 +07:00**: **0.19 giờ** (11 phút 29 giây, thời gian đồng hồ). Ước tính trong phiếu AI-3: **3 giờ**.

## Bàn giao AI-7 — 14/11/2026

**Kết luận: Chưa đạt đầy đủ:** công cụ đã có và được kiểm giả lập; ca DEMO AI-4 chưa có trên nhánh AI-3 nên tạm dùng ca hiện có trong manifest. Chưa chạy Local thật. PR: **chờ lead mở**.

- Đã làm: công cụ mặc định chạy khô; `--that --url` mới kết nối Local, thử từng model phát hiện, so đáp án, kiểm trích dẫn, ghi thời gian và JSON vào thư mục chạy. Ca Local tắt được giả lập qua provider; đếm Cloud bằng provider khóa. Có CMD ASCII và hướng dẫn 5 dòng. Không sửa gói hoặc chạy model thật.
- Kiểm: SDK thu trực tiếp thiếu cấu hình → 0/1 ĐẠT, mã 1; cùng lệnh qua bộ chạy Core giả (CoreGia) và Local HTTP giả → 1/1 ĐẠT, mã 0. Pytest 176 passed, 0 skipped; kiểm độc lập mã 0. Công cụ: 4 test mock đạt, không gọi mạng.
- Lệch phiếu: bộ AI-4 chưa hiện diện; phải đối chiếu/chuyển sang ca AI-4 sau khi gộp. Ca Local tắt hiện là giả lập, không chứng minh tình huống máy thật ngừng hoạt động. Không phát sinh yêu cầu Core/SDK mới.
- Ước tính AI-7: 2 giờ; bắt đầu 14/11/2026 23:07 theo lead. Kết thúc 14/11/2026 23:11:30; thời gian thực tế 0,075 giờ (4 phút 30 giây).
## Bàn giao việc gộp AI-2/AI-3 — 14/11/2026

Kết luận: **Đạt** — đã giải năm tệp xung đột, giữ đủ hành vi và test hai lát. **Đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả trên Windows/Python 3.13.14; chưa kiểm Linux/Core thật/model thật.

Đã làm: giữ `chon_model.py`, catalog/cache 300 giây, ưu tiên/dự phòng, lý do chọn và bảo vệ mạng AI-3; giữ toàn bộ khuôn, hỏi lại một lần, hậu kiểm và chuyển tiếp AI-2. `_kiem_model` trả `catalog.loai` từ lần kiểm khả dụng trước POST, không thêm GET để chọn khuôn. Truyền kiểm hủy vào discovery của luồng AI-2. Hợp nhất đầy đủ hai bản bàn giao, README/CHANGELOG/NGUON; tăng minor từ hai bản 0.3.0 lên 0.4.0; bổ sung SHA-256 hiện tại và giữ các mốc băm cũ làm lịch sử.

Kết quả kiểm (đặt PATH dùng `.venv/Scripts`, `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`):

```text
python e_hoi_ai/tests/chay_demo_voi_local_gia.py
SDK thu: 1/1 ĐẠT, engine e_hoi_ai 0.4.0; 1 lượt Local; mã thoát 0.

python -m pytest e_hoi_ai/tests -q
278 passed in 34.16s; 0 skipped; mã thoát 0.

python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.
```

Giữ mọi hàm test AI-2/AI-3, xác minh bằng đối chiếu AST với HEAD/MERGE_HEAD; giữ nguyên byte nội dung hai bản bàn giao trong VIEC. Năm ca mới kiểm đủ bốn API (Ollama, LM Studio v1/v0, OpenAI-compatible), khuôn và dự phòng/lý do chọn, cache không dò thêm API chọn khuôn, hủy discovery trước gửi nội dung; hàng rào mạng/DNS và bộ đếm Cloud tiếp tục có hiệu lực. Không có test bị bỏ qua.

Thời gian thực tế: khoảng **0.13 giờ (8 phút)** thời gian đồng hồ cho việc gộp và kiểm; không có ước tính riêng cho việc gộp (phiếu gốc: AI-2 4 giờ, AI-3 3 giờ).

Lệch khỏi phiếu / quyết định tạm đã dùng: không đổi phạm vi nghiệp vụ; tiếp tục cấu hình JSON ngoài gói. Test hủy mới giả tín hiệu SDK đã nhận để tránh phụ thuộc lịch luồng gia hạn của CoreGia. Không thêm thư viện, không sửa Core/SDK hay các thay đổi OCR đi kèm merge. PR: **chờ lead**; nhánh `codex/e_hoi_ai-ai-2`. Không chạy git commit, merge --continue hoặc push; lead hoàn tất merge.

Cần Core / Chờ Anh mới phát sinh: **không**.

Lưu ý Git index: `git add` bị từ chối quyền ghi vì index worktree nằm ngoài writable root; năm tệp vẫn hiện `UU` trong index dù nội dung đã sạch dấu merge. Lead cần stage năm tệp xung đột cùng `hoi_yeu_cau.py`, `engine.json`, `tests/test_hoi_yeu_cau.py`, rồi tự hoàn tất merge. Không dùng index thay thế hoặc thay đổi quyền.


## Bàn giao AI-6 — 14/11/2026

Kết luận: **Đạt** lát khung Cloud; đã kiểm bằng Core giả (CoreGia), Local HTTP giả và Cloud giả trong bộ nhớ trên Windows/Python 3.13.14. Chưa kiểm Linux, Core thật hoặc model/API Cloud thật.

PR: **chờ lead mở**. Nhánh `codex/e_hoi_ai-ai-6`; tiêu đề đề nghị: `[e_hoi_ai] AI-6 — Khung Cloud và seam nhà cung cấp`. Không chạy git commit/push.

Đã làm:
- Đúng 3 tệp mã chạy thêm/sửa: `nha_cung_cap.py`, `cloud.py`, `cong_ai.py`. Chuyển Local sang mô-đun provider, giữ import tương thích; hai năng lực chỉ dùng khóa provider `local`. Cloud Anthropic/OpenAI nhận khóa qua constructor, không đọc env/tệp/đĩa để lấy khóa; HTTPS host cố định, không proxy/redirect/retry.
- `BAT_CLOUD = False` cố định; cả `hoi_cloud` và provider chặn khi tắt. Test kiểm literal cờ, env không bật được Cloud, và chặn cả khởi tạo/gọi NhaCungCapCloud trong bộ test hai năng lực (kể cả sai khuôn/hỏi lại, thiếu prompt, lỗi Local, hủy, gửi lại kết quả).
- Chỉ phong bì đã che phiên bản 1, con_sot phải là list rỗng, kiem_tien_ngay phải đúng boolean true; thiếu/sai trường từ chối. Văn bản/model chứa mã mở che bị từ chối; trần 500.000 ký tự, chuyển tiếp 64 KiB tính cả mã mở che, vượt thì không cắt ngầm. Chỉ văn bản đã che đi ra ngoài; ma_yeu_cau và metadata không ra payload. Kết quả chép ma_yeu_cau vào chuyen_tiep, không sửa đầu vào, hậu kiểm trích dẫn bằng lõi hiện có.
- 56 test mới chỉ Cloud giả trong RAM, chặn socket/DNS; kiểm payload hai API, không đọc env/tệp, metadata/chuyển tiếp, mã xung đột, biên 64 KiB, không căn cứ/trích dẫn bịa, cắt token/từ chối, hủy, mất phản hồi/202 thành ChuaRo, HTTP/redirect/trần phản hồi. Transport HTTPS cũng kiểm bằng đối tượng giả trong bộ nhớ, không dựng Cloud server hoặc gọi mạng ngoài.
- Giữ nguyên byte engine.json và chay_thu_demo; không thêm thư viện, không sửa ma-nguon/Core/SDK, không xóa tệp. README/CHANGELOG/NGUON ghi nguồn và băm các tệp gói đổi/thêm.

Kết quả kiểm thật: SDK 2.0.0 cài từ wheel repo bằng --no-index --no-deps, SHA-256 khớp SHA256SUMS.txt. Venv trong worktree dùng --system-site-packages cho pytest 9.1.1 có sẵn, không tải mạng. Đặt PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1.

```text
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
Chạy nguyên lệnh trong tiến trình con:
  python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
Engine e_hoi_ai 0.4.0: mọi ví dụ chạy thử DEMO đều đạt.
[ĐẠT] Đã kiểm bằng Core giả (CoreGia) và Local HTTP giả; 1 lượt Local.
Mã thoát 0; 1/1 ĐẠT.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
334 passed in 34.75s
Mã thoát 0; 0 skipped.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.
```

Lệch khỏi phiếu / quyết định tạm đã dùng: không đổi phạm vi; giữ manifest 0.4.0 theo chỉ đạo không sửa engine.json khi AI-4 đang chạy song song. SDK thu được chạy nguyên lệnh qua runner Local giả kế thừa AI-1, không thay handler. Khung Cloud không nhận prompt thô riêng: yêu cầu và dữ liệu phải nằm trong văn bản đã qua Mask. Chưa nối khuôn động/định tuyến/đo độ chính xác Cloud, chưa bật Cloud vận hành. Giữ mốc API Anthropic từ nguồn cũ, bỏ tùy chọn beta/fallback và danh sách model cũ; tương thích API/model thật cần xác minh ở bản 2.

Cần Core / Chờ Anh mới phát sinh: không có điểm chặn mới. Đã ghi rõ nợ bản 2 ở mục Cần Core: bi_mat[], công tắc module mặc định tắt (M9 và nhóm 07 luôn Local), Mask/mở che và ngăn dữ liệu để đo độ chính xác theo function + lịch kiểm 20%→10%→5%, dưới 90% trở lại 20%. Không có câu Chờ Anh mới.

Thời gian thực tế: bắt đầu **14/11/2026 23:23** (theo lead), kết thúc **14/11/2026 23:32:37 +0700**, **0.16 giờ** thời gian đồng hồ; ước tính trong phiếu AI-6: **3 giờ**.
## Bàn giao AI-4 — 14/11/2026

Kết luận: **Đạt** — đã kiểm bằng Core giả (CoreGia), Local HTTP giả và MayChuGia trên Windows/Python 3.13.14. Chưa kiểm thực tế Linux/Core thật/model thật.

Đã làm:

- Mở rộng một DEMO AI-1 thành ba ví dụ `chay_thu_demo`: hỏi tiền/ngày có trích dẫn; hỏi người bảo lãnh không có đáp án; hỏi theo yêu cầu có khuôn. Tất cả dùng hợp đồng GIẢ DEMO-001 của Công ty DEMO Ánh Dương, 1.000.000 VND, 30/10/2026. Dữ liệu có kiểu tiền kèm `VND`, ngày `2026-10-30`.
- Bộ chạy bật Local giả trên cổng loopback động, tạo cấu hình DEMO dưới `tests/ktt-ai-4-demo-*/`, đặt `KTT_ENGINE_CAU_HINH`, gọi trực tiếp `CoreGia().chay_thu_demo(app)` bằng handler thật. Mã 0 chỉ khi bộ ví dụ khác rỗng, mọi ví dụ XONG và số lượt Local khớp. Dọn cấu hình tạm, khôi phục biến môi trường sau kiểm. README nêu đây là cổng đạt thay lệnh SDK thu riêng không cấp máy AI.
- Thêm 5 ca pytest: đối chiếu toàn bộ đáp án/khuôn/trích dẫn/chuyển tiếp; ba ca cổng đạt/lỗi/rỗng và cấu hình tạm; một ca tiến trình thật nhận dòng JSON stdin qua MayChuGia HTTP loopback cho cả hai năng lực. Kiểm xác thực/instance, đọc đầu vào HTTP, nộp kết quả trước kết thúc, khóa chống trùng và 0 Cloud. Khóa test sinh ngẫu nhiên lúc chạy, không ghi vào mã/phiếu/log.
- Chỉ sửa `engine.json.chay_thu_demo`, tests, README, CHANGELOG và tài liệu. Không sửa lõi AI/Cloud, Core/SDK hoặc mã nguồn cũ; không thêm thư viện. PR: **chờ lead mở**; nhánh `codex/e_hoi_ai-ai-4`; không commit/push.

Kết quả kiểm thật:

`.venv` trong worktree, tạo bằng `--system-site-packages` để dùng pytest 9.1.1 có sẵn. SDK 2.0.0 cài bằng `--no-index --no-deps` từ wheel trong repo, SHA-256 khớp `SHA256SUMS.txt`. Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
[ĐẠT] Hỏi người bảo lãnh không có trong tài liệu DEMO
[ĐẠT] Trích tiền và ngày theo khuôn DEMO
[ĐẠT] Đã kiểm bằng Core giả (CoreGia); 3/3 DEMO, 3 lượt Local HTTP giả.
Mã thoát: 0.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
283 passed in 39.12s
Mã thoát: 0; 0 skipped (278 ca nền + 5 ca AI-4).

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát: 0.
```

Kiểm thêm đúng lệnh gốc AGENTS.md §5 trong tiến trình con với LocalGia, ba phản hồi DEMO và cấu hình tạm dưới tests được cấp trước:

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
[ĐẠT] Hỏi người bảo lãnh không có trong tài liệu DEMO
[ĐẠT] Trích tiền và ngày theo khuôn DEMO
Engine e_hoi_ai 0.4.0: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát: 0; 3 lượt Local HTTP giả.
```

`git diff --check` không lỗi. Gói không có bytecode/liên kết; mọi dữ liệu kiểm là DEMO.

Thời gian thực tế: bắt đầu **14/11/2026 23:23** theo lead; kết thúc **14/11/2026 23:31 +07:00** (đến phút): **0.13 giờ** thời gian đồng hồ. Ước tính trong phiếu AI-4: **3 giờ**.

Lệch khỏi phiếu / quyết định tạm đã dùng: không đổi phạm vi; tiếp tục cấu hình JSON ngoài gói theo quyết định tạm. Cấu hình sinh dưới thư mục tạm trong tests để dùng cổng động, tránh ghim cổng hoặc chạm cấu hình máy thật. Phiên bản gói giữ 0.4.0; chỉ đổi dữ liệu DEMO, test và tài liệu.

Cần Core / Chờ Anh mới phát sinh: **không**. Các phụ thuộc Core thật giữ như mục Cần Core.

## B?n giao AI-5 ? 14/11/2026

K?t lu?n: **Ch?a ??t ??y ??** ? ?? ki?m b?ng Core gi? (CoreGia); workflow Linux ?? khai b?o nh?ng ch?a ch?y CI th?c t? v? lead s? push v? m? PR.

?? l?m: `requirements.lock` ghi ch? d?ng th? vi?n chu?n, SDK 2.0.0 c?i ri?ng t? wheel; `NGUON.md` ghi ngu?n m? c? v? SHA-256 hi?n t?i c?a c?c t?p c?n l?i trong g?i (kh?ng t? b?m). Hai k?ch b?n ASCII t?o venv m?i, c?i offline r?i ch?y DEMO; workflow CI ch?y b?n `.sh`. Kh?ng c? Cloud AI-6 trong worktree n?y.

K?t qu? ki?m tr?n Windows/Python 3.13: SDK wheel SHA-256 kh?p `SHA256SUMS.txt`; SDK thu v?i Local HTTP gi? 3/3 ??T, m? 0; pytest 283 passed, 0 skipped; `kiem_doc_lap.py` ??T, m? 0. C? `.sh` (Git Bash) v? `.cmd` ??t 3/3 DEMO, m? 0. Ch?a ch?y Linux/CI th?c t?. G?i s?ch bytecode.

Th?i gian: b?t ??u 14/11/2026 23:34 theo lead; k?t th?c kho?ng 23:37 (+07:00), kho?ng 0,05 gi?; phi?u ??c t?nh 2 gi?. PR: **ch? lead m?**.

L?ch kh?i phi?u / quy?t ??nh t?m: `.sh` ?? ki?m b?ng Git Bash tr?n Windows; CI Linux ch? push. Kh?ng commit/push. `NGUON.md` kh?ng t? b?m ?? tr?nh t? tham chi?u; SHA theo byte worktree.

C?n Core / Ch? Anh m?i ph?t sinh: kh?ng.
## Lich su truoc khi gop

| 2 | Màn Chạy thử DEMO, Cổng Local AI, Cổng Cloud AI (tắt ở bản 1) thành **giao diện của engine** (không đặt trong Core) | AI-10, 11, 12 | Chờ làm | Bản cũ trong `tu-core-cu\phia-core\` |

## Hoàn thiện AI-7 sau khi gộp AI-4 — 14/11/2026

Kết luận: Đạt phạm vi công cụ; đã kiểm bằng Core giả (CoreGia) và Local HTTP giả, chưa chạy model thật. PR: **chờ lead mở**.

Đã hợp nhất nội dung hai phía VIEC, giữ dòng lịch sử của cả hai; công cụ đọc ba ca DEMO từ `engine.json`, đánh giá riêng từng ca cho từng model; CMD tự tạo venv và cài SDK khi thiếu, mặc định chạy khô. Local tắt vẫn là giả lập; không có lượt Cloud.

Kiểm: chạy khô mã 0; cổng DEMO Core giả 3/3 ĐẠT; pytest 284 passed, 0 skipped; kiểm độc lập mã 0. Codex không chạy Local thật. Git index vẫn chờ lead stage và hoàn tất merge.

Thời gian bổ sung: khoảng 0,07 giờ; ước tính AI-7 trong phiếu 2 giờ. Lệch phiếu / quyết định tạm: không; Cần Core / Chờ Anh mới phát sinh: không.


## Bàn giao AI-8 — 15/11/2026

**Kết luận:** Đạt phạm vi AI-8 theo cổng DEMO thay thế được phiếu AI-4/AI-8 cho phép; **đã kiểm bằng Core giả (CoreGia)**, Local HTTP giả và KttCore/DOM giả. Chưa kiểm Core thật, trình duyệt thật, model thật hoặc chạy thực tế Linux.

**PR:** chờ lead mở. Nhánh `codex/e_hoi_ai-ai-8`. Không commit/push.

**Đã làm:**

- Thêm `ngan.py` và `cau_hinh.py` trong gói, chỉ thư viện chuẩn. Ngăn RAM khóa luồng, lô tối đa 100 lệnh, nguyên tử, CAS/duy nhất, phạm vi pháp nhân, phân trang tối đa 500 bản ghi. Có kiểm rollback, hai luồng lấy/tạo chỉ một bản, không đọc/ghi chéo pháp nhân và CAS cũ sau xóa/tạo lại.
- Hai năng lực đọc cấu hình qua ngăn/schema; ưu tiên `viec.ngan`, rồi `chon_ngan(app)`. Thiếu cấu hình → `CHUA_CAU_HINH`; đọc lại mỗi việc để nhận thay đổi. Schema không chứa bí mật, timeout dương tối đa 600 giây, quy tắc mặc định `[]`.
- Model lấy/tạo theo `id_model`, cập nhật metadata bằng CAS, đọc ngăn để chọn; đệm discovery RAM 300 giây giữ nguyên. Vẫn đọc metadata mới mỗi lượt và trước POST, không dùng model mất hoặc nguồn discovery lỗi. Xung đột ghi model thử lại tối đa ba lần; hết lượt báo lỗi có thể thử lại, không gửi tài liệu.
- Thêm màn Local (địa chỉ/thời hạn/trạng thái/model/quy tắc/lưu CAS) và Cloud (“Chưa áp dụng ở bản 1”, không nút bật). Màn chỉ dùng KttCore và DOM `textContent`, không gọi mạng ngoài hay lưu trình duyệt. Trạng thái có thời điểm và chỉ mô tả lần kiểm gần nhất.
- Giữ `engine.json` SDK 2.0 nguyên trạng; thêm `KHAI-SDK-2.1.json`. Cổng DEMO nạp cấu hình RAM, không ghi tệp hoặc dùng biến cấu hình. Công cụ AI-7 giữ nguyên `--url`; đã kiểm chạy khô và ca Local giả, không gọi thật.
- Cập nhật README, CHANGELOG, NGUON (băm toàn gói) và hiện trạng. Giữ nguyên mọi mã nguồn cũ.

**Chờ chuyển LUU-TRU (không xóa):** `goi/e_hoi_ai/e_hoi_ai/cau_hinh_may.py`, `goi/e_hoi_ai/contract/cau_hinh_may.schema.json`. Hai tệp và test lịch sử bộ đọc cũ giữ nguyên; test độc lập xác nhận đường chạy engine không import mô-đun cũ.

**Kết quả kiểm thật:** Windows/Python 3.13.14, Node v24.18.0. `.venv` trong worktree; SDK 2.0.0 cài wheel `--no-index --no-deps`, SHA-256 trùng `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Venv dùng `--system-site-packages` để chạy pytest đã cài, không mạng; test gói cách ly chạy `-I -S -B`. Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
3/3 ví dụ trả CHUA_CAU_HINH; 0/3 ĐẠT, mã thoát 1.
Lý do: SDK 2.0 CLI riêng không được cấp ngăn/cấu hình hoặc Local giả.

.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
[ĐẠT] Hỏi người bảo lãnh không có trong tài liệu DEMO
[ĐẠT] Trích tiền và ngày theo khuôn DEMO
[ĐẠT] Đã kiểm bằng Core giả (CoreGia); 3/3 DEMO, 3 lượt Local HTTP giả.
Mã thoát 0.

.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py --sdk-thu
3/3 [ĐẠT], mọi ví dụ chạy thử DEMO đều đạt; mã thoát 0.
Gọi đúng hàm CLI kho_tri_thuc_sdk.thu.main với cấu hình đã nạp qua ngăn RAM.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q
360 passed, 2 skipped in 51.77s; mã thoát 0; không warning.
Hai skip: test so băm ngan.py/cau_hinh.py, lý do “chờ NGAN-0 gộp”.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.

node --test e_hoi_ai/tests/ui/cau_hinh.test.mjs
4 passed, 0 failed, 0 skipped; mã thoát 0.

.venv/Scripts/python e_hoi_ai/cong-cu/thu_local_ai_that.py
CHẠY KHÔ: không dò model, không gọi mạng. Dùng --that và --url để chạy thật.
Mã thoát 0.
```

Các test hai năng lực đếm provider Cloud **0 lượt**, chặn DNS và kết nối ngoài loopback. Test khung Cloud chỉ giả trong RAM, không gọi dịch vụ Cloud thật.

**Hàm/tham số Ngan đã dùng — để lead đối chiếu NGAN-0:**

| Nơi dùng | Chữ ký / dạng dữ liệu |
|---|---|
| Engine | `chon_ngan(app)`; ưu tiên `viec.ngan` khi có |
| Đọc cấu hình | `doc_cau_hinh(ngan, schema_dict)`; bên trong `ngan.doc("cau_hinh", {})` → `None` hoặc bản ghi `.gia_tri`, `.row_version` |
| Đọc model | `ngan.doc("model_phat_hien", {"id_model": id})`; `ngan.tim("model_phat_hien", loc={"url": url}, gioi_han=500, tiep=None_or_token)` → `{"danh_sach": [BanGhi], "tiep": token_or_None}` |
| Ghi model | `with ngan.lo() as lo`; `lo.lay_hoac_tao("model_phat_hien", {"id_model": id}, gia_tri)`; `lo.sua(..., gia_tri, row_version=ban.row_version)`; bắt `NganXungDot` |
| Nạp DEMO | `NganBoNho()` hoặc `NganBoNho(khai_bao)`; `lo.them("cau_hinh", {}, gia_tri)` / `lo.sua(..., row_version=...)` |
| Test hợp đồng | `NganBoNho(khai_bao, phap_nhan_id=...)`; `.voi_phap_nhan(id)` dùng chung kho/khóa; `lo.xoa(bang, khoa, row_version=...)`; `lo.ket_qua` là danh sách `{row_version, da_tao}` |

**Lệch khỏi phiếu / quyết định tạm:**

- Theo lệnh bổ sung của lead, không chờ/chỉnh `_chung/mau-ma`: viết hai bản tạm trong gói và skip so băm. Chưa thể khẳng định tương thích byte/API hoàn toàn với NGAN-0 chưa gộp; cần lead đối chiếu bảng trên khi thay mẫu.
- Giữ cổng DEMO thay thế của AI-4, ghi trung thực lệnh SDK thu thiếu cấu hình mã 1. Không tự nạp DEMO vào engine thật để làm xanh lệnh.
- Phạm vi AI-8 được chia hai phần review: **AI-8a** hai tệp cổng dùng chung tạm; **AI-8b** năm tệp nối engine/UI (`hoi.py`, `hoi_yeu_cau.py`, `cong_ai.py`, `chon_model.py`, `ui/cau_hinh.js`). Tổng bảy tệp mã do cần hai cổng tạm trong lúc NGAN-0 làm song song; bàn giao chung theo lệnh Anh, lead có thể tách hai commit review. Chưa tạo commit/PR.
- Không phát sinh câu Chờ Anh. Cần Core/SDK và đồng bộ NGAN-0 như mục Cần Core phía trên. Chưa chạy Linux thực tế; mã/test không phụ thuộc Windows ngoài kịch bản chạy có sẵn.

**Thời gian thực tế:** bắt đầu **15/11/2026 07:38:00 +07:00** (theo lead), kết thúc **15/11/2026 07:55:09 +0700**; **0.29 giờ** theo đồng hồ. Ước tính phiếu AI-8: **4 giờ**.

## Nối ngăn chung NGAN-0 — AI-8, 15/11/2026

Kết luận: **Đạt — đã nối ngăn chung NGAN-0**, đã kiểm bằng Core giả (CoreGia), Local HTTP giả và KttCore/DOM giả. PR: **chờ lead mở**; nhánh `codex/e_hoi_ai-ai-8`. Không commit/push.

Đã làm: giữ nguyên `ngan.py`, `cau_hinh.py` do lead chép từ mẫu PR #34, không sửa `_chung/**`. Tạo ngăn RAM với khai báo `KHAI-SDK-2.1.json/ngan_du_lieu` cho engine, công cụ độc lập và cổng DEMO; giữ ngăn SDK nếu có. Sửa đọc `TrangNgan`, test dùng `KetQuaLenh` sau commit, `cho_phap_nhan`, khóa duy nhất và ngoại lệ đúng API. Giữ test hành vi riêng của engine: đổi cấu hình/catalog, model mất, discovery lỗi, CAS thử lại có giới hạn; bổ sung ca 501 model qua phân trang, lỗi ngăn/cấu hình qua hai năng lực không lộ traceback và gói khởi động ngoài repo. Hai test so SHA-256 chuẩn CRLF → LF đều chạy, không skip. Đã cập nhật SHA-256 chuẩn LF của toàn bộ 27 tệp gói trong NGUON.md, CHANGELOG, README và hiện trạng.

Kết quả kiểm thật trên Windows/Python 3.13.14, `.venv` trong worktree; SDK 2.0.0 từ wheel nội bộ, SHA-256 khớp SHA256SUMS.txt. Biến môi trường: `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
0/3 ĐẠT, 3 ca CHUA_CAU_HINH; mã thoát 1.
CLI độc lập chưa có cấu hình/ngăn và Local giả. Dùng cổng thay thế có sẵn:

.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py --sdk-thu
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
[ĐẠT] Hỏi người bảo lãnh không có trong tài liệu DEMO
[ĐẠT] Trích tiền và ngày theo khuôn DEMO
Engine e_hoi_ai 0.4.0: mọi ví dụ chạy thử DEMO đều đạt.
3/3 ĐẠT, mã thoát 0; gọi kho_tri_thuc_sdk.thu.main với ngăn RAM/Local giả.

.venv/Scripts/python e_hoi_ai/tests/chay_demo_voi_local_gia.py
[ĐẠT] Đã kiểm bằng Core giả (CoreGia); 3/3 DEMO, 3 lượt Local HTTP giả.
Mã thoát 0.

.venv/Scripts/python -m pytest e_hoi_ai/tests -q --basetemp=.pytest-tmp
370 passed in 41.30s; 0 skipped, mã thoát 0.
Gồm kiểm UI Node/KttCore giả và hai test so băm NGAN-0.

.venv/Scripts/python e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.
```

Thời gian thực tế phần nối: **15/11/2026 07:57–08:04 +07:00**, khoảng **0,12 giờ**; phiếu AI-8 ước tính **4 giờ** cho toàn lát (phần trước đã bàn giao riêng).

Lệch khỏi phiếu / quyết định tạm đã dùng: cổng DEMO thay thế có sẵn, nạp cấu hình qua ngăn và bật Local giả theo phiếu AI-4/AI-8; không nạp DEMO vào đường chạy thật. Giữ nguyên test hợp đồng RAM hiện có, sửa theo API chung. Bản bàn giao ban đầu có hai skip và cổng tạm phía trên là lịch sử, được thay bởi kết quả này.

Cần Core / Chờ Anh mới phát sinh: **không**. Vẫn chờ SDK 2.1 cấp ngăn bền/cấu hình và cửa màn quản trị như mục Cần Core. Chưa kiểm Linux thực tế, Core thật hoặc model thật; Cloud bản 1 **0 lượt**. Thư mục `.pytest-tmp` là dữ liệu kiểm DEMO, không thuộc gói và không đưa vào PR.

## Bàn giao AI-9 — 15/11/2026

**Kết luận: Đạt phạm vi AI-9 bằng bộ giả lập** — đã kiểm bằng Core giả (CoreGia) và Local HTTP giả, giữ nguyên chuẩn trích dẫn hỏi–đáp cũ. CLI SDK độc lập chưa đạt vì không được cấp cấu hình/ngăn/model. Chưa đo model thật, Core thật, Linux thực tế hoặc chất lượng nhận diện/0 lọt; Cloud vẫn tắt cứng.

**PR:** chờ lead mở; nhánh `codex/e_hoi_ai-ai-9`. Tiêu đề đề nghị: `[e_hoi_ai] AI-9 — Nhận diện thực thể theo span chỉ Local`. Không commit/push.

**Đã làm:**

- Đúng **5 tệp mã**: `hoi_mask.py`, `chay.py`, `ai_cuc_bo.py`, `nha_cung_cap.py`, `engine.json`. Gói 0.5.0 thêm `ai.hoi_mask_cuc_bo@1`, nhận `yeu_cau_ai`, trả `tra_loi_ai`. Tái dùng helper đọc yêu cầu/schema/chọn model/provider/ngăn trong cùng gói; không sửa `hoi_yeu_cau.py` (kể cả `_kiem_tra_loi`), `khuon_json.py`, `chon_model.py`, `ngan.py`, `cau_hinh.py`, schema chung/SDK/Core/nguồn cũ; không import/gọi Mask hoặc engine khác, không dependency mới.
- Profile kỹ thuật theo sổ loại chung §6, lead đã duyệt 15/11 trong lệnh giao. Kiểm local bắt buộc, phiên bản/mã, tham chiếu kỹ thuật, dạng băm, offset/đoạn/trần; tái tính băm prompt/khuôn/đoạn, và băm gốc khi một đoạn. Chuyển tiếp giữ nguyên byte JSON chuẩn hóa; không gửi chuyển tiếp/snapshot/mã/băm nội bộ qua prompt, schema annotation hoặc model ID. Không đọc tệp/ngăn riêng Mask hoặc tự tạo chứng cứ nguồn.
- Giữ nguyên gốc Unicode (NFD/Cf/selector), model trả trực tiếp đối tượng khuôn span rồi engine đặt vào `du_lieu`. JSON nghiêm, object đóng, đủ required; Python kiểm int thật, khoảng và lát nguyên văn. Trích dẫn giữ từng lần tên lặp; nhãn/mức/offset không phải câu trích. Rỗng hợp lệ có trạng thái không thấy căn cứ/kiểm trích dẫn true và không tạo thực thể; không cấp cờ an toàn/quyền Cloud.
- Transport POST dùng cùng socket IP/bind nguồn, cấm DNS/proxy/redirect, kiểm model/metadata mới; không retry hoặc fallback sau gửi. Connect lỗi chắc chắn trước gửi → lỗi Local có thể thử lại; timeout/mất phản hồi/thân HTTP thiếu hoặc 202 → truyền nguyên `ChuaRo` với mã tương quan độc lập. Lỗi dọn socket không ghi đè ChuaRo. Ollama phải `done=true,done_reason=stop`; OpenAI-compatible phải `finish_reason=stop`; kiểm JSON/trần byte/độ sâu và từ chối dấu cắt/sai nguồn cho cả ba handler.
- AI-9 kiểm body đầu vào ≤64 KiB; dự trù byte UTF-8 + 256 + 8192 token đầu ra phải nằm trong context server khai đang dùng. Đầu ra 8192 token, tối đa 2.000.000 byte. Thiếu metadata context thì chặn trước POST; đây chưa là phép đo tokenizer/sức chứa thật. Cấu hình/model chỉ qua ngăn, đệm chỉ RAM; không tệp cấu hình/sổ/cache bền. Log AI-9 chỉ mã/phiên bản/số đếm/thời gian/trạng thái.

**Kết quả kiểm thật:** Windows x64, Python 3.13.14, SDK 2.0.0 cài offline từ wheel repo (`--no-index --no-deps`), SHA-256 khớp `a507af85f40bbdb5e0dc541a46a17c1779800d0da39176dcfa43d54759790892`. Venv trong worktree dùng `--system-site-packages` cho pytest 9.1.1 có sẵn; không tải mạng. Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`; pytest thêm `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
0/3 ĐẠT; cả ba trả CHUA_CAU_HINH; mã thoát 1.
CLI độc lập chưa được cấp ngăn/cấu hình hoặc model, không tự nạp DEMO vào runtime.

.venv/Scripts/python -B -m pytest e_hoi_ai/tests -q
560 passed in 157.20s (0:02:37)
0 skipped; mã thoát 0.

.venv/Scripts/python -B e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.

.venv/Scripts/python -B e_hoi_ai/tests/chay_demo_voi_local_gia.py
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
[ĐẠT] Hỏi người bảo lãnh không có trong tài liệu DEMO
[ĐẠT] Trích tiền và ngày theo khuôn DEMO
[ĐẠT] Đã kiểm bằng Core giả (CoreGia); 3/3 DEMO, 3 lượt Local HTTP giả.
[ĐẠT] AI-9 nhận diện tổ chức DEMO; CoreGia, 1 lượt Local HTTP giả.
Mã thoát 0.

.venv/Scripts/python -B e_hoi_ai/tests/chay_demo_voi_local_gia.py --sdk-thu
3/3 [ĐẠT]; Engine e_hoi_ai 0.5.0: mọi ví dụ chạy thử DEMO đều đạt.
Mã thoát 0; gọi thật kho_tri_thuc_sdk.thu.main với ngăn RAM/Local giả.

git diff --check
Không có lỗi; mã thoát 0.
```

Nền trước sửa: **370 passed in 48.75s**, không skip. Thêm **190 ca** trong hai tệp test AI-9/transport; toàn bộ hồi quy cũ giữ đạt, gồm công cụ AI-7 và UI/KttCore giả. Kiểm danh sách đúng/rỗng/tên lặp, NFD/Cf/emoji/code point, từng required/kiểu/offset/băm, trần 32/64 KiB và đoạn, prompt injection/metadata không lên wire, API Ollama/LM Studio/OpenAI-compatible, context thiếu/overflow/response cắt, timeout trước/sau POST/202/ChuaRo, proxy/DNS/redirect, metadata đổi trước gửi, hủy/mất lease/mất ACK. Bộ đếm Cloud **0 lượt** và hàng rào chỉ loopback có hiệu lực. Đối chiếu riêng xác nhận hai năng lực cũ, ba DEMO manifest và năm mô-đun tái dùng nêu trên giữ nguyên nội dung/ngữ nghĩa.

**Thời gian thực tế:** bắt đầu **15/11/2026 12:12** theo lead; kết thúc **12:47:27 UTC+07 ngày 15/11/2026**, khoảng **0.59 giờ** thời gian đồng hồ (gồm đọc tài liệu, triển khai, kiểm và bàn giao). Ước tính trong phiếu: **6 giờ**, độ khó kho.

**Lệch khỏi phiếu / quyết định tạm đã dùng:** không vượt 5 tệp mã. Chọn **0 lần hỏi lại AI-9**, trong giới hạn tối đa một lần được cho phép; handler hỏi–đáp cũ giữ quy tắc cũ. Giữ ba DEMO manifest vì công cụ AI-7 chấm riêng khuôn tiền/ngày; ca AI-9 nằm trong fixture/bộ chạy test ngoài gói với snapshot bytes/kích thước/băm thật ở RAM CoreGia. Cổng DEMO thay thế theo AI-4/AI-8; CLI độc lập mã 1 được giữ trung thực. Không sửa mẫu ngăn/cấu hình hoặc schema chung để làm xanh kiểm. Trường context của server chưa xác minh/đo trên máy thật; server không công bố context hiện dùng thì AI-9 từ chối.

**Cần Core / Chờ Anh mới phát sinh:** đã bổ sung ba mục AI-9 ở phần Cần Core: chứng thực nguồn/yêu cầu/băm chuẩn, lặp/ghép đủ đoạn/deadline/ChuaRo, snapshot/tệp con có quyền và vòng đời/chống lặp qua SDK 2.1; cửa Cloud kiểm hậu kiểm cuối. Lead cần xác nhận model tại chỗ/egress bị chặn và đo context/model thật trước dùng thật. Không có câu hỏi quyết định nghiệp vụ mới cho Anh; chưa đo model/Core thật hoặc held-out, không tuyên bố đạt mục tiêu 0 lọt.

## Cần Core — AI-11

- **AI-11 — 15/11/2026, còn chặn nghiệm thu:** wheel SDK 2.2.0 `thu.main()` chỉ nhận đúng một đối số là thư mục gói và gọi `CoreGia().chay_thu_demo(app)`; `chay_thu_demo()` không đọc cấu hình từ mỗi ví dụ/fixture. Phiếu không cho khai cấu hình DEMO. Vì CoreGia mới không có `local_ai`, cả ba ví dụ hợp lệ đều trả `CHUA_CAU_HINH`; đặt default cấu hình DEMO vào runtime không phải giải pháp đúng. Cần SDK/Core có cửa chung cấp cấu hình DEMO hợp lệ và thiết lập nguồn Local giả/fixture cho CLI chuẩn, không đổi handler thật. API `CoreGia.dat_cau_hinh` hiện hoạt động, bộ hồi quy chính thức đạt 3/3 + AI-9 1/1; bằng chứng này **không thay** điều kiện CLI.
- **AI-11 — màn engine:** SDK 2.2.0 chưa nhận trường `giao_dien_quan_tri` trong engine.json; wheel trình duyệt chưa cung cấp `KttCore.engine`. Giữ `ui/cau_hinh.js` dùng đúng API đề nghị `.cau_hinh.doc/luu` và `.ngan.tim`, không khai trường ngoài hợp đồng. Cần Core xác nhận cửa nạp màn module và quyền Admin trên Core thật. Đây là phần chưa nghiệm thu, không phải lỗi cần route riêng cho Hỏi AI.
- **AI-11 — đóng nợ cấu hình/ngăn:** các yêu cầu ngăn RAM/cấu hình ngoài gói ở bản ghi lịch sử dưới đây đã được thay bằng `viec.ngan`/`viec.cau_hinh` của SDK 2.2.0. Vẫn cần kiểm Core thật/Windows đích, Linux CI và model thật; CoreGia không chứng minh RLS, lưu bền hoặc vận hành thực tế của Core.

## Bàn giao AI-11 — 15/11/2026

Kết luận: **Chưa đạt** toàn bộ điều kiện AI-11 — đã chuyển runtime/gói/test sang SDK 2.2.0, còn CLI chuẩn không có cửa cấp cấu hình DEMO và Local giả.

PR: **chờ lead mở**. Nhánh `codex/e_hoi_ai-ai-11`; tiêu đề đề nghị `[e_hoi_ai] AI-11 — Chuyển sang SDK 2.2.0`. Không commit/push.

Đã làm:

- Venv `.venv` mới, cài wheel SDK với `--no-index --no-deps`; phiên bản 2.2.0, SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp bản phát hành. `requirements.lock` ghim SDK 2.2.0; không thêm dependency runtime. Bộ phụ thuộc test offline ghim riêng, sao distribution đã cài vào venv; không tải mạng.
- Manifest 0.11.0 khai ngăn catalog/cấu hình/migration theo SDK; bỏ bảng cấu hình. SQL chỉ CREATE TABLE `eng_e_hoi_ai.model_phat_hien`, đầy đủ cột hệ thống; api đổi json sang chuỗi JSON/van_ban/text vì SDK không hỗ trợ kiểu json.
- Runtime đọc snapshot `viec.cau_hinh`, dùng `viec.ngan`; không có fallback RAM. `local_ai` chưa khai không chặn khởi động; thiếu trường bắt buộc ở việc vẫn `CHUA_CAU_HINH`. Đổi cấu hình làm mới đệm discovery bằng hook SDK. Catalog không gửi ngược cột hệ thống, thứ tự đọc theo số; model mất đánh dấu trạng thái.
- Chuyển bốn tệp KHAI-SDK-2.1/ngan/cau_hinh/ngan_engine nguyên nội dung vào LUU-TRU/AI-11, không xóa. Test so băm hai mẫu cổng tạm bỏ theo phiếu; hành vi CAS/rollback/unique/pháp nhân/phân trang/trần lô/cấu hình/lỗi/khởi động HTTP được kiểm lại với CoreGia SDK. Thêm kiểm snapshot đổi giữa hai việc, hook, thứ tự >10 model và dữ liệu còn khi tạo lại đối tượng Engine nối cùng CoreGia.
- UI giữ `.cau_hinh` của KttCore; không đọc/ghi bảng cấu hình. Công cụ AI-7 cũng cấp cấu hình bằng `dat_cau_hinh`, không mock đường cấu hình. Bộ Local giả chỉ là hồi quy bổ sung, không còn tùy chọn --sdk-thu/cổng thay thế nghiệm thu.
- README/CHANGELOG/NGUON cập nhật; tệp gói chuẩn LF, kiểm kê 26 tệp raw bytes. NGUON băm LF trừ chính nó và sql/kiem_ke.json để tránh vòng băm; kiểm kê cuối bao gồm NGUON. Có `tests/cap_nhat_bam.py` để tái sinh đúng thứ tự. Mã nghiệp vụ sửa 3 tệp, SQL thêm 1, công cụ AI-7 sửa 1; các tệp lưu trữ là di chuyển, các thay đổi LF khác không đổi logic. Không sửa SDK/_chung/engine khác.

Kết quả kiểm thật — **đã kiểm bằng Core giả (CoreGia)**, Windows/Python 3.13.14, chưa kiểm Linux/Core thật/model thật. Đặt PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1; pytest thêm PYTEST_DISABLE_PLUGIN_AUTOLOAD=1:

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
[LỖI] Hỏi số tiền và ngày thanh toán DEMO: CHUA_CAU_HINH
[LỖI] Hỏi người bảo lãnh không có trong tài liệu DEMO: CHUA_CAU_HINH
[LỖI] Trích tiền và ngày theo khuôn DEMO: CHUA_CAU_HINH
=> 0/3 ĐẠT, mã thoát 1.

.venv/Scripts/python -B -m pytest e_hoi_ai/tests -q --basetemp=.pytest-tmp
574 passed in 127.02s (0:02:07)
=> 0 skipped, mã thoát 0.

.venv/Scripts/python -B e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
=> mã thoát 0.

.venv/Scripts/python -B e_hoi_ai/tests/chay_demo_voi_local_gia.py
[ĐẠT] Hỏi số tiền và ngày thanh toán DEMO
[ĐẠT] Hỏi người bảo lãnh không có trong tài liệu DEMO
[ĐẠT] Trích tiền và ngày theo khuôn DEMO
[ĐẠT] Đã kiểm bằng Core giả (CoreGia); 3/3 DEMO, 3 lượt Local HTTP giả.
[ĐẠT] AI-9 nhận diện tổ chức DEMO; CoreGia, 1 lượt Local HTTP giả.
=> mã thoát 0; chỉ bằng chứng bổ sung, không thay CLI SDK thu.

Kiểm kê SQL: 26/26 tệp, bytes/SHA-256 khớp; SQL/cột/kiểu/ràng buộc khớp manifest.
Sau sửa câu mô tả README và tái sinh băm: 7 passed in 0.10s (test_nguon_sha256 + test_sdk_22).
git diff --check => mã 0.
```

Thời gian thực tế: **16:44–17:03 ngày 15/11/2026 (+07), khoảng 0,32 giờ**; ước tính trong CHUYEN-SDK-2.2 §4: **2 giờ**.

Lệch khỏi phiếu / quyết định tạm đã dùng: không thay cửa nghiệm thu hoặc tạo nhánh DEMO runtime. CLI không đạt do SDK chưa hỗ trợ fixture cấu hình/Local giả; trường json chuyển thành văn bản; khai màn quản trị chưa thể đưa vào engine.json. Các khác biệt schema/kiểu/cột hệ thống và băm LF mô tả ở trên.

Cần Core / Chờ Anh mới phát sinh: xem ba mục AI-11 ở phần Cần Core. Cần cửa CLI chung cho cấu hình DEMO/Local giả và cửa nạp màn engine/quyền Admin. Không có câu hỏi mới cần Anh quyết về nghiệp vụ.

## Cần Core — AI-12, 15/11/2026

- Giữ nợ CLI chung của AI-11: cấp cấu hình DEMO/nguồn Local giả qua cửa SDK/Core chính thức. CLI hiện 0/3 `CHUA_CAU_HINH`, mã 1; không đưa cấu hình/fixture vào runtime để làm đạt giả.
- Lead duyệt **ĐỀ XUẤT AI-12** tại `_chung/docs/LOAI-DU-LIEU-RIENG.md` §8: annotation `$comment` đã có của JSON Schema, không đổi schema chung/trường bắt buộc. Trong lát này dùng quy ước và adapter nội bộ trên bản sao khuôn, theo lệnh giao. Không có quyết định nghiệp vụ mới cần Anh.
- Phần gây chặn metadata ở L-TC-01/C-DC-07 đã có bằng chứng consumer AI-12 đạt bằng fixture DEMO độc lập. Cần lead TC/DC nối lại pipeline với quyền nguồn/tệp xuyên bước của Core; việc này chưa được chứng nhận bởi bài kiểm e_hoi_ai. Không sửa VIEC của producer hoặc tuyên bố đóng các cửa Core còn thiếu của họ.

## Bàn giao AI-12 — 15/11/2026

Kết luận: **Chưa đạt toàn bộ điều kiện §5** do CLI SDK chuẩn thiếu cấu hình DEMO/Local giả (nợ AI-11); phần tương thích AI-12 đạt bằng bộ giả. **Đã kiểm bằng Core giả (CoreGia)** và Local HTTP giả, chưa kiểm Core/model thật hoặc Linux thực tế.

PR: **chờ lead mở**; nhánh `codex/e_hoi_ai-ai-12`. Tiêu đề đề nghị: `[e_hoi_ai] AI-12 — Tách metadata và giá trị trích trong khuôn TC/DC`. Không commit/push.

### Tái hiện trước sửa

Chép dữ liệu DEMO từ `e_tra_cuu/tests/ho_tro_tc_2/4/5/6/7.py` và `e_doi_chieu/tests/test_dc6.py` vào `tests/fixture_ai_12.json`, kèm đường nguồn/SHA-256 LF. Ngữ cảnh/khuôn được tạo bằng định nghĩa hàm thuần producer đã đọc qua AST; không import chéo package, không sửa producer. Bộ test chỉ đọc bản chép, không cần các engine kia. Tham chiếu snapshot chỉ kiểm chuyển tiếp, không chứng nhận quyền/vòng đời tệp hoặc toàn pipeline producer.

Chạy đúng `ai.hoi_theo_yeu_cau@1` qua CoreGia SDK 2.2.0, cấu hình chính thức `dat_cau_hinh`, Local HTTP giả trả JSON `du_lieu` đúng khuôn cùng `truong` có quote nguồn đúng. **Cả năm ca đều qua kiểm đầu vào, chọn/gọi Local và `khop(du_lieu,khuon)`**; SDK kết thúc `XONG`, nhưng `_kiem_tra_loi` duyệt `_cac_la` rồi `_duoc_dan` hạ kết quả về `khong_thay_can_cu`, `kiem_trich_dan={dat:false,loi:[DU_LIEU_NGOAI_TRICH_DAN]}`. Đây là từ chối căn cứ sau schema, không phải lỗi nhận khuôn.

| Fixture | Các trường bị coi nhầm là nguyên văn |
|---|---|
| TC phân loại | Nhóm/loại đề xuất, điểm 0.95, cờ chuyển bộ và offset căn cứ |
| TC phân tích câu hỏi | Ý định `gia_tri`, loại thực thể, tên/phiên bản hàm, cờ thời điểm và mốc Core |
| TC xếp hạng lại | Mã ứng viên và điểm 0.5 |
| TC soạn trả lời | Mã trường, câu tổng hợp, cờ mâu thuẫn và offset căn cứ |
| DC-6 | Mã điểm, nhãn `can_xem`, lý do phân loại và offset hai phía |

Lệnh tái hiện trước sửa: `.venv/Scripts/python -B -m pytest e_hoi_ai/tests/test_ai_12.py -q --basetemp=.pytest-tmp-ai12-truoc --tb=short` → **5 failed in 2.33s**, đều tại assertion `kiem_trich_dan.dat`; mã thoát 1. Không nhét nhãn/điểm/offset vào quote để làm qua kiểm.

### Đã làm

- Hai mô-đun runtime: thêm `vai_tro_khuon.py`, sửa `hoi_yeu_cau.py`; manifest tăng 0.12.0, kiểm kê gói tự sinh. Không sửa `khuon_json.py`: dùng đúng tập từ khóa/schema checker đang có, annotation nằm trong `$comment` đã được hỗ trợ. Không đổi schema/API chung hoặc thêm trường bắt buộc/dependency.
- Lớp tương thích nhận cấu trúc object đóng và profile phiên bản 1 của bốn tác vụ TC/DC-6, gán vai trò trên bản sao. Metadata kiểm schema/enum/const/kiểu; giá trị thực thể/tham số và khẳng định vẫn kiểm nguyên văn. Khuôn khác/trường mới giữ kiểm bảo thủ; không tự miễn mọi enum/const. Annotation xung đột không hạ chuẩn trích.
- Câu trích kiểm `tai_lieu[a:b] == cau`, int thật/code point/nửa mở; giữ các vị trí lặp, không dò sửa offset. Giá trị trong mục có `can_cu` chỉ dùng quote của mục đó; tiền phải cùng số và mã tiền trong một cụm, không ghép hai khoản. Chuỗi số/ngày phải khớp token đầy đủ; giữ chuyển đổi nhóm ba/ngày ISO đã có. Câu tổng hợp không cần nguyên văn nhưng số bịa vẫn bị chặn.
- Không sửa khuôn gửi Local/chuyển tiếp/băm đầu vào; không dùng metadata để cấp quyền. Sai giá trị/span tiếp tục hạ trạng thái và cảnh báo, sai enum/kiểu vẫn hỏi lại đúng một lần rồi `AI_TRA_SAI_KHUON`; 0 Cloud. Các handler AI-1/AI-9 và transport giữ nguyên.
- 63 ca AI-12: năm fixture thành công, enum/const/kiểu/thang điểm sai, bịa số/tiền/ngày/tham số, mượn quote khoản khác, ghép sai tiền tệ, offset/câu bịa, quote ngoài sai, câu tổng hợp bịa số, `$ref`/nhánh schema/annotation xung đột, NFD/Cf/emoji/từng vị trí lặp, offset bool/float, citation null và căn cứ rỗng. Hồi quy cũ giữ đạt.
- Cập nhật VIEC/CHANGELOG/NGUON và kiểm kê. Ngoài e_hoi_ai chỉ thêm đề xuất đúng phạm vi cho phép vào sổ loại chung §8; không sửa engine khác, docs/goi-gui-engine, Core hoặc mã cũ.

### Kết quả kiểm thật

Windows x64, Python 3.13.14, venv `.venv` trong worktree. SDK 2.2.0 cài wheel offline `--no-index --no-deps`; SHA-256 `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp `SHA256SUMS.txt`. Phụ thuộc test sao offline từ distribution đã cài theo `tests/requirements.lock`; không tải mạng. Đặt `PYTHONUTF8=1`, `PYTHONDONTWRITEBYTECODE=1`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
0/3 ĐẠT: cả ba ví dụ CHUA_CAU_HINH; mã thoát 1.
Engine e_hoi_ai 0.12.0: có ví dụ chạy thử DEMO chưa đạt.

.venv/Scripts/python -B e_hoi_ai/tests/chay_demo_voi_local_gia.py
3/3 DEMO ĐẠT, 3 lượt Local HTTP giả; AI-9 1/1 ĐẠT, 1 lượt Local HTTP giả.
Đã kiểm bằng Core giả (CoreGia); mã thoát 0.

.venv/Scripts/python -B -m pytest e_hoi_ai/tests -q --basetemp=.pytest-tmp
637 passed in 261.40s (0:04:21); 0 skipped; mã thoát 0.
Trong đó 63 ca mới AI-12; 5/5 fixture XONG/co_can_cu/kiem_trich_dan.dat=true.

.venv/Scripts/python -B e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.

Kiểm kê sql/kiem_ke.json: 27/27 tệp khớp bytes/SHA-256.
git diff --check: mã 0.
```

Thời gian thực tế: bắt đầu **15/11/2026 17:08** theo lead; bộ kiểm chính kết thúc **17:32:07 (+07)**, kiểm bàn giao kết thúc **17:33:25 (+07)**; tổng khoảng **0,42 giờ**. Phiếu `GIAO-CODEX-e_hoi_ai.md` và lệnh lead **không ghi ước tính riêng AI-12**; 4 giờ trong phiếu là AI-2 gốc, không dùng thay ước tính AI-12.

Lệch khỏi phiếu / quyết định tạm đã dùng: quy ước annotation tùy chọn và adapter schema nội bộ theo đề xuất AI-12 §8, chờ lead duyệt; không yêu cầu producer đổi payload. Không thay cổng nghiệm thu CLI bằng harness. Dữ liệu/shape fixture được chép độc lập, không phải nghiệm thu toàn pipeline TC/DC hoặc model thật.

Cần Core / Chờ Anh mới phát sinh: không có nợ kỹ thuật Core mới ngoài cửa CLI của AI-11; cần lead duyệt đề xuất §8 và nối lại TC/DC với nguồn/quyền Core thật. Không có câu hỏi nghiệp vụ mới cho Anh.

## UI-AI-1 — 21/11/2026 — Màn Máy AI

Kết luận: **Chưa đạt toàn bộ điều kiện nghiệm thu** — triển khai/pytest/UI đạt bằng bộ giả; CLI SDK chuẩn còn 0/3 do nợ cửa cấu hình DEMO/Local giả từ AI-11. PR: **chờ lead mở**. Nhánh `codex/e_hoi_ai-ui-ai-1`; tiêu đề đề nghị `[e_hoi_ai] UI-AI-1 — Màn Máy AI và thao tác quản trị`. Không commit/push. **Đã kiểm bằng Core giả (CoreGia)**; chưa nối Core hoặc model thật, chưa chạy Linux thực tế.

Đã làm:

- Màn `goi/e_hoi_ai/ui/cau_hinh.js` bám ảnh mẫu Máy AI: IP/cổng riêng, trạng thái ở đầu thẻ, ba nút Kiểm tra kết nối / Tự tìm máy AI / Cập nhật model. Bố cục hai cột trên màn rộng, một cột cả bảng quy tắc trên màn hẹp. Nhãn/hướng dẫn/mẫu và lỗi cạnh ô; không xưng hô, thời điểm kiểm dạng dd/mm/yyyy.
- Bảng quy tắc và dự phòng có chọn model, thêm/bỏ/sắp thứ tự; giữ ID cũ khi chưa khả dụng. Mẫu * dùng cho mọi prompt theo thứ tự quy tắc hiện có. Thời hạn/đường dẫn API ở Nâng cao; giữ URL/path, IPv6 và cổng 80. Lưu CAS, giữ nội dung đang sửa và khóa Lưu sau tranh chấp đến khi tải lại. Bỏ phản hồi kiểm máy cũ nếu IP/cổng/path đã đổi.
- `quan_tri.py` có `kiem_ket_noi`, `tim_may_ai`, `lay_danh_sach_model`, chỉ GET metadata qua discovery/bảo vệ mạng đã có; không gửi prompt/tài liệu hoặc gọi Cloud, không lưu tệp. Hai thao tác kiểm cập nhật catalog qua ngăn SDK/CAS; lỗi ngăn vẫn là lỗi. Tìm máy không ghi catalog trước khi chọn.
- `KHAI-SDK-2.1.json` khai D/E dự kiến, tên hàm, hợp đồng vào/ra, quyền Admin và hạn tác vụ. Không sửa `engine.json`, `chay.py`, xử lý việc hoặc danh mục engine; không thêm dependency. Bốn tệp triển khai (UI, Python, schema, bản khai), ngoài test/tài liệu/kiểm kê tự sinh.
- Schema bổ sung title/description/examples tiếng Việt ở mọi cấp, diễn giải và mẫu JSON đầy đủ tại gốc; URL chỉ HTTP phù hợp runtime. README/CHANGELOG/NGUON và kiểm kê được cập nhật.
- 26 test Python mới: CoreGia + Local HTTP giả cho cả bốn API, model rỗng/remote, lỗi máy/đầu vào/ngăn, tìm máy theo cấu hình/catalog, vượt trần từ chối. Adapter quản trị chỉ nằm trong test; gói không khai năng lực giả để SDK 2.2.0 chấp nhận.
- 24 test Node/KttCore giả, không mạng: đọc/phân trang, lưu/CAS/tải lại, lỗi nhập từng ô/dòng, thứ tự quy tắc/dự phòng, kiểm/cập nhật model/tìm máy thành công và thất bại, phản hồi cũ, lỗi đọc/lưu và DOM an toàn. UI-AI-1 không có API key hoặc gọi `.bi_mat`; test chặn truy cập két và xác nhận không có ô bí mật. Kiểm chỉ hiện 4 ký tự cuối thuộc UI-AI-2, không thêm màn Cloud ngoài phạm vi.

Ảnh PR (DEMO, dựng từ chính mã UI với KttCore giả; đã xem lại):

- [Màn rộng 1160×1340](anh-ui-ai-1/may-ai-rong.png).
- [Màn hẹp 390×2100](anh-ui-ai-1/may-ai-hep.png).
- [Mất kết nối 1160×1340](anh-ui-ai-1/may-ai-loi.png).
- [HTML DEMO có CSP chặn mạng ngoài](anh-ui-ai-1/may-ai-demo.html). Tái dựng: `node e_hoi_ai/tests/ui/chup_anh_demo.mjs`; Chrome headless/CDP chỉ trên loopback, không dịch vụ ngoài, kiểm đúng viewport và không tràn ngang trước khi chụp. Node test của UI hoàn toàn trong RAM; công cụ chụp chạy riêng.

Lệch khỏi phiếu / quyết định tạm đã dùng:

- Tự tìm giới hạn địa chỉ đã biết: đầu vào, cấu hình, catalog của Core, loopback 11434/1234; tối đa 16 URL duy nhất, 4 luồng, mỗi đích tối đa 4 GET × 1 giây. Vượt trần thì từ chối, không cắt ngầm. Không quét toàn mạng hoặc gọi DNS; màn nói rõ máy LAN mới cần nhập IP. Đây là lựa chọn triển khai có giới hạn, không khẳng định tìm được mọi máy LAN/Tailscale.
- Không thêm model mặc định hoặc tùy chọn rà hợp đồng như ảnh mẫu vì schema/runtime hiện không có các trường này; giữ đúng yêu cầu không đổi hành vi xử lý việc. Cổng Cloud vẫn giữ nội dung cũ, UI-AI-2 làm riêng.
- Lượt kiểm đầu: 660 passed, 3 failed trong 335,11 giây. Hai lỗi kiểm kê do sửa layout mobile khi pytest đang chạy; đã tái sinh băm sau khi khóa mã. Một test timeout có sẵn lỗi tại metadata trước POST. Lượt thứ hai khi không chụp Chrome: 658 passed, 5 failed trong 312,29 giây; cả năm thuộc cùng nhóm test sau POST nhưng bị timeout metadata trước POST.
- Sửa riêng fixture `test_transport_ai_9.py`: cấu hình metadata/connect 2 giây; ca timeout chờ máy giả xác nhận đã nhận POST bằng Event rồi đặt socket 0,03 giây khi chờ phản hồi. Máy giả giữ phản hồi bằng Event đến khi lời gọi kết thúc rồi giải phóng trong finally. Giữ toàn bộ assertion CHUA_RO, không retry/fallback, chỉ một POST; không thay xử lý việc hoặc transport runtime. Đây là sửa kiểm thử cần thiết để kiểm đúng giai đoạn sau POST và tránh đếm lượt trước khi server được scheduler cho chạy, không nới điều kiện thành công.

### Cần Core — UI-AI-1

- Cửa D: nạp `ui/cau_hinh.js`, quyền `admin_core`, `.cau_hinh.doc/luu` đúng CAS và hiển thị title/description/examples + Chèn mẫu ở ô JSON chung trong lúc chưa nạp màn.
- Cửa E: dispatch ba thao tác quản trị theo bản khai dự kiến (việc ưu tiên, snapshot cấu hình/ngăn, hạn 30 giây, lỗi an toàn). SDK 2.2.0 chưa có decorator/cửa này; các hàm chưa được nối trong runtime. Không cần route riêng cho Hỏi AI.
- Giữ nợ AI-11: CLI SDK chuẩn thiếu cửa cấp cấu hình DEMO + máy Local giả, hiện 0/3 CHUA_CAU_HINH; không thay cổng nghiệm thu bằng harness.
- Nếu cần tự tìm toàn LAN/Tailscale: cần nguồn danh sách IP ứng viên qua cửa chung hoặc thống nhất phạm vi quét/hạn thời gian. Hiện không có nguồn này trong hợp đồng; không phải chặn phần tìm hữu hạn đã kiểm.
- Không có câu hỏi nghiệp vụ mới chờ Anh; không yêu cầu cửa F/bí mật trong UI-AI-1.

### Kết quả kiểm cuối UI-AI-1

Windows x64, Python 3.13.14, Node 24.18.0, venv `.venv` trong worktree. Cài SDK 2.2.0 offline `--no-index --no-deps`; SHA-256 wheel `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984` khớp SHA256SUMS.txt. Phụ thuộc test sao offline từ distribution đã cài, theo tests/requirements.lock; không thêm dependency. Đặt PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1, PYTEST_DISABLE_PLUGIN_AUTOLOAD=1.

```text
.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_hoi_ai/goi/e_hoi_ai
0/3 ĐẠT: cả ba ví dụ CHUA_CAU_HINH; mã thoát 1.
Engine e_hoi_ai 0.12.0: có ví dụ chạy thử DEMO chưa đạt.

.venv/Scripts/python -B -m pytest e_hoi_ai/tests -q --basetemp=.pytest-tmp-ui-ai-1-ban-giao --tb=short
663 passed in 465.66s (0:07:45); 0 skipped; mã thoát 0.

.venv/Scripts/python -B e_hoi_ai/tests/kiem_doc_lap.py
[ĐẠT] Gói độc lập: không tham chiếu Core, không có tệp biên dịch hay liên kết.
Mã thoát 0.

node --test e_hoi_ai/tests/ui/cau_hinh.test.mjs
24 tests, 24 pass, 0 fail, 0 skipped; mã thoát 0.
Đồng thời được gọi trong test_ui_ai_8.py của lượt pytest toàn bộ.

.venv/Scripts/python -B e_hoi_ai/tests/chay_demo_voi_local_gia.py
3/3 DEMO ĐẠT, 3 lượt Local HTTP giả; AI-9 1/1 ĐẠT, 1 lượt Local HTTP giả.
Mã thoát 0; bằng chứng bổ sung, không thay CLI SDK chuẩn.

node e_hoi_ai/tests/ui/chup_anh_demo.mjs
Ảnh rộng 1160×1340, hẹp 390×2100, mất kết nối 1160×1340.
Đúng viewport, DOM không tràn ngang, KttCore giả; mã thoát 0.

Kiểm kê 29/29 tệp: bytes/SHA-256 khớp (được kiểm trong pytest toàn bộ).
git diff --check: mã thoát 0.
engine.json giữ SHA-256 cb5073b0e4423cddee82d9c7ef78b1c6fc0a2b518246cae46bb66cf533d1343f.
```

**Đã kiểm bằng Core giả (CoreGia)** và máy Local HTTP giả; không chứng nhận Core thật/model thật/Linux hoặc tự tìm toàn LAN. Không skip bài kiểm nào, không sửa SDK hoặc tạo nhánh DEMO runtime. Không commit/push; PR **chờ lead mở**.

Thời gian thực tế: **21/11/2026 21:25–21/11/2026 22:13:48 (+07), 0.81 giờ**; ước tính phiếu UI §4: **3 giờ**. Giờ bắt đầu theo lead; giờ kết thúc là lúc hoàn tất ghi báo cáo kiểm cuối.
