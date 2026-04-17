"""
构建审核所需的词库和黑名单:
- offensive_lexicon: 冒犯词 (中英双语, 7 大类)
- ip_trigger_terms: IP 触发词 (兼容词 + 知名品牌 + 卡通 + 运动 + 奢侈)
- safe_category_whitelist: 类目黑名单扩展 (BIZ-CN / 受限类目从历史反推)

用法:
    python3 audit_lexicon_builder.py        # 全量重建
    python3 audit_lexicon_builder.py --only offensive | ip | categories
"""
import argparse

import psycopg2
from psycopg2.extras import execute_values


DB_CONN = "dbname=uspto user=nextderboy"


# ==========================================================================
# 冒犯词种子库 (7 大类, 双语)
# ==========================================================================

OFFENSIVE_SEEDS = {
    "religion": [  # 宗教符号/冒犯
        ("en", "swastika", "hard_block"),
        ("en", "nazi", "hard_block"),
        ("en", "ss bolts", "warn"),
        ("en", "blessed by allah", "warn"),
        ("en", "jesus christ", "warn"),
        ("en", "crucifix", "warn"),
        ("en", "satan", "warn"),
        ("en", "devil", "warn"),
        ("en", "pentagram", "warn"),
        ("en", "church of satan", "hard_block"),
        ("zh", "纳粹", "hard_block"),
        ("zh", "卍", "warn"),
        ("zh", "佛像", "warn"),
        ("zh", "圣经", "warn"),
        ("zh", "古兰经", "warn"),
    ],
    "race": [  # 种族/肤色/仇恨
        ("en", "white power", "hard_block"),
        ("en", "white supremacy", "hard_block"),
        ("en", "kkk", "hard_block"),
        ("en", "n-word", "hard_block"),
        ("en", "nigger", "hard_block"),
        ("en", "chink", "hard_block"),
        ("en", "gook", "hard_block"),
        ("en", "spic", "hard_block"),
        ("en", "wetback", "hard_block"),
        ("en", "redskin", "warn"),  # 部分场景 OK
        ("en", "slave", "warn"),
        ("en", "confederate flag", "hard_block"),
        ("zh", "支那", "hard_block"),
        ("zh", "黄猴子", "hard_block"),
    ],
    "politics": [  # 政治敏感
        ("en", "trump", "warn"),
        ("en", "biden", "warn"),
        ("en", "maga", "warn"),
        ("en", "antifa", "warn"),
        ("en", "isis", "hard_block"),
        ("en", "taliban", "hard_block"),
        ("en", "hamas", "hard_block"),
        ("en", "hezbollah", "hard_block"),
        ("en", "al qaeda", "hard_block"),
        ("en", "cuba", "warn"),  # OFAC
        ("en", "iran", "warn"),
        ("en", "north korea", "warn"),
        ("en", "syria", "warn"),
    ],
    "sexual": [  # 性暗示/色情
        ("en", "sex toy", "hard_block"),
        ("en", "dildo", "hard_block"),
        ("en", "vibrator", "warn"),  # 某些按摩器合法
        ("en", "adult content", "hard_block"),
        ("en", "xxx", "warn"),
        ("en", "porn", "hard_block"),
        ("en", "fetish", "warn"),
        ("en", "bondage", "warn"),
        ("en", "nude", "warn"),
        ("en", "erotic", "warn"),
        ("en", "lingerie", "warn"),
        ("en", "intimate", "warn"),
    ],
    "violence": [  # 暴力/武器
        ("en", "gun", "hard_block"),
        ("en", "pistol", "hard_block"),
        ("en", "rifle", "hard_block"),
        ("en", "ammunition", "hard_block"),
        ("en", "bullet", "warn"),
        ("en", "silencer", "hard_block"),
        ("en", "sniper", "warn"),
        ("en", "killer", "warn"),
        ("en", "murder", "warn"),
        ("en", "self defense", "hard_block"),  # 沃尔玛严格
        ("en", "self-defense", "hard_block"),
        ("en", "martial arts", "warn"),
        ("en", "brass knuckles", "hard_block"),
        ("en", "throwing knife", "hard_block"),
        ("en", "ninja", "warn"),
        ("en", "combat", "warn"),
        ("zh", "自卫", "warn"),
        ("zh", "武器", "hard_block"),
        ("zh", "刀具", "warn"),
    ],
    "drug": [  # 毒品/药物
        ("en", "cbd", "hard_block"),
        ("en", "cannabis", "hard_block"),
        ("en", "marijuana", "hard_block"),
        ("en", "weed", "warn"),
        ("en", "thc", "hard_block"),
        ("en", "kratom", "hard_block"),
        ("en", "kava", "warn"),
        ("en", "salvia", "warn"),
        ("en", "opium", "hard_block"),
        ("en", "heroin", "hard_block"),
        ("en", "cocaine", "hard_block"),
        ("en", "meth", "warn"),
        ("en", "psychedelic", "warn"),
        ("en", "hemp", "warn"),  # 某些合法
        ("en", "hgh", "hard_block"),
        ("en", "steroid", "warn"),
        ("en", "bong", "warn"),
        ("en", "pipe", "warn"),  # 烟具
        ("en", "rolling paper", "warn"),
        ("en", "herbal incense", "warn"),
    ],
    "weapon_false_positive": [  # 容易被沃尔玛误判为武器的"非武器"词 (用于规避)
        ("en", "self defense", "hard_block"),   # 即使是钥匙扣也会触发
        ("en", "personal protection", "hard_block"),
        ("en", "pepper spray", "hard_block"),
        ("en", "stun gun", "hard_block"),
        ("en", "taser", "hard_block"),
        ("en", "anti-theft", "warn"),           # 防盗类容易误伤
        ("en", "lockout", "warn"),
    ],
}


