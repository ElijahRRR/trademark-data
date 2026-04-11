#!/usr/bin/env python3
"""
PTGRDT (Patent Grant Red Book) ETL Pipeline

从 PTGRDT tar 文件中解析专利 XML，入库 PostgreSQL，并提取 DESIGN 专利图片。

用法：
  被 auto_download.py 调用，也可独立测试：
    python3 etl_patent_grants.py /path/to/I20240709.tar
"""

import os
import io
import sys
import time
import tarfile
import zipfile
import logging
import psycopg2
from lxml import etree

# ─── 配置 ───
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DESIGN_IMAGE_DIR = os.path.join(PROJECT_DIR, "design_images")

DB_CONFIG = {
    "dbname": "uspto",
    "user": "nextderboy",
}

log = logging.getLogger("etl_pg")


# ─── XML 解析 ───

def parse_patent_xml(xml_bytes):
    """
    解析单个专利 XML，返回结构化 dict。

    返回:
        {
            "patent_number": "D1034980",
            "kind": "S1",
            "application_number": "29749819",
            "appl_type": "design",
            "title": "Nasal dilator",
            "grant_date": "2024-07-09",
            "filing_date": "2020-09-09",
            "abstract": None,
            "num_claims": 1,
            "num_figures": 6,
            "num_drawing_sheets": 2,
            "term_years": 15,
            "term_extension_days": None,
            "assignees": [...],
            "inventors": [...],
            "classifications": [...],
            "citations": [...],
        }
    """
    root = etree.fromstring(xml_bytes)
    bib = root.find(".//us-bibliographic-data-grant")
    if bib is None:
        return None

    # ── 主表字段 ──
    patent_number = _text(bib, ".//publication-reference/document-id/doc-number")
    kind = _text(bib, ".//publication-reference/document-id/kind")
    grant_date = _parse_date(_text(bib, ".//publication-reference/document-id/date"))
    app_number = _text(bib, ".//application-reference/document-id/doc-number")
    filing_date = _parse_date(_text(bib, ".//application-reference/document-id/date"))

    app_ref = bib.find(".//application-reference")
    appl_type = app_ref.get("appl-type", "") if app_ref is not None else ""

    title = _text(bib, ".//invention-title")

    # abstract (UTIL 有, DESIGN 通常没有)
    abstract_el = root.find(".//abstract")
    abstract = " ".join(abstract_el.itertext()).strip() if abstract_el is not None else None

    # claims count
    claims = root.findall(".//claims/claim")
    num_claims = len(claims)

    # figures
    num_figures = _int(_text(bib, ".//figures/number-of-figures"))
    num_drawing_sheets = _int(_text(bib, ".//figures/number-of-drawing-sheets"))

    # term
    term_years = _int(_text(bib, ".//us-term-of-grant/length-of-grant"))
    term_extension_days = _int(_text(bib, ".//us-term-of-grant/us-term-extension"))

    # ── Assignees ──
    assignees = []
    for a in bib.findall(".//assignees/assignee"):
        assignees.append({
            "orgname": _text(a, ".//orgname"),
            "first_name": _text(a, ".//first-name"),
            "last_name": _text(a, ".//last-name"),
            "city": _text(a, ".//city"),
            "state": _text(a, ".//state"),
            "country": _text(a, ".//country"),
        })

    # ── Inventors ──
    inventors = []
    parties = bib.find(".//us-parties")
    if parties is None:
        parties = bib.find(".//parties")
    if parties is not None:
        for inv in parties.findall(".//inventors/inventor"):
            inventors.append({
                "first_name": _text(inv, ".//first-name"),
                "last_name": _text(inv, ".//last-name"),
                "city": _text(inv, ".//city"),
                "state": _text(inv, ".//state"),
                "country": _text(inv, ".//country"),
            })

    # ── Classifications ──
    classifications = []

    # CPC
    for is_main, xpath in [(True, ".//classifications-cpc/main-cpc/classification-cpc"),
                           (False, ".//classifications-cpc/further-cpc/classification-cpc")]:
        for c in bib.findall(xpath):
            section = _text(c, "section") or ""
            cls = _text(c, "class") or ""
            subclass = _text(c, "subclass") or ""
            group = _text(c, "main-group") or ""
            subgroup = _text(c, "subgroup") or ""
            code = f"{section}{cls}{subclass} {group}/{subgroup}".strip()
            if code and code != " /":
                classifications.append({
                    "system": "cpc",
                    "code": code,
                    "is_main": is_main,
                })

    # Locarno
    locarno = _text(bib, ".//classification-locarno/main-classification")
    if locarno:
        classifications.append({
            "system": "locarno",
            "code": locarno,
            "is_main": True,
        })

    # US national
    uspc = _text(bib, ".//classification-national/main-classification")
    if uspc:
        classifications.append({
            "system": "uspc",
            "code": uspc,
            "is_main": True,
        })

    # ── Citations ──
    citations = []
    for cit in root.findall(".//us-references-cited/us-citation"):
        patcit = cit.find("patcit")
        if patcit is not None:
            doc = patcit.find("document-id")
            if doc is not None:
                citations.append({
                    "cited_doc_number": _text(doc, "doc-number"),
                    "cited_country": _text(doc, "country"),
                    "cited_kind": _text(doc, "kind"),
                    "category": _text(cit, "category"),
                })

    return {
        "patent_number": patent_number,
        "kind": kind,
        "application_number": app_number,
        "appl_type": appl_type,
        "title": title,
        "grant_date": grant_date,
        "filing_date": filing_date,
        "abstract": abstract,
        "num_claims": num_claims,
        "num_figures": num_figures,
        "num_drawing_sheets": num_drawing_sheets,
        "term_years": term_years,
        "term_extension_days": term_extension_days,
        "assignees": assignees,
        "inventors": inventors,
        "classifications": classifications,
        "citations": citations,
    }


