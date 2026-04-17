"""2026 Pre-IPO 投资平台全聚合指南封面"""
import sys
import math
sys.path.insert(0, "/home/user/crypto-daily-bot")

from PIL import Image, ImageDraw, ImageFont
from baoyu_skill import hex_to_rgb, draw_rounded_rect, _get_font


def draw_chain_icon(draw, cx, cy, size, color):
    """绘制区块链链条图标"""
    c = hex_to_rgb(color)
    # 两个椭圆链环
    w = size * 0.7
    h = size * 0.4
    # 左环
    draw.ellipse([cx - size, cy - h, cx - size + w, cy + h], outline=c, width=4)
    # 右环
    draw.ellipse([cx + size - w, cy - h, cx + size, cy + h], outline=c, width=4)


def draw_building_icon(draw, cx, cy, size, color):
    """绘制建筑/机构图标（代表传统金融）"""
    c = hex_to_rgb(color)
    # 顶部三角屋顶
    s = size
    draw.polygon([
        (cx - s, cy),
        (cx + s, cy),
        (cx, cy - s * 0.5),
    ], fill=c)
    # 底座
    draw.rectangle([cx - s, cy + 2, cx + s, cy + 8], fill=c)
    # 柱子 (4根)
    for i in range(4):
        px = cx - s + 4 + i * (s * 2 - 8) / 3
        draw.rectangle([px, cy + 10, px + 6, cy + s * 0.7], fill=c)
    # 底部台阶
    draw.rectangle([cx - s - 4, cy + s * 0.7, cx + s + 4, cy + s * 0.85], fill=c)


def draw_candle_chart(draw, x0, y0, w, h, color_up, color_down):
    """绘制一个K线图装饰"""
    cu = hex_to_rgb(color_up)
    cd = hex_to_rgb(color_down)
    # 随机模拟K线数据
    candles = [
        (0.3, 0.5, 0.2, 0.45, True),
        (0.45, 0.6, 0.4, 0.55, True),
        (0.55, 0.58, 0.3, 0.35, False),
        (0.35, 0.4, 0.15, 0.25, False),
        (0.25, 0.7, 0.2, 0.65, True),
        (0.65, 0.8, 0.55, 0.78, True),
        (0.78, 0.82, 0.6, 0.65, False),
        (0.65, 0.9, 0.6, 0.88, True),
        (0.88, 0.95, 0.75, 0.8, False),
        (0.8, 0.92, 0.75, 0.9, True),
    ]
    cw = w / len(candles) * 0.6
    gap = w / len(candles)
    for i, (o, hh, ll, c, is_up) in enumerate(candles):
        cx = x0 + i * gap + gap / 2
        color = cu if is_up else cd
        # 影线
        draw.line([(cx, y0 + h * (1 - hh)), (cx, y0 + h * (1 - ll))], fill=color, width=1)
        # 实体
        top = y0 + h * (1 - max(o, c))
        bot = y0 + h * (1 - min(o, c))
        draw.rectangle([cx - cw / 2, top, cx + cw / 2, bot], fill=color)


def draw_blockchain_nodes(img, cx, cy, size, color):
    """绘制区块链节点网络"""
    draw = ImageDraw.Draw(img)
    c = hex_to_rgb(color)
    # 中心节点
    r = size * 0.15
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    # 6个外围节点
    for i in range(6):
        angle = math.radians(i * 60)
        nx = cx + math.cos(angle) * size * 0.7
        ny = cy + math.sin(angle) * size * 0.7
        # 连线
        draw.line([(cx, cy), (nx, ny)], fill=c, width=2)
        # 外围节点
        nr = size * 0.1
        draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=c)


def draw_star(draw, cx, cy, size, color, points=5):
    """绘制星形（代表独角兽/热门）"""
    c = hex_to_rgb(color)
    pts = []
    for i in range(points * 2):
        angle = math.radians(i * 360 / (points * 2) - 90)
        r = size if i % 2 == 0 else size * 0.45
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    draw.polygon(pts, fill=c)


