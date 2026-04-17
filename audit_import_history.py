"""
从飞书'错误商品记录'表导入历史违规产品到 walmart_suspension_history

数据源: 飞书 spreadsheet YlA1szPAAhW7CCtmG5hcp6vkndd
- 日报表 (RzUg8 等): 含完整错误原因文本, 列布局 A-O
- 监管合规删除 (eGjQRX): 用于交叉验证 is_deleted

日报表列布局 (无表头):
A=店铺 B=Amazon ASIN C=沃尔玛 SKU D=标题($$ProductType 拼接) E=空 F=空
G=ProductType H=状态 I=状态2 J=价格 K=空 L=空 M=错误原因 N=时间 O=feedId

用法:
    python3 audit_import_history.py                     # 导入所有已知日报表
    python3 audit_import_history.py --sheet RzUg8 --date 2026-04-17
    python3 audit_import_history.py --mark-deleted       # 仅交叉 eGjQRX 更新 is_deleted
"""
import argparse
import re
import sys
import time
from decimal import Decimal, InvalidOperation

import psycopg2
from psycopg2.extras import execute_values

from audit_reason_classifier import classify_reason
from lark_io import read_range


# 识别明显的表头/汇总行, 防止被当成数据插入
HEADER_LIKE_VALUES = {
    "店铺", "SKU", "商品名称", "描述", "品牌", "ProductType", "错误原因",
    "是否删除", "删除时间", "删除_feedId", "停用_feedId",
    "状态", "价格", "数量", "数量（总）", "ASIN", "商品ID",
}

DATETIME_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}[\sT]\d{1,2}:\d{2}")
DATE_RE = re.compile(r"^\d{4}-\d{1,2}-\d{1,2}$")


WALMART_SS_TOKEN = "YlA1szPAAhW7CCtmG5hcp6vkndd"

# sheet_id → (source_date, 注释)
DAILY_SHEETS = {
    "RzUg8":  ("2026-04-17", "2026.4.17问题商品"),
    "3lHctO": ("2026-04-16", "2026.4.16问题商品"),
    "1yX8be": ("2026-04-15", "2026.4.15问题商品"),
    "1Falzi": ("2026-04-14", "2026.4.14问题商品"),
    "2zRkic": ("2026-04-13", "2026.4.13问题商品"),
}

# 表头标题 → 标准字段名 (兼容不同版本布局)
HEADER_FIELD_MAP = {
    "店铺": "shop",
    "SKU": "amazon_asin",          # SKU 列其实存 Amazon ASIN
    "ASIN": "amazon_asin",
    "商品ID": "amazon_asin",
    "WPID": "walmart_sku",         # WPID 是沃尔玛内部 SKU
    "沃尔玛SKU": "walmart_sku",
    "商品名称": "title",
    "标题": "title",
    "ProductType": "product_type",
    "产品类型": "product_type",
    "状态": "status",
    "生命周期": "status2",
    "价格": "price",
    "库存": None,                   # 忽略
    "上次更新": None,               # 忽略
    "错误原因": "reason_raw",
    "删除时间": "flagged_at",
    "feedId": "feed_id",
}

# RzUg8 同时含两种子布局, 按 status 字段位置动态识别
# 新格式 (常见于 A085): col 4,5,10,11 空; col 6=ProductType, 12=reason, 13=date, 14=feedId
RZUG8_NEW_COL_MAP = {
    0: "shop", 1: "amazon_asin", 2: "walmart_sku", 3: "title",
    6: "product_type", 7: "status", 8: "status2", 9: "price",
    12: "reason_raw", 13: "flagged_at", 14: "feed_id",
}
# 老格式: col 4=ProductType, 5=状态, 6=生命周期, 7=价格, 10=reason, 11=date, 12=feedId
RZUG8_OLD_COL_MAP = {
    0: "shop", 1: "amazon_asin", 2: "walmart_sku", 3: "title",
    4: "product_type", 5: "status", 6: "status2", 7: "price",
    10: "reason_raw", 11: "flagged_at", 12: "feed_id",
}
STATUS_VALUES = {"UNPUBLISHED", "SYSTEM_PROBLEM", "ACTIVE", "PUBLISHED"}

