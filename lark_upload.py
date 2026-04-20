"""
把本地 DB 结果推送到飞书

输出 sheet:
- 公司概览      (ym27aR)  : ~1775 行 × 10 列
- 品牌明细      (6IpYri)  : ~126000 行 × 9 列
- 未找到清单    (wynwtK)  : ~2310 行 × 7 列
- TRO品牌库     (sdO3YJ)  : ~19000 行 × 3 列 (公司名称 | 品牌名 | 入库日期)
- 黑名单品牌    (jF8dOw)  : ~36000 行 × 3 列 (品牌名 | 来源 | 入库日期)
  = TRO品牌库 ∪ 其他收集 去重

每个 sheet 的流程:
1. ensure_rows - 不够就扩
2. clear_sheet_data - 保留表头，清空旧数据
3. write_range - 从第 2 行写入新数据
"""
import time
from datetime import datetime, timedelta

import psycopg2

from lark_config import SHEET_IDS
from lark_io import clear_sheet_data, ensure_rows, read_range, write_range


DB_CONN = "dbname=uspto user=nextderboy"

# 飞书/Excel 日期序列号基准: day 0 = 1899-12-30
_DATE_EPOCH = datetime(1899, 12, 30)


def _normalize_date(val) -> str:
    """将飞书单元格值统一转为 YYYY-MM-DD 字符串。
    处理: 日期字符串 / 数字序列号 / None/空值
    """
    if val is None:
        return ""
    s = str(val).strip()
    if not s:
        return ""
    # 已经是 YYYY-MM-DD 格式
    if len(s) == 10 and s[4] == "-" and s[7] == "-":
        return s
    # 尝试数字序列号
    try:
        serial = int(float(s))
        if 30000 < serial < 60000:  # 合理范围 ~1982 ~ 2064
            return (_DATE_EPOCH + timedelta(days=serial)).strftime("%Y-%m-%d")
    except (ValueError, OverflowError):
        pass
    return s


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
    """生成品牌明细数据: 10 列
    列: 公司名称 | 品牌名 | Serial Number | 注册号 | 状态 |
        Nice编号 | Nice类目(中) | Nice类目(英) | 商品/服务描述 | 入库日期
    入库日期保留飞书中已有记录的日期，仅新增记录赋今日日期。
    """
    # 读取飞书现有入库日期，避免覆写历史日期
    existing_dates = {}
    try:
        sid = SHEET_IDS["brand_details"]
        print("    读取已有入库日期...")
        existing = read_range(sid, start_row=2, end_col="J")
        for r in existing:
            if len(r) >= 6 and r[0] and r[1]:
                # key = (公司, 品牌, Serial, Nice编号)
                key = (str(r[0]).strip(), str(r[1]).strip(),
                       str(r[2]).strip() if r[2] else "",
                       str(r[5]).strip() if len(r) > 5 and r[5] else "")
                date = _normalize_date(r[9] if len(r) >= 10 else None)
                if date:
                    existing_dates[key] = date
        print(f"    已有入库日期: {len(existing_dates)} 条")
    except Exception as e:
        print(f"    读取已有日期失败 (将全用今日日期): {e}")

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

    today = time.strftime("%Y-%m-%d")
    out = []
    for r in rows:
        company = r[0] or ""
        brand = r[1] or ""
        serial = str(r[2]) if r[2] is not None else ""
        int_code = r[5] or ""
        key = (company, brand, serial, int_code)
        date = existing_dates.get(key, today)

        reg = r[3] if r[3] and r[3] != "0000000" else "(申请中)"
        gs = (r[8] or "")
        if len(gs) > 500:
            gs = gs[:500] + "..."
        out.append([
            company, brand, serial, reg, r[4] or "",
            int_code, r[6] or "", r[7] or "", gs, date,
        ])
    return out


def _fetch_tro_brands():
    """生成 TRO品牌库 数据: 3 列
    列: 公司名称 | 品牌名 | 入库日期
    (按 real_company + mark 去重的 company-brand 对照)
    保留飞书中已有记录的入库日期，只给新品牌赋今日日期。
    """
    # 读取飞书现有日期映射，避免覆写历史入库日期
    existing_dates = {}
    try:
        sid = SHEET_IDS["tro_brands"]
        existing_rows = read_range(sid, start_row=2, end_col="C")
        for r in existing_rows:
            if len(r) >= 2 and r[0] and r[1]:
                key = (str(r[0]).strip(), str(r[1]).strip())
                existing_dates[key] = _normalize_date(r[2] if len(r) >= 3 else None)
        print(f"    读取已有入库日期: {len(existing_dates)} 条")
    except Exception as e:
        print(f"    读取已有日期失败 (将全用今日日期): {e}")

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

    today = time.strftime("%Y-%m-%d")
    out = []
    for r in rows:
        company = r[0] or ""
        brand = r[1] or ""
        date = existing_dates.get((company, brand)) or today
        out.append([company, brand, date])
    return out


