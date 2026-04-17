"""
C-2 LLM 文本审核

对 L1 未命中 hard_block 的产品, 用 qwen-plus 做三维风险打分:
  ip_risk / offensive_risk / regulatory_risk    (0-100)
  final_verdict: approve | hold | reject
  reasoning: 中文理由 (1-3 句)

输入: product (products_stage dict) + L1 flags 列表 (作为提示)
输出: JSON dict

核心原则:
- 沃尔玛政策嵌入 System Prompt
- 历史违规挑 few-shot 示例 (真实商品 + 真实原因)
- 输出强结构化 JSON
"""
import argparse
import concurrent.futures as cf
import json
import time
from typing import Dict, List

import psycopg2
from psycopg2.extras import Json

from audit_llm_adapter import chat_json, model_text

DB_CONN = "dbname=uspto user=nextderboy"


# ==========================================================================
# System prompt: 沃尔玛政策 + 输出格式
# ==========================================================================

SYSTEM_PROMPT = """你是沃尔玛 Marketplace 合规审核专家, 按照沃尔玛 Trust & Safety 政策判断商品能否上架.

【沃尔玛三大违规维度】
1. Intellectual Property (IP 知识产权):
   - 商标: 产品/标题/描述/图片不得含他人 LIVE 注册商标, 即使 brand=unbranded 也禁止提及他人品牌(如 Nike/Apple/Disney)
   - 版权: 卡通形象/名人头像/运动队 Logo 等
   - 专利: 外观专利覆盖的设计/形状
   - 兼容词陷阱: "for Apple" "compatible with Kleenex" 等高危 (撞商标即拒)
   - authenticity 声明: "authentic/genuine/original" 搬运场景慎用
2. Offensive (冒犯性):
   - 宗教符号/种族歧视/政治敏感/色情/暴力/毒品武器
   - 注意: "gun" 在 "piping gun/glue gun/nail gun" 等工具场景是合法的
3. Regulatory (类目合规):
   - 受限类目: 儿童(CPC)/化妆品(FDA)/医疗器械/膳食补充剂/宠物食品
   - BIZ-CN: 某些类目对中国卖家全面屏蔽 (滤芯/珠宝/服饰/宗教饰品等)
   - BIZ 品牌独占: 部分品类沃尔玛已与某些品牌独家合作
   - 硬禁: 酒精/烟草/枪支弹药/CBD/大麻/OFAC 制裁地区
   - ProductType 必须正确选, 不能是 default

【背景: 用户场景是 Amazon 搬运 + 上架沃尔玛时设 brand=unbranded + 清洗品牌名】
所以重点审视:
- 图片是否含 logo/品牌元素 (输入仅文本时靠描述推断)
- 产品本身是否是外观专利/他人设计 (根据类目+描述推断)
- 类目是否落入 BIZ-CN 或受限类目
- 描述里是否残留品牌词/兼容词/authenticity 声明

【输出要求 JSON, 只输出 JSON 不要任何其他文字】
{
  "ip_risk": 0-100,
  "offensive_risk": 0-100,
  "regulatory_risk": 0-100,
  "counterfeit_risk": 0-100,
  "final_verdict": "approve" | "hold" | "reject",
  "key_issues": ["..."],        // 关键问题列表 (中文短句, 1-3 条)
  "suggested_walmart_product_type": "...",  // 建议的沃尔玛 ProductType (或 null)
  "reasoning": "..."            // 中文总结 1-2 句
}

判定阈值:
- 任一维度 >= 70 且有明确证据 → reject
- 30-70 → hold (需人工或更多信息)
- 全部 < 30 → approve
"""


# ==========================================================================
# Few-shot 示例 (从历史违规挑代表性样本)
# ==========================================================================

