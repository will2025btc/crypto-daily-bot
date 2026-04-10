"""生成 TradingView 指标教程封面卡片"""
import sys
sys.path.insert(0, "/home/user/crypto-daily-bot")

from PIL import Image, ImageDraw, ImageFont
from baoyu_skill import hex_to_rgb, draw_rounded_rect, _get_font, THEME

def generate_cover(output_path="/home/user/crypto-daily-bot/tradingview_cover.png"):
    W = 1200
    H = 675  # 16:9 比例，适合社交媒体封面
    PADDING = 60

    # --- 颜色 ---
    BG = "#0D1117"
    CLAUDE_ORANGE = "#DA7756"    # Claude 品牌橙
    TV_BLUE = "#2962FF"          # TradingView 品牌蓝
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
    font_big = _get_font(52)
    font_mid = _get_font(36)
    font_sub = _get_font(24)
    font_tag = _get_font(20)
    font_small = _get_font(18)
    font_code = _get_font(16)

    # ===== 顶部双色装饰线 =====
    draw.rectangle([0, 0, W // 2, 6], fill=hex_to_rgb(CLAUDE_ORANGE))
    draw.rectangle([W // 2, 0, W, 6], fill=hex_to_rgb(TV_BLUE))

    # ===== 左侧主内容区 =====
    y = 50

    # 标签行: [0基础] [实战教程]
    tag_x = PADDING
    draw_rounded_rect(draw, [tag_x, y, tag_x + 100, y + 32], radius=6, fill=GREEN)
    draw.text((tag_x + 12, y + 5), "0 基础", fill=hex_to_rgb("#0D1117"), font=font_tag)
    tag_x += 115
    draw_rounded_rect(draw, [tag_x, y, tag_x + 120, y + 32], radius=6, fill=CLAUDE_ORANGE)
    draw.text((tag_x + 10, y + 5), "实战教程", fill=hex_to_rgb("#0D1117"), font=font_tag)

    y += 60

    # 主标题 - 分两行
    draw.text((PADDING, y), "如何0基础用Claude", fill=hex_to_rgb(TEXT_W), font=font_big)
    y += 68
    draw.text((PADDING, y), "编写TradingView指标", fill=hex_to_rgb(TEXT_W), font=font_big)

    y += 90

    # 副标题
    draw.text((PADDING, y), "从零开始，让AI帮你写出专业级Pine Script策略",
              fill=hex_to_rgb(TEXT_G), font=font_sub)

    y += 60

    # 三个亮点标签
    highlights = [
        ("Claude AI", CLAUDE_ORANGE),
        ("Pine Script", TV_BLUE),
        ("量化交易", ACCENT_PURPLE),
    ]
    hx = PADDING
    for text, color in highlights:
        tw = len(text) * 22 + 24
        draw_rounded_rect(draw, [hx, y, hx + tw, y + 36], radius=8, fill=CARD_BG)
        # 左边小竖线
        draw.rectangle([hx, y + 6, hx + 4, y + 30], fill=hex_to_rgb(color))
        draw.text((hx + 14, y + 7), text, fill=hex_to_rgb(color), font=font_tag)
        hx += tw + 16

    # ===== 右侧装饰区：模拟代码/图表元素 =====
    code_x = 720
    code_y = 80
    code_w = W - PADDING - code_x
    code_h = 420

    # 代码窗口背景
    draw_rounded_rect(draw, [code_x, code_y, code_x + code_w, code_y + code_h],
                      radius=16, fill=CARD_BG)

    # 窗口标题栏
    draw_rounded_rect(draw, [code_x, code_y, code_x + code_w, code_y + 40],
                      radius=16, fill="#21262D")
    # 覆盖底部圆角
    draw.rectangle([code_x, code_y + 28, code_x + code_w, code_y + 40],
                   fill=hex_to_rgb("#21262D"))

    # 窗口三个点
    for i, c in enumerate(["#F85149", "#F0B429", "#3FB950"]):
        cx = code_x + 20 + i * 22
        draw.ellipse([cx, code_y + 14, cx + 12, code_y + 26], fill=hex_to_rgb(c))

    draw.text((code_x + 160, code_y + 12), "indicator.pine",
              fill=hex_to_rgb(TEXT_G), font=font_small)

    # 模拟 Pine Script 代码
    code_lines = [
        ("//@version=5", "#8B949E"),
        ('indicator("My Strategy")', TV_BLUE),
        ("", ""),
        ("// Claude AI Generated", "#8B949E"),
        ("fast = ta.ema(close, 12)", GREEN),
        ("slow = ta.ema(close, 26)", GREEN),
        ("signal = fast - slow", CLAUDE_ORANGE),
        ("", ""),
        ("plot(fast, color=color.blue)", TV_BLUE),
        ("plot(slow, color=color.red)", RED),
        ("", ""),
        ("if ta.crossover(fast, slow)", ACCENT_PURPLE),
        ('    strategy.entry("BUY")', GREEN),
        ("if ta.crossunder(fast, slow)", ACCENT_PURPLE),
        ('    strategy.close("BUY")', RED),
    ]

    cy = code_y + 50
    for idx, (line, color) in enumerate(code_lines):
        if line:
            # 行号
            draw.text((code_x + 15, cy), str(idx + 1).rjust(2),
                      fill=hex_to_rgb("#484F58"), font=font_code)
            draw.text((code_x + 45, cy), line, fill=hex_to_rgb(color), font=font_code)
        cy += 24

    # ===== 底部装饰线 =====
    draw.rectangle([0, H - 6, W // 2, H], fill=hex_to_rgb(CLAUDE_ORANGE))
    draw.rectangle([W // 2, H - 6, W, H], fill=hex_to_rgb(TV_BLUE))

    # 底部水印
    draw.text((PADDING, H - 40), "@fwdailynews",
              fill=hex_to_rgb(TEXT_G), font=font_small)

    img.save(output_path, "PNG", quality=95)
    print(f"✅ 封面已生成: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_cover()
