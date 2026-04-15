#!/usr/bin/env python3
"""
USPTO 商标数据每日增量更新
1. 检查 USPTO 最新每日增量文件
2. 下载缺失的文件
3. 导入 PostgreSQL
4. 验证数据完整性
"""

import os
import sys
import glob
import time
import zipfile
import logging
import requests
import psycopg2
from datetime import datetime, timedelta
from pathlib import Path

# 导入 ETL 模块
sys.path.insert(0, os.path.dirname(__file__))
import etl_trademarks as etl

# ─── 配置 ───
DAILY_DIR = Path(__file__).parent / "raw" / "trademarks" / "daily"
DAILY_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = "https://data.uspto.gov/ui/datasets/products/files/TRTDXFAP/"
LOG_FILE = Path(__file__).parent / "daily_update.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("daily_update")


def get_existing_daily_files():
    """获取已下载的每日增量文件名"""
    return set(f.name for f in DAILY_DIR.glob("apc*.zip"))


def get_db_latest_date(conn):
    """获取数据库中最新的 filing_date"""
    cur = conn.cursor()
    cur.execute("SELECT MAX(filing_date) FROM trademarks")
    row = cur.fetchone()
    cur.close()
    return row[0] if row and row[0] else None


def generate_daily_filenames(start_date, end_date):
    """生成日期范围内的每日文件名"""
    files = []
    d = start_date
    while d <= end_date:
        yy = d.strftime("%y")
        mm = d.strftime("%m")
        dd = d.strftime("%d")
        files.append(f"apc{yy}{mm}{dd}.zip")
        d += timedelta(days=1)
    return files


def download_file(session, filename):
    """下载单个文件"""
    dest = DAILY_DIR / filename
    if dest.exists() and dest.stat().st_size > 1000:
        return True  # 已存在

    url = BASE_URL + filename
    try:
        resp = session.get(url, stream=True, timeout=120, allow_redirects=True)
        if resp.status_code == 404:
            return None  # 文件不存在（周末/假日无数据）
        resp.raise_for_status()

        tmp = dest.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)

        # 验证是 zip 文件（非 HTML 错误页）
        import zipfile as zf
        if not zf.is_zipfile(str(tmp)):
            tmp.unlink()
            log.warning(f"  跳过: {filename}（非 zip 文件，可能尚未发布）")
            return None

        tmp.rename(dest)
        log.info(f"  下载完成: {filename} ({dest.stat().st_size / 1024 / 1024:.1f} MB)")
        return True

    except Exception as e:
        log.error(f"  下载失败: {filename}: {e}")
        return False


def download_new_files(conn):
    """下载缺失的每日增量文件"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://data.uspto.gov/bulkdata/datasets/TRTDXFAP",
    })

    existing = get_existing_daily_files()

    # 从 2026-03-05 开始（全量数据覆盖到 2026-03-04）
    start = datetime(2026, 3, 5)
    end = datetime.now() - timedelta(days=1)  # 昨天（今天的数据可能还没发布）

    candidates = generate_daily_filenames(start, end)
    to_download = [f for f in candidates if f not in existing]

    if not to_download:
        log.info("没有新文件需要下载")
        return []

    log.info(f"需要下载 {len(to_download)} 个新文件")
    downloaded = []
    for f in to_download:
        result = download_file(session, f)
        if result is True:
            downloaded.append(f)
        elif result is None:
            pass  # 文件不存在，跳过
        time.sleep(1)

    return downloaded


def import_new_files(conn):
    """导入未处理的增量文件"""
    all_zips = sorted(DAILY_DIR.glob("apc*.zip"))

    cur = conn.cursor()
    cur.execute("SELECT source_file FROM etl_progress WHERE data_type='trademark' AND status='completed'")
    completed = set(row[0] for row in cur.fetchall())
    cur.close()

    to_import = [z for z in all_zips if z.name not in completed]

    if not to_import:
        log.info("没有新文件需要导入")
        return 0

    log.info(f"需要导入 {len(to_import)} 个文件")
    imported = 0
    for zp in to_import:
        try:
            etl.process_zip(conn, str(zp))
            imported += 1
        except Exception as e:
            log.error(f"导入失败 {zp.name}: {e}")

    return imported


def validate_data(conn):
    """验证数据完整性"""
    cur = conn.cursor()
    checks = []

    # 1. 总记录数
    cur.execute("SELECT COUNT(*) FROM trademarks")
    total = cur.fetchone()[0]
    checks.append(f"总记录数: {total:,}")

    # 2. 有品牌名的比例
    cur.execute("SELECT COUNT(mark_identification) FROM trademarks")
    with_name = cur.fetchone()[0]
    pct = round(with_name / total * 100, 1) if total > 0 else 0
    checks.append(f"有品牌名: {with_name:,} ({pct}%)")

    # 3. 最新日期
    cur.execute("SELECT MAX(filing_date) FROM trademarks")
    latest = cur.fetchone()[0]
    checks.append(f"最新 filing_date: {latest}")

    # 4. 孤儿记录检查
    orphan_ok = True
    for tbl in ['trademark_classes', 'trademark_owners', 'trademark_statements']:
        cur.execute(f"SELECT COUNT(*) FROM {tbl} c WHERE NOT EXISTS (SELECT 1 FROM trademarks t WHERE t.serial_number = c.serial_number)")
        orphans = cur.fetchone()[0]
        if orphans > 0:
            checks.append(f"⚠ {tbl} 有 {orphans} 条孤儿记录")
            orphan_ok = False
    if orphan_ok:
        checks.append("孤儿记录检查: 通过")

    # 5. ETL 错误检查
    cur.execute("SELECT SUM(records_errored) FROM etl_progress WHERE data_type='trademark'")
    errors = cur.fetchone()[0] or 0
    checks.append(f"ETL 总错误: {errors}")

    # 6. 数据库大小
    cur.execute("SELECT pg_size_pretty(pg_database_size('uspto'))")
    size = cur.fetchone()[0]
    checks.append(f"数据库大小: {size}")

    # 7. 模糊匹配测试
    cur.execute("SELECT COUNT(*) FROM trademarks WHERE mark_identification % 'NIKE'")
    nike_matches = cur.fetchone()[0]
    checks.append(f"NIKE 模糊匹配: {nike_matches} 条")

    cur.close()

    ok = errors == 0 and orphan_ok and total > 13000000 and nike_matches > 0
    return ok, checks


def main():
    log.info("=" * 50)
    log.info("USPTO 商标数据每日增量更新")
    log.info("=" * 50)

    conn = psycopg2.connect(**etl.DB_CONFIG)
    conn.autocommit = False

    try:
        # Step 1: 下载
        log.info("\n[Step 1] 下载新增量文件")
        downloaded = download_new_files(conn)
        log.info(f"下载完成: {len(downloaded)} 个新文件")

        # Step 2: 导入
        log.info("\n[Step 2] 导入到 PostgreSQL")
        imported = import_new_files(conn)
        log.info(f"导入完成: {imported} 个文件")

        # Step 3: 验证
        log.info("\n[Step 3] 数据完整性验证")
        ok, checks = validate_data(conn)
        for c in checks:
            log.info(f"  {c}")

        if ok:
            log.info("\n✓ 所有检查通过")
        else:
            log.warning("\n⚠ 部分检查未通过，请人工确认")

    except Exception as e:
        log.error(f"更新失败: {e}")
    finally:
        conn.close()

    log.info("更新流程结束\n")


if __name__ == "__main__":
    main()
