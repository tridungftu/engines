-- OCR-CR-9 / QD-TAM-20261108-05: nối nhật ký chốt OCR với request_id HTTP.
-- Chỉ tiến; giữ nguyên hàm năm tham số và GRANT của migration 130.
-- Overload sáu tham số nhận UUID yêu cầu, UUID biên nhận vẫn là doi_tuong_id.
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt || 'vai_doi_cau_truc_loi';
    chu_tl text := tt || 'vai_doi_cau_truc_loi_tai_lieu';
    login text := tt || 'dang_nhap_loi';
    path_cu text := current_setting('search_path');
    nen record; ham record; quyen record;
BEGIN
    IF (tt<>'' AND tt COLLATE "C" !~ '^[a-z][a-z0-9_]*_$') OR octet_length(chu_tl)>63
       OR (tt<>'' AND current_database() COLLATE "C" !~ '^kho_test_')
       OR current_database() COLLATE "C" !~ '^(kho_core_demo_g2_[a-z0-9_]+|kho_test_[a-z0-9_]+)$'
       OR current_setting('server_version_num')::integer<160000
       OR NOT EXISTS (SELECT FROM pg_roles WHERE rolname=current_user AND rolsuper)
       OR current_setting('role') COLLATE "C"<>'none' THEN
        RAISE EXCEPTION 'OCR_ADMIN_SAI_DICH';
    END IF;
    FOR nen IN SELECT * FROM (VALUES ('loi',chu),('loi_tai_lieu',chu_tl)) AS n(ten,chu_so_huu) LOOP
        IF NOT EXISTS (SELECT FROM pg_namespace ns JOIN pg_roles r ON r.oid=ns.nspowner
            WHERE ns.nspname=nen.ten AND r.rolname=nen.chu_so_huu AND NOT r.rolcanlogin
              AND NOT r.rolsuper AND NOT r.rolcreaterole AND NOT r.rolbypassrls
              AND NOT r.rolcreatedb AND NOT r.rolreplication) THEN
            RAISE EXCEPTION 'OCR_ADMIN_SAI_OWNER';
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=login AND rolcanlogin
        AND NOT rolsuper AND NOT rolcreaterole AND NOT rolbypassrls)
       OR EXISTS (SELECT FROM pg_auth_members m JOIN pg_roles r ON r.oid IN (m.roleid,m.member)
            WHERE r.rolname IN (chu,chu_tl)) THEN
        RAISE EXCEPTION 'OCR_ADMIN_SAI_VAI';
    END IF;
    FOR nen IN SELECT * FROM (VALUES ('loi.hang_viec',chu),('loi.lan_thu_trang_thai',chu),
        ('loi.phien_xac_thuc',chu),('loi.mtq_admin',chu),('loi.nhat_ky_kiem_toan',chu),
        ('loi_tai_lieu.bien_nhan_core',chu_tl)) AS n(ten,chu_so_huu) LOOP
        IF NOT EXISTS (SELECT FROM pg_class c WHERE c.oid=to_regclass(nen.ten)
            AND c.relkind='r' AND pg_get_userbyid(c.relowner)=nen.chu_so_huu
            AND c.relrowsecurity AND c.relforcerowsecurity) THEN
            RAISE EXCEPTION 'OCR_ADMIN_THIEU_NEN';
        END IF;
    END LOOP;
    IF to_regprocedure('loi.ocr_chua_ro_admin_kiem(uuid,uuid)') IS NULL
       OR to_regprocedure('loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text)') IS NULL
       OR to_regprocedure('loi.ghi_kiem_toan_v2(text,text,uuid,text,text,uuid,text,uuid,text,uuid,bigint)') IS NULL THEN
        RAISE EXCEPTION 'OCR_ADMIN_THIEU_NEN';
    END IF;
    FOR ham IN SELECT * FROM (VALUES
        ('loi.ocr_chua_ro_admin_kiem(uuid,uuid)',chu),
        ('loi.ghi_kiem_toan_v2(text,text,uuid,text,text,uuid,text,uuid,text,uuid,bigint)',chu),
        ('loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text)',chu_tl),
        ('loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text,uuid)',chu_tl)
    ) AS h(chu_ky,chu_so_huu) LOOP
        IF EXISTS (SELECT FROM pg_proc p WHERE p.oid=to_regprocedure(ham.chu_ky)
            AND pg_get_userbyid(p.proowner)<>ham.chu_so_huu) THEN
            RAISE EXCEPTION 'OCR_ADMIN_SAI_OWNER_HAM';
        END IF;
    END LOOP;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);

    CREATE OR REPLACE FUNCTION loi_tai_lieu.ocr_chua_ro_chot_admin(
        p_pn uuid,p_ma_tuong_quan text,p_phien_ban bigint,p_ket_qua text,p_ghi_chu text,p_request_id uuid
    ) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $chot$
    DECLARE ai uuid; so_khop bigint; luot_id uuid; bam_luot text; bien_nhan record; viec_luot uuid;
        tt_moi text; tt_truoc text; kq jsonb; pn_cu text := current_setting('ktt.ocr_phap_nhan_id',true);
    BEGIN
        IF current_setting('ktt.hanh_dong',true) IS DISTINCT FROM 'CORE:ENGINE:CAU_HINH' THEN
            RAISE EXCEPTION 'OCR_ADMIN_PHIEN' USING ERRCODE='42501';
        END IF;
        ai := loi.ocr_chua_ro_admin_kiem(p_pn,NULL);
        IF current_setting('transaction_isolation') COLLATE "C"<>'read committed' THEN
            RAISE EXCEPTION 'OCR_ADMIN_CAN_READ_COMMITTED' USING ERRCODE='25000';
        END IF;
        IF p_ma_tuong_quan IS NULL OR p_ma_tuong_quan COLLATE "C" !~ '^ocr:[0-9a-f]{1,124}$'
           OR p_phien_ban IS NULL OR p_phien_ban<1 OR p_phien_ban>=9223372036854775807
           OR p_ket_qua IS NULL OR p_ket_qua COLLATE "C" NOT IN ('da_tieu','hoan_trang')
           OR p_ghi_chu IS NULL OR btrim(p_ghi_chu)='' OR p_ghi_chu !~ '[^[:space:]]'
           OR length(p_ghi_chu)>500 OR p_request_id IS NULL THEN
            RAISE EXCEPTION 'OCR_ADMIN_DAU_VAO' USING ERRCODE='22023';
        END IF;
        PERFORM set_config('ktt.ocr_phap_nhan_id',p_pn::text,true);
        SELECT count(*),min(b.id::text)::uuid,min(b.ma_bam) INTO so_khop,luot_id,bam_luot
            FROM loi_tai_lieu.bien_nhan_core b WHERE b.phap_nhan_id=p_pn
              AND b.operation COLLATE "C"='ocr.abbyy'
              AND b.ket_qua->>'ma_tuong_quan'=p_ma_tuong_quan
              AND b.trang_thai COLLATE "C" IN ('CHUA_RO','DANG_XU_LY');
        IF so_khop<>1 THEN RAISE EXCEPTION 'OCR_ADMIN_XUNG_DOT' USING ERRCODE='40001'; END IF;
        IF NOT pg_try_advisory_xact_lock(hashtextextended(
            jsonb_build_array('ocr.abbyy',p_pn,bam_luot)::text,126)) THEN
            RAISE EXCEPTION 'OCR_ADMIN_XUNG_DOT' USING ERRCODE='40001';
        END IF;
        SELECT b.* INTO bien_nhan FROM loi_tai_lieu.bien_nhan_core b
            WHERE b.id=luot_id AND b.phap_nhan_id=p_pn AND b.operation COLLATE "C"='ocr.abbyy'
            FOR UPDATE OF b;
        IF NOT FOUND OR bien_nhan.ket_qua->'phien_ban' IS DISTINCT FROM to_jsonb(p_phien_ban)
           OR bien_nhan.trang_thai NOT IN ('CHUA_RO','DANG_XU_LY') THEN
            RAISE EXCEPTION 'OCR_ADMIN_XUNG_DOT' USING ERRCODE='40001';
        END IF;
        IF bien_nhan.trang_thai='DANG_XU_LY' THEN
            viec_luot := CASE WHEN (bien_nhan.ket_qua->>'viec_id') COLLATE "C" ~
                '^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$'
                THEN (bien_nhan.ket_qua->>'viec_id')::uuid END;
            IF viec_luot IS NULL OR loi.ocr_chua_ro_admin_kiem(p_pn,viec_luot) IS NULL THEN
                RAISE EXCEPTION 'OCR_ADMIN_LEASE_CON_HIEU_LUC' USING ERRCODE='40001';
            END IF;
        END IF;
        tt_truoc := CASE WHEN bien_nhan.trang_thai='CHUA_RO' THEN 'CHUA_RO' ELSE 'DANG_GIU' END;
        tt_moi := CASE WHEN p_ket_qua='da_tieu' THEN 'DA_TIEU_TRANG' ELSE 'HOAN_TRANG' END;
        UPDATE loi_tai_lieu.bien_nhan_core b SET
            ket_qua=b.ket_qua || jsonb_build_object('trang_thai',tt_moi,'phien_ban',p_phien_ban+1),
            quyen_doc=b.quyen_doc || jsonb_build_object('doi_chieu_admin',jsonb_build_object(
                'trang_thai_truoc',tt_truoc,'chot_boi',ai,'ghi_chu',p_ghi_chu,
                'chot_luc',clock_timestamp(),'ket_qua',p_ket_qua)),
            trang_thai='HOAN_TAT',ket_qua_cuoi_luc=clock_timestamp()
            WHERE b.id=luot_id AND b.phap_nhan_id=p_pn AND b.ket_qua->'phien_ban'=to_jsonb(p_phien_ban)
              AND b.trang_thai=bien_nhan.trang_thai RETURNING b.ket_qua INTO kq;
        IF NOT FOUND THEN RAISE EXCEPTION 'OCR_ADMIN_XUNG_DOT' USING ERRCODE='40001'; END IF;
        PERFORM loi.ghi_kiem_toan_v2(current_setting('ktt.ma_phien',true),'core',p_pn,
            'CORE:ENGINE:CAU_HINH','ocr_doi_chieu_admin',luot_id,'DAT',p_request_id,'1',NULL,NULL);
        PERFORM set_config('ktt.ocr_phap_nhan_id',coalesce(pn_cu,''),true);
        RETURN jsonb_build_object('ma_tuong_quan',kq->>'ma_tuong_quan','so_trang',kq->'so_trang',
            'trang_thai',kq->>'trang_thai','phien_ban',kq->'phien_ban');
    END;
    $chot$;
    EXECUTE format('ALTER FUNCTION loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text,uuid) OWNER TO %I',chu_tl);

    -- Chỉ bỏ ràng buộc request = biên nhận ở nhánh Core; giữ nguyên nhánh SDK.
    CREATE OR REPLACE FUNCTION loi.ghi_kiem_toan_v2(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_doi_tuong text,p_doi_tuong_id uuid,p_ket_luan text,p_request uuid,
        p_contract text DEFAULT '1',p_viec uuid DEFAULT NULL,p_the_he bigint DEFAULT NULL) RETURNS bigint
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $audit$
    DECLARE ai uuid; q jsonb; co jsonb; can text;
    BEGIN
        IF p_module COLLATE "C"='core' THEN
            IF session_user::text COLLATE "C" IS DISTINCT FROM regexp_replace(current_user::text,
                'vai_doi_cau_truc_loi$','dang_nhap_loi')
               OR p_hd IS DISTINCT FROM 'CORE:ENGINE:CAU_HINH'
               OR p_doi_tuong IS DISTINCT FROM 'ocr_doi_chieu_admin'
               OR p_ket_luan IS DISTINCT FROM 'DAT' OR p_contract IS DISTINCT FROM '1'
               OR p_doi_tuong_id IS NULL OR p_request IS NULL
               OR p_viec IS NOT NULL OR p_the_he IS NOT NULL
               OR p_ma IS DISTINCT FROM current_setting('ktt.ma_phien',true)
               OR current_setting('ktt.hanh_dong',true) IS DISTINCT FROM p_hd THEN
                RAISE EXCEPTION 'OCR_ADMIN_PHIEN' USING ERRCODE='42501';
            END IF;
            PERFORM loi.ocr_chua_ro_admin_kiem(p_pn,NULL);
            RETURN loi.ghi_kiem_toan(p_hd,p_doi_tuong,p_doi_tuong_id,p_ket_luan,
                p_ma,p_module,p_pn,p_request,p_viec,p_the_he);
        END IF;
        IF p_module IS NULL OR session_user::text IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi$','dang_nhap_mod_'||p_module) THEN
            RAISE EXCEPTION 'SDK_MODULE' USING ERRCODE='42501';
        END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        SELECT nguoi_dung_id INTO ai FROM loi.xac_minh_phien(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        IF ai IS NULL OR split_part(p_hd,':',1) IS DISTINCT FROM upper(p_module) THEN
            RAISE EXCEPTION 'TAI_LIEU_PHIEN' USING ERRCODE='42501';
        END IF;
        PERFORM set_config('ktt.ma_phien',p_ma,true), set_config('ktt.module',p_module,true),
            set_config('ktt.phap_nhan_id',p_pn::text,true), set_config('ktt.hanh_dong',p_hd,true),
            set_config('ktt.viec_id',coalesce(p_viec::text,''),true),
            set_config('ktt.the_he',coalesce(p_the_he::text,''),true);
        IF p_request IS NULL OR p_doi_tuong_id IS NULL THEN
            RAISE EXCEPTION 'SDK_DAU_VAO' USING ERRCODE='22023';
        END IF;
        q := loi.mtq_quyet_dinh_phien(p_ma,p_module,p_pn,p_hd,
            jsonb_build_object('bang',p_doi_tuong,'id',p_doi_tuong_id),p_contract,'{}',p_viec,p_the_he);
        IF q->'cho_phep' IS DISTINCT FROM 'true'::jsonb THEN
            RAISE EXCEPTION 'TAI_LIEU_MTQ' USING ERRCODE='42501';
        END IF;
        co := loi.module_trang_thai(p_ma,p_module,p_pn,p_hd,p_module,p_viec,p_the_he);
        can := CASE WHEN split_part(p_hd,':',3)='XEM' THEN 'cho_xem' ELSE 'cho_ghi' END;
        IF co->can IS DISTINCT FROM 'true'::jsonb THEN
            RAISE EXCEPTION 'TAI_LIEU_CONG_TAC' USING ERRCODE='42501';
        END IF;
        RETURN loi.ghi_kiem_toan(p_hd,p_doi_tuong,p_doi_tuong_id,p_ket_luan,
            p_ma,p_module,p_pn,p_request,p_viec,p_the_he);
    END;
    $audit$;
    EXECUTE format('ALTER FUNCTION loi.ghi_kiem_toan_v2(text,text,uuid,text,text,uuid,text,uuid,text,uuid,bigint) OWNER TO %I',chu);
    REVOKE ALL ON FUNCTION loi.ghi_kiem_toan_v2(text,text,uuid,text,text,uuid,text,uuid,text,uuid,bigint) FROM PUBLIC;
    EXECUTE format('GRANT EXECUTE ON FUNCTION loi.ghi_kiem_toan_v2(text,text,uuid,text,text,uuid,text,uuid,text,uuid,bigint) TO %I',chu_tl);

    -- Chỉ hội tụ ACL overload mới; không thu hồi GRANT hàm cũ hoặc SDK module.
    FOR ham IN SELECT * FROM (VALUES
        ('loi_tai_lieu.ocr_chua_ro_chot_admin(uuid,text,bigint,text,text,uuid)',login)
    ) AS h(chu_ky,duoc_goi) LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ham.chu_ky);
        FOR quyen IN SELECT DISTINCT a.grantee FROM pg_proc p,LATERAL aclexplode(p.proacl) a
            WHERE p.oid=to_regprocedure(ham.chu_ky) AND a.grantee<>0 AND a.grantee<>p.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I',ham.chu_ky,pg_get_userbyid(quyen.grantee));
        END LOOP;
        EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ham.chu_ky,ham.duoc_goi);
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
END;
$migration$;
