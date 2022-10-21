# Documentation
## Why switch from [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) to [Pyrogram](https://github.com/pyrogram/pyrogram)?
- Pyrogram can obtain information about any message existing in a chat using their ids
- Pyrogram can receive message edit updates for messages sent before the bot joined
- Pyrogram has more meaningful errors in case something went wrong

  e.g. `pyrogram.errors.exceptions.bad_request_400.ChatAdminRequired` vs `telegram.error.BadRequest`
- Pyrogram has less overhead due to direct connections to Telegram
- Pyrogram has decorators for update handlers