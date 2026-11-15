# Báo cáo MASK-R5 — tiếp lát từ 23:50 ngày 15/11/2026

Kết luận: **Đạt điều kiện tiếp MASK-R5** — full pytest 0 failed, kiểm độc lập mã 0, kiểm kê LF khớp. **Chưa đạt nghiệm thu chung** vì CLI DEMO chuẩn vẫn thiếu quyền Core (0/2); không nhận runtime đã nối Core thật.

Đã làm: **207 ca (a)** giữ mục tiêu an toàn với fixture RAM/SDK 2.2.0; **9 ca (b)** bỏ kỳ vọng lưu/khôi phục snapshot Core và kiểm điều ngược lại. Ba fixture snapshot cùng bản công cụ cũ được giữ nguyên trong `e_mask/LUU-TRU/mask_2c_snapshot_core/`; các bộ test hiện hành vẫn ở `tests/`. Danh mục dùng alias chính thức DEMO và ngăn SDK thật, đọc null+cờ; tên mới thiếu C-P4-03 vẫn bị chặn. Bốn xfailed cũ giữ nguyên.

Kết quả kiểm: **2523 passed, 0 failed, 4 xfailed cũ, 190 subtests passed, 0 skipped; 378,34 giây**, mã 0. Kiểm độc lập mã 0; kiểm kê **52/52 tệp bytes LF/SHA-256** khớp; `git diff --check` mã 0. Collection thật giữ **216/216 node ID cũ**, đủ 207 ca (a) và 9 ca (b), không thiếu ca; hai ca mới giữ chặn trường KHAC xung đột nhóm. Marker skip/xfail đối chiếu AST giữ nguyên, bốn xfailed MASK-2b vẫn cùng lý do giới hạn quy tắc/nợ CAO. CLI **0/2 ĐẠT, mã 1**: `MASK_NGU_CANH_CHUA_XAC_MINH`. **Đã kiểm bằng Core giả (CoreGia)**; chưa Core/Local/Office/Linux thật, Cloud tắt. Lượt nền trước sửa: 2304 passed/217 failed (216 MASK-2c + một kiểm kê), không lấy focused thay full suite.

Thời gian thực tế của lượt tiếp: **23:50:00 ngày 15/11/2026 → 00:32:52 ngày 16/11/2026 (UTC+07), 0,71 giờ**. Ước tính phiếu **6–8 giờ**, độ khó **kho**. Bản báo cáo lượt 22:17 được giữ riêng trong LUU-TRU; không cộng thời gian đó vào lượt tiếp này.

Lệch khỏi phiếu / quyết định tạm đã dùng: theo lệnh tiếp lát của Anh, giữ `chuyen_tiep.mask_2c.ho_so` đúng hình dạng AI-9, với `tep_id=ram-<mã opaque>`, tên cố định, MIME, độ dài và `bam_ho_so` tính trong RAM. Đây chỉ là metadata đối chiếu, không tệp tồn tại; runtime không gọi cửa đọc/ghi hồ sơ, không khôi phục khi mất RAM. AI-9 được kiểm nguyên bản, **không sửa e_hoi_ai**, schema/contract chung, Core/SDK hay dependency. Sửa thêm nhánh lỗi tài nguyên R5 để giữ mã lỗi fail-closed hiện hành. Không merge/commit/push; PR: **chờ lead mở**.

Cần Core / Chờ Anh mới phát sinh: **Cần phối hợp AI-9: bỏ yêu cầu snapshot Core** (lead giao AI-13). C-P4-01/02/04/05 còn mở: ghim instance, quyền/nguồn Local xuyên bước, vòng đời/ACK/deadline và binding port. `chay.py` chưa nối R5, thuộc R6; adapter chỉ ngoài gói. CLI DEMO chuẩn còn thiếu quyền tin cậy C-MS22-01, không bỏ chặn để làm xanh. Không phát sinh câu nghiệp vụ chờ Anh.

## Ba lệnh kiểm và kiểm kê chốt

