-- Ngăn OCR do Core quản lý; không có dữ liệu hoặc thao tác ngoài schema riêng.
CREATE TABLE eng_e_ocr.han_muc_ngay (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ngay date NOT NULL,
    da_nhan text NOT NULL,
    UNIQUE (ngay)
);

CREATE TABLE eng_e_ocr.luot_abbyy (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_tuong_quan text NOT NULL,
    bam_noi_dung text NOT NULL,
    so_trang numeric NOT NULL,
    lan_gui numeric NOT NULL,
    trang_thai text NOT NULL,
    da_nhan boolean NOT NULL,
    da_hoan boolean NOT NULL,
    luc_giu numeric NOT NULL,
    luc_nhan numeric,
    chu_xu_ly text,
    han_xu_ly numeric NOT NULL,
    UNIQUE (phap_nhan_id, ma_tuong_quan),
    UNIQUE (phap_nhan_id, bam_noi_dung)
);

CREATE TABLE eng_e_ocr.trang_thai_engine (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma text NOT NULL,
    abbyy_bat boolean,
    ly_do text,
    luc_kiem text,
    lan numeric,
    so_luot numeric,
    theo_ngay text,
    dang_giu text,
    UNIQUE (ma)
);
