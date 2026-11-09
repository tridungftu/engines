-- MASK-3D: snapshot có phiên bản, nhật ký RAM, chốt nguyên tử và chống phát lại.
-- Phiên bản từng ánh xạ: chỉ so các khóa RAM đã tra và yêu cầu hiện hành,
-- không so bộ đếm gặp/cụm của tài liệu khác chưa dùng. Chỉ dùng trong Core.
-- Khóa ngắn theo thứ tự yeu_cau → cho_duyet → dinh_danh, không giữ lúc xử lý.
-- Khóa EXCLUSIVE tương thích SELECT, chặn cả SELECT FOR UPDATE của cửa duyệt;
-- không nâng từ khóa hàng danh mục, không đảo thứ tự cửa dọn 117.
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
        RAISE EXCEPTION 'MASK_LUOT_SAI_DICH';
    END IF;
    FOREACH ck IN ARRAY ARRAY[chu,chu_tl,chu_mask,chay_mask] LOOP
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=ck AND NOT rolcanlogin
            AND rolinherit AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole
            AND NOT rolcreatedb AND NOT rolreplication) THEN
            RAISE EXCEPTION 'MASK_LUOT_SAI_VAI';
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
       OR to_regprocedure('loi.mask_ngu_canh(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi.mask_kiem_toan_doc(text,text,uuid,text,uuid,bigint,uuid,text)') IS NULL
       OR to_regprocedure('loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)') IS NULL
       OR to_regprocedure('mask.cap_ma_yeu_cau(text,text,uuid,text,uuid,uuid,bigint)') IS NULL
       OR to_regprocedure('mask.chuan_hoa(text)') IS NULL
       OR to_regprocedure('mask.tien_to(text)') IS NULL
       OR to_regprocedure('loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.ngu_canh(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.kiem_quyen(text,text,uuid,text,jsonb,text,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.duoc_xem_noi_dung(uuid,uuid,text)') IS NULL
       OR to_regcollation('"und-x-icu"') IS NULL THEN
        RAISE EXCEPTION 'MASK_LUOT_THIEU_NEN_119';
    END IF;
    FOREACH ck IN ARRAY ARRAY[
        'mask.kiem_yeu_cau(text,text,uuid,text,uuid,bigint,uuid)',
        'mask.liet_ke_dinh_danh(text,text,uuid,text,uuid,bigint,uuid)',
        'mask.tra_bi_danh(text,text,uuid,text,uuid,bigint,uuid,text)',
        'mask.ghi_cho_duyet(text,text,uuid,text,uuid,bigint,uuid,text,text,text,boolean)',
        'mask.doc_yeu_cau(text,text,uuid,text,uuid,bigint,uuid)',
        'mask.ghi_bi_danh_da_dung(text,text,uuid,text,uuid,bigint,uuid,text[])',
        'mask.tra_dinh_danh(text,text,uuid,text,uuid,bigint,uuid,text)',
        'mask.dong_yeu_cau(text,text,uuid,text,uuid,bigint,uuid)'] LOOP
        IF to_regprocedure(ck) IS NULL THEN
            RAISE EXCEPTION 'MASK_LUOT_THIEU_NEN_119';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['phien_xac_thuc','phap_nhan','nguoi_dung','phan_quyen'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu
            AND relrowsecurity AND relforcerowsecurity) THEN
            RAISE EXCEPTION 'MASK_LUOT_THIEU_NEN_119';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['tai_lieu','quyen_tai_lieu'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi_tai_lieu.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu_tl
            AND relrowsecurity AND relforcerowsecurity)
           OR NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('loi_tai_lieu.'||bang)
                AND polname='tai_lieu_phien') THEN
            RAISE EXCEPTION 'MASK_LUOT_THIEU_NEN_119';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['dinh_danh','cho_duyet','yeu_cau','luot_chot'] LOOP
        IF bang='luot_chot' AND to_regclass('mask.luot_chot') IS NULL THEN
            CONTINUE;
        END IF;
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('mask.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu_mask
            AND relrowsecurity AND relforcerowsecurity)
           OR NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('mask.'||bang)
                AND polname='vung_demo')
           OR EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('mask.'||bang)
                AND polname<>'vung_demo') THEN
            RAISE EXCEPTION 'MASK_LUOT_SAI_BANG_HOAC_RLS';
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT FROM pg_attribute WHERE attrelid='mask.cho_duyet'::regclass
        AND attname='so_lan_gap' AND atttypid='bigint'::regtype AND attnotnull AND NOT attisdropped)
       OR NOT EXISTS (SELECT FROM pg_attribute WHERE attrelid='mask.yeu_cau'::regclass
        AND attname='cum_da_gap' AND atttypid='text[]'::regtype AND attnotnull AND NOT attisdropped) THEN
        RAISE EXCEPTION 'MASK_LUOT_SAI_COT';
    END IF;
    FOR b IN SELECT p.* FROM pg_proc p WHERE p.oid IN (
        to_regprocedure('loi.mask_ngu_canh(text,text,uuid,text,uuid,bigint)'),
        to_regprocedure('loi.mask_kiem_toan_doc(text,text,uuid,text,uuid,bigint,uuid,text)'),
        to_regprocedure('loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)'))
        OR (p.pronamespace='mask'::regnamespace AND p.proname IN
            ('cap_ma_yeu_cau','chuan_hoa','tien_to','kiem_yeu_cau','liet_ke_dinh_danh',
             'tra_bi_danh','ghi_cho_duyet','doc_yeu_cau','ghi_bi_danh_da_dung',
             'tra_dinh_danh','dong_yeu_cau','giu_phien_anh_xa','phien_ban_luot','snapshot_luot','chot_luot')) LOOP
        IF pg_get_userbyid(b.proowner)<>(CASE WHEN b.pronamespace='loi'::regnamespace THEN chu
            WHEN b.pronamespace='loi_tai_lieu'::regnamespace THEN chu_tl ELSE chu_mask END) THEN
            RAISE EXCEPTION 'MASK_LUOT_SAI_OWNER';
        END IF;
    END LOOP;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);
    EXECUTE format('SET LOCAL ROLE %I',chu_mask);

    -- Kết quả nội bộ có thể chứa bản mở che: RLS bắt buộc, không cấp đọc bảng.
    CREATE TABLE IF NOT EXISTS mask.luot_chot (
        yeu_cau_id uuid NOT NULL,
        ma_luot uuid NOT NULL,
        loai text NOT NULL CHECK (loai IN ('che','mo_che')),
        ket_qua jsonb NOT NULL CHECK (jsonb_typeof(ket_qua)='object'),
        la_demo boolean NOT NULL,
        tao_luc timestamptz NOT NULL DEFAULT statement_timestamp(),
        PRIMARY KEY (yeu_cau_id,ma_luot),
        FOREIGN KEY (yeu_cau_id,la_demo) REFERENCES mask.yeu_cau(id,la_demo)
    );
    ALTER TABLE mask.luot_chot ENABLE ROW LEVEL SECURITY;
    ALTER TABLE mask.luot_chot FORCE ROW LEVEL SECURITY;
    IF NOT EXISTS (SELECT FROM pg_policy WHERE polrelid='mask.luot_chot'::regclass
        AND polname='vung_demo') THEN
        EXECUTE format('CREATE POLICY vung_demo ON mask.luot_chot TO %I
            USING (la_demo::text=current_setting(''ktt.mask_la_demo'',true))
            WITH CHECK (la_demo::text=current_setting(''ktt.mask_la_demo'',true))',chu_mask);
    END IF;

    -- xmin của hàng chờ đổi cả khi chỉ tăng đếm. Giữ phiên bản riêng cho
    -- ánh xạ để không gây xung đột giả; không băm giá trị gốc làm phiên bản.
    ALTER TABLE mask.cho_duyet ADD COLUMN IF NOT EXISTS phien_ban_anh_xa bigint NOT NULL DEFAULT 1
        CHECK (phien_ban_anh_xa>0);
    IF NOT EXISTS (SELECT FROM pg_attribute a JOIN pg_attrdef ad
        ON ad.adrelid=a.attrelid AND ad.adnum=a.attnum
        WHERE a.attrelid='mask.cho_duyet'::regclass AND a.attname='phien_ban_anh_xa'
            AND a.atttypid='bigint'::regtype AND a.attnotnull AND NOT a.attisdropped
            AND a.attgenerated='' AND pg_get_expr(ad.adbin,ad.adrelid)='1') THEN
        RAISE EXCEPTION 'MASK_LUOT_SAI_COT';
    END IF;
    CREATE OR REPLACE FUNCTION mask.giu_phien_anh_xa() RETURNS trigger
    LANGUAGE plpgsql SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $ham$
    BEGIN
        IF ROW(NEW.id,NEW.cum_goc,NEW.nhom,NEW.bi_danh_tam,NEW.la_demo) IS DISTINCT FROM
            ROW(OLD.id,OLD.cum_goc,OLD.nhom,OLD.bi_danh_tam,OLD.la_demo) THEN
            NEW.phien_ban_anh_xa := OLD.phien_ban_anh_xa+1;
        ELSE
            NEW.phien_ban_anh_xa := OLD.phien_ban_anh_xa;
        END IF;
        RETURN NEW;
    END;
    $ham$;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid='mask.cho_duyet'::regclass
        AND tgname='giu_phien_anh_xa') THEN
        EXECUTE format('CREATE TRIGGER giu_phien_anh_xa BEFORE UPDATE ON mask.cho_duyet
            FOR EACH ROW EXECUTE FUNCTION mask.giu_phien_anh_xa()');
    END IF;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid='mask.cho_duyet'::regclass
        AND tgname='giu_phien_anh_xa' AND tgtype=19 AND tgenabled='O' AND tgqual IS NULL
        AND tgattr=''::int2vector
        AND tgnargs=0 AND tgfoid='mask.giu_phien_anh_xa()'::regprocedure) THEN
        RAISE EXCEPTION 'MASK_LUOT_SAI_TRIGGER';
    END IF;

    -- Helper INVOKER chỉ owner gọi, sau xác minh và đặt rào DEMO.
    -- Phiên bản từ định danh + phiên bản hàng, không từ giá trị nhạy cảm.
    -- Cửa chốt tự tính lại từ CSDL rồi chỉ so các khóa lượt thực sự đã tra.
    CREATE OR REPLACE FUNCTION mask.phien_ban_luot(p_yeu_cau uuid) RETURNS text
    LANGUAGE plpgsql VOLATILE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE kq text;
    BEGIN
        WITH anh_xa AS (
            SELECT d.gia_tri_chuan AS cum,
                encode(sha256(convert_to('d:'||d.id::text||':'||d.xmin::text,'UTF8')),'hex') AS phien
                FROM mask.dinh_danh d
            UNION ALL
            SELECT c.cum_chuan,
                encode(sha256(convert_to('c:'||c.id::text||':'||c.phien_ban_anh_xa::text,'UTF8')),'hex')
                FROM mask.cho_duyet c WHERE NOT EXISTS
                    (SELECT FROM mask.dinh_danh d WHERE d.gia_tri_chuan=c.cum_chuan)
        ), phien_cum AS (
            SELECT encode(sha256(convert_to(ax.cum,'UTF8')),'hex') AS khoa,
                ax.phien FROM anh_xa ax
        ), phien_bd AS (
            -- Khác miền với phien_cum, tránh nối khóa cụm với bí danh bằng
            -- cùng mã phiên bản khi chưa biết định danh/phiên bản hàng.
            SELECT lower(bd.ma COLLATE "und-x-icu") AS khoa,
                encode(sha256(convert_to('bd:d:'||d.id::text||':'||d.xmin::text,'UTF8')),'hex') AS phien
                FROM mask.dinh_danh d CROSS JOIN LATERAL
                    (VALUES(d.bi_danh),(d.bi_danh_tam)) bd(ma) WHERE bd.ma IS NOT NULL
            UNION ALL
            SELECT lower(c.bi_danh_tam COLLATE "und-x-icu"),
                encode(sha256(convert_to('bd:c:'||c.id::text||':'||c.phien_ban_anh_xa::text,'UTF8')),'hex')
                FROM mask.cho_duyet c WHERE NOT EXISTS (SELECT FROM mask.dinh_danh d
                    WHERE lower(d.bi_danh COLLATE "und-x-icu")=lower(c.bi_danh_tam COLLATE "und-x-icu")
                        OR lower(d.bi_danh_tam COLLATE "und-x-icu")=lower(c.bi_danh_tam COLLATE "und-x-icu"))
        )
        SELECT jsonb_build_object(
            'cum',(SELECT coalesce(jsonb_object_agg(pc.khoa,pc.phien),'{}'::jsonb) FROM phien_cum pc),
            'bi_danh',(SELECT coalesce(jsonb_object_agg(pb.khoa,pb.phien),'{}'::jsonb) FROM phien_bd pb),
            'yeu_cau',(SELECT encode(sha256(convert_to(to_jsonb(y)::text,'UTF8')),'hex')
                FROM mask.yeu_cau y WHERE y.id=p_yeu_cau)
        )::text INTO kq;
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.snapshot_luot(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_tai_lieu uuid,p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_luot uuid,p_loai text)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp
    SET lock_timeout='1s' AS $ham$
    DECLARE ctx record; yc mask.yeu_cau; cu_luot mask.luot_chot;
        danh_muc jsonb; phien text; co_san boolean; kq jsonb; tt_yc jsonb; bo_sung jsonb; cum_cho jsonb;
        cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_ngu_canh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        PERFORM loi_tai_lieu.mask_kiem_tai_lieu(p_ma,p_module,ctx.phap_nhan_id,p_hd,
            p_tai_lieu,p_viec,p_the_he);
        IF p_yeu_cau IS NULL OR p_luot IS NULL OR p_loai IS NULL OR p_loai NOT IN ('che','mo_che') THEN
            RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
        END IF;
        IF current_setting('transaction_isolation')<>'read committed' THEN
            RAISE EXCEPTION 'MASK_CAN_READ_COMMITTED' USING ERRCODE='25000';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        LOCK TABLE mask.yeu_cau,mask.cho_duyet,mask.dinh_danh IN EXCLUSIVE MODE;
        SELECT y.* INTO yc FROM mask.yeu_cau y WHERE y.id=p_yeu_cau;
        co_san := FOUND;
        IF (co_san AND (yc.module<>p_module OR yc.nguoi_gui<>ctx.nguoi_gui
            OR yc.tai_lieu_id<>p_tai_lieu OR yc.la_demo<>ctx.la_demo))
            OR (NOT co_san AND p_loai='mo_che') THEN
            RAISE EXCEPTION 'MASK_YEU_CAU' USING ERRCODE='42501';
        END IF;
        SELECT l.* INTO cu_luot FROM mask.luot_chot l
            WHERE l.yeu_cau_id=p_yeu_cau AND l.ma_luot=p_luot;
        IF FOUND THEN
            IF cu_luot.loai<>p_loai THEN
                RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
            END IF;
            kq := jsonb_build_object('da_chot',true);
        ELSE
            IF co_san AND yc.trang_thai<>'DANG_XU_LY' THEN
                RAISE EXCEPTION 'MASK_YEU_CAU' USING ERRCODE='42501';
            END IF;
            phien := mask.phien_ban_luot(p_yeu_cau);
            IF co_san THEN
                tt_yc := jsonb_build_object('trang_thai',yc.trang_thai);
            END IF;
            -- 119 cần yêu cầu đã xác minh. Dựng hàng chỉ trong savepoint
            -- rồi rollback riêng savepoint bằng SQLSTATE dành riêng; biến
            -- PL/pgSQL giữ snapshot, CSDL không giữ mã yêu cầu/thay đổi nào.
            BEGIN
                IF NOT co_san THEN
                    INSERT INTO mask.yeu_cau(id,module,nguoi_gui,tai_lieu_id,la_demo)
                        VALUES(p_yeu_cau,p_module,ctx.nguoi_gui,p_tai_lieu,ctx.la_demo);
                END IF;
                danh_muc := mask.liet_ke_dinh_danh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
                IF NOT co_san THEN
                    RAISE EXCEPTION 'MASK_SNAPSHOT_TAM' USING ERRCODE='P1200';
                END IF;
            EXCEPTION WHEN SQLSTATE 'P1200' THEN
                NULL;
            END;
            -- LIET_KE của yêu cầu tạm bị rollback: ghi lại ngoài savepoint,
            -- chỉ mã yêu cầu/thao tác, không có giá trị định danh.
            IF NOT co_san THEN
                PERFORM loi.mask_kiem_toan_doc(p_ma,p_module,p_pn,p_hd,
                    p_viec,p_the_he,p_yeu_cau,'LIET_KE');
            END IF;
            -- Dùng lại bí danh của cụm chờ ở bất kỳ tài liệu/người gửi cùng
            -- vùng. Bước che chỉ nhận hash → nhóm/bí danh, không nhận cụm gốc.
            -- Core giữ khóa ở RAM, không truyền qua SQL/GUC: riêng khóa cụm
            -- còn SHA-256 trần, lộ phép dò cụm ngang oracle tra_bi_danh 119.
            SELECT coalesce(jsonb_object_agg(encode(sha256(convert_to(c.cum_chuan,'UTF8')),'hex'),
                jsonb_build_object('nhom',c.nhom,'bi_danh',c.bi_danh_tam,'nguon','tam')),
                '{}'::jsonb) INTO cum_cho FROM mask.cho_duyet c;
            bo_sung := '{}'::jsonb;
            IF p_loai='mo_che' THEN
                -- Tra toàn vùng đúng cửa 119; snapshot chưa ghi TRA cho các
                -- cụm chưa mở. Chỉ nhật ký tra thực tế mới ghi TRA khi chốt.
                SELECT coalesce(jsonb_object_agg(lower(c.bi_danh_tam COLLATE "und-x-icu"),
                    coalesce((SELECT d.gia_tri FROM mask.dinh_danh d
                        WHERE lower(d.bi_danh COLLATE "und-x-icu")=lower(c.bi_danh_tam COLLATE "und-x-icu")
                            OR lower(d.bi_danh_tam COLLATE "und-x-icu")=lower(c.bi_danh_tam COLLATE "und-x-icu")),
                        c.cum_goc)),'{}'::jsonb) INTO bo_sung FROM mask.cho_duyet c;
            END IF;
            kq := jsonb_build_object('da_chot',false,'phien_ban',phien,'danh_muc',danh_muc,
                'yeu_cau',tt_yc,'bi_danh_bo_sung',bo_sung,'cum_cho_toan_vung',cum_cho);
        END IF;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.chot_luot(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_tai_lieu uuid,p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_luot uuid,p_loai text,
        p_phien_ban text,p_nhat_ky jsonb,p_ket_qua jsonb)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp
    SET lock_timeout='1s' AS $ham$
    DECLARE ctx record; yc mask.yeu_cau; cu_luot mask.luot_chot; co_san boolean;
        muc jsonb; da_ghi jsonb; cac_tam text[]; kq jsonb; phien_cu jsonb; phien_moi jsonb; khoa text;
        cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_ngu_canh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        PERFORM loi_tai_lieu.mask_kiem_tai_lieu(p_ma,p_module,ctx.phap_nhan_id,p_hd,
            p_tai_lieu,p_viec,p_the_he);
        IF p_yeu_cau IS NULL OR p_luot IS NULL OR p_loai IS NULL OR p_loai NOT IN ('che','mo_che') THEN
            RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
        END IF;
        IF current_setting('transaction_isolation')<>'read committed' THEN
            RAISE EXCEPTION 'MASK_CAN_READ_COMMITTED' USING ERRCODE='25000';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        LOCK TABLE mask.yeu_cau,mask.cho_duyet,mask.dinh_danh IN EXCLUSIVE MODE;
        SELECT y.* INTO yc FROM mask.yeu_cau y WHERE y.id=p_yeu_cau;
        co_san := FOUND;
        IF (co_san AND (yc.module<>p_module OR yc.nguoi_gui<>ctx.nguoi_gui
            OR yc.tai_lieu_id<>p_tai_lieu OR yc.la_demo<>ctx.la_demo))
            OR (NOT co_san AND p_loai='mo_che') THEN
            RAISE EXCEPTION 'MASK_YEU_CAU' USING ERRCODE='42501';
        END IF;
        -- Phát lại kiểm quyền trước; cho phép chính lượt đã đóng yêu cầu.
        -- Không so phiên bản mới và không áp lại nhật ký của lần phát lại.
        SELECT l.* INTO cu_luot FROM mask.luot_chot l
            WHERE l.yeu_cau_id=p_yeu_cau AND l.ma_luot=p_luot;
        IF FOUND THEN
            IF cu_luot.loai<>p_loai THEN
                RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
            END IF;
            kq := cu_luot.ket_qua;
        ELSE
            IF co_san AND yc.trang_thai<>'DANG_XU_LY' THEN
                RAISE EXCEPTION 'MASK_YEU_CAU' USING ERRCODE='42501';
            END IF;
            IF jsonb_typeof(p_nhat_ky) IS DISTINCT FROM 'object'
                OR jsonb_typeof(p_nhat_ky->'cum') IS DISTINCT FROM 'array'
                OR jsonb_typeof(p_nhat_ky->'bi_danh_tam_moi') IS DISTINCT FROM 'array'
                OR jsonb_typeof(p_nhat_ky->'bi_danh_da_dung') IS DISTINCT FROM 'array'
                OR jsonb_typeof(p_nhat_ky->'cum_da_tra') IS DISTINCT FROM 'array'
                OR jsonb_typeof(p_nhat_ky->'bi_danh_da_tra') IS DISTINCT FROM 'array'
                OR jsonb_typeof(p_nhat_ky->'dong_yeu_cau') IS DISTINCT FROM 'boolean'
                OR jsonb_typeof(p_ket_qua) IS DISTINCT FROM 'object'
                OR p_ket_qua->>'ma_yeu_cau' IS DISTINCT FROM p_yeu_cau::text
                OR p_ket_qua->>'ma_luot' IS DISTINCT FROM p_luot::text THEN
                RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
            END IF;
            phien_cu := p_phien_ban::jsonb;
            phien_moi := mask.phien_ban_luot(p_yeu_cau)::jsonb;
            IF jsonb_typeof(phien_cu) IS DISTINCT FROM 'object' THEN
                RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
            END IF;
            IF phien_cu->'yeu_cau' IS DISTINCT FROM phien_moi->'yeu_cau' THEN
                RAISE EXCEPTION 'MASK_XUNG_DOT_LUOT' USING ERRCODE='40001';
            END IF;
            -- Kể cả tra hụt: hàng mới xuất hiện cho chính cụm đó phải retry.
            -- Thêm khóa từ nhật ký ghi/tham chiếu để không bỏ sót cửa cũ.
            FOR khoa IN SELECT a.value FROM jsonb_array_elements_text(p_nhat_ky->'cum_da_tra') a
                UNION SELECT encode(sha256(convert_to(mask.chuan_hoa(e.value->>'gia_tri'),'UTF8')),'hex')
                    FROM jsonb_array_elements(p_nhat_ky->'cum') e LOOP
                IF phien_cu->'cum'->khoa IS DISTINCT FROM phien_moi->'cum'->khoa THEN
                    RAISE EXCEPTION 'MASK_XUNG_DOT_LUOT' USING ERRCODE='40001';
                END IF;
            END LOOP;
            FOR khoa IN SELECT lower(a.value COLLATE "und-x-icu") FROM jsonb_array_elements_text(
                (p_nhat_ky->'bi_danh_da_tra')||(p_nhat_ky->'bi_danh_da_dung')) a LOOP
                IF phien_cu->'bi_danh'->khoa IS DISTINCT FROM phien_moi->'bi_danh'->khoa THEN
                    RAISE EXCEPTION 'MASK_XUNG_DOT_LUOT' USING ERRCODE='40001';
                END IF;
            END LOOP;
            IF p_loai='che' AND p_ket_qua->>'gui_duoc'='false'
                AND NOT (p_nhat_ky->>'dong_yeu_cau')::boolean THEN
                RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
            END IF;
            cac_tam := ARRAY(SELECT a.value FROM jsonb_array_elements_text(p_nhat_ky->'bi_danh_tam_moi') a);
            IF EXISTS (SELECT FROM unnest(cac_tam) t(bd)
                WHERE t.bd IS NULL OR t.bd !~ '^\[\[MASKTAM-[0-9a-f]{32}\]\]$') THEN
                RAISE EXCEPTION 'MASK_BI_DANH' USING ERRCODE='22023';
            END IF;
            IF NOT co_san THEN
                INSERT INTO mask.yeu_cau(id,module,nguoi_gui,tai_lieu_id,la_demo)
                    VALUES(p_yeu_cau,p_module,ctx.nguoi_gui,p_tai_lieu,ctx.la_demo);
            END IF;
            FOR muc IN SELECT e.value FROM jsonb_array_elements(p_nhat_ky->'cum') e LOOP
                IF jsonb_typeof(muc) IS DISTINCT FROM 'object'
                    OR jsonb_typeof(muc->'chi_gap_lai') IS DISTINCT FROM 'boolean'
                    OR jsonb_typeof(muc->'gia_tri') IS DISTINCT FROM 'string'
                    OR jsonb_typeof(muc->'nhom') IS DISTINCT FROM 'string'
                    OR jsonb_typeof(muc->'bi_danh') IS DISTINCT FROM 'string' THEN
                    RAISE EXCEPTION 'MASK_LUOT_DAU_VAO' USING ERRCODE='22023';
                END IF;
                IF NOT (muc->>'chi_gap_lai')::boolean
                    AND NOT (muc->>'bi_danh'=ANY(cac_tam)) THEN
                    RAISE EXCEPTION 'MASK_BI_DANH' USING ERRCODE='22023';
                END IF;
                da_ghi := mask.ghi_cho_duyet(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau,
                    muc->>'gia_tri',muc->>'nhom',muc->>'bi_danh',(muc->>'chi_gap_lai')::boolean);
                -- Không bao giờ công bố bí danh do RAM chọn mà CSDL không nhận.
                IF lower((da_ghi->>'bi_danh') COLLATE "und-x-icu")
                    IS DISTINCT FROM lower((muc->>'bi_danh') COLLATE "und-x-icu") THEN
                    RAISE EXCEPTION 'MASK_XUNG_DOT_LUOT' USING ERRCODE='40001';
                END IF;
            END LOOP;
            PERFORM mask.ghi_bi_danh_da_dung(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau,
                ARRAY(SELECT a.value FROM jsonb_array_elements_text(p_nhat_ky->'bi_danh_da_dung') a));
            FOR khoa IN SELECT DISTINCT a.value FROM jsonb_array_elements_text(p_nhat_ky->'bi_danh_da_tra') a LOOP
                PERFORM loi.mask_kiem_toan_doc(p_ma,p_module,p_pn,p_hd,
                    p_viec,p_the_he,p_yeu_cau,'TRA');
            END LOOP;
            IF (p_nhat_ky->>'dong_yeu_cau')::boolean THEN
                PERFORM mask.dong_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
            END IF;
            INSERT INTO mask.luot_chot(yeu_cau_id,ma_luot,loai,ket_qua,la_demo)
                VALUES(p_yeu_cau,p_luot,p_loai,p_ket_qua,ctx.la_demo);
            kq := p_ket_qua;
        END IF;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    PERFORM set_config('role',vai_cu,true);
    REVOKE ALL ON TABLE mask.luot_chot FROM PUBLIC CASCADE;
    FOR q IN SELECT DISTINCT a.grantee FROM pg_class c,LATERAL aclexplode(c.relacl) a
        WHERE c.oid='mask.luot_chot'::regclass AND a.grantee<>0 AND a.grantee<>c.relowner LOOP
        EXECUTE format('REVOKE ALL ON TABLE mask.luot_chot FROM %I CASCADE',pg_get_userbyid(q.grantee));
    END LOOP;
    -- Thu cả quyền cấp riêng từng cột nếu chạy lại trên ACL đã bị mở rộng.
    FOR q IN SELECT a.attname FROM pg_attribute a WHERE a.attrelid='mask.luot_chot'::regclass
        AND a.attnum>0 AND NOT a.attisdropped LOOP
        EXECUTE format('REVOKE ALL (%I) ON TABLE mask.luot_chot FROM PUBLIC CASCADE',q.attname);
    END LOOP;
    FOR q IN SELECT DISTINCT a.attname,x.grantee FROM pg_attribute a
        JOIN pg_class c ON c.oid=a.attrelid CROSS JOIN LATERAL aclexplode(a.attacl) x
        WHERE c.oid='mask.luot_chot'::regclass AND a.attnum>0 AND NOT a.attisdropped
            AND x.grantee<>0 AND x.grantee<>c.relowner LOOP
        EXECUTE format('REVOKE ALL (%I) ON TABLE mask.luot_chot FROM %I CASCADE',
            q.attname,pg_get_userbyid(q.grantee));
    END LOOP;
    FOR b IN SELECT p.* FROM pg_proc p WHERE p.pronamespace='mask'::regnamespace
        AND p.proname IN ('giu_phien_anh_xa','phien_ban_luot','snapshot_luot','chot_luot') LOOP
        ck := b.oid::regprocedure::text;
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC CASCADE',ck);
        FOR q IN SELECT DISTINCT a.grantee FROM aclexplode(b.proacl) a
            WHERE a.grantee<>0 AND a.grantee<>b.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I CASCADE',ck,pg_get_userbyid(q.grantee));
        END LOOP;
        IF b.proname IN ('snapshot_luot','chot_luot') THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,login);
        END IF;
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
