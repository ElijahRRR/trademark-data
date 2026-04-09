#!/usr/bin/env python3
"""
USPTO Patent File Wrapper JSON → PostgreSQL ETL
流式解析 zip 中的年份 JSON 文件，多进程并行写入 PostgreSQL。
支持断点续传：已完成的 JSON 文件会跳过。

硬件优化：M4 MAX (36GB RAM) — 多进程并行处理不同年份文件
"""

import os
import sys
import zipfile
import time
import logging
import json
import multiprocessing
from functools import partial
from datetime import datetime

import ijson
import psycopg2
from psycopg2.extras import execute_batch

# ─── 配置 ───
DB_CONFIG = {
    "dbname": "uspto",
    "user": "nextderboy",
    "host": "/tmp",
}
RAW_DIR = os.path.join(os.path.dirname(__file__), "raw", "patents-fw")
BATCH_SIZE = 1000
MAX_WORKERS = 6  # T7 USB SSD IO 瓶颈，6 并发最优
LOG_FILE = os.path.join(os.path.dirname(__file__), "etl_patents.log")

# 配置根日志（每个进程会用自己的 logger）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(processName)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("etl_patents")


def safe_str(val):
    """安全转字符串，None 不变"""
    if val is None:
        return None
    return str(val).strip() or None


def safe_int(val):
    """安全转整数"""
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def safe_date(val):
    """安全解析日期字符串（YYYY-MM-DD 或 YYYYMMDD）"""
    if not val:
        return None
    s = str(val).strip()
    # YYYY-MM-DD
    if len(s) == 10 and s[4] == '-':
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return s
        except ValueError:
            return None
    # YYYYMMDD
    if len(s) == 8 and s.isdigit():
        try:
            datetime.strptime(s, "%Y%m%d")
            return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
        except ValueError:
            return None
    return None


def parse_record(record, source_file):
    """解析一条专利记录，返回 (patent, inventors, applicants, correspondence, events, publications)"""
    app_num = record.get("applicationNumberText")
    if not app_num:
        return None

    meta = record.get("applicationMetaData", {})
    entity_data = meta.get("entityStatusData", {})
    type_code = safe_str(meta.get("applicationTypeCode"))

    patent = {
        "application_number": safe_str(app_num),
        "invention_title": safe_str(meta.get("inventionTitle")),
        "filing_date": safe_date(meta.get("filingDate")),
        "effective_filing_date": safe_date(meta.get("effectiveFilingDate")),
        "application_type": type_code,
        "application_type_label": safe_str(meta.get("applicationTypeLabelName")),
        "application_status_code": safe_str(meta.get("applicationStatusCode")),
        "application_status_desc": safe_str(meta.get("applicationStatusDescriptionText")),
        "application_status_date": safe_date(meta.get("applicationStatusDate")),
        "group_art_unit": safe_str(meta.get("groupArtUnitNumber")),
        "class": safe_str(meta.get("class")),
        "subclass": safe_str(meta.get("subclass")),
        "customer_number": safe_int(meta.get("customerNumber")),
        "docket_number": safe_str(meta.get("docketNumber")),
        "first_inventor_name": safe_str(meta.get("firstInventorName")),
        "first_applicant_name": safe_str(meta.get("firstApplicantName")),
        "entity_status": safe_str(entity_data.get("businessEntityStatusCategory")),
        "small_entity": entity_data.get("smallEntityStatusIndicator", False),
        "national_stage": meta.get("nationalStageIndicator", False),
        "is_design_patent": (type_code == "DES"),
        "source_file": source_file,
    }

    # 发明人
    inventors = []
    for inv in meta.get("inventorBag", []):
        addr = {}
        for a in inv.get("correspondenceAddressBag", []):
            if a.get("postalAddressCategory") == "residence":
                addr = a
                break
        if not addr and inv.get("correspondenceAddressBag"):
            addr = inv["correspondenceAddressBag"][0]
        inventors.append({
            "application_number": safe_str(app_num),
            "first_name": safe_str(inv.get("firstName")),
            "last_name": safe_str(inv.get("lastName")),
            "full_name": safe_str(inv.get("inventorNameText")),
            "city": safe_str(addr.get("cityName")),
            "country_code": safe_str(addr.get("countryCode")),
        })

    # 申请人
    applicants = []
    for appl in meta.get("applicantBag", []):
        addr = {}
        for a in appl.get("correspondenceAddressBag", []):
            addr = a
            break
        applicants.append({
            "application_number": safe_str(app_num),
            "applicant_name": safe_str(appl.get("applicantNameText")),
            "city": safe_str(addr.get("cityName")),
            "country_code": safe_str(addr.get("countryCode")),
        })

    # 通信地址
    correspondence = []
    for corr in record.get("correspondenceAddressBag", []):
        correspondence.append({
            "application_number": safe_str(app_num),
            "name": safe_str(corr.get("nameLineOneText")),
            "address_line1": safe_str(corr.get("addressLineOneText")),
            "city": safe_str(corr.get("cityName")),
            "region_code": safe_str(corr.get("geographicRegionCode")),
            "postal_code": safe_str(corr.get("postalCode")),
            "country_code": safe_str(corr.get("countryCode")),
        })

    # 事件（审查历史）
    events = []
    for evt in record.get("eventDataBag", []):
        events.append({
            "application_number": safe_str(app_num),
            "event_code": safe_str(evt.get("eventCode")),
            "event_date": safe_date(evt.get("eventDate")),
            "event_description": safe_str(evt.get("eventDescriptionText")),
        })

    # 出版类别
    publications = []
    for pub_cat in meta.get("publicationCategoryBag", []):
        publications.append({
            "application_number": safe_str(app_num),
            "publication_category": safe_str(pub_cat),
        })

    return patent, inventors, applicants, correspondence, events, publications


