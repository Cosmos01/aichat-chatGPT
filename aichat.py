import re
from hoshino import Service
from hoshino.typing import CQEvent
from . import Config
from .client import Client

help_text = """命令(人格可以替换为会话)
1. `创建人格/新建人格/设置人格+人格名+空格+设定`: 创建新人格或修改现有人格，注意人格名不能大于24位
2. `查询人格/人格列表/获取人格`: 获取当前所有人格及当前人格
3. `选择人格/切换人格/默认人格+人格名`: 切换到对应人格，不填则使用默认人格
4. `/t+消息或@bot+消息`: 你懂的（/t是随便打的，可以自己去代码里改成别的）
"""

sv = Service('人工智障', enable_on_default=False, help_=help_text)

black_word = ['今天我是什么少女', 'ba来一井']  # 如果有不想触发的词可以填在这里

cq_code_pattern = re.compile(r'\[CQ:\w+,.+\]')
config = Config()
group_clients = {}
count = 0


async def get_chat_response(group_id, prompt):
    group_id = str(group_id)
    record = config.record
    if not record and prompt.startswith("记住"):
        # prompt = prompt.removeprefix("记住")
        prompt = prompt[2:]
        record = True
    if group_id not in group_clients:
        group_clients[group_id] = Client(config.api_key, config.model, config.max_tokens)
    client: Client = group_clients[group_id]
    try:
        msg = await client.send(prompt, record)
        if record:
            config.conversations[client.conversation] = client.messages
            config.groups[group_id] = client.conversation
            global count
            count += 1
            if config.interval > 0 and count % config.interval == 0:
                config.save_conversations()
                config.save_groups()
        return msg
    except Exception as e:
        print(e)
        err = str(e) if len(str(e)) < 133 else str(e)[:133]
        return f"发生错误: {err}"


@sv.on_message('group')
async def ai_reply(bot, context):
    msg = str(context['message'])
    if msg.startswith(f'[CQ:at,qq={context["self_id"]}]'):
        text = re.sub(cq_code_pattern, '', msg).strip()
        if text == '' or text in black_word:
            return
        try:
            msg = await get_chat_response(context["group_id"], text)
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
        msg = await get_chat_response(ev.group_id, text)
        if msg:
            await bot.send(ev, msg)
    except Exception as err:
        print(err)


@sv.on_prefix(('新建人格', '创建人格', '新建会话', '创建会话', '设置人格', '设置会话'))
async def set_conversation(bot, ev: CQEvent):
    args = str(ev.message.extract_plain_text()).strip().split(" ", 1)
    if len(args) != 2:
        await bot.send(ev, "参数错误，请输入人格名+空格+预设语句")
        return
    name = args[0]
    text = args[1]
    if len(name) > 24:
        await bot.send(ev, "人格名过长")
        return
    msg = [{"role": "system", "content": text}]
    config.conversations[name] = msg
    config.save_conversations()


def save_data(group_id, conversation, messages):
    global config
    config.conversations[conversation] = messages
    config.groups[str(group_id)] = conversation
    config.save_conversations()
    config.save_groups()


@sv.on_prefix(('选择人格', '选择会话', '切换人格', '切换会话', '默认人格', '默认会话'))
async def change_conversation(bot, ev: CQEvent):
    name = str(ev.message.extract_plain_text()).strip()
    if name == "":
        name = "default"
    group_id = str(ev.group_id)
    if group_id not in group_clients:
        group_clients[group_id] = Client(config.api_key, config.model, config.max_tokens)
    if name in config.conversations:
        save_data(group_id, name, config.conversations[name])
        client = group_clients[group_id]
        client.conversation = name
        client.messages = config.conversations[name]
        await bot.send(ev, "切换完成")
    else:
        await bot.send(ev, "此人格不存在，可以使用`人格列表`命令获取现有人格。")


@sv.on_fullmatch(('查询人格', '获取人格', '人格列表', '会话列表', '获取会话', '查询会话'))
async def list_conversation(bot, ev: CQEvent):
    group_id = str(ev.group_id)
    name = config.groups[group_id] if group_id in config.groups else "default"
    msg = f"当前人格：{name}\n人格列表({len(config.conversations)})：\n"
    for k in config.conversations:
        msg += f"{k}、"
    await bot.send(ev, msg.strip("、"))
