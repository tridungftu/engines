-- Ngăn riêng Đối chiếu; Core cấp cột hệ thống, không chèn dữ liệu.


CREATE TABLE eng_e_doi_chieu.luot_doi_chieu (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_luot text NOT NULL,
    bam_cap text,
    bam_bo text,
    phien_ban_engine text,
    trang_thai text,
    chu_so_huu text,
    luc_chiem numeric,
    han_chiem numeric,
    phong_bi text,
    UNIQUE (phap_nhan_id, bam_cap, bam_bo, phien_ban_engine),
    UNIQUE (phap_nhan_id, ma_luot)
);

CREATE TABLE eng_e_doi_chieu.xac_nhan (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_xac_nhan text NOT NULL,
    ma_yeu_cau text,
    UNIQUE (phap_nhan_id, ma_yeu_cau),
    UNIQUE (phap_nhan_id, ma_xac_nhan)
);

CREATE TABLE eng_e_doi_chieu.loi_ocr_de_xuat (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    bam_cap_tu text NOT NULL,
    UNIQUE (phap_nhan_id, bam_cap_tu)
);

CREATE TABLE eng_e_doi_chieu.loi_ocr_da_duyet (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    bam_cap_tu text NOT NULL,
    phien_ban text NOT NULL,
    UNIQUE (bam_cap_tu, phien_ban)
);
