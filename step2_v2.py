#!/usr/bin/env python3
"""
Step 2 v2: 改进匹配逻辑
- 精确匹配: 用 word boundary regex 替代 ILIKE 防止子串误匹配
- 模糊匹配: 候选结果做相关性验证
"""

import psycopg2, json, re
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_CONN = "dbname=uspto user=nextderboy"


def build_regex_pattern(name):
    """
    构建 word boundary regex
    'Capcom Co., Ltd.' → '\mCapcom\M'  (取第一个有意义的词)
    'ABB Merchandising Co., Inc.' → '\mABB\M.*\mMerchandising\M'
    'Na Qui' → '\mNa\M.*\mQui\M'
    """
    # 去掉常见后缀
    stop_words = {'the', 'a', 'an', 'of', 'and', 'for', 'on', 'behalf', 'in', 'to', 'by',
                  'inc', 'inc.', 'llc', 'ltd', 'ltd.', 'co', 'co.', 'corp', 'corp.',
                  'corporation', 'company', 'limited', 'group', 'holdings', 'et', 'al',
                  'al.', 'gmbh', 'sa', 's.a.', 'srl', 'plc', 'pty', 'pte', 'pte.'}

    words = name.split()
    meaningful = [w for w in words if w.lower().strip('.,;') not in stop_words and len(w) > 1]

    if not meaningful:
        meaningful = [w for w in words if len(w) > 1]

    if not meaningful:
        return None

    # 取前3个有意义的词做 word boundary 匹配
    pattern_parts = []
    for w in meaningful[:3]:
        # 转义正则特殊字符
        escaped = re.escape(w.strip('.,;'))
        pattern_parts.append(f'\\m{escaped}\\M')

    return '.*'.join(pattern_parts)


def validate_match(query_name, candidate_name):
    """
    验证匹配结果是否真的相关
    返回 0-1 的相关性分数
    """
    q_words = set(w.lower().strip('.,;') for w in query_name.split() if len(w) > 1)
    c_words = set(w.lower().strip('.,;') for w in candidate_name.split() if len(w) > 1)

    stop_words = {'the', 'a', 'an', 'of', 'and', 'for', 'on', 'inc', 'inc.', 'llc',
                  'ltd', 'ltd.', 'co', 'co.', 'corp', 'corporation', 'company', 'limited'}

    q_meaningful = q_words - stop_words
    c_meaningful = c_words - stop_words

    if not q_meaningful:
        return 0.0

    overlap = q_meaningful & c_meaningful
    return len(overlap) / len(q_meaningful)


def query_path_a_single(plaintiff):
    """路径A: 公司名查询 (单条)"""
    if not plaintiff:
        return ('miss', [])

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # Round 1: 精确 ILIKE (对大部分正常公司名有效)
    cur.execute("""
        SELECT DISTINCT t.serial_number, t.mark_identification, o.party_name,
               t.status_code, m.live_dead
        FROM trademarks t
        JOIN trademark_owners o ON t.serial_number = o.serial_number
        JOIN status_code_mapping m ON t.status_code = m.status_code
        WHERE o.party_name ILIKE %s AND m.live_dead = 'LIVE'
    """, (f'%{plaintiff}%',))
    rows = cur.fetchall()

    if rows:
        # 验证: 过滤掉不相关的匹配
        validated = []
        for row in rows:
            score = validate_match(plaintiff, row[2])
            if score >= 0.3:  # 至少30%的词匹配
                validated.append(row)

        if validated:
            cur.close(); conn.close()
            return ('exact', validated)

    # Round 2: word boundary regex
    pattern = build_regex_pattern(plaintiff)
    if pattern:
        try:
            cur.execute("""
                SELECT DISTINCT t.serial_number, t.mark_identification, o.party_name,
                       t.status_code, m.live_dead
                FROM trademarks t
                JOIN trademark_owners o ON t.serial_number = o.serial_number
                JOIN status_code_mapping m ON t.status_code = m.status_code
                WHERE o.party_name ~* %s AND m.live_dead = 'LIVE'
                LIMIT 100
            """, (pattern,))
            rows = cur.fetchall()

            if rows:
                validated = []
                for row in rows:
                    score = validate_match(plaintiff, row[2])
                    if score >= 0.3:
                        validated.append(row)

                if validated:
                    cur.close(); conn.close()
                    return ('fuzzy', validated)
        except Exception:
            conn.rollback()

    cur.close(); conn.close()
    return ('miss', [])


