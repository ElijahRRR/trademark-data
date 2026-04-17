"""
把 product_audits + audit_flags + products_stage 的审核结果推送到飞书

目标 spreadsheet: DYZZsDNeShUxHitxGd9cL14AnSc (沃尔玛合规审核结果)
  sheet 0: 可上架池     (approve)
  sheet 1: 已拒绝       (reject)
  sheet 2: 待人工复审   (hold_manual)
  sheet 3: 本期报表     (统计指标)

首次运行自动初始化 sheet 结构 (重命名 Sheet1 + 追加 3 sheet + 写表头).
"""
import argparse
import json
import subprocess
import time

import psycopg2

from lark_config import get_client
from lark_io import (
    _build_request,
    _do_request,
    clear_sheet_data,
    ensure_rows,
    write_range,
)
import lark_oapi as lark

DB_CONN = "dbname=uspto user=nextderboy"
AUDIT_SS_TOKEN = "DYZZsDNeShUxHitxGd9cL14AnSc"

SHEET_TITLES = {
    "approve_pool":     "可上架池",
    "rejected":         "已拒绝",
    "hold_manual":      "待人工复审",
    "report":           "本期报表",
}

HEADERS = {
    "approve_pool": [
        "ASIN", "标题", "品牌", "类目路径", "价格", "畅销排名", "原产国",
        "UPC", "图片链接", "审核时间"
    ],
    "rejected": [
        "ASIN", "标题", "品牌", "类目路径", "价格", "拒绝原因汇总",
        "IP风险", "Offensive风险", "Regulatory风险", "触发规则数", "主要触发规则",
        "审核时间"
    ],
    "hold_manual": [
        "ASIN", "标题", "品牌", "类目路径", "价格", "复审建议",
        "IP风险", "Offensive风险", "Regulatory风险", "总风险",
        "触发规则数", "主要触发规则", "审核时间"
    ],
    "report": [
        "批次文件", "审核时间", "总产品数", "approve", "hold_manual", "reject",
        "approve率", "reject率", "Top拒绝原因Top3"
    ],
}


# ==========================================================================
# 初始化 spreadsheet 结构
# ==========================================================================