Môi trường `.venv`: Python 3.13.14, SDK 2.2.0, jsonschema 4.26.0, pytest 9.1.1. SHA-256 wheel repo khớp `0294ec69148313784e233913d60d402efdede4c14a44ff2fe424344839534984`. Chạy với `-B`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`.

| Lệnh | Kết quả thật | Mã thoát |
|---|---|---:|
| `.venv/Scripts/python -B -m kho_tri_thuc_sdk.thu e_mask/goi/e_mask` | 0/2 ĐẠT; hai ví dụ thiếu quyền tin cậy `MASK_NGU_CANH_CHUA_XAC_MINH` | 1 |
| `.venv/Scripts/python -B -m pytest e_mask/tests -q` | 2523 passed, 4 xfailed cũ, 190 subtests passed; 0 failed/skip; 378,34 giây | 0 |
| `.venv/Scripts/python -B e_mask/tests/kiem_doc_lap.py` | ĐẠT; không tham chiếu cấm/bytecode/symlink trong gói | 0 |
| Kiểm kê `sql/kiem_ke.json` | 52/52 tệp, đúng bytes LF/SHA-256 và tập đường dẫn, trừ chính kiểm kê | 0 |
| Collection thật | 2527 ca; 216/216 node ID lỗi nền vẫn có mặt; không thiếu ca | 0 |
| `git diff --check` | ĐẠT | 0 |

Log lệnh/kết quả đầy đủ: [KET-QUA-KIEM-MASK-R5-TIEP.txt](KET-QUA-KIEM-MASK-R5-TIEP.txt). Số đo tiến trình và giờ chốt: [SO-DO-KIEM-MASK-R5-TIEP.json](SO-DO-KIEM-MASK-R5-TIEP.json). Bốn bản fixture/công cụ lịch sử khớp Git HEAD trên bytes LF; không xóa tệp, không commit/push.

## Phương pháp và giới hạn

- (a) Giữ assertion an toàn, số trường hợp và ngưỡng; fixture gọi handler R5 thật với kho R4, CoreGia SDK 2.2.0 và nguồn Local giả. Những mốc I/O snapshot đã mất chuyển sang mốc RAM/port tương ứng. Bộ Unicode vẫn giữ đầy đủ chuỗi NFD/Cf/selector/emoji, chỉ cấp đúng ứng viên DEMO cho lookup chính xác.
- Các ca Local bổ sung alias dùng catalogue DEMO đã khai trước chuỗi, độc lập gold và phản hồi Local. Ngữ cảnh `gửi:`/`đang ký` tránh giả thuyết cả trường KHAC xung đột nhóm của R3; offset được tính trên chuỗi fixture thực. Không đổi hành vi detector, nới gate R3, cấp alias mới theo model hoặc biến chặn toàn bộ thành 0 lọt đạt. Hai test hồi quy mới giữ chính các đầu vào không nhãn ban đầu: xung đột nhóm vẫn fail-closed, không xuất map/kết quả.
- (b) Không còn snapshot/map/chỉ mục ở ngăn/tệp/Core; cùng RAM còn đọc được qua bước, mất RAM phải báo rõ chạy lại chuỗi. Sau chốt/ACK chưa rõ không tái tạo map hoặc cache bản rõ để chạy lại.
- Công cụ so baseline quy tắc qua bước chuẩn bị RAM, không coi public handler R3 đã phát hành; phép chấm đọc catalogue fixture đã cấp trước chuỗi, không đọc map runtime/kho bản rõ/gold để suy span. Model/transport/context và HTTP lỗi của AI-9 giữ nguyên. Không nhận chất lượng model thật hoặc đóng C-P4-03.
- Log nền: [KET-QUA-KIEM-MASK-R5-TIEP-DAU.txt](KET-QUA-KIEM-MASK-R5-TIEP-DAU.txt). Báo cáo trước lượt tiếp được lưu cùng thư mục lịch sử, không xóa. Bảng máy đọc: [PHAN-LOAI-MASK-R5.json](PHAN-LOAI-MASK-R5.json).

## Bảng phân loại đủ 216 ca

| Bộ | (a) | (b) | Tổng |
|---|---:|---:|---:|
| MASK-2c-1 | 13 | 5 | 18 |
| MASK-2c-2 | 37 | 2 | 39 |
| MASK-2c-3 | 131 | 2 | 133 |
| MASK-2c-4 | 26 | 0 | 26 |
| **Tổng** | **207** | **9** | **216** |

Tên dưới đây là node ID của lượt nền; mọi bộ tham số được liệt kê riêng, không gộp ca lỗi.

| Tên test | a/b | Cách xử lý |
|---|:---:|---|
| `test_mask_2c_1.py::test_core_gia_luu_doc_retry_chi_muc_khong_co_noi_dung` | b | Lưu/đọc/retry trên R4; spy cấm tệp/Core, bảng ho_so_ai phải rỗng. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[quyen]` | a | Dùng dấu hồ sơ RAM; sai quyền/instance/dấu/băm bị chặn, không đọc snapshot Core. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[cong]` | a | Dùng dấu hồ sơ RAM; sai quyền/instance/dấu/băm bị chặn, không đọc snapshot Core. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[tham_chieu]` | a | Dùng dấu hồ sơ RAM; sai quyền/instance/dấu/băm bị chặn, không đọc snapshot Core. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[chi_muc]` | b | Ngăn/tệp rỗng vẫn đọc được cùng RAM; kết thúc RAM phải lỗi rõ, không tải lại hồ sơ Core. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[tep]` | b | Ngăn/tệp rỗng vẫn đọc được cùng RAM; kết thúc RAM phải lỗi rõ, không tải lại hồ sơ Core. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[metadata]` | a | Dùng dấu hồ sơ RAM; sai quyền/instance/dấu/băm bị chặn, không đọc snapshot Core. |
| `test_mask_2c_1.py::test_thieu_quyen_tham_chieu_hash_phai_tu_choi[bam]` | a | Dùng dấu hồ sơ RAM; sai quyền/instance/dấu/băm bị chặn, không đọc snapshot Core. |
| `test_mask_2c_1.py::test_khong_doc_cheo_chu_yeu_cau[module]` | a | Scope tin cậy R4 gồm module/người/tài liệu/vùng/pháp nhân; giữ kiểm từ chối đọc chéo. |
| `test_mask_2c_1.py::test_khong_doc_cheo_chu_yeu_cau[nguoi_gui]` | a | Scope tin cậy R4 gồm module/người/tài liệu/vùng/pháp nhân; giữ kiểm từ chối đọc chéo. |
| `test_mask_2c_1.py::test_khong_doc_cheo_chu_yeu_cau[tai_lieu]` | a | Scope tin cậy R4 gồm module/người/tài liệu/vùng/pháp nhân; giữ kiểm từ chối đọc chéo. |
| `test_mask_2c_1.py::test_khong_doc_cheo_chu_yeu_cau[vung]` | a | Scope tin cậy R4 gồm module/người/tài liệu/vùng/pháp nhân; giữ kiểm từ chối đọc chéo. |
| `test_mask_2c_1.py::test_khong_doc_cheo_chu_yeu_cau[phap_nhan_id]` | a | Scope tin cậy R4 gồm module/người/tài liệu/vùng/pháp nhân; giữ kiểm từ chối đọc chéo. |
| `test_mask_2c_1.py::test_snapshot_qua_hai_buoc_core_cung_quyen` | b | Hai bước chỉ đọc cùng RAM; Core/ngăn không có hồ sơ; mất RAM trả MASK_ANH_XA_KHONG_CON. |
| `test_mask_2c_1.py::test_bam_bytes_sai_va_map_sai_du_co_bam_moi_khong_doc` | a | Sửa dữ liệu RAM/băm hoặc map thuần trong RAM; cả hai vẫn bị kiểm từ chối. |
| `test_mask_2c_1.py::test_khong_tai_dung_cung_ma_khi_noi_dung_doi` | a | Cùng mã R4 với nội dung khác bị từ chối và dọn; không tạo snapshot dự phòng. |
| `test_mask_2c_1.py::test_chua_ro_cas_huy_va_loi_port_khong_lo_noi_dung` | a | Chạy handler R5/R4 thật qua CoreGia: ACK chưa rõ giữ TTL, retry không trùng; hủy/lỗi không rò. |
| `test_mask_2c_1.py::test_xung_dot_ngan_khong_tra_tham_chieu` | b | Không còn giao dịch chỉ mục snapshot; cấm upload, ngăn rỗng, mất RAM phải lỗi rõ. |
| `test_mask_2c_2.py::test_cau_truc_yeu_cau_sha_profile_schema_va_khong_ro_map_ten` | a | Kiểm băm/profile/schema trên RAM; ho_so chỉ metadata ram-…, không tệp/giá trị gốc/map ở chuyển tiếp. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\u200b-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\u200b-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\u200f-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\u200f-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\ufe0f-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\ufe0f-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\U000e0100-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\U000e0100-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\t-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\t-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\xa0-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\xa0-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\n-NFC]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_local_giu_nguyen_goc_unicode_map_snapshot[\n-NFD]` | a | R4 + alias DEMO đã duyệt đúng ứng viên Unicode; giữ toàn bộ NFC/NFD/Cf/tab/NBSP/newline và băm. |
| `test_mask_2c_2.py::test_nfd_cf_thuc_su_giu_nguyen_bytes` | a | Cấp đúng biến thể DEMO trong kho bí mật; Local và RAM giữ nguyên bytes NFD/Cf/selector. |
| `test_mask_2c_2.py::test_lop_2b_con_sot_van_chan[l\xea th\u1ecb hoa \u0111\u01a1n g\u1ed1c; 1.000.000 VND ng\xe0y 30/10/2026; n\u1ed9i dung DEMO.]` | a | Không tự duyệt tên detector đề nghị; fixture catalogue hữu hạn, lớp 1 còn sót vẫn chặn trước Local. |
| `test_mask_2c_2.py::test_lop_2b_con_sot_van_chan[john smith \u0111\xe3 k\xfd h\u1ee3p \u0111\u1ed3ng DEMO.]` | a | Không tự duyệt tên detector đề nghị; fixture catalogue hữu hạn, lớp 1 còn sót vẫn chặn trước Local. |
| `test_mask_2c_2.py::test_lop_2b_con_sot_van_chan[Mai sau khi nh\u1eadn h\xf3a \u0111\u01a1n s\u1ebd h\u1ea1ch to\xe1n v\xe0o t\xe0i kho\u1ea3n 331.]` | a | Không tự duyệt tên detector đề nghị; fixture catalogue hữu hạn, lớp 1 còn sót vẫn chặn trước Local. |
| `test_mask_2c_2.py::test_huy_kiem_o_cac_cua_khong_tra_ket_qua[kiem_ngan_sach]` | a | Giữ ba ca hủy; mốc luu lịch sử chuyển sang chi_so_doan trong vòng đời RAM; không phát hành. |
| `test_mask_2c_2.py::test_huy_kiem_o_cac_cua_khong_tra_ket_qua[luu]` | a | Giữ ba ca hủy; mốc luu lịch sử chuyển sang chi_so_doan trong vòng đời RAM; không phát hành. |
| `test_mask_2c_2.py::test_huy_kiem_o_cac_cua_khong_tra_ket_qua[ban_giao]` | a | Giữ ba ca hủy; mốc luu lịch sử chuyển sang chi_so_doan trong vòng đời RAM; không phát hành. |
| `test_mask_2c_2.py::test_retry_sdk_mat_ack_khong_cap_alias_dem_lan_hai` | a | ACK SDK gửi lại đúng một kết quả, alias/số gặp giữ nguyên; không alias tạm/map ở ngăn. |
| `test_mask_2c_2.py::test_giao_lai_cung_ma_snapshot_y_nguyen_khong_cap_lai` | a | Retry cùng mã dùng nguyên RAM/dấu/băm/hạn tuyệt đối; không ghi lại ngăn/tệp hoặc đếm thêm. |
| `test_mask_2c_2.py::test_retry_mat_snapshot_doi_ghim_khong_phat_hanh[snapshot]` | a | Thay snapshot bằng bản ghi RAM: mất RAM/băm/prompt/profile/hạn/quyền đổi đều chặn, không phục hồi. |
| `test_mask_2c_2.py::test_retry_mat_snapshot_doi_ghim_khong_phat_hanh[bam]` | a | Thay snapshot bằng bản ghi RAM: mất RAM/băm/prompt/profile/hạn/quyền đổi đều chặn, không phục hồi. |
| `test_mask_2c_2.py::test_retry_mat_snapshot_doi_ghim_khong_phat_hanh[prompt]` | a | Thay snapshot bằng bản ghi RAM: mất RAM/băm/prompt/profile/hạn/quyền đổi đều chặn, không phục hồi. |
| `test_mask_2c_2.py::test_retry_mat_snapshot_doi_ghim_khong_phat_hanh[profile]` | a | Thay snapshot bằng bản ghi RAM: mất RAM/băm/prompt/profile/hạn/quyền đổi đều chặn, không phục hồi. |
| `test_mask_2c_2.py::test_retry_mat_snapshot_doi_ghim_khong_phat_hanh[han]` | a | Thay snapshot bằng bản ghi RAM: mất RAM/băm/prompt/profile/hạn/quyền đổi đều chặn, không phục hồi. |
| `test_mask_2c_2.py::test_retry_mat_snapshot_doi_ghim_khong_phat_hanh[quyen]` | a | Thay snapshot bằng bản ghi RAM: mất RAM/băm/prompt/profile/hạn/quyền đổi đều chặn, không phục hồi. |
| `test_mask_2c_2.py::test_chua_ro_sau_luu_retry_khong_cap_alias_lan_hai` | a | Tiêm ChuaRo tại ban_giao sau khi giữ RAM, retry trong hạn dùng cùng dấu/alias và không gia hạn. |
| `test_mask_2c_2.py::test_tep_json_nhu_che_hien_tai_va_chan_ma_tu_khai` | a | Fixture R4 + ngăn SDK 2.2.0; giữ kiểm chuẩn bị/nguồn/trần/không rò và Cloud tắt. |
| `test_mask_2c_2.py::test_core_dieu_phoi_tung_doan_giu_lap_nguon_va_khong_ro_chuyen_tiep` | a | Dấu RAM R4 dựng từng yêu cầu; giữ chỉ số/biên/băm, từ chối bool/ngoài kế hoạch. |
| `test_mask_2c_2.py::test_0_goi_engine_khac_0_cloud_khong_ghi_dia` | a | Fixture R4 + ngăn SDK 2.2.0; giữ kiểm chuẩn bị/nguồn/trần/không rò và Cloud tắt. |
| `test_mask_2c_2.py::test_van_ban_tai_lieu_khong_chuyen_ocr_metadata_ra_ai` | a | Fixture R4 + ngăn SDK 2.2.0; giữ kiểm chuẩn bị/nguồn/trần/không rò và Cloud tắt. |
| `test_mask_2c_2.py::test_prompt_injection_chi_la_noi_dung_local_khong_doi_prompt` | a | Fixture R4 + ngăn SDK 2.2.0; giữ kiểm chuẩn bị/nguồn/trần/không rò và Cloud tắt. |
| `test_mask_2c_2.py::test_cas_chot_ho_so_rollback_retry_khong_nhan_doi_alias` | b | Không ghi chỉ mục snapshot/CAS hồ sơ; mất RAM không dựng lại; alias chính thức không đổi. |
| `test_mask_2c_2.py::test_buoc_core_doc_lap_khong_doc_ngan_engine_khac` | b | Không Core nào có bảng snapshot/map; Core khác không thấy kho; đọc SDK đúng null+cờ. |
| `test_mask_2c_2.py::test_thieu_tai_nguyen_lop_1_khong_phat_hanh` | a | Thiếu tài nguyên tại runtime R5 vẫn fail-closed và trả đúng MASK_THIEU_TAI_NGUYEN, không rò. |
| `test_mask_2c_3.py::test_ten_lop_mot_lot_ai_che_them_giu_tien_ngay_khong_ro_log` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ba_loai_khong_can_danh_sach_ho[nguoi]` | a | Ba nhóm dùng alias DEMO chính thức qua ngăn SDK; fixture gửi: tránh giả thuyết cả trường KHAC; không bỏ Local. |
| `test_mask_2c_3.py::test_ba_loai_khong_can_danh_sach_ho[to_chuc]` | a | Ba nhóm dùng alias DEMO chính thức qua ngăn SDK; fixture gửi: tránh giả thuyết cả trường KHAC; không bỏ Local. |
| `test_mask_2c_3.py::test_ba_loai_khong_can_danh_sach_ho[dia_chi]` | a | Ba nhóm dùng alias DEMO chính thức qua ngăn SDK; fixture gửi: tránh giả thuyết cả trường KHAC; không bỏ Local. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\u200b-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\u200b-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\u200f-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\u200f-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\ufe0f-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\ufe0f-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\U000e0100-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\U000e0100-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\t-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\t-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\xa0-NFC]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_unicode_code_point_nfd_cf_selector_ten_lap[\xa0-NFD]` | a | Giữ emoji/NFD/Cf/selector/tên lặp/trùng; đặt ngữ cảnh gửi: và tính lại offset fixture theo chuỗi thực. |
| `test_mask_2c_3.py::test_khong_replace_toan_cuc_chi_che_lan_ai_xac_nhan` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_da_che_toan_phan_giu_nguyen_alias_khong_mo_che` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[nghi_ngo]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[loai_mau_thuan]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[muc_mau_thuan]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[long_span]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[bien_tu]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[tien]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[ngay]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nghi_van_chong_lan_bien_va_vung_bao_ve_chan[alias]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_hop_le_can_du_nguon_va_khuon` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[du_lieu-None]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[du_lieu-gia_tri1]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[du_lieu-gia_tri2]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[du_lieu-gia_tri3]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[trang_thai-co_can_cu]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[kiem_trich_dan-gia_tri5]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[kiem_trich_dan-gia_tri6]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[nha_cung_cap-cloud]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[canh_bao-gia_tri8]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[bam_dau_vao-sha256:0000000000000000000000000000000000000000000000000000000000000000]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[ma_prompt-gia]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[phien_ban_prompt-99]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_rong_gia_sai_bam_khuon_metadata_khong_thanh_cong[model-model-cloud]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_span_sai_hoac_khoa_la[bat_dau]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_span_sai_hoac_khoa_la[ket_thuc]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_span_sai_hoac_khoa_la[loai]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_span_sai_hoac_khoa_la[muc]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_span_sai_hoac_khoa_la[nguyen_van]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_span_sai_hoac_khoa_la[them]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_core_khong_tin_co_caller[khong_chung_thuc]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_core_khong_tin_co_caller[nguon_khac]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_core_khong_tin_co_caller[finish_length]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_core_khong_tin_co_caller[thieu_finish]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_core_khong_tin_co_caller[trich_dan_gia]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_core_khong_tin_co_caller[sha_tai_lieu]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_du_dung_tat_ca_doan_va_local_moi_doan[thieu]` | a | R4 giao thực sự mọi đoạn; tập phản hồi không mang yêu cầu/gốc/map; sai kế hoạch sửa trực tiếp RAM để kiểm. |
| `test_mask_2c_3.py::test_du_dung_tat_ca_doan_va_local_moi_doan[dao_thu_tu]` | a | R4 giao thực sự mọi đoạn; tập phản hồi không mang yêu cầu/gốc/map; sai kế hoạch sửa trực tiếp RAM để kiểm. |
| `test_mask_2c_3.py::test_du_dung_tat_ca_doan_va_local_moi_doan[cloud_mot_doan]` | a | R4 giao thực sự mọi đoạn; tập phản hồi không mang yêu cầu/gốc/map; sai kế hoạch sửa trực tiếp RAM để kiểm. |
| `test_mask_2c_3.py::test_du_dung_tat_ca_doan_va_local_moi_doan[lap]` | a | R4 giao thực sự mọi đoạn; tập phản hồi không mang yêu cầu/gốc/map; sai kế hoạch sửa trực tiếp RAM để kiểm. |
| `test_mask_2c_3.py::test_du_dung_tat_ca_doan_va_local_moi_doan[ke_hoach]` | a | R4 giao thực sự mọi đoạn; tập phản hồi không mang yêu cầu/gốc/map; sai kế hoạch sửa trực tiếp RAM để kiểm. |
| `test_mask_2c_3.py::test_du_dung_tat_ca_doan_va_local_moi_doan[rong_mau_thuan]` | a | R4 giao thực sự mọi đoạn; tập phản hồi không mang yêu cầu/gốc/map; sai kế hoạch sửa trực tiếp RAM để kiểm. |
| `test_mask_2c_3.py::test_gom_trung_overlap_dung_span_giu_lan_xuat_hien` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[ma_yeu_cau]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[bam_goc]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[bam_da_che_quy_tac]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[bam_prompt]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[bam_khuon]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[bam_profile]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[phien_ban_map]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[he_offset]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_gia_profile_va_bam[nha_cung_cap_bat_buoc]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_sai_quyen_tung_chieu[module]` | a | Giữ đủ sáu chiều quyền tin cậy qua R4 và port Local; không dùng ACL tệp snapshot. |
| `test_mask_2c_3.py::test_sai_quyen_tung_chieu[nguoi_gui]` | a | Giữ đủ sáu chiều quyền tin cậy qua R4 và port Local; không dùng ACL tệp snapshot. |
| `test_mask_2c_3.py::test_sai_quyen_tung_chieu[tai_lieu]` | a | Giữ đủ sáu chiều quyền tin cậy qua R4 và port Local; không dùng ACL tệp snapshot. |
| `test_mask_2c_3.py::test_sai_quyen_tung_chieu[vung]` | a | Giữ đủ sáu chiều quyền tin cậy qua R4 và port Local; không dùng ACL tệp snapshot. |
| `test_mask_2c_3.py::test_sai_quyen_tung_chieu[phien]` | a | Giữ đủ sáu chiều quyền tin cậy qua R4 và port Local; không dùng ACL tệp snapshot. |
| `test_mask_2c_3.py::test_sai_quyen_tung_chieu[phap_nhan_id]` | a | Giữ đủ sáu chiều quyền tin cậy qua R4 và port Local; không dùng ACL tệp snapshot. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[sha]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[size]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[path]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[url]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[ten_tep]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[thu_hoi]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_snapshot_tap_quyen_tham_chieu_sai[thieu_port]` | a | ho_so chỉ metadata RAM; giả băm/size/path/URL/tệp bổ sung hoặc thiếu quyền/port đều bị chặn. |
| `test_mask_2c_3.py::test_json_tap_nghiem[{"phien_ban":1,"phien_ban":1}]` | a | Tiêm bytes JSON trực tiếp vào port nhan_phan_hoi, giữ khóa trùng/NaN/Infinity/JSON hỏng bị chặn. |
| `test_mask_2c_3.py::test_json_tap_nghiem[{"x":NaN}]` | a | Tiêm bytes JSON trực tiếp vào port nhan_phan_hoi, giữ khóa trùng/NaN/Infinity/JSON hỏng bị chặn. |
| `test_mask_2c_3.py::test_json_tap_nghiem[{"x":Infinity}]` | a | Tiêm bytes JSON trực tiếp vào port nhan_phan_hoi, giữ khóa trùng/NaN/Infinity/JSON hỏng bị chặn. |
| `test_mask_2c_3.py::test_json_tap_nghiem[{}]` | a | Tiêm bytes JSON trực tiếp vào port nhan_phan_hoi, giữ khóa trùng/NaN/Infinity/JSON hỏng bị chặn. |
| `test_mask_2c_3.py::test_json_tap_nghiem[{]` | a | Tiêm bytes JSON trực tiếp vào port nhan_phan_hoi, giữ khóa trùng/NaN/Infinity/JSON hỏng bị chặn. |
| `test_mask_2c_3.py::test_loi_timeout_chuaro_huy_lease_cas_khong_phat_hanh[timeout]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_loi_timeout_chuaro_huy_lease_cas_khong_phat_hanh[chua_ro]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_loi_timeout_chuaro_huy_lease_cas_khong_phat_hanh[huy]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_loi_timeout_chuaro_huy_lease_cas_khong_phat_hanh[mat_lease]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_loi_timeout_chuaro_huy_lease_cas_khong_phat_hanh[cas]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_loi_timeout_chuaro_huy_lease_cas_khong_phat_hanh[sau_ban_giao]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_prompt_injection_chi_la_du_lieu_khong_thuc_thi` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_mat_ack_core_ban_giao_retry_khong_cap_alias_dem_lan_nua` | b | Sau bàn giao chưa rõ phải dọn RAM; retry không tái tạo map, không cấp alias/đếm thêm. |
| `test_mask_2c_3.py::test_con_sot_noi_bo_khong_chua_nguyen_van` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_khong_tin_co_kiem_tien_ngay_hay_ai_de_go_chan_cu[thieu_tai_nguyen]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_khong_tin_co_kiem_tien_ngay_hay_ai_de_go_chan_cu[hau_kiem_cu_loi]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_khong_tin_co_kiem_tien_ngay_hay_ai_de_go_chan_cu[tien_ngay_sai]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_khong_tin_co_kiem_tien_ngay_hay_ai_de_go_chan_cu[hau_kiem_chua_du]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[map]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[bam_goc]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[quy_tac_con_sot]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[quy_tac_tien_ngay]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[quy_tac_gui_duoc]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[profile]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[khuon]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_snapshot_sai_du_sha_bytes_dung_van_chan[prompt]` | a | Sửa hồ sơ/map/profile ngay RAM và tính lại SHA; kiểm ngữ nghĩa vẫn chặn, không upload. |
| `test_mask_2c_3.py::test_nfd_khong_duoc_cat_dau_ket_hop` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_che_prefix_khong_duoc_coi_che_toan_ten` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_cas_ngan_thuc_su_sai_version_rollback_alias_hang_cho` | a | Gây CAS sai row_version thật qua SDK ở port chứng thực; rollback metadata/alias, không bàn giao, dọn RAM. |
| `test_mask_2c_3.py::test_vuot_100_lenh_khong_chia_lo_gia_nguyen_tu` | b | Bỏ kỳ vọng lô lưu map cũ; spy cấm mọi lô ghi, 24 tên mới bị chặn, không ghi một phần. |
| `test_mask_2c_3.py::test_thu_hoi_quyen_huy_het_han_giua_cac_cua[han]` | a | Đổi mốc commit snapshot sang trước/sau chốt RAM/bàn giao; giữ đầy đủ năm ca thu hồi/hạn. |
| `test_mask_2c_3.py::test_thu_hoi_quyen_huy_het_han_giua_cac_cua[chung_thuc]` | a | Đổi mốc commit snapshot sang trước/sau chốt RAM/bàn giao; giữ đầy đủ năm ca thu hồi/hạn. |
| `test_mask_2c_3.py::test_thu_hoi_quyen_huy_het_han_giua_cac_cua[truoc_commit]` | a | Đổi mốc commit snapshot sang trước/sau chốt RAM/bàn giao; giữ đầy đủ năm ca thu hồi/hạn. |
| `test_mask_2c_3.py::test_thu_hoi_quyen_huy_het_han_giua_cac_cua[sau_commit]` | a | Đổi mốc commit snapshot sang trước/sau chốt RAM/bàn giao; giữ đầy đủ năm ca thu hồi/hạn. |
| `test_mask_2c_3.py::test_thu_hoi_quyen_huy_het_han_giua_cac_cua[sau_ban_giao]` | a | Đổi mốc commit snapshot sang trước/sau chốt RAM/bàn giao; giữ đầy đủ năm ca thu hồi/hạn. |
| `test_mask_2c_3.py::test_mat_ack_sdk_ket_qua_chi_nop_cung_mot_ban` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_timeout_sau_ghi_chung_cu_la_chua_ro` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_nguon_da_nhan_ai_chua_tra_khong_thanh_rong` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[module]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[nguoi_gui]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[tai_lieu]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[phien]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[ma_luot]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[phap_nhan_id]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_ngucanh_bi_doi_trong_port_phai_dung[dau_vao]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_selector_cf_cuoi_ten_khong_lam_mat_bien_unicode[\u200b]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_selector_cf_cuoi_ten_khong_lam_mat_bien_unicode[\u200f]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_selector_cf_cuoi_ten_khong_lam_mat_bien_unicode[\ufe0f]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_selector_cf_cuoi_ten_khong_lam_mat_bien_unicode[\U000e0100]` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_3.py::test_cf_noi_hai_phan_tu_khong_cho_che_prefix` | a | Tập Local qua port RAM + ngăn SDK thật; giữ kiểm span/đủ đoạn/nguồn/tiền-ngày và fail-closed. |
| `test_mask_2c_4.py::test_toan_chuoi_model_va_network_checks_nguyen_ban[False]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_toan_chuoi_model_va_network_checks_nguyen_ban[True]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_nfd_cf_selector_lap[orvella linero]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_nfd_cf_selector_lap[a\u0301nh veloria]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_nfd_cf_selector_lap[orvella\u200b linero]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_nfd_cf_selector_lap[orvella\u200f linero]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_nfd_cf_selector_lap[orvella linero\ufe0f]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_nhieu_doan_overlap_du_va_khong_gui_gold` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_hai_lop_bon_ca_lead_cu_ai_bao_du[m\u1ea1c \u0111\u0129nh chi-m\u1ea1c \u0111\u0129nh chi]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_hai_lop_bon_ca_lead_cu_ai_bao_du[l\u01b0\u01a1ng th\u1ebf vinh-l\u01b0\u01a1ng th\u1ebf vinh]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_hai_lop_bon_ca_lead_cu_ai_bao_du[t\u1eeb minh t\xe2m-t\u1eeb minh t\xe2m]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_hai_lop_bon_ca_lead_cu_ai_bao_du[v\u0103n ti\u1ebfn d\u0169ng-ph\u1ee5 tr\xe1ch h\u1ea1ng m\u1ee5c: v\u0103n ti\u1ebfn d\u0169ng]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_ai_bao_thieu_mot_phan_ten_van_lot_khong_duoc_tuyen_bo_cuu_het` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_da_thay_lot_van_khong_dat_khi_ca_khac_loi_ky_thuat` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_loi_ky_thuat_va_chua_ro_khong_thanh_0_dat[cat]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_loi_ky_thuat_va_chua_ro_khong_thanh_0_dat[202]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_loi_ky_thuat_va_chua_ro_khong_thanh_0_dat[timeout]` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_thieu_doan_hau_kiem_chan_ky_thuat` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_bao_nham_dem_tu_ca_thuong_chay_thuc_bang_mock` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_bao_cao_khong_ro_goc_url_path_ma_yeu_cau` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_tach_chan_truoc_ai_khoi_ai_do_va_mau_so_bao_nham` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_ngoai_le_giua_chung_giu_ca_xong_va_danh_dau_ca_chua_do` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_timeout_cung_cli_dung_child_va_ghi_bao_cao_tung_phan` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_che_thua_dinh_danh_qua_toan_chuoi_local_gia` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_ngoai_le_tien_trinh_cli_van_ghi_ca_truoc` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
| `test_mask_2c_4.py::test_timeout_cung_giu_dem_doan_ai_da_xong` | a | Công cụ nối RAM R4 + AI-9 nguyên bản + HTTP loopback giả; giữ số đo/ngưỡng/timeout/Cloud tắt. |
