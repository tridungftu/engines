-- MASK-3-PHIEN: xác minh phiên/ủy nhiệm và tài liệu trước khi cấp mã.
-- Người gửi và DEMO suy từ phiên; không tin cờ hoặc GUC do caller tự đặt.
-- Áp sau 113/117; chạy lại phải theo chuỗi 113 -> 117 -> 118 để khép cửa cũ.
-- Chỉ Core DEMO/test PG16+, caller giữ transaction; không đổi SDK/capability.
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt || 'vai_doi_cau_truc_loi';
    chu_tl text := tt || 'vai_doi_cau_truc_loi_tai_lieu';
    chu_mask text := tt || 'vai_doi_cau_truc_mask';
    chay_mask text := tt || 'vai_chay_mask';
    login text := tt || 'dang_nhap_loi';
    vai_cu text := current_setting('role');
    path_cu text := current_setting('search_path');
    bang text; ck text; b record; q record;
BEGIN
    IF (tt<>'' AND tt !~ '^[a-z][a-z0-9_]*_$')
       OR octet_length(tt || 'vai_doi_cau_truc_loi_tai_lieu')>63
       OR (tt<>'' AND current_database() !~ '^kho_test_')
       OR current_database() !~ '^(kho_core_demo_g2_[a-z0-9_]+|kho_test_[a-z0-9_]+)$'
       OR current_setting('server_version_num')::integer<160000
       OR NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user)
       OR vai_cu<>'none' THEN
        RAISE EXCEPTION 'MASK_PHIEN_SAI_DICH';
    END IF;
    FOREACH ck IN ARRAY ARRAY[chu,chu_tl,chu_mask,chay_mask] LOOP
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=ck AND NOT rolcanlogin
            AND rolinherit AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole
            AND NOT rolcreatedb AND NOT rolreplication) THEN
            RAISE EXCEPTION 'MASK_PHIEN_SAI_VAI';
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='loi' AND pg_get_userbyid(nspowner)=chu)
       OR NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='loi_tai_lieu' AND pg_get_userbyid(nspowner)=chu_tl)
       OR NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='mask' AND pg_get_userbyid(nspowner)=chu_mask)
       OR NOT EXISTS (SELECT FROM pg_roles WHERE rolname=login AND rolcanlogin
            AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole)
       OR EXISTS (SELECT FROM pg_auth_members WHERE roleid IN
            (SELECT oid FROM pg_roles WHERE rolname IN (chu_mask,chay_mask))
            OR member IN (SELECT oid FROM pg_roles WHERE rolname IN (chu_mask,chay_mask)))
       OR to_regprocedure('loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi.mask_kiem_admin(text,uuid,text,uuid)') IS NULL
       OR to_regprocedure('loi_tai_lieu.ngu_canh(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.kiem_quyen(text,text,uuid,text,jsonb,text,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.duoc_xem_noi_dung(uuid,uuid,text)') IS NULL
       OR to_regcollation('"und-x-icu"') IS NULL
       OR to_regprocedure('mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)') IS NULL THEN
        RAISE EXCEPTION 'MASK_PHIEN_THIEU_NEN';
    END IF;
    FOREACH bang IN ARRAY ARRAY['phien_xac_thuc','phap_nhan','nguoi_dung','phan_quyen'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu
            AND relrowsecurity AND relforcerowsecurity) THEN
            RAISE EXCEPTION 'MASK_PHIEN_THIEU_NEN';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['tai_lieu','quyen_tai_lieu'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi_tai_lieu.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu_tl
            AND relrowsecurity AND relforcerowsecurity)
           OR NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('loi_tai_lieu.'||bang)
                AND polname='tai_lieu_phien') THEN
            RAISE EXCEPTION 'MASK_PHIEN_THIEU_NEN';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['dinh_danh','cho_duyet','yeu_cau'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('mask.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu_mask
            AND relrowsecurity AND relforcerowsecurity)
           OR NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('mask.'||bang)
                AND polname='vung_demo')
           OR EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('mask.'||bang)
                AND polname<>'vung_demo') THEN
            RAISE EXCEPTION 'MASK_PHIEN_SAI_BANG_HOAC_RLS';
        END IF;
    END LOOP;
    FOR b IN SELECT p.* FROM pg_proc p WHERE p.oid IN (
        to_regprocedure('mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)'),
        to_regprocedure('mask.cap_ma_yeu_cau(text,text,uuid,text,uuid,uuid,bigint)'),
        to_regprocedure('loi.mask_ngu_canh(text,text,uuid,text,uuid,bigint)'),
        to_regprocedure('loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)')) LOOP
        IF pg_get_userbyid(b.proowner)<>(CASE WHEN b.pronamespace='loi'::regnamespace THEN chu
            WHEN b.pronamespace='loi_tai_lieu'::regnamespace THEN chu_tl ELSE chu_mask END) THEN
            RAISE EXCEPTION 'MASK_PHIEN_SAI_OWNER';
        END IF;
    END LOOP;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);
    -- Helper liên khối chỉ owner Mask gọi; không cấp đọc bảng hoặc membership.
    EXECUTE format('GRANT USAGE ON SCHEMA loi,loi_tai_lieu TO %I',chu_mask);
    EXECUTE format('SET LOCAL ROLE %I',chu);
    CREATE OR REPLACE FUNCTION loi.mask_ngu_canh(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint)
    RETURNS TABLE(nguoi_gui uuid,phap_nhan_id uuid,la_demo boolean)
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record;
    BEGIN
        IF session_user::text IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'MASK_CHI_CORE' USING ERRCODE='42501';
        END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        SELECT x.* INTO ctx FROM loi.xac_minh_phien(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he) x;
        IF ctx.nguoi_dung_id IS NULL
           OR p_module IS NULL OR p_module !~ '^[a-z][a-z0-9_]{0,49}$'
           OR split_part(p_hd,':',1) IS DISTINCT FROM upper(p_module COLLATE "und-x-icu") THEN
            RAISE EXCEPTION 'MASK_PHIEN' USING ERRCODE='42501';
        END IF;
        RETURN QUERY SELECT ctx.nguoi_dung_id,n.id,n.la_demo
            FROM loi.phap_nhan n WHERE n.id=ctx.phap_nhan_id;
    END;
    $ham$;

    EXECUTE format('SET LOCAL ROLE %I',chu_tl);
    CREATE OR REPLACE FUNCTION loi_tai_lieu.mask_kiem_tai_lieu(p_ma text,p_module text,p_pn uuid,
        p_hd text,p_tai_lieu uuid,p_viec uuid,p_the_he bigint) RETURNS void
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ai uuid; tai_lieu loi_tai_lieu.tai_lieu;
        cu_ma text := current_setting('ktt.ma_phien',true);
        cu_module text := current_setting('ktt.module',true);
        cu_pn text := current_setting('ktt.phap_nhan_id',true);
        cu_hd text := current_setting('ktt.hanh_dong',true);
        cu_viec text := current_setting('ktt.viec_id',true);
        cu_the_he text := current_setting('ktt.the_he',true);
    BEGIN
        IF session_user::text IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi_tai_lieu$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'MASK_CHI_CORE' USING ERRCODE='42501';
        END IF;
        ai := loi_tai_lieu.ngu_canh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        SELECT tl.* INTO tai_lieu FROM loi_tai_lieu.tai_lieu tl
            WHERE tl.id=p_tai_lieu AND tl.module=p_module AND tl.phap_nhan_id=p_pn;
        IF tai_lieu.id IS NULL THEN
            RAISE EXCEPTION 'MASK_TAI_LIEU' USING ERRCODE='42501';
        END IF;
        PERFORM loi_tai_lieu.kiem_quyen(p_ma,p_module,p_pn,p_hd,
            jsonb_build_object('bang',tai_lieu.bang_doi_tuong,'id',tai_lieu.doi_tuong_id),
            tai_lieu.phien_ban_contract,'cho_xem',p_viec,p_the_he);
        IF NOT loi_tai_lieu.duoc_xem_noi_dung(p_tai_lieu,ai,'goc') THEN
            RAISE EXCEPTION 'MASK_TAI_LIEU' USING ERRCODE='42501';
        END IF;
        PERFORM set_config('ktt.ma_phien',coalesce(cu_ma,''),true),
            set_config('ktt.module',coalesce(cu_module,''),true),
            set_config('ktt.phap_nhan_id',coalesce(cu_pn,''),true),
            set_config('ktt.hanh_dong',coalesce(cu_hd,''),true),
            set_config('ktt.viec_id',coalesce(cu_viec,''),true),
            set_config('ktt.the_he',coalesce(cu_the_he,''),true);
    END;
    $ham$;

    EXECUTE format('SET LOCAL ROLE %I',chu_mask);
    CREATE OR REPLACE FUNCTION mask.cap_ma_yeu_cau(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_tai_lieu uuid,p_viec uuid DEFAULT NULL,p_the_he bigint DEFAULT NULL) RETURNS uuid
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; ma uuid; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_ngu_canh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        PERFORM loi_tai_lieu.mask_kiem_tai_lieu(p_ma,p_module,ctx.phap_nhan_id,p_hd,
            p_tai_lieu,p_viec,p_the_he);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        INSERT INTO mask.yeu_cau(module,nguoi_gui,tai_lieu_id,la_demo)
            VALUES(p_module,ctx.nguoi_gui,p_tai_lieu,ctx.la_demo) RETURNING id INTO ma;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN ma;
    END;
    $ham$;

    PERFORM set_config('role',vai_cu,true);
    -- Giữ nguyên hàm cũ và EXECUTE của owner NOLOGIN, không có membership.
    -- Validator PL/pgSQL cần EXECUTE khi 113 CREATE OR REPLACE dưới owner;
    -- thu quyền này gây 42501: permission denied for function cap_ma_yeu_cau.
    -- Chỉ thu ACL caller và grant option phụ thuộc, không đổi thuộc tính hàm.
    EXECUTE format('REVOKE EXECUTE ON FUNCTION mask.cap_ma_yeu_cau(text,uuid,uuid,boolean) FROM PUBLIC CASCADE');
    FOR q IN SELECT DISTINCT a.grantee FROM pg_proc p,
        LATERAL aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a
        WHERE p.oid='mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)'::regprocedure
            AND a.grantee<>0 AND a.grantee<>p.proowner LOOP
        EXECUTE format('REVOKE EXECUTE ON FUNCTION mask.cap_ma_yeu_cau(text,uuid,uuid,boolean) FROM %I CASCADE',
            pg_get_userbyid(q.grantee));
    END LOOP;
    FOR b IN SELECT p.* FROM pg_proc p WHERE p.oid IN (
        'loi.mask_ngu_canh(text,text,uuid,text,uuid,bigint)'::regprocedure,
        'loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)'::regprocedure,
        'mask.cap_ma_yeu_cau(text,text,uuid,text,uuid,uuid,bigint)'::regprocedure) LOOP
        ck := b.oid::regprocedure::text;
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ck);
        FOR q IN SELECT DISTINCT a.grantee FROM aclexplode(b.proacl) a
            WHERE a.grantee<>0 AND a.grantee<>b.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I CASCADE',ck,pg_get_userbyid(q.grantee));
        END LOOP;
        IF b.pronamespace='mask'::regnamespace THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,login);
        ELSE
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,chu_mask);
        END IF;
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
