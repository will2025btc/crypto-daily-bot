import requests
import os
import sys

# 获取配置并打印检查（不会打印出真正的KEY，请放心）
def get_config(name):
    val = os.getenv(name)
    if not val:
        print(f"❌ 错误：缺少保险箱钥匙 {name}")
    return val

FOLLOWIN_API_KEY = get_config('FOLLOWIN_API_KEY')
AI_API_KEY = get_config('AI_API_KEY')
AI_BASE_URL = get_config('AI_BASE_URL')
TG_BOT_TOKEN = get_config('TG_BOT_TOKEN')
TG_CHAT_ID = get_config('TG_CHAT_ID')

def main():
    # 1. 抓取数据
    print("正在从 Followin 抓取数据...")
    headers = {'apikey': FOLLOWIN_API_KEY}
    urls = [
        "https://api.followin.io/open/feed/news",
        "https://api.followin.io/open/feed/list/trending"
    ]
    raw_info = ""
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                raw_info += str(r.json().get('data', []))[:1000]
        except Exception as e:
            print(f"⚠️ 抓取 {url} 出错: {e}")

    if len(raw_info) < 100:
        print("❌ 抓取到的数据太少，请检查 Followin API Key 是否正确。")
        sys.exit(1)

    # 2. AI 总结
    print("正在请求 AI 整理日报...")
    # 确保 URL 结尾有斜杠
    base_url = AI_BASE_URL if AI_BASE_URL.endswith('/') else AI_BASE_URL + '/'
    
    payload = {
        "model": "gemini-1.5-flash",
        "messages": [{"role": "user", "content": f"总结这份加密日报：{raw_info}"}]
    }
    try:
        res = requests.post(f"{base_url}chat/completions", 
                            headers={"Authorization": f"Bearer {AI_API_KEY}"}, 
                            json=payload)
        res.raise_for_status()
        report = res.json()['choices'][0]['message']['content']
        print("✅ AI 总结完成")
    except Exception as e:
        print(f"❌ AI 环节出错: {e}")
        if 'res' in locals(): print(f"返回内容: {res.text}")
        sys.exit(1)

    # 3. 发送 TG
    print(f"正在发送到频道 {TG_CHAT_ID}...")
    try:
        tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        tg_res = requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
        tg_res.raise_for_status()
        print("🎉 发送成功！")
    except Exception as e:
        print(f"❌ TG 发送失败: {e}")
        if 'tg_res' in locals(): print(f"返回内容: {tg_res.text}")
        sys.exit(1)

if __name__ == "__main__":
    main()
