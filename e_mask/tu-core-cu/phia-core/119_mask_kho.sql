-- MASK-3B: kho nội bộ Core, xác minh lại phiên/tài liệu ở mọi cửa.
-- Chỉ liet_ke_dinh_danh/tra_dinh_danh trả giá trị gốc cho xử lý nội bộ.
-- Bổ sung chú thích 117: ngoài cửa Admin, hai cửa nội bộ này được đọc gốc
-- sau kiểm phiên/tài liệu và ghi audit không chứa giá trị hoặc bí danh.
-- Chống đếm lại tối thiểu: yeu_cau.cum_da_gap (cụm đã chuẩn hóa), không xuất ra.
-- Khóa hàng yêu cầu + UPSERT tăng đếm trong cùng lần gọi; hai yêu cầu vẫn
-- tăng nguyên tử trên hàng chờ chung. yeu_cau_id của cụm cũ đã tính lần đầu;
-- không tăng lại khi chính yêu cầu đó gặp lại, không suy thêm lịch sử đã mất.
-- Mỗi gọi một transaction; snapshot/chốt toàn lượt nguyên tử thuộc lát D.
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
        RAISE EXCEPTION 'MASK_KHO_SAI_DICH';
    END IF;
    FOREACH ck IN ARRAY ARRAY[chu,chu_tl,chu_mask,chay_mask] LOOP
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=ck AND NOT rolcanlogin
            AND rolinherit AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole
            AND NOT rolcreatedb AND NOT rolreplication) THEN
            RAISE EXCEPTION 'MASK_KHO_SAI_VAI';
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
       OR to_regprocedure('loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)') IS NULL
       OR to_regprocedure('mask.cap_ma_yeu_cau(text,text,uuid,text,uuid,uuid,bigint)') IS NULL
       OR to_regprocedure('mask.chuan_hoa(text)') IS NULL
       OR to_regprocedure('mask.tien_to(text)') IS NULL
       OR to_regprocedure('loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi.ghi_kiem_toan(text,text,uuid,text,text,text,uuid,uuid,uuid,bigint,uuid,uuid)') IS NULL
       OR to_regprocedure('loi_tai_lieu.ngu_canh(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.kiem_quyen(text,text,uuid,text,jsonb,text,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi_tai_lieu.duoc_xem_noi_dung(uuid,uuid,text)') IS NULL
       OR to_regcollation('"und-x-icu"') IS NULL THEN
        RAISE EXCEPTION 'MASK_KHO_THIEU_NEN_118';
    END IF;
    FOREACH bang IN ARRAY ARRAY['phien_xac_thuc','phap_nhan','nguoi_dung','phan_quyen','nhat_ky_kiem_toan'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu
            AND relrowsecurity AND relforcerowsecurity) THEN
            RAISE EXCEPTION 'MASK_KHO_THIEU_NEN_118';
        END IF;
    END LOOP;
    FOREACH bang IN ARRAY ARRAY['tai_lieu','quyen_tai_lieu'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi_tai_lieu.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu_tl
            AND relrowsecurity AND relforcerowsecurity)
           OR NOT EXISTS (SELECT FROM pg_policy WHERE polrelid=to_regclass('loi_tai_lieu.'||bang)
                AND polname='tai_lieu_phien') THEN
            RAISE EXCEPTION 'MASK_KHO_THIEU_NEN_118';
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
            RAISE EXCEPTION 'MASK_KHO_SAI_BANG_HOAC_RLS';
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT FROM pg_attribute WHERE attrelid='mask.cho_duyet'::regclass
        AND attname='so_lan_gap' AND atttypid='bigint'::regtype AND attnotnull AND NOT attisdropped)
       OR EXISTS (SELECT FROM pg_attribute WHERE attrelid='mask.yeu_cau'::regclass
        AND attname='cum_da_gap' AND NOT attisdropped AND (atttypid<>'text[]'::regtype OR NOT attnotnull)) THEN
        RAISE EXCEPTION 'MASK_KHO_SAI_COT';
    END IF;
    -- Kiểm owner cả helper 118 lẫn các cửa khi chạy lại, trước mọi DDL.
    FOR b IN SELECT p.* FROM pg_proc p WHERE p.oid IN (
        to_regprocedure('loi.mask_ngu_canh(text,text,uuid,text,uuid,bigint)'),
        to_regprocedure('loi_tai_lieu.mask_kiem_tai_lieu(text,text,uuid,text,uuid,uuid,bigint)'),
        to_regprocedure('mask.cap_ma_yeu_cau(text,text,uuid,text,uuid,uuid,bigint)'))
        OR (p.pronamespace='loi'::regnamespace AND p.proname='mask_kiem_toan_doc')
        OR (p.pronamespace='mask'::regnamespace AND p.proname IN
            ('kiem_yeu_cau','liet_ke_dinh_danh','liet_ke_bi_danh','tra_bi_danh','ghi_cho_duyet',
             'doc_yeu_cau','ghi_bi_danh_da_dung','tra_dinh_danh','dong_yeu_cau')) LOOP
        IF pg_get_userbyid(b.proowner)<>(CASE WHEN b.pronamespace='loi'::regnamespace THEN chu
            WHEN b.pronamespace='loi_tai_lieu'::regnamespace THEN chu_tl ELSE chu_mask END) THEN
            RAISE EXCEPTION 'MASK_KHO_SAI_OWNER';
        END IF;
    END LOOP;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);
    EXECUTE format('SET LOCAL ROLE %I',chu);
    -- Chỉ owner Mask gọi; không cấp quyền ghi audit tổng quát cho Mask.
    CREATE OR REPLACE FUNCTION loi.mask_kiem_toan_doc(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_thao_tac text) RETURNS void
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; dt text;
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_ngu_canh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        SELECT v.doi_tuong INTO dt FROM (VALUES
            ('LIET_KE','mask.dinh_danh.liet_ke'),('TRA','mask.dinh_danh.tra')
        ) AS v(thao_tac,doi_tuong) WHERE v.thao_tac=p_thao_tac;
        IF NOT FOUND OR p_yeu_cau IS NULL THEN
            RAISE EXCEPTION 'MASK_THAO_TAC' USING ERRCODE='22023';
        END IF;
        PERFORM loi.ghi_kiem_toan(p_hd,dt,p_yeu_cau,'DAT',p_ma,p_module,
            ctx.phap_nhan_id,p_yeu_cau,p_viec,p_the_he);
    END;
    $ham$;
    EXECUTE format('SET LOCAL ROLE %I',chu_mask);
    ALTER TABLE mask.yeu_cau ADD COLUMN IF NOT EXISTS cum_da_gap text[]
        NOT NULL DEFAULT ARRAY[]::text[];

    -- Helper chỉ owner Mask gọi. Pháp nhân suy lại qua tài liệu của yêu cầu,
    -- vì 113 cố ý không chia danh mục Mask theo pháp nhân.
    CREATE OR REPLACE FUNCTION mask.kiem_yeu_cau(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid)
    RETURNS TABLE(nguoi_gui uuid,phap_nhan_id uuid,la_demo boolean)
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; yc mask.yeu_cau; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_ngu_canh(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        -- Cùng thứ tự khóa với cửa dọn 117 (SHARE trên yeu_cau), không nâng
        -- khóa sau khi đã giữ hàng danh mục; đóng/ghi tham chiếu không chen nhau.
        LOCK TABLE mask.yeu_cau IN ROW EXCLUSIVE MODE;
        SELECT y.* INTO yc FROM mask.yeu_cau y WHERE y.id=p_yeu_cau
            AND y.module=p_module AND y.nguoi_gui=ctx.nguoi_gui AND y.la_demo=ctx.la_demo
            AND y.trang_thai='DANG_XU_LY' FOR UPDATE;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'MASK_YEU_CAU' USING ERRCODE='42501';
        END IF;
        PERFORM loi_tai_lieu.mask_kiem_tai_lieu(p_ma,p_module,ctx.phap_nhan_id,p_hd,
            yc.tai_lieu_id,p_viec,p_the_he);
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN QUERY SELECT ctx.nguoi_gui,ctx.phap_nhan_id,ctx.la_demo;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.liet_ke_dinh_danh(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; kq jsonb; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        -- Phạm vi bước che: danh mục chính thức chung cùng vùng DEMO (113),
        -- cần đầy đủ để dò định danh kể cả khi chưa được bộ dò nhận diện.
        -- Cụm chờ chỉ của cùng module/người gửi/tài liệu đã được xác minh;
        -- không đọc các cụm chờ của tài liệu/người dùng khác trong cùng vùng.
        SELECT coalesce(jsonb_agg(z.muc ORDER BY z.khoa),'[]'::jsonb) INTO kq FROM (
            SELECT d.gia_tri_chuan AS khoa,jsonb_build_object('gia_tri',d.gia_tri,'nhom',d.nhom,
                'bi_danh',d.bi_danh,'bi_danh_tam',d.bi_danh_tam,'nguon','chinh_thuc') AS muc
                FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo
            UNION ALL
            SELECT c.cum_chuan,jsonb_build_object('gia_tri',c.cum_goc,'nhom',c.nhom,
                'bi_danh',c.bi_danh_tam,'nguon','tam','so_lan_gap',c.so_lan_gap)
                FROM mask.cho_duyet c WHERE c.la_demo=ctx.la_demo
                    AND EXISTS (SELECT FROM mask.yeu_cau y JOIN mask.yeu_cau yc
                        ON yc.id=p_yeu_cau AND yc.la_demo=ctx.la_demo
                        WHERE y.id=c.yeu_cau_id AND y.la_demo=ctx.la_demo
                            AND y.module=yc.module AND y.nguoi_gui=yc.nguoi_gui
                            AND y.tai_lieu_id=yc.tai_lieu_id)
                    AND NOT EXISTS
                    (SELECT FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo AND d.gia_tri_chuan=c.cum_chuan)
        ) z;
        PERFORM loi.mask_kiem_toan_doc(p_ma,p_module,ctx.phap_nhan_id,p_hd,
            p_viec,p_the_he,p_yeu_cau,'LIET_KE');
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    -- Mở che dò bí danh hỏng trên toàn bảng cùng vùng như 113; không cần gốc.
    CREATE OR REPLACE FUNCTION mask.liet_ke_bi_danh(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; kq jsonb; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        SELECT coalesce(jsonb_agg(z.muc ORDER BY z.ma),'[]'::jsonb) INTO kq FROM (
            SELECT d.bi_danh AS ma,jsonb_build_object('bi_danh',d.bi_danh,
                'bi_danh_tam',d.bi_danh_tam) AS muc FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo
            UNION ALL
            SELECT c.bi_danh_tam,jsonb_build_object('bi_danh',c.bi_danh_tam)
                FROM mask.cho_duyet c WHERE c.la_demo=ctx.la_demo
        ) z;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.tra_bi_danh(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_cum text) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; kq jsonb; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        SELECT jsonb_build_object('nhom',d.nhom,'bi_danh',d.bi_danh,
            'bi_danh_tam',d.bi_danh_tam,'nguon','chinh_thuc') INTO kq
            FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo AND d.gia_tri_chuan=mask.chuan_hoa(p_cum);
        IF NOT FOUND THEN
            SELECT jsonb_build_object('nhom',c.nhom,'bi_danh',c.bi_danh_tam,
                'nguon','tam','so_lan_gap',c.so_lan_gap) INTO kq FROM mask.cho_duyet c
                WHERE c.la_demo=ctx.la_demo AND c.cum_chuan=mask.chuan_hoa(p_cum);
        END IF;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.ghi_cho_duyet(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_gia_tri text,p_nhom text,p_bi_danh text,
        p_chi_gap_lai boolean DEFAULT false) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; chuan text; da_dem boolean; de_xuat text; moi_id uuid := gen_random_uuid();
        hang mask.cho_duyet; chinh mask.dinh_danh; kq jsonb;
        cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        IF p_gia_tri IS NULL OR length(p_gia_tri) NOT BETWEEN 2 AND 300
           OR mask.chuan_hoa(p_gia_tri)='' OR p_gia_tri ~ '[\[\]]'
           OR p_nhom IS NULL OR mask.tien_to(p_nhom) IS NULL OR p_chi_gap_lai IS NULL THEN
            RAISE EXCEPTION 'MASK_CUM_KHONG_HOP_LE' USING ERRCODE='22023';
        END IF;
        chuan := mask.chuan_hoa(p_gia_tri);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        -- Cùng khóa hàng chờ với duyet_cho 117. Nếu duyệt vừa xóa hàng sau
        -- khi ta chờ khóa, SELECT danh mục kế tiếp lấy snapshot mới thấy kết quả.
        SELECT c.* INTO hang FROM mask.cho_duyet c
            WHERE c.la_demo=ctx.la_demo AND c.cum_chuan=chuan FOR UPDATE;
        SELECT d.* INTO chinh FROM mask.dinh_danh d
            WHERE d.la_demo=ctx.la_demo AND d.gia_tri_chuan=chuan FOR KEY SHARE;
        IF FOUND THEN
            IF p_chi_gap_lai AND chinh.nhom<>p_nhom THEN
                RAISE EXCEPTION 'MASK_NHOM' USING ERRCODE='22023';
            END IF;
            kq := jsonb_build_object('nhom',chinh.nhom,'bi_danh',chinh.bi_danh,
                'bi_danh_tam',chinh.bi_danh_tam,'nguon','chinh_thuc','vua_them',false);
        ELSE
            de_xuat := p_bi_danh;
            IF p_chi_gap_lai THEN
                de_xuat := hang.bi_danh_tam;
                IF hang.id IS NULL THEN
                    RAISE EXCEPTION 'MASK_KHONG_THAY' USING ERRCODE='22023';
                END IF;
            END IF;
            IF de_xuat IS NULL OR de_xuat !~ '^\[\[MASKTAM-[0-9a-f]{32}\]\]$'
               OR EXISTS (SELECT FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo
                    AND lower(d.bi_danh_tam COLLATE "und-x-icu")=lower(de_xuat COLLATE "und-x-icu")) THEN
                RAISE EXCEPTION 'MASK_BI_DANH' USING ERRCODE='22023';
            END IF;
            SELECT chuan=ANY(y.cum_da_gap) INTO da_dem FROM mask.yeu_cau y
                WHERE y.id=p_yeu_cau AND y.la_demo=ctx.la_demo;
            IF hang.id IS NOT NULL THEN
                -- Không đi qua trigger INSERT 117 của cụm đã từ chối: trigger
                -- đó tăng đếm mỗi lần INSERT, không biết dấu chống lặp của 119.
                UPDATE mask.cho_duyet c SET
                    so_lan_gap=c.so_lan_gap+(NOT da_dem AND c.yeu_cau_id<>p_yeu_cau)::integer
                    WHERE c.id=hang.id AND c.la_demo=ctx.la_demo RETURNING c.* INTO hang;
            ELSE
                INSERT INTO mask.cho_duyet AS c(id,cum_goc,nhom,bi_danh_tam,yeu_cau_id,la_demo,nguon,so_lan_gap)
                VALUES(moi_id,p_gia_tri,p_nhom,de_xuat,p_yeu_cau,ctx.la_demo,'mask',1)
                ON CONFLICT (la_demo,cum_chuan) DO UPDATE
                    SET so_lan_gap=c.so_lan_gap+(NOT da_dem AND c.yeu_cau_id<>p_yeu_cau)::integer
                RETURNING c.* INTO hang;
                IF NOT FOUND THEN
                    -- Một yêu cầu khác vừa tạo rồi từ chối: trigger 117 đã
                    -- tính lần gặp này và giữ cặp tạm, INSERT không RETURNING.
                    SELECT c.* INTO STRICT hang FROM mask.cho_duyet c
                        WHERE c.la_demo=ctx.la_demo AND c.cum_chuan=chuan FOR UPDATE;
                END IF;
            END IF;
            IF hang.nhom<>p_nhom THEN
                RAISE EXCEPTION 'MASK_NHOM' USING ERRCODE='22023';
            END IF;
            -- Giữ ngay tham chiếu, kể cả trước ghi_bi_danh_da_dung; retry cùng
            -- yêu cầu không tăng lại, yêu cầu mới vẫn tăng bằng UPSERT ở trên.
            UPDATE mask.yeu_cau y SET
                cum_da_gap=ARRAY(SELECT DISTINCT u.b FROM unnest(array_append(y.cum_da_gap,chuan)) u(b) ORDER BY u.b),
                bi_danh_tam_da_dung=ARRAY(SELECT DISTINCT u.b FROM unnest(array_append(
                    y.bi_danh_tam_da_dung,hang.bi_danh_tam)) u(b) ORDER BY u.b)
                WHERE y.id=p_yeu_cau AND y.la_demo=ctx.la_demo;
            kq := jsonb_build_object('nhom',hang.nhom,'bi_danh',hang.bi_danh_tam,'nguon','tam',
                'so_lan_gap',hang.so_lan_gap,'vua_them',hang.id=moi_id);
        END IF;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.doc_yeu_cau(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; kq jsonb; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        SELECT jsonb_build_object('trang_thai',y.trang_thai) INTO kq
            FROM mask.yeu_cau y WHERE y.id=p_yeu_cau AND y.la_demo=ctx.la_demo;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.ghi_bi_danh_da_dung(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_bi_danh text[]) RETURNS boolean
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; ma_bd text; bd_goc text; tam text[] := ARRAY[]::text[];
        cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        IF p_bi_danh IS NULL OR cardinality(p_bi_danh)>250000
            OR (cardinality(p_bi_danh)>0 AND array_ndims(p_bi_danh)<>1) THEN
            RAISE EXCEPTION 'MASK_BI_DANH' USING ERRCODE='22023';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        FOREACH ma_bd IN ARRAY p_bi_danh LOOP
            IF ma_bd IS NULL OR ma_bd !~ '^\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]$' THEN
                RAISE EXCEPTION 'MASK_BI_DANH' USING ERRCODE='22023';
            END IF;
            ma_bd := lower(ma_bd COLLATE "und-x-icu");
            IF EXISTS (SELECT FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo
                AND lower(d.bi_danh COLLATE "und-x-icu")=ma_bd) THEN
                CONTINUE;
            END IF;
            SELECT c.bi_danh_tam INTO bd_goc FROM mask.cho_duyet c WHERE c.la_demo=ctx.la_demo
                AND lower(c.bi_danh_tam COLLATE "und-x-icu")=ma_bd FOR KEY SHARE;
            IF NOT FOUND THEN
                SELECT d.bi_danh_tam INTO bd_goc FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo
                    AND lower(d.bi_danh_tam COLLATE "und-x-icu")=ma_bd FOR KEY SHARE;
            END IF;
            IF NOT FOUND THEN
                RAISE EXCEPTION 'MASK_KHONG_THAY' USING ERRCODE='22023';
            END IF;
            tam := array_append(tam,bd_goc);
        END LOOP;
        UPDATE mask.yeu_cau y SET bi_danh_tam_da_dung=ARRAY(
            SELECT DISTINCT u.b FROM unnest(y.bi_danh_tam_da_dung||tam) u(b) ORDER BY u.b)
            WHERE y.id=p_yeu_cau AND y.la_demo=ctx.la_demo;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN true;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.tra_dinh_danh(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid,p_bi_danh text) RETURNS text
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; kq text; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        IF p_bi_danh IS NULL OR p_bi_danh !~ '^\[\[[A-Za-z0-9][A-Za-z0-9_.-]{0,99}\]\]$' THEN
            RAISE EXCEPTION 'MASK_BI_DANH' USING ERRCODE='22023';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        SELECT d.gia_tri INTO kq FROM mask.dinh_danh d WHERE d.la_demo=ctx.la_demo
            AND (lower(d.bi_danh COLLATE "und-x-icu")=lower(p_bi_danh COLLATE "und-x-icu")
                OR lower(d.bi_danh_tam COLLATE "und-x-icu")=lower(p_bi_danh COLLATE "und-x-icu"));
        IF NOT FOUND THEN
            SELECT c.cum_goc INTO kq FROM mask.cho_duyet c WHERE c.la_demo=ctx.la_demo
                AND lower(c.bi_danh_tam COLLATE "und-x-icu")=lower(p_bi_danh COLLATE "und-x-icu");
        END IF;
        PERFORM loi.mask_kiem_toan_doc(p_ma,p_module,ctx.phap_nhan_id,p_hd,
            p_viec,p_the_he,p_yeu_cau,'TRA');
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN kq;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.dong_yeu_cau(p_ma text,p_module text,p_pn uuid,p_hd text,
        p_viec uuid,p_the_he bigint,p_yeu_cau uuid) RETURNS boolean
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM mask.kiem_yeu_cau(p_ma,p_module,p_pn,p_hd,p_viec,p_the_he,p_yeu_cau);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        UPDATE mask.yeu_cau y SET trang_thai='DA_DONG',dong_luc=statement_timestamp()
            WHERE y.id=p_yeu_cau AND y.la_demo=ctx.la_demo;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN true;
    END;
    $ham$;

    PERFORM set_config('role',vai_cu,true);
    -- Không cấp DML bảng/cột mới. Thu cả grant option phụ thuộc khi chạy lại.
    FOR b IN SELECT p.* FROM pg_proc p WHERE
        (p.pronamespace='loi'::regnamespace AND p.proname='mask_kiem_toan_doc')
        OR (p.pronamespace='mask'::regnamespace AND p.proname IN
            ('kiem_yeu_cau','liet_ke_dinh_danh','liet_ke_bi_danh','tra_bi_danh','ghi_cho_duyet',
             'doc_yeu_cau','ghi_bi_danh_da_dung','tra_dinh_danh','dong_yeu_cau')) LOOP
        ck := b.oid::regprocedure::text;
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC CASCADE',ck);
        FOR q IN SELECT DISTINCT a.grantee FROM aclexplode(b.proacl) a
            WHERE a.grantee<>0 AND a.grantee<>b.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I CASCADE',ck,pg_get_userbyid(q.grantee));
        END LOOP;
        IF b.pronamespace='loi'::regnamespace THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,chu_mask);
        ELSIF b.proname<>'kiem_yeu_cau' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,login);
        END IF;
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