def _pick_col_map_for_row(row):
    """RzUg8 无表头时, 按 status 字段位置判断新/老布局"""
    def _at(i):
        return str(row[i]).strip() if i < len(row) and row[i] else ""
    if _at(7) in STATUS_VALUES:
        return RZUG8_NEW_COL_MAP
    if _at(5) in STATUS_VALUES:
        return RZUG8_OLD_COL_MAP
    # 兜底: 新格式 (ProductType 可能是 'default' / 空)
    return RZUG8_NEW_COL_MAP

SHEET_COMPLIANCE_DELETED = "eGjQRX"

DB_CONN = "dbname=uspto user=nextderboy"


def _parse_price(s):
    if not s:
        return None
    try:
        return Decimal(str(s).strip())
    except (InvalidOperation, ValueError):
        return None


def _split_title(raw_title):
    """标题和 ProductType 可能用 $$ 拼接. 返回 (clean_title, embedded_ptype)."""
    if not raw_title:
        return None, None
    if "$$" in raw_title:
        parts = raw_title.split("$$", 1)
        return parts[0].strip(), parts[1].strip()
    return raw_title.strip(), None


def _clean_cell(v):
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _detect_header(rows):
    """
    检测 rows[0] 是否是表头; 若是则返回 col_map {idx: std_field_name}, 否则返回 None.
    """
    if not rows:
        return None
    first = rows[0]
    # 典型表头特征: 含 '店铺' 且另外有 SKU / WPID / 商品名称 中至少一个
    header_values = [str(c).strip() if c is not None else "" for c in first]
    if "店铺" not in header_values:
        return None
    if not any(h in header_values for h in ("SKU", "WPID", "商品名称", "ProductType")):
        return None

    col_map = {}
    for idx, name in enumerate(header_values):
        if name in HEADER_FIELD_MAP:
            std = HEADER_FIELD_MAP[name]
            if std is None:
                continue
            # 若同名重复(如多列都叫 "SKU"), 保留第一个
            if std not in col_map.values():
                col_map[idx] = std
    return col_map


def _row_to_dict(row, col_map):
    """按 col_map 把 row 转为标准字段 dict"""
    out = {
        "shop": None, "amazon_asin": None, "walmart_sku": None, "feed_id": None,
        "title": None, "product_type": None, "price": None,
        "status": None, "status2": None, "reason_raw": None, "flagged_at": None,
    }
    for idx, field in col_map.items():
        if idx < len(row):
            out[field] = row[idx]
    return out


def _parse_row(row, source_sheet_id, source_date, col_map):
    """
    row 为 list, 根据 col_map 提取标准字段.
    返回 dict, 若关键字段缺失(asin & sku 都没)或疑似表头行则返回 None.
    """
    raw = _row_to_dict(row, col_map)

    shop = _clean_cell(raw["shop"])
    amazon_asin = _clean_cell(raw["amazon_asin"])
    walmart_sku = _clean_cell(raw["walmart_sku"])
    raw_title = _clean_cell(raw["title"])
    product_type = _clean_cell(raw["product_type"])
    status = _clean_cell(raw["status"])
    status2 = _clean_cell(raw["status2"])
    price_raw = _clean_cell(raw["price"])
    reason_raw = _clean_cell(raw["reason_raw"])
    flagged_at_raw = _clean_cell(raw["flagged_at"])
    feed_id = _clean_cell(raw["feed_id"])

    if not walmart_sku and not amazon_asin:
        return None

    # 表头行识别兜底
    if shop in HEADER_LIKE_VALUES and (amazon_asin in HEADER_LIKE_VALUES or walmart_sku in HEADER_LIKE_VALUES):
        return None

    # flagged_at 必须是合法时间戳/日期, 否则置空
    flagged_at = None
    if flagged_at_raw and (DATETIME_RE.match(flagged_at_raw) or DATE_RE.match(flagged_at_raw)):
        flagged_at = flagged_at_raw

    title_clean, embedded_ptype = _split_title(raw_title)
    if not product_type and embedded_ptype:
        product_type = embedded_ptype

    cls = classify_reason(reason_raw or "")

    # price 若是表头"价格"一类, _parse_price 会返回 None, OK
    return {
        "shop": shop,
        "amazon_asin": amazon_asin if amazon_asin not in HEADER_LIKE_VALUES else None,
        "walmart_sku": walmart_sku if walmart_sku not in HEADER_LIKE_VALUES else (amazon_asin or None),
        "feed_id": feed_id if feed_id not in HEADER_LIKE_VALUES else None,
        "title": raw_title,
        "title_clean": title_clean,
        "product_type": product_type if product_type not in HEADER_LIKE_VALUES else None,
        "price": _parse_price(price_raw),
        "status": status if status not in HEADER_LIKE_VALUES else None,
        "status2": status2 if status2 not in HEADER_LIKE_VALUES else None,
        "reason_raw": reason_raw if reason_raw not in HEADER_LIKE_VALUES else None,
        "reason_category": cls["primary_category"],
        "reason_subcategory": cls["primary_subcategory"],
        "source_sheet_id": source_sheet_id,
        "source_date": source_date,
        "flagged_at": flagged_at,
    }


