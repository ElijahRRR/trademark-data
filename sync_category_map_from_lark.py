"""
同步飞书 "类目映射表" (6832 条) → PostgreSQL amazon_walmart_category_map

替换原 xlsx 导入 (audit_category_mapping.load_mapping_xlsx).
新表增强字段:
- 销售资质要求 (sales_qualification):   "需Walmart审批" / "附条件允许" / "允许" / "禁售"
- 所需认证/文件 (cert_required_text):   FDA MoCRA | FCC | UL | ...
- IP侵权风险 (ip_risk_level):            高/中/低
- 合规说明 (compliance_notes):           长中文说明, 供 LLM 注入

运行:
  python sync_category_map_from_lark.py
"""
import re
import time
from typing import List

import psycopg2
from psycopg2.extras import execute_values

from lark_config import get_client
from lark_io import read_range, _get_sheet_row_count

DB_CONN = "dbname=uspto user=nextderboy"

# 飞书: 类目映射表 (独立 spreadsheet)
CATEGORY_MAP_TOKEN = "Gx9HsYEO6hA7cMtK28acVuzonwc"
CATEGORY_MAP_SHEET = "0bdc8b"


CONF_MAP = {
    "LLM_KB高": "0.85", "LLM_KB中": "0.70", "LLM_KB低": "0.50",
    "真实_高":  "0.95", "真实_中":  "0.80", "真实_低":  "0.60",
    "LLM高":    "0.95", "LLM中":    "0.75", "LLM低":    "0.55",
    "高":       "0.90", "中":       "0.70", "低":       "0.50",
}


def _clean(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s and s.upper() != "NONE" else None


def _conf(v):
    if not v:
        return None
    s = str(v).strip()
    if s in CONF_MAP:
        return CONF_MAP[s]
    try:
        return str(float(s))
    except ValueError:
        return None


def fetch_all() -> List[List[str]]:
    """拉飞书类目映射表全量 (跳过表头)"""
    total = _get_sheet_row_count(CATEGORY_MAP_SHEET, CATEGORY_MAP_TOKEN)
    print(f"  飞书行数 (含表头): {total}")
    rows = read_range(
        CATEGORY_MAP_SHEET,
        start_row=2,
        end_row=total,
        start_col="A",
        end_col="T",
        spreadsheet_token=CATEGORY_MAP_TOKEN,
    )
    print(f"  读取: {len(rows)} 行")
    return rows


def sync():
    t0 = time.time()
    print("=" * 60)
    print("飞书类目映射表 → amazon_walmart_category_map")
    print("=" * 60)

    print("\n[1/3] 从飞书读取…")
    rows = fetch_all()

    print("\n[2/3] 解析 + 去重…")
    # 列顺序 (0-based):
    # 0 Walmart Category | 1 Walmart PTG | 2 Walmart Product Type |
    # 3 L1 | 4 L2 | 5 L3 | 6 BSR | 7 Amazon Path |
    # 8 ASIN样本数 | 9 BSR分布 | 10 映射置信度 | 11 映射来源 |
    # 12 LLM判定 | 13 LLM理由 |
    # 14 销售资质要求 | 15 所需认证/文件 | 16 IP侵权风险 | 17 合规说明 |
    # 18 审核状态 | 19 审核备注
    parsed = []
    seen = set()
    for r in rows:
        # 补齐到 20 列
        r = list(r) + [None] * (20 - len(r)) if len(r) < 20 else r[:20]
        walmart_pt = _clean(r[2])
        if not walmart_pt:
            continue
        rec_path = _clean(r[7])
        rec_l1, rec_l2, rec_l3, rec_bsr = _clean(r[3]), _clean(r[4]), _clean(r[5]), _clean(r[6])
        if not rec_path:
            parts = [p for p in (rec_l1, rec_l2, rec_l3) if p]
            rec_path = " > ".join(parts) if parts else None
        if not rec_path:
            continue
        key = (rec_path, walmart_pt)
        if key in seen:
            continue
        seen.add(key)

        try:
            sample = int(r[8]) if r[8] not in (None, "", "None") else 0
        except (TypeError, ValueError):
            sample = 0

        cert = _clean(r[15])
        ip_risk = _clean(r[16])
        parsed.append((
            rec_path,                            # amazon_path
            walmart_pt,                          # walmart_product_type
            _clean(r[0]),                        # walmart_category
            _clean(r[1]),                        # walmart_ptg
            rec_l1, rec_l2, rec_l3, rec_bsr,
            rec_path,                            # recommended_amazon_path (same as amazon_path)
            _conf(r[10]),                        # confidence
            sample,                              # history_sample_count
            _clean(r[11]),                       # source (映射来源)
            cert,                                # cert_required_text
            ip_risk,                             # ip_risk_level
            _clean(r[17]),                       # compliance_notes
            _clean(r[14]),                       # sales_qualification
            _clean(r[19]),                       # notes (审核备注)
            (cert is None or cert in ("无特殊限制", "无")) and ip_risk != "高",  # is_safe
        ))
    print(f"  有效去重: {len(parsed)} 条")

    print("\n[3/3] 全量重灌…")
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("TRUNCATE amazon_walmart_category_map RESTART IDENTITY")

    COLS = [
        "amazon_path", "walmart_product_type",
        "walmart_category", "walmart_ptg",
        "recommended_amazon_l1", "recommended_amazon_l2", "recommended_amazon_l3",
        "recommended_amazon_bsr", "recommended_amazon_path",
        "confidence", "history_sample_count", "source",
        "cert_required_text", "ip_risk_level",
        "compliance_notes", "sales_qualification", "notes",
        "is_safe",
    ]
    execute_values(
        cur,
        f"INSERT INTO amazon_walmart_category_map ({','.join(COLS)}) VALUES %s",
        parsed,
        page_size=2000,
    )
    conn.commit()

    # 统计
    cur.execute("SELECT COUNT(*) FROM amazon_walmart_category_map")
    total = cur.fetchone()[0]
    cur.execute("""
        SELECT sales_qualification, COUNT(*)
        FROM amazon_walmart_category_map
        WHERE sales_qualification IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC
    """)
    quals = cur.fetchall()
    cur.execute("""
        SELECT ip_risk_level, COUNT(*)
        FROM amazon_walmart_category_map
        WHERE ip_risk_level IS NOT NULL
        GROUP BY 1 ORDER BY 2 DESC
    """)
    risks = cur.fetchall()
    cur.close()
    conn.close()

    elapsed = time.time() - t0
    print(f"\n完成: {total} 条 | 耗时 {elapsed:.1f}s")
    print("\n销售资质分布:")
    for q, n in quals:
        print(f"  {q}: {n}")
    print("\nIP 风险分布:")
    for q, n in risks:
        print(f"  {q}: {n}")
    return total


if __name__ == "__main__":
    sync()
