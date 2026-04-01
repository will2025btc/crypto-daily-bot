import requests
import os
import sys
import json

# --- 1. 读取保险箱里的钥匙 ---
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')     # 请确保这里存的是 DeepSeek 的 Key
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN') # 这个是你刚才更新过的有效 Token

# --- 2. 核心配置 ---
# 直接使用你验证成功的频道地址
TG_CHAT_ID = '@fwdailynews' 
# DeepSeek 的官方地址
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

def main():
    print("============== 🚀 Crypto Daily 启动 ==============")

    # ---------------------------------------------------
    # 第一步：抓取 Followin 币圈头条
    # ---------------------------------------------------
    print("1. 🕵️ 正在抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    target_url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(target_url, headers=headers, timeout=20)
        if r.status_code != 200:
            print(f"❌ Followin 抓取失败 (状态码 {r.status_code})"); sys.exit(1)
            
        raw_data = r.json().get('data', [])
        
        # 智能数据清洗（防止报错）
        news_list = []
        if isinstance(raw_data, list): news_list = raw_data
        elif isinstance(raw_data, dict): news_list = [raw_data]
        
        if not news_list:
            print("❌ 没有抓取到任何新闻，流程结束。"); sys.exit(1)
            
        print(f"✅ 成功获取 {len(news_list)} 条快讯。")
        
        # 提取前 15 条标题给 AI
        context = ""
        for i, item in enumerate(news_list[:15]):
            title = item.get('title', '').replace('\n', ' ')
            context += f"{i+1}. {title}\n"

    except Exception as e:
        print(f"💥 抓取环节出错: {e}"); sys.exit(1)

    # ---------------------------------------------------
    # 第二步：DeepSeek 大脑思考 (写日报)
    # ---------------------------------------------------
    print("2. 🤖 正在召唤 DeepSeek AI 写作...")
    
    prompt = f"""
    你亦是加密货币领域的资深主编。请根据以下【原始快讯】，写一份要在 Telegram 频道发布的《Crypto Daily》日报。
    
    【写作要求】：
    1. 🎯 **核心叙事**：从快讯中提炼 1-2 个今天的市场主线（如：以太坊ETF、Meme币暴涨等）。
    2. 💰 **行情/热点**：列出 3 个值得关注的具体代币或项目。
    3. 风格：专业、简练、必须使用 Emoji (🔥, 🚀, 📉) 增加可读性。
    4. ⚠️ 风险提示：结尾必须加一句“本文不构成投资建议”。
    5. **格式**：不要使用 Markdown 的 # 标题，使用加粗（**标题**）即可。
    
    【原始快讯】：
    {context}
    """
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的币圈资讯机器人。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    headers_ai = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post(DEEPSEEK_URL, json=payload, headers=headers_ai, timeout=60)
        
        if res.status_code == 200:
            ai_content = res.json()['choices'][0]['message']['content']
            print("✅ AI 日报生成完毕！")
        else:
            print(f"❌ DeepSeek 请求失败 (Code {res.status_code})")
            print(f"原因: {res.text}")
            print("💡 提示：请检查 GitHub Secret 里的 AI_API_KEY 是不是 DeepSeek 的 Key？")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 AI 连接失败: {e}"); sys.exit(1)

    # ---------------------------------------------------
    # 第三步：Baoyu Skill 配图
    # ---------------------------------------------------
    print("3. 🎨 正在生成 Baoyu 配图...")
    try:
        from baoyu_skill import generate_text_card, send_photo_to_telegram
        # 从 AI 日报中提取关键行作为卡片内容
        lines = [l.strip() for l in ai_content.split('\n') if l.strip()]
        card_lines = lines[:10]  # 取前10行作为卡片内容
        card_title = card_lines[0] if card_lines else "Crypto Daily"
        card_body = card_lines[1:] if len(card_lines) > 1 else ["暂无内容"]

        card_path = generate_text_card(card_title, card_body, output_path="/tmp/daily_card.png")
        print("✅ 配图生成完毕！")
    except Exception as e:
        print(f"⚠️ 配图生成失败（不影响日报发送）: {e}")
        card_path = None

    # ---------------------------------------------------
    # 第四步：发送到 Telegram 频道
    # ---------------------------------------------------
    print(f"4. 🚀 正在发送到频道 {TG_CHAT_ID}...")

    # 先发配图（如果有）
    if card_path:
        try:
            send_photo_to_telegram(card_path, caption="📊 今日速览",
                                   bot_token=TG_BOT_TOKEN, chat_id=TG_CHAT_ID)
        except Exception as e:
            print(f"⚠️ 配图发送失败: {e}")

    # 再发文字日报
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

    # 尝试 Markdown 发送（好看）
    data_md = {"chat_id": TG_CHAT_ID, "text": ai_content, "parse_mode": "Markdown"}
    res_md = requests.post(tg_url, data=data_md)

    if res_md.status_code == 200:
        print("🎉【完美成功】Markdown 格式日报已发出！")
    else:
        print("⚠️ Markdown 发送失败，尝试纯文本兜底...")
        # 失败则发送纯文本（保底）
        data_txt = {"chat_id": TG_CHAT_ID, "text": ai_content}
        requests.post(tg_url, data=data_txt)
        print("🎉【保底成功】纯文本日报已发出！")

if __name__ == "__main__":
    main()
