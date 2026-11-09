-- LHD-C1 / QD-TAM-20261106-02 + QD-TAM-20261106-07: danh mục trích theo loại.
-- Loại hợp đồng, phiên bản danh mục và con trỏ "Đang dùng" (kèm căn cứ kích
-- hoạt) đều là DÒNG chỉ-ghi-thêm trong loi.engine_tep_cau_hinh; không dùng
-- loi.ho_so_chay_engine.cau_hinh, không vá loi.ho_so_chay_ghi. Không đọc Excel.
--
-- Kiểu dòng (cột kieu), mỗi (kieu,khoa) đánh so_phien_ban 1,2,3…; dòng mới nhất
-- là trạng thái hiện tại:
--   LOAI      tom_tat = {ten,mo_ta,nhom_danh_muc_hop_dong,co_kiem_logic_rieng,
--             trang_thai: hoat_dong|ngung}; ma_bam/tep_id/tham_chieu_id NULL.
--   PHIEN_BAN ma_bam = SHA-256 bytes Excel, ma_bam_noi_dung = SHA JSON 10 cột,
--             tep_id = tệp trong kho tệp (không khóa ngoại sang loi_tai_lieu),
--             tom_tat = {so_tham_so,so_dang_dung,so_muc_3,so_luon_hoi,co_quy_tac}.
--   DANG_DUNG con trỏ: ma_bam + tham_chieu_id = dòng PHIEN_BAN được kích hoạt;
--             tom_tat = {ly_do,viec_chay_thu,quay_lui}; người = tao_boi,
--             lúc = tao_luc, nhật ký = kiem_toan_id.
-- Seed XD v1 (LOAI + PHIEN_BAN + DANG_DUNG) ngay trong migration: SHA bytes
-- 05846a2a…, hash nội dung/tóm tắt tính bằng sdk_core.danh_muc_tham_so trên đúng
-- tệp đó; tep_id/tao_boi NULL chỉ cho seed này. XD chạy như cũ ngay sau khi áp.
--
-- Cửa cho đăng nhập Core (SECURITY DEFINER, kiểm phiên + MTQ trước mọi đọc/ghi),
-- KHÔNG RAISE với lỗi nghiệp vụ: luôn ghi nhật ký (DAT/KHONG_DAT/TU_CHOI) rồi trả
-- jsonb; tầng trên phải COMMIT cả kết quả từ chối (như 104). Lỗi ngoài dự kiến
-- (hỏng nền, ràng buộc) được để nổi lên, không gom.
--   loi.trich_danh_muc_loai(p_ma,p_loai,p_thong_tin,p_so_phien_ban_cu)  SUA
--       DAT → {ma,id,so_phien_ban,khong_doi,kiem_toan_id}
--   loi.trich_danh_muc_ghi(p_ma,p_loai,p_bam,p_bam_noi_dung,p_tep,p_tom_tat) SUA
--       DAT → {ma,id,so_phien_ban,khong_doi,kiem_toan_id}
--   loi.trich_danh_muc_kich_hoat(p_ma,p_loai,p_bam,p_ly_do)  DUYET
--       DAT → {ma,id,so_phien_ban,phien_ban_danh_muc,viec_chay_thu,quay_lui,
--              khong_doi,kiem_toan_id}
--   loi.trich_danh_muc_doc(p_ma,p_loai)  XEM (p_loai NULL = danh sách loại)
--       DAT → {ma,loai,phien_ban,dang_dung,lich_su_kich_hoat,kiem_toan_id}
--   Mọi kết quả khác DAT → {ma,kiem_toan_id} (kich_hoat thêm viec_chay_thu).
-- Ánh xạ ma → HTTP cho LHD-C2:
--   DAT 200 · LHD_PHIEN 401 · LHD_CHI_CORE, LHD_TU_CHOI, LHD_CHI_PHAP_NHAN_DEMO 403
--   LHD_DAU_VAO, LHD_TEP_KHONG_HOP_LE, LHD_LOAI_KHONG_THAY, LHD_LOAI_PHIEN_BAN 422
--   LHD_XUNG_DOT_HASH, LHD_XUNG_DOT_PHIEN_BAN, LHD_LOAI_NGUNG,
--   LHD_CHUA_DU_CHAY_THU 409 · LHD_CAN_READ_COMMITTED 500 (lỗi cấu hình gọi).
-- Nhật ký: TU_CHOI khi chưa qua phiên/MTQ; KHONG_DAT khi qua quyền nhưng dữ liệu
-- không đạt; DAT khi ghi/đọc được (doi_tuong_id = dòng liên quan).
--
-- Đọc loi_tai_lieu CHỈ qua cầu nối loi.trich_danh_muc_tep (schema loi vì owner
-- Core không có USAGE loi_tai_lieu — gọi hàm cần USAGE schema chứa nó; owner
-- vai_doi_cau_truc_loi_tai_lieu, DEFINER, EXECUTE chỉ cho owner Core, chỉ trả
-- danh sách id) — đúng mẫu loi.xdl_dang_ky_tep (067).
-- Giao kèo C2/CE (chạy thử): quy_trinh_lan.buoc[quy_trinh_buoc].dau_vao mang
-- chay_thu=true, loai_hop_dong, danh_muc.sha256 và tep_id của mẫu DEMO; chỉ đếm
-- việc và lần chạy có module='core'.
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt||'vai_doi_cau_truc_loi';
    chu_tl text := tt||'vai_doi_cau_truc_loi_tai_lieu';
    login text := tt||'dang_nhap_loi';
    vai_cu text := current_setting('role');
    path_cu text := current_setting('search_path');
    bang text; ham text; hd text; quyen record; kt bigint; pb uuid;
    xd constant text := '05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd';
    xd_nd constant text := '6b8190a73e73ced8784fb22e3339a42d72785826ae15b1a499955facb4d65812';
    xd_loai constant jsonb := '{"ten":"Hợp đồng xây dựng","mo_ta":"Danh mục gốc XD",
        "nhom_danh_muc_hop_dong":"XAY_DUNG","co_kiem_logic_rieng":true,"trang_thai":"hoat_dong"}';
    xd_tom_tat constant jsonb := '{"so_tham_so":37,"so_dang_dung":37,"so_muc_3":10,
        "so_luon_hoi":5,"co_quy_tac":false}';
    xd_kich_hoat constant jsonb := '{"ly_do":"chuyển từ công cụ gốc, đã kiểm nhanh CD-071",
        "viec_chay_thu":[],"quay_lui":false}';
