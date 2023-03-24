import re
import random
from hoshino import Service
from hoshino.typing import CQEvent
from . import Config
from .client import Client

help_text = """命令(人格可以替换为会话)
1. `创建人格/新建人格/设置人格+人格名+空格+设定`: 创建新人格或修改现有人格，注意人格名不能大于24位
2. `查询人格/人格列表/获取人格`: 获取当前所有人格及当前人格
3. `选择人格/切换人格/默认人格+人格名`: 切换到对应人格，不填则使用默认人格
4. `/t+消息或@bot+消息`: 前面加上记住两字可以让关闭记忆功能的bot记住对话，记住两字不会放入对话
5. `重置人格/重置会话+人格名`: 重置人格，不填则重置当前人格，无当前人格则重置默认人格
6. `对话记忆+on/off`: 开启/关闭对话记忆，不加则返回当前状态
7. `删除会话+会话名` : 删除会话，不填则删除当前会话，默认会话不可删除
8. `删除对话+条数`: 删除上N条对话，不加条数则删除上一条。1条对话指一次问与答，不需要乘2。
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
    api_key = random.choice(config.api_keys)
    if group_id not in group_clients:
        group_clients[group_id] = Client(random.choice(config.api_keys), config.model, config.max_tokens, config.proxy)
    client: Client = group_clients[group_id]
    client.chat.api_key = api_key
    try:
        msg = await client.send(prompt, record)
        if record:
            config.conversations[client.conversation] = client.messages
            config.groups[group_id] = client.conversation
            global count
            count += 1
            if config.interval > 0 and count % config.interval == 0:
                config.save_conversations()
                config.save_config()
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
    if str(ev.group_id) in group_clients:
        group_clients[str(ev.group_id)].conversation = name
        group_clients[str(ev.group_id)].messages = msg
    await bot.send(ev, f"{name}创建完成")


@sv.on_prefix(('删除人格', '删除会话'))
async def delete_conversation(bot, ev: CQEvent):
    name = str(ev.message.extract_plain_text()).strip()
    if name == "":
        if str(ev.group_id) in group_clients:
            name = group_clients[str(ev.group_id)].conversation
            if name != "default":
                group_clients[str(ev.group_id)].conversation = "default"
                group_clients[str(ev.group_id)].messages = config.conversations["default"]
        else:
            await bot.send(ev, "当前无会话，请指定要删除的会话")
            return
    if name == "default":
        await bot.send(ev, "默认会话不可删除")
        return
    if name not in config.conversations:
        await bot.send(ev, "人格不存在")
        return
    del config.conversations[name]
    config.save_conversations()
    await bot.send(ev, f"{name}删除成功")


def save_data(group_id, conversation, messages):
    global config
    config.conversations[conversation] = messages
    config.groups[str(group_id)] = conversation
    config.save_conversations()
    config.save_config()


@sv.on_prefix(('选择人格', '选择会话', '切换人格', '切换会话', '默认人格', '默认会话'))
async def change_conversation(bot, ev: CQEvent):
    name = str(ev.message.extract_plain_text()).strip()
    if name == "":
        name = "default"
    group_id = str(ev.group_id)
    if group_id not in group_clients:
        group_clients[group_id] = Client(random.choice(config.api_keys), config.model, config.max_tokens, config.proxy)
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


@sv.on_prefix(('重置人格', '重置会话'))
async def reset_conversation(bot, ev: CQEvent):
    group_id = str(ev.group_id)
    name = str(ev.message.extract_plain_text()).strip()
    if name == "":
        if group_id in config.groups:
            name = config.groups[group_id]
        else:
            name = "default"
    if name in config.conversations:
        config.conversations[name] = config.conversations[name][:1]
        config.save_conversations()
        for client in group_clients.values():
            if client.conversation == name:
                client.messages = config.conversations[name]
        await bot.send(ev, "重置成功")

        
@sv.on_prefix('删除对话')
async def del_msg(bot, ev: CQEvent):
    group_id = str(ev.group_id)
    p = str(ev.message.extract_plain_text()).strip()
    num = 2
    if p != "":
        num = int(p)*2
    name = "default"
    if group_id in config.groups:
        name = config.groups[group_id]
    if name not in config.conversations:
        await bot.send(ev, "人格不存在")
        return
    max = len(config.conversations[name])-1
    if num < max:
        del config.conversations[name][-num:]
        config.save_conversations()
        for client in group_clients.values():
            if client.conversation == name:
                client.messages = config.conversations[name]
        await bot.send(ev, "删除成功")
    else:
        await bot.send(ev, f"最多只能删除{str(int(max/2)-1)}条对话")
        

@sv.on_prefix('对话记忆')
async def set_record(bot, ev: CQEvent):
    cfg = str(ev.message.extract_plain_text()).strip()
    if cfg == "on":
        config.record = True
        await bot.send(ev, "对话记忆已开启")
    elif cfg == "off":
        config.record = False
        await bot.send(ev, "对话记忆已关闭")
    else:
        if config.record:
            await bot.send(ev, "当前对话记忆状态：开启")
        else:
            await bot.send(ev, "当前对话记忆状态：关闭")
        return
    config.save_config()
