-- AI-LAT10a / QD-TAM-20261108-04. Dữ liệu tạm DEMO, caller giữ transaction.
-- Một bảng riêng; hàng việc chỉ giữ tham_chieu_id/ket_qua_id như XS-2.
DO $migration$
DECLARE
    tt text := coalesce(current_setting('kho_tri_thuc.tien_to_vai',true),'');
    chu text := tt||'vai_doi_cau_truc_loi';
    vai_cu text := current_setting('role');
    path_cu text := current_setting('search_path');
    ck text; f regprocedure; nguon text; moi text; rang_buoc text; neo text;
    moc text := 'IF p_loai IS DISTINCT FROM ''XUAT_DU_LIEU'' OR p_phien_ban IS DISTINCT FROM 1';
BEGIN
    IF (tt<>'' AND tt !~ '^[a-z][a-z0-9_]*_$')
        OR octet_length(tt||'vai_doi_cau_truc_loi_tai_lieu')>63
        OR (tt<>'' AND current_database() !~ '^kho_test_')
        OR current_database() !~ '^(kho_core_demo_g2_[a-z0-9_]+|kho_test_[a-z0-9_]+)$'
        OR current_setting('server_version_num')::integer<160000
        OR NOT EXISTS (SELECT FROM pg_namespace WHERE nspname='loi' AND pg_get_userbyid(nspowner)=chu)
        OR to_regprocedure('loi.xuat_loai_tru()') IS NULL
        OR to_regprocedure('loi.viec_giu(text,text,uuid,text,uuid,uuid,bigint)') IS NULL THEN
        RAISE EXCEPTION 'AI-LAT10a: cần Core DEMO/test PG16+, đúng owner và nền hàng việc';
    END IF;
    EXECUTE format('SET LOCAL ROLE %I',chu);
    PERFORM set_config('search_path','pg_catalog,pg_temp',true);

    -- Giữ danh sách 048/090; dữ liệu chạy thử không đi theo bản xuất công ty.
    CREATE OR REPLACE FUNCTION loi.xuat_loai_tru() RETURNS jsonb
    LANGUAGE sql IMMUTABLE SECURITY INVOKER SET search_path=pg_catalog,pg_temp AS $loai_tru$
        SELECT '{
            "loi.phan_quyen":"Phan quyen nguoi dung, khong chuyen quyen sang ban xuat",
            "loi.phien_xac_thuc":"Phien xac thuc va bi mat phien",
            "loi.mtq_phong":"Cau hinh to chuc phan quyen",
            "loi.mtq_phien_ban":"Phien ban ma tran quyen",
            "loi.mtq_dong":"Dong ma tran quyen",
            "loi.mtq_gan_vai":"Gan vai nguoi dung",
            "loi.mtq_pham_vi":"Pham vi uy quyen nguoi dung",
            "loi.mtq_kich_hoat":"Trang thai kich hoat ma tran quyen",
            "loi.mtq_thay_doi":"Audit dieu khien ma tran quyen; audit nghiep vu o nhat_ky_kiem_toan",
            "loi.mtq_tu_choi":"Audit tu choi phan quyen, co the chua pham vi phap nhan khac",
            "loi.module_cong_tac":"Cau hinh rollout module tai runtime",
            "loi.module_nguoi_thu":"Danh sach nguoi thu rollout",
            "loi_tai_lieu.quyen_tai_lieu":"Quyen truy cap tai lieu gan nguoi dung",
            "loi.hang_viec":"Hang doi runtime, khong tai phat cong viec khi nhap",
            "loi.buoc_viec":"Dieu phoi buoc runtime",
            "loi.lan_thu":"Lan thu runtime",
            "loi.lan_thu_trang_thai":"Trang thai lan thu runtime",
            "loi.su_kien":"Outbox dieu phoi runtime",
            "loi.hop_nhan_su_kien":"Inbox dieu phoi runtime",
            "loi.ack_su_kien":"Xac nhan giao nhan runtime",
            "loi.quy_trinh":"Dinh nghia dieu phoi runtime",
            "loi.quy_trinh_lan":"Lan chay dieu phoi runtime",
            "loi.xdl_yeu_cau_xuat":"Yêu cầu xuất Excel gắn phiên và hàng việc runtime, không tái phát khi nhập",
            "loi_tai_lieu.ban_giao_engine":"Biên nhận chống lặp theo lease/lần thử engine; kết quả nghiệp vụ ở ket_qua_xu_ly",
            "loi.trang_chu_module":"Cấu hình hiển thị ô module và đường dẫn tại runtime đích",
            "loi.ai_chay_thu":"dữ liệu chạy thử DEMO tạm, có hàm dọn, không thuộc dữ liệu công ty"
        }'::jsonb
    $loai_tru$;
    REVOKE ALL ON FUNCTION loi.xuat_loai_tru() FROM PUBLIC;

    CREATE TABLE loi.ai_chay_thu (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        phap_nhan_id uuid NOT NULL REFERENCES loi.phap_nhan(id),
        ma_module text NOT NULL CHECK (ma_module ~ '^[a-z][a-z0-9_]{0,30}$' AND ma_module<>'core'),
        ma_function text NOT NULL CHECK (ma_function ~ '^[a-z][a-z0-9_]{0,127}$'),
        dau_vao jsonb NOT NULL CHECK (
            jsonb_typeof(dau_vao)='object'
            AND dau_vao ?& ARRAY['tai_lieu','cau_hoi','phien_ban_module','ma_bam_goi','ma_prompt','phien_ban_prompt']
            AND dau_vao - ARRAY['tai_lieu','cau_hoi','phien_ban_module','ma_bam_goi','ma_prompt','phien_ban_prompt']='{}'::jsonb
            AND jsonb_typeof(dau_vao->'tai_lieu')='string' AND length(btrim(dau_vao->>'tai_lieu'))>0
            AND length(dau_vao->>'tai_lieu')<=20000
            AND jsonb_typeof(dau_vao->'cau_hoi')='string' AND length(btrim(dau_vao->>'cau_hoi'))>0
            AND length(dau_vao->>'cau_hoi')<=2000
            AND jsonb_typeof(dau_vao->'phien_ban_module')='string' AND length(dau_vao->>'phien_ban_module') BETWEEN 1 AND 64
            AND jsonb_typeof(dau_vao->'ma_bam_goi')='string' AND dau_vao->>'ma_bam_goi' ~ '^[0-9a-f]{64}$'
            AND jsonb_typeof(dau_vao->'ma_prompt')='string' AND dau_vao->>'ma_prompt' ~ '^[a-z][a-z0-9_]{0,127}$'
            AND jsonb_typeof(dau_vao->'phien_ban_prompt')='string' AND dau_vao->>'phien_ban_prompt' ~ '^[1-9][0-9]{0,9}$'
            AND octet_length(dau_vao::text)<=150000),
        trang_thai text NOT NULL DEFAULT 'dang_cho' CHECK (trang_thai IN ('dang_cho','dang_chay','xong','loi')),
        ket_qua jsonb CHECK (ket_qua IS NULL OR (
            jsonb_typeof(ket_qua)='object'
            AND ket_qua ?& ARRAY['tra_loi','model','ly_do_chon','loi']
            AND ket_qua - ARRAY['tra_loi','model','ly_do_chon','loi']='{}'::jsonb
            AND jsonb_typeof(ket_qua->'tra_loi')='string' AND length(ket_qua->>'tra_loi')<=20000
            AND jsonb_typeof(ket_qua->'model')='string' AND length(ket_qua->>'model')<=128
            AND jsonb_typeof(ket_qua->'ly_do_chon')='string' AND length(ket_qua->>'ly_do_chon')<=255
            AND (ket_qua->'loi'='null'::jsonb OR (
                jsonb_typeof(ket_qua->'loi')='object'
                AND (ket_qua->'loi') ?& ARRAY['thong_diep_viet','ma_ho_tro']
                AND (ket_qua->'loi') - ARRAY['thong_diep_viet','ma_ho_tro']='{}'::jsonb
                AND jsonb_typeof(ket_qua->'loi'->'thong_diep_viet')='string'
                AND length(ket_qua->'loi'->>'thong_diep_viet') BETWEEN 1 AND 500
                AND jsonb_typeof(ket_qua->'loi'->'ma_ho_tro')='string'
                AND ket_qua->'loi'->>'ma_ho_tro' ~ '^[A-Z][A-Z0-9_]{0,79}$'))
            AND octet_length(ket_qua::text)<=150000)),
        tao_luc timestamptz NOT NULL DEFAULT clock_timestamp(),
        bat_dau timestamptz,
        ket_thuc timestamptz,
        tao_boi uuid NOT NULL REFERENCES loi.nguoi_dung(id),
        CHECK ((trang_thai IN ('xong','loi'))=(ket_qua IS NOT NULL AND ket_thuc IS NOT NULL)),
        CHECK ((trang_thai='dang_cho')=(bat_dau IS NULL)),
        CHECK (ket_qua IS NULL OR (trang_thai='xong' AND ket_qua->'loi'='null'::jsonb)
            OR (trang_thai='loi' AND jsonb_typeof(ket_qua->'loi')='object'))
    );
    CREATE INDEX ai_chay_thu_lich_su ON loi.ai_chay_thu(phap_nhan_id,tao_luc DESC,id DESC);
    ALTER TABLE loi.ai_chay_thu ENABLE ROW LEVEL SECURITY;
    ALTER TABLE loi.ai_chay_thu FORCE ROW LEVEL SECURITY;
    EXECUTE format('CREATE POLICY ai_thu_chu ON loi.ai_chay_thu TO %I USING(true) WITH CHECK(true)',chu);
    CREATE POLICY ai_thu_phien ON loi.ai_chay_thu FOR SELECT TO PUBLIC USING (
        EXISTS (SELECT FROM loi.mtq_phien_rls() x WHERE x.phap_nhan_id=ai_chay_thu.phap_nhan_id
            AND current_setting('ktt.module',true)='core'
            AND EXISTS (SELECT FROM loi.mtq_admin a WHERE a.nguoi_dung_id=x.nguoi_dung_id AND a.thu_hoi_luc IS NULL)));
    EXECUTE format('REVOKE ALL ON loi.ai_chay_thu FROM PUBLIC,%I,%I,%I',
        tt||'dang_nhap_loi',tt||'vai_chay_loi',tt||'dang_nhap_cai_dat');

    CREATE FUNCTION loi.ai_chay_thu_demo(p_pn uuid) RETURNS void
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    BEGIN
        PERFORM loi.viec_chi_core();
        -- Cùng khóa đổi cờ DEMO ở 023; giữ cờ ổn định tới commit.
        PERFORM pg_advisory_xact_lock_shared(hashtextextended('demo|'||p_pn::text,23));
        IF p_pn IS NULL OR NOT EXISTS (SELECT FROM loi.phap_nhan p WHERE p.id=p_pn AND p.la_demo) THEN
            RAISE EXCEPTION 'AI_THU_DEMO' USING ERRCODE='42501';
        END IF;
    END;
    $ham$;
    CREATE FUNCTION loi.ai_chay_thu_quyen(p_ma text,p_nguoi uuid,p_pn uuid) RETURNS void
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE actor uuid;
    BEGIN
        PERFORM loi.viec_chi_core();
        PERFORM pg_advisory_xact_lock_shared(742601,1);
        SELECT x.nguoi_dung_id INTO actor FROM loi.xac_minh_phien(
            p_ma,'core',p_pn,'CORE:ENGINE:CAU_HINH',NULL,NULL) x;
        IF actor IS NULL OR actor IS DISTINCT FROM p_nguoi OR NOT EXISTS (
            SELECT FROM loi.phien_xac_thuc p WHERE p.ma_bam=sha256(convert_to(p_ma,'UTF8')) AND p.loai='NGUOI_DUNG') THEN
            RAISE EXCEPTION 'AI_THU_PHIEN' USING ERRCODE='42501';
        END IF;
        IF NOT EXISTS (SELECT FROM loi.mtq_admin a WHERE a.nguoi_dung_id=actor AND a.thu_hoi_luc IS NULL) THEN
            RAISE EXCEPTION 'AI_THU_ADMIN' USING ERRCODE='42501';
        END IF;
        PERFORM loi.ai_chay_thu_demo(p_pn);
    END;
    $ham$;

    -- Mở đúng một loại việc Core trong CẢ HAI overload 16/18 tham số của 082.
    -- Không đổi OID/ACL, không chép lại cơ chế MTQ/lease/biên nhận hiện có.
    FOREACH ck IN ARRAY ARRAY[
        'loi.viec_tao(text,text,uuid,text,text,integer,text,text,uuid,text,boolean,boolean,integer,integer,integer,uuid)',
        'loi.viec_tao(text,text,uuid,text,text,integer,text,text,uuid,text,boolean,boolean,integer,integer,integer,uuid,text,text)'] LOOP
        f := to_regprocedure(ck);
        SELECT prosrc INTO nguon FROM pg_proc WHERE oid=f AND prosecdef AND pg_get_userbyid(proowner)=chu;
        IF nguon IS NULL OR cardinality(string_to_array(nguon,moc))<>2 THEN
            RAISE EXCEPTION 'AI-LAT10a: cửa việc khác mẫu, cần lead';
        END IF;
        -- Cửa 16 tham số luôn từ chối chạy thử: không có capability.
        rang_buoc := 'RAISE EXCEPTION ''VIEC_CHUA_DANG_KY'' USING ERRCODE=''42501'';';
        IF ck LIKE '%,uuid,text,text)' THEN
            rang_buoc := $patch$
                IF p_capability IS DISTINCT FROM 'ai.hoi@1'
                    OR p_ma_contract IS DISTINCT FROM 'tra_loi_ai.v2' OR p_engine IS NULL THEN
                    RAISE EXCEPTION 'VIEC_CHUA_DANG_KY' USING ERRCODE='42501';
                END IF;$patch$;
        END IF;
        moi := replace(nguon,moc,$patch$
            IF p_loai='CHAY_THU_HOI_AI' THEN
                __RANG_BUOC__
                PERFORM loi.ai_chay_thu_quyen(p_ma,
                    (SELECT a.tao_boi FROM loi.ai_chay_thu a WHERE a.id=p_tham_chieu AND a.phap_nhan_id=p_pn),p_pn);
                IF p_bang IS DISTINCT FROM 'loi.ai_chay_thu' THEN
                    RAISE EXCEPTION 'VIEC_CHUA_DANG_KY' USING ERRCODE='42501';
                END IF;
            END IF;
            IF p_loai IS NULL OR p_loai NOT IN ('XUAT_DU_LIEU','CHAY_THU_HOI_AI') OR p_phien_ban IS DISTINCT FROM 1$patch$);
        moi := replace(moi,'__RANG_BUOC__',rang_buoc);
        -- Từng neo một dòng: không phụ thuộc CRLF/LF của thân hàm đã áp.
        FOREACH neo IN ARRAY ARRAY[
            'OR p_hd IS DISTINCT FROM ''CORE:DU_LIEU:LAP'' OR p_contract IS DISTINCT FROM ''1.2''',
            'OR p_engine IS NOT NULL',
            'WHERE module=''core'' AND loai=p_loai AND phien_ban=p_phien_ban AND engine_id IS NULL'] LOOP
            IF cardinality(string_to_array(moi,neo))<>2 THEN
                RAISE EXCEPTION 'AI-LAT10a: nhánh Core khác mẫu, cần lead';
            END IF;
        END LOOP;
        moi := replace(moi,'OR p_hd IS DISTINCT FROM ''CORE:DU_LIEU:LAP'' OR p_contract IS DISTINCT FROM ''1.2''',
            $patch$OR p_hd IS DISTINCT FROM 'CORE:DU_LIEU:LAP'
                OR (p_loai='XUAT_DU_LIEU' AND p_contract IS DISTINCT FROM '1.2')
                OR (p_loai='CHAY_THU_HOI_AI' AND p_contract IS DISTINCT FROM '2.0.0')$patch$);
        moi := replace(moi,'OR p_engine IS NOT NULL',
            $patch$OR (p_loai='XUAT_DU_LIEU' AND p_engine IS NOT NULL)
                OR (p_loai='CHAY_THU_HOI_AI' AND p_engine IS NULL)$patch$);
        moi := replace(moi,'WHERE module=''core'' AND loai=p_loai AND phien_ban=p_phien_ban AND engine_id IS NULL',
            'WHERE module=''core'' AND loai=p_loai AND phien_ban=p_phien_ban AND engine_id IS NOT DISTINCT FROM p_engine');
        IF ck LIKE '%,uuid,text,text)' THEN
            -- Chỉ cho thay engine của chạy thử; capability/contract lịch sử vẫn phải khớp.
            neo := 'AND (engine_id,capability,ma_contract,phien_ban_contract)';
            IF cardinality(string_to_array(moi,neo))<>2 THEN
                RAISE EXCEPTION 'AI-LAT10a: cửa binding lịch sử khác mẫu, cần lead';
            END IF;
            moi := replace(moi,neo,$patch$AND NOT (p_module='core' AND p_loai='CHAY_THU_HOI_AI'
                AND p_capability='ai.hoi@1' AND p_ma_contract='tra_loi_ai.v2' AND p_contract='2.0.0'
                AND capability=p_capability AND ma_contract=p_ma_contract AND phien_ban_contract=p_contract)
            AND (engine_id,capability,ma_contract,phien_ban_contract)$patch$);
            neo := 'PERFORM loi.viec_kiem_quyen(v,p_ma,NULL,NULL,true);';
            IF cardinality(string_to_array(moi,neo))<>2 THEN
                RAISE EXCEPTION 'AI-LAT10a: cửa tạo thiếu kiểm quyền, cần lead';
            END IF;
            moi := replace(moi,neo,$patch$
                IF p_module='core' AND p_loai='CHAY_THU_HOI_AI' THEN
                    v.loai := p_loai; v.capability := p_capability; v.ma_contract := p_ma_contract;
                END IF;
                PERFORM loi.viec_kiem_quyen(v,p_ma,NULL,NULL,true);$patch$);
        END IF;
        EXECUTE replace(pg_get_functiondef(f),nguon,moi);
    END LOOP;

    -- Chỉ overload có binding: instance/eid, MTQ, công tắc và lease vẫn do 068/082 kiểm.
    f := 'loi.nhan_viec_engine(text,text,uuid,text,uuid,text,integer,text,integer,text,uuid,text,text)'::regprocedure;
    SELECT prosrc INTO nguon FROM pg_proc WHERE oid=f AND prosecdef AND pg_get_userbyid(proowner)=chu;
    neo := 'AND tao_boi=ai AND hanh_dong=p_hd';
    IF nguon IS NULL OR cardinality(string_to_array(nguon,neo))<>2 THEN
        RAISE EXCEPTION 'AI-LAT10a: cửa nhận engine khác mẫu, cần lead';
    END IF;
    moi := replace(nguon,neo,$patch$AND (tao_boi=ai OR (module='core' AND loai='CHAY_THU_HOI_AI'
        AND capability='ai.hoi@1' AND engine_id=p_engine
        AND ma_contract='tra_loi_ai.v2' AND phien_ban_contract='2.0.0'
        AND EXISTS (SELECT FROM loi.engine_dinh_nghia e WHERE e.id=engine_id AND e.ma='e_hoi_ai')))
        AND hanh_dong=p_hd$patch$);
    -- Xác minh phiên/MTQ kênh ở trên; ủy nhiệm đúng việc theo Admin đã tạo.
    -- Giữ nguyên các cửa xac_minh_phien/viec_giu so danh tính với tao_boi.
    neo := 'phien:=loi.cap_phien(p_ma_moi,ai,p_module,p_pn,session_user::text,pham_vi,den,';
    IF cardinality(string_to_array(moi,neo))<>2 THEN
        RAISE EXCEPTION 'AI-LAT10a: cửa cấp lease engine khác mẫu, cần lead';
    END IF;
    moi := replace(moi,neo,$patch$IF v.module='core' AND v.loai='CHAY_THU_HOI_AI' AND v.phien_ban=1
        AND v.capability='ai.hoi@1' AND v.ma_contract='tra_loi_ai.v2' AND v.phien_ban_contract='2.0.0' THEN
        ai := v.tao_boi;
        pham_vi := ARRAY['CORE:DU_LIEU:LAP'];
    END IF;
    phien:=loi.cap_phien(p_ma_moi,ai,p_module,p_pn,session_user::text,pham_vi,den,$patch$);
    EXECUTE replace(pg_get_functiondef(f),nguon,moi);

    -- MTQ của việc Core vẫn dùng đối tượng hang_viec bản 1.2 ở 052;
    -- 2.0.0 trên hàng việc là bản contract đầu ra của engine, không phải resolver.
    f := 'loi.viec_kiem_quyen(loi.hang_viec,text,uuid,bigint,boolean)'::regprocedure;
    SELECT prosrc INTO nguon FROM pg_proc WHERE oid=f AND prosecdef AND pg_get_userbyid(proowner)=chu;
    FOREACH neo IN ARRAY ARRAY['DECLARE q jsonb;', 'q:=loi.mtq_quyet_dinh_phien(p_ma,v.module,v.phap_nhan_id,v.hanh_dong,',
        'v.phien_ban_contract,''{}'',p_viec,p_the_he);'] LOOP
        IF nguon IS NULL OR cardinality(string_to_array(nguon,neo))<>2 THEN
            RAISE EXCEPTION 'AI-LAT10a: cửa quyền việc khác mẫu, cần lead';
        END IF;
    END LOOP;
    moi := replace(nguon,'DECLARE q jsonb;','DECLARE q jsonb; ban_quyen text;');
    moi := replace(moi,'q:=loi.mtq_quyet_dinh_phien(p_ma,v.module,v.phap_nhan_id,v.hanh_dong,',$patch$
        ban_quyen := v.phien_ban_contract;
        IF v.module='core' AND v.loai='CHAY_THU_HOI_AI' AND v.capability='ai.hoi@1'
            AND v.ma_contract='tra_loi_ai.v2' AND v.phien_ban_contract='2.0.0' THEN
            ban_quyen := '1.2';
        END IF;
        q:=loi.mtq_quyet_dinh_phien(p_ma,v.module,v.phap_nhan_id,v.hanh_dong,$patch$);
    moi := replace(moi,'v.phien_ban_contract,''{}'',p_viec,p_the_he);','ban_quyen,''{}'',p_viec,p_the_he);');
    EXECUTE replace(pg_get_functiondef(f),nguon,moi);

    CREATE FUNCTION loi.ai_chay_thu_xep(p_ma text,p_nguoi uuid,p_pn uuid,p_id uuid,
        p_module text,p_function text,p_dau_vao jsonb) RETURNS uuid
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE cu loi.ai_chay_thu; eid uuid; eid_cu uuid; job_cu loi.hang_viec; can_don integer;
    BEGIN
        PERFORM loi.ai_chay_thu_quyen(p_ma,p_nguoi,p_pn);
        IF p_id IS NULL THEN RAISE EXCEPTION 'AI_THU_DAU_VAO' USING ERRCODE='22023'; END IF;
        PERFORM pg_advisory_xact_lock(hashtextextended('ai_thu|'||p_id::text,129));
        SELECT * INTO cu FROM loi.ai_chay_thu a WHERE a.id=p_id;
        IF FOUND THEN
            IF (cu.phap_nhan_id,cu.tao_boi,cu.ma_module,cu.ma_function,cu.dau_vao)
                IS DISTINCT FROM (p_pn,p_nguoi,p_module,p_function,p_dau_vao) THEN
                RAISE EXCEPTION 'AI_THU_CAS' USING ERRCODE='23505';
            END IF;
            RETURN cu.id;
        END IF;
        -- Nội dung tạm có thể đã dọn; không tạo lượt chờ gắn việc cũ đã xong.
        IF EXISTS (SELECT FROM loi.hang_viec v WHERE v.module='core' AND v.loai='CHAY_THU_HOI_AI'
            AND v.phap_nhan_id=p_pn AND v.tham_chieu_id=p_id) THEN
            RAISE EXCEPTION 'AI_THU_CAS' USING ERRCODE='23505';
        END IF;
        -- Cùng khóa với bộ cài/đổi cấu hình; lấy bản đang kích hoạt, không lấy lịch sử registry.
        PERFORM pg_advisory_xact_lock_shared(hashtextextended('ho_so_chay|e_hoi_ai',40));
        PERFORM pg_advisory_xact_lock(hashtextextended('viec_binding|core|CHAY_THU_HOI_AI|1',80));
        SELECT e.id INTO eid FROM loi.engine_dinh_nghia e
            JOIN loi.engine_ho_so_chay h ON h.engine_id=e.id AND h.het_hieu_luc_luc IS NULL
            JOIN loi.ho_so_chay_engine hc ON hc.engine_id=e.id AND hc.ho_so_mau_id=h.id
            WHERE e.ma='e_hoi_ai' AND hc.ma_engine='e_hoi_ai'
                AND hc.phien_ban_dong=(SELECT max(s.phien_ban_dong) FROM loi.ho_so_chay_engine s
                    WHERE s.ma_engine='e_hoi_ai')
                AND EXISTS (SELECT FROM jsonb_array_elements(e.nang_luc) c WHERE c->>'ma'='ai.hoi@1'
                    AND c->>'dau_vao'='hoi_ai.v2' AND c->>'dau_ra'='tra_loi_ai.v2');
        IF eid IS NULL THEN
            RAISE EXCEPTION 'AI_THU_CHUA_SAN_SANG' USING ERRCODE='55000';
        END IF;
        SELECT d.engine_id INTO eid_cu FROM loi.dang_ky_loai_viec d
            WHERE d.module='core' AND d.loai='CHAY_THU_HOI_AI' AND d.phien_ban=1;
        IF NOT FOUND THEN
            INSERT INTO loi.dang_ky_loai_viec(module,loai,phien_ban,engine_id)
                VALUES ('core','CHAY_THU_HOI_AI',1,eid);
        ELSIF eid_cu IS DISTINCT FROM eid THEN
            UPDATE loi.dang_ky_loai_viec d SET engine_id=eid
                WHERE d.module='core' AND d.loai='CHAY_THU_HOI_AI' AND d.phien_ban=1;
            -- Khóa cả việc và lượt; không kết thúc lease đã nhận nhưng chưa đọc đầu vào.
            FOR job_cu IN SELECT v.* FROM loi.hang_viec v JOIN loi.ai_chay_thu a
                ON a.id=v.tham_chieu_id AND a.phap_nhan_id=v.phap_nhan_id
                JOIN loi.phap_nhan pn ON pn.id=a.phap_nhan_id AND pn.la_demo
                WHERE v.module='core' AND v.loai='CHAY_THU_HOI_AI' AND v.phien_ban=1
                    AND v.engine_id IS DISTINCT FROM eid AND v.trang_thai='CHO'
                    AND a.trang_thai='dang_cho'
                ORDER BY v.id FOR UPDATE OF v,a
            LOOP
                UPDATE loi.ai_chay_thu a SET trang_thai='loi',bat_dau=clock_timestamp(),ket_thuc=clock_timestamp(),
                    ket_qua=jsonb_build_object('tra_loi','','model','','ly_do_chon','','loi',jsonb_build_object(
                        'thong_diep_viet','Engine Hỏi AI vừa được cài lại, cần gửi lượt mới',
                        'ma_ho_tro','AI_THU_ENGINE_CAI_LAI'))
                    WHERE a.id=job_cu.tham_chieu_id AND a.phap_nhan_id=job_cu.phap_nhan_id;
                UPDATE loi.hang_viec v SET trang_thai='LOI',ma_loi='AI_THU_ENGINE_CAI_LAI',
                    ket_thuc_luc=clock_timestamp(),cap_nhat_luc=clock_timestamp(),phien_ban_dong=v.phien_ban_dong+1
                    WHERE v.id=job_cu.id RETURNING v.* INTO job_cu;
                IF job_cu.lan_thu_id IS NOT NULL THEN
                    PERFORM loi.viec_dau(job_cu,'LOI');
                END IF;
            END LOOP;
        END IF;
        -- Tuần tự theo pháp nhân để hai Admin không cùng vượt trần 200.
        PERFORM pg_advisory_xact_lock(hashtextextended('ai_thu_pn|'||p_pn::text,129));
        SELECT greatest(count(*)::integer-199,0) INTO can_don FROM loi.ai_chay_thu a WHERE a.phap_nhan_id=p_pn;
        DELETE FROM loi.ai_chay_thu a WHERE a.id IN (
            SELECT s.id FROM loi.ai_chay_thu s WHERE s.phap_nhan_id=p_pn
                AND NOT EXISTS (SELECT FROM loi.hang_viec v WHERE v.module='core' AND v.phap_nhan_id=p_pn
                    AND v.loai='CHAY_THU_HOI_AI' AND v.tham_chieu_id=s.id AND v.trang_thai IN ('CHO','DANG_CHAY')
                    AND NOT v.yeu_cau_dung AND (v.trang_thai='CHO' OR v.giu_den>clock_timestamp()))
                ORDER BY s.tao_luc,s.id LIMIT can_don);
        IF (SELECT count(*) FROM loi.ai_chay_thu a WHERE a.phap_nhan_id=p_pn)>=200 THEN
            RAISE EXCEPTION 'AI_THU_GIOI_HAN' USING ERRCODE='54000';
        END IF;
        INSERT INTO loi.ai_chay_thu(id,phap_nhan_id,ma_module,ma_function,dau_vao,tao_boi)
            VALUES (p_id,p_pn,p_module,p_function,p_dau_vao,p_nguoi);
        PERFORM loi.viec_tao(p_ma,'core',p_pn,'CORE:DU_LIEU:LAP','CHAY_THU_HOI_AI',1,
            'ai-thu:'||p_id::text,'loi.ai_chay_thu',p_id,'2.0.0',false,true,3,60,1,eid,'ai.hoi@1','tra_loi_ai.v2');
        RETURN p_id;
    END;
    $ham$;

    CREATE FUNCTION loi.ai_chay_thu_dau_vao(p_ma text,p_pn uuid,p_viec uuid,p_instance uuid,p_the_he bigint)
    RETURNS jsonb LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE job loi.hang_viec; luot loi.ai_chay_thu;
    BEGIN
        PERFORM loi.ai_chay_thu_demo(p_pn);
        job := loi.viec_giu(p_ma,'core',p_pn,'CORE:DU_LIEU:LAP',p_viec,p_instance,p_the_he);
        IF job.loai<>'CHAY_THU_HOI_AI' OR job.bang_tham_chieu<>'loi.ai_chay_thu' OR job.yeu_cau_dung
            OR job.capability IS DISTINCT FROM 'ai.hoi@1' OR job.ma_contract IS DISTINCT FROM 'tra_loi_ai.v2'
            OR NOT EXISTS (SELECT FROM loi.engine_phien_chay c JOIN loi.engine_ho_so_chay h ON h.id=c.engine_ho_so_id
                JOIN loi.engine_dinh_nghia e ON e.id=h.engine_id WHERE c.id=p_instance AND e.id=job.engine_id
                AND e.ma='e_hoi_ai' AND c.ket_thuc_luc IS NULL AND c.san_sang_luc IS NOT NULL
                AND c.phien_ban_thuc=e.so_phien_ban AND h.het_hieu_luc_luc IS NULL) THEN
            RAISE EXCEPTION 'VIEC_MAT_LEASE' USING ERRCODE='40001';
        END IF;
        UPDATE loi.ai_chay_thu a SET trang_thai='dang_chay',bat_dau=coalesce(a.bat_dau,clock_timestamp())
            WHERE a.id=job.tham_chieu_id AND a.phap_nhan_id=p_pn AND a.trang_thai IN ('dang_cho','dang_chay')
            RETURNING a.* INTO luot;
        IF NOT FOUND THEN RAISE EXCEPTION 'AI_THU_CAS' USING ERRCODE='40001'; END IF;
        RETURN to_jsonb(luot);
    END;
    $ham$;
    CREATE FUNCTION loi.ai_chay_thu_ghi_ket_qua(p_ma text,p_pn uuid,p_viec uuid,p_instance uuid,p_the_he bigint,
        p_cu text,p_moi text,p_ket_qua jsonb) RETURNS boolean
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE job loi.hang_viec; tt_viec text; kq_id uuid; ma_loi_viec text;
    BEGIN
        PERFORM loi.ai_chay_thu_demo(p_pn);
        job := loi.viec_giu(p_ma,'core',p_pn,'CORE:DU_LIEU:LAP',p_viec,p_instance,p_the_he);
        IF job.loai<>'CHAY_THU_HOI_AI' OR job.bang_tham_chieu<>'loi.ai_chay_thu' OR job.yeu_cau_dung
            OR job.capability IS DISTINCT FROM 'ai.hoi@1' OR job.ma_contract IS DISTINCT FROM 'tra_loi_ai.v2' THEN
            RAISE EXCEPTION 'VIEC_MAT_LEASE' USING ERRCODE='40001';
        END IF;
        IF p_cu IS DISTINCT FROM 'dang_chay' OR p_moi IS NULL OR p_moi NOT IN ('xong','loi') OR p_ket_qua IS NULL THEN
            RAISE EXCEPTION 'AI_THU_DAU_VAO' USING ERRCODE='22023';
        END IF;
        UPDATE loi.ai_chay_thu a SET trang_thai=p_moi,ket_qua=p_ket_qua,ket_thuc=clock_timestamp()
            WHERE a.id=job.tham_chieu_id AND a.phap_nhan_id=p_pn AND a.trang_thai=p_cu;
        IF NOT FOUND THEN RAISE EXCEPTION 'AI_THU_CAS' USING ERRCODE='40001'; END IF;
        tt_viec := 'XONG'; kq_id := job.tham_chieu_id;
        IF p_moi='loi' THEN
            tt_viec := 'LOI'; kq_id := NULL; ma_loi_viec := p_ket_qua->'loi'->>'ma_ho_tro';
        END IF;
        -- Cùng transaction với kết quả; mất lease/commit lỗi rollback cả hai.
        PERFORM loi.viec_ket_thuc(p_ma,'core',p_pn,'CORE:DU_LIEU:LAP',p_viec,p_instance,p_the_he,
            tt_viec,kq_id,ma_loi_viec);
        RETURN true;
    END;
    $ham$;
    CREATE FUNCTION loi.ai_chay_thu_doc(p_ma text,p_nguoi uuid,p_pn uuid,p_id uuid) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE luot loi.ai_chay_thu; job loi.hang_viec; du_lieu jsonb; eid uuid;
    BEGIN
        PERFORM loi.ai_chay_thu_quyen(p_ma,p_nguoi,p_pn);
        SELECT a.* INTO luot FROM loi.ai_chay_thu a WHERE a.id=p_id AND a.phap_nhan_id=p_pn;
        IF NOT FOUND THEN RETURN NULL; END IF;
        du_lieu := to_jsonb(luot)-'dau_vao'-'tao_boi';
        SELECT v.* INTO job FROM loi.hang_viec v WHERE v.module='core' AND v.phap_nhan_id=p_pn
            AND v.loai='CHAY_THU_HOI_AI' AND v.tham_chieu_id=p_id;
        -- Suy trạng thái ngay khi đọc, trước lượt xếp kế tiếp cập nhật binding.
        -- Lease đã nhận vẫn được giữ, kể cả chưa đọc đầu vào.
        IF luot.trang_thai='dang_cho' AND job.trang_thai='CHO' THEN
            SELECT e.id INTO eid FROM loi.engine_dinh_nghia e
                JOIN loi.engine_ho_so_chay h ON h.engine_id=e.id AND h.het_hieu_luc_luc IS NULL
                JOIN loi.ho_so_chay_engine hc ON hc.engine_id=e.id AND hc.ho_so_mau_id=h.id
                WHERE e.ma='e_hoi_ai' AND hc.ma_engine='e_hoi_ai'
                    AND hc.phien_ban_dong=(SELECT max(s.phien_ban_dong) FROM loi.ho_so_chay_engine s
                        WHERE s.ma_engine='e_hoi_ai')
                    AND EXISTS (SELECT FROM jsonb_array_elements(e.nang_luc) c WHERE c->>'ma'='ai.hoi@1'
                        AND c->>'dau_vao'='hoi_ai.v2' AND c->>'dau_ra'='tra_loi_ai.v2');
            IF eid IS NOT NULL AND job.engine_id IS DISTINCT FROM eid THEN
                RETURN du_lieu || jsonb_build_object('trang_thai','loi',
                    'bat_dau',coalesce(luot.bat_dau,luot.tao_luc),'ket_thuc',clock_timestamp(),
                    'ket_qua',jsonb_build_object('tra_loi','','model','','ly_do_chon','','loi',jsonb_build_object(
                        'thong_diep_viet','Engine Hỏi AI vừa được cài lại, cần gửi lượt mới',
                        'ma_ho_tro','AI_THU_ENGINE_CAI_LAI')));
            END IF;
        END IF;
        IF luot.trang_thai IN ('dang_cho','dang_chay') AND (job.id IS NULL
            OR job.trang_thai NOT IN ('CHO','DANG_CHAY') OR job.yeu_cau_dung
            OR (job.trang_thai='DANG_CHAY' AND job.giu_den<=clock_timestamp())) THEN
            du_lieu := du_lieu || jsonb_build_object('trang_thai','loi',
                'bat_dau',coalesce(luot.bat_dau,luot.tao_luc),'ket_thuc',coalesce(job.ket_thuc_luc,clock_timestamp()),
                'ket_qua',jsonb_build_object('tra_loi','','model','','ly_do_chon','','loi',jsonb_build_object(
                    'thong_diep_viet','Lượt chạy thử đã gián đoạn hoặc hết thời gian xử lý. Có thể gửi lượt mới.',
                    'ma_ho_tro','AI_THU_GIAN_DOAN')));
        END IF;
        RETURN du_lieu;
    END;
    $ham$;
    CREATE FUNCTION loi.ai_chay_thu_lich_su(p_ma text,p_nguoi uuid,p_pn uuid,p_gioi_han integer DEFAULT 20) RETURNS jsonb
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    BEGIN
        PERFORM loi.ai_chay_thu_quyen(p_ma,p_nguoi,p_pn);
        IF p_gioi_han IS NULL OR p_gioi_han NOT BETWEEN 1 AND 50 THEN
            RAISE EXCEPTION 'AI_THU_DAU_VAO' USING ERRCODE='22023';
        END IF;
        RETURN coalesce((SELECT jsonb_agg(loi.ai_chay_thu_doc(p_ma,p_nguoi,p_pn,s.id) ORDER BY s.tao_luc DESC,s.id DESC)
            FROM (SELECT a.* FROM loi.ai_chay_thu a WHERE a.phap_nhan_id=p_pn
                ORDER BY a.tao_luc DESC,a.id DESC LIMIT p_gioi_han) s),'[]'::jsonb);
    END;
    $ham$;
    CREATE FUNCTION loi.ai_chay_thu_don(p_ma text,p_nguoi uuid,p_pn uuid,p_cu_hon interval) RETURNS integer
    LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $ham$
    DECLARE so_dong integer;
    BEGIN
        PERFORM loi.ai_chay_thu_quyen(p_ma,p_nguoi,p_pn);
        PERFORM pg_advisory_xact_lock(hashtextextended('ai_thu_pn|'||p_pn::text,129));
        IF p_cu_hon IS NULL OR p_cu_hon<=interval '0 seconds' THEN
            RAISE EXCEPTION 'AI_THU_DAU_VAO' USING ERRCODE='22023';
        END IF;
        -- Giữ việc còn chờ/chạy còn hạn; lượt lỗi/dừng/hết lease đã kết thúc.
        DELETE FROM loi.ai_chay_thu a WHERE a.phap_nhan_id=p_pn
            AND coalesce(a.ket_thuc,a.tao_luc)<clock_timestamp()-p_cu_hon
            AND EXISTS (SELECT FROM loi.phap_nhan p WHERE p.id=a.phap_nhan_id AND p.la_demo)
            AND NOT EXISTS (SELECT FROM loi.hang_viec v WHERE v.module='core' AND v.phap_nhan_id=p_pn
                AND v.loai='CHAY_THU_HOI_AI' AND v.tham_chieu_id=a.id AND v.trang_thai IN ('CHO','DANG_CHAY')
                AND NOT v.yeu_cau_dung AND (v.trang_thai='CHO' OR v.giu_den>clock_timestamp()));
        GET DIAGNOSTICS so_dong=ROW_COUNT;
        RETURN so_dong;
    END;
    $ham$;

    FOREACH ck IN ARRAY ARRAY[
        'loi.ai_chay_thu_demo(uuid)',
        'loi.ai_chay_thu_quyen(text,uuid,uuid)',
        'loi.ai_chay_thu_xep(text,uuid,uuid,uuid,text,text,jsonb)',
        'loi.ai_chay_thu_dau_vao(text,uuid,uuid,uuid,bigint)',
        'loi.ai_chay_thu_ghi_ket_qua(text,uuid,uuid,uuid,bigint,text,text,jsonb)',
        'loi.ai_chay_thu_doc(text,uuid,uuid,uuid)',
        'loi.ai_chay_thu_lich_su(text,uuid,uuid,integer)',
        'loi.ai_chay_thu_don(text,uuid,uuid,interval)'] LOOP
        EXECUTE format('REVOKE ALL ON FUNCTION %s FROM PUBLIC',ck);
        EXECUTE format('GRANT EXECUTE ON FUNCTION %s TO %I',ck,tt||'dang_nhap_loi');
    END LOOP;
    PERFORM set_config('search_path',path_cu,true);
    PERFORM set_config('role',vai_cu,true);
END;
$migration$;
