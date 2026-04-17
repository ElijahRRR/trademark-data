"""
L1 硬规则引擎

对 products_stage 的一行产品, 运行不花 LLM 预算的硬规则:
1. rule_asin_hit          ASIN 在历史违规中出现
2. rule_category_keyword  Amazon 类目路径含硬禁关键词
3. rule_offensive_keyword offensive_lexicon 命中
4. rule_ip_keyword        ip_trigger_terms keyword 命中 (奢侈/卡通/科技/运动品牌)
5. rule_compat_trademark  兼容词 regex 抽品牌名 + 查 USPTO LIVE trademarks
6. rule_default_ptype_risk Amazon 商品类型空 (预示 Walmart ProductType 可能 default)

输出:
{
    'verdict': 'approve' | 'hold' | 'reject',
    'ip_risk': 0-100,
    'offensive_risk': 0-100,
    'regulatory_risk': 0-100,
    'counterfeit_risk': 0-100,
    'overall_risk': 0-100,
    'reason_summary': str,
    'flags': [flag, ...],
}
"""
import re
from typing import Dict, List

import psycopg2


DB_CONN = "dbname=uspto user=nextderboy"

# Amazon category path 硬禁关键词 (搬运场景不允许)
# 所有关键词 lowercase 后在 category_path (全转小写) 里 substring 匹配
CATEGORY_HARD_KEYWORDS = [
    # --- 武器类 ---
    ("firearm",       "regulatory", "firearm"),
    ("ammunition",    "regulatory", "firearm"),
    ("ammo ",         "regulatory", "firearm"),
    ("gunpowder",     "regulatory", "firearm"),
    ("weapon",        "regulatory", "weapon"),
    ("knife",         "regulatory", "weapon"),
    ("sword",         "regulatory", "weapon"),
    ("bayonet",       "regulatory", "weapon"),
    ("dagger",        "regulatory", "weapon"),
    ("machete",       "regulatory", "weapon"),
    ("crossbow",      "regulatory", "weapon"),
    ("compound bow",  "regulatory", "weapon"),
    ("recurve bow",   "regulatory", "weapon"),
    ("throwing star", "regulatory", "weapon"),
    ("shuriken",      "regulatory", "weapon"),
    ("nunchak",       "regulatory", "weapon"),
    ("nunchuck",      "regulatory", "weapon"),
    ("pepper spray",  "regulatory", "weapon"),
    ("stun gun",      "regulatory", "weapon"),
    ("taser",         "regulatory", "weapon"),
    ("self-defense",  "regulatory", "weapon"),
    ("self defense",  "regulatory", "weapon"),
    ("brass knuckle", "regulatory", "weapon"),
    ("switchblade",   "regulatory", "weapon"),
    # --- 仿真/玩具武器 (沃尔玛多限制) ---
    ("airsoft",       "regulatory", "imitation_weapon"),
    ("paintball",     "regulatory", "imitation_weapon"),
    ("bb gun",        "regulatory", "imitation_weapon"),
    ("blowgun",       "regulatory", "imitation_weapon"),
    ("slingshot",     "regulatory", "imitation_weapon"),
    ("replica firearm","regulatory", "imitation_weapon"),
    ("prop gun",      "regulatory", "imitation_weapon"),
    # --- 烟花爆炸 ---
    ("firework",      "regulatory", "pyrotechnic"),
    ("pyrotechnic",   "regulatory", "pyrotechnic"),
    ("sparkler",      "regulatory", "pyrotechnic"),
    ("explosive",     "regulatory", "pyrotechnic"),
    ("smoke bomb",    "regulatory", "pyrotechnic"),
    # --- 酒类 ---
    ("alcohol",       "regulatory", "alcohol"),
    ("wine",          "regulatory", "alcohol"),
    ("beer",          "regulatory", "alcohol"),
    ("liquor",        "regulatory", "alcohol"),
    ("whiskey",       "regulatory", "alcohol"),
    ("vodka",         "regulatory", "alcohol"),
    # --- 烟草/尼古丁 ---
    ("tobacco",       "regulatory", "tobacco"),
    ("cigarette",     "regulatory", "tobacco"),
    ("cigar",         "regulatory", "tobacco"),
    ("vape",          "regulatory", "tobacco"),
    ("e-cigarette",   "regulatory", "tobacco"),
    ("nicotine",      "regulatory", "tobacco"),
    ("shisha",        "regulatory", "tobacco"),
    ("hookah",        "regulatory", "tobacco"),
    # --- 毒品/管制 ---
    ("cbd",           "regulatory", "drug"),
    ("cannabis",      "regulatory", "drug"),
    ("marijuana",     "regulatory", "drug"),
    ("kratom",        "regulatory", "drug"),
    ("hemp extract",  "regulatory", "drug"),
    ("thc",           "regulatory", "drug"),
    ("bong",          "regulatory", "drug"),
    ("dab rig",       "regulatory", "drug"),
    ("rolling paper", "regulatory", "drug"),
    ("grinder",       "regulatory", "drug_paraphernalia"),
    ("pipe",          "regulatory", "drug_paraphernalia"),
    # --- 医疗器械 ---
    ("medical device","regulatory", "medical"),
    ("prescription",  "regulatory", "medical"),
    ("otoscope",      "regulatory", "medical"),
    ("stethoscope",   "regulatory", "medical"),
    ("blood pressure","regulatory", "medical"),
    ("glucose monitor","regulatory", "medical"),
    ("syringe",       "regulatory", "medical"),
    ("surgical",      "regulatory", "medical"),
    ("dental",        "regulatory", "medical"),
    ("hearing aid",   "regulatory", "medical"),
    # --- 化妆品 ---
    ("cosmetic",      "regulatory", "cosmetic"),
    ("fragrance",     "regulatory", "cosmetic"),
    ("perfume",       "regulatory", "cosmetic"),
    ("cologne",       "regulatory", "cosmetic"),
    ("face mask",     "regulatory", "cosmetic"),  # 口罩除外, 类目路径已区分
    ("lipstick",      "regulatory", "cosmetic"),
    ("foundation",    "regulatory", "cosmetic"),
    ("skin care",     "regulatory", "cosmetic"),
    # --- 膳食补充剂 ---
    ("dietary supplement", "regulatory", "supplement"),
    ("vitamin",       "regulatory", "supplement"),
    ("probiotic",     "regulatory", "supplement"),
    ("herbal supplement", "regulatory", "supplement"),
    ("weight loss supplement", "regulatory", "supplement"),
    # --- 食品 ---
    ("pet food",      "regulatory", "pet_food"),
    ("baby food",     "regulatory", "food"),
    ("infant formula","regulatory", "food"),
    ("grocery",       "regulatory", "food"),
    ("raw meat",      "regulatory", "food"),
    ("fresh seafood", "regulatory", "food"),
    # --- 成人/性 ---
    ("erotic",        "regulatory", "adult"),
    ("adult novelty", "regulatory", "adult"),
    ("sex toy",       "regulatory", "adult"),
    ("sexual aid",    "regulatory", "adult"),
    ("fetish",        "regulatory", "adult"),
    # --- 化学品/有害 ---
    ("pesticide",     "regulatory", "chemical"),
    ("insecticide",   "regulatory", "chemical"),
    ("herbicide",     "regulatory", "chemical"),
    ("rodenticide",   "regulatory", "chemical"),
    ("lead paint",    "regulatory", "chemical"),
    ("asbestos",      "regulatory", "chemical"),
    # --- 野生动物制品 ---
    ("ivory",         "regulatory", "wildlife"),
    ("fur coat",      "regulatory", "wildlife"),
    ("real fur",      "regulatory", "wildlife"),
    ("leopard skin",  "regulatory", "wildlife"),
    # --- 活体动物 ---
    ("live animal",   "regulatory", "live_animal"),
    ("live fish",     "regulatory", "live_animal"),
]

