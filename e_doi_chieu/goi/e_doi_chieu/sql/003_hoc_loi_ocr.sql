-- Chỉ khai cột; Core sở hữu ACL/chỉ-thêm/kiểm toán, không phải UI.
ALTER TABLE eng_e_doi_chieu.loi_ocr_de_xuat ADD COLUMN noi_dung text;
ALTER TABLE eng_e_doi_chieu.loi_ocr_da_duyet ADD COLUMN noi_dung text;
