"""
同步飞书 "黑名单品牌" sheet (jF8dOw, 35,953 条) → PostgreSQL blacklist_brands

权威入口: 以飞书表为准, 规则直接读 DB 这张表.
涵盖 TRO品牌库 ∪ 其他收集 (用户手动维护的外部来源).

运行:
  python sync_blacklist_from_lark.py

增量策略: TRUNCATE + 全量重灌 (35K 行, < 5s)
"""
import re
import time
from typing import List, Tuple

import psycopg2
from psycopg2.extras import execute_values

from lark_config import SHEET_IDS, SPREADSHEET_TOKEN
from lark_io import read_range, _get_sheet_row_count

DB_CONN = "dbname=uspto user=nextderboy"


# 品牌名两端可能被飞书的文本型包裹 ("BEE" / "PAPERWORK"), 统一剥离
_QUOTE_RE = re.compile(r'^[\s"\'\u201c\u201d\u2018\u2019]+|[\s"\'\u201c\u201d\u2018\u2019]+$')


def _normalize(name: str) -> str:
    if not name:
        return ""
    n = _QUOTE_RE.sub("", name).strip()
    # 合并内部多空格
    n = re.sub(r"\s+", " ", n)
    return n


def _is_multi_word(name: str) -> bool:
    """含空格或连字符 (长度 >=2) 视为多词, 作为高置信度匹配"""
    if not name:
        return False
    if " " in name:
        return True
    if "-" in name and len(name) > 3:
        return True
    return False


def fetch_all_from_lark() -> List[Tuple[str, str, str]]:
    """拉飞书 黑名单品牌 sheet 全量 (品牌名 | 来源 | 入库日期)"""
    sheet_id = SHEET_IDS["merged_blacklist"]
    total_rows = _get_sheet_row_count(sheet_id, SPREADSHEET_TOKEN)
    print(f"  飞书行数 (含表头): {total_rows}")
    # 跳过表头, 从第 2 行开始
    rows = read_range(
        sheet_id,
        start_row=2,
        end_row=total_rows,
        start_col="A",
        end_col="C",
        spreadsheet_token=SPREADSHEET_TOKEN,
    )
    print(f"  实际读取: {len(rows)} 行")
    return rows


def sync():
    t0 = time.time()
    print("=" * 60)
    print("飞书 黑名单品牌 → blacklist_brands 全量同步")
    print("=" * 60)

    print("\n[1/3] 从飞书读取…")
    rows = fetch_all_from_lark()

    # 清洗 + 去重
    print("\n[2/3] 清洗 + 去重…")
    seen = {}  # upper -> (name, source, date, is_multi)
    skipped_empty = 0
    for row in rows:
        name_raw = row[0] if len(row) > 0 else ""
        source_raw = row[1] if len(row) > 1 else ""
        date_raw = row[2] if len(row) > 2 else ""
        name = _normalize(str(name_raw))
        if not name or len(name) < 2:
            skipped_empty += 1
            continue
        key = name.upper()
        if key in seen:
            continue
        is_multi = _is_multi_word(name)
        date_val = date_raw.strip() if date_raw else None
        if date_val and not re.match(r"^\d{4}-\d{2}-\d{2}$", date_val):
            date_val = None
        seen[key] = (name, source_raw.strip() or None, date_val, is_multi)

    multi_cnt = sum(1 for v in seen.values() if v[3])
    single_cnt = len(seen) - multi_cnt
    print(f"  有效: {len(seen)}  |  空/无效: {skipped_empty}")
    print(f"  多词: {multi_cnt}  |  单词: {single_cnt}")

    print("\n[3/3] 全量写入 DB…")
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("TRUNCATE blacklist_brands RESTART IDENTITY")
    data = [
        (name, key, source, date_val, is_multi)
        for key, (name, source, date_val, is_multi) in seen.items()
    ]
    execute_values(
        cur,
        "INSERT INTO blacklist_brands (brand_name, brand_upper, source, added_date, is_multi_word) VALUES %s",
        data,
        page_size=5000,
    )
    conn.commit()
    cur.execute("SELECT COUNT(*), COUNT(*) FILTER (WHERE is_multi_word), COUNT(*) FILTER (WHERE NOT is_multi_word) FROM blacklist_brands")
    total, mw, sw = cur.fetchone()
    cur.close()
    conn.close()

    elapsed = time.time() - t0
    print(f"\n完成: 总 {total} | 多词 {mw} | 单词 {sw} | 耗时 {elapsed:.1f}s")
    return total


if __name__ == "__main__":
    sync()
