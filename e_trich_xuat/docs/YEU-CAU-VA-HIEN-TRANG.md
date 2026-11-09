# e_trich_xuat — Trích thông tin hợp đồng: yêu cầu và hiện trạng

*Lập ngày 08/11/2026.*

**Căn cứ:**
- `QUYET-DINH-CUOI-e_trich_xuat.md` (Anh chốt 07/11 lúc 20:42; CD-107).
- `PHIEU-ENGINE-e_trich_xuat.md`: bản lập lại 07/11, có bổ sung CD-111.
- `KE-HOACH-LOAI-HOP-DONG.md`; TL 44 (5 bộ tham số mua theo loại); TL 56 §9.2 (trích có mục tiêu cho tầng 3 tra cứu).
- Yêu cầu chung: `..\_chung\docs\YEU-CAU-CHUNG-ENGINE.md`.

**Ký hiệu hiện trạng:** ✅ có / 🟡 một phần / ❌ chưa có.

## 0. Kết luận
- **Bộ tham số theo loại hợp đồng thuộc module, không thuộc Core.** Mỗi module giữ bản riêng.
- Module gửi **tệp + loại + bộ tham số**. Core điều phối các bước: OCR (nếu cần) → **bước chuẩn bị** của engine trích → Hỏi AI Local → **bước hậu kiểm** của engine trích → trả bảng kết quả về module.
- Engine trích **không gọi AI trực tiếp** và **không tự tra danh mục**.
- **Hiện trạng:**
  - Đã có: gói 0.1.0-demo.1 (đóng gói G3-GOI-31); mã E1 (kiểm Excel); E2 (nhận bộ gửi kèm việc, kiểm hash); bộ 37 tham số xây dựng làm mặc định.
  - Phiếu mới gồm **16 lát, 53 giờ công ước tính**, chưa duyệt.
  - Hướng cũ "kho bộ tham số ở Core" (migration 108, màn `danh_muc_trich_mau.js`) đã bị Anh bỏ. Cần migration bù và chuyển phần tận dụng được sang module.

## 1. Yêu cầu

| Mã | Yêu cầu | Căn cứ |
|---|---|---|
| TX-1 | Bộ tham số theo loại hợp đồng nằm ở **module**. Mỗi module có **bản riêng**, kể cả khi hai module dùng cùng một loại | QĐ §1 |
| TX-2 | Module gửi việc gồm tệp + loại + bộ tham số **đã cố định**, kèm nhận diện module, loại, phiên bản, hash | QĐ §1; phiếu §1 |
| TX-3 | **Chuỗi xử lý do Core điều phối.** Bước chuẩn bị (kiểm nội dung và hash, lập các trường và đầu vào) và bước hậu kiểm (nhận kết quả Hỏi AI, kiểm trích dẫn và trường thiếu, lập bảng) là **hai năng lực riêng** của engine. Engine không gọi AI, không tự lặp | QĐ §1; CD-111 |
| TX-4 | Engine **không tự tra danh mục**, chỉ trích theo bộ gửi kèm. Thiếu bộ hoặc sai hash thì từ chối, không tự dùng bộ xây dựng thay | QĐ §1; phiếu §1 |
| TX-5 | Kết quả gồm: bảng thông tin, trích dẫn và vị trí nguồn, ô cần xem lại. Ghi đủ **module, loại, phiên bản, hash** | QĐ §1 |
| TX-6 | Kết quả trả về module; module tự quyết khi nào lưu. Core giữ tạm tới khi module lưu hoặc đóng việc, rồi dọn. Gửi lại xác nhận không gây lưu hay dọn hai lần | QĐ §1 |
| TX-7 | **Bộ 37 tham số xây dựng:** engine giữ tạm làm mặc định. Chỉ chuyển sang module khi **E6 so từng byte** cho kết quả trùng. Sau khi chuyển, bộ mặc định vào lưu trữ, không xóa | QĐ §1 |
| TX-8 | **Quản lý bộ tham số đặt trong phần quản lý của từng module:** màn nạp Excel, lịch sử, so sánh, chạy thử, kích hoạt. Admin module quản bộ của mình; Admin Core xem và sửa tất cả. **Không** tạo quyền "Kích hoạt" riêng ở Core | QĐ §2 |
| TX-9 | Màn người dùng **không hiện** phiên bản bộ, hash, UUID | QĐ §2 |
| TX-10 | **Loại thứ hai: thuê đất kèm cơ sở hạ tầng (KCN).** CRM giữ bộ; M3 dùng lại dữ liệu đã trích. Lead soạn bộ nháp và hợp đồng DEMO; người nghiệp vụ duyệt trước khi kích hoạt | QĐ §3 |
| TX-11 | Bộ 30 tham số dịch vụ và 3 hợp đồng dịch vụ DEMO chuyển vào lưu trữ, không xóa | QĐ §3 |
| TX-12 | Giữ E6 và bài kiểm Word có Track Changes. N1 chỉ kiểm nhanh **một lần**, không lặp | QĐ §4 |
| TX-13 | Bài test cuối chia vào các buổi 17:00. Lead chạy trước các bước chờ AI/OCR. Phần Anh tham gia mỗi buổi **≤ 30 phút** | QĐ §4 |
| TX-14 | Tận dụng tối đa mã đã có: E1 kiểm Excel, logic phiên bản, 3 màn U1a/U1b. Phần không dùng chuyển lưu trữ | QĐ §5 |
| TX-15 | Word không qua OCR; PDF qua OCR | Phiếu §5 |
| TX-16 | Nhận "danh sách trường cần trích" để trích có mục tiêu trên một tệp (tầng 3 của `e_tra_cuu`) | TL 56 §9.2 |
| TX-17 | Câu hỏi bổ sung của một việc: tối đa 5 câu (đề xuất, chưa duyệt); không sửa bộ đã ghim | Phiếu §4 |
| TX-18 | Hỏi lại trường thiếu qua nhiều vòng AI chỉ khi cần, với số vòng giới hạn, **do Core điều phối** (đề xuất CD-111, chưa duyệt) | Phiếu §4 |

