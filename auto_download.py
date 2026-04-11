#!/usr/bin/env python3
"""
PTGRDT 并发自动下载+处理脚本

每个 worker 独立 Playwright 浏览器实例，独立代理，并行下载+处理。
文件级锁防止多 worker 下载同一文件。

用法：
  python3 auto_download.py                    # 默认 1 worker
  python3 auto_download.py --workers 3        # 3 worker 并发
  python3 auto_download.py --status           # 查看进度
  python3 auto_download.py --retry-errors     # 重试失败文件
"""

import os
import sys
import json
import time
import random
import logging
import argparse
import signal
import atexit
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from captcha_solver import parse_captcha_grid, read_captcha_js, submit_captcha_js, CLOSE_DIALOG_JS
from etl_patent_grants import process_tar, get_processed_tars, get_failed_tars, get_patent_stats

# ─── 配置 ───
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
PAGE_URL = "https://data.uspto.gov/bulkdata/datasets/ptgrdt?fileDataFromDate=2002-01-01&fileDataToDate=2026-12-31"
MAX_CAPTCHA_RETRIES = 5

LOG_FILE = os.path.join(PROJECT_DIR, "auto_download.log")
_fh = logging.FileHandler(LOG_FILE)
_sh = logging.StreamHandler()
_fmt = logging.Formatter("%(asctime)s [DL] %(message)s")
_fh.setFormatter(_fmt)
_sh.setFormatter(_fmt)
log = logging.getLogger("auto_dl")
log.setLevel(logging.INFO)
log.addHandler(_fh)
log.addHandler(_sh)


class _FlushHandler(logging.Handler):
    def __init__(self, target):
        super().__init__()
        self.target = target

    def emit(self, record):
        self.target.flush()


log.addHandler(_FlushHandler(_fh.stream))
log.propagate = False

# 禁止 captcha_solver 和 pipeline 的 root logger 输出到终端
logging.getLogger().handlers = [logging.NullHandler()]

# 全局浏览器列表，用于清理
_browsers = []
_playwrights = []
_lock = threading.Lock()

# 文件级锁：防止多 worker 下载同一文件
_claimed = set()
_claim_lock = threading.Lock()

# 本次 session 下载失败计数，失败 >= 2 次则跳过，下次启动重试
_fail_count = {}
_fail_lock = threading.Lock()
MAX_DOWNLOAD_RETRIES = 2

# 停止标志
_stop = False


def _cleanup():
    global _browsers, _playwrights
    for b in _browsers:
        try:
            b.close()
        except Exception:
            pass
    _browsers.clear()
    for p in _playwrights:
        try:
            p.stop()
        except Exception:
            pass
    _playwrights.clear()


atexit.register(_cleanup)


def _signal_handler(signum, frame):
    global _stop
    log.info(f"收到信号 {signum}，停止所有 worker...")
    _stop = True
    _cleanup()
    sys.exit(0)


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# ─── 进度查询 ───

def get_processed_files():
    """查询数据库获取已完成的 tar 文件名"""
    return get_processed_tars()


def get_error_files():
    """查询数据库获取处理失败的 tar 文件"""
    return [f for f, _ in get_failed_tars()]


def remove_from_processed(filename):
    """从 etl_progress 中删除记录以允许重试"""
    import psycopg2
    from etl_patent_grants import DB_CONFIG
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM etl_progress WHERE data_type='patent' AND source_file=%s",
        (filename,)
    )
    conn.commit()
    cur.close()
    conn.close()
    log.info(f"已从 etl_progress 移除: {filename}")


def claim_file(filename):
    """原子性声明文件，防止多 worker 下载同一文件"""
    with _claim_lock:
        if filename in _claimed:
            return False
        _claimed.add(filename)
        return True


def release_file(filename):
    with _claim_lock:
        _claimed.discard(filename)


def record_fail(filename):
    """记录下载失败，返回累计失败次数"""
    with _fail_lock:
        _fail_count[filename] = _fail_count.get(filename, 0) + 1
        return _fail_count[filename]


def is_skipped(filename):
    """本次 session 是否已跳过（失败 >= MAX_DOWNLOAD_RETRIES 次）"""
    with _fail_lock:
        return _fail_count.get(filename, 0) >= MAX_DOWNLOAD_RETRIES


# ─── Playwright 操作 ───

def create_browser(pw):
    """创建 Playwright 浏览器实例"""
    browser = pw.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled", "--disable-popup-blocking"],
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        accept_downloads=True,
    )
    page = context.new_page()
    page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => false})')
    return browser, context, page