# 兼容词 regex → 抽取候选品牌名
COMPAT_RE = [
    re.compile(r"\b(?:for|compatible\s+with|fits|replaces?|replacement\s+for)\s+([A-Z][A-Za-z0-9][A-Za-z0-9\s&\-]{1,40}?)(?=\s+(?:[a-z]|\d|,|\.|;|for|compatible|with)|$)", re.IGNORECASE),
]

# IP 真实性声明 (搬运场景极敏感) — 强信号词 + 强搭配短语
AUTHENTICITY_RE = re.compile(
    r"\b(?:"
    r"authentic|genuine|official\s+(?:product|merchandise|brand)|"
    r"100%\s*(?:original|authentic)|"
    r"brand\s+new\s+original|"
    r"OEM\s+(?:replacement|original|part)|"
    r"factory\s+sealed|"
    r"direct\s+from\s+manufacturer|direct\s+from\s+factory|"
    r"certified\s+(?:original|authentic|genuine)|"
    r"licensed\s+(?:product|reseller|merchandise)|"
    r"limited\s+edition|collector'?s\s+(?:edition|item)|"
    r"heritage\s+collection|"
    r"proprietary\s+design"
    r")\b",
    re.I,
)

# IP 关键词的歧义词集合 (hard_block → warn 降级)
IP_AMBIGUOUS_WORDS = {
    "AMAZON",   # 平台名, 描述中常见 "amazon.com" / "available on amazon"
    "SWITCH",   # 普通动词 "switch on/off"
    "APPLE",    # 水果/常用词
    "PIXEL",    # 图像学常用词
    "FIRE TV",  # 组合词但 Fire 本身常用
    "JORDAN",   # 人名/地名
}


