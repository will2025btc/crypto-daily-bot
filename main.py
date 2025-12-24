import requests
import os
import sys
import json

# 读取配置
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def main():
    # 1. 抓取数据 (这步你已经通了，保留成功逻辑)
    print("1. 🕵️ 正在抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 报错: {r.status_code}")
            sys.exit(1)
        news_data = r.json().get('data', [])
        print(f"✅ 成功拿到 {len(news_data)} 条新闻。")
        # 简化数据给 AI，节省额度
        context = ""
        for item in news_data[:8]:
            context += f"- {item.get('title', '')}\n"
    except Exception as e:
        print(f"💥 抓取环节失败: {e}")
        sys.exit(1)

    # 2. 🤖 调用 Google Gemini 原生接口 (解决 404 问题的核心)
    print("2. 🤖 正在请求 Google Gemini 整理日报...")
    # 使用谷歌最稳固的原生地址
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"你是一个币圈资深分析师。请根据以下快讯标题，总结一份精美的中文加密日报。要求：包含【今日看点】和【市场情绪】，多用Emoji，排版要适合手机阅读。内容如下：\n{context}"
            }]
        }]
    }
    
    try:
        res = requests.post(gemini_url, json=payload, timeout=30)
        res_data = res.json()
        
        if res.status_code == 200:
            # 原生格式提取内容
            report = res_data['candidates'][0]['content']['parts'][0]['text']
            print("✅ AI 整理完成！")
        else:
            print(f"❌ AI 环节报错 (代码 {res.status_code}): {res.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ AI 解析失败: {e}")
        sys.exit(1)

    # 3. 🚀 推送到 Telegram
    print(f"3. 🚀 正在发送到频道: {TG_CHAT_ID}")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        # 发送日报
        tg_res = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID, 
            "text": report
        })
        if tg_res.status_code == 200:
            print("🎉【大功告成】日报已正式发布到你的频道！")
        else:
            print(f"❌ TG 发送失败: {tg_res.text}")
            # 如果是格式问题，尝试强制纯文本发送
            requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
    except Exception as e:
        print(f"❌ TG 环节最后失败: {e}")

if __name__ == "__main__":
    main()