def get_page_files(page):
    return page.evaluate(r"""() => {
        const rows = document.querySelectorAll('table tbody tr');
        const files = [];
        for (const r of rows) {
            const a = r.querySelector('a');
            if (a) {
                const m = a.textContent.trim().match(/I\d{8}(_r\d)?\.tar/);
                if (m) files.push(m[0]);
            }
        }
        return files;
    }""")


def goto_next_page(page):
    result = page.evaluate("""() => {
        const btn = document.querySelector('.p-paginator-next');
        if (btn && !btn.disabled) { btn.click(); return true; }
        return false;
    }""")
    if result:
        time.sleep(3)
        page.wait_for_selector("table tbody tr", timeout=20000)
        time.sleep(1)
    return result


def click_file(page, filename):
    page.evaluate(CLOSE_DIALOG_JS)
    time.sleep(0.5)
    return page.evaluate(f"""() => {{
        const rows = document.querySelectorAll('table tbody tr');
        for (const r of rows) {{
            const a = r.querySelector('a');
            if (a && a.textContent.trim().includes('{filename}')) {{
                a.click(); return true;
            }}
        }}
        return false;
    }}""")


def solve_captcha(page):
    # 等待 canvas 元素出现并渲染完成
    try:
        page.wait_for_selector(".jCaptchaCanvas", timeout=10000)
        time.sleep(1)  # 等 canvas 绘制完成
    except Exception:
        return None
    grid = page.evaluate(read_captcha_js())
    if not grid:
        return None
    return parse_captcha_grid(grid)


SURGE_PROXY = "http://127.0.0.1:6152"

MAX_NAV_RETRIES = 3


def _navigate_to_list(page, wid, target_page=1):
    """导航到列表页并翻到指定页码，失败最多重试 MAX_NAV_RETRIES 次"""
    for attempt in range(MAX_NAV_RETRIES):
        try:
            page.goto(PAGE_URL, timeout=90000)
            page.wait_for_selector("table tbody tr", timeout=30000)
            time.sleep(2)
            for _ in range(target_page - 1):
                goto_next_page(page)
            return True
        except Exception as e:
            log.warning(f"  W{wid}: 导航失败 (attempt {attempt + 1}/{MAX_NAV_RETRIES}): {e}")
            time.sleep(5 * (attempt + 1))
    return False


PROGRESS_INTERVAL = 15  # 秒


