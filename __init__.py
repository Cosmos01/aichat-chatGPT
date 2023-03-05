import configparser
import json
import os

class Config:
    _config = configparser.ConfigParser()
    api_keys: list = []  # api key
    model: str = "gpt-3.5-turbo"  # 模型
    record: bool = True  # 是否记录对话
    conversations: dict = {}  # 会话列表
    groups: dict = {}  # 群组列表
    interval: int = 5  # 存档间隔
    max_tokens: int = 1000  # 最大字符数
    proxy: str = ""  # 代理

    def __init__(self):
        self._config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding='utf-8')
        self.load_conversations()
        api_keys = self._config.get("OPTION", "api_key", fallback="")
        self.api_keys = api_keys.split(",")
        self.model = self._config.get("OPTION", "model", fallback="gpt-3.5-turbo")
        self.record = self._config.getboolean("OPTION", "record", fallback=True)
        self.interval = self._config.getint("OPTION", "interval", fallback=5)
        self.max_tokens = self._config.getint("OPTION", "max_tokens", fallback=1000)
        self.proxy = self._config.get("OPTION", "proxy", fallback="")
        items = self._config.items("GROUP")
        for item in items:
            if item[1] not in self.conversations:
                self.groups[item[0]] = item[1]
            else:
                self.groups[item[0]] = "default"

    def save_conversations(self):
        with open(os.path.join(os.path.dirname(__file__), 'conversations.json'), 'w', encoding='utf-8') as f:
            json.dump(self.conversations, f, ensure_ascii=False, indent=4)

    def load_conversations(self):
        with open(os.path.join(os.path.dirname(__file__), 'conversations.json'), 'r', encoding='utf-8') as f:
            self.conversations = json.load(f)

    def save_config(self):
        for group in self.groups:
            if self.groups[group] not in self.conversations:
                self._config.set("GROUP", group, "default")
            else:
                self._config.set("GROUP", group, self.groups[group])
        self._config.set("OPTION", "record", str(self.record).lower())
        with open(os.path.join(os.path.dirname(__file__), 'config.ini'), 'w', encoding='utf-8') as f:
            self._config.write(f)