def query_path_b_single(brand):
    """路径B: 品牌名查询 (单条)"""
    if not brand or not any(c.isalpha() for c in str(brand)):
        return ('miss', [])

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # Round 1: 精确匹配品牌名 (用 = 而非 ILIKE)
    cur.execute("""
        SELECT DISTINCT t.serial_number, t.mark_identification, o.party_name,
               t.status_code, m.live_dead
        FROM trademarks t
        JOIN trademark_owners o ON t.serial_number = o.serial_number
        JOIN status_code_mapping m ON t.status_code = m.status_code
        WHERE UPPER(t.mark_identification) = UPPER(%s) AND m.live_dead = 'LIVE'
    """, (brand,))
    rows = cur.fetchall()

    if rows:
        cur.close(); conn.close()
        return ('exact', rows)

    # Round 2: ILIKE + 后验证（走GIN索引比regex快）
    words = brand.split()
    if len(words) >= 2:
        ilike_pattern = f'%{words[0]}%{words[1]}%'
    elif len(words) == 1 and len(words[0]) >= 3:
        ilike_pattern = f'%{words[0]}%'
    else:
        ilike_pattern = None

    if ilike_pattern:
        try:
            cur.execute("""
                SELECT DISTINCT t.serial_number, t.mark_identification, o.party_name,
                       t.status_code, m.live_dead
                FROM trademarks t
                JOIN trademark_owners o ON t.serial_number = o.serial_number
                JOIN status_code_mapping m ON t.status_code = m.status_code
                WHERE t.mark_identification ILIKE %s AND m.live_dead = 'LIVE'
                LIMIT 100
            """, (ilike_pattern,))
            rows = cur.fetchall()

            # 后验证: 过滤掉品牌名不匹配的（防止子串误匹配）
            if rows:
                validated = []
                brand_upper = brand.upper()
                for row in rows:
                    mark = (row[1] or '').upper()
                    # 品牌名应该是商标名的主要部分
                    if brand_upper in mark or mark in brand_upper:
                        validated.append(row)
                    elif validate_match(brand, row[1] or '') >= 0.5:
                        validated.append(row)

                if validated:
                    cur.close(); conn.close()
                    return ('fuzzy', validated)
        except Exception:
            conn.rollback()

    cur.close(); conn.close()
    return ('miss', [])


def run_step2():
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("TRUNCATE path_a_results RESTART IDENTITY")
    cur.execute("TRUNCATE path_b_results RESTART IDENTITY")
    conn.commit()

    # === 路径A ===
    cur.execute("SELECT id, plaintiff_clean FROM unique_plaintiffs ORDER BY id")
    plaintiffs = cur.fetchall()
    print(f"路径A: {len(plaintiffs)} 个原告 (8并发)...")

    a_exact = a_fuzzy = a_miss = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(query_path_a_single, p): (pid, p) for pid, p in plaintiffs}
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 500 == 0:
                print(f"  进度: {done}/{len(plaintiffs)}")

            pid, plaintiff = futures[future]
            match_type, rows = future.result()

            if match_type == 'exact': a_exact += 1
            elif match_type == 'fuzzy': a_fuzzy += 1
            else: a_miss += 1

            for row in rows:
                cur.execute("""
                    INSERT INTO path_a_results
                        (plaintiff_clean, match_type, serial_number, mark_identification,
                         owner_name, status_code, live_dead)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (plaintiff, match_type, row[0], row[1], row[2], row[3], row[4]))

            cur.execute("UPDATE unique_plaintiffs SET query_status = %s WHERE id = %s",
                        (match_type, pid))

        conn.commit()

    print(f"路径A完成: exact={a_exact}, fuzzy={a_fuzzy}, miss={a_miss}")

    # === 路径B ===
    cur.execute("SELECT id, brand_clean FROM unique_brands ORDER BY id")
    brands = cur.fetchall()
    print(f"\n路径B: {len(brands)} 个品牌 (8并发)...")

    b_exact = b_fuzzy = b_miss = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(query_path_b_single, b): (bid, b) for bid, b in brands}
        done = 0
        for future in as_completed(futures):
            done += 1
            if done % 500 == 0:
                print(f"  进度: {done}/{len(brands)}")

            bid, brand = futures[future]
            match_type, rows = future.result()

            if match_type == 'exact': b_exact += 1
            elif match_type == 'fuzzy': b_fuzzy += 1
            else: b_miss += 1

            for row in rows:
                cur.execute("""
                    INSERT INTO path_b_results
                        (brand_clean, match_type, serial_number, mark_identification,
                         owner_name, status_code, live_dead)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (brand, match_type, row[0], row[1], row[2], row[3], row[4]))

            cur.execute("UPDATE unique_brands SET query_status = %s WHERE id = %s",
                        (match_type, bid))

        conn.commit()

    print(f"路径B完成: exact={b_exact}, fuzzy={b_fuzzy}, miss={b_miss}")
    cur.close(); conn.close()


