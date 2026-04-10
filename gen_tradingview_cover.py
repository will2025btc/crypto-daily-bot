"""生成 TradingView 指标教程封面卡片 - 精致版，含 Logo"""
import sys
import math
sys.path.insert(0, "/home/user/crypto-daily-bot")

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from baoyu_skill import hex_to_rgb, draw_rounded_rect, _get_font, THEME


def draw_claude_logo(img, cx, cy, size=60):
    """
    绘制 Claude logo（星芒/光芒形状）
    Claude 的 logo 是一个暖橙色的星芒图案，类似于一个有多个光线的太阳
    """
    draw = ImageDraw.Draw(img)
    color = hex_to_rgb("#DA7756")
    color_light = hex_to_rgb("#E8A88A")

    # 外圈光芒 - 8条射线
    num_rays = 8
    outer_r = size
    inner_r = size * 0.35
    ray_width = size * 0.18

    for i in range(num_rays):
        angle = (i * 360 / num_rays) - 90
        rad = math.radians(angle)

        # 射线末端圆形
        ex = cx + math.cos(rad) * outer_r
        ey = cy + math.sin(rad) * outer_r
        dot_r = ray_width * 0.9
        draw.ellipse([ex - dot_r, ey - dot_r, ex + dot_r, ey + dot_r], fill=color)

        # 射线本体（用粗线段模拟）
        perp_rad = math.radians(angle + 90)
        hw = ray_width * 0.45  # 半宽
        sx = cx + math.cos(rad) * inner_r
        sy = cy + math.sin(rad) * inner_r
        # 四个角
        p1 = (sx + math.cos(perp_rad) * hw, sy + math.sin(perp_rad) * hw)
        p2 = (sx - math.cos(perp_rad) * hw, sy - math.sin(perp_rad) * hw)
        p3 = (ex - math.cos(perp_rad) * hw, ey - math.sin(perp_rad) * hw)
        p4 = (ex + math.cos(perp_rad) * hw, ey + math.sin(perp_rad) * hw)
        draw.polygon([p1, p2, p3, p4], fill=color)

    # 中心圆
    center_r = size * 0.3
    draw.ellipse([cx - center_r, cy - center_r, cx + center_r, cy + center_r], fill=color)
    # 中心高光
    hl_r = center_r * 0.45
    draw.ellipse([cx - hl_r - 2, cy - hl_r - 2, cx + hl_r - 2, cy + hl_r - 2], fill=color_light)


def draw_tradingview_logo(img, cx, cy, size=55):
    """
    绘制 TradingView logo（闪电+图表形状）
    简化为一个蓝色的上升折线图标 + 闪电元素
    """
    draw = ImageDraw.Draw(img)
    color = hex_to_rgb("#2962FF")
    color_light = hex_to_rgb("#5B8DEF")

    s = size

    # 外框圆角矩形
    draw_rounded_rect(draw,
                      [cx - s, cy - s, cx + s, cy + s],
                      radius=s * 0.25, fill="#1A3A7A")

    # 上升折线图 (TradingView 的核心视觉)
    # 从左下到右上的折线
    margin = s * 0.28
    pts = [
        (cx - s + margin, cy + s * 0.45),         # 左下起点
        (cx - s * 0.3, cy + s * 0.1),             # 第一个拐点
        (cx, cy + s * 0.35),                       # 第二个拐点（回调）
        (cx + s * 0.45, cy - s * 0.55),            # 高点
    ]
    line_w = max(int(s * 0.1), 3)
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color_light, width=line_w)

    # 终点箭头
    arrow_tip = pts[-1]
    ax, ay = arrow_tip
    arrow_size = s * 0.2
    draw.polygon([
        (ax + arrow_size * 0.3, ay - arrow_size),
        (ax + arrow_size, ay + arrow_size * 0.2),
        (ax - arrow_size * 0.3, ay + arrow_size * 0.1),
    ], fill=color_light)

    # 底部柱状图装饰
    bar_bottom = cy + s * 0.7
    bar_w = s * 0.12
    bars_data = [0.25, 0.4, 0.3, 0.55, 0.45, 0.7]
    bar_start_x = cx - s * 0.65
    for i, h_ratio in enumerate(bars_data):
        bx = bar_start_x + i * (bar_w + s * 0.1)
        bh = s * h_ratio * 0.5
        bar_color = color if i < 4 else color_light
        draw.rectangle([bx, bar_bottom - bh, bx + bar_w, bar_bottom],
                       fill=bar_color)


def draw_plus_sign(draw, cx, cy, size, color):
    """绘制一个 + 号"""
    t = size * 0.2  # 粗细
    # 横
    draw.rounded_rectangle([cx - size, cy - t, cx + size, cy + t],
                           radius=t, fill=hex_to_rgb(color))
    # 竖
    draw.rounded_rectangle([cx - t, cy - size, cx + t, cy + size],
                           radius=t, fill=hex_to_rgb(color))


