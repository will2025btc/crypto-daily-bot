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
    # --- 1. 抓取数据 (Followin) ---
    print("1. 🕵️ 正在抓取 Followin 数据...")
    headers = {'Authorization': FOLLOWIN_API_KEY}
    # 使用快讯接口，通常返回列表
    url = "https://api.followin.io/open/feed/news"
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            print(f"❌ Followin 接口报错: {r.status_code}")
            sys.exit(1)
        
        raw_data = r.json().get('data', [])
        
        # 【强制修正 1】数据清洗：不管是不是列表，统一转成列表处理
        if isinstance(raw_data, dict):
            news_list = [raw_data] # 如果是字典，包一层变成列表
            print("⚠️ 注意：API 返回了单条数据字典，已自动兼容。")
        elif isinstance(raw_data, list):
            news_list = raw_data   # 如果是列表，直接用
            print(f"✅ 成功获取 {len(news_list)} 条数据列表。")
        else:
            news_list = []
            print("⚠️ 数据格式未知，无法处理。")

        # 提取标题
        context = ""
        for item in news_list[:10]: # 现在这里绝对不会报错了
            title = item.get('title', '无标题')
            context += f"- {title}\n"
            
        if not context:
            print("❌ 没有提取到有效新闻标题，脚本终止。")
            sys.exit(1)

    except Exception as e:
        print(f"💥 抓取环节失败: {e}")
        sys.exit(1)

    # --- 2. AI 整理 (Google Gemini) ---
    print("2. 🤖 正在请求 Google AI (v1beta)...")
    
    # 【强制修正 2】使用 v1beta 接口 (Flash 模型必须用这个)
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={AI_API_KEY}"
    
    prompt = f"你是一个币圈资深分析师。请根据以下快讯标题，总结一份简洁精美的中文加密日报。要求：包含【今日看点】和【市场情绪】，多用Emoji，排版要适合手机阅读。内容如下：\n{context}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        res = requests.post(gemini_url, json=payload, timeout=30)
        
        if res.status_code == 200:
            res_data = res.json()
            # 兼容提取逻辑
            try:
                report = res_data['candidates'][0]['content']['parts'][0]['text']
                print("✅ AI 总结完成！")
            except (KeyError, IndexError):
                print(f"❌ AI 返回内容结构异常: {res.text}")
                sys.exit(1)
        else:
            # 打印详细错误方便调试
            print(f"❌ AI 请求被拒绝 (Code {res.status_code}): {res.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ AI 网络/解析失败: {e}")
        sys.exit(1)

    # --- 3. 推送 Telegram ---
    print(f"3. 🚀 正在推送到频道...")
    tg_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    
    try:
        # 先尝试 Markdown 格式
        payload_tg = {
            "chat_id": TG_CHAT_ID, 
            "text": report,
            "parse_mode": "Markdown"
        }
        tg_res = requests.post(tg
