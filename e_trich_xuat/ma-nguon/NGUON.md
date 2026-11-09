# NGUON — e_trich_xuat

Chuyển nội bộ từ nhánh lat/g3-goi-31 (nền hop-nhat-20261023), nội dung giữ nguyên (git rename):

| Đường gốc | Đích | Ghi chú |
|---|---|---|
| src/kho_tri_thuc/engines/e_trich_xuat/ai_chung.py | engines/e_trich_xuat/ai_chung.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_trich_xuat/chay.py | engines/e_trich_xuat/chay.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_trich_xuat/docx.py | engines/e_trich_xuat/docx.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_trich_xuat/do_chinh_xac.py | engines/e_trich_xuat/do_chinh_xac.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_trich_xuat/engine.json | engines/e_trich_xuat/engine.json | đổi khoảng core ">=1.0.0 <2.0.0" (bỏ dấu phẩy) |
| src/kho_tri_thuc/engines/e_trich_xuat/quy_trinh.py | engines/e_trich_xuat/quy_trinh.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_trich_xuat/tham_so.py | engines/e_trich_xuat/tham_so.py | nguyên trạng |
| src/kho_tri_thuc/engines/e_trich_xuat/tich_hop.py | engines/e_trich_xuat/tich_hop.py | đổi 3 khóa đường dẫn trong NGUON_CHEP |
| src/kho_tri_thuc/core/contract/ky_thuat.json (3 schema) | engines/e_trich_xuat/contract/schemas.json | trích chung.v1, tham_chieu_tep.v1, tham_so.v1; nội dung đồng nhất |

SHA-256 từng tệp: lead bổ sung khi chốt lát (sau gộp).
