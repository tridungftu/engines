-- Ngăn dùng chung trong engine; Core cấp cột hệ thống, không có dữ liệu mẫu.
CREATE TABLE eng_e_hoi_ai.model_phat_hien (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    id_model text NOT NULL,
    url text,
    kha_dung boolean,
    loai text,
    api text,
    thu_tu numeric,
    kiem_luc text,
    phat_hien_dat boolean,
    UNIQUE (id_model)
);
