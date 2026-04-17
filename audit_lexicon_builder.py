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
        ("en", "hitler", "hard_block"),
        ("en", "ss bolts", "warn"),
        ("en", "blessed by allah", "warn"),
        ("en", "jesus christ", "warn"),
        ("en", "crucifix", "warn"),
        ("en", "rosary", "warn"),
        ("en", "prayer beads", "warn"),
        ("en", "satan", "warn"),
        ("en", "satanic", "warn"),
        ("en", "devil", "warn"),
        ("en", "demonic", "warn"),
        ("en", "pentagram", "warn"),
        ("en", "upside down cross", "warn"),
        ("en", "church of satan", "hard_block"),
        ("en", "ouija", "warn"),
        ("en", "occult", "warn"),
        ("en", "tarot", "warn"),
        ("en", "voodoo", "warn"),
        ("en", "wiccan", "warn"),
        ("en", "mecca", "warn"),
        ("en", "prayer rug", "warn"),
        ("zh", "纳粹", "hard_block"),
        ("zh", "卍", "warn"),
        ("zh", "佛像", "warn"),
        ("zh", "菩萨", "warn"),
        ("zh", "圣经", "warn"),
        ("zh", "古兰经", "warn"),
        ("zh", "十字架", "warn"),
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
        ("en", "anal", "hard_block"),
        ("en", "butt plug", "hard_block"),
        ("en", "penis", "hard_block"),
        ("en", "vagina", "hard_block"),
        ("en", "vibrator", "warn"),
        ("en", "adult content", "hard_block"),
        ("en", "adult novelty", "hard_block"),
        ("en", "xxx", "warn"),
        ("en", "porn", "hard_block"),
        ("en", "pornography", "hard_block"),
        ("en", "pornographic", "hard_block"),
        ("en", "fetish", "warn"),
        ("en", "bondage", "warn"),
        ("en", "bdsm", "warn"),
        ("en", "kink", "warn"),
        ("en", "nude", "warn"),
        ("en", "naked", "warn"),
        ("en", "erotic", "warn"),
        ("en", "lingerie", "warn"),
        ("en", "intimate", "warn"),
        ("en", "g-spot", "hard_block"),
        ("en", "prostate massager", "hard_block"),
        ("en", "couples toy", "warn"),
        ("en", "orgasm", "hard_block"),
        ("en", "sensual", "warn"),
    ],
    "violence": [  # 暴力/武器
        ("en", "gun", "warn"),  # 有工具上下文豁免, 不硬拒
        ("en", "pistol", "warn"),
        ("en", "rifle", "hard_block"),
        ("en", "shotgun", "hard_block"),
        ("en", "assault", "warn"),
        ("en", "firearm", "hard_block"),
        ("en", "ammunition", "hard_block"),
        ("en", "ammo", "hard_block"),
        ("en", "bullet", "warn"),
        ("en", "cartridge", "warn"),
        ("en", "magazine clip", "warn"),
        ("en", "silencer", "hard_block"),
        ("en", "suppressor", "warn"),
        ("en", "sniper", "warn"),
        ("en", "killer", "warn"),
        ("en", "murder", "warn"),
        ("en", "suicide", "warn"),
        ("en", "self harm", "warn"),
        ("en", "cutting", "warn"),
        ("en", "self defense", "hard_block"),
        ("en", "self-defense", "hard_block"),
        ("en", "martial arts", "warn"),
        ("en", "brass knuckles", "hard_block"),
        ("en", "throwing knife", "hard_block"),
        ("en", "dagger", "hard_block"),
        ("en", "bayonet", "hard_block"),
        ("en", "machete", "hard_block"),
        ("en", "katana", "warn"),
        ("en", "samurai sword", "warn"),
        ("en", "butterfly knife", "hard_block"),
        ("en", "karambit", "hard_block"),
        ("en", "nunchuck", "hard_block"),
        ("en", "nunchaku", "hard_block"),
        ("en", "tomahawk", "warn"),
        ("en", "hatchet", "warn"),
        ("en", "ninja", "warn"),
        ("en", "combat", "warn"),
        ("en", "tactical knife", "hard_block"),
        ("en", "crossbow", "hard_block"),
        ("en", "compound bow", "warn"),
        ("en", "blowgun", "hard_block"),
        ("en", "slingshot", "warn"),
        ("en", "catapult", "warn"),
        ("zh", "自卫", "warn"),
        ("zh", "武器", "hard_block"),
        ("zh", "刀具", "warn"),
    ],
    "drug": [  # 毒品/药物/管制药
        ("en", "cbd", "hard_block"),
        ("en", "cannabis", "hard_block"),
        ("en", "marijuana", "hard_block"),
        ("en", "weed", "warn"),
        ("en", "thc", "hard_block"),
        ("en", "cbg", "warn"),
        ("en", "cbn", "warn"),
        ("en", "delta 8", "hard_block"),
        ("en", "delta-8", "hard_block"),
        ("en", "kratom", "hard_block"),
        ("en", "kava", "warn"),
        ("en", "salvia", "warn"),
        ("en", "opium", "hard_block"),
        ("en", "poppy seed", "warn"),
        ("en", "heroin", "hard_block"),
        ("en", "cocaine", "hard_block"),
        ("en", "meth", "warn"),
        ("en", "methamphetamine", "hard_block"),
        ("en", "psychedelic", "warn"),
        ("en", "lsd", "hard_block"),
        ("en", "mdma", "hard_block"),
        ("en", "mushroom", "warn"),
        ("en", "psilocybin", "hard_block"),
        ("en", "hemp", "warn"),
        ("en", "hgh", "hard_block"),
        ("en", "steroid", "warn"),
        ("en", "anabolic", "warn"),
        ("en", "testosterone", "warn"),
        ("en", "sarm", "warn"),
        ("en", "bong", "warn"),
        ("en", "pipe", "warn"),
        ("en", "dab rig", "warn"),
        ("en", "vape pen", "warn"),
        ("en", "vape mod", "warn"),
        ("en", "e-liquid", "warn"),
        ("en", "nicotine", "warn"),
        ("en", "rolling paper", "warn"),
        ("en", "herbal incense", "warn"),
        ("en", "research chemical", "hard_block"),
        ("en", "nootropic", "warn"),
        ("en", "benzo", "warn"),
        ("en", "xanax", "hard_block"),
        ("en", "adderall", "hard_block"),
        ("en", "oxycontin", "hard_block"),
        ("en", "fentanyl", "hard_block"),
        ("en", "codeine", "hard_block"),
    ],
    "weapon_false_positive": [  # 沃尔玛特别严格词组 (即使是日用品也会误判为武器)
        ("en", "self defense", "hard_block"),
        ("en", "personal protection", "hard_block"),
        ("en", "pepper spray", "hard_block"),
        ("en", "mace spray", "hard_block"),
        ("en", "stun gun", "hard_block"),
        ("en", "taser", "hard_block"),
        ("en", "anti-theft", "warn"),
        ("en", "lockout", "warn"),
        ("en", "tactical", "warn"),
        ("en", "cosplay weapon", "warn"),  # 虽然是 prop 但易误判
        ("en", "replica gun", "hard_block"),
        ("en", "foam blaster", "warn"),
        ("en", "foam dart", "warn"),
        ("en", "larp", "warn"),
        ("en", "live action role play", "warn"),
    ],
    "tobacco_adult": [  # 烟草制品
        ("en", "cigarette", "hard_block"),
        ("en", "cigar", "hard_block"),
        ("en", "tobacco", "hard_block"),
        ("en", "shisha", "hard_block"),
        ("en", "hookah", "hard_block"),
        ("en", "e-cigarette", "hard_block"),
        ("en", "vape", "warn"),
        ("en", "juul", "hard_block"),
        ("en", "nicotine pouch", "hard_block"),
    ],
    "alcohol": [
        ("en", "alcohol", "hard_block"),
        ("en", "beer", "hard_block"),
        ("en", "wine", "warn"),  # 酒瓶套/杯等周边合法, 酒本身硬拒
        ("en", "liquor", "hard_block"),
        ("en", "whiskey", "hard_block"),
        ("en", "vodka", "hard_block"),
        ("en", "rum", "warn"),
        ("en", "gin", "warn"),
        ("en", "tequila", "hard_block"),
        ("en", "sake", "warn"),
    ],
    "regulatory_keyword": [  # 合规敏感关键词 (需认证/受限)
        ("en", "n95", "warn"),
        ("en", "kn95", "warn"),
        ("en", "fda approved", "warn"),
        ("en", "ce certified", "warn"),
        ("en", "rohs", "warn"),
        ("en", "organic certified", "warn"),
        ("en", "cgmp", "warn"),
        ("en", "mercury", "warn"),
        ("en", "lead free", "warn"),
        ("en", "bpa free", "warn"),
        ("en", "asbestos", "hard_block"),
    ],
    "counterfeit_signal": [  # 仿品高危词 (搬运场景)
        ("en", "replica", "warn"),
        ("en", "inspired by", "warn"),
        ("en", "like original", "warn"),
        ("en", "high copy", "hard_block"),
        ("en", "1:1 copy", "hard_block"),
        ("en", "aaa quality", "hard_block"),
        ("en", "designer inspired", "hard_block"),
        ("en", "knockoff", "hard_block"),
        ("en", "dupe", "warn"),
        ("en", "fake", "warn"),
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
    "Tiffany", "Bulgari", "Bvlgari", "Rolex", "Omega", "Patek Philippe",
    "Audemars Piguet", "Breitling", "IWC", "Tag Heuer",
    "Supreme", "Off-White", "Yeezy", "Palace", "Bape",
    "Céline", "Celine", "Givenchy", "Saint Laurent", "YSL",
    "Valentino", "Bottega Veneta", "Loewe", "Mulberry",
    "Coach", "Michael Kors", "Kate Spade", "Tory Burch",
    "Rimowa", "Montblanc",
]

