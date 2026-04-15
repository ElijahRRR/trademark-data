"""
把本地 DB 结果推送到飞书
- 公司概览 (ym27aR)    : ~1775 行 × 10 列
- 品牌明细 (6IpYri)    : ~126000 行 × 9 列
- 未找到清单 (wynwtK)  : ~2310 行 × 7 列
- 黑名单品牌 (sdO3YJ)  : ~20800 行 × 2 列 (公司-品牌对照)

每个 sheet 的流程:
1. ensure_rows - 不够就扩
2. clear_sheet_data - 保留表头，清空旧数据
3. write_range - 从第 2 行写入新数据
"""
import time

import psycopg2

from lark_config import SHEET_IDS
from lark_io import clear_sheet_data, ensure_rows, write_range


DB_CONN = "dbname=uspto user=nextderboy"


def _fetch_company_overview():
    """生成公司概览数据: 10 列
    列: 公司名称 | 涉案数量 | 最近一次起诉时间 | 案件号 | 匹配质量 |
        TRO原告名 | TRO品牌名 | 活跃品牌数 | 需人工审核 | 起诉类型
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    # 主查询: 每个 real_company 一行
    cur.execute("""
        SELECT mc.real_company,
               COUNT(DISTINCT mc.case_number) AS case_count,
               MAX(tc.date_filed) AS last_date,
               STRING_AGG(DISTINCT mc.case_number, ', ') AS case_numbers,
               (ARRAY_AGG(mc.match_quality ORDER BY
                   CASE mc.match_quality
                       WHEN 'exact' THEN 1
                       WHEN 'a_preferred' THEN 2
                       WHEN 'a_only' THEN 3
                       WHEN 'ai_high' THEN 4
                       WHEN 'ai_medium' THEN 5
                       WHEN 'b_only' THEN 6
                       WHEN 'ai_low' THEN 7
                       WHEN 'b_uncertain' THEN 8
                       ELSE 9
                   END
               ))[1] AS best_quality,
               STRING_AGG(DISTINCT mc.plaintiff_clean, '; ') AS plaintiffs,
               STRING_AGG(DISTINCT mc.brand_clean, '; ') AS brands,
               BOOL_OR(mc.needs_review) AS needs_review,
               STRING_AGG(DISTINCT tc.nature_of_suit, ', ') AS suit_types
        FROM matched_companies mc
        LEFT JOIN tro_cases tc ON mc.case_number = tc.case_number
        WHERE mc.real_company IS NOT NULL
        GROUP BY mc.real_company
        ORDER BY case_count DESC
    """)
    rows = cur.fetchall()

    # 预查活跃品牌数 (批量)
    cur.execute("""
        SELECT real_company, COUNT(DISTINCT mark_identification)
        FROM company_brand_details
        WHERE mark_identification IS NOT NULL AND mark_identification != ''
        GROUP BY real_company
    """)
    brand_counts = dict(cur.fetchall())

    cur.close()
    conn.close()

    out = []
    for r in rows:
        company = r[0]
        case_count = r[1]
        last_date = r[2].strftime("%Y-%m-%d") if r[2] else ""
        case_nums = (r[3] or "")
        if len(case_nums) > 500:
            case_nums = case_nums[:500] + "..."
        quality = r[4] or ""
        plaintiffs = (r[5] or "")
        if len(plaintiffs) > 300:
            plaintiffs = plaintiffs[:300] + "..."
        brands = (r[6] or "")
        if len(brands) > 300:
            brands = brands[:300] + "..."
        brand_count = brand_counts.get(company, 0)
        needs_review = "是" if r[7] else "否"
        suit_types = r[8] or ""
        out.append([
            company, case_count, last_date, case_nums, quality,
            plaintiffs, brands, brand_count, needs_review, suit_types,
        ])
    return out


def _fetch_brand_details():
    """生成品牌明细数据: 9 列
    列: 公司名称 | 品牌名 | Serial Number | 注册号 | 状态 |
        Nice编号 | Nice类目(中) | Nice类目(英) | 商品/服务描述
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT real_company, mark_identification, serial_number,
               registration_number,
               live_dead || '/' || COALESCE(category, '') AS status,
               international_code, international_desc_cn, international_desc_en,
               goods_services
        FROM company_brand_details
        WHERE mark_identification IS NOT NULL AND mark_identification != ''
        ORDER BY real_company, mark_identification, international_code
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    out = []
    for r in rows:
        reg = r[3] if r[3] and r[3] != "0000000" else "(申请中)"
        serial = str(r[2]) if r[2] is not None else ""
        gs = (r[8] or "")
        if len(gs) > 500:
            gs = gs[:500] + "..."
        out.append([
            r[0] or "", r[1] or "", serial, reg, r[4] or "",
            r[5] or "", r[6] or "", r[7] or "", gs,
        ])
    return out


