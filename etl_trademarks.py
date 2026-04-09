#!/usr/bin/env python3
"""
USPTO Trademark XML → PostgreSQL ETL
流式解析 apc*.zip 中的 XML，逐条写入 PostgreSQL。
支持断点续传：已完成的 zip 会跳过。
"""

import os
import sys
import glob
import zipfile
import time
import logging
import psycopg2
from psycopg2.extras import execute_batch
from xml.etree.ElementTree import iterparse

# ─── 配置 ───
DB_CONFIG = {
    "dbname": "uspto",
    "user": "nextderboy",
    "host": "/tmp",
}
RAW_DIR = os.path.join(os.path.dirname(__file__), "raw", "trademarks")
BATCH_SIZE = 1000  # 每批插入条数
LOG_FILE = os.path.join(os.path.dirname(__file__), "etl_trademarks.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def get_text(elem, path, default=None):
    """安全获取子元素文本"""
    e = elem.find(path)
    if e is not None and e.text:
        return e.text.strip()
    return default


def flag(elem, path):
    """T/F 标志转布尔"""
    v = get_text(elem, path)
    return v == "T" if v else False


def parse_date(s):
    """YYYYMMDD → YYYY-MM-DD，用 datetime 严格校验"""
    if not s or len(s) != 8:
        return None
    try:
        from datetime import date
        y, m, d = int(s[:4]), int(s[4:6]), int(s[6:8])
        date(y, m, d)  # 校验合法性（闰年、月天数等）
        return f"{y:04d}-{m:02d}-{d:02d}"
    except:
        return None


def parse_case_file(elem, source_file):
    """解析一条 case-file 元素，返回 (trademark_dict, classes_list, statements_list, owners_list, design_codes_list)"""
    serial = get_text(elem, "serial-number")
    if not serial:
        return None

    try:
        serial_int = int(serial)
    except ValueError:
        return None

    header = elem.find("case-file-header")
    h = header if header is not None else elem  # fallback

    trademark = {
        "serial_number": serial_int,
        "registration_number": get_text(elem, "registration-number"),
        "mark_identification": get_text(h, "mark-identification"),
        "status_code": get_text(h, "status-code"),
        "status_date": parse_date(get_text(h, "status-date")),
        "filing_date": parse_date(get_text(h, "filing-date")),
        "registration_date": parse_date(get_text(h, "registration-date")),
        "cancellation_date": parse_date(get_text(h, "cancellation-date")),
        "abandonment_date": parse_date(get_text(h, "abandonment-date")),
        "mark_drawing_code": get_text(h, "mark-drawing-code"),
        "attorney_name": get_text(h, "attorney-name"),
        "is_trademark": flag(h, "trademark-in"),
        "is_service_mark": flag(h, "service-mark-in"),
        "is_collective": flag(h, "collective-trademark-in") or flag(h, "collective-service-mark-in") or flag(h, "collective-membership-mark-in"),
        "is_certification": flag(h, "certification-mark-in"),
        "is_intent_to_use": flag(h, "intent-to-use-in"),
        "is_use_based": flag(h, "use-application-currently-in") or flag(h, "filed-as-use-application-in"),
        "is_44d": flag(h, "filing-basis-current-44d-in") or flag(h, "filing-basis-filed-as-44d-in"),
        "is_44e": flag(h, "filing-basis-current-44e-in") or flag(h, "filing-basis-filed-as-44e-in"),
        "is_66a": flag(h, "filing-basis-current-66a-in") or flag(h, "filing-basis-filed-as-66a-in"),
        "standard_characters": flag(h, "standard-characters-claimed-in"),
        "color_drawing": flag(h, "color-drawing-current-in") or flag(h, "color-drawing-filed-in"),
        "drawing_3d": flag(h, "drawing-3d-current-in") or flag(h, "drawing-3d-filed-in"),
        "renewal_filed": flag(h, "renewal-filed-in"),
        "section_8_accepted": flag(h, "section-8-accepted-in"),
        "section_15_acknowledged": flag(h, "section-15-acknowledged-in"),
        "source_file": source_file,
    }

    # 分类
    classes = []
    for cls in elem.findall(".//classifications/classification") or elem.findall(".//classification"):
        classes.append({
            "serial_number": serial_int,
            "international_code": get_text(cls, "international-code"),
            "us_code": get_text(cls, "us-code"),
            "status_code": get_text(cls, "status-code"),
            "first_use_date": parse_date(get_text(cls, "first-use-anywhere-date")),
            "first_use_commerce_date": parse_date(get_text(cls, "first-use-in-commerce-date")),
        })

    # 声明（商品服务描述等）
    statements = []
    for stmt in elem.findall(".//case-file-statements/case-file-statement") or []:
        type_code = get_text(stmt, "type-code")
        text = get_text(stmt, "text")
        if type_code:
            statements.append({
                "serial_number": serial_int,
                "type_code": type_code,
                "text": text,
            })

    # 所有者
    owners = []
    for owner in elem.findall(".//case-file-owners/case-file-owner") or []:
        owners.append({
            "serial_number": serial_int,
            "entry_number": get_text(owner, "entry-number"),
            "party_type": get_text(owner, "party-type"),
            "party_name": get_text(owner, "party-name"),
            "entity_type": get_text(owner, "entity-statement/entity-type") or get_text(owner, "entity-type"),
            "nationality_state": get_text(owner, "nationality/state"),
            "nationality_country": get_text(owner, "nationality/country"),
        })

    # 设计搜索码
    design_codes = []
    for ds in elem.findall(".//design-searches/design-search") or []:
        code = get_text(ds, "code")
        if code:
            design_codes.append({
                "serial_number": serial_int,
                "design_code": code,
            })

    return trademark, classes, statements, owners, design_codes


def insert_batch(cur, trademarks, classes, statements, owners, design_codes):
    """批量插入一批数据（幂等：先清理子表旧数据）"""
    if not trademarks:
        return
    # 清理子表旧数据，确保重跑不产生重复
    serial_numbers = [t["serial_number"] for t in trademarks]
    cur.execute("DELETE FROM trademark_classes WHERE serial_number = ANY(%s)", (serial_numbers,))
    cur.execute("DELETE FROM trademark_statements WHERE serial_number = ANY(%s)", (serial_numbers,))
    cur.execute("DELETE FROM trademark_owners WHERE serial_number = ANY(%s)", (serial_numbers,))
    cur.execute("DELETE FROM trademark_design_codes WHERE serial_number = ANY(%s)", (serial_numbers,))

    if trademarks:
        execute_batch(cur, """
            INSERT INTO trademarks (
                serial_number, registration_number, mark_identification,
                status_code, status_date, filing_date, registration_date,
                cancellation_date, abandonment_date, mark_drawing_code, attorney_name,
                is_trademark, is_service_mark, is_collective, is_certification,
                is_intent_to_use, is_use_based, is_44d, is_44e, is_66a,
                standard_characters, color_drawing, drawing_3d,
                renewal_filed, section_8_accepted, section_15_acknowledged,
                source_file
            ) VALUES (
                %(serial_number)s, %(registration_number)s, %(mark_identification)s,
                %(status_code)s, %(status_date)s, %(filing_date)s, %(registration_date)s,
                %(cancellation_date)s, %(abandonment_date)s, %(mark_drawing_code)s, %(attorney_name)s,
                %(is_trademark)s, %(is_service_mark)s, %(is_collective)s, %(is_certification)s,
                %(is_intent_to_use)s, %(is_use_based)s, %(is_44d)s, %(is_44e)s, %(is_66a)s,
                %(standard_characters)s, %(color_drawing)s, %(drawing_3d)s,
                %(renewal_filed)s, %(section_8_accepted)s, %(section_15_acknowledged)s,
                %(source_file)s
            ) ON CONFLICT (serial_number) DO UPDATE SET
                registration_number = EXCLUDED.registration_number,
                mark_identification = EXCLUDED.mark_identification,
                status_code = EXCLUDED.status_code,
                status_date = EXCLUDED.status_date,
                filing_date = EXCLUDED.filing_date,
                registration_date = EXCLUDED.registration_date,
                cancellation_date = EXCLUDED.cancellation_date,
                abandonment_date = EXCLUDED.abandonment_date,
                mark_drawing_code = EXCLUDED.mark_drawing_code,
                attorney_name = EXCLUDED.attorney_name,
                is_trademark = EXCLUDED.is_trademark,
                is_service_mark = EXCLUDED.is_service_mark,
                is_collective = EXCLUDED.is_collective,
                is_certification = EXCLUDED.is_certification,
                is_intent_to_use = EXCLUDED.is_intent_to_use,
                is_use_based = EXCLUDED.is_use_based,
                is_44d = EXCLUDED.is_44d,
                is_44e = EXCLUDED.is_44e,
                is_66a = EXCLUDED.is_66a,
                standard_characters = EXCLUDED.standard_characters,
                color_drawing = EXCLUDED.color_drawing,
                drawing_3d = EXCLUDED.drawing_3d,
                renewal_filed = EXCLUDED.renewal_filed,
                section_8_accepted = EXCLUDED.section_8_accepted,
                section_15_acknowledged = EXCLUDED.section_15_acknowledged,
                source_file = EXCLUDED.source_file
        """, trademarks, page_size=BATCH_SIZE)

    if classes:
        execute_batch(cur, """
            INSERT INTO trademark_classes (
                serial_number, international_code, us_code, status_code,
                first_use_date, first_use_commerce_date
            ) VALUES (
                %(serial_number)s, %(international_code)s, %(us_code)s, %(status_code)s,
                %(first_use_date)s, %(first_use_commerce_date)s
            )
        """, classes, page_size=BATCH_SIZE)

    if statements:
        execute_batch(cur, """
            INSERT INTO trademark_statements (serial_number, type_code, text)
            VALUES (%(serial_number)s, %(type_code)s, %(text)s)
        """, statements, page_size=BATCH_SIZE)

    if owners:
        execute_batch(cur, """
            INSERT INTO trademark_owners (
                serial_number, entry_number, party_type, party_name,
                entity_type, nationality_state, nationality_country
            ) VALUES (
                %(serial_number)s, %(entry_number)s, %(party_type)s, %(party_name)s,
                %(entity_type)s, %(nationality_state)s, %(nationality_country)s
            )
        """, owners, page_size=BATCH_SIZE)

    if design_codes:
        execute_batch(cur, """
            INSERT INTO trademark_design_codes (serial_number, design_code)
            VALUES (%(serial_number)s, %(design_code)s)
        """, design_codes, page_size=BATCH_SIZE)


def process_zip(conn, zip_path):
    """处理一个 zip 文件"""
    zip_name = os.path.basename(zip_path)
    cur = conn.cursor()

    # 检查是否已完成
    cur.execute("SELECT status FROM etl_progress WHERE data_type='trademark' AND source_file=%s", (zip_name,))
    row = cur.fetchone()
    if row and row[0] == "completed":
        log.info(f"跳过已完成: {zip_name}")
        return

    # 标记开始
    cur.execute("""
        INSERT INTO etl_progress (data_type, source_file, status, started_at)
        VALUES ('trademark', %s, 'running', NOW())
        ON CONFLICT (data_type, source_file) DO UPDATE SET status='running', started_at=NOW()
    """, (zip_name,))
    conn.commit()

    log.info(f"开始处理: {zip_name}")
    t0 = time.time()

    zf = zipfile.ZipFile(zip_path)
    xml_name = zf.namelist()[0]

    total = 0
    inserted = 0
    errored = 0

    # 批量缓冲
    buf_tm, buf_cls, buf_stmt, buf_own, buf_dc = [], [], [], [], []

    with zf.open(xml_name) as f:
        for event, elem in iterparse(f, events=["end"]):
            if elem.tag != "case-file":
                continue

            total += 1
            try:
                result = parse_case_file(elem, zip_name)
                if result is None:
                    errored += 1
                    elem.clear()
                    continue

                tm, cls, stmt, own, dc = result
                buf_tm.append(tm)
                buf_cls.extend(cls)
                buf_stmt.extend(stmt)
                buf_own.extend(own)
                buf_dc.extend(dc)
                inserted += 1

                if len(buf_tm) >= BATCH_SIZE:
                    try:
                        insert_batch(cur, buf_tm, buf_cls, buf_stmt, buf_own, buf_dc)
                        conn.commit()
                    except Exception as e:
                        conn.rollback()
                        errored += len(buf_tm)
                        inserted -= len(buf_tm)
                        log.warning(f"  批量插入失败 ({zip_name}), 回滚 {len(buf_tm)} 条: {e}")
                    buf_tm, buf_cls, buf_stmt, buf_own, buf_dc = [], [], [], [], []

                    if inserted % 10000 == 0:
                        elapsed = time.time() - t0
                        rate = inserted / elapsed if elapsed > 0 else 0
                        log.info(f"  {zip_name}: {inserted:,} 条, {rate:.0f} 条/秒")

            except Exception as e:
                errored += 1
                if errored <= 10:
                    log.warning(f"  解析错误 ({zip_name}): {e}")

            elem.clear()

    # 剩余数据
    if buf_tm:
        try:
            insert_batch(cur, buf_tm, buf_cls, buf_stmt, buf_own, buf_dc)
            conn.commit()
        except Exception as e:
            conn.rollback()
            errored += len(buf_tm)
            inserted -= len(buf_tm)
            log.warning(f"  末尾批量插入失败 ({zip_name}): {e}")

    elapsed = time.time() - t0

    # 更新进度
    cur.execute("""
        UPDATE etl_progress SET
            status='completed', records_total=%s, records_inserted=%s,
            records_errored=%s, completed_at=NOW()
        WHERE data_type='trademark' AND source_file=%s
    """, (total, inserted, errored, zip_name))
    conn.commit()
    cur.close()

    log.info(f"完成: {zip_name} | {inserted:,}/{total:,} 条 | {errored} 错误 | {elapsed:.1f}秒")


def main():
    zip_files = sorted(glob.glob(os.path.join(RAW_DIR, "apc*.zip")))
    log.info(f"找到 {len(zip_files)} 个商标 zip 文件")

    if not zip_files:
        log.error("未找到 zip 文件，请检查 raw/trademarks/ 目录")
        sys.exit(1)

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False

    try:
        for i, zp in enumerate(zip_files):
            log.info(f"\n═══ [{i+1}/{len(zip_files)}] {os.path.basename(zp)} ═══")
            process_zip(conn, zp)
    except KeyboardInterrupt:
        log.warning("用户中断，已处理的数据已提交")
    finally:
        conn.close()

    # 打印总结
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM trademarks")
    total_tm = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM etl_progress WHERE data_type='trademark' AND status='completed'")
    completed = cur.fetchone()[0]
    log.info(f"\n总结: {completed}/{len(zip_files)} 个 zip 完成, {total_tm:,} 条商标记录")
    conn.close()


if __name__ == "__main__":
    main()
