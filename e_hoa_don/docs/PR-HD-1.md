# [e_hoa_don] HD-1 — XML strict, tiền và vấn đề nguồn

Kết luận: **Đạt phạm vi HD-1 — đã kiểm bằng Core giả (CoreGia)**, chưa nghiệm thu Core thật. PR: **chờ lead mở**; tiêu đề `[e_hoa_don] HD-1 — XML strict, tiền và vấn đề nguồn`. Không git add/commit/push.

Đã làm:

- Giữ phần HD-1 trước: `doc.py` phân biệt XML hỏng với encoding/DOCTYPE/namespace/path ngoài profile bằng câu lỗi cố định; kiểm UTF-8 và trần bytes; không bắt tràn DataError. Nhiều TToan không chiếu scalar tiền mơ hồ. Giữ chuỗi định danh, Decimal exact, ABSENT/EMPTY/TEXT, mọi occurrence, money/relations/thuế và issue ngoài semantic envelope V1.
- `chay.py` trả đúng `HD_XML_QUA_LON` và `HD_KET_QUA_QUA_LON` theo phiếu. Chỉ ánh xạ `LoiDuongTruyen(VUOT_GIOI_HAN_KICH_THUOC)` hoặc `LoiNghiepVu(VUOT_GIOI_HAN)` trong khối mở/đọc tệp; mã khác, hủy, mất lease và lỗi invariant giữ nguyên. Vẫn đọc tối đa 16 MiB + 1, kiểm JSON 32 MiB trước upload.
- Trả nợ HD-0: trần vận hành **1.000 HHDVu/XML**. Mỗi dòng khuếch đại thành nhiều DTO/occurrence/locator; ca 200.000 dòng mất 66 giây do lead báo là căn cứ chọn trần bảo thủ cho DEMO, chưa có corpus thật để hiệu chỉnh. Đây không phải giới hạn pháp lý. XML parser tiền kiểm không dựng cây, đếm mọi phần tử HHDVu không namespace, dừng ngay ở dòng 1.001 **trước parser lõi/DTO/phép chiếu/JSON**, bằng `LoiNghiepVu("HD_QUA_NHIEU_DONG_HANG", "Tệp XML vượt giới hạn 1.000 dòng hàng hóa. Anh hãy gửi tệp ít dòng hơn.")`. Đếm cả dòng rỗng/trùng STT/mã hàng; không đếm comment/CDATA, không cắt ngầm. Trần JSON 32 MiB vẫn cần vì ít dòng nhưng nhiều occurrence/nội dung dài vẫn có thể vượt. README gói ghi giá trị và lý do.
- Thêm 20 test DEMO lượt bổ sung, tổng 157 test: năm ca đỏ cũ đã xanh; kiểm ánh xạ lỗi mở/đọc hẹp, giữ lỗi khác/hủy/mất lease/invariant, biên đúng 16 MiB và trần JSON, đúng 1.000 dòng giữ đủ thứ tự/occurrence, 1.001/200.000 dòng bị chặn trước parser lõi/JSON và không upload, comment/CDATA không bị đếm nhầm. Ca 400.000 occurrence SHDon vẫn kiểm thật JSON >32 MiB, không cắt occurrence. Không skip/xfail hoặc sinh expected từ parser.

Kết quả thật trên Windows, Python 3.13.14, SDK 2.0.0. Cả ba lệnh đặt `PYTHONDONTWRITEBYTECODE=1`:

```text
.venv\Scripts\python -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
→ 1/1 DEMO [ĐẠT], mã thoát 0
.venv\Scripts\python -m pytest e_hoa_don/tests -q -p no:cacheprovider
→ 157 passed in 5.57s; 0 skipped; mã thoát 0
.venv\Scripts\python e_hoa_don/tests/kiem_doc_lap.py
→ [ĐẠT] AST/import, cây gói và tiến trình sạch; mã thoát 0
```

Đo bổ sung một lần: XML DEMO 200.000 HHDVu rỗng, 1.600.597 bytes, `doc_xml` từ chối bằng `HD_QUA_NHIEU_DONG_HANG` sau **0.014118 giây**. Chỉ đo lượt gọi hàm thuần trên máy hiện tại, không gồm tạo fixture/I/O Core; không cam kết hiệu năng hoặc so trực tiếp với ca 66 giây khi chưa xác nhận cùng fixture.

Thời gian thực tế: lượt bổ sung khoảng **0.2 giờ**; cộng mốc trước **0.17 giờ**, tổng HD-1 khoảng **0.37 giờ** (ước tính trong phiếu: **3 giờ**); không tính chờ giữa lượt.

Lệch khỏi phiếu / quyết định đã dùng: **lead Claude**, theo phản hồi chuyển trong đầu bài, cho sửa `chay.py` cùng `doc.py`; đây là quyết định của lead, không phải của Anh. Chỉ hai tệp runtime thay đổi, trong trần ≤5; giữ nguyên parser `hoa_don_xml.py`. Thêm trần dòng theo đầu bài bổ sung. Giữ handler `context=None`, `can_kiem_tra=true`, identity/digest null; không ChuaRo cho thiếu context; không mở ZIP/bảng kê/portal/Cloud hoặc đổi API/SDK/Core/ma-nguon.

Cần Core / Chờ Anh mới phát sinh: **không có**. Giữ nợ SDK phát hiện lượt trước: CoreGia chặn bytes khi mở tệp bằng 413 `VUOT_GIOI_HAN_KICH_THUOC`; SDK 2.0.0 ánh xạ thành `KHONG_TRAO_DOI_DUOC_CORE`. Lớp bọc hẹp đã đáp ứng HD-1; đề nghị SDK có ánh xạ chung lỗi tải tệp vượt trần, không chặn bàn giao HD-1. Giữ các mục context tin cậy/quyền tệp/kênh cấu hình đã có. Chưa chạy Linux, máy sạch HD-4 hoặc Core thật.

Bàn giao đầy đủ và nguyên bản nháp lượt trước nằm trong `VIEC.md`, mục **Bàn giao HD-1**. Tệp mô tả PR này được giữ lại để lead sử dụng.