def insert_batch(cur, patents, inventors, applicants, correspondence, events, publications, skip_delete=False):
    """批量插入一批数据。skip_delete=True 时跳过子表清理（用于确认为新记录的场景）"""
    if not patents:
        return

    if not skip_delete:
        # 清理子表旧数据（幂等，仅对可能已存在的记录执行）
        app_numbers = [p["application_number"] for p in patents]
        cur.execute("DELETE FROM patent_inventors WHERE application_number = ANY(%s)", (app_numbers,))
        cur.execute("DELETE FROM patent_applicants WHERE application_number = ANY(%s)", (app_numbers,))
        cur.execute("DELETE FROM patent_correspondence WHERE application_number = ANY(%s)", (app_numbers,))
        cur.execute("DELETE FROM patent_events WHERE application_number = ANY(%s)", (app_numbers,))
        cur.execute("DELETE FROM patent_publications WHERE application_number = ANY(%s)", (app_numbers,))

    execute_batch(cur, """
        INSERT INTO patents (
            application_number, invention_title, filing_date, effective_filing_date,
            application_type, application_type_label,
            application_status_code, application_status_desc, application_status_date,
            group_art_unit, "class", subclass, customer_number, docket_number,
            first_inventor_name, first_applicant_name,
            entity_status, small_entity, national_stage, is_design_patent,
            source_file
        ) VALUES (
            %(application_number)s, %(invention_title)s, %(filing_date)s, %(effective_filing_date)s,
            %(application_type)s, %(application_type_label)s,
            %(application_status_code)s, %(application_status_desc)s, %(application_status_date)s,
            %(group_art_unit)s, %(class)s, %(subclass)s, %(customer_number)s, %(docket_number)s,
            %(first_inventor_name)s, %(first_applicant_name)s,
            %(entity_status)s, %(small_entity)s, %(national_stage)s, %(is_design_patent)s,
            %(source_file)s
        ) ON CONFLICT (application_number) DO NOTHING
    """, patents, page_size=BATCH_SIZE)

    if inventors:
        execute_batch(cur, """
            INSERT INTO patent_inventors (application_number, first_name, last_name, full_name, city, country_code)
            VALUES (%(application_number)s, %(first_name)s, %(last_name)s, %(full_name)s, %(city)s, %(country_code)s)
        """, inventors, page_size=BATCH_SIZE)

    if applicants:
        execute_batch(cur, """
            INSERT INTO patent_applicants (application_number, applicant_name, city, country_code)
            VALUES (%(application_number)s, %(applicant_name)s, %(city)s, %(country_code)s)
        """, applicants, page_size=BATCH_SIZE)

    if correspondence:
        execute_batch(cur, """
            INSERT INTO patent_correspondence (application_number, name, address_line1, city, region_code, postal_code, country_code)
            VALUES (%(application_number)s, %(name)s, %(address_line1)s, %(city)s, %(region_code)s, %(postal_code)s, %(country_code)s)
        """, correspondence, page_size=BATCH_SIZE)

    if events:
        execute_batch(cur, """
            INSERT INTO patent_events (application_number, event_code, event_date, event_description)
            VALUES (%(application_number)s, %(event_code)s, %(event_date)s, %(event_description)s)
        """, events, page_size=BATCH_SIZE)

    if publications:
        execute_batch(cur, """
            INSERT INTO patent_publications (application_number, publication_category)
            VALUES (%(application_number)s, %(publication_category)s)
        """, publications, page_size=BATCH_SIZE)