# 运动品牌
SPORTS_BRANDS = [
    "Nike", "Adidas", "Puma", "Under Armour", "Reebok", "New Balance",
    "Converse", "Vans", "Asics", "The North Face", "Patagonia",
    "Columbia", "Lululemon", "Jordan", "Yeezy",
    "Skechers", "Timberland", "Dr. Martens", "Birkenstock",
    "Fila", "Champion", "Kappa", "Mizuno", "Brooks", "Hoka",
    "Salomon", "Oakley", "Ray-Ban", "Maui Jim",
    "TaylorMade", "Callaway", "Titleist", "Wilson", "Spalding",
    "Fanatics",
]

# 科技巨头
TECH_BRANDS = [
    "Apple", "iPhone", "iPad", "MacBook", "AirPods", "iMac", "iWatch", "Mac Mini",
    "Samsung", "Galaxy", "Google", "Pixel",
    "Microsoft", "Xbox", "PlayStation", "Sony", "Nintendo", "Switch",
    "Amazon", "Kindle", "Alexa", "Echo", "Fire TV", "Ring", "Blink",
    "Dyson", "Bose", "Beats", "GoPro", "DJI", "Anker", "Razer", "Logitech",
    "Huawei", "Xiaomi", "OnePlus", "Oppo", "Vivo", "Redmi", "Honor",
    "Garmin", "Fitbit", "Polar",
    "HP", "Dell", "Lenovo", "ASUS", "Acer", "Razer",
    "Canon", "Nikon", "Fujifilm", "Leica",
    "Intel", "AMD", "NVIDIA", "Qualcomm",
]

