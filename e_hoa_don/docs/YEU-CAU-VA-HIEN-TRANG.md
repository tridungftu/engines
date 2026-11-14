# e_hoa_don — Hóa đơn điện tử: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- `PHIEU-ENGINE-e_hoa_don.md`: phiếu đề xuất, **Anh chưa có quyết định cuối**.
- TL 43 (M2-00 nhận nguồn từ cổng thuế).
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

**Ký hiệu:** ✅ có / 🟡 một phần / ❌ chưa có.

## 0. Kết luận cập nhật HD-3 (mốc 14/11/2026, kiểm 15/11/2026)

- Gói SDK 2.0 tại `goi/e_hoa_don/` chỉ đăng ký `hoa_don.doc_xml@2`: một XML → đủ 18 trường + tệp JSON chi tiết. HD-0…HD-3 đã kiểm bằng Core giả (CoreGia); bằng chứng HD-3 và kết quả lệnh tại `VIEC.md`, `PR-HD-3.md`, CHANGELOG gói. Chưa nghiệm thu Core thật/quyền kho tệp, chưa chạy Linux hoặc bài Core thật 120 phút.
- HD-3 có ba XML DEMO độc lập: tiền nguyên, tiền lẻ exact và nguồn thiếu/null; đáp án literal + pin bytes tại `tests/demo/`. Fixture lớn 1.000/1.001 dòng chỉ sinh trong thư mục DEMO tạm. Tất cả mẫu handler thiếu context đều cần kiểm tra; TToan ngoài semantic envelope V1 không thành bằng chứng nội dung đầy đủ.
- Đợt XML theo `GIAO-CODEX-e_hoa_don.md`: 5 lát HD-0…HD-4, tổng **15 giờ ước tính**; HD-4 ghim nguồn/cài máy sạch còn chờ làm. Không dùng số 9 lát/29 giờ của phiếu cũ làm tiến độ đợt này.
- XML đã kiểm bằng Core giả (CoreGia) khác với ZIP/bảng kê/tải/Node/Cloud/Windows: các phần mở rộng còn chờ Anh chốt và cửa chung Core, chưa có năng lực công bố trong gói mới. Không dùng tài khoản/cổng thuế thật.
- Đọc XML, tải về và nhận vào nghiệp vụ kế toán là ba kết quả riêng: thuế UNKNOWN, ghi nhận NOT_PERFORMED. Lead/Core giữ và chuyển quy trình @1 → @2; bản @1 trong ma-nguon không bị sửa.

Các mục 1–5 dưới đây là lịch sử phiếu 08/11/2026, giữ để đối chiếu; mã HD-n ở đó là mã yêu cầu cũ, không đồng nhất với lát SDK 2.0 HD-n.

## 1. Yêu cầu (theo phiếu, chờ Anh chốt)

| Mã | Yêu cầu |
|---|---|
| HD-1 | Đọc XML/ZIP hóa đơn. Giữ đúng số hóa đơn (kể cả số 0 đầu), tiền, thuế (Decimal) và dấu vết nguồn (hash, vị trí). ZIP lỗi một phần thì không báo là "đầy đủ" |
| HD-2 | Xuất bảng kê bằng nguồn Node nội bộ đóng trong gói. Không đường dẫn cố định tới máy phát triển; thư viện Node được ghim |
| HD-3 | Tải từ cổng thuế: phiên trình duyệt có màn hình; CAPTCHA gõ tại máy chủ; profile riêng cho mỗi pháp nhân và mỗi phiên; mật khẩu chỉ qua bộ nhớ (không qua biến môi trường, tham số dòng lệnh hay tệp) |
| HD-4 | Tài khoản Windows riêng cho tải hóa đơn, khác tài khoản của Core, module và engine khác |
| HD-5 | Hoàn thiện mẫu kết quả ZIP, bảng kê và tải trước. Chỉ công bố năng lực nào đủ bằng chứng. Tên đề xuất: `hoa_don.doc_zip_bang_ke@1`, `hoa_don.tai_cong_thue@1` |
| HD-6 | Core nhận tệp hoặc kỳ tải, giao đúng engine, lưu kết quả đúng pháp nhân, không nhận trùng. Không SQL sang module khác |
| HD-7 | Màn Đọc hóa đơn / Thử tải: chọn tháng, xem tiến độ, lỗi theo nhóm, tải tệp kết quả. Chỉ người được phép mới chọn nguồn và xem tệp. Quản lý engine chỉ xem tình trạng và cấu hình |
| HD-8 | Kiểm tiền, số hóa đơn, bảng kê và PDF khớp nguồn bằng bộ hóa đơn DEMO có đáp án |
| HD-9 | Ghim gói, phụ thuộc và mã băm cuối; có hướng dẫn quay về bản đã ghim |
| HD-10 | Bài test tổng thể 120 phút: XML, ZIP, bảng kê, tải giả. Tải cổng thuế thật là mốc sau, cần lệnh riêng |

