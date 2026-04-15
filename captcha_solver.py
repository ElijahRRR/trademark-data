#!/usr/bin/env python3
"""
USPTO jCaptcha 验证码识别模块

针对 USPTO Open Data Portal 的 canvas 算术验证码（70×15 像素）。
识别流程：canvas → ASCII 网格 → 列投影分块 → 5×3 扇区模板匹配 → 计算答案

准确率约 80%，失败时重试即可（每次刷新新题）。
"""

import logging

log = logging.getLogger(__name__)


# ─── 数字模板 ───
# 5 行 × 3 列扇区填充率，基于实际 jCaptcha 像素统计校准
# 行: top, upper-mid, mid, lower-mid, bottom
# 列: left, center, right

DIGIT_TEMPLATES = {
    0: [0.4, 1.0, 0.4,
        0.8, 0.0, 0.8,
        0.8, 0.0, 0.8,
        0.8, 0.0, 0.8,
        0.4, 1.0, 0.4],

    1: [0.0, 0.3, 1.0,
        0.3, 0.3, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0],

    2: [0.3, 1.0, 0.7,
        0.4, 0.0, 0.7,
        0.0, 0.2, 0.8,
        0.1, 0.8, 0.1,
        0.8, 0.8, 0.7],

    3: [0.5, 1.0, 0.3,
        0.2, 0.1, 0.7,
        0.0, 1.0, 0.5,
        0.2, 0.0, 0.7,
        0.7, 0.6, 0.7],

    4: [0.3, 0.0, 0.7,
        0.7, 0.0, 0.7,
        1.0, 1.0, 1.0,
        0.0, 0.0, 0.7,
        0.0, 0.0, 0.7],

    5: [0.5, 1.0, 0.8,
        0.8, 0.4, 0.1,
        0.9, 0.5, 0.7,
        0.3, 0.0, 0.7,
        0.7, 0.6, 0.6],

    6: [0.5, 1.0, 0.7,
        0.8, 0.3, 0.1,
        0.9, 0.5, 0.7,
        0.8, 0.0, 0.7,
        0.6, 0.6, 0.6],

    7: [0.8, 1.0, 1.0,
        0.0, 0.0, 0.7,
        0.0, 0.3, 0.3,
        0.0, 0.5, 0.0,
        0.0, 0.5, 0.0],

    8: [0.3, 1.0, 0.5,
        0.8, 0.1, 0.7,
        0.5, 1.0, 0.6,
        0.9, 0.0, 0.7,
        0.7, 0.6, 0.7],

    9: [0.5, 1.0, 0.5,
        0.7, 0.0, 0.8,
        0.5, 1.0, 0.8,
        0.0, 0.0, 0.7,
        0.5, 0.7, 0.5],
}


# ─── 核心识别 ───

def parse_captcha_grid(grid_str):
    """
    解析 jCaptcha canvas 的 ASCII 网格，返回算术答案。

    参数:
        grid_str: 多行字符串，'#' = 有像素, '.' = 无像素
    返回:
        int 答案，或 None（识别失败）
    """
    lines = grid_str.strip().split("\n")
    h = len(lines)
    w = max(len(l) for l in lines)

    grid = []
    for line in lines:
        row = [1 if i < len(line) and line[i] == "#" else 0 for i in range(w)]
        grid.append(row)

    # 按列统计像素，找字符块
    col_sums = [sum(grid[y][x] for y in range(h)) for x in range(w)]
    blocks = []
    in_block = False
    start = 0
    for x in range(w):
        if col_sums[x] > 0:
            if not in_block:
                start = x
                in_block = True
        else:
            if in_block:
                blocks.append((start, x))
                in_block = False
    if in_block:
        blocks.append((start, w))

    if len(blocks) < 4:
        log.warning(f"只找到 {len(blocks)} 个字符块, 需要 4 个")
        return None

    # 固定格式: [数字] [运算符] [数字] [=]
    d1 = _classify_digit(grid, h, w, blocks[0][0], blocks[0][1])
    op = _classify_operator(grid, h, blocks[1][0], blocks[1][1])
    d2 = _classify_digit(grid, h, w, blocks[2][0], blocks[2][1])

    log.info(f"识别结果: {d1}{op}{d2}=")

    if d1 is None or d2 is None or op is None:
        return None

    if op == "+":
        return d1 + d2
    elif op == "-":
        return d1 - d2

    return None


def _classify_operator(grid, h, bs, be):
    """分类运算符: '+' 或 '-'"""
    bw = be - bs
    row_fills = [sum(grid[y][x] for x in range(bs, be)) for y in range(h)]
    filled_rows = sum(1 for rf in row_fills if rf > 0)

    # "-" 只有少数行有像素（一条横线）
    if filled_rows <= 4:
        return "-"
    return "+"


