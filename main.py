import requests
import os
# 1. 自动从保险箱读取秘钥
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
AI_BASE_URL = os.getenv('AI_BASE_URL')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def fetch_data(url):
    headers = {'apikey': FOLLOWIN_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return str(response.json().get('data', []))[:2000] # 截取一段防止数据太长
    return ""

def main():
    # 2. 抓取你提供的四个接口
    urls = [
        "https://api.followin.io/open/feed/news",
        "https://api.followin.io/open/feed/list/trending",
        "https://api.followin.io/open/feed/list/tag/opinions",
        "https://api.followin.io/open/feed/list/tag"
    ]
    all_data = ""
    for url in urls:
        all_data += fetch_data(url) + "\n"

    # 3. 让 AI 整理
    prompt = f"你是一个币圈专家，请根据以下原始信息总结一份简洁、有Emoji的中文日报：\n{all_data}"
    
    ai_payload = {
        "model": "gemini-1.5-flash", # 改成谷歌的模型名称
        "messages": [{"role": "user", "content": prompt}]
    }
    ai_res = requests.post(f"{AI_BASE_URL}/chat/completions", 
                           headers={"Authorization": f"Bearer {AI_API_KEY}"}, 
                           json=ai_payload)
    report = ai_res.json()['choices'][0]['message']['content']

    # 4. 发送到 TG
    requests.post(f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage", 
                  data={"chat_id": TG_CHAT_ID, "text": report})

if __name__ == "__main__":
    main()
