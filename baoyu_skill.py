"""
Baoyu Skill 配图模块
生成精美的视觉卡片图片，用于 Telegram 频道配图。
风格参考宝玉(@dotey)的信息卡片设计。
"""

from PIL import Image, ImageDraw, ImageFont
import os
import textwrap


# --- 字体配置 ---
# 优先使用系统中文字体
FONT_PATHS = [
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

def _get_font(size, bold=False):
    """获取可用字体"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


# --- 颜色主题 ---
THEME = {
    "bg": "#0D1117",           # 深色背景
    "card_bg": "#161B22",      # 卡片背景
    "accent": "#58A6FF",       # 强调色（蓝）
    "gold": "#F0B429",         # 金色
    "red": "#F85149",          # 红色
    "green": "#3FB950",        # 绿色
    "text_primary": "#F0F6FC", # 主文字
    "text_secondary": "#8B949E",# 次要文字
    "divider": "#30363D",      # 分割线
    "bar_colors": [            # 柱状图颜色
        "#F85149", "#F0B429", "#58A6FF", "#3FB950", "#BC8CFF", "#79C0FF"
    ],
}


def hex_to_rgb(hex_color):
    """十六进制颜色转RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def draw_rounded_rect(draw, xy, radius, fill):
    """绘制圆角矩形"""
    x0, y0, x1, y1 = xy
    fill_rgb = hex_to_rgb(fill) if isinstance(fill, str) else fill
    draw.rounded_rectangle(xy, radius=radius, fill=fill_rgb)


def generate_ipo_card(companies, title="2025 超级IPO浪潮", subtitle="估值排行榜", output_path="ipo_card.png"):
    """
    生成 IPO 估值排行卡片

    Args:
        companies: list of dict, 每个包含 name, valuation(亿美元), emoji, color(可选)
        title: 标题
        subtitle: 副标题
        output_path: 输出路径
    """
    W = 1080
    PADDING = 60
    TOP_MARGIN = 80
    BAR_HEIGHT = 56
    BAR_GAP = 28
    LABEL_HEIGHT = 30

    n = len(companies)
    # 动态计算高度
    content_h = TOP_MARGIN + 160 + n * (BAR_HEIGHT + BAR_GAP + LABEL_HEIGHT) + 120
    H = max(content_h, 800)

    img = Image.new("RGB", (W, H), hex_to_rgb(THEME["bg"]))
    draw = ImageDraw.Draw(img)

    # --- 顶部装饰线 ---
    draw.rectangle([0, 0, W, 6], fill=hex_to_rgb(THEME["accent"]))

    # --- 标题区域 ---
    font_title = _get_font(44, bold=True)
    font_sub = _get_font(24)
    font_label = _get_font(22)
    font_value = _get_font(20)
    font_bar_label = _get_font(26, bold=True)
    font_footer = _get_font(18)

    y = TOP_MARGIN
    # 火箭 emoji 用文字替代
    draw.text((PADDING, y), title, fill=hex_to_rgb(THEME["text_primary"]), font=font_title)
    y += 60
    draw.text((PADDING, y), subtitle, fill=hex_to_rgb(THEME["text_secondary"]), font=font_sub)
    y += 50

    # --- 分割线 ---
    draw.rectangle([PADDING, y, W - PADDING, y + 2], fill=hex_to_rgb(THEME["divider"]))
    y += 40

    # --- 排序：按估值降序 ---
    sorted_companies = sorted(companies, key=lambda x: x["valuation"], reverse=True)
    max_val = sorted_companies[0]["valuation"] if sorted_companies else 1

    bar_area_left = PADDING + 200  # 留出公司名称空间
    bar_area_right = W - PADDING - 160  # 留出数值空间
    bar_max_width = bar_area_right - bar_area_left

    for i, company in enumerate(sorted_companies):
        name = company["name"]
        val = company["valuation"]
        color_idx = i % len(THEME["bar_colors"])
        color = company.get("color", THEME["bar_colors"][color_idx])

        # 序号圆点 + 公司名称
        dot_x = PADDING
        dot_y = y + BAR_HEIGHT // 2
        draw.ellipse([dot_x, dot_y - 6, dot_x + 12, dot_y + 6], fill=hex_to_rgb(color))
        label_text = f"{name}"
        draw.text((PADDING + 22, y + (BAR_HEIGHT - 26) // 2), label_text,
                  fill=hex_to_rgb(THEME["text_primary"]), font=font_bar_label)

        # 柱状图
        bar_width = int((val / max_val) * bar_max_width)
        bar_width = max(bar_width, 20)  # 最小宽度

        # 渐变效果用圆角矩形
        draw_rounded_rect(draw,
                         [bar_area_left, y + 4, bar_area_left + bar_width, y + BAR_HEIGHT - 4],
                         radius=8, fill=color)

        # 数值标签
        val_text = f"${val:,}亿"
        draw.text((bar_area_left + bar_width + 12, y + (BAR_HEIGHT - 22) // 2),
                  val_text, fill=hex_to_rgb(color), font=font_label)

        y += BAR_HEIGHT + BAR_GAP

    # --- 底部 ---
    y += 20
    draw.rectangle([PADDING, y, W - PADDING, y + 1], fill=hex_to_rgb(THEME["divider"]))
    y += 20
    draw.text((PADDING, y), "数据来源：公开市场信息 | @fwdailynews",
              fill=hex_to_rgb(THEME["text_secondary"]), font=font_footer)

    img.save(output_path, "PNG", quality=95)
    print(f"✅ 卡片已生成: {output_path}")
    return output_path


def generate_text_card(title, body_lines, output_path="text_card.png",
                       accent_color=None):
    """
    生成通用文本信息卡片

    Args:
        title: 卡片标题
        body_lines: list of str, 每行内容
        output_path: 输出路径
        accent_color: 强调色
    """
    accent = accent_color or THEME["accent"]
    W = 1080
    PADDING = 60
    LINE_HEIGHT = 48

    n = len(body_lines)
    H = 160 + n * LINE_HEIGHT + 160

    img = Image.new("RGB", (W, H), hex_to_rgb(THEME["bg"]))
    draw = ImageDraw.Draw(img)

    font_title = _get_font(40, bold=True)
    font_body = _get_font(26)
    font_footer = _get_font(18)

    # 顶部装饰
    draw.rectangle([0, 0, W, 6], fill=hex_to_rgb(accent))

    y = 80
    draw.text((PADDING, y), title, fill=hex_to_rgb(THEME["text_primary"]), font=font_title)
    y += 70

    draw.rectangle([PADDING, y, W - PADDING, y + 2], fill=hex_to_rgb(THEME["divider"]))
    y += 30

    for line in body_lines:
        draw.text((PADDING, y), line, fill=hex_to_rgb(THEME["text_secondary"]), font=font_body)
        y += LINE_HEIGHT

    y += 30
    draw.rectangle([PADDING, y, W - PADDING, y + 1], fill=hex_to_rgb(THEME["divider"]))
    y += 20
    draw.text((PADDING, y), "@fwdailynews",
              fill=hex_to_rgb(THEME["text_secondary"]), font=font_footer)

    img.save(output_path, "PNG", quality=95)
    print(f"✅ 文本卡片已生成: {output_path}")
    return output_path


def send_photo_to_telegram(photo_path, caption="", bot_token=None, chat_id=None):
    """发送图片到 Telegram 频道"""
    import requests
    token = bot_token or os.getenv("TG_BOT_TOKEN")
    chat = chat_id or os.getenv("TG_CHAT_ID", "@fwdailynews")

    if not token:
        print("❌ 缺少 TG_BOT_TOKEN")
        return False

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(photo_path, "rb") as f:
        data = {"chat_id": chat, "caption": caption, "parse_mode": "Markdown"}
        files = {"photo": f}
        res = requests.post(url, data=data, files=files)

    if res.status_code == 200:
        print("🎉 图片已发送到 Telegram!")
        return True
    else:
        print(f"❌ 发送失败: {res.text}")
        return False


# ============================================================
# 快捷生成函数
# ============================================================

def make_ipo_wave_card(output_path="ipo_card.png"):
    """生成 2025 IPO 浪潮卡片"""
    companies = [
        {"name": "SpaceX",     "valuation": 15000, "color": "#F85149"},
        {"name": "OpenAI",     "valuation": 8300,  "color": "#3FB950"},
        {"name": "Anthropic",  "valuation": 1830,  "color": "#BC8CFF"},
        {"name": "Databricks", "valuation": 1600,  "color": "#58A6FF"},
        {"name": "Stripe",     "valuation": 1590,  "color": "#F0B429"},
        {"name": "Revolut",    "valuation": 750,   "color": "#79C0FF"},
        {"name": "Kraken",     "valuation": 200,   "color": "#FF7B72"},
    ]
    return generate_ipo_card(
        companies,
        title="2025 超级IPO浪潮",
        subtitle="史上最大规模科技公司上市潮 | 估值排行 (亿美元)",
        output_path=output_path
    )


if __name__ == "__main__":
    # 直接运行生成 IPO 卡片
    make_ipo_wave_card("ipo_card.png")
