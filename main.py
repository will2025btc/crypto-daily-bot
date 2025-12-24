import requests
import os
import sys
import json
import time

# --- 配置读取 ---
FOLLOWIN_API_KEY = os.getenv('FOLLOWIN_API_KEY')
AI_API_KEY = os.getenv('AI_API_KEY')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

def get_ai_summary(context):
    """
    尝试多个模型，直到成功为止。
    解决 404 Model Not Found 问题。
    """
    # 备选模型列表：优先用 Flash，不行就用 Pro
    models_to_try = [
        "gemini-1.5-flash", 
        "gemini-1.5-flash-latest",
        "gemini-pro"
    ]
    
    base_url = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent?key={}"
    
    prompt = f"你是一个币圈资深分析师。请根据以下快讯标题，总结一份中文加密日报。要求：包含【今日看点】和【市场情绪】，多用Emoji，排版要适合手机阅读。内容如下：\n{context}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model in models_to_try:
        print(f"🤖 正在尝试使用模型: {model} ...")
        try:
            target_url = base_url.format(model, AI_API_KEY)
            res = requests.post(target_url, json=payload, timeout=30)
            
            if res.status_code == 200:
                # 成功！提取内容
                try:
                    text = res.json()['candidates'][0]['content']['parts'][0]['text']
                    print(f"✅ 模型 {model} 调用成功！")
                    return text
                except Exception as e:
                    print(f"⚠️ 模型 {model} 返回格式异常: {e}")
            elif res.status_code == 404:
                print(f"❌ 模型 {model} 不存在 (404)，尝试下一个...")
            else:
                print(f"❌ 模型 {model} 报错 (Code {res.status_code}): {res.text}")
                
        except Exception as e:
            print(f"💥 请求 {model} 发生网络错误: {e}")
        
        # 失败了，休息1秒再试下一个
        time.sleep(1)

    # 如果所有模型都失败
    print("💀 所有 AI 模型都尝试失败。")
    sys.exit(1)

def main():
    # --- 1. 抓取 Followin 数据 ---
    print("1. 🕵️ 正在抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 接口报错: {r.status_code}")
            sys.exit(1)
            
        raw_data = r.json().get('data', [])
        
        # 数据清洗（防弹逻辑）
        news_list = []
        if isinstance(raw_data, dict):
            print("⚠️ 自动兼容：将单条字典转换为列表。")
            news_list = [raw_data]
        elif isinstance(raw_data, list):
            print(f"✅ 成功获取 {len(raw_data)} 条数据列表。")
            news_list = raw_data
        else:
            print(f"❌ 数据格式异常: {type(raw_data)}")
            sys.exit(1)

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

    # --- 2. 智能 AI 处理 (自动切换模型) ---
    print("2. 🤖 正在请求 AI...")
    report = get_ai_summary(context)

    # --- 3. 推送 Telegram ---
    print(f"3. 🚀 正在推送到频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        # 尝试 Markdown
        tg_res = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID, 
            "text": report,
            "parse_mode": "Markdown"
        })
        
        if tg_res.status_code == 200:
            print("🎉【大功告成】日报已发送！")
        else:
            print(f"⚠️ Markdown 发送失败，切换纯文本模式...")
            requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
            print("🎉【纯文本已发】日报已送达！")
            
    except Exception as e:
        print(f"❌ TG 发送失败: {e}")

if __name__ == "__main__":
    main()
