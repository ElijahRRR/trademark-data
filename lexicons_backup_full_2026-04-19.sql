--
-- PostgreSQL database dump
--

\restrict WoMVkiXFftYcvg4KbmsZucyBdckxyzAUDU9MfJFtoh6NaPUzqyPgav3hMIpjhpF

-- Dumped from database version 17.9 (Homebrew)
-- Dumped by pg_dump version 17.9 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: ip_trigger_terms; Type: TABLE; Schema: public; Owner: nextderboy
--

CREATE TABLE public.ip_trigger_terms (
    id bigint NOT NULL,
    pattern text,
    pattern_type text,
    trigger_category text,
    severity text,
    notes text
);


ALTER TABLE public.ip_trigger_terms OWNER TO nextderboy;

--
-- Name: ip_trigger_terms_id_seq; Type: SEQUENCE; Schema: public; Owner: nextderboy
--

CREATE SEQUENCE public.ip_trigger_terms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ip_trigger_terms_id_seq OWNER TO nextderboy;

--
-- Name: ip_trigger_terms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nextderboy
--

ALTER SEQUENCE public.ip_trigger_terms_id_seq OWNED BY public.ip_trigger_terms.id;


--
-- Name: offensive_lexicon; Type: TABLE; Schema: public; Owner: nextderboy
--

CREATE TABLE public.offensive_lexicon (
    id bigint NOT NULL,
    term text,
    term_normalized text,
    language text,
    category text,
    severity text,
    notes text
);


ALTER TABLE public.offensive_lexicon OWNER TO nextderboy;

--
-- Name: offensive_lexicon_id_seq; Type: SEQUENCE; Schema: public; Owner: nextderboy
--

CREATE SEQUENCE public.offensive_lexicon_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.offensive_lexicon_id_seq OWNER TO nextderboy;

--
-- Name: offensive_lexicon_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nextderboy
--

ALTER SEQUENCE public.offensive_lexicon_id_seq OWNED BY public.offensive_lexicon.id;


--
-- Name: safe_category_whitelist; Type: TABLE; Schema: public; Owner: nextderboy
--

CREATE TABLE public.safe_category_whitelist (
    id bigint NOT NULL,
    amazon_path_prefix text,
    recommended_walmart_type text,
    shop_focus boolean DEFAULT false,
    ip_risk_level text,
    cert_required text,
    allowed boolean DEFAULT true,
    sub_risks text[],
    notes text
);


ALTER TABLE public.safe_category_whitelist OWNER TO nextderboy;

--
-- Name: safe_category_whitelist_id_seq; Type: SEQUENCE; Schema: public; Owner: nextderboy
--

CREATE SEQUENCE public.safe_category_whitelist_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.safe_category_whitelist_id_seq OWNER TO nextderboy;

--
-- Name: safe_category_whitelist_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nextderboy
--

ALTER SEQUENCE public.safe_category_whitelist_id_seq OWNED BY public.safe_category_whitelist.id;


--
-- Name: ip_trigger_terms id; Type: DEFAULT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.ip_trigger_terms ALTER COLUMN id SET DEFAULT nextval('public.ip_trigger_terms_id_seq'::regclass);


--
-- Name: offensive_lexicon id; Type: DEFAULT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.offensive_lexicon ALTER COLUMN id SET DEFAULT nextval('public.offensive_lexicon_id_seq'::regclass);


--
-- Name: safe_category_whitelist id; Type: DEFAULT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.safe_category_whitelist ALTER COLUMN id SET DEFAULT nextval('public.safe_category_whitelist_id_seq'::regclass);


--
-- Data for Name: ip_trigger_terms; Type: TABLE DATA; Schema: public; Owner: nextderboy
--

INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (1, '(?i)\bfor\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (2, '(?i)\bcompatible\s+with\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (3, '(?i)\bfits\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (4, '(?i)\breplaces?\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (5, '(?i)\breplacement\s+for\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (6, '(?i)\blike\s+([A-Z][A-Za-z0-9&\-]+)\s+(style|brand|quality)', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (7, '(?i)\binspired\s+by\s+([A-Z][A-Za-z0-9&\-]+)', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (8, '(?i)\b([A-Z][A-Za-z0-9&\-]+)\s+style\b', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (9, '(?i)\bOEM\b', 'regex', 'compat_word', 'hard_block', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (10, '(?i)\bgenuine\b', 'regex', 'ip_authenticity', 'warn', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (11, '(?i)\boriginal\b', 'regex', 'ip_authenticity', 'warn', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (12, '(?i)\bauthentic\b', 'regex', 'ip_authenticity', 'warn', '兼容/仿品模式');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (13, 'Louis Vuitton', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (14, 'LV', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (15, 'Gucci', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (16, 'Prada', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (17, 'Hermes', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (18, 'Chanel', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (19, 'Dior', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (20, 'Burberry', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (21, 'Fendi', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (22, 'Balenciaga', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (23, 'Versace', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (24, 'Armani', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (25, 'Cartier', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (26, 'Tiffany', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (27, 'Bulgari', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (28, 'Bvlgari', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (29, 'Rolex', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (30, 'Omega', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (31, 'Patek Philippe', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (32, 'Audemars Piguet', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (33, 'Breitling', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (34, 'IWC', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (35, 'Tag Heuer', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (36, 'Supreme', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (37, 'Off-White', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (38, 'Yeezy', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (39, 'Palace', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (40, 'Bape', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (41, 'Céline', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (42, 'Celine', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (43, 'Givenchy', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (44, 'Saint Laurent', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (45, 'YSL', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (46, 'Valentino', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (47, 'Bottega Veneta', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (48, 'Loewe', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (49, 'Mulberry', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (50, 'Coach', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (51, 'Michael Kors', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (52, 'Kate Spade', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (53, 'Tory Burch', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (54, 'Rimowa', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (55, 'Montblanc', 'keyword', 'luxury_brand', 'hard_block', '奢侈品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (56, 'Nike', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (57, 'Adidas', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (58, 'Puma', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (59, 'Under Armour', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (60, 'Reebok', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (61, 'New Balance', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (62, 'Converse', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (63, 'Vans', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (64, 'Asics', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (65, 'The North Face', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (66, 'Patagonia', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (67, 'Columbia', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (68, 'Lululemon', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (69, 'Jordan', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (71, 'Skechers', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (72, 'Timberland', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (73, 'Dr. Martens', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (74, 'Birkenstock', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (75, 'Fila', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (76, 'Champion', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (77, 'Kappa', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (78, 'Mizuno', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (79, 'Brooks', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (80, 'Hoka', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (81, 'Salomon', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (82, 'Oakley', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (83, 'Ray-Ban', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (84, 'Maui Jim', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (85, 'TaylorMade', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (86, 'Callaway', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (87, 'Titleist', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (88, 'Wilson', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (89, 'Spalding', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (90, 'Fanatics', 'keyword', 'sports_brand', 'hard_block', '运动品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (91, 'Apple', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (92, 'iPhone', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (93, 'iPad', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (94, 'MacBook', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (95, 'AirPods', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (96, 'iMac', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (97, 'iWatch', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (98, 'Mac Mini', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (99, 'Samsung', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (100, 'Galaxy', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (101, 'Google', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (102, 'Pixel', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (103, 'Microsoft', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (104, 'Xbox', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (105, 'PlayStation', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (106, 'Sony', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (107, 'Nintendo', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (108, 'Switch', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (109, 'Amazon', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (110, 'Kindle', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (111, 'Alexa', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (112, 'Echo', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (113, 'Fire TV', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (114, 'Ring', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (115, 'Blink', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (116, 'Dyson', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (117, 'Bose', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (118, 'Beats', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (119, 'GoPro', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (120, 'DJI', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (121, 'Anker', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (122, 'Razer', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (123, 'Logitech', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (124, 'Huawei', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (125, 'Xiaomi', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (126, 'OnePlus', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (127, 'Oppo', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (128, 'Vivo', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (129, 'Redmi', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (130, 'Honor', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (131, 'Garmin', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (132, 'Fitbit', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (133, 'Polar', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (134, 'HP', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (135, 'Dell', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (136, 'Lenovo', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (137, 'ASUS', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (138, 'Acer', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (140, 'Canon', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (141, 'Nikon', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (142, 'Fujifilm', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (143, 'Leica', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (144, 'Intel', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (145, 'AMD', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (146, 'NVIDIA', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (147, 'Qualcomm', 'keyword', 'tech_brand', 'hard_block', '科技品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (148, 'Toyota', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (149, 'Camry', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (150, 'Corolla', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (151, 'RAV4', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (152, 'Tacoma', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (153, 'Tundra', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (154, 'Highlander', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (155, '4Runner', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (156, 'Prius', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (157, 'Sienna', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (158, 'Honda', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (159, 'Civic', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (160, 'Accord', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (161, 'CR-V', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (162, 'CRV', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (163, 'Pilot', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (164, 'Odyssey', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (165, 'Ridgeline', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (166, 'Nissan', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (167, 'Altima', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (168, 'Sentra', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (169, 'Rogue', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (170, 'Pathfinder', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (171, 'Frontier', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (172, 'Titan', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (173, 'Mazda', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (174, 'Mazda3', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (175, 'CX-5', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (176, 'CX-9', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (177, 'MX-5', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (178, 'Miata', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (179, 'Subaru', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (180, 'Outback', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (181, 'Forester', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (182, 'Impreza', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (183, 'WRX', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (184, 'Crosstrek', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (185, 'Hyundai', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (186, 'Elantra', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (187, 'Sonata', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (188, 'Tucson', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (189, 'Santa Fe', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (190, 'Kia', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (191, 'Sorento', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (192, 'Sportage', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (193, 'Telluride', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (194, 'Lexus', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (195, 'Infiniti', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (196, 'Acura', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (197, 'Genesis', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (198, 'Ford', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (199, 'F-150', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (200, 'F150', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (201, 'F-250', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (202, 'F250', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (203, 'Mustang', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (204, 'Explorer', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (205, 'Escape', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (206, 'Ranger', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (207, 'Bronco', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (208, 'Edge', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (209, 'Expedition', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (210, 'Super Duty', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (211, 'Chevrolet', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (212, 'Chevy', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (213, 'Silverado', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (214, 'Equinox', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (215, 'Traverse', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (216, 'Tahoe', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (217, 'Suburban', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (218, 'Camaro', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (219, 'Corvette', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (220, 'Colorado', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (221, 'Impala', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (222, 'Malibu', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (223, 'Blazer', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (224, 'GMC', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (225, 'Sierra', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (226, 'Yukon', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (227, 'Canyon', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (228, 'Acadia', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (229, 'Jeep', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (230, 'Wrangler', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (231, 'Cherokee', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (232, 'Grand Cherokee', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (233, 'Compass', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (234, 'Renegade', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (235, 'Gladiator', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (236, 'Dodge', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (237, 'RAM', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (238, 'Ram 1500', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (239, 'Charger', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (240, 'Challenger', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (241, 'Durango', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (242, 'Chrysler', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (243, 'Pacifica', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (244, '300', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (245, 'Cadillac', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (246, 'Escalade', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (247, 'CTS', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (248, 'ATS', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (249, 'Buick', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (250, 'Lincoln', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (251, 'Navigator', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (252, 'BMW', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (253, 'BMW M3', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (254, 'BMW M5', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (255, 'X3', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (256, 'X5', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (257, 'X7', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (258, 'Mercedes-Benz', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (259, 'Mercedes', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (260, 'Benz', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (261, 'E-Class', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (262, 'S-Class', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (263, 'GLC', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (264, 'GLE', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (265, 'G-Wagon', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (266, 'Audi', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (267, 'A3', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (268, 'A4', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (269, 'A6', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (270, 'Q5', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (271, 'Q7', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (272, 'Porsche', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (273, '911', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (274, 'Cayenne', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (275, 'Macan', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (276, 'Panamera', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (277, 'Volkswagen', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (278, 'VW', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (279, 'Jetta', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (280, 'Passat', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (281, 'Tiguan', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (282, 'Atlas', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (283, 'Golf', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (284, 'Volvo', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (285, 'XC90', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (286, 'XC60', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (287, 'Land Rover', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (288, 'Range Rover', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (289, 'Defender', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (290, 'Jaguar', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (291, 'Mini Cooper', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (292, 'MINI', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (293, 'Tesla', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (294, 'Model 3', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (295, 'Model S', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (296, 'Model X', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (297, 'Model Y', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (298, 'Cybertruck', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (299, 'Rivian', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (300, 'Lucid', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (301, 'Lamborghini', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (302, 'Ferrari', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (303, 'Bugatti', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (304, 'McLaren', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (305, 'Maserati', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (306, 'Rolls-Royce', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (307, 'Rolls Royce', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (308, 'Bentley', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (309, 'Maybach', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (310, 'Aston Martin', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (311, 'Harley-Davidson', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (312, 'Harley Davidson', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (313, 'Harley', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (314, 'Indian Motorcycle', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (315, 'Polaris', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (316, 'Ducati', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (317, 'Kawasaki', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (318, 'Ninja', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (319, 'Yamaha Motor', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (320, 'Suzuki', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (321, 'Triumph Motorcycle', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (322, 'KTM', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (323, 'BMW Motorrad', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (324, 'Moto Guzzi', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (325, 'Aprilia', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (326, 'Peterbilt', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (327, 'Kenworth', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (328, 'Freightliner', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (329, 'Volvo Truck', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (330, 'Mack Trucks', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (331, 'Caterpillar', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (332, 'John Deere', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (333, 'Kubota', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (334, 'Case IH', 'keyword', 'auto_brand', 'hard_block', '汽车/摩托车品牌/车型 (搬运场景硬拒)');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (335, 'Disney', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (336, 'Mickey Mouse', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (337, 'Minnie Mouse', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (338, 'Donald Duck', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (339, 'Goofy', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (340, 'Pixar', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (341, 'Toy Story', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (342, 'Frozen', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (343, 'Elsa', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (344, 'Anna', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (345, 'Olaf', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (346, 'Moana', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (347, 'Mulan', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (348, 'Aladdin', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (349, 'Cinderella', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (350, 'Snow White', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (351, 'Lion King', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (352, 'Beauty and the Beast', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (353, 'Little Mermaid', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (354, 'Tangled', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (355, 'Marvel', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (356, 'Spider-Man', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (357, 'Iron Man', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (358, 'Captain America', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (359, 'Thor', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (360, 'Hulk', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (361, 'Avengers', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (362, 'Black Panther', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (363, 'Deadpool', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (364, 'X-Men', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (365, 'Wolverine', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (366, 'Venom', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (367, 'Guardians of the Galaxy', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (368, 'Doctor Strange', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (369, 'Ant-Man', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (370, 'DC Comics', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (371, 'Batman', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (372, 'Superman', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (373, 'Wonder Woman', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (374, 'Joker', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (375, 'Aquaman', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (376, 'Flash', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (377, 'Green Lantern', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (378, 'Harley Quinn', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (379, 'Star Wars', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (380, 'Darth Vader', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (381, 'Yoda', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (382, 'Baby Yoda', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (383, 'Mandalorian', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (384, 'Luke Skywalker', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (385, 'Chewbacca', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (386, 'Stormtrooper', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (387, 'Lightsaber', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (388, 'Harry Potter', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (389, 'Hogwarts', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (390, 'Dumbledore', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (391, 'Hermione', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (392, 'Voldemort', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (393, 'Pokemon', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (394, 'Pikachu', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (395, 'Bulbasaur', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (396, 'Charmander', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (397, 'Naruto', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (398, 'One Piece', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (399, 'Attack on Titan', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (400, 'Demon Slayer', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (401, 'Dragon Ball', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (402, 'My Hero Academia', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (403, 'Jujutsu Kaisen', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (404, 'Bleach', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (405, 'Death Note', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (406, 'Studio Ghibli', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (407, 'Totoro', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (408, 'Spirited Away', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (409, 'Minions', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (410, 'Shrek', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (411, 'Kung Fu Panda', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (412, 'How to Train Your Dragon', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (413, 'Peppa Pig', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (414, 'Paw Patrol', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (415, 'Hello Kitty', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (416, 'Sanrio', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (417, 'Barbie', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (418, 'Bratz', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (419, 'Transformers', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (420, 'Power Rangers', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (421, 'SpongeBob', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (422, 'Dora', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (423, 'PJ Masks', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (424, 'Bluey', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (425, 'Cocomelon', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (426, 'Sesame Street', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (427, 'Elmo', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (428, 'Big Bird', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (429, 'Tom and Jerry', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (430, 'Looney Tunes', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (431, 'Bugs Bunny', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (432, 'Minecraft', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (433, 'Fortnite', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (434, 'Roblox', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (435, 'Call of Duty', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (436, 'Halo', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (437, 'Super Mario', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (438, 'Mario', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (439, 'Luigi', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (440, 'Zelda', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (441, 'Link', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (442, 'Sonic', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (443, 'Pac-Man', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (444, 'Tetris', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (445, 'League of Legends', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (446, 'World of Warcraft', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (447, 'Overwatch', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (448, 'Grand Theft Auto', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (449, 'GTA', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (450, 'Final Fantasy', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (451, 'LEGO', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (452, 'Hot Wheels', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (454, 'Fisher-Price', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (455, 'Nerf', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (456, 'Rubik''s Cube', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (457, 'Tonka', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (458, 'Monopoly', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (459, 'Play-Doh', 'keyword', 'cartoon_ip', 'hard_block', '卡通/电影/动漫/游戏 IP');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (460, 'NFL', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (461, 'NBA', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (462, 'MLB', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (463, 'NHL', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (464, 'MLS', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (465, 'FIFA', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (466, 'UEFA', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (467, 'Premier League', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (468, 'Super Bowl', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (469, 'World Cup', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (470, 'Olympics', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (471, 'NCAA', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (472, 'March Madness', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (473, 'Lakers', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (474, 'Warriors', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (475, 'Celtics', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (476, 'Bulls', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (477, 'Heat', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (478, 'Knicks', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (479, 'LeBron James', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (480, 'Stephen Curry', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (481, 'Kevin Durant', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (482, 'Giannis', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (483, 'Luka Doncic', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (484, 'Michael Jordan', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (485, 'Kobe Bryant', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (486, 'Cowboys', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (487, 'Patriots', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (488, 'Packers', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (489, 'Steelers', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (490, '49ers', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (491, 'Chiefs', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (492, 'Tom Brady', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (493, 'Patrick Mahomes', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (494, 'Aaron Rodgers', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (495, 'Yankees', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (496, 'Red Sox', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (497, 'Dodgers', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (498, 'Cubs', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (499, 'Giants', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (500, 'Real Madrid', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (501, 'Barcelona', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (502, 'Manchester United', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (503, 'Manchester City', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (504, 'Liverpool', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (505, 'Chelsea', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (506, 'Arsenal', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (507, 'Juventus', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (508, 'Bayern Munich', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (509, 'PSG', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (510, 'Messi', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (511, 'Cristiano Ronaldo', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (512, 'Neymar', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (513, 'Mbappe', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (514, 'Haaland', 'keyword', 'sports_league', 'hard_block', '体育联赛/球队/球员');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (515, 'Harvard', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (516, 'Yale', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (517, 'Princeton', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (518, 'MIT', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (519, 'Stanford', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (520, 'Cornell', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (521, 'Columbia University', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (522, 'UCLA', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (523, 'UC Berkeley', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (524, 'NYU', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (525, 'Oxford', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (526, 'Cambridge', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (527, 'Duke', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (528, 'Michigan', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (529, 'Wisconsin', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (530, 'Texas', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (531, 'USC', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (532, 'Notre Dame', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (533, 'Florida State', 'keyword', 'college_brand', 'warn', '大学品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (534, 'Coca-Cola', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (535, 'Coke', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (536, 'Pepsi', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (537, 'Sprite', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (538, 'Fanta', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (539, 'Starbucks', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (540, 'McDonald''s', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (541, 'KFC', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (542, 'Burger King', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (543, 'Subway', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (544, 'Nestle', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (545, 'Hershey', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (546, 'Cadbury', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (547, 'Mars', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (548, 'M&M', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (549, 'Snickers', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (550, 'Kraft', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (551, 'Heinz', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (552, 'Kellogg''s', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (553, 'General Mills', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (554, 'Red Bull', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (555, 'Monster Energy', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (556, 'Gatorade', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (557, 'Oreo', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (558, 'Kit Kat', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (559, 'Ritz', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (560, 'Pringles', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (561, 'Doritos', 'keyword', 'food_brand', 'hard_block', '食品饮料巨头');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (562, 'Taylor Swift', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (563, 'Beyoncé', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (564, 'Rihanna', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (565, 'Lady Gaga', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (566, 'Drake', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (567, 'Kanye West', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (568, 'Kim Kardashian', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (569, 'BTS', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (570, 'BLACKPINK', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (571, 'Twice', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (572, 'Elvis Presley', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (573, 'Michael Jackson', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (574, 'Beatles', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (575, 'Bob Marley', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (576, 'Marilyn Monroe', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (577, 'Audrey Hepburn', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (578, 'Albert Einstein', 'keyword', 'celebrity', 'hard_block', '明星/艺人');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (579, 'KitchenAid', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (580, 'Cuisinart', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (582, 'Instant Pot', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (583, 'Keurig', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (584, 'Nespresso', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (585, 'Breville', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (586, 'Vitamix', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (587, 'Panasonic', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (588, 'Hamilton Beach', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (589, 'Black+Decker', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (590, 'Whirlpool', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (591, 'Maytag', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (592, 'Frigidaire', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (593, 'LG', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (594, 'GE Appliances', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (595, 'Roomba', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (596, 'iRobot', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (597, 'Shark', 'keyword', 'appliance_brand', 'hard_block', '家电品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (598, 'MAC Cosmetics', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (599, 'Maybelline', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (600, 'Revlon', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (601, 'L''Oreal', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (602, 'L''Oréal', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (603, 'Estée Lauder', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (604, 'Lancôme', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (605, 'Clinique', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (606, 'Shiseido', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (607, 'Sephora', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (608, 'Ulta', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (609, 'Kylie Cosmetics', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (610, 'Fenty Beauty', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (611, 'Urban Decay', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (612, 'La Mer', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (613, 'SK-II', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');
INSERT INTO public.ip_trigger_terms (id, pattern, pattern_type, trigger_category, severity, notes) VALUES (614, 'Olay', 'keyword', 'beauty_brand', 'hard_block', '美妆品牌');


--
-- Data for Name: offensive_lexicon; Type: TABLE DATA; Schema: public; Owner: nextderboy
--

INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (1, 'swastika', 'swastika', 'en', 'religion', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (2, 'nazi', 'nazi', 'en', 'religion', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (3, 'hitler', 'hitler', 'en', 'religion', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (4, 'ss bolts', 'ss bolts', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (5, 'blessed by allah', 'blessed by allah', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (6, 'jesus christ', 'jesus christ', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (7, 'crucifix', 'crucifix', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (8, 'rosary', 'rosary', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (9, 'prayer beads', 'prayer beads', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (10, 'satan', 'satan', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (11, 'satanic', 'satanic', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (12, 'devil', 'devil', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (13, 'demonic', 'demonic', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (14, 'pentagram', 'pentagram', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (15, 'upside down cross', 'upside down cross', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (16, 'church of satan', 'church of satan', 'en', 'religion', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (17, 'ouija', 'ouija', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (18, 'occult', 'occult', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (19, 'tarot', 'tarot', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (20, 'voodoo', 'voodoo', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (21, 'wiccan', 'wiccan', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (22, 'mecca', 'mecca', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (23, 'prayer rug', 'prayer rug', 'en', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (24, '纳粹', '纳粹', 'zh', 'religion', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (25, '卍', '卍', 'zh', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (26, '佛像', '佛像', 'zh', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (27, '菩萨', '菩萨', 'zh', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (28, '圣经', '圣经', 'zh', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (29, '古兰经', '古兰经', 'zh', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (30, '十字架', '十字架', 'zh', 'religion', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (31, 'white power', 'white power', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (32, 'white supremacy', 'white supremacy', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (33, 'kkk', 'kkk', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (34, 'n-word', 'n-word', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (35, 'nigger', 'nigger', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (36, 'chink', 'chink', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (37, 'gook', 'gook', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (38, 'spic', 'spic', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (39, 'wetback', 'wetback', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (40, 'redskin', 'redskin', 'en', 'race', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (41, 'slave', 'slave', 'en', 'race', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (42, 'confederate flag', 'confederate flag', 'en', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (43, '支那', '支那', 'zh', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (44, '黄猴子', '黄猴子', 'zh', 'race', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (45, 'trump', 'trump', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (46, 'biden', 'biden', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (47, 'maga', 'maga', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (48, 'antifa', 'antifa', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (49, 'isis', 'isis', 'en', 'politics', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (50, 'taliban', 'taliban', 'en', 'politics', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (51, 'hamas', 'hamas', 'en', 'politics', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (52, 'hezbollah', 'hezbollah', 'en', 'politics', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (53, 'al qaeda', 'al qaeda', 'en', 'politics', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (54, 'cuba', 'cuba', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (55, 'iran', 'iran', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (56, 'north korea', 'north korea', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (57, 'syria', 'syria', 'en', 'politics', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (58, 'sex toy', 'sex toy', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (59, 'dildo', 'dildo', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (60, 'anal', 'anal', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (61, 'butt plug', 'butt plug', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (62, 'penis', 'penis', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (63, 'vagina', 'vagina', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (64, 'vibrator', 'vibrator', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (65, 'adult content', 'adult content', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (66, 'adult novelty', 'adult novelty', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (67, 'xxx', 'xxx', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (68, 'porn', 'porn', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (69, 'pornography', 'pornography', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (70, 'pornographic', 'pornographic', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (71, 'fetish', 'fetish', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (72, 'bondage', 'bondage', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (73, 'bdsm', 'bdsm', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (74, 'kink', 'kink', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (75, 'nude', 'nude', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (76, 'naked', 'naked', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (77, 'erotic', 'erotic', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (78, 'lingerie', 'lingerie', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (79, 'intimate', 'intimate', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (80, 'g-spot', 'g-spot', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (81, 'prostate massager', 'prostate massager', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (82, 'couples toy', 'couples toy', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (83, 'orgasm', 'orgasm', 'en', 'sexual', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (84, 'sensual', 'sensual', 'en', 'sexual', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (85, 'gun', 'gun', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (86, 'pistol', 'pistol', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (87, 'rifle', 'rifle', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (88, 'shotgun', 'shotgun', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (89, 'assault', 'assault', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (90, 'firearm', 'firearm', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (91, 'ammunition', 'ammunition', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (92, 'ammo', 'ammo', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (93, 'bullet', 'bullet', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (94, 'cartridge', 'cartridge', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (95, 'magazine clip', 'magazine clip', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (96, 'silencer', 'silencer', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (97, 'suppressor', 'suppressor', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (98, 'sniper', 'sniper', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (99, 'killer', 'killer', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (100, 'murder', 'murder', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (101, 'suicide', 'suicide', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (102, 'self harm', 'self harm', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (103, 'martial arts', 'martial arts', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (104, 'brass knuckles', 'brass knuckles', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (105, 'throwing knife', 'throwing knife', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (106, 'dagger', 'dagger', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (107, 'bayonet', 'bayonet', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (108, 'machete', 'machete', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (109, 'katana', 'katana', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (110, 'samurai sword', 'samurai sword', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (111, 'butterfly knife', 'butterfly knife', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (112, 'karambit', 'karambit', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (113, 'nunchuck', 'nunchuck', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (114, 'nunchaku', 'nunchaku', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (115, 'tomahawk', 'tomahawk', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (116, 'hatchet', 'hatchet', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (117, 'ninja', 'ninja', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (118, 'combat', 'combat', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (119, 'tactical knife', 'tactical knife', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (120, 'crossbow', 'crossbow', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (121, 'compound bow', 'compound bow', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (122, 'blowgun', 'blowgun', 'en', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (123, 'slingshot', 'slingshot', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (124, 'catapult', 'catapult', 'en', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (125, '自卫', '自卫', 'zh', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (126, '武器', '武器', 'zh', 'violence', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (127, '刀具', '刀具', 'zh', 'violence', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (128, 'cbd', 'cbd', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (129, 'cannabis', 'cannabis', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (130, 'marijuana', 'marijuana', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (131, 'weed', 'weed', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (132, 'thc', 'thc', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (133, 'cbg', 'cbg', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (134, 'cbn', 'cbn', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (135, 'delta 8', 'delta 8', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (136, 'delta-8', 'delta-8', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (137, 'kratom', 'kratom', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (138, 'kava', 'kava', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (139, 'salvia', 'salvia', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (140, 'opium', 'opium', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (141, 'poppy seed', 'poppy seed', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (142, 'heroin', 'heroin', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (143, 'cocaine', 'cocaine', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (144, 'meth', 'meth', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (145, 'methamphetamine', 'methamphetamine', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (146, 'psychedelic', 'psychedelic', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (147, 'lsd', 'lsd', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (148, 'mdma', 'mdma', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (149, 'mushroom', 'mushroom', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (150, 'psilocybin', 'psilocybin', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (151, 'hemp', 'hemp', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (152, 'hgh', 'hgh', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (153, 'steroid', 'steroid', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (154, 'anabolic', 'anabolic', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (155, 'testosterone', 'testosterone', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (156, 'sarm', 'sarm', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (157, 'bong', 'bong', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (158, 'pipe', 'pipe', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (159, 'dab rig', 'dab rig', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (160, 'vape pen', 'vape pen', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (161, 'vape mod', 'vape mod', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (162, 'e-liquid', 'e-liquid', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (163, 'nicotine', 'nicotine', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (164, 'rolling paper', 'rolling paper', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (165, 'herbal incense', 'herbal incense', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (166, 'research chemical', 'research chemical', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (167, 'nootropic', 'nootropic', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (168, 'benzo', 'benzo', 'en', 'drug', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (169, 'xanax', 'xanax', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (170, 'adderall', 'adderall', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (171, 'oxycontin', 'oxycontin', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (172, 'fentanyl', 'fentanyl', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (173, 'codeine', 'codeine', 'en', 'drug', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (174, 'pepper spray', 'pepper spray', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (175, 'mace spray', 'mace spray', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (176, 'stun gun', 'stun gun', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (177, 'taser', 'taser', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (178, 'replica gun', 'replica gun', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (179, 'airsoft gun', 'airsoft gun', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (180, 'bb gun', 'bb gun', 'en', 'walmart_strict_weapon', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (181, 'paintball gun', 'paintball gun', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (182, 'self defense', 'self defense', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (183, 'self-defense', 'self-defense', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (184, 'personal protection', 'personal protection', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (185, 'anti-theft', 'anti-theft', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (186, 'lockout', 'lockout', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (187, 'tactical', 'tactical', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (188, 'cosplay weapon', 'cosplay weapon', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (189, 'foam blaster', 'foam blaster', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (190, 'foam dart', 'foam dart', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (191, 'larp', 'larp', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (192, 'live action role play', 'live action role play', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (193, 'cutting', 'cutting', 'en', 'walmart_strict_weapon', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (194, 'cigarette', 'cigarette', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (195, 'cigar', 'cigar', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (196, 'tobacco', 'tobacco', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (197, 'shisha', 'shisha', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (198, 'hookah', 'hookah', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (199, 'e-cigarette', 'e-cigarette', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (200, 'vape', 'vape', 'en', 'tobacco_adult', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (201, 'juul', 'juul', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (202, 'nicotine pouch', 'nicotine pouch', 'en', 'tobacco_adult', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (203, 'alcohol', 'alcohol', 'en', 'alcohol', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (204, 'beer', 'beer', 'en', 'alcohol', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (205, 'wine', 'wine', 'en', 'alcohol', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (206, 'liquor', 'liquor', 'en', 'alcohol', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (207, 'whiskey', 'whiskey', 'en', 'alcohol', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (208, 'vodka', 'vodka', 'en', 'alcohol', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (209, 'rum', 'rum', 'en', 'alcohol', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (210, 'gin', 'gin', 'en', 'alcohol', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (211, 'tequila', 'tequila', 'en', 'alcohol', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (212, 'sake', 'sake', 'en', 'alcohol', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (213, 'n95', 'n95', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (214, 'kn95', 'kn95', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (215, 'fda approved', 'fda approved', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (216, 'ce certified', 'ce certified', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (217, 'rohs', 'rohs', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (218, 'organic certified', 'organic certified', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (219, 'cgmp', 'cgmp', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (220, 'mercury', 'mercury', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (221, 'lead free', 'lead free', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (222, 'bpa free', 'bpa free', 'en', 'regulatory_keyword', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (223, 'asbestos', 'asbestos', 'en', 'regulatory_keyword', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (224, 'replica', 'replica', 'en', 'counterfeit_signal', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (225, 'inspired by', 'inspired by', 'en', 'counterfeit_signal', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (226, 'like original', 'like original', 'en', 'counterfeit_signal', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (227, 'high copy', 'high copy', 'en', 'counterfeit_signal', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (228, '1:1 copy', '1:1 copy', 'en', 'counterfeit_signal', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (229, 'aaa quality', 'aaa quality', 'en', 'counterfeit_signal', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (230, 'designer inspired', 'designer inspired', 'en', 'counterfeit_signal', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (231, 'knockoff', 'knockoff', 'en', 'counterfeit_signal', 'hard_block', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (232, 'dupe', 'dupe', 'en', 'counterfeit_signal', 'warn', 'seed');
INSERT INTO public.offensive_lexicon (id, term, term_normalized, language, category, severity, notes) VALUES (233, 'fake', 'fake', 'en', 'counterfeit_signal', 'warn', 'seed');


--
-- Data for Name: safe_category_whitelist; Type: TABLE DATA; Schema: public; Owner: nextderboy
--

INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (1, 'Walmart ProductType=default', 'default', false, 'high', 'none', false, '{default_productype}', '选不出正确类目的兜底, 100% 暂停, 必须禁用');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (2, 'WalmartPtype=Backpacks', 'Backpacks', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:20');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (3, 'WalmartPtype=Boots', 'Boots', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (4, 'WalmartPtype=Bracelets', 'Bracelets', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (5, 'WalmartPtype=default', 'default', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction,regulatory_children,regulatory_cosmetic,regulatory_drug,regulatory_firearm,regulatory_tobacco}', 'biz_cn:5 + regulatory_children:1 + regulatory_cosmetic:1 + regulatory_drug:4 + regulatory_firearm:1 + regulatory_tobacco:7');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (6, 'WalmartPtype=Faucet Water Filters', 'Faucet Water Filters', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (7, 'WalmartPtype=Garage Door Opener Systems & Supplies', 'Garage Door Opener Systems & Supplies', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:7');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (8, 'WalmartPtype=Gem Scales', 'Gem Scales', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:8');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (9, 'WalmartPtype=Handbags', 'Handbags', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:22');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (10, 'WalmartPtype=Hats', 'Hats', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:9');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (11, 'WalmartPtype=Jewelry Boxes', 'Jewelry Boxes', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:19');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (12, 'WalmartPtype=Jewelry Cleaner', 'Jewelry Cleaner', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (13, 'WalmartPtype=Jewelry Cleaning Machines', 'Jewelry Cleaning Machines', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (14, 'WalmartPtype=Jewelry Displays', 'Jewelry Displays', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:15');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (15, 'WalmartPtype=Jewelry Holders & Organizers', 'Jewelry Holders & Organizers', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:11');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (16, 'WalmartPtype=Lawn Mower Blades', 'Lawn Mower Blades', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive,biz_cn_restriction}', 'biz_cn:3 + biz_brand:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (17, 'WalmartPtype=Loose Beads', 'Loose Beads', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:24');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (18, 'WalmartPtype=Messenger & Shoulder Bags', 'Messenger & Shoulder Bags', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (19, 'WalmartPtype=Necklaces', 'Necklaces', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:11');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (20, 'WalmartPtype=Pins & Brooches', 'Pins & Brooches', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:11');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (21, 'WalmartPtype=Replacement Water Filters', 'Replacement Water Filters', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:75');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (22, 'WalmartPtype=Ring Sizers', 'Ring Sizers', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (23, 'WalmartPtype=Rings', 'Rings', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (24, 'WalmartPtype=Rosaries & Prayer Beads', 'Rosaries & Prayer Beads', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:11');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (25, 'WalmartPtype=Safety Shoes & Boots', 'Safety Shoes & Boots', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:8');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (26, 'WalmartPtype=Sweatshirts & Hoodies', 'Sweatshirts & Hoodies', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:20');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (27, 'WalmartPtype=T-Shirts', 'T-Shirts', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:22');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (28, 'WalmartPtype=Watch Repair Tools & Kits', 'Watch Repair Tools & Kits', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:9');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (29, 'WalmartPtype=Wedding Rings', 'Wedding Rings', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (30, 'WalmartPtype=Window Shades', 'Window Shades', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (31, 'WalmartPtype=Wristwatches', 'Wristwatches', false, 'high', 'biz_cn_block', false, '{biz_cn_restriction}', 'biz_cn:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (32, 'WalmartPtype=Adhesive Tape Dispensers', 'Adhesive Tape Dispensers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (33, 'WalmartPtype=Adhesive Tapes', 'Adhesive Tapes', false, 'high', 'CPC', false, '{regulatory_children,regulatory_drug}', 'regulatory_children:1 + regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (34, 'WalmartPtype=Alphabet Toys', 'Alphabet Toys', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (35, 'WalmartPtype=Ammunition', 'Ammunition', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (36, 'WalmartPtype=Animal Feed', 'Animal Feed', false, 'high', 'EPA', false, '{regulatory_pet}', 'regulatory_pet:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (37, 'WalmartPtype=Animal Supplements & Vitamins', 'Animal Supplements & Vitamins', false, 'high', 'EPA', false, '{regulatory_pet}', 'regulatory_pet:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (38, 'WalmartPtype=Appliance Hoses', 'Appliance Hoses', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (39, 'WalmartPtype=Aromatherapy & Essential Oils', 'Aromatherapy & Essential Oils', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (40, 'WalmartPtype=Audio Power Amplifiers', 'Audio Power Amplifiers', false, 'high', 'other_cert', false, '{regulatory_preapproval}', 'regulatory_preapproval:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (41, 'WalmartPtype=Automotive Specialty Parts', 'Automotive Specialty Parts', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (42, 'WalmartPtype=Baby Bathtubs', 'Baby Bathtubs', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (43, 'WalmartPtype=Baby Blankets', 'Baby Blankets', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (44, 'WalmartPtype=Baby Feeding Chairs', 'Baby Feeding Chairs', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (45, 'WalmartPtype=Baby Rattles', 'Baby Rattles', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (46, 'WalmartPtype=Beanbag Toss Game Sets', 'Beanbag Toss Game Sets', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (47, 'WalmartPtype=Bed Frames', 'Bed Frames', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (48, 'WalmartPtype=Beds', 'Beds', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (49, 'WalmartPtype=Bento Boxes', 'Bento Boxes', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (50, 'WalmartPtype=Bicycle Helmets', 'Bicycle Helmets', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (51, 'WalmartPtype=Bicycle Lights', 'Bicycle Lights', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (52, 'WalmartPtype=Bicycle Tire Tubes', 'Bicycle Tire Tubes', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (53, 'WalmartPtype=Bicycles', 'Bicycles', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (54, 'WalmartPtype=Binder Clips', 'Binder Clips', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (55, 'WalmartPtype=Binders', 'Binders', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (56, 'WalmartPtype=Bird Food', 'Bird Food', false, 'high', 'EPA', false, '{regulatory_pet}', 'regulatory_pet:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (57, 'WalmartPtype=Blank Diaries & Journals', 'Blank Diaries & Journals', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (58, 'WalmartPtype=Board Games', 'Board Games', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (59, 'WalmartPtype=Body Moisturizers', 'Body Moisturizers', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (60, 'WalmartPtype=Book Covers', 'Book Covers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (61, 'WalmartPtype=Book Stands', 'Book Stands', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (62, 'WalmartPtype=Boomerangs', 'Boomerangs', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (63, 'WalmartPtype=Booster Seats', 'Booster Seats', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (64, 'WalmartPtype=Bunk Beds', 'Bunk Beds', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (65, 'WalmartPtype=Card Games', 'Card Games', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (66, 'WalmartPtype=Catheters', 'Catheters', false, 'high', 'FDA', false, '{regulatory_medical}', 'regulatory_medical:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (67, 'WalmartPtype=Chalkboard Erasers', 'Chalkboard Erasers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (68, 'WalmartPtype=Chalkboards', 'Chalkboards', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (69, 'WalmartPtype=Cigarette Tubes', 'Cigarette Tubes', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (70, 'WalmartPtype=Composition Notebooks', 'Composition Notebooks', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:9');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (71, 'WalmartPtype=Compression Gloves, Sleeves & Socks', 'Compression Gloves, Sleeves & Socks', false, 'high', 'FDA', false, '{regulatory_medical}', 'regulatory_medical:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (72, 'WalmartPtype=Contour Pillows', 'Contour Pillows', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (73, 'WalmartPtype=Correction Tape', 'Correction Tape', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (74, 'WalmartPtype=Deodorants & Antiperspirants', 'Deodorants & Antiperspirants', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (75, 'WalmartPtype=Desk Chairs', 'Desk Chairs', false, 'high', 'other_cert', false, '{regulatory_preapproval}', 'regulatory_preapproval:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (76, 'WalmartPtype=Desk Staplers', 'Desk Staplers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (77, 'WalmartPtype=Desktop Organizers', 'Desktop Organizers', false, 'high', 'CPC', false, '{regulatory_children,regulatory_tobacco}', 'regulatory_children:29 + regulatory_tobacco:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (78, 'WalmartPtype=Drug Tests', 'Drug Tests', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (79, 'WalmartPtype=Dry Erase Markers', 'Dry Erase Markers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:9');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (80, 'WalmartPtype=Dry Shampoos', 'Dry Shampoos', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (81, 'WalmartPtype=Easel Flip Charts', 'Easel Flip Charts', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (82, 'WalmartPtype=Engravers', 'Engravers', false, 'high', 'other_cert', false, '{regulatory_preapproval}', 'regulatory_preapproval:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (83, 'WalmartPtype=Eye Drops', 'Eye Drops', false, 'high', 'FDA', false, '{regulatory_medical}', 'regulatory_medical:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (84, 'WalmartPtype=Filler Paper', 'Filler Paper', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (85, 'WalmartPtype=Flashlights', 'Flashlights', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (86, 'WalmartPtype=Golf Club Grips', 'Golf Club Grips', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (87, 'WalmartPtype=Graph Paper', 'Graph Paper', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (88, 'WalmartPtype=Gun Monopods, Bipods & Accessories', 'Gun Monopods, Bipods & Accessories', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (89, 'WalmartPtype=Gun Rails', 'Gun Rails', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (90, 'WalmartPtype=Hair Oils', 'Hair Oils', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (91, 'WalmartPtype=Hand Sanitizers', 'Hand Sanitizers', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (92, 'WalmartPtype=Hand Soaps', 'Hand Soaps', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (93, 'WalmartPtype=Heating Pads', 'Heating Pads', false, 'high', 'FDA', false, '{regulatory_medical}', 'regulatory_medical:7');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (94, 'WalmartPtype=Helmet Covers', 'Helmet Covers', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (95, 'WalmartPtype=Herbal Supplements', 'Herbal Supplements', false, 'high', 'FDA', false, '{regulatory_supplement}', 'regulatory_supplement:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (96, 'WalmartPtype=Highlighters', 'Highlighters', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:12');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (97, 'WalmartPtype=Hookah Charcoal', 'Hookah Charcoal', false, 'high', 'other_cert', false, '{regulatory_tobacco}', 'regulatory_tobacco:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (98, 'WalmartPtype=Hunting Camouflage Accessories', 'Hunting Camouflage Accessories', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (99, 'WalmartPtype=Index Cards', 'Index Cards', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (100, 'WalmartPtype=Industrial Sealants', 'Industrial Sealants', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (101, 'WalmartPtype=Kids Gardening Tools', 'Kids Gardening Tools', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (102, 'WalmartPtype=Lab Distillation Apparatus', 'Lab Distillation Apparatus', false, 'high', 'other_cert', false, '{regulatory_alcohol}', 'regulatory_alcohol:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (103, 'WalmartPtype=Label Makers', 'Label Makers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (104, 'WalmartPtype=Labels', 'Labels', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (105, 'WalmartPtype=Manual Pencil Sharpeners', 'Manual Pencil Sharpeners', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (106, 'WalmartPtype=Markers', 'Markers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:20');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (107, 'WalmartPtype=Masking Tapes', 'Masking Tapes', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (108, 'WalmartPtype=Mechanical Pencils', 'Mechanical Pencils', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (109, 'WalmartPtype=Medical Thermometers', 'Medical Thermometers', false, 'high', 'FDA', false, '{regulatory_medical}', 'regulatory_medical:6');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (110, 'WalmartPtype=Mineral Supplements', 'Mineral Supplements', false, 'high', 'FDA', false, '{regulatory_supplement}', 'regulatory_supplement:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (111, 'WalmartPtype=Novelty & Gag Toys', 'Novelty & Gag Toys', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (112, 'WalmartPtype=Other Learning & Educational Toys', 'Other Learning & Educational Toys', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (113, 'WalmartPtype=Other Nail Care', 'Other Nail Care', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (114, 'WalmartPtype=Other Power & Hand Tool Accessories', 'Other Power & Hand Tool Accessories', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (115, 'WalmartPtype=Paper Clips', 'Paper Clips', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (116, 'WalmartPtype=Party Favors', 'Party Favors', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (117, 'WalmartPtype=Pencil & Pen Erasers', 'Pencil & Pen Erasers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (118, 'WalmartPtype=Pencil Cases', 'Pencil Cases', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (119, 'WalmartPtype=Pencil Holders', 'Pencil Holders', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:18');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (120, 'WalmartPtype=Pencils', 'Pencils', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:11');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (121, 'WalmartPtype=Pens', 'Pens', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:25');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (122, 'WalmartPtype=Pet Milk Replacers', 'Pet Milk Replacers', false, 'high', 'EPA', false, '{regulatory_pet}', 'regulatory_pet:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (123, 'WalmartPtype=Pet Repellents', 'Pet Repellents', false, 'high', 'EPA', false, '{regulatory_pet}', 'regulatory_pet:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (124, 'WalmartPtype=Photo Paper', 'Photo Paper', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (125, 'WalmartPtype=Pins & Tacks', 'Pins & Tacks', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (126, 'WalmartPtype=Planners & Appointment Books', 'Planners & Appointment Books', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (127, 'WalmartPtype=Play Food', 'Play Food', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (128, 'WalmartPtype=Play Gardening Tools', 'Play Gardening Tools', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (129, 'WalmartPtype=Pool Toys & Floats', 'Pool Toys & Floats', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (130, 'WalmartPtype=Power Adapters', 'Power Adapters', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive,regulatory_firearm}', 'regulatory_firearm:2 + biz_brand:10');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (131, 'WalmartPtype=Pressure Washer Attachments', 'Pressure Washer Attachments', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (132, 'WalmartPtype=Protein Supplements', 'Protein Supplements', false, 'high', 'FDA', false, '{regulatory_supplement}', 'regulatory_supplement:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (133, 'WalmartPtype=Report Covers', 'Report Covers', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (134, 'WalmartPtype=Reusable Lunch Bags & Boxes', 'Reusable Lunch Bags & Boxes', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (135, 'WalmartPtype=Riflescope Cases', 'Riflescope Cases', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (136, 'WalmartPtype=Riflescopes & Sights', 'Riflescopes & Sights', false, 'high', 'FinCEN', false, '{regulatory_firearm}', 'regulatory_firearm:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (137, 'WalmartPtype=Rubber Bands', 'Rubber Bands', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (138, 'WalmartPtype=Safes', 'Safes', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (139, 'WalmartPtype=School & Office Paper', 'School & Office Paper', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (140, 'WalmartPtype=Science Sets', 'Science Sets', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (141, 'WalmartPtype=Seating Cushions', 'Seating Cushions', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (142, 'WalmartPtype=Soap Making Bases', 'Soap Making Bases', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (143, 'WalmartPtype=Stationery & Stationery Sets', 'Stationery & Stationery Sets', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (144, 'WalmartPtype=Step Stools', 'Step Stools', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (145, 'WalmartPtype=Sticky Notes', 'Sticky Notes', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:15');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (146, 'WalmartPtype=Stress Squeeze Balls', 'Stress Squeeze Balls', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (147, 'WalmartPtype=Table Skirts', 'Table Skirts', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (148, 'WalmartPtype=Tampons', 'Tampons', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (149, 'WalmartPtype=Target Toss Games', 'Target Toss Games', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:3');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (150, 'WalmartPtype=Teeth Whitening', 'Teeth Whitening', false, 'high', 'FDA', false, '{regulatory_cosmetic}', 'regulatory_cosmetic:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (151, 'WalmartPtype=Ticket Holders', 'Ticket Holders', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (152, 'WalmartPtype=Toy Doodle Tablets', 'Toy Doodle Tablets', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (153, 'WalmartPtype=Toy Musical Instruments', 'Toy Musical Instruments', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:6');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (154, 'WalmartPtype=Urinary Tract Infection Test Strips', 'Urinary Tract Infection Test Strips', false, 'high', 'FDA', false, '{regulatory_medical}', 'regulatory_medical:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (155, 'WalmartPtype=Vending Machines', 'Vending Machines', false, 'high', 'other_cert', false, '{regulatory_drug}', 'regulatory_drug:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (156, 'WalmartPtype=Whiteboards', 'Whiteboards', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:8');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (157, 'WalmartPtype=Writing Notebooks & Sketch Books', 'Writing Notebooks & Sketch Books', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:19');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (158, 'WalmartPtype=Writing Pads', 'Writing Pads', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:1');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (159, 'WalmartPtype=Zipper Binders', 'Zipper Binders', false, 'high', 'CPC', false, '{regulatory_children}', 'regulatory_children:10');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (160, 'WalmartPtype=Drum Replacement Parts', 'Drum Replacement Parts', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive}', 'biz_brand:6');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (161, 'WalmartPtype=Electronic Pianos', 'Electronic Pianos', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive}', 'biz_brand:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (162, 'WalmartPtype=Grilling Side Burners', 'Grilling Side Burners', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive}', 'biz_brand:4');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (163, 'WalmartPtype=Other Electronic Components & Accessories', 'Other Electronic Components & Accessories', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive}', 'biz_brand:2');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (164, 'WalmartPtype=Power Tool Batteries', 'Power Tool Batteries', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive}', 'biz_brand:5');
INSERT INTO public.safe_category_whitelist (id, amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level, cert_required, allowed, sub_risks, notes) VALUES (165, 'WalmartPtype=Wallets', 'Wallets', false, 'high', 'biz_brand_block', false, '{biz_brand_exclusive}', 'biz_brand:2');


--
-- Name: ip_trigger_terms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nextderboy
--

SELECT pg_catalog.setval('public.ip_trigger_terms_id_seq', 614, true);


--
-- Name: offensive_lexicon_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nextderboy
--

SELECT pg_catalog.setval('public.offensive_lexicon_id_seq', 233, true);


--
-- Name: safe_category_whitelist_id_seq; Type: SEQUENCE SET; Schema: public; Owner: nextderboy
--

SELECT pg_catalog.setval('public.safe_category_whitelist_id_seq', 165, true);


--
-- Name: ip_trigger_terms ip_trigger_terms_pattern_key; Type: CONSTRAINT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.ip_trigger_terms
    ADD CONSTRAINT ip_trigger_terms_pattern_key UNIQUE (pattern);


--
-- Name: ip_trigger_terms ip_trigger_terms_pkey; Type: CONSTRAINT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.ip_trigger_terms
    ADD CONSTRAINT ip_trigger_terms_pkey PRIMARY KEY (id);


--
-- Name: offensive_lexicon offensive_lexicon_pkey; Type: CONSTRAINT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.offensive_lexicon
    ADD CONSTRAINT offensive_lexicon_pkey PRIMARY KEY (id);


--
-- Name: offensive_lexicon offensive_lexicon_term_normalized_category_key; Type: CONSTRAINT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.offensive_lexicon
    ADD CONSTRAINT offensive_lexicon_term_normalized_category_key UNIQUE (term_normalized, category);


--
-- Name: safe_category_whitelist safe_category_whitelist_amazon_path_prefix_key; Type: CONSTRAINT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.safe_category_whitelist
    ADD CONSTRAINT safe_category_whitelist_amazon_path_prefix_key UNIQUE (amazon_path_prefix);


--
-- Name: safe_category_whitelist safe_category_whitelist_pkey; Type: CONSTRAINT; Schema: public; Owner: nextderboy
--

ALTER TABLE ONLY public.safe_category_whitelist
    ADD CONSTRAINT safe_category_whitelist_pkey PRIMARY KEY (id);


--
-- Name: idx_ipt_cat; Type: INDEX; Schema: public; Owner: nextderboy
--

CREATE INDEX idx_ipt_cat ON public.ip_trigger_terms USING btree (trigger_category);


--
-- Name: idx_offensive_cat; Type: INDEX; Schema: public; Owner: nextderboy
--

CREATE INDEX idx_offensive_cat ON public.offensive_lexicon USING btree (category);


--
-- Name: idx_offensive_term; Type: INDEX; Schema: public; Owner: nextderboy
--

CREATE INDEX idx_offensive_term ON public.offensive_lexicon USING btree (term_normalized);


--
-- PostgreSQL database dump complete
--

\unrestrict WoMVkiXFftYcvg4KbmsZucyBdckxyzAUDU9MfJFtoh6NaPUzqyPgav3hMIpjhpF

