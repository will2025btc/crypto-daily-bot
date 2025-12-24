import requests
import os
import sys

def get_config(name):
    return os.getenv(name)

FOLLOWIN_API_KEY = get_config('FOLLOWIN_API_KEY')
AI_API_KEY = get_config('AI_API_KEY')
AI_BASE_URL = get_config('AI_BASE_URL')
TG_BOT_TOKEN = get_config('TG_BOT_TOKEN')
TG_CHAT_ID = get_config('TG_CHAT_ID')

def main():
    print("1. 🕵️ 正在诊断 Followin 接口...")
    headers = {'apikey': FOLLOWIN_API_KEY}
    # 先只测一个最简单的接口
    test_url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(test_url, headers=headers, timeout=15)
        print(f"📡 接口返回状态码: {r.status_code}") # 如果是 401 说明 Key 错位，403 说明被封，200 才是正常
        
        if r.status_code != 200:
            print(f"❌ Followin 拒绝了请求，错误内容: {r.text}")
            sys.exit(1)
            
        data = r.json().get('data', [])
        print(f"✅ 成功抓取到 {len(data)} 条新闻数据。")
        raw_info = str(data)[:2000]
    except Exception as e:
        print(f"💥 网络连接发生崩坏: {e}")
        sys.exit(1)

    print("2. 🤖 正在请求 AI 总结...")
    base_url = AI_BASE_URL if AI_BASE_URL.endswith('/') else AI_BASE_URL + '/'
    payload = {
        "model": "gemini-1.5-flash",
        "messages": [{"role": "user", "content": f"总结这份加密日报：{raw_info}"}]
    }
    try:
        res = requests.post(f"{base_url}chat/completions", 
                            headers={"Authorization": f"Bearer {AI_API_KEY}"}, 
                            json=payload)
        if res.status_code != 200:
            print(f"❌ AI 报错: {res.text}")
            sys.exit(1)
        report = res.json()['choices'][0]['message']['content']
        print("✅ AI 总结完成。")
    except Exception as e:
        print(f"❌ AI 环节出错: {e}")
        sys.exit(1)

    print(f"3. 🚀 正在发送到 TG 频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    tg_res = requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
    if tg_res.status_code == 200:
        print("🎉 恭喜！日报已成功发送！")
    else:
        print(f"❌ TG 发送失败，原因: {tg_res.text}")
        print("💡 提示：请检查你的 TG_CHAT_ID 是否正确，并确认 Bot 是频道管理员。")

if __name__ == "__main__":
    main()
