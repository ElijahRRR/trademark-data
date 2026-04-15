"""
周度任务: 全量刷新 company_brand_details

为什么需要:
- 日常增量流程 (lark_pipeline.py) 不会重查已识别公司的品牌
- USPTO 每天有新商标注册, 老公司可能申请了新品牌
- 这个脚本对所有已有的 real_company 重跑 USPTO 品牌查询

流程:
1. 读出所有 real_company (从 matched_companies)
2. TRUNCATE company_brand_details
3. 对每家公司跑大 JOIN 查询, 重新填充
4. 推送依赖 company_brand_details 的 3 张飞书表
   (公司概览 / 黑名单品牌 / 品牌明细)
   不动 未找到清单 (它不依赖 company_brand_details)
"""
import time

import psycopg2

from lark_process import collect_brands_for_companies
from lark_upload import (
    upload_blacklist,
    upload_brand_details,
    upload_company_overview,
)


DB_CONN = "dbname=uspto user=nextderboy"


def refresh_all_brands():
    """全量刷新 company_brand_details, 返回 (公司数, 品牌记录数)"""
    t0 = time.time()

    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT DISTINCT real_company FROM matched_companies
        WHERE real_company IS NOT NULL
        ORDER BY real_company
        """
    )
    companies = [r[0] for r in cur.fetchall()]
    print(f"  待刷新公司数: {len(companies)}")

    # 记录旧的行数供对比
    cur.execute("SELECT COUNT(*) FROM company_brand_details")
    old_count = cur.fetchone()[0]

    print("  TRUNCATE company_brand_details...")
    cur.execute("TRUNCATE company_brand_details RESTART IDENTITY")
    conn.commit()
    cur.close()
    conn.close()

    print(f"  重新查询 USPTO ({len(companies)} 家公司, 大 JOIN)...")
    # 复用 lark_process.collect_brands_for_companies
    # TRUNCATE 后 already 集合为空, 所有公司都会被查询
    total = collect_brands_for_companies(companies)

    elapsed = time.time() - t0
    print(f"  完成: {total} 条品牌记录 (旧 {old_count} -> 新 {total}, Δ {total - old_count:+d})")
    print(f"  耗时: {elapsed:.1f}s")
    return len(companies), total


def main():
    t_start = time.time()
    print("=" * 60)
    print(f"周度全量刷新 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: 全量重查品牌
    print("\n[1/2] 全量刷新 company_brand_details")
    company_count, brand_count = refresh_all_brands()

    # Step 2: 推送依赖 company_brand_details 的 3 张表
    print("\n[2/2] 推送到飞书 (依赖 company_brand_details 的表)")
    upload_company_overview()  # 活跃品牌数列依赖 company_brand_details
    print()
    upload_blacklist()          # 公司-品牌对照
    print()
    upload_brand_details()      # 品牌明细

    print(f"\n>>> 全部完成 {time.strftime('%Y-%m-%d %H:%M:%S')}, 总耗时 {time.time()-t_start:.1f}s")


if __name__ == "__main__":
    main()