BEGIN
    IF (tt<>'' AND tt !~ '^[a-z][a-z0-9_]*_$')
       OR octet_length(tt||'vai_doi_cau_truc_loi_tai_lieu')>63
       OR (tt<>'' AND current_database() !~ '^kho_test_')
       OR current_database() !~ '^(kho_core_demo_g2_[a-z0-9_]+|kho_test_[a-z0-9_]+)$'
       OR current_setting('server_version_num')::integer<160000 THEN
        RAISE EXCEPTION 'LHD_CHI_DEMO_TEST_PG16';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_namespace n JOIN pg_roles v ON v.oid=n.nspowner
        WHERE n.nspname='loi' AND v.rolname=chu AND NOT v.rolcanlogin
          AND NOT v.rolsuper AND NOT v.rolcreaterole AND NOT v.rolbypassrls)
       OR NOT EXISTS (SELECT FROM pg_namespace n JOIN pg_roles v ON v.oid=n.nspowner
        WHERE n.nspname='loi_tai_lieu' AND v.rolname=chu_tl AND NOT v.rolcanlogin
          AND NOT v.rolsuper AND NOT v.rolcreaterole AND NOT v.rolbypassrls)
       OR NOT EXISTS (SELECT FROM pg_roles WHERE rolname=login AND rolcanlogin
          AND NOT rolsuper AND NOT rolcreaterole AND NOT rolbypassrls)
       OR NOT pg_has_role(chu_tl,'MEMBER') OR NOT pg_has_role(chu,'MEMBER')
       OR to_regprocedure('loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi.chan_sua_kiem_toan()') IS NULL
       OR NOT EXISTS (SELECT FROM pg_proc WHERE prosecdef
          AND oid=to_regprocedure('loi_tai_lieu.ngu_canh(text,text,uuid,text,uuid,bigint)')
          AND pg_get_userbyid(proowner)=chu_tl) THEN
        RAISE EXCEPTION 'LHD_THIEU_NEN';
    END IF;
    FOREACH bang IN ARRAY ARRAY['nhat_ky_kiem_toan','mtq_danh_muc_hanh_dong',
        'hang_viec','quy_trinh_lan','engine_dinh_nghia'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class c WHERE c.oid=to_regclass('loi.'||bang)
            AND c.relkind='r' AND pg_get_userbyid(c.relowner)=chu
            AND c.relrowsecurity AND c.relforcerowsecurity) THEN
            RAISE EXCEPTION 'LHD_NEN_SAI_OWNER_RLS';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['tep_goc','ket_qua_xu_ly'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class c WHERE c.oid=to_regclass('loi_tai_lieu.'||bang)
            AND c.relkind='r' AND pg_get_userbyid(c.relowner)=chu_tl
            AND c.relrowsecurity AND c.relforcerowsecurity) THEN
            RAISE EXCEPTION 'LHD_NEN_SAI_OWNER_RLS';
        END IF;
    END LOOP;
    IF EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi.engine_tep_cau_hinh')
        AND (relkind<>'r' OR pg_get_userbyid(relowner)<>chu))
       OR EXISTS (SELECT FROM pg_proc WHERE pronamespace='loi'::regnamespace
        AND proname IN ('trich_danh_muc_quyen','trich_danh_muc_kiem_toan','trich_danh_muc_loai',
            'trich_danh_muc_ghi','trich_danh_muc_kich_hoat','trich_danh_muc_doc')
        AND pg_get_userbyid(proowner)<>chu)
       OR EXISTS (SELECT FROM pg_proc WHERE pronamespace='loi'::regnamespace
        AND proname='trich_danh_muc_tep' AND pg_get_userbyid(proowner)<>chu_tl) THEN
        RAISE EXCEPTION 'LHD_SAI_OWNER';
    END IF;
    -- Bảng dạng vòng 1 (chưa có cột kieu) không được dùng lại âm thầm.
    -- Chỉ đọc catalog qua to_regclass: hằng 'x'::regclass bị gập lúc lập kế
    -- hoạch nên CSDL sạch (chưa có bảng) báo 42P01 dù vế trước của AND sai.
    IF to_regclass('loi.engine_tep_cau_hinh') IS NOT NULL AND NOT EXISTS (
        SELECT FROM pg_attribute WHERE attrelid=to_regclass('loi.engine_tep_cau_hinh')
          AND attname='kieu' AND NOT attisdropped) THEN
        RAISE EXCEPTION 'LHD_BANG_108_VONG_1';
    END IF;
    EXECUTE format('SET LOCAL ROLE %I',chu);
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);

    CREATE TABLE IF NOT EXISTS loi.engine_tep_cau_hinh (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        ma_engine text NOT NULL CHECK (ma_engine='e_trich_xuat'),
        nhom text NOT NULL CHECK (nhom='danh_muc_tham_so'),
        kieu text NOT NULL CHECK (kieu IN ('LOAI','PHIEN_BAN','DANG_DUNG')),
        khoa text NOT NULL CHECK (khoa ~ '^[A-Z][A-Z0-9_]{1,15}$'),
        so_phien_ban integer NOT NULL CHECK (so_phien_ban>0),
        ma_bam text CHECK (ma_bam ~ '^[0-9a-f]{64}$'),
        ma_bam_noi_dung text CHECK (ma_bam_noi_dung ~ '^[0-9a-f]{64}$'),
        tep_id uuid,
        tham_chieu_id uuid REFERENCES loi.engine_tep_cau_hinh(id),
        tom_tat jsonb NOT NULL CHECK (jsonb_typeof(tom_tat)='object'),
        tao_boi uuid REFERENCES loi.nguoi_dung(id),
        tao_luc timestamptz NOT NULL DEFAULT clock_timestamp(),
        kiem_toan_id bigint NOT NULL REFERENCES loi.nhat_ky_kiem_toan(id),
        UNIQUE(ma_engine,nhom,kieu,khoa,so_phien_ban),
        CHECK (CASE kieu
            WHEN 'LOAI' THEN ma_bam IS NULL AND ma_bam_noi_dung IS NULL
                AND tep_id IS NULL AND tham_chieu_id IS NULL
            WHEN 'PHIEN_BAN' THEN ma_bam IS NOT NULL AND ma_bam_noi_dung IS NOT NULL
                AND tham_chieu_id IS NULL AND (tep_id IS NOT NULL
                    OR (khoa='XD' AND so_phien_ban=1
                        AND ma_bam='05846a2acd60f2cde708d13a163a137ee3fb0b4e08fd84f85a7e14e7ef861bcd'))
            ELSE ma_bam IS NOT NULL AND tham_chieu_id IS NOT NULL
                AND ma_bam_noi_dung IS NULL AND tep_id IS NULL END),
        CHECK (tao_boi IS NOT NULL OR (khoa='XD' AND so_phien_ban=1))
    );
    CREATE UNIQUE INDEX IF NOT EXISTS engine_tep_cau_hinh_phien_ban_bam
        ON loi.engine_tep_cau_hinh(ma_engine,nhom,khoa,ma_bam) WHERE kieu='PHIEN_BAN';
    ALTER TABLE loi.engine_tep_cau_hinh ENABLE ROW LEVEL SECURITY;
    ALTER TABLE loi.engine_tep_cau_hinh FORCE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('loi.engine_tep_cau_hinh')
        AND polname='engine_tep_chu') THEN
        EXECUTE format('CREATE POLICY engine_tep_chu ON loi.engine_tep_cau_hinh TO %I
            USING (true) WITH CHECK (true)',chu);
    END IF;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid=to_regclass('loi.engine_tep_cau_hinh')
        AND tgname='engine_tep_bat_bien') THEN
        CREATE TRIGGER engine_tep_bat_bien BEFORE UPDATE OR DELETE OR TRUNCATE
            ON loi.engine_tep_cau_hinh FOR EACH STATEMENT
            EXECUTE FUNCTION loi.chan_sua_kiem_toan();
    END IF;
    REVOKE ALL ON TABLE loi.engine_tep_cau_hinh FROM PUBLIC;
    FOR quyen IN SELECT DISTINCT a.grantee FROM pg_class c,LATERAL aclexplode(c.relacl) a
        WHERE c.oid=to_regclass('loi.engine_tep_cau_hinh')
          AND a.grantee<>0 AND a.grantee<>c.relowner LOOP
        EXECUTE format('REVOKE ALL ON TABLE loi.engine_tep_cau_hinh FROM %I',pg_get_userbyid(quyen.grantee));
    END LOOP;

    INSERT INTO loi.mtq_danh_muc_hanh_dong
        (phien_ban_danh_muc,module,man,hanh_dong,lenh_ky_thuat,loai_doi_tuong,resolver,loai_tien)
    VALUES (1,'CORE','DANH_MUC_TRICH','XEM','CORE:DANH_MUC_TRICH:XEM','DANH_MUC_TRICH','MAY_CHU_MTQ4','PHI_TIEN'),
           (1,'CORE','DANH_MUC_TRICH','SUA','CORE:DANH_MUC_TRICH:SUA','DANH_MUC_TRICH','MAY_CHU_MTQ4','PHI_TIEN'),
           (1,'CORE','DANH_MUC_TRICH','DUYET','CORE:DANH_MUC_TRICH:DUYET','DANH_MUC_TRICH','MAY_CHU_MTQ4','PHI_TIEN')
    ON CONFLICT DO NOTHING;
    FOREACH hd IN ARRAY ARRAY['XEM','SUA','DUYET'] LOOP
        IF NOT EXISTS (SELECT FROM loi.mtq_danh_muc_hanh_dong
            WHERE phien_ban_danh_muc=1 AND module='CORE' AND man='DANH_MUC_TRICH'
              AND hanh_dong=hd AND lenh_ky_thuat='CORE:DANH_MUC_TRICH:'||hd
              AND loai_doi_tuong='DANH_MUC_TRICH' AND resolver='MAY_CHU_MTQ4' AND loai_tien='PHI_TIEN') THEN
            RAISE EXCEPTION 'LHD_XUNG_DOT_MTQ';
        END IF;
    END LOOP;

    -- Helper INVOKER, chỉ owner gọi: danh tính không lấy từ header/GUC.
    -- Dùng quyết định MTQ hiện có, không cấp ô/vai, không fallback Admin.
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_quyen(p_ma text,p_hd text)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE s loi.phien_xac_thuc; ai uuid; phong uuid; scope_id uuid; n integer; q jsonb;
    BEGIN
        IF session_user::text IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi$','dang_nhap_loi') THEN
            RETURN jsonb_build_object('ma','LHD_CHI_CORE');
        END IF;
        IF current_setting('transaction_isolation')<>'read committed' THEN
            RETURN jsonb_build_object('ma','LHD_CAN_READ_COMMITTED');
        END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        SELECT * INTO s FROM loi.phien_xac_thuc
            WHERE ma_bam=sha256(convert_to(coalesce(p_ma,''),'UTF8'))
              AND dang_nhap_csdl=session_user AND loai='NGUOI_DUNG' AND module='core';
        -- Xác minh danh tính bằng quyền phiên đã có, kể cả thiếu quyền yêu cầu.
        SELECT x.nguoi_dung_id INTO ai FROM loi.xac_minh_phien(
            p_ma,'core',s.phap_nhan_id,s.pham_vi_hanh_dong[1],NULL,NULL) x;
        IF ai IS NULL THEN RETURN jsonb_build_object('ma','LHD_PHIEN'); END IF;
        q:=jsonb_build_object('nguoi_dung_id',ai,'phap_nhan_id',s.phap_nhan_id);
        IF NOT EXISTS (SELECT FROM loi.phap_nhan WHERE id=s.phap_nhan_id AND la_demo) THEN
            RETURN q||jsonb_build_object('ma','LHD_CHI_PHAP_NHAN_DEMO');
        END IF;
        IF p_hd NOT IN ('CORE:DANH_MUC_TRICH:XEM','CORE:DANH_MUC_TRICH:SUA','CORE:DANH_MUC_TRICH:DUYET')
           OR NOT EXISTS (SELECT FROM loi.xac_minh_phien(p_ma,'core',s.phap_nhan_id,p_hd,NULL,NULL)) THEN
            RETURN q||jsonb_build_object('ma','LHD_TU_CHOI');
        END IF;
        SELECT count(*),(array_agg(g.phong_id))[1] INTO n,phong
            FROM loi.mtq_gan_vai g JOIN loi.mtq_phong p ON p.id=g.phong_id AND p.hoat_dong
            WHERE g.nguoi_dung_id=ai AND g.phap_nhan_id=s.phap_nhan_id AND g.thu_hoi_luc IS NULL;
        IF n<>1 THEN RETURN q||jsonb_build_object('ma','LHD_TU_CHOI'); END IF;
        SELECT v.id INTO scope_id FROM loi.mtq_pham_vi v JOIN loi.mtq_gan_vai g ON g.id=v.gan_vai_id
            WHERE g.nguoi_dung_id=ai AND g.phap_nhan_id=s.phap_nhan_id AND g.phong_id=phong
              AND g.thu_hoi_luc IS NULL AND v.thu_hoi_luc IS NULL AND v.phap_nhan_id=s.phap_nhan_id
              AND v.loai='PHAP_NHAN' AND v.khoa=s.phap_nhan_id::text;
        IF (loi.mtq_quyet_dinh(ai,s.phap_nhan_id,phong,p_hd,'DANH_MUC_TRICH',
            'e_trich_xuat',s.phap_nhan_id::text,'PHAP_NHAN',NULL,scope_id,NULL)->'cho_phep')
            IS DISTINCT FROM 'true'::jsonb THEN
            RETURN q||jsonb_build_object('ma','LHD_TU_CHOI');
        END IF;
        RETURN q||jsonb_build_object('ma','DAT');
    END;
    $ham$;

    -- Helper INVOKER, chỉ owner gọi: một dòng nhật ký cho mỗi lần gọi cửa.
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_kiem_toan(p_q jsonb,p_hd text,p_ma_kq text,p_doi_tuong uuid)
    RETURNS bigint LANGUAGE plpgsql VOLATILE SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE kt bigint;
    BEGIN
        INSERT INTO loi.nhat_ky_kiem_toan(nguoi_dung_id,phap_nhan_id,module,hanh_dong,
            doi_tuong,doi_tuong_id,ket_luan,request_id)
        VALUES((p_q->>'nguoi_dung_id')::uuid,(p_q->>'phap_nhan_id')::uuid,
            CASE WHEN p_q ? 'nguoi_dung_id' THEN 'core' END,p_hd,'engine_tep_cau_hinh',p_doi_tuong,
            CASE WHEN p_ma_kq IS NULL THEN 'DAT'
                WHEN p_q->>'ma' IS DISTINCT FROM 'DAT' THEN 'TU_CHOI' ELSE 'KHONG_DAT' END,
            gen_random_uuid()) RETURNING id INTO kt;
        RETURN kt;
    END;
    $ham$;

    -- Thêm loại / đổi tên, mô tả, nhóm, Ngừng: mỗi lần một dòng LOAI mới.
    -- p_so_phien_ban_cu = 0 khi thêm mới, = số phiên bản đang thấy khi sửa.
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_loai(p_ma text,p_loai text,p_thong_tin jsonb,
        p_so_phien_ban_cu integer)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE q jsonb; ma text; kt bigint; cu loi.engine_tep_cau_hinh;
        moi_id uuid := gen_random_uuid(); ghi boolean := false;
    BEGIN
        q:=loi.trich_danh_muc_quyen(p_ma,'CORE:DANH_MUC_TRICH:SUA');
        ma:=nullif(q->>'ma','DAT');
        <<kiem>>
        BEGIN
            EXIT kiem WHEN ma IS NOT NULL;
            IF coalesce(p_loai,'') !~ '^[A-Z][A-Z0-9_]{1,15}$'
               OR jsonb_typeof(p_thong_tin) IS DISTINCT FROM 'object'
               OR p_so_phien_ban_cu IS NULL OR p_so_phien_ban_cu<0 THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            IF NOT p_thong_tin ?& ARRAY['ten','mo_ta','nhom_danh_muc_hop_dong','co_kiem_logic_rieng','trang_thai']
               OR p_thong_tin-ARRAY['ten','mo_ta','nhom_danh_muc_hop_dong','co_kiem_logic_rieng','trang_thai']<>'{}'::jsonb
               OR jsonb_typeof(p_thong_tin->'ten') IS DISTINCT FROM 'string'
               OR jsonb_typeof(p_thong_tin->'mo_ta') IS DISTINCT FROM 'string'
               OR jsonb_typeof(p_thong_tin->'co_kiem_logic_rieng') IS DISTINCT FROM 'boolean' THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            IF length(btrim(p_thong_tin->>'ten')) NOT BETWEEN 1 AND 200
               OR p_thong_tin->>'ten'<>btrim(p_thong_tin->>'ten')
               OR length(p_thong_tin->>'mo_ta')>1000
               OR coalesce(p_thong_tin->>'nhom_danh_muc_hop_dong','') NOT IN
                    ('XAY_DUNG','THUE_DAT','BAN_NHA','VAY','MUA','DICH_VU','KHAC')
               OR coalesce(p_thong_tin->>'trang_thai','') NOT IN ('hoat_dong','ngung') THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            PERFORM pg_advisory_xact_lock(hashtextextended('engine_tep_cau_hinh|e_trich_xuat|'||p_loai,0));
            SELECT * INTO cu FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='LOAI' AND khoa=p_loai
                ORDER BY so_phien_ban DESC LIMIT 1;
            -- Gửi lại đúng nội dung đang có: không thêm dòng.
            EXIT kiem WHEN cu.id IS NOT NULL AND cu.tom_tat=p_thong_tin;
            IF coalesce(cu.so_phien_ban,0)<>p_so_phien_ban_cu THEN
                ma:='LHD_XUNG_DOT_PHIEN_BAN'; EXIT kiem;
            END IF;
            ghi:=true;
        END kiem;
        kt:=loi.trich_danh_muc_kiem_toan(q,'CORE:DANH_MUC_TRICH:SUA',ma,
            CASE WHEN ghi THEN moi_id ELSE cu.id END);
        IF ma IS NOT NULL THEN RETURN jsonb_build_object('ma',ma,'kiem_toan_id',kt); END IF;
        IF ghi THEN
            INSERT INTO loi.engine_tep_cau_hinh(id,ma_engine,nhom,kieu,khoa,so_phien_ban,
                tom_tat,tao_boi,kiem_toan_id)
            VALUES(moi_id,'e_trich_xuat','danh_muc_tham_so','LOAI',p_loai,coalesce(cu.so_phien_ban,0)+1,
                p_thong_tin,(q->>'nguoi_dung_id')::uuid,kt) RETURNING * INTO cu;
        END IF;
        RETURN jsonb_build_object('ma','DAT','id',cu.id,'so_phien_ban',cu.so_phien_ban,
            'khong_doi',NOT ghi,'kiem_toan_id',kt);
    END;
    $ham$;

    -- Nạp phiên bản danh mục (chỉ metadata; bytes ở kho tệp Core).
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_ghi(p_ma text,p_loai text,p_bam text,
        p_bam_noi_dung text,p_tep uuid,p_tom_tat jsonb)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE q jsonb; ma text; kt bigint; v loi.engine_tep_cau_hinh; k text; so_moi integer;
        moi_id uuid := gen_random_uuid(); ghi boolean := false;
    BEGIN
        q:=loi.trich_danh_muc_quyen(p_ma,'CORE:DANH_MUC_TRICH:SUA');
        ma:=nullif(q->>'ma','DAT');
        <<kiem>>
        BEGIN
            EXIT kiem WHEN ma IS NOT NULL;
            IF coalesce(p_loai,'') !~ '^[A-Z][A-Z0-9_]{1,15}$'
               OR coalesce(p_bam,'') !~ '^[0-9a-f]{64}$'
               OR coalesce(p_bam_noi_dung,'') !~ '^[0-9a-f]{64}$'
               OR p_tep IS NULL OR jsonb_typeof(p_tom_tat) IS DISTINCT FROM 'object' THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            IF NOT p_tom_tat ?& ARRAY['so_tham_so','so_dang_dung','so_muc_3','so_luon_hoi','co_quy_tac']
               OR p_tom_tat-ARRAY['so_tham_so','so_dang_dung','so_muc_3','so_luon_hoi','co_quy_tac']<>'{}'::jsonb
               OR jsonb_typeof(p_tom_tat->'co_quy_tac') IS DISTINCT FROM 'boolean' THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            FOREACH k IN ARRAY ARRAY['so_tham_so','so_dang_dung','so_muc_3','so_luon_hoi'] LOOP
                IF jsonb_typeof(p_tom_tat->k) IS DISTINCT FROM 'number'
                   OR (p_tom_tat->>k) !~ '^[0-9]{1,6}$' THEN
                    ma:='LHD_DAU_VAO'; EXIT kiem;
                END IF;
            END LOOP;
            IF (p_tom_tat->>'so_dang_dung')::integer<1
               OR (p_tom_tat->>'so_tham_so')::integer<(p_tom_tat->>'so_dang_dung')::integer
               OR (p_tom_tat->>'so_muc_3')::integer>(p_tom_tat->>'so_tham_so')::integer
               OR (p_tom_tat->>'so_luon_hoi')::integer>(p_tom_tat->>'so_tham_so')::integer THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            PERFORM pg_advisory_xact_lock(hashtextextended('engine_tep_cau_hinh|e_trich_xuat|'||p_loai,0));
            IF NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='LOAI' AND khoa=p_loai) THEN
                ma:='LHD_LOAI_KHONG_THAY'; EXIT kiem;
            END IF;
            IF coalesce(cardinality(loi.trich_danh_muc_tep(p_ma,(q->>'phap_nhan_id')::uuid,
                'CORE:DANH_MUC_TRICH:SUA','DANH_MUC',
                jsonb_build_object('tep_id',p_tep,'sha256',p_bam))),0)<>1 THEN
                ma:='LHD_TEP_KHONG_HOP_LE'; EXIT kiem;
            END IF;
            SELECT * INTO v FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='PHIEN_BAN' AND khoa=p_loai AND ma_bam=p_bam;
            IF v.id IS NOT NULL THEN
                IF v.ma_bam_noi_dung IS DISTINCT FROM p_bam_noi_dung
                   OR v.tom_tat IS DISTINCT FROM p_tom_tat THEN ma:='LHD_XUNG_DOT_HASH'; END IF;
                EXIT kiem;
            END IF;
            SELECT coalesce(max(so_phien_ban),0)+1 INTO so_moi FROM loi.engine_tep_cau_hinh
                WHERE ma_engine='e_trich_xuat' AND nhom='danh_muc_tham_so'
                  AND kieu='PHIEN_BAN' AND khoa=p_loai;
            ghi:=true;
        END kiem;
        kt:=loi.trich_danh_muc_kiem_toan(q,'CORE:DANH_MUC_TRICH:SUA',ma,
            CASE WHEN ghi THEN moi_id ELSE v.id END);
        IF ma IS NOT NULL THEN RETURN jsonb_build_object('ma',ma,'kiem_toan_id',kt); END IF;
        IF ghi THEN
            INSERT INTO loi.engine_tep_cau_hinh(id,ma_engine,nhom,kieu,khoa,so_phien_ban,ma_bam,
                ma_bam_noi_dung,tep_id,tom_tat,tao_boi,kiem_toan_id)
            VALUES(moi_id,'e_trich_xuat','danh_muc_tham_so','PHIEN_BAN',p_loai,so_moi,p_bam,
                p_bam_noi_dung,p_tep,p_tom_tat,(q->>'nguoi_dung_id')::uuid,kt) RETURNING * INTO v;
        END IF;
        RETURN jsonb_build_object('ma','DAT','id',v.id,'so_phien_ban',v.so_phien_ban,
            'khong_doi',NOT ghi,'kiem_toan_id',kt);
    END;
    $ham$;

    -- Kích hoạt (kế hoạch 4.6): đặt con trỏ = một dòng DANG_DUNG mới.
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_kich_hoat(p_ma text,p_loai text,p_bam text,p_ly_do text)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE q jsonb; ma text; kt bigint; pn uuid;
        loai loi.engine_tep_cau_hinh; pb loi.engine_tep_cau_hinh; dd loi.engine_tep_cau_hinh;
        viec uuid[] := '{}'::uuid[]; quay_lui boolean := false; ung_vien jsonb;
        moi_id uuid := gen_random_uuid(); ghi boolean := false;
    BEGIN
        q:=loi.trich_danh_muc_quyen(p_ma,'CORE:DANH_MUC_TRICH:DUYET');
        ma:=nullif(q->>'ma','DAT');
        pn:=(q->>'phap_nhan_id')::uuid;
        <<kiem>>
        BEGIN
            EXIT kiem WHEN ma IS NOT NULL;
            IF coalesce(p_loai,'') !~ '^[A-Z][A-Z0-9_]{1,15}$'
               OR coalesce(p_bam,'') !~ '^[0-9a-f]{64}$'
               OR coalesce(length(btrim(p_ly_do)),0) NOT BETWEEN 10 AND 1000 THEN
                ma:='LHD_DAU_VAO'; EXIT kiem;
            END IF;
            PERFORM pg_advisory_xact_lock(hashtextextended('engine_tep_cau_hinh|e_trich_xuat|'||p_loai,0));
            SELECT * INTO loai FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='LOAI' AND khoa=p_loai
                ORDER BY so_phien_ban DESC LIMIT 1;
            SELECT * INTO pb FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='PHIEN_BAN' AND khoa=p_loai AND ma_bam=p_bam;
            IF loai.id IS NULL OR pb.id IS NULL THEN ma:='LHD_LOAI_PHIEN_BAN'; EXIT kiem; END IF;
            IF loai.tom_tat->>'trang_thai'='ngung' THEN ma:='LHD_LOAI_NGUNG'; EXIT kiem; END IF;
            SELECT * INTO dd FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='DANG_DUNG' AND khoa=p_loai
                ORDER BY so_phien_ban DESC LIMIT 1;
            -- Đang dùng đúng phiên bản này: không thêm dòng.
            EXIT kiem WHEN dd.ma_bam=p_bam;
            -- Quay lui: phiên bản từng là con trỏ (dòng DANG_DUNG chỉ sinh qua cửa
            -- này hoặc seed migration, luôn có nhật ký DAT) — không cần chạy thử lại.
            quay_lui:=EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                AND nhom='danh_muc_tham_so' AND kieu='DANG_DUNG' AND khoa=p_loai AND ma_bam=p_bam);
            IF NOT quay_lui THEN
                -- Ứng viên: việc do Core tạo (việc và lần chạy đều module='core'),
                -- pháp nhân DEMO của phiên, XONG không lỗi trong 30 ngày, đúng loại/SHA.
                SELECT coalesce(jsonb_agg(jsonb_build_object('viec_id',c.id,'ket_qua_id',c.ket_qua_id,
                        'tep_id',c.tep_id,'engine_id',c.engine_id) ORDER BY c.ket_thuc_luc DESC,c.id),'[]'::jsonb)
                    INTO ung_vien FROM (
                    SELECT v.id,v.ket_qua_id,v.engine_id,v.ket_thuc_luc,
                        r.buoc->v.quy_trinh_buoc->'dau_vao'->>'tep_id' AS tep_id
                    FROM loi.hang_viec v
                    JOIN loi.quy_trinh_lan r ON r.id=v.quy_trinh_lan_id
                        AND r.phap_nhan_id=v.phap_nhan_id AND r.module=v.module
                    JOIN loi.engine_dinh_nghia e ON e.id=v.engine_id AND e.ma='e_trich_xuat'
                    JOIN loi.phap_nhan p ON p.id=v.phap_nhan_id AND p.la_demo
                    WHERE v.phap_nhan_id=pn AND v.module='core' AND r.module='core'
                      AND v.trang_thai='XONG' AND v.ma_loi IS NULL AND v.ket_qua_id IS NOT NULL
                      AND v.ket_thuc_luc>=clock_timestamp()-interval '30 days'
                      AND v.ket_thuc_luc<=clock_timestamp()
                      AND r.buoc->v.quy_trinh_buoc->'dau_vao'->'chay_thu'='true'::jsonb
                      AND r.buoc->v.quy_trinh_buoc->'dau_vao'->>'loai_hop_dong'=p_loai
                      AND r.buoc->v.quy_trinh_buoc->'dau_vao'->'danh_muc'->>'sha256'=p_bam
                      AND r.buoc->v.quy_trinh_buoc->'dau_vao'->>'tep_id'
                          ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                    ORDER BY v.ket_thuc_luc DESC,v.id LIMIT 200) c;
                -- Cầu nối lọc kết quả thành công + đếm mẫu khác bytes (không tính ba
                -- lần chạy lại cùng một hợp đồng), trả tối đa 5 id việc.
                viec:=coalesce(loi.trich_danh_muc_tep(p_ma,pn,'CORE:DANH_MUC_TRICH:DUYET',
                    'CHAY_THU',ung_vien),'{}'::uuid[]);
                IF cardinality(viec)<3 THEN ma:='LHD_CHUA_DU_CHAY_THU'; EXIT kiem; END IF;
            END IF;
            ghi:=true;
        END kiem;
        kt:=loi.trich_danh_muc_kiem_toan(q,'CORE:DANH_MUC_TRICH:DUYET',ma,
            CASE WHEN ghi THEN moi_id ELSE dd.id END);
        IF ma IS NOT NULL THEN
            RETURN jsonb_build_object('ma',ma,'kiem_toan_id',kt,'viec_chay_thu',to_jsonb(viec));
        END IF;
        IF ghi THEN
            INSERT INTO loi.engine_tep_cau_hinh(id,ma_engine,nhom,kieu,khoa,so_phien_ban,ma_bam,
                tham_chieu_id,tom_tat,tao_boi,kiem_toan_id)
            VALUES(moi_id,'e_trich_xuat','danh_muc_tham_so','DANG_DUNG',p_loai,
                coalesce(dd.so_phien_ban,0)+1,p_bam,pb.id,
                jsonb_build_object('ly_do',btrim(p_ly_do),'viec_chay_thu',to_jsonb(viec),'quay_lui',quay_lui),
                (q->>'nguoi_dung_id')::uuid,kt) RETURNING * INTO dd;
        END IF;
        RETURN jsonb_build_object('ma','DAT','id',dd.id,'so_phien_ban',dd.so_phien_ban,
            'phien_ban_danh_muc',pb.so_phien_ban,'viec_chay_thu',to_jsonb(viec),
            'quay_lui',quay_lui,'khong_doi',NOT ghi,'kiem_toan_id',kt);
    END;
    $ham$;

    -- Đọc: p_loai NULL → danh sách loại + con trỏ; có p_loai → chi tiết một loại.
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_doc(p_ma text,p_loai text)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE q jsonb; ma text; kt bigint; loai jsonb; ds jsonb; dd jsonb; ls jsonb;
    BEGIN
        q:=loi.trich_danh_muc_quyen(p_ma,'CORE:DANH_MUC_TRICH:XEM');
        ma:=nullif(q->>'ma','DAT');
        <<kiem>>
        BEGIN
            EXIT kiem WHEN ma IS NOT NULL;
            IF p_loai IS NULL THEN
                SELECT coalesce(jsonb_agg(jsonb_build_object('khoa',l.khoa,
                        'so_phien_ban',l.so_phien_ban,'thong_tin',l.tom_tat,
                        'so_phien_ban_danh_muc',(SELECT count(*) FROM loi.engine_tep_cau_hinh x
                            WHERE x.ma_engine=l.ma_engine AND x.nhom=l.nhom
                              AND x.kieu='PHIEN_BAN' AND x.khoa=l.khoa),
                        'dang_dung',CASE WHEN d.id IS NOT NULL THEN jsonb_build_object(
                            'ma_bam',d.ma_bam,'phien_ban_danh_muc',p.so_phien_ban,
                            'tao_luc',d.tao_luc,'tao_boi',d.tao_boi) END) ORDER BY l.khoa),'[]'::jsonb)
                    INTO loai
                    FROM (SELECT DISTINCT ON (khoa) * FROM loi.engine_tep_cau_hinh
                        WHERE ma_engine='e_trich_xuat' AND nhom='danh_muc_tham_so' AND kieu='LOAI'
                        ORDER BY khoa,so_phien_ban DESC) l
                    LEFT JOIN LATERAL (SELECT * FROM loi.engine_tep_cau_hinh y
                        WHERE y.ma_engine=l.ma_engine AND y.nhom=l.nhom AND y.kieu='DANG_DUNG'
                          AND y.khoa=l.khoa ORDER BY y.so_phien_ban DESC LIMIT 1) d ON true
                    LEFT JOIN loi.engine_tep_cau_hinh p ON p.id=d.tham_chieu_id;
                EXIT kiem;
            END IF;
            IF p_loai !~ '^[A-Z][A-Z0-9_]{1,15}$' THEN ma:='LHD_DAU_VAO'; EXIT kiem; END IF;
            SELECT jsonb_build_object('khoa',khoa,'so_phien_ban',so_phien_ban,'thong_tin',tom_tat,
                    'tao_luc',tao_luc,'tao_boi',tao_boi) INTO loai
                FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                  AND nhom='danh_muc_tham_so' AND kieu='LOAI' AND khoa=p_loai
                ORDER BY so_phien_ban DESC LIMIT 1;
            IF loai IS NULL THEN ma:='LHD_LOAI_KHONG_THAY'; EXIT kiem; END IF;
            SELECT coalesce(jsonb_agg(jsonb_build_object('id',id,'so_phien_ban',so_phien_ban,
                    'ma_bam',ma_bam,'ma_bam_noi_dung',ma_bam_noi_dung,'tep_id',tep_id,
                    'tom_tat',tom_tat,'tao_luc',tao_luc,'tao_boi',tao_boi) ORDER BY so_phien_ban),'[]'::jsonb)
                INTO ds FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
                  AND nhom='danh_muc_tham_so' AND kieu='PHIEN_BAN' AND khoa=p_loai;
            SELECT coalesce(jsonb_agg(jsonb_build_object('id',d.id,'so_phien_ban',d.so_phien_ban,
                    'ma_bam',d.ma_bam,'phien_ban_danh_muc',p.so_phien_ban,'can_cu',d.tom_tat,
                    'tao_luc',d.tao_luc,'tao_boi',d.tao_boi,'kiem_toan_id',d.kiem_toan_id)
                    ORDER BY d.so_phien_ban),'[]'::jsonb)
                INTO ls FROM loi.engine_tep_cau_hinh d
                JOIN loi.engine_tep_cau_hinh p ON p.id=d.tham_chieu_id
                WHERE d.ma_engine='e_trich_xuat' AND d.nhom='danh_muc_tham_so'
                  AND d.kieu='DANG_DUNG' AND d.khoa=p_loai;
            dd:=ls->-1;
        END kiem;
        kt:=loi.trich_danh_muc_kiem_toan(q,'CORE:DANH_MUC_TRICH:XEM',ma,NULL);
        IF ma IS NOT NULL THEN RETURN jsonb_build_object('ma',ma,'kiem_toan_id',kt); END IF;
        RETURN jsonb_build_object('ma','DAT','loai',loai,'phien_ban',ds,'dang_dung',dd,
            'lich_su_kich_hoat',ls,'kiem_toan_id',kt);
    END;
    $ham$;

    FOREACH ham IN ARRAY ARRAY['loi.trich_danh_muc_quyen(text,text)',
        'loi.trich_danh_muc_kiem_toan(jsonb,text,text,uuid)',
        'loi.trich_danh_muc_loai(text,text,jsonb,integer)',
        'loi.trich_danh_muc_ghi(text,text,text,text,uuid,jsonb)',
        'loi.trich_danh_muc_kich_hoat(text,text,text,text)','loi.trich_danh_muc_doc(text,text)'] LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ham);
        FOR quyen IN SELECT DISTINCT a.grantee FROM pg_proc p,LATERAL aclexplode(p.proacl) a
            WHERE p.oid=ham::regprocedure AND a.grantee<>0 AND a.grantee<>p.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I',ham,pg_get_userbyid(quyen.grantee));
        END LOOP;
    END LOOP;
    EXECUTE format('GRANT EXECUTE ON FUNCTION loi.trich_danh_muc_loai(text,text,jsonb,integer),
        loi.trich_danh_muc_ghi(text,text,text,text,uuid,jsonb),
        loi.trich_danh_muc_kich_hoat(text,text,text,text),loi.trich_danh_muc_doc(text,text) TO %I',login);

    -- Cầu nối loi_tai_lieu (mẫu 065/067): CREATE trên loi chỉ tồn tại trong
    -- transaction này; owner Core chỉ nhận EXECUTE, không USAGE loi_tai_lieu.
    EXECUTE format('GRANT CREATE ON SCHEMA loi TO %I',chu_tl);
    PERFORM set_config('role',vai_cu,true);
    EXECUTE format('SET LOCAL ROLE %I',chu_tl);
    -- DANH_MUC (p_hd SUA): {tep_id,sha256} → [tep_id] nếu tệp thuộc p_pn, đúng SHA,
    --   .xlsx, 1 B–2 MiB, không có hạn lưu giữ (het_han_luc NULL, 059); ngược lại [].
    -- CHAY_THU (p_hd DUYET): [{viec_id,ket_qua_id,tep_id,engine_id}…] (≤200, theo
    --   thứ tự ưu tiên) → tối đa 5 viec_id có kết quả tham_so.v1 1.0.0 thành công
    --   của đúng việc/engine/pháp nhân, mỗi mẫu (SHA bytes tệp) một việc.
    -- Phiên được kiểm lại qua loi_tai_lieu.ngu_canh (đặt ngữ cảnh RLS); phiên
    -- không đạt → []. Không trả nội dung, tên tệp hay SHA.
    CREATE OR REPLACE FUNCTION loi.trich_danh_muc_tep(p_ma text,p_pn uuid,p_hd text,
        p_che_do text,p_du_lieu jsonb)
    RETURNS uuid[] LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE kq uuid[] := '{}'::uuid[];
        re_uuid constant text := '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$';
    BEGIN
        IF p_pn IS NULL OR p_che_do IS NULL OR p_du_lieu IS NULL THEN RETURN kq; END IF;
        IF p_che_do='DANH_MUC' THEN
            IF p_hd IS DISTINCT FROM 'CORE:DANH_MUC_TRICH:SUA'
               OR jsonb_typeof(p_du_lieu)<>'object' THEN RETURN kq; END IF;
            IF p_du_lieu-ARRAY['tep_id','sha256']<>'{}'::jsonb
               OR coalesce(p_du_lieu->>'tep_id','') !~ re_uuid
               OR coalesce(p_du_lieu->>'sha256','') !~ '^[0-9a-f]{64}$' THEN RETURN kq; END IF;
        ELSIF p_che_do='CHAY_THU' THEN
            IF p_hd IS DISTINCT FROM 'CORE:DANH_MUC_TRICH:DUYET'
               OR jsonb_typeof(p_du_lieu)<>'array' THEN RETURN kq; END IF;
            IF jsonb_array_length(p_du_lieu)>200 OR EXISTS (
                SELECT FROM jsonb_array_elements(p_du_lieu) e WHERE CASE
                    WHEN jsonb_typeof(e)<>'object' THEN true
                    ELSE e-ARRAY['viec_id','ket_qua_id','tep_id','engine_id']<>'{}'::jsonb
                        OR coalesce(e->>'viec_id','') !~ re_uuid
                        OR coalesce(e->>'ket_qua_id','') !~ re_uuid
                        OR coalesce(e->>'tep_id','') !~ re_uuid
                        OR coalesce(e->>'engine_id','') !~ re_uuid END) THEN
                RETURN kq;
            END IF;
        ELSE
            RETURN kq;
        END IF;
        PERFORM loi_tai_lieu.ngu_canh(p_ma,'core',p_pn,p_hd,NULL,NULL);
        IF p_che_do='DANH_MUC' THEN
            SELECT coalesce(array_agg(t.id),'{}'::uuid[]) INTO kq FROM loi_tai_lieu.tep_goc t
                WHERE t.id=(p_du_lieu->>'tep_id')::uuid AND t.phap_nhan_id=p_pn
                  AND t.ma_bam=p_du_lieu->>'sha256' AND t.kich_thuoc BETWEEN 1 AND 2097152
                  AND t.mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                  AND lower(t.ten_tep) LIKE '%.xlsx' AND t.het_han_luc IS NULL;
        ELSE
            SELECT coalesce(array_agg(z.viec_id ORDER BY z.thu_tu),'{}'::uuid[]) INTO kq FROM (
                SELECT y.viec_id,y.thu_tu FROM (
                    SELECT DISTINCT ON (t.ma_bam) c.viec_id,c.thu_tu
                    FROM (SELECT (a.e->>'viec_id')::uuid AS viec_id,(a.e->>'ket_qua_id')::uuid AS ket_qua_id,
                            (a.e->>'tep_id')::uuid AS tep_id,(a.e->>'engine_id')::uuid AS engine_id,
                            a.thu_tu
                        FROM jsonb_array_elements(p_du_lieu) WITH ORDINALITY a(e,thu_tu)) c
                    JOIN loi_tai_lieu.ket_qua_xu_ly k ON k.id=c.ket_qua_id
                        AND k.phap_nhan_id=p_pn AND k.viec_id=c.viec_id
                        AND k.engine_id=c.engine_id AND k.trang_thai='thanh_cong'
                        AND k.ma_contract='tham_so.v1' AND k.phien_ban_contract='1.0.0'
                    JOIN loi_tai_lieu.tep_goc t ON t.id=c.tep_id AND t.phap_nhan_id=p_pn
                    ORDER BY t.ma_bam,c.thu_tu) y
                ORDER BY y.thu_tu LIMIT 5) z;
        END IF;
        RETURN kq;
    EXCEPTION WHEN insufficient_privilege THEN
        RETURN '{}'::uuid[];
    END;
    $ham$;
    REVOKE ALL ON FUNCTION loi.trich_danh_muc_tep(text,uuid,text,text,jsonb) FROM PUBLIC;
    FOR quyen IN SELECT DISTINCT a.grantee FROM pg_proc p,LATERAL aclexplode(p.proacl) a
        WHERE p.oid='loi.trich_danh_muc_tep(text,uuid,text,text,jsonb)'::regprocedure
          AND a.grantee<>0 AND a.grantee<>p.proowner LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION loi.trich_danh_muc_tep(text,uuid,text,text,jsonb) FROM %I',
            pg_get_userbyid(quyen.grantee));
    END LOOP;
    EXECUTE format('GRANT EXECUTE ON FUNCTION loi.trich_danh_muc_tep(text,uuid,text,text,jsonb) TO %I',chu);
    PERFORM set_config('role',vai_cu,true);
    EXECUTE format('SET LOCAL ROLE %I',chu);
    EXECUTE format('REVOKE CREATE ON SCHEMA loi FROM %I',chu_tl);
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);

    -- Seed XD v1: loại + phiên bản + con trỏ Đang dùng; không phụ thuộc hồ sơ engine.
    IF NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
        AND nhom='danh_muc_tham_so' AND kieu='LOAI' AND khoa='XD' AND so_phien_ban=1) THEN
        INSERT INTO loi.nhat_ky_kiem_toan(hanh_dong,doi_tuong,ket_luan,request_id)
        VALUES('CORE:DANH_MUC_TRICH:SUA','engine_tep_cau_hinh','DAT',gen_random_uuid()) RETURNING id INTO kt;
        INSERT INTO loi.engine_tep_cau_hinh(ma_engine,nhom,kieu,khoa,so_phien_ban,tom_tat,kiem_toan_id)
        VALUES('e_trich_xuat','danh_muc_tham_so','LOAI','XD',1,xd_loai,kt);
    END IF;
    IF NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
        AND nhom='danh_muc_tham_so' AND kieu='PHIEN_BAN' AND khoa='XD' AND so_phien_ban=1) THEN
        INSERT INTO loi.nhat_ky_kiem_toan(hanh_dong,doi_tuong,ket_luan,request_id)
        VALUES('CORE:DANH_MUC_TRICH:SUA','engine_tep_cau_hinh','DAT',gen_random_uuid()) RETURNING id INTO kt;
        INSERT INTO loi.engine_tep_cau_hinh(ma_engine,nhom,kieu,khoa,so_phien_ban,ma_bam,
            ma_bam_noi_dung,tom_tat,kiem_toan_id)
        VALUES('e_trich_xuat','danh_muc_tham_so','PHIEN_BAN','XD',1,xd,xd_nd,xd_tom_tat,kt);
    END IF;
    SELECT id INTO pb FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
        AND nhom='danh_muc_tham_so' AND kieu='PHIEN_BAN' AND khoa='XD' AND so_phien_ban=1;
    IF NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE ma_engine='e_trich_xuat'
        AND nhom='danh_muc_tham_so' AND kieu='DANG_DUNG' AND khoa='XD' AND so_phien_ban=1) THEN
        INSERT INTO loi.nhat_ky_kiem_toan(hanh_dong,doi_tuong,ket_luan,request_id)
        VALUES('CORE:DANH_MUC_TRICH:DUYET','engine_tep_cau_hinh','DAT',gen_random_uuid()) RETURNING id INTO kt;
        INSERT INTO loi.engine_tep_cau_hinh(ma_engine,nhom,kieu,khoa,so_phien_ban,ma_bam,
            tham_chieu_id,tom_tat,kiem_toan_id)
        VALUES('e_trich_xuat','danh_muc_tham_so','DANG_DUNG','XD',1,xd,pb,xd_kich_hoat,kt);
    END IF;
    IF NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE kieu='LOAI' AND khoa='XD'
            AND so_phien_ban=1 AND tom_tat=xd_loai AND tao_boi IS NULL)
       OR NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE kieu='PHIEN_BAN' AND khoa='XD'
            AND so_phien_ban=1 AND ma_bam=xd AND ma_bam_noi_dung=xd_nd AND tom_tat=xd_tom_tat
            AND tep_id IS NULL AND tao_boi IS NULL)
       OR NOT EXISTS (SELECT FROM loi.engine_tep_cau_hinh WHERE kieu='DANG_DUNG' AND khoa='XD'
            AND so_phien_ban=1 AND ma_bam=xd AND tham_chieu_id=pb AND tom_tat=xd_kich_hoat
            AND tao_boi IS NULL) THEN
        RAISE EXCEPTION 'LHD_SEED_XD_KHAC_MAU';
    END IF;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
