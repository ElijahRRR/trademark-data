"""
E-1 回测: 用历史已知违规 (is_deleted=TRUE) ASIN 作为 ground truth
测 L1 规则引擎的召回率 / 误伤率

步骤:
1. 取 walmart_suspension_history 中 is_deleted=TRUE 的所有 ASIN
   这是"真·违规"样本池
2. 从 Scraper API 拉这些 ASIN 的 Amazon 数据 (回填 products_stage)
3. 跑 audit_rules 得到每个 ASIN 的 verdict
4. 统计:
   - 召回率 = L1 正确判为 reject 的 / 真实违规总数
   - 误伤率 = L1 误判 hold/reject 的 / 本应 approve 的
     (需另加一组"通过"样本作为负样本. 这里用非历史违规的 ASIN)
5. 按 reason_category 细分

使用真实历史 ASIN 而不是 batch_20260417 的 1938, 是因为:
- batch_20260417 里 163 条与历史重合 → 作为正样本偏少
- walmart_suspension_history 里 is_deleted=TRUE 的 ASIN 覆盖面更广 (273 + 新增)
"""
import argparse
import json
import time
import urllib.parse
import urllib.request
from decimal import Decimal

import psycopg2
from psycopg2.extras import Json, execute_values


DB_CONN = "dbname=uspto user=nextderboy"
SCRAPER_BASE = "http://64.186.239.11:8899"


def fetch_scraper(asin: str, timeout=10):
    """从 Amazon Scraper 拉 ASIN 完整数据"""
    url = f"{SCRAPER_BASE}/api/results/{asin}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = json.loads(resp.read())
        return body.get("data") or None
    except Exception as e:
        return None


def _scraper_to_stage(d: dict, batch_name="backtest_history") -> dict:
    """Scraper 响应 → products_stage 字段"""
    def _clean(v):
        if v is None or v == "":
            return None
        s = str(v).strip()
        return s if s and s.upper() != "N/A" else None

    def _price(s):
        if not s:
            return None
        import re
        m = re.search(r"[\d,]+\.?\d*", str(s).replace(",", ""))
        if not m:
            return None
        try:
            return Decimal(m.group(0))
        except Exception:
            return None

    return {
        "batch_file": batch_name,
        "asin": d["asin"],
        "title": _clean(d.get("title")),
        "brand": _clean(d.get("brand")),
        "product_type": _clean(d.get("product_type")),  # Amazon 商品类型 (常见为 N/A)
        "manufacturer": _clean(d.get("manufacturer")),
        "model_number": _clean(d.get("model_number")),
        "part_number": _clean(d.get("part_number")),
        "origin_country": _clean(d.get("country_of_origin")),
        "bullet_points": _clean(d.get("bullet_points")),
        "long_description": _clean(d.get("long_description")),
        "image_urls": _clean(d.get("image_urls")),
        "upc": _clean(d.get("upc_list")),
        "ean": _clean(d.get("ean_list")),
        "root_category_id": _clean(d.get("root_category_id")),
        "category_chain_ids": _clean(d.get("category_ids")),
        "category_path": _clean(d.get("category_tree")),
        "price": _price(d.get("current_price")) or _price(d.get("buybox_price")),
        "bsr": _clean(d.get("best_sellers_rank")),
        "is_fba": (str(d.get("is_fba") or "").upper() == "FBA") if d.get("is_fba") else None,
        "collected_at": _clean(d.get("crawl_time")),
        "raw_data": {k: (str(v) if v is not None else None) for k, v in d.items()},
    }


