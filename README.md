# GPT3.5 API无法使用的可以试试这个

### 使用[pyChatGPT](https://github.com/terry3041/pyChatGPT)方案。
> #### 我是在Windows环境下测试的，其他环境出问题我无法处理，作者给出了linux的方案，具体可以看看说明：https://github.com/terry3041/pyChatGPT
> #### 增加了简易认证方式，通过指定浏览器账号，提前登录谷歌账号，可以实现几乎不用动手的登录体验，顺便还能用浏览器插件解决代理等问题。
> #### 注意谷歌浏览器需要110以上版本。代理得有正常的速度，卡太久程序也会退出。
------
  
# aichat-chatGPT
  
aichat插件魔改chatGPT版本  

ChatGPT要一个一个字打印，会比较慢。要快的可以去找GPT-3 API版的插件(需要不断创号获取key)。
  
## 命令
1. `创建人格/新建人格+人格名`: 创建新人格，注意人格名不能大于36位
2. `查看人格/人格列表/获取人格`: 获取当前所有人格及id
3. `选择人格/切换人格+人格名`: 打开对应人格的会话
4. `添加人格/添加会话+人格名:人格id`: 添加人格。
5. `获取会话id`: 获取首位会话的id
6. `初始化会话/初始化人工智障`: 打开新会话，但是不会返回会话id，可以使用`获取会话id`获取
7. `人格初始化/猫娘初始化`: 内置猫娘，也可以改成别的初始化设定，修改目录下的init_msg.txt即可（UTF-8编码保存）
8. `/t+消息或@bot+消息`: 你懂的（/t是随便打的，可以自己去代码里改成别的）
9. `更新凭证+session_token或不加`: 重启浏览器并重新登录，如果配置文件没有会话id则选择最新的一个会话，如果输入了session_token则是指定用session_token登录
10. `重新组织语言`: 重试上一条对话
0. `清空会话`: (慎用)注释掉了，要用的话自己取消注释，注意代码中使用权限是SUPERUSER

## 安装方法
0. 确保有安装110以上版本的谷歌浏览器，参考:https://github.com/terry3041/pyChatGPT#getting-started
1. 在HoshinoBot的插件目录modules下clone本项目 `git clone --branch pyChatGPT https://github.com/Cosmos01/aichat-chatGPT.git`
2. 安装必要第三方库[pyChatGPT](https://github.com/terry3041/pyChatGPT)：`pip install pyChatGPT==0.4.3.3`
3. 在 `config/__bot__.py`的MODULES_ON列表里加入 `aichat-chatGPT`
4. 到auth.json中填写配置，参考下面认证方式和配置，
5. 重启HoshinoBot (启动前确保关闭了浏览器)
6. 在弹出的浏览器中手动通过一下CF验证
7. 插件默认禁用，在要启用本插件的群中发送命令`启用 人工智障`
  
## 认证方式
- session_token：容易过期，推荐用下面的方式。
- google账号登录：可以配合指定浏览器用户的参数来实现轻松登录。
  
## 配置参数
- session_token
> 用session_token认证方式时填写，具体获取方式参考：[pyChatGPT](https://github.com/terry3041/pyChatGPT#usage)，**请尽量用一台机器的同浏览器获取token，要保证UA和IP一致**，参数过期后可以使用更新凭证命令或是重新填写然后执行初始化命令，推荐使用EditThisCookie插件读Cookie。
- user_data_dic/profile_directory
> 指定浏览器用户，两个参数必须同时存在，获取方式：  
> 浏览器输入chrome:\//version，查看个人资料路径，前面的路径为user_data_dic，末尾文件夹名为profile_directory，注意Windows下打两个反斜杠转义，参考下面例子。
>> 利用这两个参数可以提前在浏览器登录谷歌账号实现快速认证，可以提前装好SwitchyOmega（用法自己查询）来配置代理，或是安装Tampermonkey，顺便推荐个[屏蔽安全检查脚本](https://greasyfork.org/zh-CN/scripts/456507-openai-catgirl-chat)
- email/password/auth_type
> 账号登录时使用，auth_type支持google、windowslive、openai。建议使用google，另外两个参数没测试过。账号密码和类型三个参数需要同时存在，如果使用上一个参数让浏览器已经登录了谷歌账户就会自动跳过用户名密码步骤，所以密码可以随便填，但密码参数必须存在。
- proxy
> 支持http/https/socks4/socks5，更推荐使用上面提到的SwitchyOmega代理，这东西似乎有时候有点问题。
- 更多参数参考chatGPT.py源码中的注释，目前大部分都已经同步支持，但我没测试过
  
**其中不需要的参数请整行删去，否则会被认为是有效参数。**
```
{
	"session_token":"********",
	"email":"*******@gmail.com",
	"password":"*******",
	"auth_type": "google",
	"proxy": "http://127.0.0.1:7890",
	"user_data_dic": "C:\\Users\\Admin\\AppData\\Local\\Google\\Chrome\\User Data",
	"profile_directory": "Default"
}
```
    
## 参考项目
- 原插件：[aichat](https://github.com/pcrbot/aichat)   
- 略微修改集成进了项目：[pyChatGPT](https://github.com/terry3041/pyChatGPT)

## 常见问题
1. `发生错误: name 'api' is not defined`: 多种情况，看看浏览器窗口，可能是你浏览器没更新到110版本或者网络太慢，也可能凭证问题，更新凭证或修改登录方式（我只保证谷歌账号自动登录方式能稳定使用，其他方式懒得测试了）
2. 如果压根没弹出网页，请先确保你已经关闭了浏览器(检查一下后台或重启系统)，再不行可能是你的环境有点问题，检查一下上面的第三方库是否正常安装之类的。再不行我也无力，环境问题太难解决了。如果你运行作者的[demo](https://github.com/terry3041/pyChatGPT/blob/main/src/pyChatGPT/__main__.py)也弹不出浏览器，可以去问问他。
3. `发生错误: Too many requests in 1 hour. Try again later.`: 配额上限，等下一个小时，如果没在频繁使用则是你的ip访问量太大了，换个代理应该就行了。

## 我的环境
- Windows Server 2019 Datacenter
- Python 3.8.9
- Google Chrome 版本 110.0.5481.78（正式版本） （64 位）
- 浏览器安装SwitchyOmega插件进行代理

## 鸣谢

- [BlueDeer](https://github.com/BlueDeer233) - 增加异步

<br><br><br><br><br><br><br><br>

------
  
# TODO
有空实现这个
![0CCC2@19$E0_OB_~RMYW JR](https://user-images.githubusercontent.com/37209685/208008656-e4868ff6-006d-4018-a5b0-b337157ce58d.jpg)  

  
  
<br><br><br><br><br><br><br><br>
------  
    
# chatGPT调教
  
## 案例集合  

- [一个分享咒语的网站](https://onetwo.ren/ChatGPT-Magic-Chat)
- [一个逝去的猫娘纪录](https://gist.githubusercontent.com/ChenYFan/ffb8390aac6c4aa44869ec10fe4eb9e2/raw/3e10b883b6e78f22172f985e48dc5ecfda1a764c/train.txt)
- [ChatGPT 中文调教指南](https://github.com/PlexPt/awesome-chatgpt-prompts-zh)
- [催眠](https://github.com/golfzert/chatgpt-chinese-prompt-hack)


