-- OCR-CR-1 / QD-20261107-05: lưu bền lượt ABBYY trước khi gửi.
-- Dùng biên nhận 011 gắn hàng việc 014; không lưu nội dung/tên/đường dẫn tệp.
-- Core xác minh nguồn, quyền và lease ở tầng gọi; commit giữ lượt trước gửi.
-- Khóa theo pháp nhân + băm, không theo module/người tạo (QD-TAM-20261107-08).
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt || 'vai_doi_cau_truc_loi';
    chu_tl text := tt || 'vai_doi_cau_truc_loi_tai_lieu';
    login text := tt || 'dang_nhap_loi';
    vai_cu text := current_setting('role');
    path_cu text := current_setting('search_path');
    nen record; ham record; quyen record;
BEGIN
    IF (tt<>'' AND tt COLLATE "C" !~ '^[a-z][a-z0-9_]*_$') OR octet_length(chu_tl)>63
       OR (tt<>'' AND current_database() COLLATE "C" !~ '^kho_test_')
       OR current_database() COLLATE "C" !~ '^(kho_core_demo_g2_[a-z0-9_]+|kho_test_[a-z0-9_]+)$'
       OR current_setting('server_version_num')::integer<160000
       OR NOT EXISTS (SELECT FROM pg_roles WHERE rolname=current_user AND rolsuper)
       OR vai_cu COLLATE "C"<>'none' THEN
        RAISE EXCEPTION 'OCR_LUOT_SAI_DICH';
    END IF;
    FOR nen IN SELECT * FROM (VALUES ('loi',chu),('loi_tai_lieu',chu_tl)) AS n(ten,chu_so_huu) LOOP
        IF NOT EXISTS (SELECT FROM pg_namespace ns JOIN pg_roles r ON r.oid=ns.nspowner
            WHERE ns.nspname=nen.ten AND r.rolname=nen.chu_so_huu AND NOT r.rolcanlogin
              AND NOT r.rolsuper AND NOT r.rolcreaterole AND NOT r.rolbypassrls
              AND NOT r.rolcreatedb AND NOT r.rolreplication) THEN
            RAISE EXCEPTION 'OCR_LUOT_SAI_OWNER';
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=login AND rolcanlogin
        AND NOT rolsuper AND NOT rolcreaterole AND NOT rolbypassrls)
       OR EXISTS (SELECT FROM pg_auth_members m JOIN pg_roles r
            ON r.oid IN (m.roleid,m.member) WHERE r.rolname IN (chu,chu_tl)) THEN
        RAISE EXCEPTION 'OCR_LUOT_SAI_VAI';
    END IF;
    FOR nen IN SELECT * FROM (VALUES
        ('loi.hang_viec',chu,'viec_chu'),
        ('loi_tai_lieu.bien_nhan_core',chu_tl,'tiep_nhan_phien')
    ) AS n(ten,chu_so_huu,chinh_sach) LOOP
        IF NOT EXISTS (SELECT FROM pg_class c WHERE c.oid=to_regclass(nen.ten)
            AND c.relkind='r' AND pg_get_userbyid(c.relowner)=nen.chu_so_huu
            AND c.relrowsecurity AND c.relforcerowsecurity)
           OR NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass(nen.ten)
                AND polname=nen.chinh_sach) THEN
            RAISE EXCEPTION 'OCR_LUOT_THIEU_NEN';
        END IF;
    END LOOP;
    -- Chạy lại giữ OID/owner, không nhận hàm cùng chữ ký do owner khác cài.
    FOR ham IN SELECT * FROM (VALUES
        ('loi.ocr_viec(uuid,uuid)',chu),
        ('loi_tai_lieu.ocr_giu_luot(uuid,text,uuid,text,integer,uuid)',chu_tl),
        ('loi_tai_lieu.ocr_chot_luot(uuid,text,uuid,bigint,text,text)',chu_tl),
        ('loi_tai_lieu.ocr_doc_trang_thai(uuid,text)',chu_tl)
    ) AS h(chu_ky,chu_so_huu) LOOP
        IF EXISTS (SELECT FROM pg_proc p WHERE p.oid=to_regprocedure(ham.chu_ky)
            AND pg_get_userbyid(p.proowner)<>ham.chu_so_huu) THEN
            RAISE EXCEPTION 'OCR_LUOT_SAI_OWNER_HAM';
        END IF;
    END LOOP;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);

    CREATE OR REPLACE FUNCTION loi.ocr_viec(p_pn uuid,p_viec uuid) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $viec$
    DECLARE kq jsonb;
    BEGIN
        IF session_user::text COLLATE "C" IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'OCR_LUOT_CHI_CORE' USING ERRCODE='42501';
        END IF;
        SELECT jsonb_build_object('module',v.module,'tao_boi',v.tao_boi) INTO kq
            FROM loi.hang_viec v WHERE v.id=p_viec AND v.phap_nhan_id=p_pn FOR SHARE OF v;
        IF kq IS NULL THEN
            RAISE EXCEPTION 'OCR_LUOT_SAI_VIEC' USING ERRCODE='22023';
        END IF;
        RETURN kq;
    END;
    $viec$;
    EXECUTE format('ALTER FUNCTION loi.ocr_viec(uuid,uuid) OWNER TO %I',chu);

    -- Đối chiếu có thể xảy ra sau khi việc XONG/fallback và phiên hết hạn.
    -- Policy nội bộ chỉ mở các dòng OCR cho login Core, trong pháp nhân đã đặt;
    -- không cấp quyền bảng, không thay policy phiên/module hiện có.
    IF NOT EXISTS (SELECT FROM pg_policy WHERE polrelid='loi_tai_lieu.bien_nhan_core'::regclass
        AND polname='ocr_luot_core') THEN
        EXECUTE format('CREATE POLICY ocr_luot_core ON loi_tai_lieu.bien_nhan_core TO %I
            USING (false) WITH CHECK (false)',chu_tl);
    END IF;
    IF NOT EXISTS (SELECT FROM pg_policy p JOIN pg_roles r ON r.oid=ANY(p.polroles)
        WHERE p.polrelid='loi_tai_lieu.bien_nhan_core'::regclass AND p.polname='ocr_luot_core'
          AND p.polcmd='*' AND p.polpermissive AND p.polroles=ARRAY[r.oid] AND r.rolname=chu_tl) THEN
        RAISE EXCEPTION 'OCR_LUOT_SAI_POLICY';
    END IF;
    EXECUTE format('ALTER POLICY ocr_luot_core ON loi_tai_lieu.bien_nhan_core
        USING (operation COLLATE "C"=''ocr.abbyy'' AND session_user::text COLLATE "C"=%1$L
            AND phap_nhan_id::text COLLATE "C"=current_setting(''ktt.ocr_phap_nhan_id'',true))
        WITH CHECK (operation COLLATE "C"=''ocr.abbyy'' AND session_user::text COLLATE "C"=%1$L
            AND phap_nhan_id::text COLLATE "C"=current_setting(''ktt.ocr_phap_nhan_id'',true))',login);

    CREATE OR REPLACE FUNCTION loi_tai_lieu.ocr_giu_luot(
        p_pn uuid,p_bam text,p_viec uuid,p_tuong_quan text,p_so_trang integer,p_giu_trang uuid
    ) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $giu$
    DECLARE viec jsonb; kq jsonb; pn_cu text := current_setting('ktt.ocr_phap_nhan_id',true);
    BEGIN
        IF session_user::text COLLATE "C" IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi_tai_lieu$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'OCR_LUOT_CHI_CORE' USING ERRCODE='42501';
        END IF;
        IF current_setting('transaction_isolation') COLLATE "C"<>'read committed' THEN
            RAISE EXCEPTION 'OCR_LUOT_CAN_READ_COMMITTED' USING ERRCODE='25000';
        END IF;
        IF p_pn IS NULL OR p_bam IS NULL OR p_bam COLLATE "C" !~ '^[0-9a-f]{64}$'
           OR p_viec IS NULL OR p_giu_trang IS NULL OR p_so_trang IS NULL OR p_so_trang<=0
           OR p_tuong_quan IS NULL OR p_tuong_quan COLLATE "C" !~ '^[A-Za-z0-9_:-]{1,128}$' THEN
            RAISE EXCEPTION 'OCR_LUOT_DAU_VAO' USING ERRCODE='22023';
        END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        IF NOT pg_try_advisory_xact_lock(hashtextextended(
            jsonb_build_array('ocr.abbyy',p_pn,p_bam)::text,126)) THEN
            RAISE EXCEPTION 'OCR_LUOT_DANG_BI_CHAN' USING ERRCODE='P0001';
        END IF;
        PERFORM set_config('ktt.ocr_phap_nhan_id',p_pn::text,true);
        IF EXISTS (SELECT FROM loi_tai_lieu.bien_nhan_core b
            WHERE b.phap_nhan_id=p_pn AND b.ma_bam COLLATE "C"=p_bam
              AND b.operation COLLATE "C"='ocr.abbyy'
              AND b.trang_thai COLLATE "C" IN ('DANG_XU_LY','CHUA_RO')) THEN
            RAISE EXCEPTION 'OCR_LUOT_DANG_BI_CHAN' USING ERRCODE='P0001';
        END IF;
        viec := loi.ocr_viec(p_pn,p_viec);
        kq := jsonb_build_object('giu_trang_id',p_giu_trang,'viec_id',p_viec,
            'ma_tuong_quan',p_tuong_quan,'so_trang',p_so_trang,'trang_thai','GIU','phien_ban',1);
        INSERT INTO loi_tai_lieu.bien_nhan_core(id,phap_nhan_id,module,operation,khoa_chong_trung,
            ma_bam,ket_qua,quyen_doc,trang_thai,tao_boi)
            VALUES(p_giu_trang,p_pn,viec->>'module','ocr.abbyy','ocr:'||p_giu_trang::text,
                p_bam,kq,'{}'::jsonb,'DANG_XU_LY',(viec->>'tao_boi')::uuid);
        PERFORM set_config('ktt.ocr_phap_nhan_id',coalesce(pn_cu,''),true);
        RETURN kq;
    END;
    $giu$;
    EXECUTE format('ALTER FUNCTION loi_tai_lieu.ocr_giu_luot(uuid,text,uuid,text,integer,uuid) OWNER TO %I',chu_tl);

    -- CHUA_RO là dấu bền, không có TTL. Chốt cuối không thể hoàn/tiêu lần hai.
    CREATE OR REPLACE FUNCTION loi_tai_lieu.ocr_chot_luot(
        p_pn uuid,p_bam text,p_giu_trang uuid,p_phien_ban bigint,p_trang_thai_cu text,p_trang_thai_moi text
    ) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $chot$
    DECLARE kq jsonb; pn_cu text := current_setting('ktt.ocr_phap_nhan_id',true);
    BEGIN
        IF session_user::text COLLATE "C" IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi_tai_lieu$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'OCR_LUOT_CHI_CORE' USING ERRCODE='42501';
        END IF;
        IF current_setting('transaction_isolation') COLLATE "C"<>'read committed' THEN
            RAISE EXCEPTION 'OCR_LUOT_CAN_READ_COMMITTED' USING ERRCODE='25000';
        END IF;
        IF p_pn IS NULL OR p_bam IS NULL OR p_bam COLLATE "C" !~ '^[0-9a-f]{64}$'
           OR p_giu_trang IS NULL OR p_phien_ban IS NULL OR p_phien_ban<1
           OR p_trang_thai_cu IS NULL OR p_trang_thai_cu COLLATE "C" NOT IN ('GIU','CHUA_RO')
           OR p_trang_thai_moi IS NULL OR p_trang_thai_moi COLLATE "C" NOT IN ('CHUA_RO','DA_TIEU_TRANG','HOAN_TRANG')
           OR (p_trang_thai_moi COLLATE "C"='CHUA_RO' AND p_trang_thai_cu COLLATE "C"<>'GIU') THEN
            RAISE EXCEPTION 'OCR_LUOT_DAU_VAO' USING ERRCODE='22023';
        END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        IF NOT pg_try_advisory_xact_lock(hashtextextended(
            jsonb_build_array('ocr.abbyy',p_pn,p_bam)::text,126)) THEN
            RAISE EXCEPTION 'OCR_LUOT_DANG_BI_CHAN' USING ERRCODE='P0001';
        END IF;
        PERFORM set_config('ktt.ocr_phap_nhan_id',p_pn::text,true);
        UPDATE loi_tai_lieu.bien_nhan_core b
            SET ket_qua=b.ket_qua || jsonb_build_object('trang_thai',p_trang_thai_moi,'phien_ban',p_phien_ban+1),
                trang_thai=CASE WHEN p_trang_thai_moi COLLATE "C"='CHUA_RO' THEN 'CHUA_RO' ELSE 'HOAN_TAT' END,
                ket_qua_cuoi_luc=CASE WHEN p_trang_thai_moi COLLATE "C"<>'CHUA_RO' THEN clock_timestamp() END
            WHERE b.id=p_giu_trang AND b.phap_nhan_id=p_pn AND b.ma_bam COLLATE "C"=p_bam
              AND b.operation COLLATE "C"='ocr.abbyy'
              AND b.trang_thai COLLATE "C"=(CASE WHEN p_trang_thai_cu COLLATE "C"='GIU' THEN 'DANG_XU_LY' ELSE 'CHUA_RO' END)
              AND (b.ket_qua->>'trang_thai') COLLATE "C"=p_trang_thai_cu
              AND b.ket_qua->'phien_ban'=to_jsonb(p_phien_ban)
            RETURNING b.ket_qua INTO kq;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'OCR_LUOT_XUNG_DOT' USING ERRCODE='40001';
        END IF;
        PERFORM set_config('ktt.ocr_phap_nhan_id',coalesce(pn_cu,''),true);
        RETURN kq;
    END;
    $chot$;
    EXECUTE format('ALTER FUNCTION loi_tai_lieu.ocr_chot_luot(uuid,text,uuid,bigint,text,text) OWNER TO %I',chu_tl);

    CREATE OR REPLACE FUNCTION loi_tai_lieu.ocr_doc_trang_thai(p_pn uuid,p_bam text) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $doc$
    DECLARE kq jsonb; pn_cu text := current_setting('ktt.ocr_phap_nhan_id',true);
    BEGIN
        IF session_user::text COLLATE "C" IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi_tai_lieu$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'OCR_LUOT_CHI_CORE' USING ERRCODE='42501';
        END IF;
        IF p_pn IS NULL OR p_bam IS NULL OR p_bam COLLATE "C" !~ '^[0-9a-f]{64}$' THEN
            RAISE EXCEPTION 'OCR_LUOT_DAU_VAO' USING ERRCODE='22023';
        END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        PERFORM set_config('ktt.ocr_phap_nhan_id',p_pn::text,true);
        SELECT b.ket_qua INTO kq FROM loi_tai_lieu.bien_nhan_core b
            WHERE b.phap_nhan_id=p_pn AND b.ma_bam COLLATE "C"=p_bam
              AND b.operation COLLATE "C"='ocr.abbyy'
            ORDER BY (b.trang_thai COLLATE "C" IN ('DANG_XU_LY','CHUA_RO')) DESC,b.tao_luc DESC,b.id DESC LIMIT 1;
        PERFORM set_config('ktt.ocr_phap_nhan_id',coalesce(pn_cu,''),true);
        RETURN kq;
    END;
    $doc$;
    EXECUTE format('ALTER FUNCTION loi_tai_lieu.ocr_doc_trang_thai(uuid,text) OWNER TO %I',chu_tl);

    -- ACL hội tụ khi chạy lại; helper chỉ owner tài liệu, ba cửa chỉ login Core.
    FOR ham IN SELECT * FROM (VALUES
        ('loi.ocr_viec(uuid,uuid)',chu_tl),
        ('loi_tai_lieu.ocr_giu_luot(uuid,text,uuid,text,integer,uuid)',login),
        ('loi_tai_lieu.ocr_chot_luot(uuid,text,uuid,bigint,text,text)',login),
        ('loi_tai_lieu.ocr_doc_trang_thai(uuid,text)',login)
    ) AS h(chu_ky,duoc_goi) LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ham.chu_ky);
        FOR quyen IN SELECT DISTINCT a.grantee FROM pg_proc p,LATERAL aclexplode(p.proacl) a
            WHERE p.oid=to_regprocedure(ham.chu_ky) AND a.grantee<>0 AND a.grantee<>p.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I',ham.chu_ky,pg_get_userbyid(quyen.grantee));
        END LOOP;
        EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ham.chu_ky,ham.duoc_goi);
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
