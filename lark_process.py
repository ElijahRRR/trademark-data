"""
增量处理新增 TRO 案件

工作流程:
1. 找出 tro_cases 中尚未在 matched_companies 的 case_numbers
2. 收集这些案件涉及的 plaintiff_clean / brand_clean
3. 仅对 path_a_results / path_b_results 还没查过的值跑 query_path_a/b_single
4. 用 step3 汇合逻辑给新案件插入 matched_companies 行 (不 TRUNCATE)
5. 对新出现的 real_company 收集品牌到 company_brand_details

对外主函数:
- process_pending_cases() -> dict 统计
"""
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import psycopg2

from step2_v2 import (
    DB_CONN,
    query_path_a_single,
    query_path_b_single,
    validate_match,
)


# ---------- Step A: 查询新原告/新品牌 ----------

def _missing_plaintiffs(cur, plaintiffs):
    """返回 plaintiffs 中尚未在 path_a_results 出现过的"""
    if not plaintiffs:
        return []
    cur.execute(
        "SELECT DISTINCT plaintiff_clean FROM path_a_results WHERE plaintiff_clean = ANY(%s)",
        (list(plaintiffs),),
    )
    seen = set(r[0] for r in cur.fetchall())
    # 还要排除 unique_plaintiffs 中 query_status='miss' 的（已查过但无结果）
    cur.execute(
        "SELECT plaintiff_clean FROM unique_plaintiffs WHERE plaintiff_clean = ANY(%s) AND query_status IN ('exact','fuzzy','miss')",
        (list(plaintiffs),),
    )
    queried = set(r[0] for r in cur.fetchall())
    return [p for p in plaintiffs if p not in seen and p not in queried]


def _missing_brands(cur, brands):
    """返回 brands 中尚未在 path_b_results 出现过的"""
    if not brands:
        return []
    cur.execute(
        "SELECT DISTINCT brand_clean FROM path_b_results WHERE brand_clean = ANY(%s)",
        (list(brands),),
    )
    seen = set(r[0] for r in cur.fetchall())
    cur.execute(
        "SELECT brand_clean FROM unique_brands WHERE brand_clean = ANY(%s) AND query_status IN ('exact','fuzzy','miss')",
        (list(brands),),
    )
    queried = set(r[0] for r in cur.fetchall())
    return [b for b in brands if b not in seen and b not in queried]


def query_new_plaintiffs(plaintiffs, max_workers=8):
    """对一批新 plaintiff 跑路径A 并写入 path_a_results / unique_plaintiffs"""
    if not plaintiffs:
        return {"exact": 0, "fuzzy": 0, "miss": 0}

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    stats = {"exact": 0, "fuzzy": 0, "miss": 0}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(query_path_a_single, p): p for p in plaintiffs}
        for fut in as_completed(futures):
            p = futures[fut]
            match_type, rows = fut.result()
            stats[match_type] += 1
            for row in rows:
                cur.execute(
                    """
                    INSERT INTO path_a_results
                        (plaintiff_clean, match_type, serial_number, mark_identification,
                         owner_name, status_code, live_dead)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (p, match_type, row[0], row[1], row[2], row[3], row[4]),
                )
            # upsert 到 unique_plaintiffs (UNIQUE 约束)
            cur.execute(
                """
                INSERT INTO unique_plaintiffs (plaintiff_clean, case_count, query_status)
                VALUES (%s, 0, %s)
                ON CONFLICT (plaintiff_clean) DO UPDATE SET query_status = EXCLUDED.query_status
                """,
                (p, match_type),
            )
    conn.commit()
    cur.close()
    conn.close()
    return stats


def query_new_brands(brands, max_workers=8):
    """对一批新 brand 跑路径B 并写入 path_b_results / unique_brands"""
    if not brands:
        return {"exact": 0, "fuzzy": 0, "miss": 0}

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    stats = {"exact": 0, "fuzzy": 0, "miss": 0}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(query_path_b_single, b): b for b in brands}
        for fut in as_completed(futures):
            b = futures[fut]
            match_type, rows = fut.result()
            stats[match_type] += 1
            for row in rows:
                cur.execute(
                    """
                    INSERT INTO path_b_results
                        (brand_clean, match_type, serial_number, mark_identification,
                         owner_name, status_code, live_dead)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (b, match_type, row[0], row[1], row[2], row[3], row[4]),
                )
            cur.execute(
                """
                INSERT INTO unique_brands (brand_clean, case_count, query_status)
                VALUES (%s, 0, %s)
                ON CONFLICT (brand_clean) DO UPDATE SET query_status = EXCLUDED.query_status
                """,
                (b, match_type),
            )
    conn.commit()
    cur.close()
    conn.close()
    return stats