# ==========================================================================
# IP 触发词种子库
# ==========================================================================

# 兼容词 (compat_word): 描述中出现 "for X / compatible with X / replaces X" 时需抓 X
IP_COMPAT_PATTERNS = [
    (r"(?i)\bfor\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})", "compat_word", "for_brand", "regex"),
    (r"(?i)\bcompatible\s+with\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})", "compat_word", "compat_with", "regex"),
    (r"(?i)\bfits\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})", "compat_word", "fits_brand", "regex"),
    (r"(?i)\breplaces?\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})", "compat_word", "replaces_brand", "regex"),
    (r"(?i)\breplacement\s+for\s+([A-Z][A-Za-z0-9&\-]+(?:\s+[A-Z][A-Za-z0-9&\-]+){0,3})", "compat_word", "replacement_for", "regex"),
    (r"(?i)\blike\s+([A-Z][A-Za-z0-9&\-]+)\s+(style|brand|quality)", "compat_word", "like_x_style", "regex"),
    (r"(?i)\binspired\s+by\s+([A-Z][A-Za-z0-9&\-]+)", "compat_word", "inspired_by", "regex"),
    (r"(?i)\b([A-Z][A-Za-z0-9&\-]+)\s+style\b", "compat_word", "x_style", "regex"),
    (r"(?i)\bOEM\b", "compat_word", "oem_claim", "regex"),
    (r"(?i)\bgenuine\b", "ip_authenticity", "genuine_claim", "regex"),
    (r"(?i)\boriginal\b", "ip_authenticity", "original_claim", "regex"),
    (r"(?i)\bauthentic\b", "ip_authenticity", "authentic_claim", "regex"),
]

# 奢侈品 & 顶级品牌 (命中即拒)
LUXURY_BRANDS = [
    "Louis Vuitton", "LV", "Gucci", "Prada", "Hermes", "Chanel", "Dior",
    "Burberry", "Fendi", "Balenciaga", "Versace", "Armani", "Cartier",
    "Tiffany", "Bulgari", "Rolex", "Omega", "Patek Philippe",
    "Supreme", "Off-White", "Yeezy", "Palace",
]

# 运动品牌 (易撞)
SPORTS_BRANDS = [
    "Nike", "Adidas", "Puma", "Under Armour", "Reebok", "New Balance",
    "Converse", "Vans", "Asics", "The North Face", "Patagonia",
    "Columbia", "Lululemon", "Jordan",
]

