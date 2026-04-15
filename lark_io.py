"""
飞书电子表格读写封装

读写策略:
- 读取: 用 SDK + bot 身份 (sheets:spreadsheet:read 已开通)
- 写入: 通过 lark-cli subprocess + user 身份 (复用本地已认证的 user_access_token)
       数据通过 stdin 传递避免命令行参数过长

API 限制:
- 单次最多 5000 行 × 100 列, 总单元格 50000
- 单元格最大 50000 字符
"""
import json
import os
import subprocess
import time
from typing import Iterable, List, Optional

import lark_oapi as lark

from lark_config import SPREADSHEET_TOKEN, get_client


# 单次读写的最大行数 (留余量防止超限)
MAX_ROWS_PER_REQUEST = 4000
MAX_CELLS_PER_REQUEST = 40000  # 实际限制 50000, 留余量


def _col_letter(n: int) -> str:
    """1->A, 2->B, ..., 27->AA"""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _flatten_cell(cell):
    """把飞书单元格的复杂类型 (链接对象/null) 转为字符串。"""
    if cell is None:
        return ""
    if isinstance(cell, list):
        # 链接/at 等富文本
        parts = []
        for item in cell:
            if isinstance(item, dict):
                if "text" in item:
                    parts.append(item["text"])
                elif "link" in item:
                    parts.append(item["link"])
            else:
                parts.append(str(item))
        return "".join(parts)
    if isinstance(cell, dict):
        return cell.get("text") or cell.get("link") or json.dumps(cell, ensure_ascii=False)
    return str(cell)


def read_range(sheet_id: str, start_row: int = 1, end_row: Optional[int] = None,
               start_col: str = "A", end_col: str = "T",
               spreadsheet_token: str = SPREADSHEET_TOKEN) -> List[List[str]]:
    """读取一段区域，自动分批处理超大表。

    Args:
        sheet_id: sheet 的 id (不是 title)
        start_row: 起始行 (1-based, 包含)
        end_row: 结束行 (1-based, 包含). None = 读取到末尾 (会先查行数)
        start_col, end_col: 列字母
    Returns:
        二维列表 (每行是字符串列表)
    """
    client = get_client()

    if end_row is None:
        # 查询 sheet 元信息获取行数
        end_row = _get_sheet_row_count(sheet_id, spreadsheet_token)

    if end_row < start_row:
        return []

    all_rows = []
    n_cols = _col_index(end_col) - _col_index(start_col) + 1
    rows_per_batch = max(1, MAX_CELLS_PER_REQUEST // max(n_cols, 1))
    rows_per_batch = min(rows_per_batch, MAX_ROWS_PER_REQUEST)

    cursor = start_row
    while cursor <= end_row:
        batch_end = min(cursor + rows_per_batch - 1, end_row)
        rng = f"{sheet_id}!{start_col}{cursor}:{end_col}{batch_end}"
        batch = _read_one_range(client, spreadsheet_token, rng)
        all_rows.extend(batch)
        cursor = batch_end + 1
    return all_rows


def _col_index(letter: str) -> int:
    """A->1, B->2, ..., AA->27"""
    n = 0
    for ch in letter.upper():
        n = n * 26 + (ord(ch) - 64)
    return n


def _build_request(method, uri, body=None, queries=None):
    """构造 BaseRequest 对象 (使用 tenant_access_token)"""
    builder = (
        lark.BaseRequest.builder()
        .http_method(method)
        .uri(uri)
        .token_types({lark.AccessTokenType.TENANT})
    )
    if body is not None:
        builder = builder.body(body)
    req = builder.build()
    if queries:
        for k, v in queries:
            req.add_query(k, v)
    return req


def _do_request(client, request):
    """执行请求并解析 JSON, 失败抛错"""
    resp = client.request(request)
    if resp.raw is None or resp.raw.content is None:
        raise RuntimeError(f"请求无响应: {resp.code} {resp.msg}")
    body = json.loads(resp.raw.content)
    if body.get("code") != 0:
        raise RuntimeError(f"API 错误 [{body.get('code')}]: {body.get('msg')}")
    return body


def _get_sheet_row_count(sheet_id: str, spreadsheet_token: str) -> int:
    """查询 sheet 总行数"""
    client = get_client()
    req = _build_request(
        lark.HttpMethod.GET,
        f"/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query",
    )
    body = _do_request(client, req)
    for s in body.get("data", {}).get("sheets", []):
        if s.get("sheet_id") == sheet_id:
            return s.get("grid_properties", {}).get("row_count", 0)
    raise ValueError(f"未找到 sheet_id={sheet_id}")


def _read_one_range(client, spreadsheet_token: str, range_str: str) -> List[List[str]]:
    """单次读取"""
    req = _build_request(
        lark.HttpMethod.GET,
        f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}",
        queries=[("valueRenderOption", "ToString")],
    )
    body = _do_request(client, req)
    values = body.get("data", {}).get("valueRange", {}).get("values", []) or []
    return [[_flatten_cell(c) for c in row] for row in values]


