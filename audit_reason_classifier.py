"""
沃尔玛错误原因文本 → (category, subcategory) 分类器

输入: 原始富文本拼接后的字符串 (reason_raw)
输出: (primary_category, primary_subcategory) 二元组

分类优先级 (高到低): offensive > ip > weapons_melee > auto_motor > prohibited_generic >
                     internal_flag > pricing > no_price > tax_code > end_date > other
"""
import re
from typing import List, Tuple

# (regex, category, subcategory) — 按具体到泛化顺序
# 带 re.IGNORECASE
REASON_PATTERNS: List[Tuple[re.Pattern, str, str]] = [
    # ---------- 中国卖家特别限制 (最大头, 优先匹配) ----------
    (re.compile(r"code\s+BIZ-CN", re.I), "biz_cn_restriction", "china_seller_blocked"),
    (re.compile(r"code\s+BIZ\b", re.I), "biz_brand_exclusive", "brand_partnership"),

    # ---------- 类目受限 (enhanced vetting program) ----------
    (re.compile(r"listed\s+in\s+a\s+cosmetics\s+category,?\s+which\s+is\s+restricted", re.I), "regulatory_cosmetic", "cosmetic_restricted"),
    (re.compile(r"listed\s+in\s+a\s+medical\s+device\s+category,?\s+which\s+is\s+restricted", re.I), "regulatory_medical", "medical_restricted"),
    (re.compile(r"listed\s+in\s+a\s+dietary\s+supplement\s+category", re.I), "regulatory_supplement", "supplement_restricted"),
    (re.compile(r"listed\s+in\s+a\s+pet\s+category", re.I), "regulatory_pet", "pet_restricted"),
    (re.compile(r"listed\s+in\s+a\s+grocery\s+category|food\s+category", re.I), "regulatory_food", "food_restricted"),
    (re.compile(r"enhanced\s+vetting\s+program", re.I), "regulatory_vetting", "vetting_required"),
    (re.compile(r"restricted\s+category\s+that\s+requires\s+pre-approval", re.I), "regulatory_preapproval", "pre_approval_required"),

    # ---------- Pre-Owned / Refurbished / Restored ----------
    (re.compile(r"Pre-Owned\s+policy|Pre-Owned\s+Program", re.I), "refurbished", "pre_owned"),
    (re.compile(r"refurbished\s+or\s+restored|Restored.*Refurbished", re.I), "refurbished", "refurbished"),
    (re.compile(r"title\s+wasn't\s+in\s+the\s+correct\s+format", re.I), "refurbished", "title_format"),

    # ---------- Content policy / Content standards ----------
    (re.compile(r"Walmart'?s?\s+content\s+policy", re.I), "content_policy", "generic_content"),
    (re.compile(r"keyword\s+stuffing", re.I), "content_policy", "keyword_stuffing"),
    (re.compile(r"content\s+standards|Content-standards", re.I), "content_policy", "content_standards"),
    (re.compile(r"primary\s+image\s+shows.*while\s+the\s+title", re.I), "content_policy", "image_title_mismatch"),
    (re.compile(r"blank\s+images|images\s+are\s+blank", re.I), "content_policy", "blank_images"),
    (re.compile(r"unverified\s+authenticity\s+claims", re.I), "ip", "unverified_authenticity"),

    # ---------- Offensive ----------
    (re.compile(r"offensive|hate(ful)? (content|symbol)|racist|discriminat", re.I), "offensive", "generic_offensive"),
    (re.compile(r"religious (symbol|offense)|blasphem", re.I), "offensive", "religious"),

    # ---------- Intellectual Property ----------
    (re.compile(r"trademark\s+(violation|infringe)", re.I), "ip", "trademark"),
    (re.compile(r"copyright\s+(violation|infringe|claim)", re.I), "ip", "copyright"),
    (re.compile(r"patent\s+(violation|infringe)", re.I), "ip", "patent"),
    (re.compile(r"unauthorized (brand|seller|resel)", re.I), "ip", "unauthorized_brand"),
    (re.compile(r"counterfeit", re.I), "ip", "counterfeit"),
    (re.compile(r"intellectual property", re.I), "ip", "generic_ip"),

    # ---------- 系统内部错误 (非合规) ----------
    (re.compile(r"internal\s+error\s+occurred", re.I), "system_error", "internal"),

    # ---------- Weapons / Self Defense 误判 ----------
    (re.compile(r"Knives\s+and\s+other\s+Melee\s+Weapons", re.I), "weapons_melee", "knives_melee"),
    (re.compile(r"martial\s+arts|self.?defen[cs]e", re.I), "weapons_melee", "self_defense_claim"),
    (re.compile(r"prohibits?\s+the\s+sale\s+of\s+weapons?", re.I), "weapons_melee", "weapons_general"),

    # ---------- Auto and Motor Vehicles ----------
    (re.compile(r"gas\s+cans?\s+that\s+do\s+not\s+contain\s+flame\s+mitigation", re.I), "auto_motor", "gas_can_epa"),
    (re.compile(r"designed\s+to\s+defeat.*environmental\s+controls", re.I), "auto_motor", "env_bypass"),
    (re.compile(r"motor\s+vehicle\s+safety\s+standards", re.I), "auto_motor", "safety_bypass"),
    (re.compile(r"Prohibited\s+Product\s+Policy:\s*Auto\s+and\s+Motor\s+Vehicles", re.I), "auto_motor", "generic_auto"),

    # ---------- 其他具体受禁 ----------
    (re.compile(r"drugs?\s+(and\s+)?drug\s+paraphernalia", re.I), "regulatory_drug", "drug_general"),
    (re.compile(r"CBD|kratom|hemp\s+oil|HGH", re.I), "regulatory_drug", "drug_keyword"),
    (re.compile(r"alcohol", re.I), "regulatory_alcohol", "alcohol"),
    (re.compile(r"firearm", re.I), "regulatory_firearm", "firearm"),
    (re.compile(r"ammunition", re.I), "regulatory_firearm", "ammo"),
    (re.compile(r"tobacco|e-?cigarette|vape", re.I), "regulatory_tobacco", "tobacco"),
    (re.compile(r"children.?s\s+product|CPSC|CPC\s+certificate", re.I), "regulatory_children", "cpc_required"),
    (re.compile(r"cosmetic.*FDA|FD&C\s+Act", re.I), "regulatory_cosmetic", "fda_cosmetic"),

    # ---------- 通用 Prohibited Product Policy (最后兜底) ----------
    (re.compile(r"Prohibited\s+Product\s+Policy", re.I), "prohibited_generic", "no_specific_reason"),

    # ---------- 运维 ----------
    (re.compile(r"Tax\s+code\s+information\s+was\s+not\s+added", re.I), "tax_code", "missing_tax"),
    (re.compile(r"No\s+price\s+was\s+found", re.I), "no_price", "missing_price"),
    (re.compile(r"Walmart\s+Marketplace'?s?\s+Pricing\s+Rule|price\s+gouging", re.I), "pricing", "rule_violation"),
    (re.compile(r"End\s+Date\s+has\s+passed|Site\s+End\s+Date", re.I), "end_date", "expired"),
    (re.compile(r"item\s+reactivation", re.I), "end_date", "needs_reactivation"),
    (re.compile(r"flagged\s+by\s+our\s+internal\s+team|Case\s+Management", re.I), "internal_flag", "manual_review"),
]

