# [@IbTagBot](https://t.me/IbTagBot)
Telegram 标签分词机器人

## 标签分词
### 内联查询模式
在聊天框中输入：
```
@IbTagBot 白发 红眼 美少女 #白发红眼美少女
```

机器人会为每个词语加上 `#` 前缀，并对 `#` 开头的词组进行分词：

<pre><code><a href="">#白发</a> <a href="">#红眼</a> <a href="">#美少女</a> <a href="">#白发</a> <a href="">#红眼</a> <a href="">#美少女</a></code></pre>

### 管理员模式
自动对频道或群组消息中的标签进行分词。

例如，当发送以下消息时：

<pre><code>想看#<a href="">#白发红眼美少女</a> 吗？</code></pre>

它将被机器人自动编辑为：

<pre><code>想看#<a href="">#白发红眼美少女</a><i>(<a href="">#白发</a> <a href="">#红眼</a> <a href="">#美少女</a>)</i>吗？</code></pre>

你也可以对机器人编辑后的消息进行二次编辑，括号中的内容会被自动更新。

## Deployment
```sh
git clone https://github.com/Chaoses-Ib/IbTagBot.git
cd IbTagBot
pip3 install -r requirements.txt
echo [YOUR_API_ID] >> token.txt
echo [YOUR_API_HASH] >> token.txt
echo [YOUR_BOT_TOKEN] >> token.txt
python3 bot.py
```