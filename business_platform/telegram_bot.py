import logging
import sys
sys.path.append("..")

from telegram import Message, MessageEntity, Update, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler

from config import telegram_config



def message_text(message: Message) -> str:
    """
    Returns the text of a message, excluding any bot commands.
    """
    message_text = message.text
    if message_text is None:
        return ''

    for _, text in sorted(message.parse_entities([MessageEntity.BOT_COMMAND]).items(), key=(lambda item: item[0].offset)):
        message_text = message_text.replace(text, '').strip()

    return message_text if len(message_text) > 0 else ''


commands = [
    BotCommand(command='help', description='Show help message'),
    BotCommand(command='draw', description='draw a picture'),
    BotCommand(command='token', description='please input your replicate token, you should sign up and get your API token: https://replicate.com/account/api-tokens'),
]


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Shows the help menu.
    """
    help_text = 'I\'m a ytb_dl bot, send me a ytb/twitter link!'
    await update.message.reply_text(help_text, disable_web_page_preview=True)


async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    logging.info(message.text)
    strs = message.text.split()
    logging.info(strs)
    if len(strs) < 2:
        await message.reply_text(r'please input points as /points <points>')
        return

    points = int(strs[1])
    id = str(message.from_user.id)
    logging.info(id)
    user = db.get_user(id)
    logging.info(user)
    if user is not None:
        user.points += points
        db.update_user(user)
        new_user = db.get_user(id)
        logging.info(new_user)
        await message.reply_text(f'{new_user}')


async def run():
    """
    Runs the bot indefinitely until the user presses Ctrl+C
    """
    application = ApplicationBuilder() \
        .token(telegram_config['token']) \
        .concurrent_updates(True) \
        .build()

    application.add_handler(CommandHandler('start', help))
    application.add_handler(CommandHandler('help', help))

    # application.add_handler(CallbackQueryHandler(callback=self.set_model, pattern='GuoFeng|chill|uber|majic'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_dress, pattern='.*dress|.*suit|.*wear|.*uniform|armor|hot|bikini|see|.*hanfu'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_bg, pattern='.*beach|grass|space|street|mountain'))

    # application.add_handler(MessageHandler(filters.PHOTO & ~filters.CaptionRegex('dress|bg|mi|hand|lace|up|lower|ext|rep|high|clip|all'), self.trip))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('hh'), high))
    application.add_handler(MessageHandler(filters.PHOTO & filters.CaptionRegex('tt'), trip))

    #application.add_error_handler(self.error_handler)

    # application.run_polling()
    await application.initialize()
    await application.start()
    logging.info("start up successful ……")
    await application.updater.start_polling(drop_pending_updates=True)


async def start_task():
    """|coro|
    以异步方式启动
    """
    return await run()