# 科技巨头
TECH_BRANDS = [
    "Apple", "iPhone", "iPad", "MacBook", "AirPods",
    "Samsung", "Galaxy", "Google", "Pixel",
    "Microsoft", "Xbox", "PlayStation", "Sony", "Nintendo", "Switch",
    "Amazon", "Kindle", "Alexa", "Echo", "Fire TV",
    "Dyson", "Bose", "Beats", "GoPro",
]

# 汽车品牌 (汽车配件兼容词常撞)
AUTO_BRANDS = [
    "Ford", "Chevrolet", "Chevy", "Toyota", "Honda", "Nissan",
    "Mazda", "Subaru", "Hyundai", "Kia",
    "BMW", "Mercedes-Benz", "Audi", "Porsche", "Volkswagen", "VW",
    "Jeep", "Dodge", "Chrysler", "Ram", "GMC", "Cadillac", "Buick",
    "Tesla", "Harley-Davidson", "Harley",
]

# 迪士尼 / 卡通 IP
CARTOON_IPS = [
    "Disney", "Mickey Mouse", "Minnie Mouse", "Donald Duck", "Goofy",
    "Pixar", "Toy Story", "Frozen", "Elsa", "Anna", "Olaf",
    "Marvel", "Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk",
    "Avengers", "Black Panther", "Deadpool", "X-Men",
    "DC Comics", "Batman", "Superman", "Wonder Woman", "Joker",
    "Star Wars", "Darth Vader", "Yoda", "Baby Yoda", "Mandalorian",
    "Harry Potter", "Hogwarts", "Dumbledore",
    "Pokemon", "Pikachu",
    "Minions", "Shrek", "Kung Fu Panda",
    "Peppa Pig", "Paw Patrol", "Hello Kitty", "Sanrio",
    "Barbie", "Transformers", "Power Rangers",
    "SpongeBob", "Dora", "PJ Masks",
]

# 体育联赛/球队
SPORTS_LEAGUES = [
    "NFL", "NBA", "MLB", "NHL", "MLS", "FIFA", "UEFA",
    "Super Bowl", "World Cup", "Olympics",
]

# 著名大学/品牌 (常被印在 T 恤/水杯上)
COLLEGE_BRANDS = [
    "Harvard", "Yale", "Princeton", "MIT", "Stanford",
    "Cornell", "Columbia", "UCLA", "Berkeley", "NYU",
]


# ==========================================================================
# 从历史违规反推新词
# ==========================================================================

def extract_terms_from_history(conn):
    """从 reason_category in ('offensive', 'ip') 的产品标题里抽高频词"""
    cur = conn.cursor()
    # 抽 IP 类产品标题的第一个大写词组 (可能是品牌名)
    cur.execute("""
        SELECT title_clean, reason_category
        FROM walmart_suspension_history
        WHERE reason_category IN ('ip', 'offensive')
          AND title_clean IS NOT NULL
          AND length(title_clean) > 10
    """)
    results = cur.fetchall()
    cur.close()

    import re
    cap_re = re.compile(r"\b([A-Z][A-Za-z0-9]+(?:[\s\-][A-Z][A-Za-z0-9]+){0,2})\b")
    stopwords = {
        "The", "For", "With", "And", "Or", "New", "Pack", "Set", "Pcs", "Size",
        "Large", "Small", "Medium", "Inch", "Ft", "Lb", "Oz", "Ml", "Cm", "Mm",
        "Black", "White", "Red", "Blue", "Green", "Yellow", "Gray", "Grey", "Silver",
        "Gold", "Brown", "Orange", "Purple", "Pink",
        "Case", "Cover", "Holder", "Mount", "Adapter", "Cable", "Stand", "Bag",
        "Home", "Kitchen", "Car", "Bike", "Phone",
    }
    term_counts = {}
    for title, cat in results:
        for m in cap_re.findall(title or ""):
            term = m.strip()
            if term in stopwords:
                continue
            if len(term) < 3:
                continue
            key = (term.upper(), cat)
            term_counts[key] = term_counts.get(key, 0) + 1
    return sorted(term_counts.items(), key=lambda x: -x[1])


