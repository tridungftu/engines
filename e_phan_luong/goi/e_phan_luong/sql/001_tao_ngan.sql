-- Migration PL-0: chỉ tạo sáu bảng ngăn riêng; không ghi dữ liệu.

CREATE TABLE eng_e_phan_luong.luot (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_luot text NOT NULL,
    ma_module text,
    khau text,
    hat_giong text,
    bam_dau_vao text,
    UNIQUE (phap_nhan_id, ma_luot)
);
COMMENT ON TABLE eng_e_phan_luong.luot IS 'Lượt phân luồng';
COMMENT ON COLUMN eng_e_phan_luong.luot.id IS 'Định danh bản ghi do Core cấp';
COMMENT ON COLUMN eng_e_phan_luong.luot.phap_nhan_id IS 'Pháp nhân do Core điền từ việc';
COMMENT ON COLUMN eng_e_phan_luong.luot.row_version IS 'Phiên bản bản ghi dùng để kiểm xung đột';
COMMENT ON COLUMN eng_e_phan_luong.luot.tao_luc IS 'Thời điểm Core tạo bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.luot.sua_luc IS 'Thời điểm Core sửa bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.luot.het_han_luc IS 'Thời điểm hết hạn hiển thị do Core đặt';
COMMENT ON COLUMN eng_e_phan_luong.luot.viec_id IS 'Mã việc do Core ghi để kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.luot.ma_luot IS 'Mã lượt phân luồng';
COMMENT ON COLUMN eng_e_phan_luong.luot.ma_module IS 'Mã module';
COMMENT ON COLUMN eng_e_phan_luong.luot.khau IS 'Mã khâu duyệt';
COMMENT ON COLUMN eng_e_phan_luong.luot.hat_giong IS 'Hạt giống 32 byte biểu diễn 64 ký tự hex cho kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.luot.bam_dau_vao IS 'Băm dữ liệu đầu vào';

CREATE TABLE eng_e_phan_luong.dong_luot (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_luot text NOT NULL,
    ma text NOT NULL,
    ma_module text,
    khau text,
    ly_do text,
    loai text,
    nguon_loai text,
    UNIQUE (phap_nhan_id, ma_luot, ma)
);
COMMENT ON TABLE eng_e_phan_luong.dong_luot IS 'Dòng của lượt phân luồng';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.id IS 'Định danh bản ghi do Core cấp';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.phap_nhan_id IS 'Pháp nhân do Core điền từ việc';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.row_version IS 'Phiên bản bản ghi dùng để kiểm xung đột';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.tao_luc IS 'Thời điểm Core tạo bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.sua_luc IS 'Thời điểm Core sửa bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.het_han_luc IS 'Thời điểm hết hạn hiển thị do Core đặt';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.viec_id IS 'Mã việc do Core ghi để kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.ma_luot IS 'Mã lượt phân luồng';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.ma IS 'Mã giao dịch do module cấp';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.ma_module IS 'Mã module';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.khau IS 'Mã khâu duyệt';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.ly_do IS 'Các mã lý do theo thứ tự quy định';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.loai IS 'Mã loại nghiệp vụ trong danh mục';
COMMENT ON COLUMN eng_e_phan_luong.dong_luot.nguon_loai IS 'Nguồn gán loại';

CREATE TABLE eng_e_phan_luong.ket_qua_kiem (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ma_luot text NOT NULL,
    ma text NOT NULL,
    khau text NOT NULL,
    ma_module text,
    loai text,
    ket_qua text,
    muc_sai text,
    nguon_mau text,
    nguon_loai_sai text,
    UNIQUE (phap_nhan_id, ma_luot, ma, khau)
);
COMMENT ON TABLE eng_e_phan_luong.ket_qua_kiem IS 'Kết quả kiểm từng mã';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.id IS 'Định danh bản ghi do Core cấp';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.phap_nhan_id IS 'Pháp nhân do Core điền từ việc';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.row_version IS 'Phiên bản bản ghi dùng để kiểm xung đột';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.tao_luc IS 'Thời điểm Core tạo bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.sua_luc IS 'Thời điểm Core sửa bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.het_han_luc IS 'Thời điểm hết hạn hiển thị do Core đặt';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.viec_id IS 'Mã việc do Core ghi để kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.ma_luot IS 'Mã lượt phân luồng';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.ma IS 'Mã giao dịch do module cấp';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.khau IS 'Mã khâu duyệt';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.ma_module IS 'Mã module';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.loai IS 'Mã loại nghiệp vụ trong danh mục';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.ket_qua IS 'Kết quả kiểm';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.muc_sai IS 'Mức sai nhỏ hoặc đạt SAD hoặc đạt TE';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.nguon_mau IS 'Nguồn mẫu kiểm';
COMMENT ON COLUMN eng_e_phan_luong.ket_qua_kiem.nguon_loai_sai IS 'Nguồn gán loại bị sửa';