def generate_cover(output_path="/home/user/crypto-daily-bot/preipo_cover.png"):
    W = 1200
    H = 675
    PADDING = 50

    # --- 颜色方案 ---
    BG = "#0A0E14"
    CHAIN_COLOR = "#9B7BFF"        # 紫色 - 链上
    CHAIN_LIGHT = "#BC8CFF"
    TRAD_COLOR = "#FFB547"         # 金色 - 传统
    TRAD_LIGHT = "#FFD080"
    CARD_BG = "#141922"
    CARD_BG_LIGHT = "#1C2230"
    TEXT_W = "#F0F6FC"
    TEXT_G = "#8B949E"
    TEXT_DIM = "#484F58"
    DIVIDER = "#30363D"
    GREEN = "#3FB950"
    RED = "#F85149"
    GOLD = "#F0B429"

    img = Image.new("RGB", (W, H), hex_to_rgb(BG))
    draw = ImageDraw.Draw(img)

    # --- 字体 ---
    font_mega = _get_font(58)
    font_big = _get_font(44)
    font_mid = _get_font(32)
    font_sub = _get_font(22)
    font_sub_sm = _get_font(18)
    font_tag = _get_font(18)
    font_small = _get_font(16)
    font_tiny = _get_font(14)
    font_platform = _get_font(19)
    font_vs = _get_font(68)

    # ===== 背景装饰：左右区域底色 =====
    # 左侧紫色区 (链上)
    left_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(left_bg)
    for i in range(120):
        alpha = max(30 - i // 4, 2)
        ld.rectangle([0, 0, W // 2 - i, H], fill=(155, 123, 255, alpha))
    img.paste(Image.alpha_composite(img.convert("RGBA"), left_bg).convert("RGB"))
    draw = ImageDraw.Draw(img)

    # 右侧金色区 (传统)
    right_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(right_bg)
    for i in range(120):
        alpha = max(30 - i // 4, 2)
        rd.rectangle([W // 2 + i, 0, W, H], fill=(255, 181, 71, alpha))
    img.paste(Image.alpha_composite(img.convert("RGBA"), right_bg).convert("RGB"))
    draw = ImageDraw.Draw(img)

    # ===== 顶部装饰 =====
    # 顶部双色渐变条
    for x in range(W):
        ratio = x / W
        r = int(155 * (1 - ratio) + 255 * ratio)
        g = int(123 * (1 - ratio) + 181 * ratio)
        b = int(255 * (1 - ratio) + 71 * ratio)
        draw.line([(x, 0), (x, 5)], fill=(r, g, b))

    # ===== 顶部标签行 =====
    y = 35
    tag_x = PADDING

    # 2026 热门标签
    draw_rounded_rect(draw, [tag_x, y, tag_x + 70, y + 30], radius=6, fill=RED)
    draw.text((tag_x + 16, y + 5), "HOT", fill=hex_to_rgb("#FFFFFF"), font=font_tag)
    tag_x += 80

    draw_rounded_rect(draw, [tag_x, y, tag_x + 110, y + 30], radius=6, fill=GOLD)
    draw.text((tag_x + 10, y + 5), "Pre-IPO", fill=hex_to_rgb("#0D1117"), font=font_tag)
    tag_x += 120

    draw_rounded_rect(draw, [tag_x, y, tag_x + 90, y + 30], radius=6, fill=GREEN)
    draw.text((tag_x + 12, y + 5), "2026", fill=hex_to_rgb("#0D1117"), font=font_tag)
    tag_x += 100

    draw_rounded_rect(draw, [tag_x, y, tag_x + 100, y + 30], radius=6, fill=CHAIN_COLOR)
    draw.text((tag_x + 8, y + 5), "聚合指南", fill=hex_to_rgb("#FFFFFF"), font=font_tag)

    # ===== 主标题 =====
    y = 85
    title1 = "Pre-IPO 投资平台"
    title2 = "全聚合指南"
    draw.text((PADDING, y), title1, fill=hex_to_rgb(TEXT_W), font=font_mega)
    y += 72
    draw.text((PADDING, y), title2, fill=hex_to_rgb(TEXT_W), font=font_mega)

    # 右上角装饰独角兽star
    draw_star(draw, W - 100, 100, 28, GOLD)
    draw_star(draw, W - 150, 155, 14, GOLD)
    draw_star(draw, W - 60, 160, 10, TEXT_W)

    # ===== 副标题 =====
    y += 90
    sub1 = "Tokenized 链上  vs  传统二级市场"
    draw.text((PADDING, y), sub1, fill=hex_to_rgb(TEXT_G), font=font_mid)
    y += 42
    sub2 = "谁适合你？——SpaceX / OpenAI / Anthropic 热门标的全解析"
    draw.text((PADDING, y), sub2, fill=hex_to_rgb(TEXT_DIM), font=font_sub)

    # ===== 底部对比卡片区 =====
    card_y = 395
    card_h = 235
    gap = 30
    card_w = (W - PADDING * 2 - gap) // 2

    # ----- 左卡：链上 -----
    lx = PADDING
    draw_rounded_rect(draw, [lx + 3, card_y + 3, lx + card_w + 3, card_y + card_h + 3],
                      radius=16, fill="#05070A")  # 阴影
    draw_rounded_rect(draw, [lx, card_y, lx + card_w, card_y + card_h],
                      radius=16, fill=CARD_BG)
    # 顶部色条
    draw_rounded_rect(draw, [lx, card_y, lx + card_w, card_y + 6],
                      radius=16, fill=CHAIN_COLOR)
    draw.rectangle([lx, card_y + 3, lx + card_w, card_y + 6], fill=hex_to_rgb(CHAIN_COLOR))

    # 链上图标+标题
    icon_cx = lx + 40
    icon_cy = card_y + 38
    draw_blockchain_nodes(img, icon_cx, icon_cy, 28, CHAIN_COLOR)
    draw = ImageDraw.Draw(img)

    draw.text((lx + 85, card_y + 22), "链上 / Tokenized",
              fill=hex_to_rgb(CHAIN_LIGHT), font=font_big)

    draw.text((lx + 20, card_y + 80), "零售友好 · 24/7 · 低门槛",
              fill=hex_to_rgb(TEXT_G), font=font_sub_sm)

    # 平台列表
    platforms_chain = [
        ("PreStocks", "Solana 链上"),
        ("Bitget IPO Prime", "SpaceX 首发"),
        ("Jarsy", "$10 起投"),
        ("Robinhood", "$1 超低门槛"),
    ]
    py = card_y + 115
    for name, tag in platforms_chain:
        # 紫色小圆点
        draw.ellipse([lx + 22, py + 6, lx + 34, py + 18], fill=hex_to_rgb(CHAIN_COLOR))
        # 平台名
        draw.text((lx + 44, py), name, fill=hex_to_rgb(TEXT_W), font=font_platform)
        # 小标签
        bbox = draw.textbbox((0, 0), name, font=font_platform)
        nw = bbox[2] - bbox[0]
        draw.text((lx + 44 + nw + 12, py + 4), f"· {tag}",
                  fill=hex_to_rgb(TEXT_DIM), font=font_small)
        py += 26

    # (VS 放到最后绘制以免被卡片遮挡)

    # ----- 右卡：传统 -----
    rx = PADDING + card_w + gap
    draw_rounded_rect(draw, [rx + 3, card_y + 3, rx + card_w + 3, card_y + card_h + 3],
                      radius=16, fill="#05070A")
    draw_rounded_rect(draw, [rx, card_y, rx + card_w, card_y + card_h],
                      radius=16, fill=CARD_BG)
    draw_rounded_rect(draw, [rx, card_y, rx + card_w, card_y + 6],
                      radius=16, fill=TRAD_COLOR)
    draw.rectangle([rx, card_y + 3, rx + card_w, card_y + 6], fill=hex_to_rgb(TRAD_COLOR))

    # 建筑图标+标题
    icon_cx = rx + 40
    icon_cy = card_y + 42
    draw_building_icon(draw, icon_cx, icon_cy, 24, TRAD_COLOR)

    draw.text((rx + 85, card_y + 22), "传统二级市场",
              fill=hex_to_rgb(TRAD_LIGHT), font=font_big)

    draw.text((rx + 20, card_y + 80), "真实股权 · 合规严格 · 高门槛",
              fill=hex_to_rgb(TEXT_G), font=font_sub_sm)

    # 平台列表
    platforms_trad = [
        ("Hiive", "3000+ 公司"),
        ("Forge Global", "机构级"),
        ("EquityZen", "科技聚焦"),
        ("Linqto", "SPV 低门槛"),
    ]
    py = card_y + 115
    for name, tag in platforms_trad:
        draw.ellipse([rx + 22, py + 6, rx + 34, py + 18], fill=hex_to_rgb(TRAD_COLOR))
        draw.text((rx + 44, py), name, fill=hex_to_rgb(TEXT_W), font=font_platform)
        bbox = draw.textbbox((0, 0), name, font=font_platform)
        nw = bbox[2] - bbox[0]
        draw.text((rx + 44 + nw + 12, py + 4), f"· {tag}",
                  fill=hex_to_rgb(TEXT_DIM), font=font_small)
        py += 26

    # ===== 右上角小K线图装饰 =====
    draw_candle_chart(draw, W - 320, 250, 260, 90, GREEN, RED)

    # ===== VS 徽章 (最后画，浮在最上层) =====
    vs_cx = PADDING + card_w + gap // 2
    vs_cy = card_y + card_h // 2
    r = 46
    # 外阴影圆
    draw.ellipse([vs_cx - r - 3, vs_cy - r - 3, vs_cx + r + 3, vs_cy + r + 3],
                 fill=hex_to_rgb("#05070A"))
    # 主圆
    draw.ellipse([vs_cx - r, vs_cy - r, vs_cx + r, vs_cy + r], fill=hex_to_rgb(BG))
    # 描边
    draw.ellipse([vs_cx - r + 2, vs_cy - r + 2, vs_cx + r - 2, vs_cy - r + 2 + (r - 2) * 2],
                 outline=hex_to_rgb("#3A4050"), width=3)
    # VS 文字 - 整体绘制并居中
    vs_font = _get_font(52)
    bbox = draw.textbbox((0, 0), "VS", font=vs_font)
    vw = bbox[2] - bbox[0]
    vh = bbox[3] - bbox[1]
    # V 部分
    v_bbox = draw.textbbox((0, 0), "V", font=vs_font)
    v_w = v_bbox[2] - v_bbox[0]
    start_x = vs_cx - vw // 2
    start_y = vs_cy - vh // 2 - 6
    draw.text((start_x, start_y), "V",
              fill=hex_to_rgb(CHAIN_LIGHT), font=vs_font)
    draw.text((start_x + v_w + 2, start_y), "S",
              fill=hex_to_rgb(TRAD_LIGHT), font=vs_font)

    # ===== 底部装饰线 =====
    for x in range(W):
        ratio = x / W
        r = int(155 * (1 - ratio) + 255 * ratio)
        g = int(123 * (1 - ratio) + 181 * ratio)
        b = int(255 * (1 - ratio) + 71 * ratio)
        draw.line([(x, H - 5), (x, H)], fill=(r, g, b))

    # 底部水印
    draw.text((PADDING, H - 32), "@fwdailynews",
              fill=hex_to_rgb(TEXT_G), font=font_small)
    right_text = "⚠ Pre-IPO 高风险 · 本文非投资建议"
    bbox = draw.textbbox((0, 0), right_text, font=font_small)
    rw = bbox[2] - bbox[0]
    draw.text((W - PADDING - rw, H - 32), right_text,
              fill=hex_to_rgb(TEXT_DIM), font=font_small)

    img.save(output_path, "PNG", quality=95)
    print(f"✅ Pre-IPO 封面已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_cover()