# ==========================================================================
# 写入 DB
# ==========================================================================

def build_offensive_lexicon(conn):
    cur = conn.cursor()
    cur.execute("TRUNCATE offensive_lexicon RESTART IDENTITY")
    values = []
    for category, items in OFFENSIVE_SEEDS.items():
        for lang, term, severity in items:
            values.append((term, term.lower(), lang, category, severity, "seed"))
    execute_values(cur,
        "INSERT INTO offensive_lexicon (term, term_normalized, language, category, severity, notes) "
        "VALUES %s ON CONFLICT (term_normalized, category) DO NOTHING",
        values
    )
    conn.commit()
    n = cur.rowcount
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT category) FROM offensive_lexicon")
    total, n_cat = cur.fetchone()
    cur.close()
    print(f"[offensive_lexicon] 插入 {len(values)} 条, 去重后 {total} 条, {n_cat} 类")
    return total


def build_ip_trigger_terms(conn):
    cur = conn.cursor()
    cur.execute("TRUNCATE ip_trigger_terms RESTART IDENTITY")
    values = []
    # 兼容词模式
    for pattern, trig_cat, severity_code, p_type in IP_COMPAT_PATTERNS:
        severity = "hard_block" if "compat" in trig_cat else "warn"
        values.append((pattern, p_type, trig_cat, severity, "兼容/仿品模式"))
    # 品牌关键词
    for brand in LUXURY_BRANDS:
        values.append((brand, "keyword", "luxury_brand", "hard_block", "奢侈品牌"))
    for brand in SPORTS_BRANDS:
        values.append((brand, "keyword", "sports_brand", "hard_block", "运动品牌"))
    for brand in TECH_BRANDS:
        values.append((brand, "keyword", "tech_brand", "hard_block", "科技品牌"))
    for brand in AUTO_BRANDS:
        values.append((brand, "keyword", "auto_brand", "warn", "汽车品牌 (兼容词部分合法)"))
    for ip in CARTOON_IPS:
        values.append((ip, "keyword", "cartoon_ip", "hard_block", "卡通/电影 IP"))
    for league in SPORTS_LEAGUES:
        values.append((league, "keyword", "sports_league", "hard_block", "体育联赛"))
    for college in COLLEGE_BRANDS:
        values.append((college, "keyword", "college_brand", "warn", "大学品牌"))

    execute_values(cur,
        "INSERT INTO ip_trigger_terms (pattern, pattern_type, trigger_category, severity, notes) "
        "VALUES %s ON CONFLICT (pattern) DO NOTHING",
        values
    )
    conn.commit()
    cur.execute("SELECT COUNT(*), COUNT(DISTINCT trigger_category) FROM ip_trigger_terms")
    total, n_cat = cur.fetchone()
    cur.close()
    print(f"[ip_trigger_terms] 插入 {len(values)} 条, 去重后 {total} 条, {n_cat} 类")
    return total


