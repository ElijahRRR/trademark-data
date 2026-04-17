-- ============================================================
-- 沃尔玛合规审核流水线 schema (Phase A-2a)
-- 建立在现有 uspto DB 之上, 依赖 pg_trgm + vector 扩展
-- ============================================================

-- ------------------------------------------------------------
-- 1. 历史违规 (从飞书日报表导入)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS walmart_suspension_history (
    id                  BIGSERIAL PRIMARY KEY,
    shop                TEXT,                   -- 店铺名 (A085朱丽霖)
    amazon_asin         TEXT,                   -- B01LY7WL4E (B 列)
    walmart_sku         TEXT,                   -- 5HDPCC9TOFZ9 (C 列)
    feed_id             TEXT,                   -- 沃尔玛 feedId (O 列)
    title               TEXT,                   -- 原始标题 (D 列, 可能含 $$ProductType)
    title_clean         TEXT,                   -- 去除 $$ 后缀
    product_type        TEXT,                   -- 沃尔玛 ProductType (G 列)
    price               NUMERIC(10,2),          -- J 列
    status              TEXT,                   -- UNPUBLISHED / SYSTEM_PROBLEM (H 列)
    status2             TEXT,                   -- ACTIVE / RETIRED (I 列)
    reason_raw          TEXT,                   -- M 列原始富文本拼接
    reason_category     TEXT,                   -- prohibited_generic / weapons_melee / auto_motor /
                                                -- pricing / tax_code / end_date / internal_flag /
                                                -- ip / offensive / no_price / other
    reason_subcategory  TEXT,                   -- knives_melee / gas_can_epa / obd2_bypass / ...
    is_deleted          BOOLEAN DEFAULT FALSE,  -- 从 eGjQRX 监管合规删除 交叉验证
    source_sheet_id     TEXT,                   -- RzUg8 / 3lHctO / ...
    source_date         DATE,                   -- 数据日期
    flagged_at          TIMESTAMPTZ,            -- N 列时间
    imported_at         TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (walmart_sku, source_date)
);

