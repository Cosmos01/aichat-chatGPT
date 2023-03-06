import base64
import os
import openai


class Client:
    chat = openai.ChatCompletion()
    model: str = "gpt-3.5-turbo"
    conversation: str = ""
    messages: list = []
    max_tokens: int = 1000

    def __init__(self, api_key="", model="gpt-3.5-turbo", max_tokens=1000, proxy=""):
        self.chat.api_key = api_key
        if proxy.strip() != "":
            openai.proxy = {'http': proxy,'https': proxy}
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
                messages=self.messages,
                max_tokens=self.max_tokens,
                timeout=30
            )
            msg = response.choices[0].message.content.strip()
            if msg and record:
                self.messages.append({"role": "assistant", "content": msg})
            else:
                self.messages = self.messages[:-1]

            #token过长删除前一条对话
            if response['usage']['total_tokens'] > 4096 - self.max_tokens:
                del self.messages[1:5]

            return msg.strip()
        except Exception as e:
            self.messages = self.messages[:-1]
            if "This model's maximum context length is 4096 tokens" in str(e):
                del self.messages[1:5]
                return "对话过长，已删除部分对话"
            if "Rate limit reached for" in str(e):
                return "API请求过于频繁，请稍后再试"
            return f"发生错误: {str(e).strip()}"