def load_lexicons(conn):
    """一次性加载词库 (供批量审核复用)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT term, term_normalized, category, severity
        FROM offensive_lexicon
    """)
    offensive = cur.fetchall()
    cur.execute("""
        SELECT pattern, pattern_type, trigger_category, severity
        FROM ip_trigger_terms
        WHERE pattern_type = 'keyword'
    """)
    ip_terms = cur.fetchall()
    cur.close()
    return {"offensive": offensive, "ip_keywords": ip_terms}


def _full_text(product: Dict) -> str:
    parts = [
        product.get("title") or "",
        product.get("bullet_points") or "",
        product.get("long_description") or "",
        product.get("product_type") or "",
    ]
    return " ".join(parts)


# 不作为 ASIN 直击信号的 reason_category (可修复 / 非产品本身问题)
# - 类目映射问题 (用户持续优化类目映射, 不作历史教训)
# - 运维类 (tax code / end date / pricing, 非合规违规)
# - 无原因/系统错误 (数据源噪声)
ASIN_HIT_EXCLUDED_REASONS = {
    "prohibited_generic",    # ProductType 选错, 靠 A-3 映射解决
    "end_date",              # 运维
    "tax_code", "no_price", "pricing",
    "system_error",
    "no_reason",
    "internal_flag",         # 沃尔玛团队标记, 未给原因
    "other",
    "refurbished",           # 翻新政策, 改写标题可解
}


