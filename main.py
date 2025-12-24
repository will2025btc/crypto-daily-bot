import requests
import os
import sys

# 读取配置
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
# 这里填你确定的频道地址
TARGET_CHANNEL = '@fwdailynews'

def main():
    print("============== 🕵️‍♂️ 侦探模式启动 ==============")
    
    # --- 1. 查户口：这个 Token 到底是谁的？ ---
    print("1. 正在检查机器人身份...")
    try:
        me_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/getMe"
        me_res = requests.get(me_url).json()
        
        if me_res.get('ok'):
            bot_username = me_res['result']['username']
            bot_name = me_res['result']['first_name']
            print(f"✅ 身份确认成功！")
            print(f"🤖 机器人用户名 (ID): @{bot_username}")
            print(f"👤 机器人昵称 (Name): {bot_name}")
            print("-------------------------------------------")
            print("👉 请务必检查：这个 @名字 和你在频道里添加的管理员是同一个吗？")
            print("-------------------------------------------")
        else:
            print(f"❌ Token 无效！Telegram 拒绝识别。")
            print(f"错误信息: {me_res}")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 连接 Telegram 失败: {e}")
        sys.exit(1)

    # --- 2. 试开门：强制发送一条测试消息 ---
    print(f"\n2. 正在尝试向频道 {TARGET_CHANNEL} 发送测试消息...")
    
    send_url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TARGET_CHANNEL,
        "text": "🔍 这是一条测试消息。\n如果你看到了它，说明【频道地址】和【机器人权限】都没问题！"
    }
    
    try:
        r = requests.post(send_url, json=payload)
        response_json = r.json()
        
        print(f"📡 Telegram 服务器返回的状态码: {r.status_code}")
        print(f"📝 Telegram 返回的完整回执:\n{response_json}")
        
        if response_json.get('ok'):
            print("\n🎉 结论：发送成功！请现在去频道看一眼。")
        else:
            print("\n❌ 结论：发送失败！")
            error_desc = response_json.get('description', '未知错误')
            print(f"💀 失败原因: {error_desc}")
            
            # 智能分析错误原因
            if "chat not found" in error_desc:
                print("💡 分析：频道地址写错了，或者机器人还没被拉进频道。")
            elif "Unauthorized" in error_desc:
                print("💡 分析：Token 可能是旧的，或者机器人被删除了。")
            elif "Rights" in error_desc:
                print("💡 分析：机器人虽然在频道里，但没有【发布消息】的管理员权限。")

    except Exception as e:
        print(f"💥 发送环节报错: {e}")

    print("============== 侦探模式结束 ==============")

if __name__ == "__main__":
    main()