# 严重度优先级 (数字越大越严重, 用于多原因时挑主因)
SEVERITY_ORDER = {
    "offensive": 100,
    "ip": 90,
    "biz_cn_restriction": 88,
    "biz_brand_exclusive": 87,
    "regulatory_firearm": 85,
    "regulatory_drug": 84,
    "regulatory_alcohol": 83,
    "regulatory_tobacco": 82,
    "regulatory_children": 81,
    "regulatory_cosmetic": 80,
    "regulatory_medical": 79,
    "regulatory_supplement": 78,
    "regulatory_pet": 77,
    "regulatory_food": 76,
    "regulatory_vetting": 75,
    "regulatory_preapproval": 74,
    "weapons_melee": 70,
    "auto_motor": 60,
    "content_policy": 55,
    "refurbished": 52,
    "prohibited_generic": 50,
    "internal_flag": 40,
    "pricing": 30,
    "no_price": 20,
    "tax_code": 15,
    "end_date": 10,
    "system_error": 5,
    "other": 0,
}


def classify_reason(text: str):
    """
    输入: 原始错误原因字符串
    输出: dict {
        'primary_category': str,
        'primary_subcategory': str,
        'all_matches': List[Tuple[category, subcategory]],
    }

    no_reason: 原文为空 (数据源没提供)
    other:    原文非空但未命中任何规则 (需补 pattern)
    """
    if not text or not text.strip():
        return {
            "primary_category": "no_reason",
            "primary_subcategory": None,
            "all_matches": [],
        }

    all_matches = []
    seen = set()
    for pat, cat, sub in REASON_PATTERNS:
        if pat.search(text):
            key = (cat, sub)
            if key not in seen:
                seen.add(key)
                all_matches.append(key)

    if not all_matches:
        return {
            "primary_category": "other",
            "primary_subcategory": None,
            "all_matches": [],
        }

    primary = max(all_matches, key=lambda x: SEVERITY_ORDER.get(x[0], 0))
    return {
        "primary_category": primary[0],
        "primary_subcategory": primary[1],
        "all_matches": all_matches,
    }


if __name__ == "__main__":
    samples = [
        "This item has been unpublished for violating Walmart's Marketplace *Prohibited Product Policy*. To republish this item please make sure you have the appropriate product type selected.",
        "This item has been unpublished for violating Walmart's Marketplace ||Prohibited Product Policy: Knives and other Melee Weapons@@@ . Walmart's policy prohibits the sale of weapons. This includes martial arts items as well as any items marketed for self defense.",
        "This item has been unpublished for violating Walmart's Marketplace ||Prohibited Product Policy: Auto and Motor Vehicles@@@ . Walmart's policy prohibits the sale of gas cans that do not contain flame mitigation devices or that do not comply with all laws and regulations including the EPA",
        "Tax code information was not added during item setup. Resubmit your item with a valid tax code. | This item is unpublished because the End Date has passed. | No price was found for the item.",
        "Your item has been flagged by our internal team. To find out why, file a case in Case Management.",
        "This item is unpublished because it violates Walmart Marketplace's Pricing Rule, which prevents price gouging.",
        "",
    ]
    for i, s in enumerate(samples):
        r = classify_reason(s)
        print(f"[{i}] {r['primary_category']}/{r['primary_subcategory']}  matches={r['all_matches']}")
        print(f"    {s[:100]}")
