"""
飞书 TRO 匹配流水线 主入口

用法:
    python3 lark_pipeline.py                     # 默认 --action all
    python3 lark_pipeline.py --action sync       # 仅同步飞书 → DB
    python3 lark_pipeline.py --action process    # 仅增量处理
    python3 lark_pipeline.py --action upload     # 仅推送 DB → 飞书
    python3 lark_pipeline.py --action all        # 三步全跑
"""
import argparse
import sys
import time


def step_sync():
    from lark_sync import read_lark_tro_cases, sync_to_db, get_db_summary
    print("=" * 60)
    print("[1/3] 同步飞书 → DB")
    print("=" * 60)
    t0 = time.time()
    cases = read_lark_tro_cases()
    print(f"  飞书读取: {len(cases)} 个案件")
    inserted, updated = sync_to_db(cases)
    print(f"  DB UPSERT: 新增={inserted}, 更新={updated}")
    summary = get_db_summary()
    print(f"  DB 概览: total_cases={summary['total_cases']}, "
          f"matched_total={summary['matched_total']}, "
          f"not_found={summary['not_found']}")
    print(f"  耗时: {time.time() - t0:.1f}s")
    return {"inserted": inserted, "updated": updated}


def step_process():
    from lark_process import process_pending_cases
    print()
    print("=" * 60)
    print("[2/3] 增量处理新案件")
    print("=" * 60)
    t0 = time.time()
    result = process_pending_cases()
    print(f"  结果: {result}")
    print(f"  耗时: {time.time() - t0:.1f}s")
    return result


def step_upload():
    from lark_upload import upload_all
    print()
    print("=" * 60)
    print("[3/3] 推送 DB → 飞书")
    print("=" * 60)
    t0 = time.time()
    result = upload_all()
    print(f"  总耗时: {time.time() - t0:.1f}s")
    return result


def main():
    parser = argparse.ArgumentParser(description="飞书 TRO 匹配流水线")
    parser.add_argument(
        "--action",
        choices=["sync", "process", "upload", "all"],
        default="all",
        help="执行步骤 (默认 all)",
    )
    args = parser.parse_args()

    t0 = time.time()
    print(f"\n>>> lark_pipeline --action={args.action} 开始\n")

    try:
        if args.action in ("sync", "all"):
            step_sync()
        if args.action in ("process", "all"):
            step_process()
        if args.action in ("upload", "all"):
            step_upload()
    except Exception as e:
        print(f"\n❌ 失败: {type(e).__name__}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    print(f"\n>>> 全部完成，总耗时 {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