INSERT_SQL = """
INSERT INTO walmart_suspension_history (
    shop, amazon_asin, walmart_sku, feed_id,
    title, title_clean, product_type, price,
    status, status2, reason_raw, reason_category, reason_subcategory,
    source_sheet_id, source_date, flagged_at
) VALUES %s
ON CONFLICT (walmart_sku, source_date) DO UPDATE SET
    reason_raw = EXCLUDED.reason_raw,
    reason_category = EXCLUDED.reason_category,
    reason_subcategory = EXCLUDED.reason_subcategory,
    status = EXCLUDED.status,
    status2 = EXCLUDED.status2,
    product_type = EXCLUDED.product_type,
    title = COALESCE(EXCLUDED.title, walmart_suspension_history.title),
    title_clean = COALESCE(EXCLUDED.title_clean, walmart_suspension_history.title_clean),
    imported_at = NOW()
"""

COLS_ORDER = [
    "shop", "amazon_asin", "walmart_sku", "feed_id",
    "title", "title_clean", "product_type", "price",
    "status", "status2", "reason_raw", "reason_category", "reason_subcategory",
    "source_sheet_id", "source_date", "flagged_at",
]


def import_daily_sheet(sheet_id, source_date, verbose=True):
    """导入一张日报表到 walmart_suspension_history"""
    if verbose:
        print(f"\n=== 导入 {sheet_id} ({source_date}) ===")

    t0 = time.time()
    rows = read_range(sheet_id, start_row=1, start_col="A", end_col="T",
                      spreadsheet_token=WALMART_SS_TOKEN)
    t_read = time.time() - t0
    if verbose:
        print(f"  飞书读取: {len(rows)} 行, 耗时 {t_read:.1f}s")

    header_col_map = _detect_header(rows)
    data_rows = rows[1:] if header_col_map is not None else rows
    if verbose:
        if header_col_map:
            print(f"  检测到表头, col_map={header_col_map}")
        else:
            print(f"  无表头, 按行动态识别新/老布局")

    parsed = []
    skipped = 0
    for r in data_rows:
        effective_map = header_col_map or _pick_col_map_for_row(r)
        # 行级 sanity check: 若按 effective_map 读出的 status 不是合法状态值, fallback 到行级
        status_idx = next((k for k, v in effective_map.items() if v == "status"), None)
        status_val = (str(r[status_idx]).strip() if status_idx is not None and status_idx < len(r) and r[status_idx] else "")
        if status_val and status_val not in STATUS_VALUES:
            effective_map = _pick_col_map_for_row(r)
        d = _parse_row(r, sheet_id, source_date, effective_map)
        if d is None:
            skipped += 1
            continue
        parsed.append(d)

    # 同一天同一 SKU 的去重 (避免 ON CONFLICT UPSERT 多次)
    dedup = {}
    for d in parsed:
        key = (d["walmart_sku"], d["source_date"])
        # 保留非空原因的那一条
        if key not in dedup or (d["reason_raw"] and not dedup[key]["reason_raw"]):
            dedup[key] = d
    parsed = list(dedup.values())

    if verbose:
        print(f"  解析: {len(parsed)} 有效, {skipped} 跳过 (关键字段缺失)")
        # 分类分布
        cat_stats = {}
        for d in parsed:
            c = d["reason_category"]
            cat_stats[c] = cat_stats.get(c, 0) + 1
        for c, n in sorted(cat_stats.items(), key=lambda x: -x[1]):
            print(f"    {c}: {n}")

    # 批量插入
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    batch_size = 1000
    t_insert = time.time()
    total_inserted = 0
    for i in range(0, len(parsed), batch_size):
        batch = parsed[i:i + batch_size]
        values = [tuple(d[c] for c in COLS_ORDER) for d in batch]
        execute_values(cur, INSERT_SQL, values, page_size=500)
        total_inserted += len(batch)
    conn.commit()
    cur.close()
    conn.close()
    if verbose:
        print(f"  DB 写入: {total_inserted} 行, 耗时 {time.time() - t_insert:.1f}s")
    return total_inserted


