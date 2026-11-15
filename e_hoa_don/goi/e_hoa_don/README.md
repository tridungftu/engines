# Đọc XML hóa đơn — HD-4

Gói SDK 2.0.0, phiên bản 1.0.0; một năng lực `hoa_don.doc_xml@2` nhận `tep` XML và trả `truong`. Bộ đọc strict chỉ hỗ trợ profile `DEMO_M2_XML_QD1271_FIELDS_V1`. Đã kiểm bằng Core giả (CoreGia), chưa nghiệm thu Core thật.

## Dữ liệu vào và ra

Đầu vào là tham chiếu tệp của Core, MIME `application/xml` hoặc `text/xml`, tối đa 16 MiB; handler đọc tối đa 16 MiB + 1 trước parse. Thời hạn bước 600 giây, hỗ trợ hủy qua SDK. Không nhận đường dẫn máy hoặc context từ tham số; `tham_so` và `loai_du_lieu_rieng` đều rỗng.

Trần vận hành **1.000 dòng hàng hóa (`HHDVu`) trên một XML**. Lý do: mỗi dòng sinh nhiều DTO/occurrence/locator trong JSON; kiểm HD-0 đã ghi nhận ca 200.000 dòng mất 66 giây và giới hạn 32 MiB chỉ chặn sau khi dựng JSON. Chọn 1.000 để giới hạn sớm mức khuếch đại theo số dòng trong đợt DEMO, chưa có corpus thật để hiệu chỉnh; đây không phải giới hạn pháp lý của hóa đơn. XML parser tiền kiểm chỉ đếm sự kiện mở phần tử, không dựng cây/DTO/JSON, dừng ngay ở dòng 1.001 bằng `LoiNghiepVu("HD_QUA_NHIEU_DONG_HANG", "Tệp XML vượt giới hạn 1.000 dòng hàng hóa. Anh hãy gửi tệp ít dòng hơn.")`. Đếm mọi phần tử `HHDVu` không namespace, gồm dòng rỗng hoặc trùng STT/mã hàng; không đếm chuỗi trong comment/CDATA, không cắt dòng. Bộ đọc strict vẫn kiểm path/namespace và bảo toàn occurrence cho đầu vào trong trần.

18 trường trả về đúng phiếu giao §2.2:

| Trường | Kiểu |
|---|---|
| `mau_so`, `ky_hieu`, `so_hoa_don` | `van_ban` |
| `ngay_lap` | `ngay` (`YYYY-MM-DD`) |
| `ma_so_thue_ban`, `ma_so_thue_mua`, `don_vi_tien` | `van_ban` |
| `tien_truoc_thue`, `tien_thue`, `tong_thanh_toan` | `so_tien` |
| `so_dong` | `so` |
| `can_kiem_tra` | `co_khong` |
| `canh_bao`, `nguon_doc`, `phien_ban_engine`, `bam_dau_vao` | `van_ban` |
| `tep_xml`, `chi_tiet_nguon` | `tep` |

Số hóa đơn giữ chuỗi và số 0 đầu. Tiền lấy đúng nguồn, ví dụ `{"so":"1000000.123456","tien_te":"VND"}`, chuyển Decimal bằng `format(value, "f")`; không float/round/tính lại tổng. Thiếu, sai, trùng hoặc mixed content thì trả `null`; thiếu currency không mặc định VND. Vượt miền 18 chữ số phần nguyên/6 chữ số thập phân: trường tiền là `null`, số exact và issue vẫn trong báo cáo. Tổng mâu thuẫn giữ các số nguồn và bật cảnh báo; `tien_truoc_thue` bao gồm phần không chịu thuế theo `TgTCThue`.

`tep_xml` giữ nguyên đối tượng tệp đầu vào, không yêu cầu UUID hoặc upload lại XML. `chi_tiet_nguon` là tham chiếu upload thành công của tệp `hoa-don-chi-tiet.json` (MIME `application/json`). Không trả kết quả nếu upload lỗi. Báo cáo kỹ thuật có schema `contract/bao_cao_xml.schema.json`, phiên bản 1: nguồn/phiên bản/băm bytes, tham chiếu XML và `chi_tiet_nguon = ra_json(InvoiceReadResult)`; `van_de_phep_chieu` bổ sung issue của phép chiếu. Không tự tham chiếu ID báo cáo. Giữ occurrence, thứ tự dòng, locator, hash, raw_ref, Decimal exact, money/relations và lý do ứng viên; loại raw bytes khỏi JSON. Trần JSON kỹ thuật 32 MiB là giới hạn đề xuất chưa đo trên corpus lớn, vượt thì từ chối trước upload.

SDK hiện chưa có cửa context nghiệp vụ được kiểm quyền. Handler luôn truyền `context=None`: đọc nguồn có thể `XONG` nhưng `can_kiem_tra=true`, giữ `CONTEXT_ABSENT`, `IDENTITY_UNRESOLVED`, định danh và semantic digest `null`. Thuế luôn `UNKNOWN`, ghi nhận nghiệp vụ `NOT_PERFORMED`. Đây là bước đọc kỹ thuật; không chứng nhận chữ ký số, hợp lệ thuế hoặc đủ điều kiện hạch toán.

XML hỏng trả `HD_XML_KHONG_DOC_DUOC`; encoding/DOCTYPE/namespace/path ngoài profile trả `HD_XML_NGOAI_PROFILE`. Bytes thực vượt 16 MiB trả `HD_XML_QUA_LON`; JSON vượt 32 MiB trả `HD_KET_QUA_QUA_LON` trước upload. Trần dòng không thay trần bytes/JSON: nhiều occurrence hoặc nội dung dài vẫn có thể vượt 32 MiB dù ít dòng. Các lỗi dùng `LoiNghiepVu`, câu tiếng Việt cố định không chứa nội dung/đường nguồn. Cảnh báo chỉ gồm mã do lõi sinh và câu cố định; chi tiết kỹ thuật được lưu trong kho tệp Core.

