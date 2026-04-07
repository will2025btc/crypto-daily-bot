"""生成 Hermes Agent vs OpenClaw 对比卡片"""
import sys
sys.path.insert(0, "/home/user/crypto-daily-bot")

from PIL import Image, ImageDraw, ImageFont
from baoyu_skill import hex_to_rgb, draw_rounded_rect, _get_font, THEME

def generate_vs_card(output_path="/home/user/crypto-daily-bot/hermes_vs_openclaw.png"):
    W = 1200
    PADDING = 50

    # --- 颜色 ---
    HERMES_COLOR = "#BC8CFF"   # 紫色
    OPENCLAW_COLOR = "#58A6FF" # 蓝色
    WIN_COLOR = "#3FB950"      # 绿色胜出标记
    BG = "#0D1117"
    CARD_BG = "#161B22"
    DIVIDER = "#30363D"
    TEXT_W = "#F0F6FC"
    TEXT_G = "#8B949E"

    # --- 对比数据 ---
    rows = [
        ("架构核心",   "中央Gateway控制器",        "Agent自执行循环(do>learn>improve)", "right"),
        ("记忆系统",   "基础持久记忆+文件存储",     "多层记忆(SQLite+FTS5+LLM总结)",   "right"),
        ("学习能力",   "手动写Skill/社区插件",      "自动学习闭环,自动提炼Skill",      "right"),
        ("技能生态",   "10k+社区Skill(ClawHub)",   "自动生成,数量少但专为你定制",      "left"),
        ("消息平台",   "50+平台(极致广)",           "7-10个主流平台",                  "left"),
        ("模型支持",   "主流模型",                  "200+模型(超灵活)",                "right"),
        ("部署上手",   "成熟稳定",                  "更快更轻($5 VPS即跑)",           "right"),
        ("迁移支持",   "-",                        "一键迁移(hermes claw migrate)",   "right"),
        ("社区规模",   "339k+星,巨型生态",          "Nous Research背书,增长极快",      "left"),
    ]

    # --- 字体 ---
    font_title = _get_font(42)
    font_subtitle = _get_font(22)
    font_tag = _get_font(20)
    font_dim = _get_font(20)
    font_cell = _get_font(19)
    font_section = _get_font(26)
    font_footer = _get_font(16)
    font_bullet = _get_font(20)

    # --- 计算高度 ---
    ROW_H = 90
    HEADER_H = 280
    TABLE_H = len(rows) * ROW_H + 60
    VERDICT_H = 400
    H = HEADER_H + TABLE_H + VERDICT_H + 80

    img = Image.new("RGB", (W, H), hex_to_rgb(BG))
    draw = ImageDraw.Draw(img)

    # ===== 顶部装饰：双色渐变线 =====
    half = W // 2
    draw.rectangle([0, 0, half, 5], fill=hex_to_rgb(HERMES_COLOR))
    draw.rectangle([half, 0, W, 5], fill=hex_to_rgb(OPENCLAW_COLOR))

    y = 40

    # ===== 标题 =====
    title = "Hermes Agent vs OpenClaw"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), title, fill=hex_to_rgb(TEXT_W), font=font_title)
    y += 60

    sub = "2026 最新对比 | 开源本地AI Agent"
    bbox2 = draw.textbbox((0, 0), sub, font=font_subtitle)
    sw = bbox2[2] - bbox2[0]
    draw.text(((W - sw) // 2, y), sub, fill=hex_to_rgb(TEXT_G), font=font_subtitle)
    y += 50

    # ===== 一句话总结区 =====
    draw_rounded_rect(draw, [PADDING, y, W // 2 - 10, y + 80], radius=12, fill=CARD_BG)
    draw_rounded_rect(draw, [W // 2 + 10, y, W - PADDING, y + 80], radius=12, fill=CARD_BG)

    # Hermes 标签
    draw_rounded_rect(draw, [PADDING + 12, y + 10, PADDING + 12 + 120, y + 36], radius=6, fill=HERMES_COLOR)
    draw.text((PADDING + 22, y + 11), "Hermes", fill=hex_to_rgb("#0D1117"), font=font_tag)
    draw.text((PADDING + 12, y + 44), '"自我进化的私人分身"', fill=hex_to_rgb(TEXT_W), font=font_cell)

    # OpenClaw 标签
    ox = W // 2 + 22
    draw_rounded_rect(draw, [ox, y + 10, ox + 130, y + 36], radius=6, fill=OPENCLAW_COLOR)
    draw.text((ox + 10, y + 11), "OpenClaw", fill=hex_to_rgb("#0D1117"), font=font_tag)
    draw.text((ox, y + 44), '"生态大、插件多的万能工具箱"', fill=hex_to_rgb(TEXT_W), font=font_cell)

    y += 105

    # ===== 对比表格 =====
    draw.rectangle([PADDING, y, W - PADDING, y + 1], fill=hex_to_rgb(DIVIDER))
    y += 15

    # 表头
    col_dim = PADDING + 10
    col_oc = PADDING + 150
    col_hm = W // 2 + 40

    draw.text((col_dim, y), "维度", fill=hex_to_rgb(TEXT_G), font=font_dim)
    draw.text((col_oc, y), "OpenClaw", fill=hex_to_rgb(OPENCLAW_COLOR), font=font_dim)
    draw.text((col_hm, y), "Hermes Agent", fill=hex_to_rgb(HERMES_COLOR), font=font_dim)
    y += 36

    draw.rectangle([PADDING, y, W - PADDING, y + 1], fill=hex_to_rgb(DIVIDER))
    y += 8

    for dim, oc_text, hm_text, winner in rows:
        row_y = y

        # 维度名
        draw.text((col_dim, row_y + 8), dim, fill=hex_to_rgb(TEXT_W), font=font_dim)

        # OpenClaw 列
        oc_color = WIN_COLOR if winner == "left" else TEXT_G
        # 自动换行
        oc_lines = _wrap_text(oc_text, 20)
        for j, line in enumerate(oc_lines):
            draw.text((col_oc, row_y + 8 + j * 26), line, fill=hex_to_rgb(oc_color), font=font_cell)

        # Hermes 列
        hm_color = WIN_COLOR if winner == "right" else TEXT_G
        hm_lines = _wrap_text(hm_text, 20)
        for j, line in enumerate(hm_lines):
            draw.text((col_hm, row_y + 8 + j * 26), line, fill=hex_to_rgb(hm_color), font=font_cell)

        y += ROW_H
        # 行分割线
        draw.rectangle([PADDING, y - 8, W - PADDING, y - 7], fill=hex_to_rgb(DIVIDER))

    y += 15

    # ===== Hermes 真正优势区 =====
    draw_rounded_rect(draw, [PADDING, y, W - PADDING, y + 42], radius=8, fill=HERMES_COLOR)
    sec_text = "Hermes 真正的优势 (为什么很多人从OpenClaw转投)"
    bbox3 = draw.textbbox((0, 0), sec_text, font=font_dim)
    stw = bbox3[2] - bbox3[0]
    draw.text(((W - stw) // 2, y + 10), sec_text, fill=hex_to_rgb("#0D1117"), font=font_dim)
    y += 60

    advantages = [
        ("越用越聪明", "每次任务后自动反思、提炼经验、创建可复用Skill"),
        ("记忆深度完胜", "SQLite+全文搜索+LLM总结,多层记忆不会忘事"),
        ("更轻更灵活", "部署快、资源低、200+模型一键切换"),
        ("迁移零成本", "hermes claw migrate 一键搬家,切换几乎无痛"),
        ("专注个人成长", "适合研究型、长期个性化工作流"),
    ]

    for title_t, desc in advantages:
        # 圆点
        draw.ellipse([PADDING + 10, y + 6, PADDING + 22, y + 18], fill=hex_to_rgb(HERMES_COLOR))
        draw.text((PADDING + 32, y), title_t, fill=hex_to_rgb(TEXT_W), font=font_dim)
        draw.text((PADDING + 32, y + 28), desc, fill=hex_to_rgb(TEXT_G), font=font_cell)
        y += 58

    # ===== 底部 =====
    y += 10
    draw.rectangle([PADDING, y, W - PADDING, y + 1], fill=hex_to_rgb(DIVIDER))
    y += 15
    draw.text((PADDING, y), "数据来源：社区实测 + 官方文档 | @fwdailynews",
              fill=hex_to_rgb(TEXT_G), font=font_footer)

    img.save(output_path, "PNG", quality=95)
    print(f"✅ 对比卡片已生成: {output_path}")
    return output_path


def _wrap_text(text, max_chars):
    """简单中文换行"""
    lines = []
    while len(text) > max_chars:
        lines.append(text[:max_chars])
        text = text[max_chars:]
    if text:
        lines.append(text)
    return lines


if __name__ == "__main__":
    generate_vs_card()
