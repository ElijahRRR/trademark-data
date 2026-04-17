"""
C-3 视觉审核 — qwen-vl-plus 对 hold_manual 产品的图片做 IP / 冒犯检测

场景: Amazon 搬运, 已 brand=unbranded 清洗, 但产品图上可能残留:
  - 品牌 logo (Nike 钩/Apple/Disney 等)
  - 卡通形象 (Mickey/Spider-Man/Pikachu)
  - 运动队标 (NFL/NBA 队徽)
  - 宗教/种族/仇恨符号
  - 武器/毒品/烟草图像
  - 外观专利侵权 (明显抄款)

输入: product (products_stage) + 主图 1-3 张 URL
输出: JSON {
    "has_logo": bool, "logo_brands": [...],
    "has_cartoon_ip": bool, "cartoon_refs": [...],
    "has_sports_team": bool,
    "has_offensive_image": bool, "offensive_type": "...",
    "has_weapon_drug_image": bool,
    "vision_verdict": "approve" | "hold" | "reject",
    "visual_risk": 0-100,
    "reasoning": "..."
}
"""
import argparse
import concurrent.futures as cf
import time
from typing import Dict, List

import psycopg2
from psycopg2.extras import Json

from audit_llm_adapter import vision_json, model_vision

DB_CONN = "dbname=uspto user=nextderboy"


SYSTEM_PROMPT = """你是沃尔玛 Marketplace 视觉合规审核专家. 看商品图片判断是否含侵权或冒犯元素.

【检测项】
1. has_logo: 图片里有可识别的品牌 logo 吗? (Nike 钩 / Apple / Samsung / Starbucks / Coca-Cola / 奢侈品LOGO等)
2. has_cartoon_ip: 图片含卡通形象吗? (Disney/Marvel/DC/Pixar/Sanrio/Pokemon/Peppa Pig 等)
3. has_sports_team: 图片含运动队/联赛标志吗? (NFL/NBA/MLB/NHL/足球队徽等)
4. has_offensive_image: 图片含宗教符号(十字架/佛像/古兰经)/种族歧视/政治敏感/色情/暴力/毒品/仇恨符号(卐/KKK)吗?
5. has_weapon_drug_image: 图片含枪支/刀具/毒品/烟草图像吗? (工具类 piping gun/glue gun 不算)
6. visual_verdict: 综合判定 approve (无任何问题) / hold (有疑似需人工) / reject (明确侵权/冒犯/违禁)
7. visual_risk: 0-100 整体视觉风险分

【搬运场景特别注意】
- 产品本身清洁, 但包装或铭牌 logo 侵权 → reject
- 产品上印有卡通角色 (T恤/水杯/贴纸) → reject
- 外观与已知名牌高度相似 (仿款) → hold
- 宗教节日元素 (圣诞/复活节) 若是普通装饰可 approve, 若是特定宗教符号需 hold

【只输出 JSON, 不要其他文字】
{
  "has_logo": false,
  "logo_brands": [],
  "has_cartoon_ip": false,
  "cartoon_refs": [],
  "has_sports_team": false,
  "has_offensive_image": false,
  "offensive_type": null,
  "has_weapon_drug_image": false,
  "visual_verdict": "approve",
  "visual_risk": 0,
  "reasoning": "..."
}
"""


def _parse_image_urls(s: str, limit=3) -> List[str]:
    """image_urls 原文按 \n 分隔, 取前 limit 张"""
    if not s:
        return []
    urls = [u.strip() for u in s.split("\n") if u.strip().startswith("http")]
    return urls[:limit]