FEW_SHOT_EXAMPLES = [
    {
        "product": {
            "title": "Universal Motorcycle Belt Tension Gauge for Harley Davidson",
            "brand": "unbranded",
            "category_path": "Automotive > Motorcycle & Powersports > Parts > Tools",
            "description": "Compatible with Harley Davidson motorcycles, professional mechanic tool.",
        },
        "l1_flags": ["compat_live_trademark: HARLEY DAVIDSON"],
        "output": {
            "ip_risk": 85, "offensive_risk": 5, "regulatory_risk": 30,
            "counterfeit_risk": 50,
            "final_verdict": "reject",
            "key_issues": ["描述声明 'Compatible with Harley Davidson' 撞注册商标",
                          "沃尔玛对 Harley-Davidson 为品牌独占类目"],
            "suggested_walmart_product_type": "Motorcycle Parts",
            "reasoning": "使用 Harley 商标且为品牌独占类目 → IP + BIZ 双重违规",
        },
    },
    {
        "product": {
            "title": "12PCS Color Plastic Cookie Cutters Heart Star Triangle for Vegetable Fruit",
            "brand": "XIPEGPA",
            "category_path": "Home & Kitchen > Kitchen & Dining > Bakeware > Baking Tools",
            "description": "Kid friendly cookie cutters, no sharp edges. For cutting cookie dough, fondant.",
        },
        "l1_flags": [],
        "output": {
            "ip_risk": 5, "offensive_risk": 5, "regulatory_risk": 15,
            "counterfeit_risk": 5,
            "final_verdict": "approve",
            "key_issues": [],
            "suggested_walmart_product_type": "Cookie Cutters",
            "reasoning": "普通厨房烘焙用品, 自有品牌, 无 IP/冒犯/合规风险",
        },
    },
    {
        "product": {
            "title": "Portable Fuel Pump - Battery Powered Gas & Diesel Transfer Siphon 2.6 GPM",
            "brand": "unbranded",
            "category_path": "Automotive > Fluid Change Pumps",
            "description": "Quick transfer for gas, diesel, multi-use siphon.",
        },
        "l1_flags": ["cat_keyword_regulatory: fuel"],
        "output": {
            "ip_risk": 10, "offensive_risk": 5, "regulatory_risk": 90,
            "counterfeit_risk": 10,
            "final_verdict": "reject",
            "key_issues": ["燃油转移泵在沃尔玛属于 Auto and Motor Vehicles Prohibited (EPA 合规限制)",
                          "不含防爆装置的燃油容器/泵类为硬禁"],
            "suggested_walmart_product_type": None,
            "reasoning": "Auto/Motor Vehicles 类目硬禁, 搬运无法补正",
        },
    },
    {
        "product": {
            "title": "Replacement Water Filter Cartridge for Kitchen Faucet",
            "brand": "unbranded",
            "category_path": "Home & Kitchen > Kitchen & Dining > Water Filters",
            "description": "Standard water filter, fits most faucets.",
        },
        "l1_flags": [],
        "output": {
            "ip_risk": 20, "offensive_risk": 5, "regulatory_risk": 85,
            "counterfeit_risk": 25,
            "final_verdict": "reject",
            "key_issues": ["Replacement Water Filters 在沃尔玛是 BIZ-CN 类目 (中国卖家全面屏蔽)"],
            "suggested_walmart_product_type": "Replacement Water Filters",
            "reasoning": "BIZ-CN 代码硬禁, 无法上架",
        },
    },
    {
        "product": {
            "title": "Outdoor Garden Gnome Statue with Hidden Gun Replica",
            "brand": "unbranded",
            "category_path": "Patio, Lawn & Garden > Garden Décor > Statues",
            "description": "Funny garden gnome decoration, features a pistol prop. LARP cosplay friendly.",
        },
        "l1_flags": ["offensive_violence: gun", "offensive_weapon_false_positive: larp"],
        "output": {
            "ip_risk": 10, "offensive_risk": 75, "regulatory_risk": 45,
            "counterfeit_risk": 5,
            "final_verdict": "reject",
            "key_issues": ["商品含枪支复制品 (gun replica / pistol prop), 触发武器类禁售",
                          "LARP cosplay 武器在沃尔玛受限"],
            "suggested_walmart_product_type": None,
            "reasoning": "武器复制品硬禁, 无法上架",
        },
    },
]


# ==========================================================================
# 业务逻辑
# ==========================================================================

def _truncate(s: str, n: int) -> str:
    if not s:
        return ""
    s = str(s)
    if len(s) <= n:
        return s
    return s[:n] + "..."


def _format_product_for_prompt(product: Dict, l1_flags: List[str]) -> str:
    lines = [
        f"标题: {_truncate(product.get('title'), 200)}",
        f"品牌: {product.get('brand') or '(无)'}",
        f"类目路径: {_truncate(product.get('category_path'), 200)}",
        f"原产国: {product.get('origin_country') or '(无)'}",
        f"价格: {product.get('price') or '(无)'}",
        f"五点描述: {_truncate(product.get('bullet_points'), 500)}",
        f"长描述摘要: {_truncate(product.get('long_description'), 800)}",
    ]
    if l1_flags:
        lines.append(f"L1 规则已命中: {' | '.join(l1_flags[:10])}")
    else:
        lines.append("L1 规则未命中硬性违规")
    return "\n".join(lines)


def _build_user_prompt(product: Dict, l1_flags: List[str]) -> str:
    parts = ["以下是历史真实审核示例, 供你参照判断:\n"]
    for i, ex in enumerate(FEW_SHOT_EXAMPLES):
        parts.append(f"\n示例 {i+1}:")
        parts.append("商品:")
        parts.append(_format_product_for_prompt(ex["product"], ex["l1_flags"]))
        parts.append("审核输出:")
        parts.append(json.dumps(ex["output"], ensure_ascii=False, indent=2))
    parts.append("\n\n--- 请对下面的商品做合规审核 ---")
    parts.append(_format_product_for_prompt(product, l1_flags))
    parts.append("\n只输出 JSON, 不要 markdown 标记, 不要其他文字.")
    return "\n".join(parts)