# 汽车 / 摩托车品牌
AUTO_BRANDS = [
    "Ford", "Chevrolet", "Chevy", "Toyota", "Honda", "Nissan",
    "Mazda", "Subaru", "Hyundai", "Kia", "Lexus", "Infiniti", "Acura",
    "BMW", "Mercedes-Benz", "Mercedes", "Audi", "Porsche", "Volkswagen", "VW",
    "Volvo", "Land Rover", "Range Rover", "Jaguar", "Mini Cooper",
    "Jeep", "Dodge", "Chrysler", "Ram", "GMC", "Cadillac", "Buick", "Lincoln",
    "Tesla", "Rivian", "Lucid",
    "Lamborghini", "Ferrari", "Bugatti", "McLaren", "Maserati",
    "Rolls-Royce", "Rolls Royce", "Bentley", "Maybach", "Aston Martin",
    "Harley-Davidson", "Harley", "Indian Motorcycle",
    "Ducati", "Kawasaki", "Yamaha", "Suzuki", "Triumph",
]

# 迪士尼 / 卡通 / 动漫 / 游戏 IP
CARTOON_IPS = [
    # Disney
    "Disney", "Mickey Mouse", "Minnie Mouse", "Donald Duck", "Goofy",
    "Pixar", "Toy Story", "Frozen", "Elsa", "Anna", "Olaf",
    "Moana", "Mulan", "Aladdin", "Cinderella", "Snow White", "Lion King",
    "Beauty and the Beast", "Little Mermaid", "Tangled",
    # Marvel / DC
    "Marvel", "Spider-Man", "Iron Man", "Captain America", "Thor", "Hulk",
    "Avengers", "Black Panther", "Deadpool", "X-Men", "Wolverine", "Venom",
    "Guardians of the Galaxy", "Doctor Strange", "Ant-Man",
    "DC Comics", "Batman", "Superman", "Wonder Woman", "Joker",
    "Aquaman", "Flash", "Green Lantern", "Harley Quinn",
    # Star Wars / Harry Potter
    "Star Wars", "Darth Vader", "Yoda", "Baby Yoda", "Mandalorian",
    "Luke Skywalker", "Chewbacca", "Stormtrooper", "Lightsaber",
    "Harry Potter", "Hogwarts", "Dumbledore", "Hermione", "Voldemort",
    # 日本动漫
    "Pokemon", "Pikachu", "Bulbasaur", "Charmander",
    "Naruto", "One Piece", "Attack on Titan", "Demon Slayer", "Dragon Ball",
    "My Hero Academia", "Jujutsu Kaisen", "Bleach", "Death Note",
    "Studio Ghibli", "Totoro", "Spirited Away",
    # 动画片 & 角色
    "Minions", "Shrek", "Kung Fu Panda", "How to Train Your Dragon",
    "Peppa Pig", "Paw Patrol", "Hello Kitty", "Sanrio",
    "Barbie", "Bratz", "Transformers", "Power Rangers",
    "SpongeBob", "Dora", "PJ Masks", "Bluey", "Cocomelon",
    "Sesame Street", "Elmo", "Big Bird",
    "Tom and Jerry", "Looney Tunes", "Bugs Bunny",
    # 游戏 IP
    "Minecraft", "Fortnite", "Roblox", "Call of Duty", "Halo",
    "Super Mario", "Mario", "Luigi", "Zelda", "Link",
    "Sonic", "Pac-Man", "Tetris",
    "League of Legends", "World of Warcraft", "Overwatch",
    "Grand Theft Auto", "GTA", "Final Fantasy",
    # 玩具 IP
    "LEGO", "Hot Wheels", "Transformers", "Fisher-Price", "Nerf",
    "Rubik's Cube", "Tonka", "Monopoly", "Play-Doh",
]

