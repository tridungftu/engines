# -*- coding: utf-8 -*-
"""vendor — closure THUẦN của lõi Review mà engine trích xuất dùng (lát G3-GOI-32).

Chép từ src/kho_tri_thuc/m4/review_goc/trich_xuat/ vào vendor/review/.
7/9 tệp nguyên byte; 2 tệp là bản RÚT GỌN: review/cau_hinh.py (chỉ THU_MUC_GOI, DANH_MUC_THAM_SO; bỏ khóa Cloud/máy AI/ghi cấu hình theo TL 48) và review/doc_hop_dong.py (bỏ Word COM/LibreOffice/subprocess; .doc ném ValueError('CAN_CHUYEN_DOC_NGOAI_ENGINE'); .docx đọc thuần zip/XML như cũ). Không đổi import nào: toàn bộ import nội bộ của 9 tệp vốn đã là import tương đối
(`from .cau_truc import ...`), nên closure chạy độc lập mà không cần sửa.
Không vendor: ai_local, ai_cloud, cloud, may_ai, ocr_abbyy, lo, quy_trinh (client riêng), __main__, giao diện, máy chủ.
Việc chuyển import của docx/tham_so/do_chinh_xac/quy_trinh/tich_hop sang vendor là lát 33.

SHA-256 (7 tệp: bản gốc = bản vendor; doc_hop_dong và cau_hinh: RÚT GỌN, ghi cả SHA gốc):
  review/__init__.py     f200159d6de51d346ea40d0abc2efe3132ac679dc0c31e778c10aa266490be8b
  review/doc_hop_dong.py RÚT GỌN 1a73354377cd5a13aaa9c45254756d54099796150c7ad798ef26cff5e86c556f
                         (SHA gốc bbe8d9579ad9cce2c4b50e77fa734e7fc9826cd7933abe1aad2e5bf8b3d8a98b)
  review/cau_truc.py     2817a46ec2fc967d1e64eae1dd68e35047e687a7b654a9c8ce03f106b9aad5c6
  review/kiem_tra.py     47ee35567cb7b864a6b3d6825bc90f93a7a26c0c6872a326e99ead9160467f12
  review/logic.py        f7cfcf37ff2293d8f8ea994f1ae0a69f57d1d1d9a844f0620f018a3d285a4452
  review/xlsx_mini.py    a29ed16811637daa756fcb2640557ec817734d3d2ee617c30deca51d3799857b
  review/xuat.py         d255b2d01b67283b3b5febfb6c3f5f937df80c5020531bd04862fc89ad969efb
  review/danh_muc.py     f0796984f7b18a4d0d3389b557a6324f3ad59ca488c29ad3284e11ca97ca2ff2
  review/cau_hinh.py     RÚT GỌN 8aa6e436e63125369c4c20a3c18753a6ac59b4f2f404b4878b202e34f4a35e04
                         (SHA gốc 53defa8fc52859c2e14cc9a00701fbc055e8eb47e0bb69156ccd8cdcacc58d93)

DANH_MUC_THAM_SO.xlsx: KHÔNG nằm trong git (.gitignore `*.xlsx`). Bản ở nguồn
src/kho_tri_thuc/m4/review_goc/trich_xuat/DANH_MUC_THAM_SO.xlsx có
SHA-256 05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd
(trùng DANH_MUC_SHA256 trong tich_hop.py). Cấu hình tìm catalog ở review/DANH_MUC_THAM_SO.xlsx
(cau_hinh.THU_MUC_GOI); lead cấp bản đúng SHA này khi cần chạy thật.
"""