def _text(el, xpath):
    """安全提取 XML 文本"""
    node = el.find(xpath)
    if node is not None and node.text:
        return node.text.strip()
    return None


def _parse_date(s):
    """'20240709' → '2024-07-09'"""
    if not s or len(s) != 8:
        return None
    return f"{s[:4]}-{s[4:6]}-{s[6:8]}"


def _int(s):
    """安全转 int"""
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


# ─── 数据库写入 ───

def insert_patent(cur, patent, source_tar=None):
    """
    将一个 patent dict 写入数据库。
    ON CONFLICT (patent_number) DO NOTHING 防重复。
    返回 True 表示插入成功，False 表示已存在被跳过。
    """
    pn = patent["patent_number"]
    if not pn:
        return False

    # 主表
    cur.execute("""
        INSERT INTO patent_grants
            (patent_number, kind, application_number, appl_type, title,
             grant_date, filing_date, abstract, num_claims, num_figures,
             num_drawing_sheets, term_years, term_extension_days, source_tar)
        VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s, %s,%s,%s,%s)
        ON CONFLICT (patent_number) DO NOTHING
    """, (
        pn, patent["kind"], patent["application_number"], patent["appl_type"],
        patent["title"], patent["grant_date"], patent["filing_date"],
        patent["abstract"], patent["num_claims"], patent["num_figures"],
        patent["num_drawing_sheets"], patent["term_years"],
        patent["term_extension_days"], source_tar,
    ))

    if cur.rowcount == 0:
        return False  # 已存在

    # Assignees
    for a in patent.get("assignees", []):
        cur.execute("""
            INSERT INTO patent_grant_assignees
                (patent_number, orgname, first_name, last_name, city, state, country)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (pn, a["orgname"], a["first_name"], a["last_name"],
              a["city"], a["state"], a["country"]))

    # Inventors
    for inv in patent.get("inventors", []):
        cur.execute("""
            INSERT INTO patent_grant_inventors
                (patent_number, first_name, last_name, city, state, country)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (pn, inv["first_name"], inv["last_name"],
              inv["city"], inv["state"], inv["country"]))

    # Classifications
    for cl in patent.get("classifications", []):
        cur.execute("""
            INSERT INTO patent_grant_classifications
                (patent_number, system, code, is_main)
            VALUES (%s,%s,%s,%s)
        """, (pn, cl["system"], cl["code"], cl["is_main"]))

    # Citations
    for cit in patent.get("citations", []):
        cur.execute("""
            INSERT INTO patent_grant_citations
                (patent_number, cited_doc_number, cited_country, cited_kind, category)
            VALUES (%s,%s,%s,%s,%s)
        """, (pn, cit["cited_doc_number"], cit["cited_country"],
              cit["cited_kind"], cit["category"]))

    return True