def run_step3():
    """Step 3: 汇合判定 + AI验证"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("TRUNCATE matched_companies RESTART IDENTITY")

    cur.execute("""
        SELECT case_number, plaintiff_clean, brand_clean, brand_eq_plaintiff, nature_of_suit
        FROM tro_cases
    """)
    cases = cur.fetchall()

    from collections import defaultdict
    stats = defaultdict(int)

    for case_num, plaintiff, brand, brand_eq, nature in cases:
        companies_a = set()
        if plaintiff:
            cur.execute("SELECT DISTINCT owner_name FROM path_a_results WHERE plaintiff_clean = %s", (plaintiff,))
            companies_a = set(r[0] for r in cur.fetchall())
        a_status = 'hit' if companies_a else 'miss'

        companies_b = set()
        b_status = 'skip'
        if not brand_eq and brand:
            cur.execute("SELECT DISTINCT owner_name FROM path_b_results WHERE brand_clean = %s", (brand,))
            companies_b = set(r[0] for r in cur.fetchall())
            b_status = 'hit' if companies_b else 'miss'

        # 汇合判定（修复版: A优先 + B多owner过滤 + 相似度审核）
        if a_status == 'hit' and b_status == 'hit':
            overlap = companies_a & companies_b
            if overlap:
                real_company = max(overlap, key=lambda c: validate_match(plaintiff, c))
                quality = 'exact'
                needs_review = False  # A+B双重确认，无需审核
                reason = None
            else:
                best_a = max(companies_a, key=lambda c: validate_match(plaintiff, c))
                score = validate_match(plaintiff, best_a)
                real_company = best_a
                quality = 'a_preferred'
                needs_review = score < 0.3
                reason = f'low_similarity: {score:.3f}' if needs_review else None

        elif a_status == 'hit':
            best_a = max(companies_a, key=lambda c: validate_match(plaintiff, c))
            score = validate_match(plaintiff, best_a)
            real_company = best_a
            quality = 'a_only'
            needs_review = score < 0.3
            reason = f'low_similarity: {score:.3f}' if needs_review else None

        elif b_status == 'hit':
            # B命中: owner数少→可信, owner数多→品牌名太通用,不确定
            if len(companies_b) <= 5:
                real_company = list(companies_b)[0]
                quality = 'b_only'
                needs_review = False
                reason = None
            else:
                real_company = list(companies_b)[0]
                quality = 'b_uncertain'
                needs_review = True
                reason = f'brand {brand} has {len(companies_b)} owners'
        else:
            real_company = None
            quality = 'not_found'
            needs_review = True
            reason = f'nature={nature}'

        stats[quality] += 1
        cur.execute("""
            INSERT INTO matched_companies
                (case_number, plaintiff_clean, brand_clean, real_company, match_quality, needs_review, review_reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (case_num, plaintiff, brand, real_company, quality, needs_review, reason))

    conn.commit()

    print(f"\nStep 3 汇合结果:")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    cur.execute("SELECT COUNT(*) FROM matched_companies WHERE needs_review")
    print(f"需人工审核: {cur.fetchone()[0]}")

    cur.close(); conn.close()


if __name__ == '__main__':
    print("=" * 60)
    print("Step 2 v2: 改进匹配 (word boundary + 验证)")
    print("=" * 60)
    run_step2()

    print("\n" + "=" * 60)
    print("Step 3 v2: 汇合 + AI验证")
    print("=" * 60)
    run_step3()
