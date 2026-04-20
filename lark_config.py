"""
飞书集成配置模块
- 从 ~/.lark-cli/config.json 读取 appId / appSecret
- 提供 get_client() 返回已初始化的 lark Client
- 维护飞书表格的常量定义
"""
import json
import os
from pathlib import Path

import lark_oapi as lark

# ====== 飞书表格常量 ======
SPREADSHEET_TOKEN = "ZkL0sFqKMhNO1vtq3t1cn8X7nhg"
SPREADSHEET_TITLE = "TRO案件及商标黑名单"

SHEET_IDS = {
    "tro_brands": "sdO3YJ",       # TRO品牌库 (公司-品牌对照, 来自 company_brand_details)
    "other_collected": "gTrLP3",   # 其他收集 (沃尔玛合规 / 历史集成等外部来源)
    "merged_blacklist": "jF8dOw",  # 黑名单品牌 (TRO品牌库 + 其他收集 的去重合并)
    "tro_cases": "34f9f3",         # Tro案件 (源数据)
    "company_overview": "ym27aR",  # 公司概览 (输出)
    "brand_details": "6IpYri",     # 品牌明细 (输出)
    "not_found": "wynwtK",         # 未找到清单 (输出)
}

# Tro案件 sheet 列定义 (A=0)
TRO_COLUMNS = [
    "date_filed",      # A
    "case_number",     # B
    "case_name",       # C
    "nature_of_suit",  # D
    "plaintiff",       # E
    "plaintiff_cn",    # F
    "brand",           # G
    "brand_title",     # H
    "law_firms_abbr",  # I
    "law_firms",       # J
    "lawyer",          # K
    "description",     # L
    "court",           # M
    "judge",           # N
    "cause",           # O
    "date_hit",        # P
    "state",           # Q
    "url",             # R
    "source",          # S
    "created_at",      # T
]


def _load_lark_cli_config():
    """读取应用凭证。
    优先级:
      1. 环境变量 LARK_APP_ID / LARK_APP_SECRET
      2. 项目目录下的 .lark_secret 文件 (两行: appId / appSecret)
    """
    env_id = os.environ.get("LARK_APP_ID")
    env_secret = os.environ.get("LARK_APP_SECRET")
    if env_id and env_secret:
        return env_id, env_secret

    secret_file = Path(__file__).parent / ".lark_secret"
    if secret_file.exists():
        lines = secret_file.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) >= 2:
            return lines[0].strip(), lines[1].strip()

    raise FileNotFoundError(
        "未找到飞书凭证: 请设置 LARK_APP_ID / LARK_APP_SECRET 环境变量, "
        "或在项目根目录创建 .lark_secret 文件 (第一行 appId, 第二行 appSecret)"
    )


_client = None


def get_client():
    """获取已初始化的 lark Client (单例)"""
    global _client
    if _client is None:
        app_id, app_secret = _load_lark_cli_config()
        _client = (
            lark.Client.builder()
            .app_id(app_id)
            .app_secret(app_secret)
            .log_level(lark.LogLevel.WARNING)
            .build()
        )
    return _client


if __name__ == "__main__":
    # 测试: 打印配置摘要 (不暴露 secret)
    app_id, app_secret = _load_lark_cli_config()
    print(f"App ID: {app_id}")
    print(f"App Secret: {'*' * len(app_secret)} ({len(app_secret)} chars)")
    print(f"Spreadsheet: {SPREADSHEET_TITLE} ({SPREADSHEET_TOKEN})")
    print(f"Sheets: {SHEET_IDS}")
    client = get_client()
    print(f"Client initialized: {client.__class__.__name__}")
