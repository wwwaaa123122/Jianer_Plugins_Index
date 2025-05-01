from Hyper import Configurator
import json
import os
import random
from datetime import datetime
import httpx

# 加载配置
Configurator.cm = Configurator.ConfigManager(Configurator.Config(file="config.json").load_from_file())

TRIGGHT_KEYWORD = "Any"
HELP_MESSAGE = f"签到 -> 签到获取积分和好感度"

DEFAULT_CONFIG = {
    "好感度": {
        "min": 1,
        "max": 10
    },
    "积分": {
        "min": 10,
        "max": 100
    },
    "数据存储路径": "./data/check_in/",
    "总计数据文件": "total_check_in.json",
    "每日数据文件": "daily_check_in.json",
    "用户数据文件": "user_data.json"
}

class CheckInManager:
    def __init__(self):
        self.config = self._load_or_create_config()
        self.total_data = self._load_or_create_total_data()
        self.daily_data = None
        self.user_data = self._load_or_create_user_data()
        self.last_date = None
    
    def _load_or_create_config(self):
        """加载或创建配置文件"""
        config_path = "./data/check_in/check_in_config.json"
        if not os.path.exists(config_path):
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_or_create_total_data(self):
        """加载或创建总计签到数据"""
        os.makedirs(self.config["数据存储路径"], exist_ok=True)
        path = os.path.join(self.config["数据存储路径"], self.config["总计数据文件"])
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_or_create_daily_data(self):
        """加载或创建每日签到数据，每天自动刷新"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        if self.last_date != today or self.daily_data is None:
            self.daily_data = {"count": 0, "users": []}
            self.last_date = today
            self._save_daily_data()
            print(f"[签到系统]创建新的每日签到数据: {today}")
            
        return self.daily_data

    def _load_or_create_user_data(self):
        """加载或创建用户数据"""
        path = os.path.join(self.config["数据存储路径"], "user_data.json")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _save_total_data(self):
        """保存总计签到数据"""
        path = os.path.join(self.config["数据存储路径"], self.config["总计数据文件"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.total_data, f, ensure_ascii=False, indent=2)

    def _save_daily_data(self):
        """保存每日签到数据"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            path = os.path.join(self.config["数据存储路径"], 
                              f"{today}_{self.config['每日数据文件']}")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.daily_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[签到系统]保存每日数据出错: {e}")

    def _save_user_data(self):
        """保存用户数据"""
        path = os.path.join(self.config["数据存储路径"], "user_data.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.user_data, f, ensure_ascii=False, indent=2)

    def check_in(self, user_id: str) -> dict:
        """处理用户签到"""
        self.daily_data = self._load_or_create_daily_data()
        
        if user_id in self.daily_data["users"]:
            return {"success": False, "message": "今天已经签到过了哦~"}

        self.daily_data["count"] += 1
        self.daily_data["users"].append(user_id)
        self._save_daily_data()

        if user_id not in self.total_data:
            self.total_data[user_id] = {"total_days": 0}
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "好感度": 0,
                "积分": 0
            }
        
        favor = random.randint(self.config["好感度"]["min"], self.config["好感度"]["max"])
        points = random.randint(self.config["积分"]["min"], self.config["积分"]["max"])
        
        self.total_data[user_id]["total_days"] += 1
        self.user_data[user_id]["好感度"] += favor
        self.user_data[user_id]["积分"] += points
        
        self._save_total_data()
        self._save_user_data()

        rewards = {
            "rank": self.daily_data["count"],
            "favor": favor,
            "points": points,
            "total_days": self.total_data[user_id]["total_days"],
            "total_favor": self.user_data[user_id]["好感度"],
            "total_points": self.user_data[user_id]["积分"]
        }

        return {"success": True, "rewards": rewards}

check_in_manager = CheckInManager()

async def on_message(event, actions, Manager, Segments):
    if not hasattr(event, 'message'):
        return False
        
    message_content = ""
    if isinstance(event.message, list):
        message_content = str(event.message[0])
    else:
        message_content = str(event.message)
        
    if message_content != "签到":
        return False
    
    try:
        user_info = await actions.get_stranger_info(event.user_id)
        user_nickname = user_info.data.raw["nickname"]
        
        result = check_in_manager.check_in(str(event.user_id))
        
        if not result["success"]:
            await actions.send(
                group_id=event.group_id,
                message=Manager.Message(
                    Segments.At(event.user_id),
                    Segments.Text(result["message"])
                )
            )
            return True

        hitokoto_response = httpx.get("https://international.v1.hitokoto.cn/")
        try:
            hitokoto_text = f"{hitokoto_response.json()['hitokoto']} —— {hitokoto_response.json()['from_who']}, {hitokoto_response.json()['from']}"
        except:
            hitokoto_text = "今天也要元气满满哦~"

        rewards = result["rewards"]
        message = f'''
签到成功，你是第{rewards["rank"]}名签到的小伙伴
好感度：+{rewards["favor"]}
奖励积分：{rewards["points"]}
累计好感：{rewards["total_favor"]}
累计总计：{rewards["total_points"]}
累计签到：{rewards["total_days"]}天
——————————
{hitokoto_text}'''

        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Image(f"http://q2.qlogo.cn/headimg_dl?dst_uin={event.user_id}&spec=640"),
                Segments.Text(f"昵称："),
                Segments.At(event.user_id),
                Segments.Text(message)
            )
        )
        return True
        
    except Exception as e:
        await actions.send(
            group_id=event.group_id,
            message=Manager.Message(
                Segments.Text(f"签到出错了: {e}")
            )
        )
        return True

print("[Xiaoyi_QQ]签到插件已加载")