# 体育联赛/球队/运动员
SPORTS_LEAGUES = [
    # 联赛
    "NFL", "NBA", "MLB", "NHL", "MLS", "FIFA", "UEFA", "Premier League",
    "Super Bowl", "World Cup", "Olympics", "NCAA", "March Madness",
    # NBA 球队/球员
    "Lakers", "Warriors", "Celtics", "Bulls", "Heat", "Knicks",
    "LeBron James", "Stephen Curry", "Kevin Durant", "Giannis", "Luka Doncic",
    "Michael Jordan", "Kobe Bryant",
    # NFL 球队
    "Cowboys", "Patriots", "Packers", "Steelers", "49ers", "Chiefs",
    "Tom Brady", "Patrick Mahomes", "Aaron Rodgers",
    # MLB 球队
    "Yankees", "Red Sox", "Dodgers", "Cubs", "Giants",
    # 足球球星/俱乐部
    "Real Madrid", "Barcelona", "Manchester United", "Manchester City",
    "Liverpool", "Chelsea", "Arsenal", "Juventus", "Bayern Munich", "PSG",
    "Messi", "Cristiano Ronaldo", "Neymar", "Mbappe", "Haaland",
]

# 著名大学
COLLEGE_BRANDS = [
    "Harvard", "Yale", "Princeton", "MIT", "Stanford",
    "Cornell", "Columbia University", "UCLA", "UC Berkeley", "NYU",
    "Oxford", "Cambridge", "Duke", "Michigan", "Wisconsin",
    "Texas", "USC", "Notre Dame", "Florida State",
]