def _read_other_collected():
    """从飞书读取 '其他收集' sheet 的品牌数据.
    返回 list of [品牌名, 来源, 入库日期].
    """
    sid = SHEET_IDS["other_collected"]
    rows = read_range(sid, start_row=2, end_col="C")  # 跳过表头
    out = []
    for r in rows:
        brand = (str(r[0]) or "").strip() if len(r) > 0 and r[0] else ""
        source = (str(r[1]) or "").strip() if len(r) > 1 and r[1] else ""
        date = _normalize_date(r[2] if len(r) > 2 else None)
        if brand:
            out.append([brand, source, date])
    return out


def _fetch_not_found():
    """生成未找到清单数据: 8 列
    列: 立案日期 | 案件号 | 原告名 | 品牌名 | 匹配质量 | 起诉类型 | 审核原因 | 品牌=原告
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT tc.date_filed, mc.case_number, mc.plaintiff_clean, mc.brand_clean, mc.match_quality,
               tc.nature_of_suit, mc.review_reason, tc.brand_eq_plaintiff
        FROM matched_companies mc
        LEFT JOIN tro_cases tc ON mc.case_number = tc.case_number
        WHERE mc.match_quality = 'not_found'
        ORDER BY tc.date_filed DESC NULLS LAST, mc.case_number DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    out = []
    for r in rows:
        out.append([
            str(r[0]) if r[0] else "",
            r[1] or "",
            r[2] or "",
            r[3] or "",
            r[4] or "",
            r[5] or "",
            r[6] or "",
            "是" if r[7] else "否",
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
    return _push("brand_details", data, end_col="J")


def upload_not_found():
    data = _fetch_not_found()
    return _push("not_found", data, end_col="H")


def upload_tro_brands():
    """推送 TRO品牌库 (公司名称 | 品牌名 | 入库日期)"""
    data = _fetch_tro_brands()
    return _push("tro_brands", data, end_col="C")


def upload_merged_blacklist():
    """合并 TRO品牌库 + 其他收集 → 黑名单品牌 (去重)

    品牌名 | 来源 | 入库日期
    - TRO品牌库来源 → 来源='TRO品牌', 日期保留 TRO品牌库中的入库日期
    - 其他收集来源 → 来源=该行的来源值, 日期保留其他收集中的入库日期
    """
    today = time.strftime("%Y-%m-%d")
    merged = {}  # brand_upper -> [品牌名, 来源, 入库日期]

    # 1. 从飞书读 TRO品牌库 (保留已有入库日期)
    print("    读取 TRO品牌库...")
    tro_sid = SHEET_IDS["tro_brands"]
    tro_rows = read_range(tro_sid, start_row=2, end_col="C")
    tro_count = 0
    for r in tro_rows:
        brand = str(r[1]).strip() if len(r) >= 2 and r[1] else ""
        if not brand:
            continue
        date = _normalize_date(r[2] if len(r) >= 3 else None) or today
        key = brand.upper()
        if key not in merged:
            merged[key] = [brand, "TRO品牌", date]
            tro_count += 1
        else:
            # 同品牌多公司时取最早日期
            if date and date < merged[key][2]:
                merged[key][2] = date
    print(f"    TRO品牌: {tro_count} 个 (去重)")

    # 2. 从飞书读 其他收集
    print("    读取 其他收集...")
    other = _read_other_collected()
    print(f"    其他收集: {len(other)} 条")

    other_added = 0
    for row in other:
        key = row[0].upper()
        if key not in merged:
            merged[key] = [row[0], row[1] or "其他", row[2] or today]
            other_added += 1

    # 按品牌名排序
    data = sorted(merged.values(), key=lambda x: x[0].upper())
    print(f"    合并去重: TRO={tro_count} + 其他新增={other_added} → {len(data)}")

    return _push("merged_blacklist", data, end_col="C")


def upload_all():
    """按顺序推送所有 sheet (小的先写, 大的殿后)"""
    print("=" * 60)
    print("飞书数据推送")
    print("=" * 60)

    results = {}
    results["company_overview"] = upload_company_overview()
    print()
    results["not_found"] = upload_not_found()
    print()
    results["tro_brands"] = upload_tro_brands()
    print()
    results["merged_blacklist"] = upload_merged_blacklist()
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
        elif action == "tro":
            upload_tro_brands()
        elif action == "blacklist":
            upload_merged_blacklist()
        else:
            upload_all()
    else:
        upload_all()
