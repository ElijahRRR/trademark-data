#!/usr/bin/env python3
"""
对 not_found 案例做增强匹配:
1. USPTO常见的 "LastName, FirstName" 格式
2. 去标点后精确匹配
3. pg_trgm 相似度匹配
4. 品牌名精确查商标
"""

import psycopg2, sys, json

DB_CONN = "dbname=uspto user=nextderboy"

def clean_name(name):
    """去掉标点和多余空格"""
    import re
    name = re.sub(r'[.,;:\'\"()\[\]]+', ' ', name)
    return ' '.join(name.split()).strip()

def flip_person_name(name):
    """
    'Abraham Hunter' → 'Hunter, Abraham'
    'Holly Denise Simental' → 'Simental, Holly Denise'
    """
    parts = name.strip().split()
    if len(parts) == 2:
        return f"{parts[1]}, {parts[0]}"
    elif len(parts) == 3:
        return f"{parts[2]}, {parts[0]} {parts[1]}"
    return None

def try_match_plaintiff(cur, plaintiff):
    """多策略匹配原告名"""
    if not plaintiff or len(plaintiff.strip()) < 2:
        return None

    # 策略1: 精确匹配 (已有，但这里用更宽松的方式)
    cleaned = clean_name(plaintiff)
    cur.execute("""
        SELECT DISTINCT o.party_name
        FROM trademark_owners o
        JOIN trademarks t ON o.serial_number = t.serial_number
        JOIN status_code_mapping m ON t.status_code = m.status_code
        WHERE UPPER(REPLACE(REPLACE(o.party_name, ',', ''), '.', '')) = UPPER(REPLACE(REPLACE(%s, ',', ''), '.', ''))
          AND m.live_dead = 'LIVE'
        LIMIT 5
    """, (cleaned,))
    rows = cur.fetchall()
    if rows:
        return ('clean_exact', [r[0] for r in rows])

    # 策略2: 翻转人名格式 (Abraham Hunter → Hunter, Abraham)
    flipped = flip_person_name(plaintiff)
    if flipped:
        cur.execute("""
            SELECT DISTINCT o.party_name
            FROM trademark_owners o
            JOIN trademarks t ON o.serial_number = t.serial_number
            JOIN status_code_mapping m ON t.status_code = m.status_code
            WHERE UPPER(o.party_name) LIKE UPPER(%s)
              AND m.live_dead = 'LIVE'
            LIMIT 5
        """, (f'%{flipped}%',))
        rows = cur.fetchall()
        if rows:
            return ('name_flip', [r[0] for r in rows])

    # 策略3: pg_trgm相似度 (仅对长度>=5的名字)
    if len(cleaned) >= 5:
        try:
            cur.execute("""
                SELECT DISTINCT o.party_name, similarity(o.party_name, %s) AS sim
                FROM trademark_owners o
                JOIN trademarks t ON o.serial_number = t.serial_number
                JOIN status_code_mapping m ON t.status_code = m.status_code
                WHERE o.party_name %% %s
                  AND m.live_dead = 'LIVE'
                ORDER BY sim DESC
                LIMIT 5
            """, (plaintiff, plaintiff))
            rows = cur.fetchall()
            if rows and rows[0][1] >= 0.4:
                return ('trgm', [r[0] for r in rows])
        except Exception:
            cur.connection.rollback()

    return None

def try_match_brand(cur, brand):
    """品牌名查商标"""
    if not brand or len(brand.strip()) < 2:
        return None

    # 只包含中文 → 跳过
    if all('\u4e00' <= c <= '\u9fff' or not c.isalpha() for c in brand):
        return None

    cleaned = clean_name(brand)

    # 精确匹配品牌名
    cur.execute("""
        SELECT DISTINCT o.party_name
        FROM trademarks t
        JOIN trademark_owners o ON t.serial_number = o.serial_number
        JOIN status_code_mapping m ON t.status_code = m.status_code
        WHERE UPPER(t.mark_identification) = UPPER(%s)
          AND m.live_dead = 'LIVE'
        LIMIT 10
    """, (cleaned,))
    rows = cur.fetchall()
    if rows:
        return ('brand_exact', [r[0] for r in rows])

    return None

def process_batch(offset, batch_size):
    """处理一批 not_found 案例"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # 获取 not_found 案例
    cur.execute("""
        SELECT mc.case_number, mc.plaintiff_clean, mc.brand_clean, t.brand_eq_plaintiff
        FROM matched_companies mc
        JOIN tro_cases t ON mc.case_number = t.case_number
        WHERE mc.match_quality = 'not_found'
          AND mc.plaintiff_clean IS NOT NULL
          AND mc.plaintiff_clean NOT IN ('', '？', '?')
        ORDER BY mc.case_number
        OFFSET %s LIMIT %s
    """, (offset, batch_size))
    cases = cur.fetchall()

    results = []
    for case_num, plaintiff, brand, brand_eq in cases:
        # 先试原告名
        match = try_match_plaintiff(cur, plaintiff)
        source = 'a'

        # 再试品牌名 (如果品牌和原告不同)
        if not match and not brand_eq and brand:
            match = try_match_brand(cur, brand)
            source = 'b'

        # 品牌=原告时也试品牌精确匹配
        if not match and brand_eq and brand:
            match = try_match_brand(cur, brand)
            source = 'b'

        if match:
            strategy, companies = match
            results.append({
                'case_number': case_num,
                'plaintiff': plaintiff,
                'brand': brand,
                'strategy': strategy,
                'source': source,
                'companies': companies[:3]  # 最多3个
            })

    cur.close()
    conn.close()
    return results


def process_brands_only(offset, batch_size):
    """处理仅有品牌名的 not_found 案例"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("""
        SELECT mc.case_number, mc.brand_clean
        FROM matched_companies mc
        WHERE mc.match_quality = 'not_found'
          AND (mc.plaintiff_clean = '' OR mc.plaintiff_clean IS NULL)
          AND mc.brand_clean IS NOT NULL AND mc.brand_clean != ''
        ORDER BY mc.case_number
        OFFSET %s LIMIT %s
    """, (offset, batch_size))
    cases = cur.fetchall()

    results = []
    for case_num, brand in cases:
        match = try_match_brand(cur, brand)
        if match:
            strategy, companies = match
            results.append({
                'case_number': case_num,
                'brand': brand,
                'strategy': strategy,
                'companies': companies[:3]
            })

    cur.close()
    conn.close()
    return results


if __name__ == '__main__':
    mode = sys.argv[1]  # 'plaintiff' or 'brand_only'
    offset = int(sys.argv[2])
    batch_size = int(sys.argv[3])

    if mode == 'plaintiff':
        results = process_batch(offset, batch_size)
    else:
        results = process_brands_only(offset, batch_size)

    # 输出JSON结果
    print(json.dumps(results, ensure_ascii=False))