def _curl_download(url, save_path, wid, filename=""):
    """用 curl + Surge 代理下载文件到指定路径，通过 logger 输出进度"""
    cmd = [
        "curl", "-L", "-x", SURGE_PROXY,
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "-o", save_path, "--connect-timeout", "30", "--retry", "3",
        "--silent", "--show-error",
        url,
    ]
    t0 = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    last_size = 0
    last_report = t0

    try:
        while proc.poll() is None:
            time.sleep(2)
            now = time.time()
            if now - last_report >= PROGRESS_INTERVAL:
                try:
                    cur_size = os.path.getsize(save_path)
                except OSError:
                    cur_size = 0
                elapsed = now - t0
                speed = (cur_size - last_size) / (now - last_report) / 1024 / 1024 if (now - last_report) > 0 else 0
                cur_mb = cur_size / 1024 / 1024
                label = filename or os.path.basename(save_path)
                log.info(f"  W{wid}: 下载 {label} — {cur_mb:.0f} MB, {speed:.1f} MB/s")
                last_size = cur_size
                last_report = now

        # curl 结束
        returncode = proc.returncode
        stderr_out = proc.stderr.read().decode(errors="replace").strip()
    except Exception:
        proc.kill()
        raise

    if returncode != 0:
        log.error(f"  W{wid}: curl 失败 (code {returncode}) {stderr_out}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False

    elapsed = time.time() - t0
    size_mb = os.path.getsize(save_path) / 1024 / 1024
    speed = size_mb / elapsed if elapsed > 0 else 0
    log.info(f"  W{wid}: 下载完成 {size_mb:.0f} MB, {elapsed:.0f}s, {speed:.1f} MB/s")
    return True


def download_file(page, filename, wid):
    """获取签名 URL（Playwright 验证码）+ curl 下载到 ~/Downloads"""
    save_path = os.path.join(DOWNLOAD_DIR, filename)

    for attempt in range(MAX_CAPTCHA_RETRIES):
        if _stop:
            return None

        if not click_file(page, filename):
            log.warning(f"  W{wid}: 链接未找到: {filename}")
            return None

        # 等待对话框出现，而非固定 sleep
        try:
            page.wait_for_selector("p-dialog", timeout=10000)
            time.sleep(1)
        except Exception:
            log.warning(f"  W{wid}: 对话框未出现 (attempt {attempt + 1})")
            continue

        answer = solve_captcha(page)
        if answer is None:
            log.warning(f"  W{wid}: 验证码解析失败 (attempt {attempt + 1})，刷新页面")
            page.evaluate(CLOSE_DIALOG_JS)
            time.sleep(1)
            page.reload(timeout=60000)
            page.wait_for_selector("table tbody tr", timeout=30000)
            time.sleep(2)
            continue

        log.info(f"  W{wid}: 验证码={answer}")

        try:
            with page.expect_download(timeout=30000) as dl_info:
                page.evaluate(submit_captcha_js(answer))

            download = dl_info.value
            dl_url = download.url
            download.cancel()  # 立即取消 Playwright 下载
            log.info(f"  W{wid}: 拿到 URL，curl 下载中...")

            if _curl_download(dl_url, save_path, wid, filename):
                return save_path
            continue

        except Exception as e:
            log.warning(f"  W{wid}: 获取 URL 失败 (attempt {attempt + 1}): {e}")
            still_captcha = page.evaluate("!!document.querySelector('.jCaptchaCanvas')")
            if still_captcha:
                log.info(f"  W{wid}: 验证码错误，刷新页面重试")
                page.evaluate(CLOSE_DIALOG_JS)
                time.sleep(1)
                page.reload(timeout=60000)
                page.wait_for_selector("table tbody tr", timeout=30000)
                time.sleep(2)
                continue
            if "bulkdata/datasets/ptgrdt" not in page.url:
                log.info(f"  W{wid}: 页面跳转，导航回列表页")
                if not _navigate_to_list(page, wid):
                    log.error(f"  W{wid}: 导航回列表页失败")
                return None

    log.error(f"  W{wid}: {filename} 全部失败")
    return None


def process_downloaded_file(tar_path, filename, wid):
    """处理下载的 tar 文件：解析 XML 入库 + 提取 DESIGN 图片"""
    if not os.path.exists(tar_path):
        log.warning(f"  W{wid}: 文件不存在: {filename}")
        if filename in get_processed_files():
            return True
        return False

    log.info(f"  W{wid}: 处理 {filename}...")
    stats = process_tar(tar_path)

    if "fatal_error" not in stats:
        try:
            os.remove(tar_path)
        except FileNotFoundError:
            pass
        log.info(
            f"  W{wid}: 完成 {filename} — "
            f"{stats.get('inserted', 0)} 入库, "
            f"{stats.get('design_count', 0)} DESIGN, "
            f"{stats.get('design_images', 0)} 图片, "
            f"{stats.get('elapsed_seconds', 0):.0f}s"
        )
        return True
    else:
        log.error(f"  W{wid}: 处理失败 {filename} — {stats.get('fatal_error', '?')}")
        return False


# ─── Worker ───

def run_worker(worker_id):
    """单个 worker 的下载循环"""
    from playwright.sync_api import sync_playwright

    # 错开启动，避免 5 个 worker 同时解验证码被服务器拒绝
    if worker_id > 0:
        delay = worker_id * 3
        log.info(f"W{worker_id} 等待 {delay}s 后启动")
        time.sleep(delay)

    log.info(f"W{worker_id} 启动")

    pw = sync_playwright().start()
    with _lock:
        _playwrights.append(pw)

    try:
        browser, context, page = create_browser(pw)
        with _lock:
            _browsers.append(browser)

        if not _navigate_to_list(page, worker_id):
            log.error(f"W{worker_id}: 初始导航失败，退出")
            return

        current_page = 1
        downloaded = 0
        consecutive_skip = 0

        while not _stop:
            processed = get_processed_files()
            page_files = get_page_files(page)

            if not page_files:
                log.warning(f"W{worker_id}: 页面无文件")
                break

            unprocessed = [f for f in page_files if f not in processed and not is_skipped(f)]

            if not unprocessed:
                if goto_next_page(page):
                    current_page += 1
                    consecutive_skip = 0
                    continue
                log.info(f"W{worker_id}: 已到最后一页，完成!")
                break

            # 找一个没被其他 worker 声明的文件
            target = None
            for f in unprocessed:
                if claim_file(f):
                    target = f
                    break

            if not target:
                # 当前页文件都被其他 worker 声明了
                if goto_next_page(page):
                    current_page += 1
                    continue
                # 等一下再检查
                time.sleep(10)
                continue

            log.info(f"W{worker_id}: [{downloaded + 1}] 下载 {target} (第{current_page}页)")

            try:
                tar_path = download_file(page, target, worker_id)

                if tar_path:
                    success = process_downloaded_file(tar_path, target, worker_id)
                    if success:
                        downloaded += 1
                        total = len(get_processed_files())
                        log.info(f"W{worker_id}: 累计 {total}/1390 ({total/1390*100:.1f}%)")
                    consecutive_skip = 0
                else:
                    fails = record_fail(target)
                    if fails >= MAX_DOWNLOAD_RETRIES:
                        log.warning(f"W{worker_id}: {target} 失败 {fails} 次，本次跳过")
                    else:
                        log.info(f"W{worker_id}: {target} 失败 {fails}/{MAX_DOWNLOAD_RETRIES}，稍后重试")
                    consecutive_skip += 1
                    if consecutive_skip >= 5:
                        log.info(f"W{worker_id}: 连续 {consecutive_skip} 次失败，翻页")
                        if goto_next_page(page):
                            current_page += 1
                            consecutive_skip = 0
                        else:
                            break

                # 确保回到列表页
                if "bulkdata/datasets/ptgrdt" not in page.url:
                    if not _navigate_to_list(page, worker_id, current_page):
                        log.error(f"W{worker_id}: 无法导航回列表页，重建浏览器")
                        try:
                            browser.close()
                        except Exception:
                            pass
                        browser, context, page = create_browser(pw)
                        with _lock:
                            _browsers.append(browser)
                        if not _navigate_to_list(page, worker_id, current_page):
                            log.error(f"W{worker_id}: 重建后仍无法导航，退出")
                            break

            finally:
                release_file(target)

        log.info(f"W{worker_id}: 退出，共下载 {downloaded} 个文件")

    except Exception as e:
        log.error(f"W{worker_id}: 异常退出 — {e}")
    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            pw.stop()
        except Exception:
            pass


# ─── 入口 ───

def run(num_workers=1):
    log.info("=" * 60)
    log.info(f"PTGRDT 自动下载+处理 启动 ({num_workers} worker{'s' if num_workers > 1 else ''})")
    log.info("=" * 60)

    if num_workers == 1:
        run_worker(0)
    else:
        with ThreadPoolExecutor(max_workers=num_workers) as pool:
            futures = {pool.submit(run_worker, i): i for i in range(num_workers)}
            for future in as_completed(futures):
                wid = futures[future]
                try:
                    future.result()
                except Exception as e:
                    log.error(f"W{wid}: 异常 — {e}")

    _cleanup()


def show_status():
    stats = get_patent_stats()
    failed = get_failed_tars()
    total = stats["tars_completed"] + stats["tars_failed"]

    print(f"\n{'='*50}")
    print(f"PTGRDT 自动下载+处理进度")
    print(f"{'='*50}")
    print(f"已处理 tar: {stats['tars_completed']} 完成, {stats['tars_failed']} 失败 / ~1390 总计")
    print(f"进度: {stats['tars_completed']/1390*100:.1f}%")
    print(f"\n专利总数: {stats['total_patents']:,}")
    print(f"  外观 (DESIGN): {stats['design_patents']:,}")
    print(f"  实用 (UTILITY): {stats['utility_patents']:,}")
    print(f"图片: {stats['total_images']:,}")
    if failed:
        print(f"\n失败的文件 ({len(failed)}):")
        for f, err in sorted(failed):
            print(f"  - {f}: {err}")


def retry_errors():
    failed = get_failed_tars()
    if not failed:
        print("没有需要重试的文件")
        return
    print(f"将重试 {len(failed)} 个失败文件:")
    for f, err in sorted(failed):
        print(f"  - {f}: {err}")
        tar_path = os.path.join(DOWNLOAD_DIR, f)
        if os.path.exists(tar_path):
            os.remove(tar_path)
        remove_from_processed(f)
    print(f"\n已移除，运行 python3 auto_download.py 重新下载")


def main():
    parser = argparse.ArgumentParser(description="PTGRDT 自动下载+处理")
    parser.add_argument("--status", action="store_true", help="查看进度")
    parser.add_argument("--retry-errors", action="store_true", help="重试失败文件")
    parser.add_argument("--workers", type=int, default=1, help="并发 worker 数 (默认 1)")
    args = parser.parse_args()

    if args.status:
        show_status()
    elif args.retry_errors:
        retry_errors()
    else:
        run(args.workers)


if __name__ == "__main__":
    main()
