import logging
import sys
sys.path.append("..")

from telegram import Message, MessageEntity, Update, constants, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler

import yt_dlp

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


async def parse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    logging.info(message.text)
    url = message.text

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'cookiesfrombrowser': ("chrome",),
        'ignore_errors': True,
        # 'match_filter': 'protocol == "https"',
        # 'match_filter': lambda x: '.m3u8' not in x['url'],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=False)
        # result = ydl.download([url])

        # logging.info(video_info)
        formats = video_info.get('formats', [])
        mp4_formats = [f for f in formats if f.get('ext') == 'mp4' and f.get('protocol') == 'https']
        for f in mp4_formats:
            print(f)
        top_mp4_formats = sorted(mp4_formats, key=lambda x: x.get('height', 0), reverse=True)[:min(2, len(mp4_formats))]
        # top_mp4_urls = [f.get('url') for f in top_mp4_formats]
        for f in top_mp4_formats:
            print(f['format_id'], f['ext'], f['resolution'], f['url'])
            resolution = f['resolution']
            url = f['url']
            await message.reply_text(f'{resolution}\n{url}')


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
    application.add_handler(MessageHandler(filters.TEXT & filters.Entity("url") & filters.Regex(r'(.*twitter)'), parse))
    # application.add_handler(MessageHandler(filters.TEXT & filters.Entity(constants.MessageEntityType.URL), trip))


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