# ---------- Step B: 汇合判定 (复用 step3 逻辑, 但只插入新案件) ----------

def merge_for_cases(case_numbers):
    """
    对一批 case_numbers 跑 step3 汇合判定, 插入 matched_companies (不 TRUNCATE).
    返回 quality 统计 dict.
    """
    if not case_numbers:
        return {}

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT case_number, plaintiff_clean, brand_clean, brand_eq_plaintiff, nature_of_suit
        FROM tro_cases
        WHERE case_number = ANY(%s)
        """,
        (list(case_numbers),),
    )
    cases = cur.fetchall()

    # 先删除已有的（防重复）
    cur.execute(
        "DELETE FROM matched_companies WHERE case_number = ANY(%s)",
        (list(case_numbers),),
    )

    stats = defaultdict(int)
    for case_num, plaintiff, brand, brand_eq, nature in cases:
        companies_a = set()
        if plaintiff:
            cur.execute(
                "SELECT DISTINCT owner_name FROM path_a_results WHERE plaintiff_clean = %s",
                (plaintiff,),
            )
            companies_a = set(r[0] for r in cur.fetchall())
        a_status = "hit" if companies_a else "miss"

        companies_b = set()
        b_status = "skip"
        if not brand_eq and brand:
            cur.execute(
                "SELECT DISTINCT owner_name FROM path_b_results WHERE brand_clean = %s",
                (brand,),
            )
            companies_b = set(r[0] for r in cur.fetchall())
            b_status = "hit" if companies_b else "miss"

        if a_status == "hit" and b_status == "hit":
            overlap = companies_a & companies_b
            if overlap:
                real_company = max(overlap, key=lambda c: validate_match(plaintiff, c))
                quality = "exact"
                needs_review = False
                reason = None
            else:
                best_a = max(companies_a, key=lambda c: validate_match(plaintiff, c))
                score = validate_match(plaintiff, best_a)
                real_company = best_a
                quality = "a_preferred"
                needs_review = score < 0.3
                reason = f"low_similarity: {score:.3f}" if needs_review else None

        elif a_status == "hit":
            best_a = max(companies_a, key=lambda c: validate_match(plaintiff, c))
            score = validate_match(plaintiff, best_a)
            real_company = best_a
            quality = "a_only"
            needs_review = score < 0.3
            reason = f"low_similarity: {score:.3f}" if needs_review else None

        elif b_status == "hit":
            if len(companies_b) <= 5:
                real_company = list(companies_b)[0]
                quality = "b_only"
                needs_review = False
                reason = None
            else:
                real_company = list(companies_b)[0]
                quality = "b_uncertain"
                needs_review = True
                reason = f"brand {brand} has {len(companies_b)} owners"
        else:
            real_company = None
            quality = "not_found"
            needs_review = True
            reason = f"nature={nature}"

        stats[quality] += 1
        cur.execute(
            """
            INSERT INTO matched_companies
                (case_number, plaintiff_clean, brand_clean, real_company, match_quality, needs_review, review_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (case_num, plaintiff, brand, real_company, quality, needs_review, reason),
        )

    conn.commit()
    cur.close()
    conn.close()
    return dict(stats)


# ---------- Step C: 收集新公司的品牌 ----------

