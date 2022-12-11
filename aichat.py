import os
import random
import re
import time
import json
from nonebot import get_bot
from hoshino import Service, priv
from hoshino.typing import CQEvent
from . import Config
from revChatGPT.revChatGPT import Chatbot

sv = Service('人工智障', enable_on_default=False)

black_word = ['今天我是什么少女', 'ba来一井']  # 如果有不想触发的词可以填在这里

# 可以输入bot的设定来初始化bot
init_msg = "你好"  # '''你是一个小萝莉'''

bot = get_bot()
cq_code_pattern = re.compile(r'\[CQ:\w+,.+\]')
salt = None
CONFIG_PATH = os.path.dirname(__file__)
group_config = Config(os.path.join(CONFIG_PATH, "config.json"))
with open(os.path.join(CONFIG_PATH,"auth.json"),"r") as auth_config:
    auth_config = json.load(auth_config)


DEFAULT_AI_CHANCE = 1  # 默认的AI回复概率
user_session = dict()

# 初始化bot
chatbot = Chatbot(auth_config)

def get_chat_response(session_id, prompt):

    # if session_id in user_session:
    #     # 如果在三分钟内再次发起对话则使用相同的会话ID
    #     if time.time() < user_session[session_id]['timestamp'] + 60 * 3:
    #         chatbot.conversation_id = user_session[session_id]['conversation_id']
    #         chatbot.parent_id = user_session[session_id]['parent_id']
    #     else:
    #         chatbot.reset_chat()
    # else:
    #     chatbot.reset_chat()

    if session_id in user_session:
        chatbot.conversation_id = user_session[session_id]['conversation_id']
        chatbot.parent_id = user_session[session_id]['parent_id']
    else:
        chatbot.reset_chat()

    try:
        resp = chatbot.get_chat_response(prompt, output="text")
        user_cache = dict()
        user_cache['timestamp'] = time.time()
        user_cache['conversation_id'] = resp['conversation_id']
        user_cache['parent_id'] = resp['parent_id']
        user_session[session_id] = user_cache
        return resp['message']
    except Exception as e:
        return f"发生错误: {str(e)}"


@sv.on_fullmatch(('初始化人工智障'))
async def init_neko(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return

    group_id = str(ev.group_id)
    if group_id in user_session:
        user_session.pop(group_id)
    try:
        msg = get_chat_response(group_id, init_msg)
        await bot.send(ev, msg)
        await bot.send(ev,str(user_session[group_id]))
    except Exception as err:
        await bot.send(ev, err)
        print(err)

@sv.on_prefix(('复活人工智障'))
async def set_neko(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        return
    s = ev.message.extract_plain_text()
    group_id = str(ev.group_id)

    if group_id in user_session:   
        try:     
            conversation_id = s.split(":")[0]
            parent_id = s.split(":")[1]
            user_session[group_id]['conversation_id'] = conversation_id
            user_session[group_id]['parent_id'] = parent_id
        except Exception as err:
                    print(err) 

@sv.on_prefix(('调整AI概率'))
async def enable_aichat(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '请联系群管理调整AI概率哦~')
    s = ev.message.extract_plain_text()
    if s:
        if s.isdigit() and 0 < int(s) < 51:
            chance = int(s)
        else:
            await bot.finish(ev, '参数错误: 请输入1-50之间的整数.')
            return
    else:
        chance = DEFAULT_AI_CHANCE  # 后面不接数字时调整为默认概率
    group_config.set_chance(str(ev.group_id), chance)
    await bot.send(ev, f'人工智障已启用, 当前bot回复概率为{chance}%.')


@sv.on_fullmatch(('消除AI概率', '关闭人工智障'))
async def disable_aichat(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.finish(ev, '请联系群管理关闭此功能哦~')
    group_config.delete_chance(str(ev.group_id))
    await bot.send(ev, f'人工智障已禁用')


@sv.on_message('group')
async def ai_reply(bot, context):
    msg = str(context['message'])
    session_id = str(context.group_id)
    if msg.startswith(f'[CQ:at,qq={context["self_id"]}]'):
        text = re.sub(cq_code_pattern, '', msg).strip()
        if text == '' or text in black_word:
            return
        try:
            msg = get_chat_response(session_id, text)
            await bot.send(context, msg, at_sender=False)
        except Exception as err:
            print(err)
        return
    if str(context.group_id) in group_config.chance:
        if not random.randint(1, 200) <= int(group_config.chance[str(context.group_id)]):
            return
        else:
            text = re.sub(cq_code_pattern, '', msg).strip()
            if text == '' or text in black_word:
                return
            try:
                msg = get_chat_response(session_id, text)
                await bot.send(context, msg, at_sender=False)
            except Exception as err:
                print(err)
    else:
        return
