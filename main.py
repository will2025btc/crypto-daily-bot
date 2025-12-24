import requests
import os
import sys
import json

# --- 配置读取 ---
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def main():
    # ==========================
    # 第一步：抓取 Followin 数据 (已验证成功)
    # ==========================
    print("1. 🕵️ 正在抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 接口报错: {r.status_code}")
            sys.exit(1)
            
        raw_data = r.json().get('data', [])
        
        # 你的“防弹”清洗逻辑
        news_list = []
        if isinstance(raw_data, dict):
            news_list = [raw_data]
        elif isinstance(raw_data, list):
            news_list = raw_data
        else:
            news_list = []

        print(f"✅ 成功获取 {len(news_list)} 条数据。")

        # 提取标题
        context = ""
        for item in news_list[:10]:
            title = item.get('title', '无标题')
            context += f"- {title}\n"
            
        if not context:
            print("❌ 未提取到有效内容。")
            sys.exit(1)

    except Exception as e:
        print(f"💥 抓取环节失败: {e}")
        sys.exit(1)

    # ==========================
    # 第二步：调用 AI (切换为 DeepSeek)
    # ==========================
    print("2. 🤖 正在请求 DeepSeek AI...")
    
    # DeepSeek 标准接口地址
    ai_url = "https://api.deepseek.com/chat/completions"
    
    prompt = f"你是一个币圈资深分析师。请根据以下快讯标题，总结一份中文加密日报。要求：包含【今日看点】和【市场情绪】，多用Emoji，排版要适合手机阅读。内容如下：\n{context}"
    
    payload = {
        "model": "deepseek-chat",  # 指定模型
        "messages": [
            {"role": "system", "content": "你是一个专业的加密货币分析师。"},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    headers_ai = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # 发送请求
        res = requests.post(ai_url, json=payload, headers=headers_ai, timeout=60)
        
        if res.status_code == 200:
            ai_data = res.json()
            if "choices" in ai_data and len(ai_data["choices"]) > 0:
                report = ai_data["choices"][0]["message"]["content"]
                print("✅ AI 总结完成！")
            else:
                print(f"❌ AI 返回内容为空: {res.text}")
                sys.exit(1)
        else:
            print(f"❌ AI 请求被拒绝 (Code {res.status_code}): {res.text}")
            print("💡 提示：请检查 GitHub Secret 里的 AI_API_KEY 是否更新为 DeepSeek 的 Key。")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 AI 网络请求失败: {e}")
        sys.exit(1)

    # ==========================
    # 第三步：推送 Telegram
    # ==========================
    print(f"3. 🚀 正在推送到频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        # 优先 Markdown
        tg_res = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID, 
            "text": report,
            "parse_mode": "Markdown"
        })
        
        if tg_res.status_code == 200:
            print("🎉【大功告成】日报已发送！")
        else:
            print("⚠️ Markdown 发送失败，切换纯文本模式...")
            requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
            print("🎉【纯文本已发】日报已送达！")
            
    except Exception as e:
        print(f"❌ TG 发送失败: {e}")

if __name__ == "__main__":
    main()
