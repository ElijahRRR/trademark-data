-- USPTO Trademark & Patent Database Schema
-- Target: PostgreSQL 17

-- Extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- trigram fuzzy matching

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
-- PATENTS (File Wrapper)
---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS patents (
    application_number TEXT PRIMARY KEY,
    invention_title TEXT,
    filing_date     DATE,
    effective_filing_date DATE,
    application_type TEXT,               -- UTL, DES, PLT, PPA, etc
    application_type_label TEXT,         -- Utility, Design, Plant, etc
    application_status_code TEXT,
    application_status_desc TEXT,
    application_status_date DATE,
    group_art_unit  TEXT,
    class           TEXT,                -- USPC class
    subclass        TEXT,
    customer_number INTEGER,
    docket_number   TEXT,
    first_inventor_name TEXT,
    first_applicant_name TEXT,
    entity_status   TEXT,                -- Small, Micro, Regular
    small_entity    BOOLEAN DEFAULT FALSE,
    national_stage  BOOLEAN DEFAULT FALSE,
    is_design_patent BOOLEAN DEFAULT FALSE,
    -- source tracking
    source_file     TEXT,                -- which year JSON
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Patent inventors
CREATE TABLE IF NOT EXISTS patent_inventors (
    id              BIGSERIAL PRIMARY KEY,
    application_number TEXT NOT NULL REFERENCES patents(application_number),
    first_name      TEXT,
    last_name       TEXT,
    full_name       TEXT,
    city            TEXT,
    country_code    TEXT
);

-- Patent applicants (may differ from inventors)
CREATE TABLE IF NOT EXISTS patent_applicants (
    id              BIGSERIAL PRIMARY KEY,
    application_number TEXT NOT NULL REFERENCES patents(application_number),
    applicant_name  TEXT,
    city            TEXT,
    country_code    TEXT
);

-- Patent correspondence address
CREATE TABLE IF NOT EXISTS patent_correspondence (
    id              BIGSERIAL PRIMARY KEY,
    application_number TEXT NOT NULL REFERENCES patents(application_number),
    name            TEXT,
    address_line1   TEXT,
    city            TEXT,
    region_code     TEXT,
    postal_code     TEXT,
    country_code    TEXT
);

-- Patent events (prosecution history)
CREATE TABLE IF NOT EXISTS patent_events (
    id              BIGSERIAL PRIMARY KEY,
    application_number TEXT NOT NULL REFERENCES patents(application_number),
    event_code      TEXT,
    event_date      DATE,
    event_description TEXT
);

-- Patent publication info
CREATE TABLE IF NOT EXISTS patent_publications (
    id              BIGSERIAL PRIMARY KEY,
    application_number TEXT NOT NULL REFERENCES patents(application_number),
    publication_category TEXT
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

-- Patent lookup
CREATE INDEX IF NOT EXISTS idx_patents_title_trgm
    ON patents USING gin (invention_title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_patents_type
    ON patents(application_type);
CREATE INDEX IF NOT EXISTS idx_patents_design
    ON patents(is_design_patent) WHERE is_design_patent = TRUE;
CREATE INDEX IF NOT EXISTS idx_patents_filing_date
    ON patents(filing_date);
CREATE INDEX IF NOT EXISTS idx_patents_status
    ON patents(application_status_code);

-- Patent relations
CREATE INDEX IF NOT EXISTS idx_pat_inventors_appnum
    ON patent_inventors(application_number);
CREATE INDEX IF NOT EXISTS idx_pat_applicants_appnum
    ON patent_applicants(application_number);
CREATE INDEX IF NOT EXISTS idx_pat_events_appnum
    ON patent_events(application_number);

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