# ─── 图片提取 ───

def extract_design_images(z, patent_number):
    """
    从 ZIP 中提取 DESIGN 专利的 TIFF 图片到磁盘。
    返回 [(image_name, image_path), ...]
    """
    img_dir = os.path.join(DESIGN_IMAGE_DIR, patent_number)
    os.makedirs(img_dir, exist_ok=True)

    images = []
    for name in z.namelist():
        if not name.upper().endswith(".TIF"):
            continue

        # 文件名: USD1034980-20240709-D00001.TIF → D00001.TIF
        basename = os.path.basename(name)
        parts = basename.rsplit("-", 1)
        image_name = parts[-1] if len(parts) > 1 else basename

        image_path = os.path.join("design_images", patent_number, image_name)
        full_path = os.path.join(PROJECT_DIR, image_path)

        # 写入磁盘
        with open(full_path, "wb") as f:
            f.write(z.read(name))

        images.append((image_name, image_path))

    return images


def insert_images(cur, patent_number, images):
    """将图片信息写入 patent_grant_images 表"""
    for image_name, image_path in images:
        cur.execute("""
            INSERT INTO patent_grant_images
                (patent_number, image_name, image_path)
            VALUES (%s, %s, %s)
        """, (patent_number, image_name, image_path))


# ─── 主流程：处理 tar ───

def process_tar(tar_path):
    """
    处理一个 PTGRDT tar 文件：解析所有专利 XML + 入库 + 提取 DESIGN 图片。

    返回 stats dict:
        {
            "tar_file": "I20240709.tar",
            "total_zips": 7936,
            "inserted": 7900,
            "skipped": 36,
            "errored": 0,
            "design_count": 1422,
            "design_images": 12800,
            "elapsed_seconds": 45.2,
        }
    """
    tar_file = os.path.basename(tar_path)
    t0 = time.time()

    stats = {
        "tar_file": tar_file,
        "total_zips": 0,
        "inserted": 0,
        "skipped": 0,
        "errored": 0,
        "design_count": 0,
        "design_images": 0,
        "elapsed_seconds": 0,
    }

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # 记录 etl_progress: running
    cur.execute("""
        INSERT INTO etl_progress (data_type, source_file, status, started_at)
        VALUES ('patent', %s, 'running', NOW())
        ON CONFLICT (data_type, source_file) DO UPDATE
            SET status='running', started_at=NOW(), error_message=NULL
    """, (tar_file,))
    conn.commit()

    try:
        tar = tarfile.open(tar_path, "r")

        for member in tar.getmembers():
            if not member.name.endswith(".ZIP"):
                continue

            # 跳过 SUPP
            if "-SUPP" in member.name.upper() or "/SUPP" in member.name.upper():
                continue

            stats["total_zips"] += 1

            try:
                f = tar.extractfile(member)
                if f is None:
                    continue

                z = zipfile.ZipFile(io.BytesIO(f.read()))

                # 找 XML
                xml_names = [n for n in z.namelist() if n.upper().endswith(".XML")]
                if not xml_names:
                    z.close()
                    continue

                xml_bytes = z.read(xml_names[0])
                patent = parse_patent_xml(xml_bytes)

                if patent is None or not patent.get("patent_number"):
                    stats["errored"] += 1
                    z.close()
                    continue

                pn = patent["patent_number"]

                # 入库
                inserted = insert_patent(cur, patent, source_tar=tar_file)

                if inserted:
                    stats["inserted"] += 1

                    # DESIGN: 提取图片
                    if patent["appl_type"] == "design":
                        stats["design_count"] += 1
                        images = extract_design_images(z, pn)
                        insert_images(cur, pn, images)
                        stats["design_images"] += len(images)
                else:
                    stats["skipped"] += 1

                z.close()

                # 每 500 条提交一次
                if stats["total_zips"] % 500 == 0:
                    conn.commit()
                    log.info(
                        f"  {tar_file}: {stats['total_zips']} ZIPs processed, "
                        f"{stats['inserted']} inserted, {stats['design_images']} images"
                    )

            except Exception as e:
                stats["errored"] += 1
                log.warning(f"  {tar_file}: ZIP 处理错误 {member.name}: {e}")
                continue

        tar.close()
        conn.commit()

        # 更新 etl_progress: completed
        stats["elapsed_seconds"] = round(time.time() - t0, 1)
        cur.execute("""
            UPDATE etl_progress
            SET status='completed',
                records_total=%s, records_inserted=%s,
                records_skipped=%s, records_errored=%s,
                completed_at=NOW()
            WHERE data_type='patent' AND source_file=%s
        """, (
            stats["total_zips"], stats["inserted"],
            stats["skipped"], stats["errored"], tar_file,
        ))
        conn.commit()

    except Exception as e:
        stats["elapsed_seconds"] = round(time.time() - t0, 1)
        stats["fatal_error"] = str(e)
        log.error(f"  {tar_file}: 处理失败 — {e}")

        try:
            cur.execute("""
                UPDATE etl_progress
                SET status='failed', error_message=%s, completed_at=NOW()
                WHERE data_type='patent' AND source_file=%s
            """, (str(e), tar_file))
            conn.commit()
        except Exception:
            pass

    finally:
        cur.close()
        conn.close()

    return stats


