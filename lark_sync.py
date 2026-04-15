"""
飞书 ↔ 本地 PostgreSQL 双向同步

主要函数:
- read_lark_tro_cases() -> List[dict]: 从飞书读取所有 Tro案件
- sync_to_db() -> (新增数, 更新数): UPSERT 到本地 tro_cases
- get_unprocessed_cases() -> List[str]: 找出还未匹配的 case_numbers
"""
import time
from datetime import datetime
from typing import List, Dict, Tuple

import psycopg2

from lark_config import SHEET_IDS, TRO_COLUMNS
from lark_io import read_range, _get_sheet_row_count
from batch_process import clean_plaintiff, clean_brand


DB_CONN = "dbname=uspto user=nextderboy"


def read_lark_tro_cases() -> List[Dict]:
    """从飞书 Tro案件 sheet 读取所有数据，返回字典列表"""
    sheet_id = SHEET_IDS["tro_cases"]
    total_rows = _get_sheet_row_count(sheet_id, None) if False else None
    # 直接读到末尾 (read_range 自己查行数)
    print(f"  从飞书读取 Tro案件 sheet...")
    t0 = time.time()
    rows = read_range(sheet_id, start_row=2, end_row=None, end_col="T")
    elapsed = time.time() - t0
    print(f"  读取 {len(rows)} 行，耗时 {elapsed:.1f}s")

    cases = []
    for row in rows:
        # 补齐到 20 列
        row = (row + [""] * 20)[:20]
        case_dict = dict(zip(TRO_COLUMNS, row))
        # 跳过空行
        if not case_dict.get("case_number", "").strip():
            continue
        cases.append(case_dict)
    return cases


def _parse_date(s: str):
    """飞书日期格式: 2026-04-10 -> date 对象"""
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def sync_to_db(cases: List[Dict]) -> Tuple[int, int]:
    """把飞书数据 UPSERT 到本地 tro_cases 表

    Returns:
        (新增数, 更新数)
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # 先取现有 case_numbers
    cur.execute("SELECT case_number FROM tro_cases")
    existing = set(r[0] for r in cur.fetchall())

    inserted = 0
    updated = 0
    skipped = 0

    for case in cases:
        case_number = case["case_number"].strip()
        if not case_number:
            continue

        date_filed = _parse_date(case.get("date_filed", ""))
        nature = (case.get("nature_of_suit") or "").strip()
        plaintiff_raw = (case.get("plaintiff") or "").strip()
        brand_raw = (case.get("brand") or "").strip()
        plaintiff_clean = clean_plaintiff(plaintiff_raw)
        brand_clean = clean_brand(brand_raw)
        brand_eq = (brand_raw == plaintiff_raw) or (brand_clean == plaintiff_clean)

        try:
            cur.execute("""
                INSERT INTO tro_cases (case_number, date_filed, nature_of_suit,
                    plaintiff_raw, brand_raw, plaintiff_clean, brand_clean, brand_eq_plaintiff)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (case_number) DO UPDATE SET
                    date_filed = EXCLUDED.date_filed,
                    nature_of_suit = EXCLUDED.nature_of_suit,
                    plaintiff_raw = EXCLUDED.plaintiff_raw,
                    brand_raw = EXCLUDED.brand_raw,
                    plaintiff_clean = EXCLUDED.plaintiff_clean,
                    brand_clean = EXCLUDED.brand_clean,
                    brand_eq_plaintiff = EXCLUDED.brand_eq_plaintiff
            """, (case_number, date_filed, nature, plaintiff_raw, brand_raw,
                  plaintiff_clean, brand_clean, brand_eq))
            if case_number in existing:
                updated += 1
            else:
                inserted += 1
        except Exception as e:
            print(f"  跳过 {case_number}: {e}")
            conn.rollback()
            skipped += 1
            continue

    conn.commit()
    cur.close()
    conn.close()
    return inserted, updated


def get_unprocessed_cases() -> List[str]:
    """找出 tro_cases 中还没有 matched_companies 记录的 case_numbers"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT tc.case_number
        FROM tro_cases tc
        LEFT JOIN matched_companies mc ON tc.case_number = mc.case_number
        WHERE mc.case_number IS NULL
        ORDER BY tc.case_number
    """)
    cases = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return cases


def get_db_summary() -> Dict:
    """获取本地 DB 数据概览"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM tro_cases")
    total_cases = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM matched_companies")
    matched_total = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(DISTINCT real_company)
        FROM matched_companies
        WHERE real_company IS NOT NULL
    """)
    company_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM company_brand_details")
    brand_detail_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM matched_companies WHERE match_quality = 'not_found'
    """)
    not_found = cur.fetchone()[0]

    cur.close()
    conn.close()
    return {
        "total_cases": total_cases,
        "matched_total": matched_total,
        "company_count": company_count,
        "brand_detail_count": brand_detail_count,
        "not_found": not_found,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("飞书 → 本地 DB 同步测试")
    print("=" * 60)

    cases = read_lark_tro_cases()
    print(f"\n飞书读取: {len(cases)} 个案件")
    print(f"  示例: {cases[0]['case_number']} | {cases[0]['plaintiff'][:30]}")

    print("\n开始同步到 PostgreSQL...")
    inserted, updated = sync_to_db(cases)
    print(f"  新增: {inserted}, 更新: {updated}")

    print("\n本地 DB 概览:")
    summary = get_db_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\n未处理案件:")
    pending = get_unprocessed_cases()
    print(f"  待处理: {len(pending)} 个")
    if pending[:3]:
        print(f"  前 3 个: {pending[:3]}")
