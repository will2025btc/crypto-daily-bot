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
    # --- 1. 抓取 Followin 数据 ---
    print("1. 🕵️ 正在抓取 Followin 数据...")
    
    # 官方要求的 Authorization 格式
    headers = {'Authorization': FOLLOWIN_API_KEY}
    url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 接口报错 (状态码 {r.status_code}): {r.text}")
            sys.exit(1)
        
        # 获取原始数据
        raw_data = r.json().get('data', [])
        
        # 【核心修复】自动识别数据格式，防止报错
        news_list = []
        if isinstance(raw_data, dict):
            print("⚠️ 检测到单条数据字典，正在自动转换为列表...")
            news_list = [raw_data]
        elif isinstance(raw_data, list):
            print(f"✅ 成功获取 {len(raw_data)} 条新闻列表。")
            news_list = raw_data
        else:
            print(f"❌ 数据格式异常: {type(raw_data)}")
            sys.exit(1)

        # 提取标题，准备发给 AI
        context = ""
        for item in news_list[:10]: # 现在这里绝对安全了
            title = item.get('title', '无标题')
            context += f"- {title}\n"
            
        if not context:
            print("❌ 未提取到有效内容，脚本停止。")
            sys.exit(1)

    except Exception as e:
        print(f"💥 抓取环节发生意外: {e}")
        sys.exit(1)

    # --- 2. 请求 Google Gemini (修复 404 问题) ---
    print("2. 🤖 正在请求 Google AI (使用 v1beta 接口)...")
    
    # 【核心修复】必须使用 v1beta 版本才能调用 gemini-1.5-flash
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    
    prompt = f"你是一个币圈资深分析师。请根据以下快讯标题，总结一份中文加密日报。要求：包含【今日看点】和【市场情绪】，多用Emoji，排版要适合手机阅读。内容如下：\n{context}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        res = requests.post(gemini_url, json=payload, timeout=30)
        
        if res.status_code == 200:
            try:
                # 尝试提取 AI 回复
                report = res.json()['candidates'][0]['content']['parts'][0]['text']
                print("✅ AI 总结完成！")
            except Exception as e:
                print(f"❌ AI 返回结构解析失败: {e}")
                print(f"完整返回: {res.text}")
                sys.exit(1)
        else:
            print(f"❌ AI 请求被拒绝 (Code {res.status_code}): {res.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ AI 网络请求失败: {e}")
        sys.exit(1)

    # --- 3. 推送到 Telegram ---
    print(f"3. 🚀 正在推送到频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        # 优先尝试 Markdown 格式
        tg_res = requests.post(tg_url, data={
            "chat_id": TG_CHAT_ID, 
            "text": report,
            "parse_mode": "Markdown"
        })
        
        if tg_res.status_code == 200:
            print("🎉【大功告成】日报已发送！")
        else:
            print(f"⚠️ Markdown 发送失败，自动切换纯文本模式...")
            requests.post(tg_url, data={"chat_id": TG_CHAT_ID, "text": report})
            print("🎉【纯文本已发】日报已送达！")
            
    except Exception as e:
        print(f"❌ TG 发送环节失败: {e}")

if __name__ == "__main__":
    main()