# ─── 进度查询（供 auto_download.py 使用）───

def get_processed_tars():
    """返回已完成处理的 tar 文件名集合"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT source_file FROM etl_progress
        WHERE data_type='patent' AND status='completed'
    """)
    result = {row[0] for row in cur.fetchall()}
    cur.close()
    conn.close()
    return result


def get_failed_tars():
    """返回处理失败的 tar 文件名列表"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT source_file, error_message FROM etl_progress
        WHERE data_type='patent' AND status='failed'
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


def get_patent_stats():
    """获取专利数据库统计"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    stats = {}

    cur.execute("SELECT COUNT(*) FROM etl_progress WHERE data_type='patent' AND status='completed'")
    stats["tars_completed"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM etl_progress WHERE data_type='patent' AND status='failed'")
    stats["tars_failed"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patent_grants")
    stats["total_patents"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patent_grants WHERE appl_type='design'")
    stats["design_patents"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patent_grants WHERE appl_type='utility'")
    stats["utility_patents"] = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM patent_grant_images")
    stats["total_images"] = cur.fetchone()[0]

    cur.close()
    conn.close()
    return stats


# ─── 独立运行 ───

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [ETL] %(message)s",
    )

    if len(sys.argv) < 2:
        print("用法: python3 etl_patent_grants.py <tar_path>")
        print("      python3 etl_patent_grants.py --stats")
        sys.exit(1)

    if sys.argv[1] == "--stats":
        stats = get_patent_stats()
        print(f"\n{'='*50}")
        print(f"专利数据库统计")
        print(f"{'='*50}")
        print(f"已处理 tar: {stats['tars_completed']} 完成, {stats['tars_failed']} 失败")
        print(f"专利总数: {stats['total_patents']:,}")
        print(f"  外观 (DESIGN): {stats['design_patents']:,}")
        print(f"  实用 (UTILITY): {stats['utility_patents']:,}")
        print(f"图片数: {stats['total_images']:,}")
    else:
        tar_path = sys.argv[1]
        if not os.path.exists(tar_path):
            print(f"文件不存在: {tar_path}")
            sys.exit(1)

        log.info(f"处理 {tar_path}")
        stats = process_tar(tar_path)
        log.info(f"完成: {stats}")
