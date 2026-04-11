-- USPTO Trademark & Patent Database Schema
-- Target: PostgreSQL 17

-- Extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- trigram fuzzy matching
CREATE EXTENSION IF NOT EXISTS vector;   -- pgvector for CLIP embeddings

---------------------------------------------------------------------
-- TRADEMARKS
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trademarks (
    serial_number   BIGINT PRIMARY KEY,
    registration_number TEXT,
    mark_identification TEXT,           -- brand name
    status_code     TEXT,
    status_date     DATE,
    filing_date     DATE,
    registration_date DATE,
    cancellation_date DATE,
    abandonment_date DATE,
    mark_drawing_code TEXT,             -- 0-6 (word/design/etc)
    attorney_name   TEXT,
    -- mark type flags
    is_trademark    BOOLEAN DEFAULT FALSE,
    is_service_mark BOOLEAN DEFAULT FALSE,
    is_collective   BOOLEAN DEFAULT FALSE,
    is_certification BOOLEAN DEFAULT FALSE,
    -- filing basis
    is_intent_to_use BOOLEAN DEFAULT FALSE,
    is_use_based    BOOLEAN DEFAULT FALSE,
    is_44d          BOOLEAN DEFAULT FALSE,
    is_44e          BOOLEAN DEFAULT FALSE,
    is_66a          BOOLEAN DEFAULT FALSE,
    -- design features
    standard_characters BOOLEAN DEFAULT FALSE,
    color_drawing   BOOLEAN DEFAULT FALSE,
    drawing_3d      BOOLEAN DEFAULT FALSE,
    -- renewal/maintenance
    renewal_filed   BOOLEAN DEFAULT FALSE,
    section_8_accepted BOOLEAN DEFAULT FALSE,
    section_15_acknowledged BOOLEAN DEFAULT FALSE,
    -- source tracking
    source_file     TEXT,               -- which zip it came from
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Goods and services per class
CREATE TABLE IF NOT EXISTS trademark_classes (
    id              BIGSERIAL PRIMARY KEY,
    serial_number   BIGINT NOT NULL REFERENCES trademarks(serial_number),
    international_code TEXT,            -- Nice classification code
    us_code         TEXT,
    status_code     TEXT,
    first_use_date  DATE,
    first_use_commerce_date DATE
);

-- Goods/services description & disclaimers
CREATE TABLE IF NOT EXISTS trademark_statements (
    id              BIGSERIAL PRIMARY KEY,
    serial_number   BIGINT NOT NULL REFERENCES trademarks(serial_number),
    type_code       TEXT NOT NULL,       -- GS=goods/services, DS=disclaimer, PM=pseudo-mark, etc
    text            TEXT
);

-- Owners
CREATE TABLE IF NOT EXISTS trademark_owners (
    id              BIGSERIAL PRIMARY KEY,
    serial_number   BIGINT NOT NULL REFERENCES trademarks(serial_number),
    entry_number    TEXT,
    party_type      TEXT,                -- owner type code
    party_name      TEXT,
    entity_type     TEXT,                -- corporation, individual, etc
    nationality_state TEXT,
    nationality_country TEXT
);

-- Design search codes (image-based marks)
CREATE TABLE IF NOT EXISTS trademark_design_codes (
    id              BIGSERIAL PRIMARY KEY,
    serial_number   BIGINT NOT NULL REFERENCES trademarks(serial_number),
    design_code     TEXT NOT NULL
);

---------------------------------------------------------------------
-- PATENT GRANTS (PTGRDT Red Book)
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patent_grants (
    patent_number       TEXT PRIMARY KEY,    -- D1034980, 12034149
    kind                TEXT,                -- S1 (design), B1/B2 (utility)
    application_number  TEXT,                -- 29749819
    appl_type           TEXT,                -- design, utility, plant, reissue
    title               TEXT,
    grant_date          DATE,
    filing_date         DATE,
    abstract            TEXT,                -- UTIL only, DESIGN typically NULL
    num_claims          INTEGER,
    num_figures         INTEGER,
    num_drawing_sheets  INTEGER,
    term_years          INTEGER,             -- DESIGN: 15
    term_extension_days INTEGER,             -- UTIL: PTA days
    source_tar          TEXT,                -- e.g. I20240709.tar
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Patent assignees (rights holders / companies)
CREATE TABLE IF NOT EXISTS patent_grant_assignees (
    id              BIGSERIAL PRIMARY KEY,
    patent_number   TEXT NOT NULL REFERENCES patent_grants(patent_number),
    orgname         TEXT,                    -- company name
    first_name      TEXT,                    -- individual assignee
    last_name       TEXT,
    city            TEXT,
    state           TEXT,
    country         TEXT
);

-- Patent inventors
CREATE TABLE IF NOT EXISTS patent_grant_inventors (
    id              BIGSERIAL PRIMARY KEY,
    patent_number   TEXT NOT NULL REFERENCES patent_grants(patent_number),
    first_name      TEXT,
    last_name       TEXT,
    city            TEXT,
    state           TEXT,
    country         TEXT
);

-- Patent classifications (CPC, Locarno, USPC)
CREATE TABLE IF NOT EXISTS patent_grant_classifications (
    id              BIGSERIAL PRIMARY KEY,
    patent_number   TEXT NOT NULL REFERENCES patent_grants(patent_number),
    system          TEXT NOT NULL,           -- 'cpc', 'locarno', 'uspc'
    code            TEXT NOT NULL,           -- H01M 4/364, 2402, D24135
    is_main         BOOLEAN DEFAULT FALSE
);

-- Patent citations
CREATE TABLE IF NOT EXISTS patent_grant_citations (
    id              BIGSERIAL PRIMARY KEY,
    patent_number   TEXT NOT NULL REFERENCES patent_grants(patent_number),
    cited_doc_number TEXT,
    cited_country   TEXT,
    cited_kind      TEXT,
    category        TEXT                     -- 'cited by applicant', 'cited by examiner'
);

-- Patent images (DESIGN only, stores file path + CLIP embedding)
CREATE TABLE IF NOT EXISTS patent_grant_images (
    id              BIGSERIAL PRIMARY KEY,
    patent_number   TEXT NOT NULL REFERENCES patent_grants(patent_number),
    image_name      TEXT NOT NULL,           -- D00001.TIF
    image_path      TEXT NOT NULL,           -- design_images/D1034980/D00001.TIF
    embedding       vector(512)              -- CLIP ViT-B/32, filled later
);

---------------------------------------------------------------------
-- ETL TRACKING
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS etl_progress (
    id              BIGSERIAL PRIMARY KEY,
    data_type       TEXT NOT NULL,       -- 'trademark' or 'patent'
    source_file     TEXT NOT NULL,       -- zip or json filename
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending/running/completed/failed
    records_total   INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_skipped INTEGER DEFAULT 0,
    records_errored INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error_message   TEXT,
    UNIQUE(data_type, source_file)
);

CREATE TABLE IF NOT EXISTS etl_errors (
    id              BIGSERIAL PRIMARY KEY,
    data_type       TEXT NOT NULL,
    source_file     TEXT NOT NULL,
    record_id       TEXT,                -- serial_number or application_number
    error_type      TEXT,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

---------------------------------------------------------------------
-- INDEXES for query performance
---------------------------------------------------------------------
-- Trademark text search (trigram)
CREATE INDEX IF NOT EXISTS idx_trademarks_mark_trgm
    ON trademarks USING gin (mark_identification gin_trgm_ops);

-- Trademark lookup
CREATE INDEX IF NOT EXISTS idx_trademarks_reg_number
    ON trademarks(registration_number);
CREATE INDEX IF NOT EXISTS idx_trademarks_status
    ON trademarks(status_code);
CREATE INDEX IF NOT EXISTS idx_trademarks_filing_date
    ON trademarks(filing_date);

-- Trademark relations
CREATE INDEX IF NOT EXISTS idx_tm_classes_serial
    ON trademark_classes(serial_number);
CREATE INDEX IF NOT EXISTS idx_tm_statements_serial
    ON trademark_statements(serial_number);
CREATE INDEX IF NOT EXISTS idx_tm_owners_serial
    ON trademark_owners(serial_number);
CREATE INDEX IF NOT EXISTS idx_tm_owners_name_trgm
    ON trademark_owners USING gin (party_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_tm_design_codes_serial
    ON trademark_design_codes(serial_number);

-- Patent grants lookup
CREATE INDEX IF NOT EXISTS idx_pg_title_trgm
    ON patent_grants USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_pg_appl_type
    ON patent_grants(appl_type);
CREATE INDEX IF NOT EXISTS idx_pg_grant_date
    ON patent_grants(grant_date);
CREATE INDEX IF NOT EXISTS idx_pg_app_number
    ON patent_grants(application_number);

-- Patent assignees (key for company/brand lookup)
CREATE INDEX IF NOT EXISTS idx_pga_patent
    ON patent_grant_assignees(patent_number);
CREATE INDEX IF NOT EXISTS idx_pga_orgname_trgm
    ON patent_grant_assignees USING gin (orgname gin_trgm_ops);

-- Patent inventors
CREATE INDEX IF NOT EXISTS idx_pgi_patent
    ON patent_grant_inventors(patent_number);

-- Patent classifications
CREATE INDEX IF NOT EXISTS idx_pgc_patent
    ON patent_grant_classifications(patent_number);
CREATE INDEX IF NOT EXISTS idx_pgc_code
    ON patent_grant_classifications(code);

-- Patent citations
CREATE INDEX IF NOT EXISTS idx_pgcit_patent
    ON patent_grant_citations(patent_number);

-- Patent images + vector similarity search
CREATE INDEX IF NOT EXISTS idx_pgimg_patent
    ON patent_grant_images(patent_number);
-- HNSW index for CLIP vector similarity (created after embeddings are filled)
-- CREATE INDEX IF NOT EXISTS idx_pgimg_embedding
--     ON patent_grant_images USING hnsw (embedding vector_cosine_ops);

-- ETL tracking
CREATE INDEX IF NOT EXISTS idx_etl_progress_lookup
    ON etl_progress(data_type, status);

-- Statement text search for goods/services
CREATE INDEX IF NOT EXISTS idx_tm_statements_text_trgm
    ON trademark_statements USING gin (text gin_trgm_ops);

---------------------------------------------------------------------
-- TRO CASE MATCHING PIPELINE
---------------------------------------------------------------------

-- TRO 案件源数据
CREATE TABLE IF NOT EXISTS tro_cases (
    case_number       TEXT PRIMARY KEY,
    date_filed        DATE,
    nature_of_suit    TEXT,               -- Trademark / Copyright / Patent
    plaintiff_raw     TEXT,
    brand_raw         TEXT,
    plaintiff_clean   TEXT,
    brand_clean       TEXT,
    brand_eq_plaintiff BOOLEAN DEFAULT FALSE
);

-- 去重后的原告名 (Step 2 查询用)
CREATE TABLE IF NOT EXISTS unique_plaintiffs (
    id              SERIAL PRIMARY KEY,
    plaintiff_clean TEXT UNIQUE,
    case_count      INTEGER,
    query_status    TEXT DEFAULT 'pending'  -- pending / exact / fuzzy / miss
);

-- 去重后的品牌名 (Step 2 查询用)
CREATE TABLE IF NOT EXISTS unique_brands (
    id              SERIAL PRIMARY KEY,
    brand_clean     TEXT UNIQUE,
    case_count      INTEGER,
    query_status    TEXT DEFAULT 'pending'
);

-- 路径A结果: 原告名 → trademark_owners
CREATE TABLE IF NOT EXISTS path_a_results (
    id                SERIAL PRIMARY KEY,
    plaintiff_clean   TEXT,
    match_type        TEXT,               -- exact / fuzzy
    serial_number     BIGINT,
    mark_identification TEXT,
    owner_name        TEXT,
    status_code       TEXT,
    live_dead         TEXT
);
CREATE INDEX IF NOT EXISTS idx_path_a_plaintiff ON path_a_results(plaintiff_clean);

-- 路径B结果: 品牌名 → trademarks.mark_identification
CREATE TABLE IF NOT EXISTS path_b_results (
    id                SERIAL PRIMARY KEY,
    brand_clean       TEXT,
    match_type        TEXT,
    serial_number     BIGINT,
    mark_identification TEXT,
    owner_name        TEXT,
    status_code       TEXT,
    live_dead         TEXT
);
CREATE INDEX IF NOT EXISTS idx_path_b_brand ON path_b_results(brand_clean);

-- 匹配汇合结果 (Step 3)
CREATE TABLE IF NOT EXISTS matched_companies (
    id              SERIAL PRIMARY KEY,
    case_number     TEXT,
    plaintiff_clean TEXT,
    brand_clean     TEXT,
    real_company    TEXT,
    match_quality   TEXT,                 -- exact / a_only / a_preferred / b_only / b_uncertain / not_found / ai_high / ai_medium / ai_low
    needs_review    BOOLEAN DEFAULT FALSE,
    review_reason   TEXT
);
CREATE INDEX IF NOT EXISTS idx_matched_case ON matched_companies(case_number);
CREATE INDEX IF NOT EXISTS idx_matched_plaintiff ON matched_companies(plaintiff_clean);
CREATE INDEX IF NOT EXISTS idx_matched_brand ON matched_companies(brand_clean);
CREATE INDEX IF NOT EXISTS idx_matched_company ON matched_companies(real_company);

-- AI 子代理匹配结果
CREATE TABLE IF NOT EXISTS ai_match_results (
    id              SERIAL PRIMARY KEY,
    case_number     TEXT NOT NULL,
    plaintiff_clean TEXT,
    brand_clean     TEXT,
    real_company    TEXT,
    match_quality   TEXT,
    confidence      DOUBLE PRECISION,
    match_reason    TEXT,
    brands_found    TEXT,
    agent_id        INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- 公司品牌明细 (Step 4 输出)
CREATE TABLE IF NOT EXISTS company_brand_details (
    id                  SERIAL PRIMARY KEY,
    real_company        TEXT,
    mark_identification TEXT,
    serial_number       BIGINT,
    registration_number TEXT,
    status_code         TEXT,
    live_dead           TEXT,
    category            TEXT,
    international_code  TEXT,
    international_desc_cn TEXT,
    international_desc_en TEXT,
    goods_services      TEXT,
    first_use_date      DATE
);
CREATE INDEX IF NOT EXISTS idx_cbd_company ON company_brand_details(real_company);

-- Nice 分类中英文对照
CREATE TABLE IF NOT EXISTS nice_classification (
    code    TEXT PRIMARY KEY,
    name_en TEXT,
    name_cn TEXT
);