def audit_product_llm(product: Dict, l1_flags: List[str], model=None) -> Dict:
    """对一条产品调 LLM 做三维风险打分"""
    user = _build_user_prompt(product, l1_flags)
    try:
        result = chat_json(SYSTEM_PROMPT, user, model=model, max_tokens=1500)
    except Exception as e:
        return {"_error": str(e), "final_verdict": "hold"}
    # 默认值兜底
    for k in ("ip_risk", "offensive_risk", "regulatory_risk", "counterfeit_risk"):
        v = result.get(k)
        if not isinstance(v, (int, float)):
            result[k] = 30
        else:
            result[k] = max(0, min(100, int(v)))
    if result.get("final_verdict") not in ("approve", "hold", "reject"):
        # 按最高分推断
        maxr = max(result[k] for k in ("ip_risk", "offensive_risk", "regulatory_risk", "counterfeit_risk"))
        result["final_verdict"] = "reject" if maxr >= 70 else ("hold" if maxr >= 30 else "approve")
    return result


# ==========================================================================
# 批量跑 hold_manual 的产品升级审核
# ==========================================================================

def run_llm_on_batch(batch_file: str, verdict_filter=("hold_manual",),
                     max_workers=4, limit=None, verbose=True):
    """
    把指定 batch 中 verdict in filter 的产品送 LLM 二审
    更新 product_audits 的 l2_triggered + llm_raw_response, 并可调整 verdict
    """
    conn = psycopg2.connect(DB_CONN)
    cur = conn.cursor()
    # 拉取待二审产品 + L1 flags
    cur.execute("""
        SELECT pa.id, pa.asin, pa.stage_id, pa.verdict,
               ps.title, ps.brand, ps.category_path, ps.price,
               ps.origin_country, ps.bullet_points, ps.long_description,
               ps.product_type
        FROM product_audits pa
        JOIN products_stage ps ON ps.id = pa.stage_id
        WHERE pa.batch_file = %s AND pa.verdict = ANY(%s)
        ORDER BY pa.overall_risk DESC
    """, (batch_file, list(verdict_filter)))
    rows = cur.fetchall()
    cols = [c[0] for c in cur.description]

    if limit:
        rows = rows[:limit]

    if verbose:
        print(f"待 LLM 审核: {len(rows)} 产品")

    # 取 audit_flags
    def fetch_flags(audit_id):
        cur2 = conn.cursor()
        cur2.execute("""
            SELECT flag_code, description, severity
            FROM audit_flags WHERE audit_id = %s
            ORDER BY CASE severity WHEN 'hard_block' THEN 1 WHEN 'warn' THEN 2 ELSE 3 END
            LIMIT 8
        """, (audit_id,))
        flag_rows = cur2.fetchall()
        cur2.close()
        return [f"{fc}({sv}): {desc}" for fc, desc, sv in flag_rows]

    t0 = time.time()

    def worker(row):
        d = dict(zip(cols, row))
        flags = fetch_flags(d["id"])
        try:
            r = audit_product_llm(d, flags)
            return d, flags, r
        except Exception as e:
            return d, flags, {"_error": str(e)}

    updates = []
    new_verdicts = {"approve": 0, "hold": 0, "reject": 0, "error": 0}
    with cf.ThreadPoolExecutor(max_workers=max_workers) as ex:
        for d, flags, r in ex.map(worker, rows):
            if "_error" in r:
                new_verdicts["error"] += 1
            else:
                nv = r.get("final_verdict", "hold")
                new_verdicts[nv] = new_verdicts.get(nv, 0) + 1

            llm_verdict = r.get("final_verdict", "hold")
            # 映射 LLM 输出到 product_audits verdict: approve / hold_manual / reject
            mapped_verdict = "hold_manual" if llm_verdict == "hold" else llm_verdict
            updates.append((
                mapped_verdict,
                r.get("ip_risk"), r.get("offensive_risk"),
                r.get("regulatory_risk"), r.get("counterfeit_risk"),
                max(
                    r.get("ip_risk") or 0, r.get("offensive_risk") or 0,
                    r.get("regulatory_risk") or 0, r.get("counterfeit_risk") or 0,
                ),
                ((r.get("reasoning") or "") + " | " + "; ".join(r.get("key_issues") or []))[:500],
                Json(r),
                d["id"],
            ))

    cur2 = conn.cursor()
    cur2.executemany("""
        UPDATE product_audits SET
            verdict = %s, ip_risk = %s, offensive_risk = %s,
            regulatory_risk = %s, counterfeit_risk = %s, overall_risk = %s,
            reason_summary = %s,
            llm_raw_response = %s,
            l2_triggered = TRUE
        WHERE id = %s
    """, updates)
    conn.commit()
    cur2.close()
    cur.close()
    conn.close()

    elapsed = time.time() - t0
    if verbose:
        print(f"LLM 审核完成: {len(updates)} 产品, 耗时 {elapsed:.1f}s (avg {elapsed/max(1,len(updates)):.2f}s/product)")
        print(f"LLM verdict 分布:")
        for k, v in new_verdicts.items():
            print(f"  {k}: {v}")
    return new_verdicts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--batch", required=True)
    p.add_argument("--limit", type=int, help="限制审核数量 (抽样)")
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()

    run_llm_on_batch(args.batch, limit=args.limit, max_workers=args.workers)


if __name__ == "__main__":
    main()
