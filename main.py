import requests
import os
import sys
import json

# 安全读取 Secrets
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def main():
    # --- 第一步：抓取数据 ---
    print("1. 🕵️ 开始抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 接口报错: {r.status_code}")
            sys.exit(1)
        
        full_json = r.json()
        news_data = full_json.get('data', [])
        
        # 兼容性处理：防止 unhashable type: 'slice' 报错
        context = ""
        if isinstance(news_data, list):
            print(f"✅ 成功拿到 {len(news_data)} 条新闻列表。")
            for item in news_data[:10]: # 取前10条
                title = item.get('title', '无标题')
                context += f"- {title}\n"
        elif isinstance(news_data, dict):
            print("✅ 拿到的是单条数据字典。")
            context = news_data.get('title', '无标题内容')
        else:
            context = str(news_data)

    except Exception as e:
        print(f"💥 抓取环节失败: {e}")
        sys.exit(1)

    # --- 第二步：调用 Google AI (使用原生最稳地址) ---
    print("2. 🤖 正在请求 Google AI 整理日报...")
    # 使用 v1 版本和更稳固的请求地址
    gemini_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    
    prompt = f"你是一个币圈资深分析师。请根据以下快讯标题，总结一份简洁精美的中文加密日报。要求：包含【今日看点】和【市场情绪】，多用Emoji，排版要适合手机阅读。内容如下：\n{context}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        res = requests.post(gemini_url, json=payload, timeout=30)
        if res.status_code == 200:
            res_data = res.json()
            report = res_data['candidates'][0]['content']['parts'][0]['text']
            print("✅ AI 总结完成！")
        else:
            print(f"❌ AI 报错 (代码 {res.status_code}): {res.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ AI 解析失败: {e}")
        sys.exit(1)

    # --- 第三步：推送到 Telegram ---
    print(f"3. 🚀 正在发送到 TG 频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        tg_res = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID, 
            "text": report
        })
        if tg_res.status_code == 200:
            print("🎉【全线通车】日报已成功发布到你的频道！")
        else:
            print(f"❌ TG 发送失败: {tg_res.text}")
            # 备选方案：尝试纯文本
            requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
    except Exception as e:
        print(f"❌ TG 环节最后失败: {e}")

if __name__ == "__main__":
    main()