INSERT_STAGE_SQL = """
INSERT INTO products_stage (
    batch_file, asin, title, brand, product_type, manufacturer,
    model_number, part_number, origin_country,
    bullet_points, long_description, image_urls,
    upc, ean, root_category_id, category_chain_ids, category_path,
    price, bsr, is_fba, raw_data, collected_at
) VALUES %s
ON CONFLICT (batch_file, asin) DO UPDATE SET
    title = EXCLUDED.title, brand = EXCLUDED.brand,
    product_type = EXCLUDED.product_type,
    bullet_points = EXCLUDED.bullet_points,
    long_description = EXCLUDED.long_description,
    image_urls = EXCLUDED.image_urls,
    category_path = EXCLUDED.category_path,
    price = EXCLUDED.price, raw_data = EXCLUDED.raw_data,
    imported_at = NOW()
"""

STAGE_COLS = [
    "batch_file", "asin", "title", "brand", "product_type", "manufacturer",
    "model_number", "part_number", "origin_country",
    "bullet_points", "long_description", "image_urls",
    "upc", "ean", "root_category_id", "category_chain_ids", "category_path",
    "price", "bsr", "is_fba", "raw_data", "collected_at",
]


def backfill_from_scraper(asins, batch_name, verbose=True):
    """用 Scraper API 拉 ASIN 列表, 批量入 products_stage"""
    if verbose:
        print(f"Scraper 回填: {len(asins)} ASIN")
    t0 = time.time()
    rows = []
    miss = []
    for i, asin in enumerate(asins):
        d = fetch_scraper(asin)
        if not d:
            miss.append(asin)
            continue
        stage = _scraper_to_stage(d, batch_name)
        rows.append(tuple(
            Json(stage[c]) if c == "raw_data" else stage[c]
            for c in STAGE_COLS
        ))
        if verbose and (i+1) % 100 == 0:
            print(f"  进度: {i+1}/{len(asins)} (命中 {len(rows)}, 缺失 {len(miss)})", flush=True)

    t_fetch = time.time() - t0
    if verbose:
        print(f"拉取完成: {len(rows)} 命中, {len(miss)} 缺失, 耗时 {t_fetch:.1f}s")

    if not rows:
        return 0, miss

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    execute_values(cur, INSERT_STAGE_SQL, rows, page_size=200)
    conn.commit()
    cur.close()
    conn.close()
    return len(rows), miss