def write_range(sheet_id: str, start_row: int, values: List[List],
                start_col: str = "A",
                spreadsheet_token: str = SPREADSHEET_TOKEN) -> int:
    """写入数据到指定起始位置，自动分批。

    Args:
        sheet_id: sheet 的 id
        start_row: 起始行 (1-based)
        values: 二维数据 (每行是单元格列表)
        start_col: 起始列字母
    Returns:
        写入的总行数
    """
    if not values:
        return 0
    client = get_client()

    n_cols = max(len(row) for row in values)
    end_col = _col_letter(_col_index(start_col) + n_cols - 1)

    rows_per_batch = max(1, MAX_CELLS_PER_REQUEST // max(n_cols, 1))
    rows_per_batch = min(rows_per_batch, MAX_ROWS_PER_REQUEST)

    total = 0
    for i in range(0, len(values), rows_per_batch):
        batch = values[i:i + rows_per_batch]
        row_start = start_row + i
        row_end = row_start + len(batch) - 1
        rng = f"{sheet_id}!{start_col}{row_start}:{end_col}{row_end}"
        _write_one_range(client, spreadsheet_token, rng, batch)
        total += len(batch)
    return total


def _write_one_range(client, spreadsheet_token: str, range_str: str, values: List[List]):
    """单次写入: 通过 lark-cli subprocess + stdin 使用 user 身份"""
    payload = {
        "valueRange": {
            "range": range_str,
            "values": values,
        }
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    cmd = [
        "lark-cli", "api", "PUT",
        f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values",
        "--data", "-",
        "--as", "user",
        "--format", "json",
    ]
    env = os.environ.copy()
    env["LARK_CLI_NO_PROXY"] = "1"  # 避免代理警告
    proc = subprocess.run(
        cmd, input=payload_json, capture_output=True,
        text=True, encoding="utf-8", env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"lark-cli 写入失败 [{range_str}]: {proc.stderr or proc.stdout}")
    try:
        body = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"lark-cli 返回非 JSON [{range_str}]: {proc.stdout[:500]}")
    if body.get("code") != 0:
        raise RuntimeError(f"飞书 API 错误 [{range_str}]: [{body.get('code')}] {body.get('msg')}")


def ensure_rows(sheet_id: str, required_rows: int,
                spreadsheet_token: str = SPREADSHEET_TOKEN):
    """确保 sheet 至少有 required_rows 行，不足则追加 (写操作: 走 lark-cli)"""
    current = _get_sheet_row_count(sheet_id, spreadsheet_token)
    if current >= required_rows:
        return current
    delta = required_rows - current
    payload = {
        "dimension": {
            "sheetId": sheet_id,
            "majorDimension": "ROWS",
            "length": delta,
        }
    }
    payload_json = json.dumps(payload, ensure_ascii=False)
    cmd = [
        "lark-cli", "api", "POST",
        f"/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range",
        "--data", "-",
        "--as", "user",
        "--format", "json",
    ]
    env = os.environ.copy()
    env["LARK_CLI_NO_PROXY"] = "1"
    proc = subprocess.run(
        cmd, input=payload_json, capture_output=True,
        text=True, encoding="utf-8", env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"扩展行数失败: {proc.stderr or proc.stdout}")
    body = json.loads(proc.stdout)
    if body.get("code") != 0:
        raise RuntimeError(f"扩展行数 API 错误: [{body.get('code')}] {body.get('msg')}")
    return required_rows


def clear_sheet_data(sheet_id: str, start_row: int = 2, end_col: str = "T",
                     spreadsheet_token: str = SPREADSHEET_TOKEN):
    """清空数据行 (保留第一行表头)"""
    client = get_client()
    total_rows = _get_sheet_row_count(sheet_id, spreadsheet_token)
    if total_rows < start_row:
        return 0
    # 分批清空
    rows_per_batch = MAX_ROWS_PER_REQUEST
    cleared = 0
    cursor = start_row
    n_cols = _col_index(end_col)
    while cursor <= total_rows:
        batch_end = min(cursor + rows_per_batch - 1, total_rows)
        empty_rows = [[""] * n_cols for _ in range(batch_end - cursor + 1)]
        rng = f"{sheet_id}!A{cursor}:{end_col}{batch_end}"
        _write_one_range(client, spreadsheet_token, rng, empty_rows)
        cleared += len(empty_rows)
        cursor = batch_end + 1
    return cleared


if __name__ == "__main__":
    # 烟雾测试: 读取 Tro案件 sheet 前 3 行
    from lark_config import SHEET_IDS
    rows = read_range(SHEET_IDS["tro_cases"], start_row=1, end_row=3)
    print(f"读取 {len(rows)} 行")
    for i, row in enumerate(rows):
        print(f"  Row {i+1}: {row[:5]}...")
