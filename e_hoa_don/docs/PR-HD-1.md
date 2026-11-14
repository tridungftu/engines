# [e_hoa_don] HD-1 — XML strict, tiền và vấn đề nguồn

**Bản nháp bàn giao, chưa đủ điều kiện mở PR đạt; PR: chờ lead mở.** Không commit/push.

Kết luận: **Chưa đạt** — phép chiếu/lỗi nguồn đã sửa, còn hợp đồng lỗi vượt trần tại `chay.py` ngoài phạm vi tệp đã giao. Đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật.

Đã làm: chỉ sửa runtime `doc.py`; giữ nguyên parser `hoa_don_xml.py`. Tách lỗi XML hỏng và ngoài profile, không phản chiếu nguồn, không bắt tràn DataError; nhiều TToan không còn chiếu scalar tiền mơ hồ. Giữ chuỗi định danh, Decimal exact, ABSENT/EMPTY/TEXT, occurrence, issue ngoài envelope V1, chi tiết tiền/thuế/quan hệ và handler context=None. Thêm 74 test DEMO với đáp án literal, cập nhật ca hợp đồng lỗi của HD-0.

Kết quả kiểm thực tế trên Windows, Python 3.13.14, SDK 2.0.0 cài wheel offline đúng SHA; ba lệnh dùng `-B`:

```text
.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -B -m pytest e_hoa_don/tests -q
→ 5 failed, 132 passed in 4.01s; 0 skipped; mã thoát 1
.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import, cây gói và tiến trình sạch; mã thoát 0
```

Năm test thất bại:

- `test_bytes_thuc_vuot_tran_core_metadata_nho`: CoreGia phát 413 `VUOT_GIOI_HAN_KICH_THUOC`, SDK trả `KHONG_TRAO_DOI_DUOC_CORE`; cần bọc riêng lỗi kích thước khi mở tệp.
- `test_gioi_han_read_16_mib_cong_1` và `test_vuot_16_mib_kiem_bytes_thuc_metadata_khai_thieu`: handler vẫn phát `HD_XML_VUOT_GIOI_HAN` thay `HD_XML_QUA_LON`.
- `test_bao_cao_thuc_vuot_32_mib_khong_upload` và `test_json_vuot_tran_tu_choi_truoc_upload`: handler vẫn phát `HD_JSON_VUOT_GIOI_HAN` thay `HD_KET_QUA_QUA_LON`.

Ca báo cáo quá trần sinh 400.000 occurrence SHDon trong RAM (XML <10 MiB, JSON >32 MiB); engine từ chối trước upload, nhưng mã/câu lỗi đang là bản HD-0. Ca luồng thực xác nhận `read(16 MiB + 1)`; không cắt occurrence hoặc làm xanh test bằng skip/xfail. Các test thuần kiểm context DEMO đầy đủ và mâu thuẫn không đưa context vào handler/manifest.

## Thay đổi cụ thể đề nghị cho `chay.py` (chưa áp dụng)

Vẫn chỉ hai tệp runtime tổng cộng: `doc.py` và `chay.py`; không sửa `hoa_don_xml.py`.

1. Đổi lỗi sau `read(MAX_XML_BYTES + 1)` thành `LoiNghiepVu("HD_XML_QUA_LON", "Tệp XML vượt giới hạn 16 MiB. Anh hãy gửi tệp nhỏ hơn.")`.
2. Riêng khối `viec.mo_tep`/đọc bytes: bọc `LoiDuongTruyen` có mã chính xác `VUOT_GIOI_HAN_KICH_THUOC` hoặc `LoiNghiepVu` có mã `VUOT_GIOI_HAN` thành lỗi trên; các mã khác `raise` nguyên trạng. Không bắt hủy, mất lease, DataError hoặc exception tổng quát.
3. Đổi lỗi sau kiểm `len(bao_cao) > JSON_TOI_DA_BYTE` thành `LoiNghiepVu("HD_KET_QUA_QUA_LON", "Kết quả đọc hóa đơn vượt giới hạn. Anh hãy chia nhỏ dữ liệu đầu vào.")`. Giữ vị trí trước upload, không đổi trần 32 MiB.
4. Bổ sung test lỗi mở tệp khác không bị đổi mã, kiểm biên trần và chạy lại toàn bộ ba lệnh. Chỉ đổi trạng thái HD-1 khi không còn lỗi.

Lệch khỏi phiếu / quyết định tạm: chưa mở rộng tệp khi chưa có xác nhận. Giữ context=None, không ChuaRo cho thiếu context, không ZIP/bảng kê/portal/Cloud. Giữ phạm vi XML DEMO, không sửa ma-nguon/SDK/Core.

Thời gian thực tế đến mốc chờ xác nhận: khoảng **0.17 giờ** (01:11–01:21, 15/11/2026, UTC+07); ước tính trong phiếu: **3 giờ**. Đây chưa phải báo cáo hoàn tất lát.

Cần Core / Chờ Anh mới phát sinh: cần chốt cặp tệp runtime `doc.py` + `chay.py`; ghi nợ SDK ánh xạ lỗi kích thước tải tệp 413 thành lỗi giới hạn chung. Không cần API/ngữ cảnh mới để hoàn tất HD-1. Chưa chạy Linux, máy sạch HD-4 hoặc Core thật.
