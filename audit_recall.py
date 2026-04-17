"""
相似度召回 — 在 walmart_suspension_history 中找与产品最相似的历史违规

两种召回:
1. ASIN 精确命中 (已在 audit_rules.rule_asin_hit 处理)
2. 标题 trigram 相似度 top-K
   使用 pg_trgm 的 % 操作符 + similarity(), 依赖 idx_wsh_title_trgm 索引

输出:
- similar_history: list of {sku, asin, title, ptype, reason, deleted, similarity}
- 阈值以上触发 audit flag (warn/hard_block 视 reason + deleted)
"""
from typing import Dict, List


THRESHOLD_WARN = 0.30
THRESHOLD_HARD = 0.55   # 非常相似且历史被删 + 硬违规原因 → hard_block
HARD_REASON_CATEGORIES = {
    "ip", "offensive", "biz_cn_restriction", "biz_brand_exclusive",
    "regulatory_firearm", "regulatory_drug", "regulatory_alcohol",
    "regulatory_tobacco", "regulatory_children", "regulatory_cosmetic",
    "regulatory_medical", "regulatory_supplement", "regulatory_pet",
    "weapons_melee", "auto_motor",
}


def recall_similar_history(product: Dict, conn, k=10, threshold=THRESHOLD_WARN):
    """
    对产品标题做 trigram 相似度召回, 返回历史违规 top-K
    """
    title = product.get("title")
    if not title:
        return []
    cur = conn.cursor()
    cur.execute("""
        SELECT walmart_sku, amazon_asin, title_clean, product_type,
               reason_category, reason_subcategory,
               is_deleted, similarity(title_clean, %s) AS sim
        FROM walmart_suspension_history
        WHERE title_clean %% %s
          AND title_clean IS NOT NULL
        ORDER BY sim DESC
        LIMIT %s
    """, (title, title, k))
    rows = cur.fetchall()
    cur.close()
    return [
        {
            "sku": r[0], "asin": r[1], "title": r[2], "ptype": r[3],
            "reason": r[4], "reason_sub": r[5],
            "deleted": r[6], "similarity": float(r[7]),
        }
        for r in rows
        if r[7] is not None and float(r[7]) >= threshold
    ]


def rule_historical_similarity(product: Dict, conn) -> List[Dict]:
    """相似度召回 → audit_flag"""
    sims = recall_similar_history(product, conn, k=5, threshold=THRESHOLD_WARN)
    if not sims:
        return []
    flags = []
    # 若相似度极高且历史是硬违规已删, 标 hard_block
    for s in sims:
        severity = "info"
        if s["similarity"] >= THRESHOLD_HARD and s["deleted"] and s["reason"] in HARD_REASON_CATEGORIES:
            severity = "hard_block"
        elif s["similarity"] >= 0.4 and (s["deleted"] or s["reason"] in HARD_REASON_CATEGORIES):
            severity = "warn"

        if severity == "info":
            continue  # 只要 warn/hard_block 才出 flag, info 级不推入最终决策
        flags.append({
            "flag_type": "historical_recall",
            "flag_category": "historical",
            "flag_code": f"similar_history_{s['reason']}",
            "description": (
                f'标题与历史违规 SKU={s["sku"]} 相似度 {s["similarity"]:.2f} '
                f'({s["reason"]}, {"已删除" if s["deleted"] else "未删除"})'
            ),
            "severity": severity,
            "evidence": {
                "similar_sku": s["sku"],
                "similar_asin": s["asin"],
                "similar_title": s["title"][:200] if s["title"] else None,
                "similarity": s["similarity"],
                "reason_category": s["reason"],
                "reason_sub": s["reason_sub"],
                "deleted": s["deleted"],
            },
        })
    # 只保留最高严重度的一条 flag (避免重复刷屏)
    if flags:
        flags.sort(key=lambda f: 0 if f["severity"] == "hard_block" else 1)
        return flags[:1]
    return []


if __name__ == "__main__":
    import psycopg2
    conn = psycopg2.connect("dbname=uspto user=nextderboy")
    cur = conn.cursor()
    cur.execute("SELECT asin, title FROM products_stage LIMIT 5")
    for asin, title in cur.fetchall():
        sims = recall_similar_history({"title": title}, conn, k=3)
        print(f"\nASIN {asin} | {title[:60]}")
        for s in sims:
            print(f"  sim={s['similarity']:.2f} | {s['reason']} ({s['reason_sub']}) | "
                  f'{"DEL" if s["deleted"] else "    "} | {s["title"][:60] if s["title"] else ""}')
    cur.close()
    conn.close()