def audit_product_vision(product: Dict, max_images=3) -> Dict:
    """对一条产品调 qwen-vl"""
    urls = _parse_image_urls(product.get("image_urls") or "", limit=max_images)
    if not urls:
        return {"vision_verdict": "hold", "visual_risk": 50,
                "reasoning": "无图片 URL 可审", "_no_images": True}
    user = (
        f"商品标题: {product.get('title')}\n"
        f"类目: {product.get('category_path')}\n"
        f"品牌: {product.get('brand')}\n"
        f"请审核以下 {len(urls)} 张商品图是否有 IP 侵权/冒犯/违禁元素"
    )
    try:
        r = vision_json(SYSTEM_PROMPT, user, urls, model=model_vision())
    except Exception as e:
        return {"_error": str(e), "vision_verdict": "hold"}
    # 类型兜底
    for boolk in ("has_logo", "has_cartoon_ip", "has_sports_team",
                   "has_offensive_image", "has_weapon_drug_image"):
        r.setdefault(boolk, False)
    r["visual_risk"] = int(r.get("visual_risk") or 0)
    if r.get("visual_verdict") not in ("approve", "hold", "reject"):
        r["visual_verdict"] = "reject" if r["visual_risk"] >= 70 else (
            "hold" if r["visual_risk"] >= 30 else "approve")
    return r


def run_vision_on_batch(batch_file, verdict_filter=("hold_manual",),
                        max_workers=4, limit=None, verbose=True):
    """对指定 batch 的 hold 产品调 qwen-vl"""
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    cur.execute("""
        SELECT pa.id, pa.asin, pa.stage_id, pa.verdict,
               ps.title, ps.brand, ps.category_path, ps.image_urls, pa.overall_risk,
               pa.llm_raw_response
        FROM product_audits pa
        JOIN products_stage ps ON ps.id = pa.stage_id
        WHERE pa.batch_file = %s
          AND pa.verdict = ANY(%s)
          AND ps.image_urls IS NOT NULL
        ORDER BY pa.overall_risk DESC
    """, (batch_file, list(verdict_filter)))
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    if limit:
        rows = rows[:limit]
    if verbose:
        print(f"视觉审核: {len(rows)} 产品")
    cur.close()

    t0 = time.time()

    def worker(row):
        d = dict(zip(cols, row))
        r = audit_product_vision(d)
        return d, r

    updates = []
    verdict_counts = {"approve": 0, "hold": 0, "reject": 0, "no_images": 0, "error": 0}

    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        for d, r in ex.map(worker, rows):
            if r.get("_error"):
                verdict_counts["error"] += 1
            elif r.get("_no_images"):
                verdict_counts["no_images"] += 1
            else:
                verdict_counts[r.get("visual_verdict", "hold")] += 1

            vv = r.get("visual_verdict", "hold")
            mapped = "hold_manual" if vv == "hold" else vv
            # 合并之前 llm_raw_response 存新结果
            prev = d.get("llm_raw_response") or {}
            if isinstance(prev, str):
                import json as _json
                try:
                    prev = _json.loads(prev)
                except Exception:
                    prev = {}
            prev["vision"] = r
            visual_risk = r.get("visual_risk") or 0
            new_overall = max(d.get("overall_risk") or 0, visual_risk)
            updates.append((
                mapped,
                max(prev.get("ip_risk") or 0, visual_risk if r.get("has_logo") or r.get("has_cartoon_ip") or r.get("has_sports_team") else 0),
                max(prev.get("offensive_risk") or 0, visual_risk if r.get("has_offensive_image") or r.get("has_weapon_drug_image") else 0),
                prev.get("regulatory_risk") or 0,
                new_overall,
                (((prev.get("reasoning") or "") + " | 视觉: " + (r.get("reasoning") or ""))[:500]),
                Json(prev),
                d["id"],
            ))

    cur = conn.cursor()
    cur.executemany("""
        UPDATE product_audits SET
            verdict = %s, ip_risk = %s, offensive_risk = %s,
            regulatory_risk = %s, overall_risk = %s,
            reason_summary = %s, llm_raw_response = %s,
            l2_vision_triggered = TRUE
        WHERE id = %s
    """, updates)
    conn.commit()
    cur.close()
    conn.close()

    elapsed = time.time() - t0
    if verbose:
        print(f"视觉审核完成: {len(updates)} 产品, {elapsed:.1f}s (avg {elapsed/max(1,len(updates)):.2f}s/product)")
        print("视觉 verdict 分布:")
        for k, v in verdict_counts.items():
            print(f"  {k}: {v}")
    return verdict_counts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--batch", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()
    run_vision_on_batch(args.batch, limit=args.limit, max_workers=args.workers)


if __name__ == "__main__":
    main()
