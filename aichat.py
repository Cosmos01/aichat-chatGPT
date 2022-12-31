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


def init_conversation():
    global conversation
    try:
        with open(os.path.join(CONFIG_PATH, "conversation.json"), "r", encoding='utf-8') as conversation_config:
            conversation = json.load(conversation_config)
    except Exception as e:
        conversation = {}
        print(e)


def save_conversation():
    try:
        with open(os.path.join(CONFIG_PATH, "conversation.json"), "w", encoding='utf-8') as conversation_config:
            json.dump(conversation, conversation_config)
    except Exception as e:
        print(e)


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
                   conversation_id=auth_config.get("conversation_id") if auth_config.get("conversation_id") else "",
                   email=auth_config.get("email"),
                   password=auth_config.get("password"),
                   auth_type=auth_config.get("auth_type"),
                   proxy=auth_config.get("proxy"),
                   captcha_solver=auth_config.get("captcha_solver") if auth_config.get(
                       "captcha_solver") else "pypasser",
                   solver_apikey=auth_config.get("solver_apikey") if auth_config.get("solver_apikey") else "",
                   login_cookies_path=auth_config.get("login_cookies_path") if auth_config.get(
                       "login_cookies_path") else "",
                   user_data_dic=auth_config.get("user_data_dic"),
                   profile_directory=auth_config.get("profile_directory"),
                   )


try:
    api = get_api()
    init_conversation()
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


@sv.on_fullmatch('重新组织语言')
async def try_again(bot, ev: CQEvent):
    global flag
    if flag:
        return "等待上一对话完成中"
    flag = True
    try:
        msg = await run_sync_func(api.try_again)
        if msg:
            await bot.send(ev, msg.strip())
    except Exception as e:
        print(e)
        await bot.send(ev, f"发生错误：{e}")
    flag = False


@sv.on_prefix(('人格初始化', '猫娘初始化'))
async def init_neko(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    set_flag(False)
    name = str(ev.message.extract_plain_text()).strip()
    if name == "" or len(name) > 36:
        name = "Default"
    with open(os.path.join(CONFIG_PATH, "init_msg.txt"), "r", encoding="utf-8") as f:
        init_msg = f.read()
    try:
        api.reset_conversation()
        msg = (await get_chat_response(init_msg)).strip()
        if msg:
            await bot.send(ev, msg)
            id = api.get_new_conversation_id()
            if id == "":
                await bot.send(ev, "获取会话id失败")
                return
            conversation[name] = id
            save_conversation()
            await bot.send(ev, f"人格初始化成功：\n{name}:{id}")
    except Exception as err:
        print(err)


@sv.on_fullmatch(('初始化会话', '初始化人工智障'))
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
    await bot.send(ev, "重启中，请等待半分钟左右")
    input_token = str(ev.message.extract_plain_text()).strip()
    session_token = input_token if len(input_token) > 50 else None
    global api
    try:
        api.__del__()
        api = get_api(session_token)
        api.select_last_conversation()
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


@sv.on_prefix(('新建人格', '创建人格'))
async def get_new_conversation(bot, ev: CQEvent):
    name = str(ev.message.extract_plain_text()).strip()
    if name == "" or len(name) > 36:
        await bot.send(ev, "请输入人格名(不要过长)")
        return
    try:
        api.reset_conversation()
        msg = (await get_chat_response("hello")).strip()
        if msg:
            await bot.send(ev, msg)
            id = api.get_new_conversation_id()
            if id == "":
                await bot.send(ev, "获取会话id失败")
                return
            conversation[name] = id
            save_conversation()
            await bot.send(ev, f"人格创建成功：\n{name}:{id}")
        else:
            await bot.send(ev, "人格创建失败")
    except Exception as err:
        print(err)


@sv.on_prefix(('选择人格', '选择会话', '切换人格'))
async def change_conversation(bot, ev: CQEvent):
    name = str(ev.message.extract_plain_text()).strip()
    if name == "":
        name = "Default"
    if name in conversation:
        api.conversation_id = conversation[name]
        api.change_conversation()
    else:
        await bot.send(ev, "此人格不存在，可以使用`人格列表`命令获取现有人格。")


@sv.on_fullmatch(('查询人格', '获取人格', '人格列表'))
async def list_conversation(bot, ev: CQEvent):
    if len(conversation) == 0:
        await bot.send(ev, "目前没有可用人格，可以使用`新建人格+人格名`创建新人格")
        return
    msg = f"人格列表({len(conversation)})：\n"
    for k, v in conversation.items():
        msg += f"{k}:{v}\n"
    await bot.send(ev, msg)


@sv.on_prefix(('添加人格', '添加会话'))
async def add_conversation(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    text = str(ev.message.extract_plain_text()).strip().split(":", 1)
    if len(text) != 2:
        await bot.send(ev, "格式错误，格式示例：`添加人格neko:36107c5a-49c8-48ab-b4b5-1b46a576b0d5`")
        return
    name = text[0]
    if name == "" or len(name) > 36:
        await bot.send(ev, "人格名为空或过长，请正确填写")
        return
    id = text[1]
    if len(id) != 36:
        await bot.send(ev, "id输入错误，请检查id是否完整")
        return
    conversation[name] = id


@sv.on_fullmatch('获取会话id')
async def get_conversation_id(bot, ev: CQEvent):
    id = api.get_new_conversation_id()
    if id == "":
        await bot.send(ev, "获取会话id失败")
        return
    await bot.send(ev, id)


# @sv.on_fullmatch('清空会话')
# async def clear_conversation(bot, ev: CQEvent):
#     if not priv.check_priv(ev, priv.SUPERUSER):
#         return
#     api.clear_conversations()