## 2. Hiện trạng

| Mã | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|
| Gói engine | 🟡 | 0.1.0-demo.1 (G3-GOI-31). `engine.json` ghi rõ "chưa sẵn sàng: chờ phép đo TRICH-4b" (phép đo này đã hủy, thay bằng N1) |
| TX-2, TX-4 (E2) | 🟡 | `tich_hop.py`: nhận bộ gửi kèm việc, đọc tệp theo tham chiếu, kiểm hash trước AI. Ngữ cảnh module chưa đủ |
| TX-3 | ❌ | Năng lực hiện là một khối `trich.tham_so_hop_dong@1` và **có gọi AI qua SDK** (`ai_chung.py`). Phải tách thành chuẩn bị + hậu kiểm |
| TX-5 (E5) | 🟡 | Metadata loại/hash có; module/phiên bản chưa đủ ở mọi đường trả |
| TX-6 (C3) | ❌ | Phụ thuộc bộ điều phối chuỗi và cơ chế giữ tạm của Core |
| TX-7 (E6) | ❌ | Chưa chạy. **Thiếu tệp ghim `DANH_MUC_THAM_SO.xlsx`** khiến 1 test lỗi và 1 test bị bỏ qua (phiếu §6) |
| TX-8 (C1, C2, C4) | 🟡 | Có E1 (`sdk_core/danh_muc_tham_so.py`, kiểm Excel thuần); U1a/U1b (`danh_muc_trich_mau.js`, mô phỏng trong RAM, **đang đặt ở Core**); SQL 108 (kho ở Core: **hướng đã bỏ**). Chưa có route C2 |
| TX-10 (LHD-02b) | ❌ | Bộ thuê đất KCN chưa soạn |
| TX-11 | ❌ | Chưa chuyển lưu trữ |
| TX-12 … TX-18 | ❌ | |
| Thế hệ cũ K2 | 🔁 | "Engine trích #6" chạy như tiến trình riêng: `nguon\trich6_host.py`, `trich_chung_6.py`, `trich_hop_dong_6.py` (vẫn trong Core, M4 và CRM K2 đang dùng; bản sao ở `tu-core-cu\phia-core\`) |

**Kết quả kiểm gần nhất** (phiếu §6, 07/11):
- E1 + C1: 48 ca = 46 đạt / 0 hỏng / 1 lỗi / 1 bỏ qua.
- Node `danh_muc_trich_mau.cjs`: 16 đạt.

## 3. Lát (phiếu 07/11, 16 lát, 53 giờ công ước tính, chưa duyệt)
- **Đường chính:**
  - C1 → C2 → C3 → C4 → N2;
  - E2 → E3/E4/E5 → E6 → G3-GOI-37 → N1/READY → N2.
- **Song song:** LHD-02b (KCN). LHD-C1-BU (migration bù, khóa đường kho Core cũ) làm sau C1/C3/E5.
- Chi tiết: `PHIEU-ENGINE-e_trich_xuat.md` §3.
- **Lưu ý khi chuyển sang project riêng:**
  - C1, C2, C4 là việc **trong module** (CRM, M4…), không phải việc của engine.
  - C3 là việc của **Core** (chuỗi, giữ tạm).
  - Project engine chỉ làm: E2–E6, tách năng lực chuẩn bị/hậu kiểm, G3-GOI-37, N1, READY; và cung cấp mã E1/U1 cho module dùng lại.

## 4. Thư mục
| Thư mục | Nội dung |
|---|---|
| `ma-nguon\` | 26 tệp: `tich_hop.py`, `tham_so.py`, `quy_trinh.py`, `docx.py`, `ai_chung.py`, `do_chinh_xac.py`, `chay.py`, `vendor\`, `contract\`, `tests\` |
| `tests-tu-core\` | 8 test cũ |
| `tu-core-cu\tests\`, `tools\` | `test_lhd_c1_danh_muc.py`, `test_lhd_e1_danh_muc.py`, `test_lhd_e2_loai.py`, `kiem_nhanh_trich.py` |
| `tu-core-cu\phia-core\` | Bản sao: `trich6_host.py`, `trich_chung_6.py`, `trich_hop_dong_6.py`, `danh_muc_trich_mau.js`, SQL 108 |
| `docs\` | Quyết định cuối, phiếu (có phụ lục bản 06/11), kế hoạch loại hợp đồng |

## 5. Chờ Anh
- Duyệt phiếu lập lại (16 lát, 53 giờ công ước tính).
- Quy tắc kiểm logic cho thuê đất KCN (người nghiệp vụ duyệt).
- Số mẫu chạy thử tối thiểu (đề xuất 3 hợp đồng KCN DEMO).
- Cấu trúc đầu vào/kết quả E5.
- Giới hạn câu hỏi thêm (đề xuất 5).
- Hỏi lại nhiều vòng (CD-111).
- Có mở nhánh trích bảng không (4 lát, 10 giờ, ngoài phạm vi chính).
