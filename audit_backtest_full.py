"""
E-3 极限回测: L1 (禁 ASIN 直击) + LLM (收紧 prompt) + 视觉审 approve+hold

统计最终漏网率 (approve 条数 / 1938).
"""
import argparse
import time
import psycopg2

BATCH = "batch_20260417_032822.xlsx"
DB_CONN = "dbname=uspto user=nextderboy"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--llm-concurrency", type=int, default=100)
    p.add_argument("--vision-concurrency", type=int, default=15)
    p.add_argument("--skip-l1", action="store_true")
    p.add_argument("--skip-llm", action="store_true")
    p.add_argument("--skip-vision", action="store_true")
    args = p.parse_args()

    import audit_rules
    orig = audit_rules.rule_asin_hit
    audit_rules.rule_asin_hit = lambda p, c: []

    try:
        # Step 1: L1 全量
        if not args.skip_l1:
            print(f"\n{'='*60}\n[Step 1] L1 (A-3映射 + F-2 召回, 禁 ASIN 直击)\n{'='*60}")
            from audit_rules import run_batch
            run_batch(BATCH)

        # Step 2: LLM 对 hold_manual (收紧 prompt)
        if not args.skip_llm:
            print(f"\n{'='*60}\n[Step 2] LLM 二审 hold_manual (收紧 prompt)\n{'='*60}")
            from audit_llm import run_llm_on_batch
            run_llm_on_batch(BATCH, verdict_filter=("hold_manual",),
                             concurrency=args.llm_concurrency)

        # Step 3: 视觉审 approve + hold (找漏网)
        if not args.skip_vision:
            print(f"\n{'='*60}\n[Step 3] 视觉审 approve + hold (找漏网)\n{'='*60}")
            from audit_vision import run_vision_on_batch
            run_vision_on_batch(BATCH, verdict_filter=("approve", "hold_manual"),
                                 concurrency=args.vision_concurrency)
    finally:
        audit_rules.rule_asin_hit = orig

    # 统计
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT verdict, COUNT(*) FROM product_audits
        WHERE batch_file=%s GROUP BY verdict
    """, (BATCH,))
    counts = dict(cur.fetchall())
    total = sum(counts.values())
    rej = counts.get("reject", 0)
    hold = counts.get("hold_manual", 0)
    apr = counts.get("approve", 0)
    print(f"\n{'='*60}\nE-3 极限回测结果 ({total} 真违规 ground truth)\n{'='*60}")
    print(f"  reject:       {rej:5d} ({100*rej/total:5.1f}%)  ← 硬拒")
    print(f"  hold_manual:  {hold:5d} ({100*hold/total:5.1f}%)  ← 需人工")
    print(f"  approve:      {apr:5d} ({100*apr/total:5.1f}%)  ← 漏网")
    print(f"\n  识别率 (reject+hold): {100*(rej+hold)/total:.1f}%")
    print(f"  漏网率:                {100*apr/total:.1f}%")
    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
