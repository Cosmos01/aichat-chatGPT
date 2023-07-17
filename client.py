import base64
import os
import openai


class Client:
    chat = openai.ChatCompletion()
    model: str = "gpt-3.5-turbo"
    conversation: str = ""
    messages: list = []
    max_tokens: int = 1000


    def __init__(self, api_key="", model="gpt-3.5-turbo", max_tokens=1000, proxy="", api_base="", api_type="open_ai", api_version=""):
        self.chat.api_key = api_key

        if proxy.strip() != "":
            openai.proxy = {'http': proxy}
        if api_base.strip() != "":
            openai.verify_ssl_certs = False
            openai.api_base = api_base
        if api_version.strip() != "":
            openai.api_version = api_version
        openai.api_type = api_type
        self.model = model
        self.max_tokens = max_tokens
        self.conversation = "default"
        self.messages = [
            {"role": "system", "content": "你是一个AI助手"},
        ]

    def load_conversation(self, conversation, message):
        self.conversation = conversation
        self.messages = message

    async def send(self, message, record=True):
        openai.api_key = self.chat.api_key
        self.messages.append({"role": "user", "content": message})
        try:
            response = await self.chat.acreate(
                model=self.model,
                engine=self.model if openai.api_type == "azure" else None,
                messages=self.messages,
                max_tokens=self.max_tokens,
                timeout=30
            )
            msg = response.choices[0].message.content.strip()
            if msg and record:
                self.messages.append({"role": "assistant", "content": msg})
            else:
                self.messages = self.messages[:-1]

            #token过长删除最早两条对话
            if response['usage']['total_tokens'] > 3800 - self.max_tokens:
                del self.messages[1:5]

            return msg.strip()
        except Exception as e:
            self.messages = self.messages[:-1]
            if "This model's maximum context length is" in str(e):
                del self.messages[1:5]
                return "对话过长，已删除部分对话"
            if "Rate limit reached for" in str(e):
                return "API请求过于频繁，请稍后再试"
            if "You exceeded your current quota" in str(e):
                return f"api key({openai.api_key[0:len(openai.api_key)-8]}********)配额已用完，请更换api key"
            return f"发生错误: {str(e).strip()}"