def draw_glow(img, cx, cy, radius, color, alpha=40):
    """给logo添加发光效果"""
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r, g, b = hex_to_rgb(color) if isinstance(color, str) else color
    for i in range(5):
        r_now = radius + i * 8
        a = max(alpha - i * 8, 5)
        gd.ellipse([cx - r_now, cy - r_now, cx + r_now, cy + r_now],
                   fill=(r, g, b, a))
    # 合成
    img_rgba = img.convert("RGBA")
    composite = Image.alpha_composite(img_rgba, glow)
    return composite.convert("RGB")


def generate_cover(output_path="/home/user/crypto-daily-bot/tradingview_cover.png"):
    W = 1200
    H = 675
    PADDING = 60

    # --- 颜色 ---
    BG = "#0D1117"
    CLAUDE_ORANGE = "#DA7756"
    TV_BLUE = "#2962FF"
    ACCENT_PURPLE = "#BC8CFF"
    TEXT_W = "#F0F6FC"
    TEXT_G = "#8B949E"
    CARD_BG = "#161B22"
    DIVIDER = "#30363D"
    GREEN = "#3FB950"
    RED = "#F85149"

    img = Image.new("RGB", (W, H), hex_to_rgb(BG))
    draw = ImageDraw.Draw(img)

    # --- 字体 ---
    font_big = _get_font(48)
    font_mid = _get_font(36)
    font_sub = _get_font(22)
    font_tag = _get_font(19)
    font_small = _get_font(17)
    font_code = _get_font(15)
    font_logo_label = _get_font(16)

    # ===== 顶部渐变装饰线 =====
    for x in range(W):
        ratio = x / W
        r = int(218 * (1 - ratio) + 41 * ratio)
        g = int(119 * (1 - ratio) + 98 * ratio)
        b = int(86 * (1 - ratio) + 255 * ratio)
        draw.line([(x, 0), (x, 5)], fill=(r, g, b))

    # ===== Logo 区域（顶部中间偏左） =====
    logo_y = 65
    logo_section_x = PADDING

    # Claude Logo
    claude_logo_cx = logo_section_x + 50
    claude_logo_cy = logo_y + 50
    draw_claude_logo(img, claude_logo_cx, claude_logo_cy, size=38)
    draw = ImageDraw.Draw(img)  # 重新获取draw

    # + 号
    plus_cx = claude_logo_cx + 85
    plus_cy = claude_logo_cy
    draw_plus_sign(draw, plus_cx, plus_cy, 14, TEXT_G)

    # TradingView Logo
    tv_logo_cx = plus_cx + 85
    tv_logo_cy = claude_logo_cy
    draw_tradingview_logo(img, tv_logo_cx, tv_logo_cy, size=38)
    draw = ImageDraw.Draw(img)

    # Logo 文字标签
    draw.text((claude_logo_cx - 26, claude_logo_cy + 46), "Claude",
              fill=hex_to_rgb(CLAUDE_ORANGE), font=font_logo_label)
    draw.text((tv_logo_cx - 42, tv_logo_cy + 46), "TradingView",
              fill=hex_to_rgb(TV_BLUE), font=font_logo_label)

    # ===== 标签行 =====
    tag_y = logo_y + 115
    tag_x = PADDING
    draw_rounded_rect(draw, [tag_x, tag_y, tag_x + 90, tag_y + 30], radius=6, fill=GREEN)
    draw.text((tag_x + 10, tag_y + 4), "0 基础", fill=hex_to_rgb("#0D1117"), font=font_tag)
    tag_x += 100
    draw_rounded_rect(draw, [tag_x, tag_y, tag_x + 110, tag_y + 30], radius=6, fill=CLAUDE_ORANGE)
    draw.text((tag_x + 8, tag_y + 4), "实战教程", fill=hex_to_rgb("#0D1117"), font=font_tag)
    tag_x += 120
    draw_rounded_rect(draw, [tag_x, tag_y, tag_x + 80, tag_y + 30], radius=6, fill=TV_BLUE)
    draw.text((tag_x + 10, tag_y + 4), "2026", fill=hex_to_rgb("#FFFFFF"), font=font_tag)

    # ===== 主标题 =====
    title_y = tag_y + 50
    draw.text((PADDING, title_y), "如何0基础用Claude",
              fill=hex_to_rgb(TEXT_W), font=font_big)
    title_y += 62
    draw.text((PADDING, title_y), "编写TradingView指标",
              fill=hex_to_rgb(TEXT_W), font=font_big)

    # ===== 副标题 =====
    title_y += 70
    draw.text((PADDING, title_y), "从零开始，让AI帮你写出专业级Pine Script策略",
              fill=hex_to_rgb(TEXT_G), font=font_sub)

    # ===== 底部关键词标签 =====
    title_y += 50
    highlights = [
        ("Claude AI", CLAUDE_ORANGE),
        ("Pine Script", TV_BLUE),
        ("量化交易", ACCENT_PURPLE),
    ]
    hx = PADDING
    for text, color in highlights:
        tw = len(text) * 20 + 28
        draw_rounded_rect(draw, [hx, title_y, hx + tw, title_y + 34], radius=8, fill=CARD_BG)
        draw.rectangle([hx + 1, title_y + 7, hx + 5, title_y + 27], fill=hex_to_rgb(color))
        draw.text((hx + 14, title_y + 6), text, fill=hex_to_rgb(color), font=font_tag)
        hx += tw + 14

    # ===== 右侧代码窗口 =====
    code_x = 660
    code_y = 55
    code_w = W - PADDING - code_x
    code_h = 540

    # 窗口阴影
    draw_rounded_rect(draw, [code_x + 4, code_y + 4, code_x + code_w + 4, code_y + code_h + 4],
                      radius=16, fill="#080B10")

    # 代码窗口背景
    draw_rounded_rect(draw, [code_x, code_y, code_x + code_w, code_y + code_h],
                      radius=16, fill=CARD_BG)

    # 窗口标题栏
    draw_rounded_rect(draw, [code_x, code_y, code_x + code_w, code_y + 40],
                      radius=16, fill="#21262D")
    draw.rectangle([code_x, code_y + 28, code_x + code_w, code_y + 40],
                   fill=hex_to_rgb("#21262D"))

    # 窗口三个点
    for i, c in enumerate(["#F85149", "#F0B429", "#3FB950"]):
        dotx = code_x + 20 + i * 22
        draw.ellipse([dotx, code_y + 13, dotx + 14, code_y + 27], fill=hex_to_rgb(c))

    # 文件名标签
    fname_x = code_x + 100
    draw_rounded_rect(draw, [fname_x, code_y + 8, fname_x + 150, code_y + 34],
                      radius=4, fill=CARD_BG)
    draw.text((fname_x + 10, code_y + 11), "indicator.pine",
              fill=hex_to_rgb(TEXT_G), font=font_small)

    # Pine Script 代码 - 更详细
    code_lines = [
        ("//@version=5", "#6A737D"),
        ('indicator("Claude策略", overlay=true)', TV_BLUE),
        ("", ""),
        ("// ===  Claude AI 自动生成  ===", "#6A737D"),
        ("length_fast = input(12, '快线')", TEXT_W),
        ("length_slow = input(26, '慢线')", TEXT_W),
        ("", ""),
        ("// EMA 均线计算", "#6A737D"),
        ("fast = ta.ema(close, length_fast)", GREEN),
        ("slow = ta.ema(close, length_slow)", GREEN),
        ("macd = fast - slow", CLAUDE_ORANGE),
        ("", ""),
        ("// 绘制信号线", "#6A737D"),
        ("plot(fast, 'Fast', color.blue, 2)", TV_BLUE),
        ("plot(slow, 'Slow', color.orange, 2)", CLAUDE_ORANGE),
        ("", ""),
        ("// 交叉信号", "#6A737D"),
        ("bull = ta.crossover(fast, slow)", GREEN),
        ("bear = ta.crossunder(fast, slow)", RED),
        ("", ""),
        ("plotshape(bull, 'BUY',", GREEN),
        ("  shape.triangleup, location.belowbar,", GREEN),
        ("  color.green, size=size.small)", GREEN),
    ]

    cy = code_y + 50
    line_h = 21
    for idx, (line, color) in enumerate(code_lines):
        if line:
            # 行号
            ln = str(idx + 1).rjust(2)
            draw.text((code_x + 12, cy), ln,
                      fill=hex_to_rgb("#484F58"), font=font_code)
            # 分割竖线
            draw.rectangle([code_x + 38, cy, code_x + 39, cy + line_h - 2],
                           fill=hex_to_rgb("#30363D"))
            # 代码文本
            draw.text((code_x + 46, cy), line,
                      fill=hex_to_rgb(color), font=font_code)
        cy += line_h

    # ===== 底部渐变装饰线 =====
    for x in range(W):
        ratio = x / W
        r = int(218 * (1 - ratio) + 41 * ratio)
        g = int(119 * (1 - ratio) + 98 * ratio)
        b = int(86 * (1 - ratio) + 255 * ratio)
        draw.line([(x, H - 5), (x, H)], fill=(r, g, b))

    # 底部水印
    draw.text((PADDING, H - 35), "@fwdailynews",
              fill=hex_to_rgb(TEXT_G), font=font_small)
    draw.text((W - PADDING - 200, H - 35), "Powered by Claude + TradingView",
              fill=hex_to_rgb("#484F58"), font=font_small)

    # ===== 添加发光效果 =====
    img = draw_glow(img, claude_logo_cx, claude_logo_cy, 50, CLAUDE_ORANGE, alpha=25)
    img = draw_glow(img, tv_logo_cx, tv_logo_cy, 50, TV_BLUE, alpha=25)

    img.save(output_path, "PNG", quality=95)
    print(f"✅ 精致封面已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_cover()