CREATE INDEX IF NOT EXISTS idx_wsh_asin ON walmart_suspension_history(amazon_asin);
CREATE INDEX IF NOT EXISTS idx_wsh_reason ON walmart_suspension_history(reason_category);
CREATE INDEX IF NOT EXISTS idx_wsh_ptype ON walmart_suspension_history(product_type);
CREATE INDEX IF NOT EXISTS idx_wsh_title_trgm ON walmart_suspension_history USING gin (title_clean gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_wsh_date ON walmart_suspension_history(source_date);
CREATE INDEX IF NOT EXISTS idx_wsh_deleted ON walmart_suspension_history(is_deleted);

-- ------------------------------------------------------------
-- 2. 历史违规文本嵌入 (相似度召回用)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS walmart_suspension_embeddings (
    history_id          BIGINT PRIMARY KEY REFERENCES walmart_suspension_history(id) ON DELETE CASCADE,
    text_embedding      vector(1024),           -- 通义 text-embedding-v3
    embedding_model     TEXT DEFAULT 'qwen-text-embedding-v3',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
-- HNSW index 在嵌入填充后创建:
-- CREATE INDEX idx_wse_vec ON walmart_suspension_embeddings USING hnsw (text_embedding vector_cosine_ops);

-- ------------------------------------------------------------
-- 3. 沃尔玛 ProductType 字典 (统计历史风险)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS walmart_product_types (
    product_type        TEXT PRIMARY KEY,
    sample_count        INTEGER DEFAULT 0,      -- 历史出现次数
    suspend_count       INTEGER DEFAULT 0,      -- 其中被暂停的数量
    suspend_rate        NUMERIC(5,4),           -- 暂停率 = suspend/sample
    dominant_reason     TEXT,                   -- 该 ProductType 最常见的违规原因
    is_risky            BOOLEAN DEFAULT FALSE,  -- suspend_rate > 阈值 标记高风险
    notes               TEXT,                   -- 人工注释 (如 "易被武器误判")
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 4. Amazon 类目 → Walmart ProductType 映射 (防错类型首选)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS amazon_walmart_category_map (
    id                  BIGSERIAL PRIMARY KEY,
    amazon_root_id      TEXT,                   -- Amazon root id (1055398)
    amazon_path         TEXT,                   -- Home & Kitchen > Seasonal Décor > ...
    walmart_product_type TEXT,                  -- 推荐 Walmart ProductType
    confidence          NUMERIC(3,2),           -- 0-1
    history_suspend_rate NUMERIC(5,4),          -- 该路径历史暂停率
    history_sample_count INTEGER DEFAULT 0,
    source              TEXT,                   -- observed / manual / llm
    is_safe             BOOLEAN DEFAULT FALSE,  -- 是否认为"搬运安全"
    notes               TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (amazon_path, walmart_product_type)
);
CREATE INDEX IF NOT EXISTS idx_awm_amazon ON amazon_walmart_category_map(amazon_path);
CREATE INDEX IF NOT EXISTS idx_awm_root ON amazon_walmart_category_map(amazon_root_id);

-- ------------------------------------------------------------
-- 5. 类目白名单 (允许搬运的类目路径)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS safe_category_whitelist (
    id                  BIGSERIAL PRIMARY KEY,
    amazon_path_prefix  TEXT UNIQUE,            -- 前缀匹配, 如 "Home & Kitchen > Seasonal Décor"
    recommended_walmart_type TEXT,
    shop_focus          BOOLEAN DEFAULT FALSE,  -- 是否你们主播类目
    ip_risk_level       TEXT,                   -- low / medium / high
    cert_required       TEXT,                   -- none / CPC / GCC / FDA / FCC / FinCEN / EPA
    allowed             BOOLEAN DEFAULT TRUE,   -- 白名单默认 true; 黑名单用 false
    sub_risks           TEXT[],                 -- 子风险标记 (如 '{religion,cartoon_ip}')
    notes               TEXT
);

-- ------------------------------------------------------------
-- 6. 冒犯词库 (双语, 从政策 + 历史反推)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS offensive_lexicon (
    id                  BIGSERIAL PRIMARY KEY,
    term                TEXT,                   -- 单词或短语
    term_normalized     TEXT,                   -- 小写化去重 key
    language            TEXT,                   -- en / zh
    category            TEXT,                   -- religion / race / politics / sexual /
                                                -- violence / drug / weapon / hate / self_defense
    severity            TEXT,                   -- hard_block / warn / context_dependent
    notes               TEXT,
    UNIQUE (term_normalized, category)
);
CREATE INDEX IF NOT EXISTS idx_offensive_cat ON offensive_lexicon(category);
CREATE INDEX IF NOT EXISTS idx_offensive_term ON offensive_lexicon(term_normalized);

-- ------------------------------------------------------------
-- 7. IP 触发词库
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ip_trigger_terms (
    id                  BIGSERIAL PRIMARY KEY,
    pattern             TEXT UNIQUE,            -- 关键词或正则
    pattern_type        TEXT,                   -- keyword / regex / prefix
    trigger_category    TEXT,                   -- compat_word / known_brand / cartoon_ip /
                                                -- sports_team / celebrity / luxury_brand
    severity            TEXT,                   -- hard_block / warn
    notes               TEXT
);
CREATE INDEX IF NOT EXISTS idx_ipt_cat ON ip_trigger_terms(trigger_category);

-- ------------------------------------------------------------
-- 8. 产品采集 stage 表 (batch xlsx 标准化)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products_stage (
    id                  BIGSERIAL PRIMARY KEY,
    batch_file          TEXT,                   -- batch_20260417_032822.xlsx
    asin                TEXT,
    title               TEXT,
    brand               TEXT,
    product_type        TEXT,                   -- Amazon 商品类型字段
    manufacturer        TEXT,
    model_number        TEXT,
    part_number         TEXT,
    origin_country      TEXT,
    bullet_points       TEXT,                   -- 五点描述 (\n 分隔)
    long_description    TEXT,                   -- 长描述
    image_urls          TEXT,                   -- 图片 URL 列表 (\n 分隔)
    upc                 TEXT,
    ean                 TEXT,
    root_category_id    TEXT,                   -- Amazon root id (1055398)
    category_chain_ids  TEXT,                   -- 1055398,13679381,13679411,...
    category_path       TEXT,                   -- 'Home & Kitchen > Seasonal Décor > ...'
    price               NUMERIC(10,2),
    bsr                 TEXT,                   -- 畅销排名原文
    is_fba              BOOLEAN,
    raw_data            JSONB,                  -- 原始行
    collected_at        TIMESTAMPTZ,
    imported_at         TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (batch_file, asin)
);
CREATE INDEX IF NOT EXISTS idx_ps_asin ON products_stage(asin);
CREATE INDEX IF NOT EXISTS idx_ps_brand_trgm ON products_stage USING gin (brand gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_ps_title_trgm ON products_stage USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_ps_root_cat ON products_stage(root_category_id);

-- ------------------------------------------------------------
-- 9. 产品嵌入 (用于历史违规召回)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products_embeddings (
    stage_id            BIGINT PRIMARY KEY REFERENCES products_stage(id) ON DELETE CASCADE,
    text_embedding      vector(1024),
    embedding_model     TEXT DEFAULT 'qwen-text-embedding-v3',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 10. 审核主决策
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_audits (
    id                  BIGSERIAL PRIMARY KEY,
    stage_id            BIGINT REFERENCES products_stage(id) ON DELETE CASCADE,
    asin                TEXT,
    batch_file          TEXT,
    verdict             TEXT,                   -- approve / hold_manual / reject
    ip_risk             INTEGER,                -- 0-100
    offensive_risk      INTEGER,
    regulatory_risk     INTEGER,
    counterfeit_risk    INTEGER,
    overall_risk        INTEGER,
    reason_summary      TEXT,                   -- 中文汇总 (给运营看)
    recommended_walmart_product_type TEXT,      -- 反向建议: 应该选哪个 ProductType
    l1_triggered        BOOLEAN DEFAULT FALSE,
    l2_triggered        BOOLEAN DEFAULT FALSE,
    l2_vision_triggered BOOLEAN DEFAULT FALSE,
    llm_raw_response    JSONB,
    audited_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (stage_id)
);
CREATE INDEX IF NOT EXISTS idx_pa_verdict ON product_audits(verdict);
CREATE INDEX IF NOT EXISTS idx_pa_asin ON product_audits(asin);
CREATE INDEX IF NOT EXISTS idx_pa_batch ON product_audits(batch_file);

-- ------------------------------------------------------------
-- 11. 细粒度审核标签 (多对一)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audit_flags (
    id                  BIGSERIAL PRIMARY KEY,
    audit_id            BIGINT REFERENCES product_audits(id) ON DELETE CASCADE,
    flag_type           TEXT,                   -- rule_hit / llm_finding / vision_finding /
                                                -- historical_recall / ptype_mismatch
    flag_category       TEXT,                   -- ip / offensive / regulatory / product_type /
                                                -- counterfeit / pricing / cert_missing
    flag_code           TEXT,                   -- 具体代码
    description         TEXT,                   -- 人类可读原因
    severity            TEXT,                   -- hard_block / warn / info
    evidence            JSONB                   -- 触发证据 (撞名商标, 历史相似 SKU 等)
);
CREATE INDEX IF NOT EXISTS idx_af_audit ON audit_flags(audit_id);
CREATE INDEX IF NOT EXISTS idx_af_category ON audit_flags(flag_category);
CREATE INDEX IF NOT EXISTS idx_af_code ON audit_flags(flag_code);