def mark_deleted_from_compliance_sheet(verbose=True):
    """从 eGjQRX 监管合规删除 sheet 标记 is_deleted=true"""
    if verbose:
        print(f"\n=== 交叉 eGjQRX 更新 is_deleted ===")
    rows = read_range(SHEET_COMPLIANCE_DELETED, start_row=2, start_col="A", end_col="K",
                      spreadsheet_token=WALMART_SS_TOKEN)
    if verbose:
        print(f"  飞书读取: {len(rows)} 行")

    # 该 sheet 列 B = SKU (实际存的是店铺内部识别, 可能是 Amazon ASIN)
    # 同时交叉 amazon_asin 和 walmart_sku
    ids = set()
    for r in rows:
        if len(r) > 1 and r[1]:
            s = str(r[1]).strip()
            if s:
                ids.add(s)
    if verbose:
        print(f"  唯一 ID: {len(ids)}")

    if not ids:
        return 0

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        UPDATE walmart_suspension_history
        SET is_deleted = TRUE
        WHERE walmart_sku = ANY(%s) OR amazon_asin = ANY(%s)
    """, (list(ids), list(ids)))
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if verbose:
        print(f"  DB 更新: {updated} 行标记 is_deleted=TRUE")
    return updated


def update_product_type_stats():
    """基于 walmart_suspension_history 刷新 walmart_product_types 统计"""
    print("\n=== 更新 walmart_product_types 统计 ===")
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("TRUNCATE walmart_product_types")
    cur.execute("""
        INSERT INTO walmart_product_types (product_type, sample_count, suspend_count, suspend_rate, dominant_reason, is_risky, updated_at)
        SELECT
            product_type,
            COUNT(DISTINCT walmart_sku) AS sample_count,
            COUNT(DISTINCT walmart_sku) FILTER (WHERE status IN ('SYSTEM_PROBLEM', 'UNPUBLISHED')) AS suspend_count,
            ROUND(
                COUNT(DISTINCT walmart_sku) FILTER (WHERE status IN ('SYSTEM_PROBLEM', 'UNPUBLISHED'))::NUMERIC
                / NULLIF(COUNT(DISTINCT walmart_sku), 0),
                4
            ) AS suspend_rate,
            (SELECT reason_category FROM walmart_suspension_history w2
             WHERE w2.product_type = w.product_type
             GROUP BY reason_category
             ORDER BY COUNT(*) DESC LIMIT 1) AS dominant_reason,
            FALSE AS is_risky,
            NOW()
        FROM walmart_suspension_history w
        WHERE product_type IS NOT NULL
        GROUP BY product_type
    """)
    cur.execute("SELECT COUNT(*) FROM walmart_product_types")
    n = cur.fetchone()[0]
    # 标记高风险: 样本≥10 且暂停率>60% (可调)
    cur.execute("""
        UPDATE walmart_product_types
        SET is_risky = TRUE
        WHERE sample_count >= 10 AND suspend_rate > 0.60
    """)
    risky = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"  ProductType 条目: {n}")
    print(f"  高风险标记: {risky}")
    return n


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sheet", help="只导入指定 sheet_id")
    p.add_argument("--date", help="对应的 source_date (yyyy-mm-dd), 与 --sheet 配合")
    p.add_argument("--mark-deleted", action="store_true", help="仅交叉 eGjQRX 更新 is_deleted")
    p.add_argument("--no-stats", action="store_true", help="跳过 ProductType 统计刷新")
    args = p.parse_args()

    if args.mark_deleted:
        mark_deleted_from_compliance_sheet()
        if not args.no_stats:
            update_product_type_stats()
        return

    if args.sheet:
        date = args.date or DAILY_SHEETS.get(args.sheet, (None,))[0]
        if not date:
            print(f"未知 sheet_id {args.sheet}, 请用 --date 指定日期")
            sys.exit(1)
        import_daily_sheet(args.sheet, date)
    else:
        total = 0
        for sid, (date, title) in DAILY_SHEETS.items():
            total += import_daily_sheet(sid, date)
        print(f"\n=== 合计导入 {total} 行 ===")

    mark_deleted_from_compliance_sheet()
    if not args.no_stats:
        update_product_type_stats()


if __name__ == "__main__":
    main()