def rule_asin_hit(product: Dict, conn) -> List[Dict]:
    """
    ASIN 历史直击: 只用"真合规违规"类别做硬拒信号
    排除 ProductType 选错 / 运维 / 系统错误 — 这些可通过其他手段修复
    """
    asin = product.get("asin")
    if not asin:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT reason_category, COUNT(*) hits, BOOL_OR(is_deleted) any_del,
               STRING_AGG(DISTINCT source_date::text, ', ' ORDER BY source_date::text) dates,
               STRING_AGG(DISTINCT walmart_sku, ', ') skus
        FROM walmart_suspension_history
        WHERE amazon_asin = %s
          AND NOT (reason_category = ANY(%s))
        GROUP BY reason_category
    """, (asin, list(ASIN_HIT_EXCLUDED_REASONS)))
    rows = cur.fetchall()
    cur.close()
    flags = []
    for reason_cat, hits, any_del, dates, skus in rows:
        severity = "hard_block" if any_del else "warn"
        flags.append({
            "flag_type": "historical_recall",
            "flag_category": "historical",
            "flag_code": f"asin_history_{reason_cat}",
            "description": f"ASIN {asin} 历史真违规 {hits} 次 ({reason_cat})",
            "severity": severity,
            "evidence": {
                "asin": asin, "reason_category": reason_cat, "hits": hits,
                "deleted": any_del, "dates": dates, "skus": skus[:200] if skus else "",
            },
        })
    return flags


def rule_category_keyword(product: Dict) -> List[Dict]:
    cat_path = (product.get("category_path") or "").lower()
    if not cat_path:
        return []
    flags = []
    for kw, flag_cat, sub in CATEGORY_HARD_KEYWORDS:
        if kw in cat_path:
            flags.append({
                "flag_type": "rule_hit",
                "flag_category": flag_cat,
                "flag_code": f"cat_keyword_{sub}",
                "description": f'类目路径含硬禁词 "{kw}" (类别: {sub})',
                "severity": "hard_block",
                "evidence": {"term": kw, "sub": sub, "path": cat_path},
            })
    return flags


# "gun" 家族的工具语境白名单 (非武器)
GUN_TOOL_CONTEXTS = re.compile(
    r"\b(?:nail|glue|staple|caulk|caulking|heat|piping|pipe|spray|grease|solder(?:ing)?|"
    r"paint|pressure|water|toy|squirt|bb|foam|dart|airsoft|rivet|riveting|brad|hot|"
    r"silicone|adhesive|welding|blow|icing|frosting|decorating|cookie|pastry|"
    r"confectionery|dispensing|pie|cake|sausage|jerky|cookie|cream|whipped|batter|"
    r"bleach|mastic|epoxy|putty|gel|fuel|wash|clay)\s+guns?\b",
    re.IGNORECASE,
)
# 类目级白名单 (Kitchen/Baking/Home Improvement 等): gun 词在此类目下默认非武器
SAFE_GUN_CATEGORY_RE = re.compile(
    r"(Kitchen|Baking|Bakeware|Dining|Cooking|Cake|Dessert|Pastry|Confection|"
    r"Home Improvement|Tools|Hardware|Automotive|Garden|Lawn|Arts?, Crafts?|"
    r"Office|Janitorial|Painting|Adhesive|Sealant|Glue|Welding|Soldering)",
    re.IGNORECASE,
)


def rule_offensive_keyword(product: Dict, offensive_terms) -> List[Dict]:
    text_lower = _full_text(product).lower()
    cat_path = product.get("category_path") or ""
    # 预判: 工具短语 或 安全类目 → 跳过 gun 相关匹配
    gun_tool_hit = bool(GUN_TOOL_CONTEXTS.search(text_lower)) or bool(SAFE_GUN_CATEGORY_RE.search(cat_path))
    flags = []
    for term, term_norm, category, severity in offensive_terms:
        pat = r"\b" + re.escape(term_norm) + r"\b"
        if re.search(pat, text_lower):
            # gun 相关词在工具上下文中跳过
            if gun_tool_hit and term_norm in ("gun", "pistol", "rifle", "bullet"):
                continue
            flags.append({
                "flag_type": "rule_hit",
                "flag_category": "offensive",
                "flag_code": f"offensive_{category}",
                "description": f'含冒犯词 "{term}" (类别: {category})',
                "severity": severity,
                "evidence": {"term": term, "category": category},
            })
    return flags


def rule_ip_keyword(product: Dict, ip_keyword_terms) -> List[Dict]:
    """IP 品牌 keyword 直接命中"""
    text = _full_text(product)
    brand_claim = (product.get("brand") or "").strip().lower()
    flags = []
    # 若产品声称的品牌就是该 IP (unbranded 除外), 跳过 (自营品牌无侵权)
    claim_is_branded = brand_claim and brand_claim not in ("unbranded", "generic", "")

    for pattern, pat_type, trig_cat, severity in ip_keyword_terms:
        pat = re.compile(r"\b" + re.escape(pattern) + r"\b", re.IGNORECASE)
        m = pat.search(text)
        if not m:
            continue
        # 自营品牌例外
        if claim_is_branded and pattern.lower() == brand_claim:
            continue
        # 歧义词降级 hard_block → warn
        effective_severity = severity
        if pattern.upper() in IP_AMBIGUOUS_WORDS:
            if severity == "hard_block":
                effective_severity = "warn"
        # "amazon.com" 上下文直接跳过 ("Amazon" 作为 URL 非侵权)
        if pattern.upper() == "AMAZON":
            snippet_start = max(0, m.start() - 10)
            snippet_end = min(len(text), m.end() + 10)
            ctx = text[snippet_start:snippet_end].lower()
            if ".com" in ctx or "m.media" in ctx or "amazon.com" in ctx:
                continue
        flags.append({
            "flag_type": "rule_hit",
            "flag_category": "ip",
            "flag_code": f"ip_{trig_cat}",
            "description": f'描述含品牌/IP "{pattern}" (类型: {trig_cat})',
            "severity": effective_severity,
            "evidence": {"pattern": pattern, "category": trig_cat, "match": m.group(0)[:80]},
        })
    return flags


_COMPAT_CACHE: Dict[str, List[Dict]] = {}  # 候选品牌名 → 撞库结果 (批量共享)


# 兼容词场景中极常见但通常不构成侵权的词 (USPTO 中可能有注册但都是泛用词)
COMPAT_STOPWORDS = {
    "SALE", "HOME", "LIFE", "KITCHEN", "CAR", "BIKE", "YOU", "YOUR", "THIS", "THE",
    "USE", "ALL", "ANY", "MANY", "MOST", "SOME", "OTHER", "OTHERS", "MORE", "LESS",
    "BEST", "GOOD", "BETTER", "NEW", "OLD", "BIG", "SMALL", "LARGE", "MEDIUM",
    "OFFICE", "SCHOOL", "HOUSE", "APARTMENT", "GARDEN", "YARD", "OUTDOOR", "INDOOR",
    "BATHROOM", "BEDROOM", "LIVING", "DINING", "GARAGE", "BASEMENT", "PATIO",
    "EASY", "SIMPLE", "FAST", "QUICK", "HEAVY", "LIGHT",
    "PETS", "CATS", "DOGS", "PET",
    "MEN", "WOMEN", "KIDS", "CHILDREN", "BABY", "BOYS", "GIRLS",
    "EVERYDAY", "DAILY", "GIFT", "GIFTS", "SET", "PACK", "PIECES", "PCS",
    "STANDARD", "DELUXE", "PREMIUM", "PRO", "PLUS", "BASIC", "ECONOMY",
    "METAL", "PLASTIC", "WOOD", "GLASS", "CERAMIC", "LEATHER",
    "BLACK", "WHITE", "RED", "BLUE", "GREEN", "YELLOW", "GRAY", "GREY", "SILVER",
    "GOLD", "BROWN", "ORANGE", "PURPLE", "PINK", "CLEAR", "TRANSPARENT",
    "COMPATIBLE", "FITS", "REPLACES", "REPLACEMENT", "UNIVERSAL",
    "FORD", "DODGE", "JEEP",  # 汽车品牌兼容词太常见, 此类场景合法 (放到 warn)
}


def extract_compat_candidates(product: Dict) -> set:
    """从 title/desc 抽所有兼容词候选品牌名"""
    text = _full_text(product)
    candidates = set()
    for rx in COMPAT_RE:
        for m in rx.finditer(text):
            cand = m.group(1).strip().rstrip(",.")
            if len(cand) < 3 or len(cand) > 40:
                continue
            cand_upper = cand.upper()
            if cand_upper in COMPAT_STOPWORDS:
                continue
            # 单词过短(<=4 个字母)且不含大写多词连接 → 概率是泛用词, 跳过
            if len(cand_upper) <= 4 and " " not in cand_upper:
                continue
            candidates.add(cand_upper)
    return candidates


def prefetch_trademark_hits(conn, candidates: set):
    """批量预查一批候选词是否撞 USPTO LIVE, 一次性 IN 查询, 填入缓存"""
    new_cands = [c for c in candidates if c not in _COMPAT_CACHE]
    if not new_cands:
        return
    cur = conn.cursor()
    # 一次批量查询 (用 = ANY(array), 走 btree 索引)
    cur.execute("""
        SELECT t.mark_identification, t.serial_number, t.status_code, o.party_name
        FROM trademarks t
        LEFT JOIN trademark_owners o ON t.serial_number = o.serial_number
        LEFT JOIN status_code_mapping m ON t.status_code = m.status_code
        WHERE t.mark_identification = ANY(%s::text[])
          AND m.live_dead = 'LIVE'
          AND length(t.mark_identification) <= 200
    """, (new_cands,))
    # 将结果按 mark 分组到 _COMPAT_CACHE
    per_cand = {c: [] for c in new_cands}
    for r in cur.fetchall():
        key = r[0]  # USPTO 标准全大写
        if key in per_cand and len(per_cand[key]) < 3:
            per_cand[key].append({
                "mark": r[0], "serial": str(r[1]), "status": r[2], "owner": r[3],
            })
    _COMPAT_CACHE.update(per_cand)
    cur.close()


def rule_compat_trademark(product: Dict, conn) -> List[Dict]:
    """兼容词抽取 'for X / compatible with X' 中的 X, 查 USPTO LIVE trademarks (复用缓存)"""
    candidates = extract_compat_candidates(product)
    if not candidates:
        return []
    prefetch_trademark_hits(conn, candidates)

    flags = []
    for cand in candidates:
        hits = _COMPAT_CACHE.get(cand, [])
        if not hits:
            continue
        # 多词候选 (如 "Harley Davidson"), 更像真品牌 → hard_block
        # 单词 + 5+ 字母 → warn (可能是兼容词合法场景, 交给 LLM 二次确认)
        is_multi_word = " " in cand or "-" in cand
        severity = "hard_block" if is_multi_word else "warn"
        flags.append({
            "flag_type": "rule_hit",
            "flag_category": "ip",
            "flag_code": "compat_live_trademark",
            "description": f'描述兼容词 "{cand}" 撞 USPTO LIVE 商标 ({len(hits)} 条)',
            "severity": severity,
            "evidence": {"candidate": cand, "marks": hits[:2]},
        })
    return flags


def rule_authenticity_claim(product: Dict) -> List[Dict]:
    """'authentic/genuine/original/official' 声明 — 搬运场景极敏感"""
    text = _full_text(product)
    m = AUTHENTICITY_RE.search(text)
    if not m:
        return []
    return [{
        "flag_type": "rule_hit",
        "flag_category": "counterfeit",
        "flag_code": "authenticity_claim",
        "description": f'描述含真实性声明 "{m.group(0)}" (搬运场景易被判仿品)',
        "severity": "warn",
        "evidence": {"match": m.group(0), "snippet": text[max(0, m.start()-40):m.end()+40]},
    }]


def rule_default_ptype_risk(product: Dict) -> List[Dict]:
    """Amazon 商品类型空 / N/A — 上架 Walmart 时很可能选成 default"""
    apt = (product.get("product_type") or "").strip()
    if not apt or apt.upper() in ("N/A", "NONE"):
        return [{
            "flag_type": "rule_hit",
            "flag_category": "product_type",
            "flag_code": "amazon_ptype_missing",
            "description": "Amazon 商品类型为空, 上架时极易选成 Walmart default (100% 暂停风险)",
            "severity": "warn",
            "evidence": {"amazon_product_type": apt},
        }]
    return []


# 搬运不可绕过的硬认证 (在 Walmart 映射表的认证字段里命中即拒)
HARD_CERT_RE = re.compile(
    r"CPC\b|510\(k\)|MoCRA|\bFCC\s*认证|\bUL\s*认证|\bETL\b|\bEPA\b|\bFinCEN|"
    r"\bSCCP|联邦专营|独家授权|FinCEN|RED\s*Cert",
    re.I,
)


def rule_ptype_mapping(product: Dict, conn) -> List[Dict]:
    """
    Amazon 类目 → Walmart ProductType 映射 (基于用户提供的 v9 映射表)
    保守触发策略 (避免大量 warn 堆积):
    - 匹到硬认证 (CPC/510(k)/MoCRA/FCC/UL/ETL/EPA/FinCEN) → hard_block
    - 匹到 IP 风险=高 且置信度 ≥ 0.85 → warn (高置信度才标)
    - 未匹配/软合规 → 不标 flag (交 LLM 判断)
    """
    from audit_category_mapping import predict_walmart_ptype
    cands = predict_walmart_ptype(conn, amazon_path=product.get("category_path"))
    if not cands:
        return []

    top = cands[0]
    flags = []
    cert = top.get("cert_required") or ""
    ip_risk = (top.get("ip_risk") or "").strip()
    conf = top.get("confidence") or 0

    if HARD_CERT_RE.search(cert):
        flags.append({
            "flag_type": "rule_hit",
            "flag_category": "regulatory",
            "flag_code": "ptype_hard_cert_required",
            "description": (
                f'推荐 Walmart PT "{top["walmart_product_type"]}" '
                f'需硬认证 ({cert[:80]}), 搬运场景无法提供'
            ),
            "severity": "hard_block",
            "evidence": {
                "walmart_product_type": top["walmart_product_type"],
                "walmart_category": top["walmart_category"],
                "cert_required": cert, "ip_risk": ip_risk,
                "match_level": top["match_level"],
                "confidence": conf,
            },
        })
    elif ip_risk == "高" and conf >= 0.85:
        flags.append({
            "flag_type": "rule_hit",
            "flag_category": "ip",
            "flag_code": "ptype_high_ip_risk",
            "description": (
                f'推荐 Walmart PT "{top["walmart_product_type"]}" IP 风险高: '
                f'{(top.get("compliance_notes") or "")[:100]}'
            ),
            "severity": "warn",
            "evidence": {
                "walmart_product_type": top["walmart_product_type"],
                "ip_risk": ip_risk,
                "compliance_notes": top.get("compliance_notes"),
                "match_level": top["match_level"],
                "confidence": conf,
            },
        })
    return flags


# ==========================================================================
# 主入口
# ==========================================================================

def audit_product(product: Dict, conn, lexicons=None) -> Dict:
    """
    对一条 products_stage 行做 L1 审核
    """
    if lexicons is None:
        lexicons = load_lexicons(conn)

    all_flags = []
    all_flags.extend(rule_asin_hit(product, conn))
    all_flags.extend(rule_category_keyword(product))
    all_flags.extend(rule_offensive_keyword(product, lexicons["offensive"]))
    all_flags.extend(rule_ip_keyword(product, lexicons["ip_keywords"]))
    all_flags.extend(rule_compat_trademark(product, conn))
    all_flags.extend(rule_authenticity_claim(product))
    all_flags.extend(rule_ptype_mapping(product, conn))
    # 相似度召回 (B-3): 对标题与历史违规做 trigram 相似, 命中 warn/hard_block
    # 永远排除自身 ASIN (正常采集场景 ASIN 不在 history 里无影响; 回测场景避免自撞作弊)
    from audit_recall import rule_historical_similarity
    all_flags.extend(rule_historical_similarity(product, conn, exclude_asin=product.get("asin")))

    # 按 category 计算风险分
    def risk_for(cat):
        score = 0
        for f in all_flags:
            if f["flag_category"] == cat:
                score += 60 if f["severity"] == "hard_block" else 25
        return min(100, score)

    ip_risk = risk_for("ip")
    offensive_risk = risk_for("offensive")
    regulatory_risk = max(risk_for("regulatory"), risk_for("historical"))
    counterfeit_risk = risk_for("counterfeit")
    overall_risk = max(ip_risk, offensive_risk, regulatory_risk, counterfeit_risk,
                       risk_for("product_type") // 2)

    # 决策
    hard = any(f["severity"] == "hard_block" for f in all_flags)
    warn = any(f["severity"] == "warn" for f in all_flags)
    if hard:
        verdict = "reject"
    elif warn:
        verdict = "hold_manual"
    else:
        verdict = "approve"

    reason_summary = (
        "; ".join(f["description"] for f in all_flags[:3]) if all_flags else "无异常"
    )

    return {
        "verdict": verdict,
        "ip_risk": ip_risk,
        "offensive_risk": offensive_risk,
        "regulatory_risk": regulatory_risk,
        "counterfeit_risk": counterfeit_risk,
        "overall_risk": overall_risk,
        "reason_summary": reason_summary,
        "l1_triggered": len(all_flags) > 0,
        "flags": all_flags,
    }


# ==========================================================================
# CLI: 对 products_stage 里所有产品跑 L1, 写入 product_audits + audit_flags
# ==========================================================================

def run_batch(batch_file: str = None, verbose=True):
    """批量审核 products_stage 表"""
    import time
    from psycopg2.extras import Json, execute_values

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    if batch_file:
        cur.execute("""
            SELECT id, asin, batch_file, title, brand, product_type, manufacturer,
                   origin_country, bullet_points, long_description, image_urls,
                   upc, category_path, root_category_id, price
            FROM products_stage
            WHERE batch_file = %s
        """, (batch_file,))
    else:
        cur.execute("""
            SELECT id, asin, batch_file, title, brand, product_type, manufacturer,
                   origin_country, bullet_points, long_description, image_urls,
                   upc, category_path, root_category_id, price
            FROM products_stage
        """)
    cols = [c[0] for c in cur.description]
    products = [dict(zip(cols, r)) for r in cur.fetchall()]
    cur.close()

    if verbose:
        print(f"待审核: {len(products)} 产品", flush=True)

    lexicons = load_lexicons(conn)

    # 预提取所有兼容词候选, 一次性批量撞 trademarks 填缓存
    all_candidates = set()
    for p in products:
        all_candidates |= extract_compat_candidates(p)
    if verbose:
        print(f"预抽兼容词候选: {len(all_candidates)} 个", flush=True)
    if all_candidates:
        t_pf = time.time()
        prefetch_trademark_hits(conn, all_candidates)
        if verbose:
            hits = sum(1 for c in all_candidates if _COMPAT_CACHE.get(c))
            print(f"  USPTO 商标撞库: {hits}/{len(all_candidates)} 命中, 耗时 {time.time()-t_pf:.1f}s", flush=True)

    t0 = time.time()

    # 写入审核结果
    audit_rows = []
    flag_rows = []  # 暂存 (audit_row_index, flag_dict)
    verdicts = {"approve": 0, "hold_manual": 0, "reject": 0}

    for p in products:
        r = audit_product(p, conn, lexicons)
        verdicts[r["verdict"]] += 1
        audit_rows.append((
            p["id"], p["asin"], p["batch_file"],
            r["verdict"],
            r["ip_risk"], r["offensive_risk"], r["regulatory_risk"],
            r["counterfeit_risk"], r["overall_risk"],
            r["reason_summary"][:500] if r["reason_summary"] else None,
            r["l1_triggered"], False, False,  # l1/l2/l2_vision
            Json({"flags_count": len(r["flags"])}),
        ))
        for f in r["flags"]:
            flag_rows.append((len(audit_rows) - 1, f))

    # 批量写 product_audits
    cur = conn.cursor()
    cur.execute("DELETE FROM product_audits WHERE batch_file = %s",
                (batch_file,) if batch_file else (None,))
    # 更简单: 若指定 batch 则删该 batch; 否则全删
    if batch_file:
        cur.execute("DELETE FROM product_audits WHERE batch_file = %s", (batch_file,))
    else:
        cur.execute("DELETE FROM product_audits")

    returned = execute_values(cur, """
        INSERT INTO product_audits (
            stage_id, asin, batch_file, verdict,
            ip_risk, offensive_risk, regulatory_risk, counterfeit_risk, overall_risk,
            reason_summary, l1_triggered, l2_triggered, l2_vision_triggered,
            llm_raw_response
        ) VALUES %s RETURNING id
    """, audit_rows, page_size=500, fetch=True)
    audit_ids = [r[0] for r in returned]

    # 批量写 audit_flags
    flag_inserts = []
    for idx, f in flag_rows:
        audit_id = audit_ids[idx]
        flag_inserts.append((
            audit_id, f["flag_type"], f["flag_category"], f["flag_code"],
            f["description"][:500] if f.get("description") else None,
            f["severity"], Json(f.get("evidence") or {}),
        ))
    if flag_inserts:
        execute_values(cur, """
            INSERT INTO audit_flags (audit_id, flag_type, flag_category, flag_code,
                                      description, severity, evidence)
            VALUES %s
        """, flag_inserts, page_size=500)
    conn.commit()
    cur.close()
    conn.close()

    elapsed = time.time() - t0
    if verbose:
        print(f"审核完成: {len(products)} 产品, 耗时 {elapsed:.1f}s")
        print(f"  approve:      {verdicts['approve']} ({100*verdicts['approve']/len(products):.1f}%)")
        print(f"  hold_manual:  {verdicts['hold_manual']} ({100*verdicts['hold_manual']/len(products):.1f}%)")
        print(f"  reject:       {verdicts['reject']} ({100*verdicts['reject']/len(products):.1f}%)")
        print(f"  flags 总数:   {len(flag_inserts)}")
    return verdicts


if __name__ == "__main__":
    import sys
    batch = sys.argv[1] if len(sys.argv) > 1 else None
    run_batch(batch)