# 食品饮料巨头 (易侵权产品相关饰品/包装/瓶塞)
FOOD_BEVERAGE_BRANDS = [
    "Coca-Cola", "Coke", "Pepsi", "Sprite", "Fanta",
    "Starbucks", "McDonald's", "KFC", "Burger King", "Subway",
    "Nestle", "Hershey", "Cadbury", "Mars", "M&M", "Snickers",
    "Kraft", "Heinz", "Kellogg's", "General Mills",
    "Red Bull", "Monster Energy", "Gatorade",
    "Oreo", "Kit Kat", "Ritz", "Pringles", "Doritos",
]

# 明星 / 艺人 (T 恤海报类)
CELEBRITIES = [
    "Taylor Swift", "Beyoncé", "Rihanna", "Lady Gaga",
    "Drake", "Kanye West", "Kim Kardashian",
    "BTS", "BLACKPINK", "Twice",
    "Elvis Presley", "Michael Jackson", "Beatles", "Bob Marley",
    "Marilyn Monroe", "Audrey Hepburn", "Albert Einstein",
]

# 家电 / 品牌厨具
APPLIANCE_BRANDS = [
    "KitchenAid", "Cuisinart", "Ninja", "Instant Pot", "Keurig", "Nespresso",
    "Breville", "Vitamix", "Panasonic", "Hamilton Beach", "Black+Decker",
    "Whirlpool", "Maytag", "Frigidaire", "LG", "GE Appliances",
    "Roomba", "iRobot", "Shark",
]

# 美妆品牌
BEAUTY_BRANDS = [
    "MAC", "Maybelline", "Revlon", "L'Oreal", "L'Oréal",
    "Estée Lauder", "Lancôme", "Clinique", "Shiseido",
    "Sephora", "Ulta",
    "Kylie Cosmetics", "Fenty Beauty", "Urban Decay",
    "La Mer", "SK-II", "Olay",
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
        values.append((ip, "keyword", "cartoon_ip", "hard_block", "卡通/电影/动漫/游戏 IP"))
    for league in SPORTS_LEAGUES:
        values.append((league, "keyword", "sports_league", "hard_block", "体育联赛/球队/球员"))
    for college in COLLEGE_BRANDS:
        values.append((college, "keyword", "college_brand", "warn", "大学品牌"))
    for fb in FOOD_BEVERAGE_BRANDS:
        values.append((fb, "keyword", "food_brand", "hard_block", "食品饮料巨头"))
    for celeb in CELEBRITIES:
        values.append((celeb, "keyword", "celebrity", "hard_block", "明星/艺人"))
    for app in APPLIANCE_BRANDS:
        values.append((app, "keyword", "appliance_brand", "hard_block", "家电品牌"))
    for bt in BEAUTY_BRANDS:
        values.append((bt, "keyword", "beauty_brand", "hard_block", "美妆品牌"))

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