def process_json_file(args):
    """处理单个年份 JSON 文件（在子进程中运行）"""
    zip_path, json_name = args
    source_file = f"{os.path.basename(zip_path)}:{json_name}"
    proc_log = logging.getLogger(f"etl_patents.{json_name}")

    # 每个进程自己的数据库连接
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cur = conn.cursor()

    # 检查是否已完成
    cur.execute("SELECT status FROM etl_progress WHERE data_type='patent' AND source_file=%s", (source_file,))
    row = cur.fetchone()
    if row and row[0] == "completed":
        proc_log.info(f"跳过已完成: {source_file}")
        conn.close()
        return source_file, "skipped", 0, 0, 0

    # 标记开始
    cur.execute("""
        INSERT INTO etl_progress (data_type, source_file, status, started_at)
        VALUES ('patent', %s, 'running', NOW())
        ON CONFLICT (data_type, source_file) DO UPDATE SET status='running', started_at=NOW(), error_message=NULL
    """, (source_file,))
    conn.commit()

    # 查询已入库记录数，用于跳过已处理的部分（断点续传）
    cur.execute("SELECT count(*) FROM patents WHERE source_file = %s", (source_file,))
    skip_count = cur.fetchone()[0]

    proc_log.info(f"开始处理: {source_file} (跳过前 {skip_count:,} 条已有记录)")
    t0 = time.time()

    total = 0
    inserted = 0
    skipped = 0
    errored = 0

    # 批量缓冲
    buf_pat, buf_inv, buf_app, buf_corr, buf_evt, buf_pub = [], [], [], [], [], []

    try:
        zf = zipfile.ZipFile(zip_path)
        with zf.open(json_name) as f:
            # ijson 流式解析 patentFileWrapperDataBag 中的每个 item
            records = ijson.items(f, "patentFileWrapperDataBag.item")

            for record in records:
                total += 1

                # 跳过已入库的记录
                if skipped < skip_count:
                    skipped += 1
                    if skipped % 50000 == 0:
                        proc_log.info(f"  {json_name}: 跳过 {skipped:,}/{skip_count:,}")
                    continue
                try:
                    result = parse_record(record, source_file)
                    if result is None:
                        errored += 1
                        continue

                    pat, inv, app, corr, evt, pub = result
                    buf_pat.append(pat)
                    buf_inv.extend(inv)
                    buf_app.extend(app)
                    buf_corr.extend(corr)
                    buf_evt.extend(evt)
                    buf_pub.extend(pub)
                    inserted += 1

                    if len(buf_pat) >= BATCH_SIZE:
                        try:
                            # 跳过区之后的记录一定是新的，不需要 DELETE 子表
                            insert_batch(cur, buf_pat, buf_inv, buf_app, buf_corr, buf_evt, buf_pub, skip_delete=True)
                            conn.commit()
                        except Exception as e:
                            conn.rollback()
                            errored += len(buf_pat)
                            inserted -= len(buf_pat)
                            proc_log.warning(f"  批量插入失败 ({source_file}): {e}")
                            # 记录错误到 etl_errors
                            try:
                                cur.execute("""
                                    INSERT INTO etl_errors (data_type, source_file, error_type, error_message)
                                    VALUES ('patent', %s, 'batch_insert', %s)
                                """, (source_file, str(e)[:500]))
                                conn.commit()
                            except:
                                conn.rollback()

                        buf_pat, buf_inv, buf_app, buf_corr, buf_evt, buf_pub = [], [], [], [], [], []

                        if inserted % 10000 == 0:
                            elapsed = time.time() - t0
                            rate = inserted / elapsed if elapsed > 0 else 0
                            proc_log.info(f"  {json_name}: {inserted:,} 条, {rate:.0f} 条/秒")
                            # 中间进度更新（每 5 万条写一次数据库进度）
                            if inserted % 50000 == 0:
                                try:
                                    cur.execute("""
                                        UPDATE etl_progress SET records_inserted=%s, records_total=%s, records_errored=%s
                                        WHERE data_type='patent' AND source_file=%s
                                    """, (inserted, total, errored, source_file))
                                    conn.commit()
                                except:
                                    conn.rollback()

                except Exception as e:
                    errored += 1
                    if errored <= 10:
                        record_id = record.get("applicationNumberText", "?")
                        proc_log.warning(f"  解析错误 ({source_file}, {record_id}): {e}")

        # 剩余数据
        if buf_pat:
            try:
                insert_batch(cur, buf_pat, buf_inv, buf_app, buf_corr, buf_evt, buf_pub, skip_delete=True)
                conn.commit()
            except Exception as e:
                conn.rollback()
                errored += len(buf_pat)
                inserted -= len(buf_pat)
                proc_log.warning(f"  末尾批量插入失败 ({source_file}): {e}")

        elapsed = time.time() - t0
        status = "completed"

        # 更新进度
        cur.execute("""
            UPDATE etl_progress SET
                status='completed', records_total=%s, records_inserted=%s,
                records_skipped=%s, records_errored=%s, completed_at=NOW()
            WHERE data_type='patent' AND source_file=%s
        """, (total, inserted, skipped, errored, source_file))
        conn.commit()

        proc_log.info(f"完成: {json_name} | {inserted:,}/{total:,} 条 | {errored} 错误 | {elapsed:.1f}秒")

    except Exception as e:
        status = "failed"
        elapsed = time.time() - t0
        proc_log.error(f"严重错误 ({source_file}): {e}")
        try:
            cur.execute("""
                UPDATE etl_progress SET
                    status='failed', records_total=%s, records_inserted=%s,
                    records_errored=%s, error_message=%s, completed_at=NOW()
                WHERE data_type='patent' AND source_file=%s
            """, (total, inserted, errored, str(e)[:500], source_file))
            conn.commit()
        except:
            conn.rollback()

    finally:
        conn.close()

    return source_file, status, total, inserted, errored