def _classify_digit(grid, h, w, bs, be):
    """分类数字 0-9"""
    bw = be - bs
    row_fills = [sum(grid[y][x] for x in range(bs, be)) for y in range(h)]
    col_fills = [sum(grid[y][x] for y in range(h)) for x in range(bs, be)]
    total = sum(row_fills)
    if total == 0:
        return None

    # "1" 特判：窄主干
    if bw <= 4:
        return 1
    non_zero_fills = sorted([rf for rf in row_fills if rf > 0])
    if non_zero_fills:
        sorted_cf = sorted(col_fills, reverse=True)
        dominance = sorted_cf[0] / max(sorted_cf[1], 1) if len(sorted_cf) >= 2 else 99
        median_fill = non_zero_fills[len(non_zero_fills) // 2]
        if median_fill <= 3 and dominance >= 2.5:
            return 1

    # 扇区模板匹配
    sig = _sector_signature(grid, h, bs, be)
    if sig is None:
        return None

    best_digit = 0
    best_dist = float("inf")
    for digit, template in DIGIT_TEMPLATES.items():
        if digit == 1:
            continue
        dist = sum((s - t) ** 2 for s, t in zip(sig, template))
        if dist < best_dist:
            best_dist = dist
            best_digit = digit

    return best_digit


def _sector_signature(grid, h, bs, be):
    """将字符块划分为 5×3 扇区，计算各扇区填充率"""
    row_fills = [sum(grid[y][x] for x in range(bs, be)) for y in range(h)]
    active_rows = [y for y in range(h) if row_fills[y] > 0]
    if not active_rows:
        return None

    y_min, y_max = active_rows[0], active_rows[-1]

    col_fills = [sum(grid[y][x] for y in range(h)) for x in range(bs, be)]
    active_cols = [i for i, cf in enumerate(col_fills) if cf > 0]
    if not active_cols:
        return None

    x_min = bs + active_cols[0]
    x_max = bs + active_cols[-1]
    ah = y_max - y_min + 1
    aw = x_max - x_min + 1

    sig = []
    for sr in range(5):
        row_start = y_min + sr * ah // 5
        row_end = y_min + (sr + 1) * ah // 5
        if row_end == row_start:
            row_end = row_start + 1
        for sc in range(3):
            col_start = x_min + sc * aw // 3
            col_end = x_min + (sc + 1) * aw // 3
            if col_end == col_start:
                col_end = col_start + 1
            count = sum(
                grid[y][x]
                for y in range(row_start, min(row_end, h))
                for x in range(col_start, min(col_end, be))
            )
            area = (min(row_end, h) - row_start) * (min(col_end, be) - col_start)
            sig.append(count / max(area, 1))
    return sig


# ─── 浏览器交互 JS ───

def read_captcha_js():
    """读取 jCaptcha canvas 像素的 JS 代码"""
    return """
    () => {
        const canvas = document.querySelector('.jCaptchaCanvas');
        if (!canvas) return null;
        const ctx = canvas.getContext('2d');
        const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const w = canvas.width, h = canvas.height;
        const grid = [];
        for (let y = 0; y < h; y++) {
            let row = '';
            for (let x = 0; x < w; x++) {
                const i = (y * w + x) * 4;
                row += imgData.data[i + 3] > 100 ? '#' : '.';
            }
            grid.push(row);
        }
        return grid.join('\\n');
    }
    """


def submit_captcha_js(answer):
    """填写并提交验证码的 JS 代码"""
    return f"""
    () => {{
        const input = document.querySelector('#jCaptcha');
        const nativeSetter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        nativeSetter.call(input, '{answer}');
        input.dispatchEvent(new Event('input', {{bubbles: true}}));
        input.dispatchEvent(new Event('change', {{bubbles: true}}));
        setTimeout(() => {{
            const dialog = document.querySelector('p-dialog');
            if (dialog) {{
                const buttons = dialog.querySelectorAll('button');
                if (buttons.length >= 3) buttons[2].click();
            }}
        }}, 300);
        return true;
    }}
    """


CLOSE_DIALOG_JS = """
() => {
    const d = document.querySelector('p-dialog');
    if (!d) return false;
    const btns = d.querySelectorAll('button');
    for (const b of btns) {
        if (b.textContent.trim() === 'Cancel') { b.click(); return true; }
    }
    const close = d.querySelector('.p-dialog-header-close, [aria-label="Close"]');
    if (close) { close.click(); return true; }
    if (btns.length > 0) { btns[0].click(); return true; }
    return false;
}
"""
