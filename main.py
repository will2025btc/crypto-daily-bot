import requests
import os
import sys
import json

# 安全读取配置
def get_config(name):
    return os.getenv(name)

FOLLOWIN_API_KEY = get_config('FOLLOWIN_API_KEY')
AI_API_KEY = get_config('AI_API_KEY')
AI_BASE_URL = get_config('AI_BASE_URL')
TG_BOT_TOKEN = get_config('TG_BOT_TOKEN')
TG_CHAT_ID = get_config('TG_CHAT_ID')

def main():
    # 1. 抓取数据（这一步你已经成功了！）
    print("1. 🕵️ 正在抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    test_url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(test_url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 报错: {r.status_code}, {r.text}")
            sys.exit(1)
        data = r.json().get('data', [])
        print(f"✅ 成功抓取到 {len(data)} 条数据。")
        # 将数据转为更易读的文本
        raw_info = json.dumps(data, ensure_ascii=False)[:3000]
    except Exception as e:
        print(f"💥 数据抓取环节崩坏: {e}")
        sys.exit(1)

    # 2. 🤖 请求 AI 总结（修复报错的关键）
    print("2. 🤖 正在请求 Google AI 整理日报...")
    base_url = AI_BASE_URL if AI_BASE_URL.endswith('/') else AI_BASE_URL + '/'
    
    # 构造请求
    ai_payload = {
        "model": "gemini-1.5-flash",
        "messages": [
            {
                "role": "user", 
                "content": f"你是一个币圈专家。请根据以下原始信息总结一份简洁精美的中文日报，包含【今日看点】和【热门代币】，多用Emoji，排版美观。原始信息：\n{raw_info}"
            }
        ]
    }
    
    try:
        res = requests.post(
            f"{base_url}chat/completions", 
            headers={"Authorization": f"Bearer {AI_API_KEY}"}, 
            json=ai_payload,
            timeout=30
        )
        
        # 调试：打印 AI 的原始返回，万一又报错我们可以看到原因
        print(f"📡 AI 响应状态码: {res.status_code}")
        
        full_response = res.json()
        
        # 安全地提取内容，防止 list indices 错误
        if "choices" in full_response and len(full_response["choices"]) > 0:
            report = full_response["choices"][0]["message"]["content"]
            print("✅ AI 总结完成！")
        else:
            print(f"❌ AI 返回格式异常: {full_response}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ AI 环节失败: {e}")
        sys.exit(1)

    # 3. 🚀 推送到 Telegram
    print(f"3. 🚀 正在推送到频道: {TG_CHAT_ID}")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        tg_res = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID, 
            "text": report,
            "parse_mode": "Markdown" 
        })
        if tg_res.status_code == 200:
            print("🎉【大功告成】日报已发出！快去 TG 频道看看吧！")
        else:
            # 如果 Markdown 格式导致失败，尝试发送纯文本
            print("⚠️ Markdown 发送失败，正在尝试纯文本模式...")
            requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
            print("🎉【成功】日报已以纯文本格式发出！")
    except Exception as e:
        print(f"❌ TG 推送最后环节失败: {e}")

if __name__ == "__main__":
    main()