def collect_tasks():
    """收集所有需要处理的 (zip_path, json_name) 任务"""
    zip_files = sorted([
        os.path.join(RAW_DIR, f) for f in os.listdir(RAW_DIR)
        if f.endswith(".zip") and not f.startswith("._")
    ])

    tasks = []
    for zip_path in zip_files:
        zf = zipfile.ZipFile(zip_path)
        json_names = sorted([n for n in zf.namelist() if n.endswith(".json")])
        for jn in json_names:
            tasks.append((zip_path, jn))

    # 按文件大小排序（大文件先启动，小文件后补位）
    def file_size(task):
        zf = zipfile.ZipFile(task[0])
        return zf.getinfo(task[1]).file_size

    tasks.sort(key=file_size, reverse=True)
    return tasks


def main():
    tasks = collect_tasks()
    log.info(f"共 {len(tasks)} 个年份 JSON 文件待处理")
    for i, (zp, jn) in enumerate(tasks):
        zf = zipfile.ZipFile(zp)
        size_mb = zf.getinfo(jn).file_size / 1024 / 1024
        log.info(f"  [{i+1}] {os.path.basename(zp)}:{jn} ({size_mb:.0f} MB)")

    # 单文件模式（用于测试）
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        target = sys.argv[2] if len(sys.argv) > 2 else None
        if target:
            tasks = [(zp, jn) for zp, jn in tasks if jn == target]
        else:
            # 取最小的文件
            tasks = tasks[-1:]
        log.info(f"单文件模式: {tasks[0][1]}")
        result = process_json_file(tasks[0])
        log.info(f"结果: {result}")
        return

    # 多进程并行
    t0 = time.time()
    workers = min(MAX_WORKERS, len(tasks))
    log.info(f"启动 {workers} 个并行进程")

    with multiprocessing.Pool(workers) as pool:
        results = pool.map(process_json_file, tasks)

    # 汇总
    elapsed = time.time() - t0
    total_inserted = sum(r[3] for r in results)
    total_errored = sum(r[4] for r in results)
    completed = sum(1 for r in results if r[1] == "completed")
    skipped = sum(1 for r in results if r[1] == "skipped")
    failed = sum(1 for r in results if r[1] == "failed")

    log.info(f"\n{'='*60}")
    log.info(f"ETL 完成")
    log.info(f"  文件: {completed} 完成, {skipped} 跳过, {failed} 失败")
    log.info(f"  记录: {total_inserted:,} 插入, {total_errored:,} 错误")
    log.info(f"  耗时: {elapsed:.0f} 秒 ({elapsed/60:.1f} 分钟)")

    # 数据库验证
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM patents")
    total = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM patents WHERE is_design_patent = TRUE")
    design = cur.fetchone()[0]
    cur.execute("SELECT application_type, count(*) FROM patents GROUP BY application_type ORDER BY count(*) DESC")
    type_dist = cur.fetchall()
    conn.close()

    log.info(f"\n数据库验证:")
    log.info(f"  专利总数: {total:,}")
    log.info(f"  外观专利: {design:,}")
    log.info(f"  类型分布:")
    for t, c in type_dist:
        log.info(f"    {t}: {c:,}")


if __name__ == "__main__":
    main()