## 2. Hiện trạng

| Việc | Trạng thái | Bằng chứng |
|---|---|---|
| Bộ đọc XML/ZIP | ✅ | HD-1 `8c0d6293`; G3-GOI-22 đưa vào `lib\hoa_don_xml.py` |
| Tải qua cổng giả, xuất bảng kê, khung chạy | ✅ giả | HD-2a `d67ce1c5`, HD-2B `6242af70`, HD-3A `1dfa116e` |
| Khung phiên có màn hình, kiểm vòng đời phiên | 🟡 | HD-2c, HD-3b. **Chưa có bằng chứng tài khoản, quyền hay Chromium thật** |
| Ánh xạ trạng thái, phiên qua SDK | ✅ | G3-GOI-23, 24 |
| Nguồn Node bảng kê trong gói (HD-2) | 🟡 | G3-GOI-25: `vendor\build.js`, `config.js`, có `package-lock`. **Chưa đưa job/portal thật vào gói** |
| Ghim cuối (HD-9) | 🟡 | G3-GOI-26: `requirements.lock` ở trạng thái CHUA_KIEM; còn 2 import ngoài SDK |
| HD-3, HD-4, HD-5, HD-6, HD-7, HD-8, HD-10 | ❌ | Theo phiếu: lát 2–7, 9 |

## 3. Lát còn lại (phiếu, 9 lát, 29 giờ công ước tính)
1. G3-GOI-25: nguồn bảng kê trong gói (5 giờ)
2. HD-NOI-PHIEN: nối phiên thật (4 giờ)
3. HD-CONG-BO: mẫu kết quả (3 giờ)
4. HD-NOI-CORE (3 giờ)
5. HD-GIAO-DIEN (4 giờ)
6. HD-SO-TIEN (3 giờ)
7. HD-WIN (3 giờ)
8. G3-GOI-26 (2 giờ)
9. HD-TONG (2 giờ)

## 4. Thư mục
| Thư mục | Nội dung |
|---|---|
| `ma-nguon\` | 24 tệp: `doc.py`, `tai.py`, `phien.py`, `chay.py`, `bang_ke.cjs`, `portal.cjs`, `lib\`, `vendor\`, `package*.json`, `contract\`, `tests\` |
| `tests-tu-core\` | 6 test cũ |
| `tu-core-cu\src\` | `ha_tang\engine_hoa_don.py`, `nguon\hoa_don_xml.py` (thế hệ cũ) |
| `tu-core-cu\tests\` | `test_g3_hd_1/2a/3a/3b.py`, `g3_hd_2b.cjs`, `g3_hd_2c.cjs` |
| `tu-core-cu\phia-core\` | `doi_chieu_hoa_don.py`: lõi đối chiếu M2 ↔ M5. Bản gốc vẫn ở Core; đây là việc của module, chỉ dùng đầu ra của bộ đọc |
| `docs\` | Phiếu kế hoạch |

## 5. Chờ Anh (phải chốt trước khi mở lát mới)
- Quyền chép nguồn Node nội bộ (bảng kê, portal).
- Duyệt mẫu kết quả ZIP và bảng kê.
- Tài khoản Windows có màn hình cho việc tải.
- Vị trí màn: trong module hóa đơn, hay màn thử trên Core DEMO.
- Cách kiểm kê đang áp tạm.
- Thời điểm thử cổng thuế thật (lệnh riêng).
- **Quyết định cuối cho cả phiếu** (như các engine khác đã có).
