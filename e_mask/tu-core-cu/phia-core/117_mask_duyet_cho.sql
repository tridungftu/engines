-- MASK-4a / CD-101: chỉ CSDL, caller giữ transaction; không công bố capability.
-- Chỉ cửa Admin Core được trả cum_goc. Không trả cụm gốc cho module/audit.
-- Dùng quyền quản trị engine/gói Core sẵn có như 111, cộng kiểm mtq_admin.
-- QD-TAM-20261107-05: giữ cụm đã từ chối và cặp tạm tới lần dọn an toàn.
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt || 'vai_doi_cau_truc_loi';
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
        RAISE EXCEPTION 'MASK_DUYET_SAI_DICH';
    END IF;
    FOREACH ck IN ARRAY ARRAY[chu,chu_mask,chay_mask] LOOP
        IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname=ck AND NOT rolcanlogin
            AND rolinherit AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole
            AND NOT rolcreatedb AND NOT rolreplication) THEN
            RAISE EXCEPTION 'MASK_DUYET_SAI_VAI';
        END IF;
    END LOOP;
    IF NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='loi' AND pg_get_userbyid(nspowner)=chu)
       OR NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='mask' AND pg_get_userbyid(nspowner)=chu_mask)
       OR NOT EXISTS (SELECT FROM pg_roles WHERE rolname=login AND rolcanlogin
            AND NOT rolsuper AND NOT rolbypassrls AND NOT rolcreaterole)
       OR EXISTS (SELECT FROM pg_auth_members WHERE roleid IN
            (SELECT oid FROM pg_roles WHERE rolname IN (chu_mask,chay_mask))
            OR member IN (SELECT oid FROM pg_roles WHERE rolname IN (chu_mask,chay_mask)))
       OR to_regprocedure('loi.xac_minh_phien(text,text,uuid,text,uuid,bigint)') IS NULL
       OR to_regprocedure('loi.ghi_kiem_toan(text,text,uuid,text,text,text,uuid,uuid,uuid,bigint,uuid,uuid)') IS NULL
       OR to_regprocedure('mask.tao_bi_danh(text,text)') IS NULL THEN
        RAISE EXCEPTION 'MASK_DUYET_THIEU_NEN';
    END IF;
    FOREACH bang IN ARRAY ARRAY['phien_xac_thuc','mtq_admin','phap_nhan','nhat_ky_kiem_toan'] LOOP
        IF NOT EXISTS (SELECT FROM pg_class WHERE oid=to_regclass('loi.'||bang)
            AND relkind='r' AND pg_get_userbyid(relowner)=chu
            AND relrowsecurity AND relforcerowsecurity) THEN
            RAISE EXCEPTION 'MASK_DUYET_THIEU_NEN';
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
            RAISE EXCEPTION 'MASK_DUYET_SAI_BANG_HOAC_RLS';
        END IF;
    END LOOP;
    FOR b IN SELECT p.* FROM pg_proc p WHERE
        (p.pronamespace='loi'::regnamespace AND p.proname='mask_kiem_admin')
        OR (p.pronamespace='mask'::regnamespace AND p.proname IN
            ('doc_cho','duyet_cho','tu_choi_cho','don_bi_danh_tam','giu_cum_tu_choi')) LOOP
        IF pg_get_userbyid(b.proowner)<>(CASE WHEN b.pronamespace='loi'::regnamespace
            THEN chu ELSE chu_mask END) THEN
            RAISE EXCEPTION 'MASK_DUYET_SAI_OWNER';
        END IF;
    END LOOP;
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);
    PERFORM pg_advisory_xact_lock(742601,1);
    EXECUTE format('SET LOCAL ROLE %I',chu_mask);
    -- 113 chỉ lưu lần gặp đầu. Lát ghi danh sách chờ tăng bộ đếm khi gặp lại,
    -- không suy đoán số lần trong lịch sử từ một yeu_cau_id duy nhất.
    ALTER TABLE mask.cho_duyet ADD COLUMN IF NOT EXISTS so_lan_gap bigint
        NOT NULL DEFAULT 1 CHECK (so_lan_gap>0);
    ALTER TABLE mask.cho_duyet ADD COLUMN IF NOT EXISTS trang_thai text
        NOT NULL DEFAULT 'CHO_DUYET' CHECK (trang_thai IN ('CHO_DUYET','DA_TU_CHOI'));
    CREATE INDEX IF NOT EXISTS cho_duyet_trang ON mask.cho_duyet(la_demo,tao_luc,id);

    -- Gặp lại cụm đã từ chối chỉ tăng đếm, không thay cặp tạm/trạng thái.
    -- INSERT bị bỏ qua; bên ghi tra lại cặp đang giữ theo (la_demo,cum_chuan).
    -- Chỉ xử lý cụm đã từ chối; giữ nguyên bất biến trùng của dòng chờ ở 113.
    CREATE OR REPLACE FUNCTION mask.giu_cum_tu_choi() RETURNS trigger
    LANGUAGE plpgsql SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE dong mask.cho_duyet;
    BEGIN
        -- Khóa cả dòng còn chờ: nếu đang từ chối đồng thời, đọc trạng thái sau khi chờ.
        SELECT * INTO dong FROM mask.cho_duyet w
            WHERE w.la_demo=NEW.la_demo AND w.cum_chuan=mask.chuan_hoa(NEW.cum_goc) FOR UPDATE;
        IF FOUND AND dong.trang_thai='DA_TU_CHOI' THEN
            UPDATE mask.cho_duyet c SET so_lan_gap=c.so_lan_gap+1 WHERE c.id=dong.id;
            RETURN NULL;
        END IF;
        RETURN NEW;
    END;
    $ham$;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid='mask.cho_duyet'::regclass
        AND tgname='giu_cum_tu_choi') THEN
        EXECUTE format('CREATE TRIGGER giu_cum_tu_choi BEFORE INSERT ON mask.cho_duyet
            FOR EACH ROW EXECUTE FUNCTION mask.giu_cum_tu_choi()');
    END IF;
    IF NOT EXISTS (SELECT FROM pg_trigger WHERE tgrelid='mask.cho_duyet'::regclass
        AND tgname='giu_cum_tu_choi' AND tgtype=7 AND tgenabled='O' AND tgqual IS NULL
        AND tgnargs=0 AND tgfoid='mask.giu_cum_tu_choi()'::regprocedure) THEN
        RAISE EXCEPTION 'MASK_DUYET_SAI_TRIGGER';
    END IF;
    -- Giữ nguyên owner/ACL/RLS 113; không cấp DML/đọc bảng cho Core hoặc module.
    -- Hàm Mask chỉ qua helper Core để xác minh phiên/Admin và ghi audit.
    EXECUTE format('SET LOCAL ROLE %I',chu);
    EXECUTE format('GRANT USAGE ON SCHEMA loi TO %I',chu_mask);

    -- Helper nội bộ chỉ owner Mask gọi; không cấp login/runtime/module.
    -- Không nhận văn bản tự do vào audit: thao tác thuộc bốn hằng, đối tượng UUID.
    CREATE OR REPLACE FUNCTION loi.mask_kiem_admin(p_ma text,p_nguoi uuid,p_thao_tac text,
        p_id uuid DEFAULT NULL)
    RETURNS TABLE(phap_nhan_id uuid,la_demo boolean)
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE pn uuid; ai uuid; hd text; dt text;
    BEGIN
        IF session_user::text IS DISTINCT FROM regexp_replace(current_user::text,
            'vai_doi_cau_truc_loi$','dang_nhap_loi') THEN
            RAISE EXCEPTION 'MASK_CHI_CORE' USING ERRCODE='42501';
        END IF;
        SELECT v.hanh_dong,v.doi_tuong INTO hd,dt FROM (VALUES
            ('DOC','CORE:MODULE:XEM','mask.cho_duyet.doc'),
            ('DUYET','CORE:MODULE:DUYET','mask.cho_duyet.duyet'),
            ('TU_CHOI','CORE:MODULE:DUYET','mask.cho_duyet.tu_choi'),
            ('DON','CORE:MODULE:SUA','mask.bi_danh_tam.don')
        ) AS v(thao_tac,hanh_dong,doi_tuong) WHERE v.thao_tac=p_thao_tac;
        IF NOT FOUND THEN RAISE EXCEPTION 'MASK_THAO_TAC' USING ERRCODE='22023'; END IF;
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        SELECT p.phap_nhan_id INTO pn FROM loi.phien_xac_thuc p
            WHERE p.ma_bam=sha256(convert_to(p_ma,'UTF8')) AND p.loai='NGUOI_DUNG';
        SELECT x.nguoi_dung_id,x.phap_nhan_id INTO ai,pn
            FROM loi.xac_minh_phien(p_ma,'core',pn,hd,NULL,NULL) x;
        IF ai IS NULL OR ai IS DISTINCT FROM p_nguoi THEN
            RAISE EXCEPTION 'MASK_PHIEN' USING ERRCODE='42501';
        END IF;
        IF NOT EXISTS (SELECT FROM loi.mtq_admin a
            WHERE a.nguoi_dung_id=ai AND a.thu_hoi_luc IS NULL) THEN
            RAISE EXCEPTION 'MASK_CHI_ADMIN' USING ERRCODE='42501';
        END IF;
        -- Audit cùng transaction, lỗi ở thao tác sau tự rollback bản ghi này.
        PERFORM loi.ghi_kiem_toan(hd,dt,p_id,'DAT',p_ma,'core',pn);
        -- Tuyệt đối không nhận cờ DEMO/pháp nhân từ người gọi hoặc GUC tự khai.
        RETURN QUERY SELECT n.id,n.la_demo FROM loi.phap_nhan n WHERE n.id=pn;
    END;
    $ham$;
    EXECUTE format('SET LOCAL ROLE %I',chu_mask);

    CREATE OR REPLACE FUNCTION mask.doc_cho(p_ma text,p_nguoi uuid,
        p_nhom text DEFAULT NULL,p_trang_thai text DEFAULT NULL,
        p_tu_ngay date DEFAULT NULL,p_den_ngay date DEFAULT NULL,
        p_sau_luc timestamptz DEFAULT NULL,p_sau_id uuid DEFAULT NULL,p_gioi_han integer DEFAULT 50)
    RETURNS TABLE(id uuid,cum_goc text,nhom text,so_lan_gap bigint,
        tao_luc timestamptz,trang_thai text)
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_kiem_admin(p_ma,p_nguoi,'DOC');
        IF p_gioi_han IS NULL OR p_gioi_han NOT BETWEEN 1 AND 200
           OR (p_nhom IS NOT NULL AND mask.tien_to(p_nhom) IS NULL)
           OR (p_trang_thai IS NOT NULL AND p_trang_thai NOT IN
               ('DANG_XU_LY','DA_DONG','CHO_DUYET','DA_TU_CHOI'))
           OR (p_tu_ngay IS NOT NULL AND NOT isfinite(p_tu_ngay))
           OR (p_den_ngay IS NOT NULL AND NOT isfinite(p_den_ngay))
           OR p_tu_ngay>p_den_ngay
           OR ((p_sau_luc IS NULL)<>(p_sau_id IS NULL)) THEN
            RAISE EXCEPTION 'MASK_BO_LOC' USING ERRCODE='22023';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        -- GIÁ TRỊ cum_goc chỉ trả ở cửa Admin đã xác minh phía trên.
        -- Giữ bộ lọc/trạng thái mã yêu cầu cũ; chỉ cửa lọc tường minh mới trả dòng từ chối.
        RETURN QUERY SELECT c.id,c.cum_goc,c.nhom,c.so_lan_gap,c.tao_luc,
                (CASE WHEN c.trang_thai='DA_TU_CHOI' THEN c.trang_thai ELSE y.trang_thai END)
            FROM mask.cho_duyet c JOIN mask.yeu_cau y ON y.id=c.yeu_cau_id AND y.la_demo=c.la_demo
            WHERE c.la_demo=ctx.la_demo
              AND (p_nhom IS NULL OR c.nhom=p_nhom)
              AND c.trang_thai=(CASE WHEN p_trang_thai='DA_TU_CHOI' THEN 'DA_TU_CHOI' ELSE 'CHO_DUYET' END)
              AND (p_trang_thai IS NULL OR p_trang_thai IN ('CHO_DUYET','DA_TU_CHOI')
                  OR y.trang_thai=p_trang_thai)
              AND (p_tu_ngay IS NULL OR c.tao_luc >= (p_tu_ngay::timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh'))
              AND (p_den_ngay IS NULL OR c.tao_luc < ((p_den_ngay+1)::timestamp AT TIME ZONE 'Asia/Ho_Chi_Minh'))
              AND (p_sau_luc IS NULL OR (c.tao_luc,c.id)>(p_sau_luc,p_sau_id))
            ORDER BY c.tao_luc,c.id LIMIT p_gioi_han;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.duyet_cho(p_ma text,p_nguoi uuid,p_id uuid,
        p_ma_junsky text DEFAULT NULL) RETURNS TABLE(id uuid,bi_danh text)
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; c mask.cho_duyet; d mask.dinh_danh;
        cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_kiem_admin(p_ma,p_nguoi,'DUYET',p_id);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        SELECT * INTO c FROM mask.cho_duyet w WHERE w.id=p_id AND w.la_demo=ctx.la_demo
            AND w.trang_thai='CHO_DUYET' FOR UPDATE;
        IF NOT FOUND THEN RAISE EXCEPTION 'MASK_KHONG_THAY' USING ERRCODE='22023'; END IF;
        -- 113 cấm ngoặc trong danh mục; không cắt/sửa ngầm cụm đang chờ.
        IF c.cum_goc ~ '[\[\]]' THEN
            RAISE EXCEPTION 'MASK_CUM_KHONG_HOP_LE' USING ERRCODE='22023';
        END IF;
        IF p_ma_junsky IS NOT NULL AND (p_ma_junsky !~ '^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$'
            OR upper(p_ma_junsky) LIKE 'MASK%') THEN
            RAISE EXCEPTION 'MASK_MA_JUNSKY' USING ERRCODE='22023';
        END IF;
        -- Không ghi đè tên chuẩn/mã cũ, kể cả tên khác dùng chung mã Junsky.
        BEGIN
            INSERT INTO mask.dinh_danh(gia_tri,nhom,ma_junsky,bi_danh_tam,nguon,la_demo)
                VALUES(c.cum_goc,c.nhom,p_ma_junsky,c.bi_danh_tam,c.nguon,ctx.la_demo)
                RETURNING * INTO d;
        EXCEPTION WHEN unique_violation THEN
            RAISE EXCEPTION 'MASK_XUNG_DOT_DANH_MUC' USING ERRCODE='22023';
        WHEN check_violation THEN
            RAISE EXCEPTION 'MASK_CUM_KHONG_HOP_LE' USING ERRCODE='22023';
        END;
        DELETE FROM mask.cho_duyet w WHERE w.id=c.id AND w.la_demo=ctx.la_demo;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN QUERY SELECT d.id,d.bi_danh;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.tu_choi_cho(p_ma text,p_nguoi uuid,p_id uuid) RETURNS boolean
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; ma uuid; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_kiem_admin(p_ma,p_nguoi,'TU_CHOI',p_id);
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        UPDATE mask.cho_duyet c SET trang_thai='DA_TU_CHOI'
            WHERE c.id=p_id AND c.la_demo=ctx.la_demo AND c.trang_thai='CHO_DUYET'
            RETURNING c.id INTO ma;
        IF NOT FOUND THEN RAISE EXCEPTION 'MASK_KHONG_THAY' USING ERRCODE='22023'; END IF;
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN true;
    END;
    $ham$;

    CREATE OR REPLACE FUNCTION mask.don_bi_danh_tam(p_ma text,p_nguoi uuid) RETURNS bigint
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE ctx record; ma uuid; so bigint := 0; cu text := current_setting('ktt.mask_la_demo',true);
    BEGIN
        SELECT * INTO STRICT ctx FROM loi.mask_kiem_admin(p_ma,p_nguoi,'DON');
        IF current_setting('transaction_isolation')<>'read committed' THEN
            RAISE EXCEPTION 'MASK_CAN_READ_COMMITTED' USING ERRCODE='25000';
        END IF;
        PERFORM set_config('ktt.mask_la_demo',ctx.la_demo::text,true);
        -- Giữ tham chiếu ổn định và lấy snapshot mới sau khi chờ các giao dịch ghi.
        LOCK TABLE mask.yeu_cau IN SHARE MODE;
        FOR ma IN UPDATE mask.dinh_danh d SET bi_danh_tam=NULL
            WHERE d.la_demo=ctx.la_demo AND d.bi_danh_tam IS NOT NULL
              AND NOT EXISTS (SELECT FROM mask.yeu_cau y WHERE y.la_demo=ctx.la_demo
                  AND y.trang_thai='DANG_XU_LY' AND d.bi_danh_tam=ANY(y.bi_danh_tam_da_dung))
            RETURNING d.id LOOP
            so := so+1;
            -- Audit Core không có trường văn bản tự do/số đếm: ghi từng id đã dọn.
            PERFORM loi.mask_kiem_admin(p_ma,p_nguoi,'DON',ma);
        END LOOP;
        FOR ma IN DELETE FROM mask.cho_duyet c
            WHERE c.la_demo=ctx.la_demo AND c.trang_thai='DA_TU_CHOI'
              AND NOT EXISTS (SELECT FROM mask.yeu_cau y WHERE y.la_demo=ctx.la_demo
                  AND y.trang_thai='DANG_XU_LY' AND c.bi_danh_tam=ANY(y.bi_danh_tam_da_dung))
            RETURNING c.id LOOP
            so := so+1;
            PERFORM loi.mask_kiem_admin(p_ma,p_nguoi,'DON',ma);
        END LOOP;
        -- Helper đầu hàm đã ghi cả lượt 0 dòng; không ghi bí danh/định danh.
        PERFORM set_config('ktt.mask_la_demo',coalesce(cu,''),true);
        RETURN so;
    END;
    $ham$;

    PERFORM set_config('role',vai_cu,true);
    FOR b IN SELECT p.oid,p.proowner,p.proacl,p.proname FROM pg_proc p WHERE
        (p.pronamespace='loi'::regnamespace AND p.proname='mask_kiem_admin')
        OR (p.pronamespace='mask'::regnamespace AND p.proname IN
            ('doc_cho','duyet_cho','tu_choi_cho','don_bi_danh_tam','giu_cum_tu_choi')) LOOP
        ck := b.oid::regprocedure::text;
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ck);
        FOR q IN SELECT DISTINCT a.grantee FROM aclexplode(b.proacl) a
            WHERE a.grantee<>0 AND a.grantee<>b.proowner LOOP
            EXECUTE format('REVOKE ALL ON FUNCTION %s FROM %I',ck,pg_get_userbyid(q.grantee));
        END LOOP;
        IF b.proname IN ('doc_cho','duyet_cho','tu_choi_cho','don_bi_danh_tam') THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,login);
        ELSIF b.proname='mask_kiem_admin' THEN
            EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,chu_mask);
        END IF;
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