## Cấu hình máy

XML không cần cấu hình. Không đọc cấu hình ở import/khởi động/handler XML, không tạo `kho_tam`, thư mục dữ liệu hoặc tệp cấu hình mặc định.

Hàm `cau_hinh_may.doc_cau_hinh()` chỉ đọc khi tính năng cần: JSON ngoài gói từ `KTT_ENGINE_CAU_HINH`; mặc định Windows `%PROGRAMDATA%\KhoTriThuc\engines\e_hoa_don\cau_hinh.json`. Linux dùng đường DEMO test cấp; nếu không có `PROGRAMDATA` thì coi như thiếu cấu hình. Schema `contract/cau_hinh_may.schema.json` chỉ cho phép `{"phien_ban":1}`; không khóa lạ, bí mật hoặc context/pháp nhân. Tệp tối đa 64 KiB; từ chối khóa lặp, NaN và JSON sai. Thiếu tệp trả `None`; `bat_buoc=True` trả `CHUA_CAU_HINH`. Cấu hình lỗi trả `CAU_HINH_MAY_KHONG_HOP_LE`, câu cố định.

## Cài và kiểm offline

Python ≥ 3.11; runtime chỉ stdlib + SDK đã ghim trong `requirements.lock`. Wheel ở `docs/goi-gui-engine/sdk-2.0.0/` của repo, đối chiếu SHA-256 trước cài:

```text
python -m venv .venv
.venv\Scripts\python -B -m pip install --no-index --no-deps docs/goi-gui-engine/sdk-2.0.0/kho_tri_thuc_sdk-2.0.0-py3-none-any.whl
.venv\Scripts\python -B -m kho_tri_thuc_sdk.thu e_hoa_don/goi/e_hoa_don
.venv\Scripts\python -B -m pytest e_hoa_don/tests -q
.venv\Scripts\python -B e_hoa_don/tests/kiem_doc_lap.py
```

Linux thay `.venv\Scripts\python` bằng `.venv/bin/python`. Công cụ pytest là dependency kiểm thử, không đóng trong gói runtime. Dùng `-B` hoặc `PYTHONDONTWRITEBYTECODE=1` để không tạo bytecode trong gói. Kiểm độc lập quét AST (cả lazy import; từ chối loader động), cây tệp, rồi nạp SDK theo đường package chính xác trong tiến trình `-I -B -S` không site-packages/PYTHONPATH/Core/shim, chạy DEMO bằng CoreGia.

Fixture nhỏ `demo/hoa-don-DEMO.xml` hoàn toàn giả: hóa đơn `0000123`, ngày `2026-10-30`, tiền hàng 1000000 VND, thuế 100000 VND, tổng 1100000 VND. Tên/mã hàng mang nhãn DEMO; không dùng hồ sơ thật.

## Phạm vi bàn giao

Chỉ đăng ký `hoa_don.doc_xml@2`. Lead/Core quản lý phiên bản và chuyển quy trình `@1` sang `@2`; giữ bản cũ tại `ma-nguon/`. Mã ZIP đi cùng lõi là phần nội bộ chưa kích hoạt, không có handler hay DEMO ZIP. ZIP/bảng kê/tải/Node/Cloud/cổng thuế còn chờ quyết định riêng. Không sửa hoặc lưu trữ lại mã tham chiếu. HD-0…HD-4 đã kiểm bằng Core giả (CoreGia); cài sạch đã kiểm trên Windows, chưa kiểm Linux hoặc nghiệm thu Core thật.

Bộ DEMO HD-3 có ba ca trong `chay_thu_demo`: `hoa-don-DEMO.xml` (1000000 VND + 100000 VND = 1100000 VND), `hoa-don-le-DEMO.xml` (1000000.123456 VND + 100000.012345 VND = 1100000.135801 VND), `hoa-don-thieu-DEMO.xml` (thiếu ký hiệu/tổng, MST mua rỗng → null/cảnh báo). Công ty DEMO Ánh Dương là nhãn mô tả, không thêm trường Ten ngoài allowlist. Cả ba đọc kỹ thuật thành công nhưng cần kiểm tra vì context=None; TToan ngoài semantic envelope V1 vẫn giữ issue. Oracle literal và pin bytes mới nằm ngoài gói ở `tests/demo/`; pytest kiểm đầy đủ trường/JSON qua CoreGia.doc_tep. Ca âm và 1.000/1.001 dòng ở pytest; tệp lớn chỉ sinh trong DEMO tạm. Không xác nhận golden cũ khi thiếu bytes fixture gốc.

## Kiểm cài sạch HD-4

Tại gốc repo chạy `e_hoa_don\tests\KIEM-MAY-SACH.cmd` trên Windows, hoặc `sh e_hoa_don/tests/kiem_may_sach.sh` trên Linux. Kịch bản đối chiếu SHA wheel SDK, cài offline vào venv mới và sao chép gói cùng bộ kiểm ra vị trí DEMO riêng. Windows giữ thư mục DEMO tạm trong `.venv/` của workspace; Linux dùng thư mục tạm hệ thống. Kiểm cấu hình thiếu, XML và nhập độc lập bằng CoreGia. Không tự chuyển quy trình `@1` sang `@2`; lead/Core giữ bản cũ và quản lý việc chuyển. Trạng thái HOLD và `canh_bao` là lý do cần kiểm tra, không phải xác nhận nghiệp vụ.
