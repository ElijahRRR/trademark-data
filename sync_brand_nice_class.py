"""
同步飞书 '品牌明细' (sheet 6IpYri, 12.6万行) → DB brand_nice_class

字段:
A 公司名称 | B 品牌名 | C Serial | D 注册号 | E 状态 |
F Nice编号 | G Nice类目(中) | H Nice类目(英) | I 商品/服务描述

用途: 类目级品牌侵权判定 — 品牌只在它注册的 Nice 类目下受保护,
跨类引用 (e.g. "MERICAAF Cookie Cutter" vs "MERICAAF Fireworks") 不构成侵权.

运行:
  python sync_brand_nice_class.py
"""
import re
import time

import psycopg2
from psycopg2.extras import execute_values

from lark_config import get_client
from lark_io import read_range, _get_sheet_row_count

DB_CONN = "dbname=uspto user=nextderboy"
SS_TOKEN = "ZkL0sFqKMhNO1vtq3t1cn8X7nhg"
SHEET_ID = "6IpYri"

_QUOTE_RE = re.compile(r'^[\s"\'\u201c\u201d\u2018\u2019]+|[\s"\'\u201c\u201d\u2018\u2019]+$')


def _norm(s):
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    s = _QUOTE_RE.sub("", s).strip()
    return s or None


def _norm_class(s):
    """Nice class 字符串化 + 补前导零到 3 位"""
    if not s:
        return None
    s = str(s).strip()
    if not s:
        return None
    # 抽数字
    m = re.search(r"\d+", s)
    if not m:
        return None
    n = int(m.group(0))
    if n < 1 or n > 45:
        return None
    return f"{n:03d}"


def fetch():
    total = _get_sheet_row_count(SHEET_ID, SS_TOKEN)
    print(f"  飞书行数 (含表头): {total}")
    rows = read_range(SHEET_ID, start_row=2, end_row=total,
                      start_col="A", end_col="I",
                      spreadsheet_token=SS_TOKEN)
    print(f"  读取: {len(rows)} 行")
    return rows


def main():
    t0 = time.time()
    print("=" * 60)
    print("飞书 品牌明细 → brand_nice_class")
    print("=" * 60)

    print("\n[1/3] 拉飞书…")
    rows = fetch()

    print("\n[2/3] 清洗…")
    parsed = []
    skipped_empty = 0
    for r in rows:
        r = list(r) + [None] * (9 - len(r)) if len(r) < 9 else r[:9]
        company = _norm(r[0])
        brand = _norm(r[1])
        if not brand:
            skipped_empty += 1
            continue
        serial = _norm(r[2])
        reg_no = _norm(r[3])
        status = _norm(r[4])
        is_live = bool(status and status.upper().startswith("LIVE"))
        nice_class = _norm_class(r[5])
        nice_cn = _norm(r[6])
        nice_en = _norm(r[7])
        goods = _norm(r[8])
        parsed.append((
            company, brand, brand.upper(), serial, reg_no, status, is_live,
            nice_class, nice_cn, nice_en, goods,
        ))
    print(f"  有效: {len(parsed)}  |  空: {skipped_empty}")

    # 统计
    live_cnt = sum(1 for p in parsed if p[6])
    print(f"  LIVE: {live_cnt}  ({100*live_cnt/len(parsed):.1f}%)")
    classes = {}
    for p in parsed:
        if p[7]:
            classes[p[7]] = classes.get(p[7], 0) + 1
    print(f"  涵盖 Nice 类目: {len(classes)}")
    top5 = sorted(classes.items(), key=lambda x: -x[1])[:5]
    for c, n in top5:
        print(f"    类 {c}: {n}")

    print("\n[3/3] 写库…")
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("TRUNCATE brand_nice_class RESTART IDENTITY")
    execute_values(
        cur,
        """INSERT INTO brand_nice_class
           (real_company, brand_name, brand_upper, serial_number,
            registration_number, status, is_live,
            nice_class, nice_class_cn, nice_class_en, goods_services)
           VALUES %s""",
        parsed, page_size=5000,
    )
    conn.commit()
    cur.execute("SELECT COUNT(*), COUNT(*) FILTER (WHERE is_live), COUNT(DISTINCT brand_upper) FROM brand_nice_class")
    total, live, distinct_brand = cur.fetchone()
    cur.close()
    conn.close()

    elapsed = time.time() - t0
    print(f"\n完成: 总 {total} | LIVE {live} | distinct 品牌 {distinct_brand} | 耗时 {elapsed:.1f}s")


if __name__ == "__main__":
    main()