def pick_ground_truth_positives(limit=500):
    """取历史已知违规 ASIN (is_deleted=TRUE, 且有 amazon_asin) 去重"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT amazon_asin, MAX(reason_category) reason_cat, BOOL_OR(is_deleted) deleted,
               STRING_AGG(DISTINCT reason_category, ',') all_reasons
        FROM walmart_suspension_history
        WHERE amazon_asin IS NOT NULL
          AND length(amazon_asin) = 10
          AND amazon_asin LIKE 'B%%'
          AND is_deleted = TRUE
        GROUP BY amazon_asin
        ORDER BY random()
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"asin": r[0], "reason": r[1], "all_reasons": r[3]} for r in rows]


def evaluate_recall(batch_name="backtest_history", verbose=True):
    """对回填后的 products_stage 跑 audit_rules, 统计"""
    from audit_rules import run_batch
    if verbose:
        print("\n跑 L1 规则...")
    run_batch(batch_name, verbose=verbose)

    # 对比 verdict vs ground truth (ground truth 都是 deleted=TRUE, 预期应该被 reject/hold)
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT pa.verdict, COUNT(*) n
        FROM product_audits pa
        WHERE pa.batch_file = %s
        GROUP BY pa.verdict
    """, (batch_name,))
    verdict_counts = dict(cur.fetchall())

    total = sum(verdict_counts.values())
    rej = verdict_counts.get("reject", 0)
    hold = verdict_counts.get("hold_manual", 0)
    apr = verdict_counts.get("approve", 0)

    # 召回率 = (reject + hold) / total (因为 ground truth 都是违规, 理想都被拦)
    # reject 召回率 = reject / total
    # 漏网率 = approve / total (被 L1 放行但实际是真违规)

    print(f"\n{'='*60}")
    print(f"回测结果 (ground truth: 历史已被删除的违规 ASIN)")
    print(f"{'='*60}")
    print(f"总样本:  {total}")
    print(f"  reject:       {rej:5d} ({100*rej/total:5.1f}%)  ← L1 直接拦截 (理想100%)")
    print(f"  hold_manual:  {hold:5d} ({100*hold/total:5.1f}%)  ← 进入 LLM 二审")
    print(f"  approve:      {apr:5d} ({100*apr/total:5.1f}%)  ← 漏网 (真违规被放行, 需改进)")
    print()
    print(f"L1 硬召回率 (reject):              {100*rej/total:.1f}%")
    print(f"L1 + 二审 覆盖率 (reject+hold):    {100*(rej+hold)/total:.1f}%")
    print(f"漏网率 (approve 但实际违规):       {100*apr/total:.1f}%")

    # 按 reason 分类看漏网情况
    cur.execute("""
        SELECT h.reason_category,
               COUNT(*) total,
               SUM(CASE WHEN pa.verdict='reject' THEN 1 ELSE 0 END) rej,
               SUM(CASE WHEN pa.verdict='hold_manual' THEN 1 ELSE 0 END) hold,
               SUM(CASE WHEN pa.verdict='approve' THEN 1 ELSE 0 END) apr
        FROM product_audits pa
        JOIN (
            SELECT amazon_asin, MAX(reason_category) reason_category
            FROM walmart_suspension_history
            WHERE is_deleted = TRUE
            GROUP BY amazon_asin
        ) h ON h.amazon_asin = pa.asin
        WHERE pa.batch_file = %s
        GROUP BY h.reason_category
        ORDER BY total DESC
    """, (batch_name,))
    print(f"\n按历史违规原因分类:")
    print(f"  {'reason':<24s}  {'total':>6s}  {'reject':>7s}  {'hold':>6s}  {'miss':>6s}  {'miss_rate':>10s}")
    for r in cur.fetchall():
        reason, total_, rj, hl, ap = r
        miss_rate = f"{100*ap/total_:.1f}%" if total_ else "-"
        print(f"  {reason:<24s}  {total_:>6d}  {rj:>7d}  {hl:>6d}  {ap:>6d}  {miss_rate:>10s}")

    cur.close()
    conn.close()
    return {"total": total, "reject": rej, "hold": hold, "approve": apr}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=500, help="测试样本数 (从历史随机抽)")
    p.add_argument("--skip-backfill", action="store_true", help="跳过 Scraper 回填, 直接用已有 batch")
    p.add_argument("--batch", default="backtest_history")
    p.add_argument("--disable-asin-rule", action="store_true",
                   help="禁用 rule_asin_hit 后再跑一次 (测其他规则单独能力)")
    args = p.parse_args()

    if not args.skip_backfill:
        print(f"{'='*60}\n步骤 1: 从历史抽 {args.limit} 个已删除 ASIN\n{'='*60}")
        truths = pick_ground_truth_positives(args.limit)
        print(f"  抽到 {len(truths)} 个 ASIN")

        print(f"\n{'='*60}\n步骤 2: Scraper 回填原始 Amazon 数据\n{'='*60}")
        asins = [t["asin"] for t in truths]
        n, miss = backfill_from_scraper(asins, args.batch)
        print(f"  成功入 stage: {n}")
        if miss:
            print(f"  Scraper 无数据 (跳过): {len(miss)}")

    print(f"\n{'='*60}\n步骤 3: 跑 L1 规则并评估\n{'='*60}")
    evaluate_recall(args.batch)

    # 额外: 禁用 ASIN 直击后的公平回测
    if args.disable_asin_rule:
        print(f"\n{'='*60}\n步骤 4: 禁用 rule_asin_hit 后重测 (公平回测)\n{'='*60}")
        import audit_rules
        orig = audit_rules.rule_asin_hit
        audit_rules.rule_asin_hit = lambda p, c: []
        try:
            evaluate_recall(args.batch)
        finally:
            audit_rules.rule_asin_hit = orig


if __name__ == "__main__":
    main()
