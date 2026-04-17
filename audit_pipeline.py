"""
沃尔玛合规审核主入口 - 一键跑全流程

用法:
    # 全流程: 导入 xlsx → L1 审核 → 飞书推送
    python3 audit_pipeline.py --xlsx /path/to/batch.xlsx

    # 只跑某阶段:
    python3 audit_pipeline.py --action normalize --xlsx batch.xlsx
    python3 audit_pipeline.py --action audit --batch batch_20260417_032822.xlsx
    python3 audit_pipeline.py --action upload --batch batch_20260417_032822.xlsx
    python3 audit_pipeline.py --action all --xlsx batch.xlsx
"""
import argparse
import os
import sys
import time
from pathlib import Path

import psycopg2

DB_CONN = "dbname=uspto user=nextderboy"


def step_normalize(xlsx_path):
    from audit_normalize import import_xlsx
    return import_xlsx(xlsx_path)


def step_audit(batch_file):
    from audit_rules import run_batch
    return run_batch(batch_file)


def step_llm(batch_file, max_workers=10):
    from audit_llm import run_llm_on_batch
    return run_llm_on_batch(batch_file, max_workers=max_workers)


def step_upload(batch_file):
    from audit_upload import upload_all
    upload_all(batch_file=batch_file)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xlsx", help="采集 xlsx 路径 (normalize/all 阶段用)")
    p.add_argument("--batch", help="batch_file 名 (audit/upload 阶段用, 默认=xlsx 文件名)")
    p.add_argument("--action", default="all",
                   choices=["normalize", "audit", "llm", "upload", "all"])
    p.add_argument("--llm-workers", type=int, default=10)
    p.add_argument("--skip-llm", action="store_true", help="all 时跳过 LLM 二审")
    args = p.parse_args()

    batch = args.batch
    if args.xlsx and not batch:
        batch = os.path.basename(args.xlsx)

    t_all = time.time()
    if args.action in ("normalize", "all"):
        if not args.xlsx:
            print("[ERR] normalize/all 需要 --xlsx")
            sys.exit(1)
        print(f"\n{'='*60}\n[1/3] 导入 xlsx → products_stage\n{'='*60}")
        step_normalize(args.xlsx)

    if args.action in ("audit", "all"):
        if not batch:
            print("[ERR] audit/all 需要 --batch 或 --xlsx 推断")
            sys.exit(1)
        print(f"\n{'='*60}\n[L1] 硬规则审核\n{'='*60}")
        step_audit(batch)

    if args.action == "llm" or (args.action == "all" and not args.skip_llm):
        if not batch:
            print("[ERR] llm/all 需要 --batch 或 --xlsx 推断")
            sys.exit(1)
        print(f"\n{'='*60}\n[L2] LLM 二审 (对 hold_manual)\n{'='*60}")
        step_llm(batch, max_workers=args.llm_workers)

    if args.action in ("upload", "all"):
        if not batch:
            print("[ERR] upload/all 需要 --batch 或 --xlsx 推断")
            sys.exit(1)
        print(f"\n{'='*60}\n[推送] 飞书输出\n{'='*60}")
        step_upload(batch)

    print(f"\n{'='*60}\n全流程耗时 {time.time() - t_all:.1f}s\n{'='*60}")


if __name__ == "__main__":
    main()
