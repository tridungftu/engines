-- MASK-2 / CD-101: khối riêng, bí danh chung toàn tập đoàn, không mã hóa cột.
-- Không có phap_nhan_id: không chia danh mục theo pháp nhân (quyết định §3).
-- Không đăng ký loi.xuat_dang_ky_bang: bảng chứa định danh/cụm gốc, không
-- được cấp đọc cho vai_xuat_phap_nhan hoặc module. Không áp helper DEMO 023
-- vốn dành cho bảng có phap_nhan_id; thay bằng la_demo + FORCE RLS ở cả ba bảng,
-- FK (id,la_demo) chặn liên kết chéo DEMO/thật. Không cấp mặc định vùng vận hành.
-- 047: giữ guard chỉ Core DEMO/test PG16+, owner/ACL riêng; caller giữ transaction.
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt || 'vai_doi_cau_truc_mask';
    chay text := tt || 'vai_chay_mask';
    login text := tt || 'dang_nhap_loi';
    vai_cu text := current_setting('role');
    path_cu text := current_setting('search_path');
    vai text; loai text; bang text; ham text; b record; q record;
BEGIN
    IF (tt<>'' AND tt !~ '^[a-z][a-z0-9_]*_$')
        OR octet_length(tt || 'vai_doi_cau_truc_mask')>63
        OR (tt<>'' AND current_database() !~ '^kho_test_')
        OR current_database() !~ '^(kho_core_demo_g2_[a-z0-9_]+|kho_test_[a-z0-9_]+)$'
        OR current_setting('server_version_num')::integer<160000
        OR NOT (SELECT rolsuper FROM pg_roles WHERE rolname=current_user)
        OR vai_cu<>'none' THEN
        RAISE EXCEPTION 'MASK_CAN_LEAD_DEMO_PG16';
    END IF;
    -- ICU tường minh để hạ chữ Việt độc lập với LC_CTYPE, kể cả CSDL locale C.
    -- Kiểm tra tồn tại riêng trước khi PostgreSQL phân giải biểu thức COLLATE.
    IF to_regcollation('"und-x-icu"') IS NULL THEN
        RAISE EXCEPTION 'MASK_THIEU_COLLATION_UND_ICU'
            USING DETAIL='Không thể áp danh mục Mask: thiếu collation ICU und-x-icu.',
                HINT='Chuẩn bị collation ICU und-x-icu trong CSDL DEMO/test rồi chạy lại migration.';
    END IF;
    IF NOT (lower('Ô' COLLATE "und-x-icu")='ô'
            AND lower('Đ' COLLATE "und-x-icu")='đ') THEN
        RAISE EXCEPTION 'MASK_ICU_KHONG_HO_TRO_TIENG_VIET'
            USING DETAIL='Không thể áp danh mục Mask: collation ICU und-x-icu không hạ được chữ Ô và Đ.',
                HINT='Kiểm tra hỗ trợ Unicode của collation ICU und-x-icu rồi chạy lại migration.';
    END IF;
    IF NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='loi'
            AND pg_get_userbyid(nspowner)=tt||'vai_doi_cau_truc_loi')
        OR NOT EXISTS (SELECT FROM pg_roles WHERE rolname=login AND rolcanlogin
            AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole)
        OR to_regprocedure('loi.phap_nhan_cua_toi(text,integer,text,uuid)') IS NULL THEN
        RAISE EXCEPTION 'MASK_THIEU_NEN_047';
    END IF;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);
    FOREACH vai IN ARRAY ARRAY[chu,chay] LOOP
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=vai) THEN
            EXECUTE format('CREATE ROLE %I NOLOGIN INHERIT NOSUPERUSER NOBYPASSRLS NOCREATEROLE NOCREATEDB NOREPLICATION',vai);
        END IF;
        IF EXISTS (SELECT FROM pg_roles WHERE rolname=vai AND
            (rolcanlogin OR NOT rolinherit OR rolsuper OR rolbypassrls
                OR rolcreaterole OR rolcreatedb OR rolreplication))
            OR EXISTS (SELECT FROM pg_auth_members WHERE
                roleid=(SELECT oid FROM pg_roles WHERE rolname=vai)
                OR member=(SELECT oid FROM pg_roles WHERE rolname=vai)) THEN
            RAISE EXCEPTION 'MASK_SAI_VAI_HOAC_MEMBERSHIP';
        END IF;
    END LOOP;
    -- Không cấp vai_chay_mask cho login Core/module; chỉ DEFINER do Core gọi.
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS mask AUTHORIZATION %I',chu);
    IF NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='mask' AND pg_get_userbyid(nspowner)=chu)
        OR EXISTS (SELECT FROM pg_class WHERE relnamespace='mask'::regnamespace
            AND pg_get_userbyid(relowner)<>chu)
        OR EXISTS (SELECT FROM pg_proc WHERE pronamespace='mask'::regnamespace
            AND pg_get_userbyid(proowner)<>chu) THEN
        RAISE EXCEPTION 'MASK_SAI_OWNER';
    END IF;
    -- Thu hồi ACL trực tiếp lạ; membership bất thường của hai vai đã chặn ở trên.
    REVOKE ALL ON SCHEMA mask FROM PUBLIC;
    FOR q IN SELECT DISTINCT a.grantee FROM pg_namespace n,LATERAL aclexplode(n.nspacl) a
        WHERE n.nspname='mask' AND a.grantee<>0 AND a.grantee<>n.nspowner LOOP
        EXECUTE format('REVOKE ALL ON SCHEMA mask FROM %I',pg_get_userbyid(q.grantee));
    END LOOP;
    EXECUTE format('GRANT USAGE ON SCHEMA mask TO %I,%I',chay,login);
    FOREACH loai IN ARRAY ARRAY['TABLES','SEQUENCES','FUNCTIONS','TYPES'] LOOP
        EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE %I REVOKE ALL ON %s FROM PUBLIC',chu,loai);
        EXECUTE format('ALTER DEFAULT PRIVILEGES FOR ROLE %I IN SCHEMA mask REVOKE ALL ON %s FROM PUBLIC',chu,loai);
    END LOOP;
    EXECUTE format('SET LOCAL ROLE %I',chu);

    CREATE OR REPLACE FUNCTION mask.chuan_hoa(p_gia_tri text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE SET search_path=pg_catalog,pg_temp AS $ham$
        -- Cùng tập khoảng trắng tường minh với công cụ Python, gồm U+001C–001F.
        -- Không dùng [:space:] vì tập ký tự phụ thuộc locale của PostgreSQL.
        SELECT lower(btrim(regexp_replace(normalize(p_gia_tri,NFC),
            U&'[\0009-\000D\001C-\0020\0085\00A0\1680\2000-\200A\2028\2029\202F\205F\3000]+',' ','g')) COLLATE "und-x-icu")
    $ham$;

    CREATE OR REPLACE FUNCTION mask.tien_to(p_nhom text) RETURNS text
    LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE SET search_path=pg_catalog,pg_temp AS $ham$
        SELECT CASE p_nhom WHEN 'CONG_TY' THEN 'MASKCT' WHEN 'CA_NHAN' THEN 'MASKCN'
            WHEN 'DIA_CHI' THEN 'MASKDC' WHEN 'MA_SO_THUE' THEN 'MASKMST'
            WHEN 'TAI_KHOAN' THEN 'MASKTK'
            WHEN 'EMAIL' THEN 'MASKKHAC' WHEN 'DIEN_THOAI' THEN 'MASKKHAC'
            WHEN 'GIAY_TO' THEN 'MASKKHAC' WHEN 'HOP_DONG' THEN 'MASKKHAC'
            WHEN 'DU_AN' THEN 'MASKKHAC' WHEN 'KHAC' THEN 'MASKKHAC' END
    $ham$;

    CREATE SEQUENCE IF NOT EXISTS mask.so_bi_danh AS bigint MINVALUE 1 NO CYCLE;
    CREATE OR REPLACE FUNCTION mask.tao_bi_danh(p_nhom text,p_ma_junsky text DEFAULT NULL)
    RETURNS text LANGUAGE plpgsql VOLATILE SECURITY INVOKER
    SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE so text;
    BEGIN
        IF mask.tien_to(p_nhom) IS NULL THEN
            RAISE EXCEPTION 'MASK_NHOM' USING ERRCODE='23514';
        END IF;
        IF p_ma_junsky IS NOT NULL THEN
            IF p_ma_junsky !~ '^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$'
                OR upper(p_ma_junsky) LIKE 'MASK%' THEN
                RAISE EXCEPTION 'MASK_MA_JUNSKY' USING ERRCODE='23514';
            END IF;
            RETURN '[[' || p_ma_junsky || ']]';
        END IF;
        so := nextval('mask.so_bi_danh'::regclass)::text;
        -- lpad(...,4) cắt số >=10000: dùng độ dài lớn hơn, không cắt ngầm.
        RETURN '[[' || mask.tien_to(p_nhom) || '-' || lpad(so,greatest(4,length(so)),'0') || ']]';
    END;
    $ham$;

    CREATE TABLE IF NOT EXISTS mask.dinh_danh (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        gia_tri text NOT NULL CHECK (length(gia_tri) BETWEEN 2 AND 300
            AND mask.chuan_hoa(gia_tri)<>'' AND gia_tri !~ '[\[\]]'),
        gia_tri_chuan text GENERATED ALWAYS AS (mask.chuan_hoa(gia_tri)) STORED,
        nhom text NOT NULL CHECK (mask.tien_to(nhom) IS NOT NULL),
        ma_junsky text CHECK (ma_junsky ~ '^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$'
            AND upper(ma_junsky) NOT LIKE 'MASK%'),
        bi_danh text NOT NULL CHECK (length(bi_danh)<=128),
        bi_danh_tam text CHECK (bi_danh_tam ~ '^\[\[MASKTAM-[0-9a-f]{32}\]\]$'),
        nguon text NOT NULL CHECK (length(btrim(nguon)) BETWEEN 1 AND 100),
        la_demo boolean NOT NULL,
        tao_luc timestamptz NOT NULL DEFAULT statement_timestamp(),
        UNIQUE (id,la_demo), UNIQUE (la_demo,gia_tri_chuan),
        CHECK ((ma_junsky IS NOT NULL AND bi_danh='[['||ma_junsky||']]')
            OR (ma_junsky IS NULL AND bi_danh ~ ('^\[\['||mask.tien_to(nhom)||'-[0-9]{4,}\]\]$')
                AND bi_danh !~ '-0+\]\]$'))
    );
    CREATE UNIQUE INDEX IF NOT EXISTS dinh_danh_bi_danh ON mask.dinh_danh(la_demo,lower(bi_danh COLLATE "und-x-icu"));
    CREATE UNIQUE INDEX IF NOT EXISTS dinh_danh_bi_danh_tam ON mask.dinh_danh(la_demo,lower(bi_danh_tam COLLATE "und-x-icu"));

    CREATE TABLE IF NOT EXISTS mask.yeu_cau (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        module text NOT NULL CHECK (module ~ '^[a-z][a-z0-9_]{0,49}$'),
        nguoi_gui uuid NOT NULL, tai_lieu_id uuid NOT NULL,
        la_demo boolean NOT NULL,
        trang_thai text NOT NULL DEFAULT 'DANG_XU_LY' CHECK (trang_thai IN ('DANG_XU_LY','DA_DONG')),
        -- Giữ tham chiếu bí danh tạm cho lát 4; không dùng để hạn chế bảng tra.
        bi_danh_tam_da_dung text[] NOT NULL DEFAULT ARRAY[]::text[],
        tao_luc timestamptz NOT NULL DEFAULT statement_timestamp(),
        dong_luc timestamptz,
        UNIQUE (id,la_demo),
        CHECK ((trang_thai='DANG_XU_LY' AND dong_luc IS NULL)
            OR (trang_thai='DA_DONG' AND dong_luc IS NOT NULL AND dong_luc>=tao_luc))
    );
    CREATE TABLE IF NOT EXISTS mask.cho_duyet (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        cum_goc text NOT NULL CHECK (length(cum_goc) BETWEEN 2 AND 300 AND mask.chuan_hoa(cum_goc)<>''),
        cum_chuan text GENERATED ALWAYS AS (mask.chuan_hoa(cum_goc)) STORED,
        nhom text NOT NULL CHECK (mask.tien_to(nhom) IS NOT NULL),
        bi_danh_tam text NOT NULL DEFAULT ('[[MASKTAM-'||replace(gen_random_uuid()::text,'-','')||']]')
            CHECK (bi_danh_tam ~ '^\[\[MASKTAM-[0-9a-f]{32}\]\]$'),
        yeu_cau_id uuid NOT NULL, la_demo boolean NOT NULL,
        nguon text NOT NULL CHECK (length(btrim(nguon)) BETWEEN 1 AND 100),
        tao_luc timestamptz NOT NULL DEFAULT statement_timestamp(),
        UNIQUE (la_demo,cum_chuan), UNIQUE (la_demo,bi_danh_tam),
        FOREIGN KEY (yeu_cau_id,la_demo) REFERENCES mask.yeu_cau(id,la_demo)
    );

    CREATE OR REPLACE FUNCTION mask.gan_bi_danh() RETURNS trigger
    LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $ham$
    BEGIN
        IF NEW.bi_danh IS NULL THEN
            NEW.bi_danh := mask.tao_bi_danh(NEW.nhom,NEW.ma_junsky);
        END IF;
        RETURN NEW;
    END;
    $ham$;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid='mask.dinh_danh'::regclass
        AND tgname='gan_bi_danh') THEN
        CREATE TRIGGER gan_bi_danh BEFORE INSERT ON mask.dinh_danh
            FOR EACH ROW EXECUTE FUNCTION mask.gan_bi_danh();
    END IF;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid='mask.dinh_danh'::regclass
        AND tgname='gan_bi_danh' AND tgtype=7 AND tgenabled='O' AND tgqual IS NULL
        AND tgnargs=0 AND tgfoid='mask.gan_bi_danh()'::regprocedure) THEN
        RAISE EXCEPTION 'MASK_SAI_TRIGGER';
    END IF;

    -- Core phải truyền module/người gửi/tài liệu đã xác minh, không lấy tự khai
    -- từ module. Cửa này chỉ cấp mã; xác minh mở che thuộc lát 3.
    CREATE OR REPLACE FUNCTION mask.cap_ma_yeu_cau(p_module text,p_nguoi_gui uuid,
        p_tai_lieu uuid,p_la_demo boolean) RETURNS uuid
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ma uuid; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        IF session_user::text IS DISTINCT FROM regexp_replace(current_user::text,
                'vai_doi_cau_truc_mask$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'MASK_CHI_CORE' USING ERRCODE='42501';
        END IF;
        IF p_module IS NULL OR p_module !~ '^[a-z][a-z0-9_]{0,49}$'
            OR p_nguoi_gui IS NULL OR p_tai_lieu IS NULL OR p_la_demo IS NULL THEN
            RAISE EXCEPTION 'MASK_YEU_CAU' USING ERRCODE='22023';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',p_la_demo::text,true);
        INSERT INTO mask.yeu_cau(module,nguoi_gui,tai_lieu_id,la_demo)
            VALUES(p_module,p_nguoi_gui,p_tai_lieu,p_la_demo) RETURNING id INTO ma;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN ma;
    END;
    $ham$;

    FOREACH bang IN ARRAY ARRAY['dinh_danh','yeu_cau','cho_duyet'] LOOP
        EXECUTE format('ALTER TABLE mask.%I ENABLE ROW LEVEL SECURITY',bang);
        EXECUTE format('ALTER TABLE mask.%I FORCE ROW LEVEL SECURITY',bang);
        IF NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('mask.'||bang)
            AND polname='vung_demo') THEN
            EXECUTE format('CREATE POLICY vung_demo ON mask.%I TO %I,%I
                USING (la_demo::text=current_setting(''ktt.mask_la_demo'',true))
                WITH CHECK (la_demo::text=current_setting(''ktt.mask_la_demo'',true))',bang,chu,chay);
        ELSE
            EXECUTE format('ALTER POLICY vung_demo ON mask.%I TO %I,%I
                USING (la_demo::text=current_setting(''ktt.mask_la_demo'',true))
                WITH CHECK (la_demo::text=current_setting(''ktt.mask_la_demo'',true))',bang,chu,chay);
        END IF;
        -- Không để policy phụ mở rộng vùng đọc đã định.
        IF EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('mask.'||bang)
            AND polname<>'vung_demo') THEN
            RAISE EXCEPTION 'MASK_POLICY_NGOAI_PHAM_VI';
        END IF;
    END LOOP;
    -- ACL chỉ owner/engine; không cấp SELECT cho vai_chay_loi hoặc login Core.
    FOR b IN SELECT c.oid,c.relkind,c.relname,c.relowner,c.relacl FROM pg_class c
        WHERE c.relnamespace='mask'::regnamespace
            AND ((c.relkind='r' AND c.relname IN ('dinh_danh','yeu_cau','cho_duyet'))
                OR (c.relkind='S' AND c.relname='so_bi_danh')) LOOP
        loai := CASE WHEN b.relkind='S' THEN 'SEQUENCE' ELSE 'TABLE' END;
        EXECUTE format('REVOKE ALL ON %s mask.%I FROM PUBLIC',loai,b.relname);
        FOR q IN SELECT DISTINCT a.grantee FROM aclexplode(b.relacl) a
            WHERE a.grantee<>0 AND a.grantee<>b.relowner LOOP
            EXECUTE format('REVOKE ALL ON %s mask.%I FROM %I',loai,b.relname,pg_get_userbyid(q.grantee));
        END LOOP;
        -- Thu hồi cả column ACL; REVOKE TABLE không thu hồi grant từng cột.
        IF b.relkind='r' THEN
            FOR q IN SELECT DISTINCT a.attname,x.grantee FROM pg_attribute a,
                LATERAL aclexplode(a.attacl) x WHERE a.attrelid=b.oid
                AND x.grantee<>b.relowner LOOP
                EXECUTE format('REVOKE ALL (%I) ON TABLE mask.%I FROM %s',q.attname,b.relname,
                    CASE WHEN q.grantee=0 THEN 'PUBLIC' ELSE quote_ident(pg_get_userbyid(q.grantee)) END);
            END LOOP;
            EXECUTE format('GRANT SELECT,INSERT,UPDATE,DELETE ON mask.%I TO %I',b.relname,chay);
        ELSE
            EXECUTE format('GRANT USAGE,SELECT ON SEQUENCE mask.%I TO %I',b.relname,chay);
        END IF;
    END LOOP;
    FOR b IN SELECT p.oid,p.proowner,p.proacl FROM pg_proc p
        WHERE p.oid IN ('mask.chuan_hoa(text)'::regprocedure,'mask.tien_to(text)'::regprocedure,
            'mask.tao_bi_danh(text,text)'::regprocedure,'mask.gan_bi_danh()'::regprocedure,
            'mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)'::regprocedure) LOOP
        ham := b.oid::regprocedure::text;
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ham);
        FOR q IN SELECT DISTINCT a.grantee FROM aclexplode(b.proacl) a
            WHERE a.grantee<>0 AND a.grantee<>b.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I',ham,pg_get_userbyid(q.grantee));
        END LOOP;
        IF b.oid='mask.cap_ma_yeu_cau(text,uuid,uuid,boolean)'::regprocedure THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ham,login);
        ELSE
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ham,chay);
        END IF;
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
