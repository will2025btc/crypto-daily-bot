import requests
import os
import sys

# 从 GitHub Secrets 中安全读取钥匙
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
AI_BASE_URL = os.getenv('AI_BASE_URL')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def main():
    print("1. 🕵️ 正在使用官方推荐的 Authorization 格式请求 Followin...")
    
    # --- 核心修改点：按照官方要求的 Authorization 格式 ---
    headers = {
        'Authorization': FOLLOWIN_API_KEY  # 官方说：要把 KEY 放在 Authorization 字段里
    }
    
    test_url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(test_url, headers=headers, timeout=15)
        print(f"📡 接口返回状态码: {r.status_code}")
        
        if r.status_code != 200:
            print(f"❌ 还是不成功，返回内容: {r.text}")
            print("💡 建议：如果还是 401，请确认 KEY 前面是否需要加 'Bearer '（带空格）")
            sys.exit(1)
            
        data = r.json().get('data', [])
        print(f"✅ 完美！成功抓取到 {len(data)} 条数据。")
        raw_info = str(data)[:2500] # 给 AI 更多一点素材
    except Exception as e:
        print(f"💥 网络错误: {e}")
        sys.exit(1)

    print("2. 🤖 正在请求 Google AI 整理日报...")
    # 确保 URL 正确
    base_url = AI_BASE_URL if AI_BASE_URL.endswith('/') else AI_BASE_URL + '/'
    
    ai_payload = {
        "model": "gemini-1.5-flash",
        "messages": [{"role": "user", "content": f"你是一个币圈专家。请根据这些原始信息总结一份简洁精美的中文日报，多用Emoji：\n{raw_info}"}]
    }
    
    try:
        res = requests.post(f"{base_url}chat/completions", 
                            headers={"Authorization": f"Bearer {AI_API_KEY}"}, 
                            json=ai_payload)
        report = res.json()['choices'][0]['message']['content']
        print("✅ AI 整理完成。")
    except Exception as e:
        print(f"❌ AI 环节失败: {e}")
        sys.exit(1)

    print(f"3. 🚀 正在推送到 TG 频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    tg_payload = {
        "chat_id": TG_CHAT_ID, 
        "text": report,
        "parse_mode": "Markdown" # 让日报支持加粗等排版
    }
    
    tg_res = requests.post(tg_url, data=tg_payload)
    if tg_res.status_code == 200:
        print("🎉【大功告成】日报已发出！去频道看看吧！")
    else:
        print(f"❌ TG 发送失败: {tg_res.text}")

if __name__ == "__main__":
    main()