def _batch_update_sheets(requests: list):
    """调用 /sheets/v2/spreadsheets/<token>/sheets_batch_update"""
    payload = {"requests": requests}
    payload_json = json.dumps(payload, ensure_ascii=False)
    cmd = [
        "lark-cli", "api", "POST",
        f"/open-apis/sheets/v2/spreadsheets/{AUDIT_SS_TOKEN}/sheets_batch_update",
        "--data", "-",
        "--as", "user",
        "--format", "json",
    ]
    import os
    env = os.environ.copy()
    env["LARK_CLI_NO_PROXY"] = "1"
    proc = subprocess.run(cmd, input=payload_json, capture_output=True,
                          text=True, encoding="utf-8", env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli 失败: {proc.stderr or proc.stdout}")
    body = json.loads(proc.stdout)
    if body.get("code") != 0:
        raise RuntimeError(f"飞书 API 错误: [{body.get('code')}] {body.get('msg')}")
    return body


def _list_sheets():
    """返回 {title: sheet_id}"""
    client = get_client()
    req = _build_request(
        lark.HttpMethod.GET,
        f"/open-apis/sheets/v3/spreadsheets/{AUDIT_SS_TOKEN}/sheets/query",
    )
    body = _do_request(client, req)
    sheets = body.get("data", {}).get("sheets", [])
    return {s["title"]: s["sheet_id"] for s in sheets}


def ensure_sheet_structure():
    """首次运行: 重命名 Sheet1 + 追加 3 sheet + 写表头"""
    title_to_id = _list_sheets()
    existing_titles = set(title_to_id.keys())

    # 需要确保存在的 4 个 sheet 标题
    want_titles = list(SHEET_TITLES.values())

    # 如果第一个目标已存在, 跳过重命名; 否则把 Sheet1 重命名为第一个
    requests = []

    if "Sheet1" in title_to_id and "可上架池" not in title_to_id:
        requests.append({
            "updateSheet": {
                "properties": {
                    "sheetId": title_to_id["Sheet1"],
                    "title": "可上架池",
                }
            }
        })
        existing_titles.discard("Sheet1")
        existing_titles.add("可上架池")

    # 追加缺失的 sheet
    index_base = len(title_to_id)
    for i, title in enumerate(want_titles):
        if title in existing_titles:
            continue
        requests.append({
            "addSheet": {
                "properties": {
                    "title": title,
                    "index": index_base + i,
                }
            }
        })

    if requests:
        print(f"  结构调整: {len(requests)} 个请求")
        _batch_update_sheets(requests)
        # 重新查询
        title_to_id = _list_sheets()

    # 写表头 (若 row1 为空)
    for key, title in SHEET_TITLES.items():
        sheet_id = title_to_id.get(title)
        if not sheet_id:
            print(f"  [WARN] 未找到 sheet {title}")
            continue
        headers = HEADERS[key]
        # 写入第 1 行作为表头
        write_range(sheet_id, start_row=1, values=[headers],
                    spreadsheet_token=AUDIT_SS_TOKEN)
        print(f"  [{title}] 表头写入 {len(headers)} 列")

    return title_to_id


# ==========================================================================
# 查询数据
# ==========================================================================

def _rows_for_approve(conn, batch_file=None):
    cur = conn.cursor()
    where = "WHERE pa.verdict = 'approve'"
    args = []
    if batch_file:
        where += " AND pa.batch_file = %s"
        args.append(batch_file)
    cur.execute(f"""
        SELECT pa.asin, ps.title, ps.brand, ps.category_path, ps.price, ps.bsr,
               ps.origin_country, ps.upc, ps.image_urls,
               to_char(pa.audited_at, 'YYYY-MM-DD HH24:MI')
        FROM product_audits pa JOIN products_stage ps ON ps.id = pa.stage_id
        {where}
        ORDER BY pa.asin
    """, args)
    rows = cur.fetchall()
    cur.close()
    return [list(r) for r in rows]


def _rows_for_rejected(conn, batch_file=None):
    cur = conn.cursor()
    where = "WHERE pa.verdict = 'reject'"
    args = []
    if batch_file:
        where += " AND pa.batch_file = %s"
        args.append(batch_file)
    cur.execute(f"""
        SELECT pa.asin, ps.title, ps.brand, ps.category_path, ps.price,
               pa.reason_summary,
               pa.ip_risk, pa.offensive_risk, pa.regulatory_risk,
               (SELECT COUNT(*) FROM audit_flags f WHERE f.audit_id = pa.id) flag_cnt,
               (SELECT STRING_AGG(flag_code, '; ') FROM (
                   SELECT flag_code FROM audit_flags f
                   WHERE f.audit_id = pa.id AND f.severity = 'hard_block'
                   LIMIT 5
               ) t) top_rules,
               to_char(pa.audited_at, 'YYYY-MM-DD HH24:MI')
        FROM product_audits pa JOIN products_stage ps ON ps.id = pa.stage_id
        {where}
        ORDER BY pa.overall_risk DESC, pa.asin
    """, args)
    rows = cur.fetchall()
    cur.close()
    return [list(r) for r in rows]


def _rows_for_hold(conn, batch_file=None):
    cur = conn.cursor()
    where = "WHERE pa.verdict = 'hold_manual'"
    args = []
    if batch_file:
        where += " AND pa.batch_file = %s"
        args.append(batch_file)
    cur.execute(f"""
        SELECT pa.asin, ps.title, ps.brand, ps.category_path, ps.price,
               CASE WHEN pa.overall_risk >= 60 THEN '建议拒绝'
                    WHEN pa.overall_risk >= 30 THEN '需 LLM 二审'
                    ELSE '可放行 (低风险)' END,
               pa.ip_risk, pa.offensive_risk, pa.regulatory_risk, pa.overall_risk,
               (SELECT COUNT(*) FROM audit_flags f WHERE f.audit_id = pa.id) flag_cnt,
               (SELECT STRING_AGG(flag_code, '; ') FROM (
                   SELECT flag_code FROM audit_flags f
                   WHERE f.audit_id = pa.id ORDER BY CASE f.severity
                       WHEN 'hard_block' THEN 1 WHEN 'warn' THEN 2 ELSE 3 END
                   LIMIT 5
               ) t) top_rules,
               to_char(pa.audited_at, 'YYYY-MM-DD HH24:MI')
        FROM product_audits pa JOIN products_stage ps ON ps.id = pa.stage_id
        {where}
        ORDER BY pa.overall_risk DESC, pa.asin
    """, args)
    rows = cur.fetchall()
    cur.close()
    return [list(r) for r in rows]


def _rows_for_report(conn, batch_file=None):
    cur = conn.cursor()
    where = ""
    args = []
    if batch_file:
        where = "WHERE pa.batch_file = %s"
        args.append(batch_file)
    cur.execute(f"""
        SELECT pa.batch_file,
               to_char(MAX(pa.audited_at), 'YYYY-MM-DD HH24:MI') audit_time,
               COUNT(*) total,
               SUM(CASE WHEN pa.verdict='approve' THEN 1 ELSE 0 END) apr,
               SUM(CASE WHEN pa.verdict='hold_manual' THEN 1 ELSE 0 END) hold,
               SUM(CASE WHEN pa.verdict='reject' THEN 1 ELSE 0 END) rej
        FROM product_audits pa {where}
        GROUP BY pa.batch_file
        ORDER BY audit_time DESC
    """, args)
    rows = cur.fetchall()

    # top 3 拒绝原因
    top_reason_data = {}
    for r in rows:
        bf = r[0]
        cur.execute("""
            SELECT flag_code, COUNT(*) c FROM audit_flags f
            JOIN product_audits pa ON pa.id = f.audit_id
            WHERE f.severity = 'hard_block' AND pa.batch_file = %s
            GROUP BY flag_code ORDER BY c DESC LIMIT 3
        """, (bf,))
        top_reason_data[bf] = "; ".join(f"{fc}:{c}" for fc, c in cur.fetchall())

    cur.close()
    out = []
    for r in rows:
        batch_file_, audit_time, total, apr, hold, rej = r
        apr_pct = f"{100*apr/total:.1f}%" if total else "0%"
        rej_pct = f"{100*rej/total:.1f}%" if total else "0%"
        out.append([
            batch_file_, audit_time, total, apr, hold, rej,
            apr_pct, rej_pct,
            top_reason_data.get(batch_file_, ""),
        ])
    return out


# ==========================================================================
# 推送
# ==========================================================================

def _push(sheet_id: str, data, title=""):
    if not data:
        print(f"  [{title}] 无数据")
        return 0
    # 扩容
    ensure_rows(sheet_id, len(data) + 1, spreadsheet_token=AUDIT_SS_TOKEN)
    # 清空旧数据 (保留表头)
    clear_sheet_data(sheet_id, start_row=2, end_col="M",
                     spreadsheet_token=AUDIT_SS_TOKEN)
    # 写入
    # 把 None → "" 和 Decimal → str
    from decimal import Decimal
    clean = [[("" if c is None else (str(c) if isinstance(c, Decimal) else c))
              for c in row] for row in data]
    written = write_range(sheet_id, start_row=2, values=clean,
                          spreadsheet_token=AUDIT_SS_TOKEN)
    print(f"  [{title}] 写入 {written} 行")
    return written


def upload_all(batch_file=None):
    print("=" * 60)
    print("飞书推送开始")
    print("=" * 60)
    print("\n=== 1. 确保 sheet 结构 ===")
    title_to_id = ensure_sheet_structure()

    conn = psycopg2.connect(DB_CONN)
    try:
        print("\n=== 2. 推送可上架池 ===")
        data = _rows_for_approve(conn, batch_file)
        _push(title_to_id[SHEET_TITLES["approve_pool"]], data, "可上架池")

        print("\n=== 3. 推送已拒绝 ===")
        data = _rows_for_rejected(conn, batch_file)
        _push(title_to_id[SHEET_TITLES["rejected"]], data, "已拒绝")

        print("\n=== 4. 推送待人工复审 ===")
        data = _rows_for_hold(conn, batch_file)
        _push(title_to_id[SHEET_TITLES["hold_manual"]], data, "待人工复审")

        print("\n=== 5. 推送本期报表 ===")
        data = _rows_for_report(conn, batch_file)
        _push(title_to_id[SHEET_TITLES["report"]], data, "本期报表")
    finally:
        conn.close()

    print("\n" + "=" * 60)
    print(f"URL: https://my.feishu.cn/sheets/{AUDIT_SS_TOKEN}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--batch", help="只推指定 batch_file (默认推全部)")
    p.add_argument("--init-only", action="store_true", help="仅初始化结构不推数据")
    args = p.parse_args()

    if args.init_only:
        ensure_sheet_structure()
        return

    upload_all(batch_file=args.batch)


if __name__ == "__main__":
    main()
