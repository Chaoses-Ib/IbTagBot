#!/usr/bin/env python3
import os
import regex
import pyrogram as tg
import jieba

# uvloop does not support Windows at the moment
if os.name != 'nt':
    import uvloop
    uvloop.install()

jieba.initialize()

with open('token.txt', 'r') as f:
    app = tg.Client('bot', api_id=f.readline().rstrip(), api_hash=f.readline().rstrip(), bot_token=f.readline().rstrip())


@app.on_message(tg.filters.command(['start', 'help']))
async def help_handler(client: tg.Client, message: tg.types.Message):
    await message.reply(
'''[IbTagBot：Telegram 标签分词机器人](https://github.com/Chaoses-Ib/IbTagBot)''',
    tg.enums.ParseMode.MARKDOWN)


@app.on_inline_query()
async def answer(client: tg.Client, inline_query: tg.types.InlineQuery):
    # tg.errors.exceptions.ArticleTitleEmpty
    if inline_query.query == '':
        return

    match = regex.search('\s|$', inline_query.query)
    first_word = inline_query.query[:match.start()]
    rest = inline_query.query[match.start():]  # including the space

    def to_tag(word, force_segment=False):
        if word[0] == '#':
            return ' '.join('#' + word for word in jieba.cut(word[1:]))
        elif force_segment:
            return ' '.join('#' + word for word in jieba.cut(word))
        else:
            return '#' + word
    
    first_word_tags = to_tag(first_word)
    first_word_segment_tags = to_tag(first_word, True)
    rest_tags = regex.sub(r'\S+', lambda m: to_tag(m[0]), rest)
    
    results = [tg.types.InlineQueryResultArticle(
                title=first_word_tags + rest_tags,
                input_message_content=tg.types.InputTextMessageContent(first_word_tags + rest_tags)
            )]
    if first_word_tags != first_word_segment_tags:
        results.append(tg.types.InlineQueryResultArticle(
            title=first_word_segment_tags + rest_tags,
            input_message_content=tg.types.InputTextMessageContent(first_word_segment_tags + rest_tags)
        ))
    
    await inline_query.answer(results=results, cache_time=5 * 60)


tag_message_filters = (
    (tg.filters.channel | tg.filters.group)
    & (tg.filters.text | tg.filters.caption)
    # Forwarded message can't be edited
    & ~(tg.filters.forwarded)
)

@app.on_message(tag_message_filters)
@app.on_edited_message(tag_message_filters)
async def tag_message_handler(client: tg.Client, message: tg.types.Message):
    html = message.text.html if message.text is not None else message.caption.html

    def segment(match: regex.Match):
        # Why '<i> </i>' and `f'<i>#{word}</i>'`?
        # Becuase if we use `f'#{word}'`:
        # When editing message, `##ab<i>(#a #b)</i>` will be formatted to `##ab<i>(</i><i>#a</i> <i>#b</i>)</i>`.
        # On our second edit of the message, what we received is `##ab<i>(</i><i>#a</i><i> </i><i>#b</i><i>)</i>` and what we generated is `##ab<i>(#a #b)</i>`. Then new_html != html, and we will get a Bad Request from Telegram:
        # pyrogram.errors.exceptions.bad_request_400.MessageNotModified: Telegram says: [400 MESSAGE_NOT_MODIFIED] - The message was not modified because you tried to edit it using the same content (caused by "messages.EditMessage")

        return f'''##{match[1]}<i>(</i>{ '<i> </i>'.join(f'<i>#{word}</i>' for word in jieba.cut(match[1])) }<i>)</i>'''

    # Which characters are available in tags?
    # For ASCII they are: [A-Za-z][A-Za-z0-9]{0,255}
    '''
    #  #! #" ## #$ #% #& #' #( #) #* #+ #, #- #. #/ 
    #0 #1 #2 #3 #4 #5 #6 #7 #8 #9 #: #; #< #= #> #? 
    #@ #A #B #C #D #E #F #G #H #I #J #K #L #M #N #O 
    #P #Q #R #S #T #U #V #W #X #Y #Z #[ #\ #] #^ #_ 
    #` #a #b #c #d #e #f #g #h #i #j #k #l #m #n #o 
    #p #q #r #s #t #u #v #w #x #y #z #{ #| #} #~ 
    '''
    # For Unicode they are probably: [\p{XID_Start}][\p{XID_Continue}]{0,255}
    # Because `re` doesn't support Unicode properties `\p` (see https://docs.python.org/3/library/re.html), we use `regex` instead.

    # HTML: ##ab...<i>(</i><i>#a</i><i> </i><i>#b</i><i> </i><i>...</i><i>)</i>
    # Markdown: ##ab...__(____#a____ ____#b____ ____...____)__
    new_html = regex.sub(r'##([\p{XID_Start}][\p{XID_Continue}]*)(?: |<i>\([^\)]*\)</i>)?', segment, html)

    if new_html == html:
        return

    try:
        await message.edit(new_html, tg.enums.ParseMode.HTML)
    except tg.errors.exceptions.bad_request_400.ChatAdminRequired:
        await message.reply('不具有编辑消息权限')
    except Exception as e:
        await message.reply(str(e))


app.run()