CREATE TABLE eng_e_phan_luong.ty_le (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    khau text NOT NULL,
    loai text NOT NULL,
    bac numeric,
    che_do text,
    mau_tu_doi_bac numeric,
    loi_tu_doi_bac numeric,
    mau_sach_toan_bo numeric,
    mau_12t numeric,
    loi_12t numeric,
    loi_sad_12t numeric,
    loi_ngoai_mau_12t numeric,
    diem numeric,
    nhan text,
    doi_bac_luc timestamptz,
    UNIQUE (phap_nhan_id, khau, loai)
);
COMMENT ON TABLE eng_e_phan_luong.ty_le IS 'Thống kê tỷ lệ theo khâu và loại';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.id IS 'Định danh bản ghi do Core cấp';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.phap_nhan_id IS 'Pháp nhân do Core điền từ việc';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.row_version IS 'Phiên bản bản ghi dùng để kiểm xung đột';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.tao_luc IS 'Thời điểm Core tạo bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.sua_luc IS 'Thời điểm Core sửa bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.het_han_luc IS 'Thời điểm hết hạn hiển thị do Core đặt';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.viec_id IS 'Mã việc do Core ghi để kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.khau IS 'Mã khâu duyệt';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.loai IS 'Mã loại nghiệp vụ trong danh mục';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.bac IS 'Bậc tỷ lệ kiểm
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.che_do IS 'Chế độ kiểm theo bậc hoặc toàn bộ';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.mau_tu_doi_bac IS 'Số mẫu từ lần đổi bậc
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.loi_tu_doi_bac IS 'Số lỗi từ lần đổi bậc
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.mau_sach_toan_bo IS 'Số mẫu sạch khi kiểm toàn bộ
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.mau_12t IS 'Số mẫu trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.loi_12t IS 'Số lỗi trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.loi_sad_12t IS 'Số lỗi từ SAD trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.loi_ngoai_mau_12t IS 'Số lỗi ngoài mẫu trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.diem IS 'Điểm rủi ro gộp
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.nhan IS 'Các nhãn rủi ro';
COMMENT ON COLUMN eng_e_phan_luong.ty_le.doi_bac_luc IS 'Thời điểm đổi bậc';

CREATE TABLE eng_e_phan_luong.ho_so_hanh_vi (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    khau text NOT NULL,
    loai text NOT NULL,
    so_nghiep_vu numeric,
    bieu_do text,
    bam_doi_tac text,
    tong_7_ngay text,
    ky_lam_moi text,
    UNIQUE (phap_nhan_id, khau, loai)
);
COMMENT ON TABLE eng_e_phan_luong.ho_so_hanh_vi IS 'Hồ sơ hành vi gộp';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.id IS 'Định danh bản ghi do Core cấp';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.phap_nhan_id IS 'Pháp nhân do Core điền từ việc';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.row_version IS 'Phiên bản bản ghi dùng để kiểm xung đột';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.tao_luc IS 'Thời điểm Core tạo bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.sua_luc IS 'Thời điểm Core sửa bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.het_han_luc IS 'Thời điểm hết hạn hiển thị do Core đặt';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.viec_id IS 'Mã việc do Core ghi để kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.khau IS 'Mã khâu duyệt';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.loai IS 'Mã loại nghiệp vụ trong danh mục';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.so_nghiep_vu IS 'Số nghiệp vụ gộp
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.bieu_do IS 'Biểu đồ tần suất gộp dạng chuỗi JSON';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.bam_doi_tac IS 'Tập băm đối tác dạng chuỗi JSON';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.tong_7_ngay IS 'Tổng gộp theo băm và ngày trong bảy ngày dạng chuỗi JSON';
COMMENT ON COLUMN eng_e_phan_luong.ho_so_hanh_vi.ky_lam_moi IS 'Kỳ làm mới hồ sơ';

CREATE TABLE eng_e_phan_luong.chot_ky (
    id uuid PRIMARY KEY,
    phap_nhan_id uuid NOT NULL,
    row_version bigint NOT NULL DEFAULT 1,
    tao_luc timestamptz NOT NULL DEFAULT now(),
    sua_luc timestamptz,
    het_han_luc timestamptz,
    viec_id uuid,
    ky text NOT NULL,
    khau text NOT NULL,
    loai text NOT NULL,
    bac numeric,
    che_do text,
    mau_tu_doi_bac numeric,
    loi_tu_doi_bac numeric,
    mau_sach_toan_bo numeric,
    mau_12t numeric,
    loi_12t numeric,
    loi_sad_12t numeric,
    loi_ngoai_mau_12t numeric,
    diem numeric,
    nhan text,
    doi_bac_luc timestamptz,
    UNIQUE (phap_nhan_id, ky, khau, loai)
);
COMMENT ON TABLE eng_e_phan_luong.chot_ky IS 'Bản chụp thống kê theo kỳ';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.id IS 'Định danh bản ghi do Core cấp';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.phap_nhan_id IS 'Pháp nhân do Core điền từ việc';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.row_version IS 'Phiên bản bản ghi dùng để kiểm xung đột';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.tao_luc IS 'Thời điểm Core tạo bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.sua_luc IS 'Thời điểm Core sửa bản ghi';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.het_han_luc IS 'Thời điểm hết hạn hiển thị do Core đặt';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.viec_id IS 'Mã việc do Core ghi để kiểm toán';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.ky IS 'Kỳ chốt thống kê theo tháng';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.khau IS 'Mã khâu duyệt';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.loai IS 'Mã loại nghiệp vụ trong danh mục';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.bac IS 'Bậc tỷ lệ kiểm
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.che_do IS 'Chế độ kiểm theo bậc hoặc toàn bộ';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.mau_tu_doi_bac IS 'Số mẫu từ lần đổi bậc
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.loi_tu_doi_bac IS 'Số lỗi từ lần đổi bậc
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.mau_sach_toan_bo IS 'Số mẫu sạch khi kiểm toàn bộ
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.mau_12t IS 'Số mẫu trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.loi_12t IS 'Số lỗi trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.loi_sad_12t IS 'Số lỗi từ SAD trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.loi_ngoai_mau_12t IS 'Số lỗi ngoài mẫu trong 12 tháng
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.diem IS 'Điểm rủi ro gộp
kieu: so';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.nhan IS 'Các nhãn rủi ro';
COMMENT ON COLUMN eng_e_phan_luong.chot_ky.doi_bac_luc IS 'Thời điểm đổi bậc';
