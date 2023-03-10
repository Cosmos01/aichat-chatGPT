### 现已更新API版本，API支持了GPT3.5并且大幅降价，约等于白嫖
> #### 网页版在这个分支下: https://github.com/Cosmos01/aichat-chatGPT/tree/pyChatGPT
> #### 我加的群压根没人用这个功能，所以很多情况测试不到位，可能会有问题。
> #### 欢迎提交issues(提交前确认是否使用最新版本)，有想加的功能也可以提。
------
  
# aichat-chatGPT
  
aichat插件魔改GPT-3.5 API版本  
  
## 命令(人格可换成会话)
1. `创建人格/新建人格/设置人格+人格名+空格+设定`: 创建新人格或修改现有人格，注意人格名不能大于24位
2. `查询人格/人格列表/获取人格`: 获取当前所有人格及当前人格
3. `选择人格/切换人格/默认人格+人格名`: 切换到对应人格，不填则使用默认人格
4. `/t+消息或@bot+消息`: 前面加上记住两字可以让关闭记忆功能的bot记住对话，记住两字不会放入对话
5. `重置人格/重置会话+人格名`: 清空对话，只保留设定，不填则重置当前人格，无当前人格则重置默认人格
6. `对话记忆+on/off`: 开启/关闭对话记忆，不加则返回当前状态  

## 安装方法
1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/Cosmos01/aichat-chatGPT.git`
2. 安装必要第三方库：`pip install openai`
3. 在 `config/__bot__.py`的MODULES_ON列表里加入 `aichat-chatGPT`
4. 到config.ini中填写配置，基本只要填api_key(可以多个)和proxy，其他配置见下文。注意修改后保存为UTF-8。
5. 重启HoshinoBot (启动前确保关闭了浏览器)
6. 插件默认禁用，在要启用本插件的群中发送命令`启用 人工智障`
  

## 配置参数
- api-key
> 由于有30分钟条数限制，可以填写多个api-key，半角逗号(",")隔开，每次对话随机选择
- proxy 代理
> HTTP代理，不需要代理留空即可，例：http://127.0.0.1:7890
- record 记忆开关
> 设为false则不会记录会话，除非你在对话前加上"记住"两个字(两个字会被删去)，这样可以节省很多费用。
- max_tokens 最大回答长度
> 改小了也能节省一些费用。
- interval 保存间隔
> 每进行N次对话就在本地保存会话记录，非记忆对话不计次。


## 常见问题
1. `Error communicating with OpenAI` 代理问题，配置了代理也这样就换节点吧。

## 注意事项
1. 会话长度有限制(4096)，当会话超过4096-max_tokens时，会自动删除最早的两条对话(不会删除设定)。

<br><br><br><br><br><br><br><br>
------  
    
# chatGPT调教
  
## 案例集合  

- [一个分享咒语的网站](https://onetwo.ren/ChatGPT-Magic-Chat)
- [一个逝去的猫娘纪录](https://gist.githubusercontent.com/ChenYFan/ffb8390aac6c4aa44869ec10fe4eb9e2/raw/3e10b883b6e78f22172f985e48dc5ecfda1a764c/train.txt)
- [ChatGPT 中文调教指南](https://github.com/PlexPt/awesome-chatgpt-prompts-zh)
- [催眠](https://github.com/golfzert/chatgpt-chinese-prompt-hack)


<br><br><br><br><br><br><br><br>

------
  
# TODO
有空实现这个
![0CCC2@19$E0_OB_~RMYW JR](https://user-images.githubusercontent.com/37209685/208008656-e4868ff6-006d-4018-a5b0-b337157ce58d.jpg)  


