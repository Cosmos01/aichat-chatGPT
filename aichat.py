import os
import random
import re
import string
import json
import time
from hoshino.aiorequests import run_sync_func
from hoshino import Service, priv
from hoshino.typing import CQEvent
from .chatGPT import ChatGPT

sv = Service('人工智障', enable_on_default=False)

black_word = ['今天我是什么少女', 'ba来一井']  # 如果有不想触发的词可以填在这里

cq_code_pattern = re.compile(r'\[CQ:\w+,.+\]')
CONFIG_PATH = os.path.dirname(__file__)
flag = False
conversation = {}


def set_flag(b):
    global flag
    flag = b


def get_auth_config() -> dict:
    try:
        with open(os.path.join(CONFIG_PATH, "auth.json"), "r") as auth_config:
            auth_config = json.load(auth_config)
    except Exception as e:
        print(e)
    return auth_config


# 初始化bot
def get_api(session_token=None):
    set_flag(False)
    auth_config = get_auth_config()
    if session_token:
        auth_config["session_token"] = session_token
    return ChatGPT(session_token=auth_config.get("session_token"),
                   email=auth_config.get("email"),
                   password=auth_config.get("password"),
                   auth_type=auth_config.get("auth_type"),
                   proxy=auth_config.get("proxy"),
                   user_data_dic=auth_config.get("user_data_dic"),
                   profile_directory=auth_config.get("profile_directory"),
                   conversation_id=auth_config.get("conversation_id") if auth_config.get("conversation_id") else "",
                   twocaptcha_apikey=auth_config.get("twocaptcha_apikey") if auth_config.get("twocaptcha_apikey") else "",
                   login_cookies_path=auth_config.get("login_cookies_path") if auth_config.get("login_cookies_path") else "",
                   )


try:
    api = get_api()
except Exception as e:
    print(e)


async def get_chat_response(prompt):
    global flag
    if flag:
        return "等待上一对话完成中"
    flag = True
    try:
        resp = await run_sync_func(api.send_message, prompt)
        flag = False
        return resp['message']
    except Exception as e:
        print(e)
        flag = False
        err = str(e) if len(str(e)) < 133 else str(e)[:133]
        return f"发生错误: {err}"


@sv.on_prefix(('人格初始化', '猫娘初始化'))
async def init_neko(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    set_flag(False)
    init_msg = str(ev.message.extract_plain_text()).strip()
    if init_msg == "":
        with open(os.path.join(CONFIG_PATH, "init_msg.txt"), "r", encoding="utf-8") as f:
            init_msg = f.read()

    try:
        api.reset_conversation()
        msg = (await get_chat_response(init_msg)).strip()
        if msg:
            await bot.send(ev, msg)
    except Exception as err:
        print(err)


@sv.on_fullmatch('初始化人工智障')
async def init_ai(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    try:
        api.reset_conversation()
        set_flag(False)
    except Exception as err:
        await bot.send(ev, err)


@sv.on_prefix('更新凭证')
async def init_api(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    input_token = str(ev.message.extract_plain_text()).strip()
    session_token = input_token if len(input_token) > 50 else None
    global api
    try:
        api.__del__()
        api = get_api(session_token)
    except Exception as err:
        await bot.send(ev, err)


@sv.on_message('group')
async def ai_reply(bot, context):
    msg = str(context['message'])
    if msg.startswith(f'[CQ:at,qq={context["self_id"]}]'):
        text = re.sub(cq_code_pattern, '', msg).strip()
        if text == '' or text in black_word:
            return
        try:
            msg = (await get_chat_response(text)).strip()
            if msg:
                await bot.send(context, msg, at_sender=False)
        except Exception as err:
            print(err)


@sv.on_prefix('/t')
async def ai_reply_prefix(bot, ev: CQEvent):
    text = str(ev.message.extract_plain_text()).strip()
    if text == '' or text in black_word:
        return
    try:
        msg = (await get_chat_response(text)).strip()
        if msg:
            await bot.send(ev, msg)
    except Exception as err:
        print(err)