def build_category_blacklist(conn):
    """从历史违规反推: 高风险 ProductType 加入黑名单 (allowed=false)"""
    cur = conn.cursor()
    cur.execute("TRUNCATE safe_category_whitelist RESTART IDENTITY")

    # 1. BIZ-CN 类目: 中国卖家硬禁
    cur.execute("""
        SELECT product_type, COUNT(DISTINCT walmart_sku) n
        FROM walmart_suspension_history
        WHERE reason_category = 'biz_cn_restriction'
          AND product_type IS NOT NULL
        GROUP BY product_type
        HAVING COUNT(DISTINCT walmart_sku) >= 3
    """)
    biz_cn_types = cur.fetchall()

    # 2. 受限类目 (regulatory_*) : 需认证无法通过
    cur.execute("""
        SELECT product_type, reason_category, COUNT(DISTINCT walmart_sku) n
        FROM walmart_suspension_history
        WHERE reason_category LIKE 'regulatory_%'
          AND product_type IS NOT NULL
        GROUP BY product_type, reason_category
    """)
    reg_types = cur.fetchall()

    # 3. 品牌独占 (biz_brand_exclusive)
    cur.execute("""
        SELECT product_type, COUNT(DISTINCT walmart_sku) n
        FROM walmart_suspension_history
        WHERE reason_category = 'biz_brand_exclusive'
          AND product_type IS NOT NULL
        GROUP BY product_type
        HAVING COUNT(DISTINCT walmart_sku) >= 2
    """)
    exclusive_types = cur.fetchall()

    # 按 ProductType 聚合 (一个类目可能多个原因)
    def _cert_for(reason_cat):
        if reason_cat == "biz_cn_restriction": return "biz_cn_block"
        if reason_cat == "biz_brand_exclusive": return "biz_brand_block"
        if reason_cat == "regulatory_children": return "CPC"
        if reason_cat in ("regulatory_cosmetic", "regulatory_medical", "regulatory_supplement"): return "FDA"
        if reason_cat == "regulatory_pet": return "EPA"
        if reason_cat == "regulatory_firearm": return "FinCEN"
        return "other_cert"

    ptype_bucket = {}  # ptype → {reasons: set, n_skus: int, notes: list}
    for ptype, n in biz_cn_types:
        b = ptype_bucket.setdefault(ptype, {"reasons": set(), "n": 0, "notes": []})
        b["reasons"].add("biz_cn_restriction")
        b["n"] += n
        b["notes"].append(f"biz_cn:{n}")
    for ptype, reason_cat, n in reg_types:
        b = ptype_bucket.setdefault(ptype, {"reasons": set(), "n": 0, "notes": []})
        b["reasons"].add(reason_cat)
        b["n"] += n
        b["notes"].append(f"{reason_cat}:{n}")
    for ptype, n in exclusive_types:
        b = ptype_bucket.setdefault(ptype, {"reasons": set(), "n": 0, "notes": []})
        b["reasons"].add("biz_brand_exclusive")
        b["n"] += n
        b["notes"].append(f"biz_brand:{n}")

    rows = [
        ("Walmart ProductType=default", "default", False, "high", "none", False,
         ["default_productype"], "选不出正确类目的兜底, 100% 暂停, 必须禁用"),
    ]
    for ptype, info in ptype_bucket.items():
        reasons_list = sorted(info["reasons"])
        primary_reason = reasons_list[0]
        cert = _cert_for(primary_reason)
        rows.append((
            f"WalmartPtype={ptype}",
            ptype,
            False,  # shop_focus
            "high",
            cert,
            False,  # allowed
            reasons_list,
            " + ".join(info["notes"]),
        ))

    cur.execute("TRUNCATE safe_category_whitelist RESTART IDENTITY")
    execute_values(cur,
        """INSERT INTO safe_category_whitelist
           (amazon_path_prefix, recommended_walmart_type, shop_focus, ip_risk_level,
            cert_required, allowed, sub_risks, notes)
           VALUES %s""",
        rows
    )
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM safe_category_whitelist WHERE allowed = FALSE")
    blocked = cur.fetchone()[0]
    cur.close()
    print(f"[safe_category_whitelist] 黑名单类目 {blocked} 条 (default + BIZ-CN + BIZ + 受限)")
    return blocked


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=["offensive", "ip", "categories"])
    args = p.parse_args()

    conn = psycopg2.connect(DB_CONN)
    if args.only in (None, "offensive"):
        build_offensive_lexicon(conn)
    if args.only in (None, "ip"):
        build_ip_trigger_terms(conn)
    if args.only in (None, "categories"):
        build_category_blacklist(conn)

    # 统计
    cur = conn.cursor()
    print("\n=== 词库汇总 ===")
    for tbl in ("offensive_lexicon", "ip_trigger_terms", "safe_category_whitelist"):
        cur.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"  {tbl}: {cur.fetchone()[0]}")

    # 历史违规反推
    print("\n=== 历史 IP/offensive 标题高频词 (top 20) ===")
    terms = extract_terms_from_history(conn)
    for (term, cat), cnt in terms[:20]:
        print(f"  [{cat}] {term}: {cnt}")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
