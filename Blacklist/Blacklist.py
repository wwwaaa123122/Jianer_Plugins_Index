import os
import re
from Hyper import Configurator

# 加载配置文件
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

# 插件触发关键词 - 设置为"Any"表示永久触发
TRIGGHT_KEYWORD = "Any"

# 插件帮助信息
HELP_MESSAGE = f"{Configurator.cm.get_cfg().others['reminder']}查看黑名单 —> 管理用户黑名单(发送/添加（移除）黑名单 QQ号或者/添加黑名单 @用户名)"

# 黑名单文件路径
BLACKLIST_FILE = "user_blacklist.txt"

def load_blacklist():
    """加载黑名单列表"""
    blacklist = set()
    if os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    user_id = line.strip()
                    if user_id:
                        blacklist.add(user_id)
        except Exception as e:
            print(f"加载黑名单失败: {e}")
    return blacklist

def save_blacklist(blacklist):
    """保存黑名单列表"""
    try:
        with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
            for user_id in blacklist:
                f.write(f"{user_id}\n")
        return True
    except Exception as e:
        print(f"保存黑名单失败: {e}")
        return False

async def on_message(event, actions, Manager, Segments, Events, ROOT_User, reminder):
    # 只处理群消息和私聊消息
    if not isinstance(event, (Events.GroupMessageEvent, Events.PrivateMessageEvent)):
        return False
    
    user_id = str(event.user_id)
    message_text = str(event.message)
    
    # 加载黑名单
    blacklist = load_blacklist()
    
    # 检查用户是否在黑名单中 - 这是主要功能
    if user_id in blacklist:
        print(f"拦截黑名单用户 {user_id} 的消息: {message_text}")
        return True  # 拦截消息，不继续处理
    
    # 只有消息以触发词开头时才处理黑名单管理命令
    if not message_text.startswith(reminder):
        return False
    
    # 提取命令部分（去掉触发词）
    command = message_text[len(reminder):].strip()
    
    # 只有ROOT用户可以使用黑名单管理命令
    if user_id not in ROOT_User:
        return False
    
    # 处理黑名单管理命令
    if command.startswith("添加黑名单"):
        # 提取要添加到黑名单的用户ID
        target_user = None
        
        # 检查是否有@用户
        for segment in event.message:
            if isinstance(segment, Segments.At):
                target_user = str(segment.qq)
                break
        
        # 如果没有@用户，尝试从文本中提取用户ID
        if target_user is None:
            match = re.search(r"添加黑名单\s+(\d+)", command)
            if match:
                target_user = match.group(1)
        
        if target_user:
            if target_user not in blacklist:
                blacklist.add(target_user)
                if save_blacklist(blacklist):
                    response_msg = f"已添加用户 {target_user} 到黑名单"
                    if hasattr(event, 'group_id'):
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
                    else:
                        await actions.send(
                            user_id=event.user_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
                else:
                    response_msg = "添加黑名单失败，请检查日志"
                    if hasattr(event, 'group_id'):
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
                    else:
                        await actions.send(
                            user_id=event.user_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
            else:
                response_msg = "该用户已在黑名单中"
                if hasattr(event, 'group_id'):
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(Segments.Text(response_msg))
                    )
                else:
                    await actions.send(
                        user_id=event.user_id,
                        message=Manager.Message(Segments.Text(response_msg))
                    )
        else:
            response_msg = "请指定要添加到黑名单的用户ID或@相应用户\n格式：/添加黑名单 123456 或 /添加黑名单 @用户"
            if hasattr(event, 'group_id'):
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(response_msg))
                )
            else:
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(Segments.Text(response_msg))
                )
        return True
    
    elif command.startswith("移除黑名单"):
        # 提取要从黑名单移除的用户ID
        target_user = None
        
        # 检查是否有@用户
        for segment in event.message:
            if isinstance(segment, Segments.At):
                target_user = str(segment.qq)
                break
        
        # 如果没有@用户，尝试从文本中提取用户ID
        if target_user is None:
            match = re.search(r"移除黑名单\s+(\d+)", command)
            if match:
                target_user = match.group(1)
        
        if target_user:
            if target_user in blacklist:
                blacklist.remove(target_user)
                if save_blacklist(blacklist):
                    response_msg = f"已从黑名单移除用户 {target_user}"
                    if hasattr(event, 'group_id'):
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
                    else:
                        await actions.send(
                            user_id=event.user_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
                else:
                    response_msg = "移除黑名单失败，请检查日志"
                    if hasattr(event, 'group_id'):
                        await actions.send(
                            group_id=event.group_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
                    else:
                        await actions.send(
                            user_id=event.user_id,
                            message=Manager.Message(Segments.Text(response_msg))
                        )
            else:
                response_msg = "该用户不在黑名单中"
                if hasattr(event, 'group_id'):
                    await actions.send(
                        group_id=event.group_id,
                        message=Manager.Message(Segments.Text(response_msg))
                    )
                else:
                    await actions.send(
                        user_id=event.user_id,
                        message=Manager.Message(Segments.Text(response_msg))
                    )
        else:
            response_msg = "请指定要从黑名单移除的用户ID或@相应用户\n格式：/移除黑名单 123456 或 /移除黑名单 @用户"
            if hasattr(event, 'group_id'):
                await actions.send(
                    group_id=event.group_id,
                    message=Manager.Message(Segments.Text(response_msg))
                )
            else:
                await actions.send(
                    user_id=event.user_id,
                    message=Manager.Message(Segments.Text(response_msg))
                )
        return True
    
    elif command.startswith("查看黑名单"):
        if blacklist:
            blacklist_str = "\n".join([f"{i+1}. {uid}" for i, uid in enumerate(blacklist)])
            response_msg = f"当前黑名单用户 ({len(blacklist)} 个):\n{blacklist_str}"
        else:
            response_msg = "黑名单为空"
        
        if hasattr(event, 'group_id'):
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(Segments.Text(response_msg))
            )
        else:
            await actions.send(
                user_id=event.user_id,
                message=Manager.Message(Segments.Text(response_msg))
            )
        return True
    
    # 如果不是黑名单相关命令，返回False让其他插件处理
    return False