def _fetch_blacklist():
    """生成黑名单品牌数据: 2 列
    列: 公司名称 | 品牌名
    (按 real_company + mark 去重的 company-brand 对照)
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT real_company, mark_identification
        FROM company_brand_details
        WHERE mark_identification IS NOT NULL AND mark_identification != ''
        ORDER BY real_company, mark_identification
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [[r[0] or "", r[1] or ""] for r in rows]


def _fetch_not_found():
    """生成未找到清单数据: 7 列
    列: 案件号 | 原告名 | 品牌名 | 匹配质量 | 起诉类型 | 审核原因 | 品牌=原告
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT mc.case_number, mc.plaintiff_clean, mc.brand_clean, mc.match_quality,
               tc.nature_of_suit, mc.review_reason, tc.brand_eq_plaintiff
        FROM matched_companies mc
        LEFT JOIN tro_cases tc ON mc.case_number = tc.case_number
        WHERE mc.match_quality = 'not_found'
        ORDER BY tc.nature_of_suit, mc.case_number
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    out = []
    for r in rows:
        out.append([
            r[0] or "",
            r[1] or "",
            r[2] or "",
            r[3] or "",
            r[4] or "",
            r[5] or "",
            "是" if r[6] else "否",
        ])
    return out


def _push(sheet_key: str, data, end_col: str):
    """通用推送: ensure_rows → clear → write
    data 是 list of lists (不含表头)
    end_col 是数据的最右列字母
    """
    sid = SHEET_IDS[sheet_key]
    n_rows = len(data)
    required = n_rows + 1  # +1 表头

    print(f"  [{sheet_key}] 推送 {n_rows} 行...")
    t0 = time.time()

    # 1. 扩容
    print("    扩容...")
    ensure_rows(sid, required)

    # 2. 清空旧数据 (保留表头)
    print("    清空旧数据...")
    cleared = clear_sheet_data(sid, start_row=2, end_col=end_col)
    print(f"    已清空 {cleared} 行")

    # 3. 写入新数据
    print(f"    写入 {n_rows} 行...")
    written = write_range(sid, start_row=2, values=data, start_col="A")

    elapsed = time.time() - t0
    print(f"  [{sheet_key}] 完成: {written} 行, 耗时 {elapsed:.1f}s")
    return written


def upload_company_overview():
    data = _fetch_company_overview()
    return _push("company_overview", data, end_col="J")


def upload_brand_details():
    data = _fetch_brand_details()
    return _push("brand_details", data, end_col="I")


def upload_not_found():
    data = _fetch_not_found()
    return _push("not_found", data, end_col="G")


def upload_blacklist():
    data = _fetch_blacklist()
    return _push("blacklist", data, end_col="B")


def upload_all():
    """按顺序推送四个 sheet (小的先写, 大的殿后)"""
    print("=" * 60)
    print("飞书数据推送")
    print("=" * 60)

    results = {}
    results["company_overview"] = upload_company_overview()
    print()
    results["not_found"] = upload_not_found()
    print()
    results["blacklist"] = upload_blacklist()
    print()
    results["brand_details"] = upload_brand_details()
    print()

    print("=" * 60)
    print("推送完成:")
    for k, v in results.items():
        print(f"  {k}: {v} 行")
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "overview":
            upload_company_overview()
        elif action == "brands":
            upload_brand_details()
        elif action == "notfound":
            upload_not_found()
        elif action == "blacklist":
            upload_blacklist()
        else:
            upload_all()
    else:
        upload_all()