def collect_brands_for_companies(companies):
    """对一批新 real_company 收集品牌到 company_brand_details (不 TRUNCATE)"""
    if not companies:
        return 0

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # 排除已经收集过的
    cur.execute(
        "SELECT DISTINCT real_company FROM company_brand_details WHERE real_company = ANY(%s)",
        (list(companies),),
    )
    already = set(r[0] for r in cur.fetchall())
    new_companies = [c for c in companies if c not in already]
    if not new_companies:
        cur.close()
        conn.close()
        return 0

    total = 0
    for company in new_companies:
        cur.execute(
            """
            INSERT INTO company_brand_details
                (real_company, mark_identification, serial_number, registration_number,
                 status_code, live_dead, category, international_code,
                 international_desc_cn, international_desc_en, goods_services, first_use_date)
            SELECT DISTINCT
                %s,
                t.mark_identification,
                t.serial_number,
                t.registration_number,
                t.status_code,
                m.live_dead,
                m.category,
                tc.international_code,
                nc.name_cn,
                nc.name_en,
                ts.text,
                tc.first_use_date
            FROM trademarks t
            JOIN trademark_owners o ON t.serial_number = o.serial_number
            JOIN status_code_mapping m ON t.status_code = m.status_code
            LEFT JOIN trademark_classes tc ON t.serial_number = tc.serial_number
            LEFT JOIN nice_classification nc ON tc.international_code = nc.code
            LEFT JOIN trademark_statements ts ON t.serial_number = ts.serial_number
                AND ts.type_code LIKE 'GS%%'
            WHERE o.party_name = %s
              AND m.live_dead = 'LIVE'
            """,
            (company, company),
        )
        total += cur.rowcount

    conn.commit()
    cur.close()
    conn.close()
    return total


# ---------- 主流程 ----------

def process_pending_cases():
    """
    增量处理 tro_cases 中尚未匹配的案件
    Returns: dict 统计
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # 1. 找未处理 cases
    cur.execute(
        """
        SELECT tc.case_number, tc.plaintiff_clean, tc.brand_clean, tc.brand_eq_plaintiff
        FROM tro_cases tc
        LEFT JOIN matched_companies mc ON tc.case_number = mc.case_number
        WHERE mc.case_number IS NULL
        ORDER BY tc.case_number
        """
    )
    pending = cur.fetchall()
    if not pending:
        cur.close()
        conn.close()
        return {"pending": 0, "msg": "无新案件"}

    pending_case_nums = [r[0] for r in pending]
    pending_plaintiffs = sorted(set(r[1] for r in pending if r[1]))
    pending_brands = sorted(set(r[2] for r in pending if r[2] and not r[3]))

    print(f"  待处理案件: {len(pending_case_nums)}")
    print(f"  涉及原告: {len(pending_plaintiffs)} (去重)")
    print(f"  涉及品牌: {len(pending_brands)} (去重, 排除=原告)")

    # 2. 找出真正未查过的
    new_plaintiffs = _missing_plaintiffs(cur, pending_plaintiffs)
    new_brands = _missing_brands(cur, pending_brands)
    print(f"  新原告(未查过): {len(new_plaintiffs)}")
    print(f"  新品牌(未查过): {len(new_brands)}")
    cur.close()
    conn.close()

    # 3. 查询路径A
    print("\n  [路径A] 查询新原告...")
    a_stats = query_new_plaintiffs(new_plaintiffs)
    print(f"    A: {a_stats}")

    # 4. 查询路径B
    print("\n  [路径B] 查询新品牌...")
    b_stats = query_new_brands(new_brands)
    print(f"    B: {b_stats}")

    # 5. 汇合
    print("\n  [汇合] 生成 matched_companies...")
    merge_stats = merge_for_cases(pending_case_nums)
    print(f"    汇合: {merge_stats}")

    # 6. 收集新公司品牌
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT real_company FROM matched_companies
        WHERE case_number = ANY(%s) AND real_company IS NOT NULL
        """,
        (pending_case_nums,),
    )
    new_companies = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()

    print(f"\n  [品牌收集] 新公司: {len(new_companies)}")
    brand_added = collect_brands_for_companies(new_companies)
    print(f"    新增品牌记录: {brand_added}")

    return {
        "pending": len(pending_case_nums),
        "new_plaintiffs": len(new_plaintiffs),
        "new_brands": len(new_brands),
        "path_a": a_stats,
        "path_b": b_stats,
        "merge": merge_stats,
        "new_companies": len(new_companies),
        "brand_records_added": brand_added,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("增量处理 TRO 案件")
    print("=" * 60)
    result = process_pending_cases()
    print("\n" + "=" * 60)
    print("结果:")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k}: {v}")
