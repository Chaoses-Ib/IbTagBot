#!/usr/bin/env python3
import regex
import logging
import telegram as tg
import telegram.constants
import telegram.ext as tge
import jieba

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

jieba.initialize()

# Read token from token.txt
with open('token.txt', 'r', encoding='utf-8') as f:
    token = f.read().strip()

application = tge.ApplicationBuilder().token(token).build()

async def help(update: tg.Update, context: tge.ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
'''[IbTagBot](https://github.com/Chaoses-Ib/IbTagBot) 是一个用于提高标签输入效率的机器人，它能够自动对频道或群组消息中的标签进行分词。

例如，当发送以下消息时：

想看##白发红眼美少女 吗？

它将被机器人自动编辑为：

想看##白发红眼美少女_(#白发 #红眼 #美少女)_吗？

你也可以对机器人编辑后的消息进行二次编辑，括号中的内容会被自动更新。''', parse_mode=tg.constants.ParseMode.MARKDOWN)

async def get_me_as_admin(chat: tg.Chat, context: tge.ContextTypes.DEFAULT_TYPE) -> tg.ChatMemberAdministrator:
    if chat.type == tg.constants.ChatType.PRIVATE:
        return None
    
    my_id = context.bot.id
    admins = await chat.get_administrators()
    for admin in admins:
        if admin.user.id == my_id:
            return admin
    
    return None

async def tag_segment(update: tg.Update, context: tge.ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    # Forwarded message can'b be edited
    if msg.forward_date is not None:
        return

    html = msg.text_html

    def segment(match: regex.Match):
        # Why `f'<i>#{word}</i>'`?
        # Becuase if we use `f'#{word}'`:
        # When editing message, `##ab<i>(#a #b)</i>` will be formatted to `##ab<i>(</i><i>#a</i> <i>#b</i>)</i>`.
        # On our second edit of the message, what we received is `##ab<i>(</i><i>#a</i> <i>#b</i><i>)</i>` and what we generated is `##ab<i>(#a #b)</i>`. Then new_html != html, and we will get a BadRequest from Telegram:
        # BadRequest('Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message')

        return f'''##{match[1]}<i>(</i>{ ' '.join(f'<i>#{word}</i>' for word in jieba.cut(match[1])) }<i>)</i>'''
    
    # Which characters are available?
    # For ASCII they are: [A-Za-z][A-Za-z0-9]*
    # For Unicode they are probably: [\p{XID_Start}][\p{XID_Continue}]*
    # Because `re` doesn't support Unicode properties `\p` (see https://docs.python.org/3/library/re.html), we use `regex` instead.
    '''
    #  #! #" ## #$ #% #& #' #( #) #* #+ #, #- #. #/ 
    #0 #1 #2 #3 #4 #5 #6 #7 #8 #9 #: #; #< #= #> #? 
    #@ #A #B #C #D #E #F #G #H #I #J #K #L #M #N #O 
    #P #Q #R #S #T #U #V #W #X #Y #Z #[ #\ #] #^ #_ 
    #` #a #b #c #d #e #f #g #h #i #j #k #l #m #n #o 
    #p #q #r #s #t #u #v #w #x #y #z #{ #| #} #~ 
    '''
    try:
        '''##ab...<i>(</i><i>#a</i> <i>#b</i> ... <i>)</i>'''
        new_html = regex.sub(r'##([\p{XID_Start}][\p{XID_Continue}]*)(?: |<i>\([^\)]*\)</i>)?', segment, html)
        if new_html != html:
            await msg.edit_text(text=new_html, parse_mode=tg.constants.ParseMode.HTML)
    except Exception as e:
        admin = await get_me_as_admin(chat, context)
        if not admin or not admin.can_edit_messages:
            await msg.reply_text('不具有编辑消息权限')
        else:
            await msg.reply_text(str(e))

help_handler = tge.CommandHandler('help', help)
application.add_handler(help_handler)

tag_segment_handler = tge.MessageHandler(tge.filters.TEXT & (~tge.filters.COMMAND), tag_segment)
application.add_handler(tag_segment_handler)

application.run_polling()