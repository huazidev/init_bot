import logging
import sys
sys.path.append("..")
import re

from telegram import Message, MessageEntity, Update, constants, \
    BotCommand, ChatMember, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, Application, CallbackContext, CallbackQueryHandler

import yt_dlp
from config import telegram_config
from framework_sites import douyin
from framework_sites import parse
from framework_sites import xiaohongshu



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
    BotCommand(command='down', description='down a link'),
    BotCommand(command='token', description='please input your replicate token, you should sign up and get your API token: https://replicate.com/account/api-tokens'),
]


def parse_url_by_ydl(url, num):
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
        top_mp4_formats = sorted(mp4_formats, key=lambda x: x.get('height', 0), reverse=True)[:min(3, len(mp4_formats))]
        # top_mp4_urls = [f.get('url') for f in top_mp4_formats]
        # for f in top_mp4_formats:
        for i in range(len(top_mp4_formats)):
            f = top_mp4_formats[i]
            print(i, f['format_id'], f['ext'], f['resolution'], f['url'])
            resolution = f['resolution']
            url = f['url']
            if i == num:
                return resolution, url


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Shows the help menu.
    """
    commands_description = [f'/{command.command} - {command.description}' for command in commands]
    help_text = 'I\'m a ytb_dl bot, send me a video link!' + \
                '\n\n' + \
                '\n'.join(commands_description) + \
                '\n\n'
    await update.message.reply_text(help_text, disable_web_page_preview=True)


async def down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    image_query = message_text(message)
    if image_query == '' or not image_query.startswith("http"):
        await message.reply_text('Please provide a prompt! (e.g. /down <url>)')
    await message.reply_document(image_query)


async def twitter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    logging.info(message.text)
    url = message.text
    strs = url.split()
    num = 0 if len(strs) == 1 else int(strs[1])
    logging.info(num)

    resolution, url = parse_url_by_ydl(url, num)
    await message.reply_text(f'{resolution}\n{url}')


async def guonei(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    # link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    url_regex = re.compile(link_pattern)
    # urls = re.search('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', text).groups()
    match = url_regex.search(text)
    if match:
        url_ori = match.group()
    # if len(urls) >= 1:
    #     url_ori = urls[0]
        logging.info(url_ori)
        if 'douyin' in url_ori:
            urls = douyin.douyin_parse(url_ori)
            resolution = '720x1080'
            for url in urls:
                await update.message.reply_text(f'{resolution}\n{url}')
        elif 'xiaohongshu' in url_ori or 'xhs' in url_ori:
            urls = xiaohongshu.xhs_parse(url_ori)
            resolution = '900x1200'
            for url in urls:
                await update.message.reply_text(f'{resolution}\n{url}')
        else:
            resolution, url = parse_url_by_ydl(url_ori, 0)
            await update.message.reply_text(f'{resolution}\n{url}')


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
    application.add_handler(CommandHandler('down', down))

    # application.add_handler(CallbackQueryHandler(callback=self.set_model, pattern='GuoFeng|chill|uber|majic'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_dress, pattern='.*dress|.*suit|.*wear|.*uniform|armor|hot|bikini|see|.*hanfu'))
    # application.add_handler(CallbackQueryHandler(callback=self.draw_bg, pattern='.*beach|grass|space|street|mountain'))

    # application.add_handler(MessageHandler(filters.PHOTO & ~filters.CaptionRegex('dress|bg|mi|hand|lace|up|lower|ext|rep|high|clip|all'), self.trip))
    # application.add_handler(MessageHandler(filters.TEXT & filters.Entity(constants.MessageEntityType.URL), trip))
    application.add_handler(MessageHandler(filters.TEXT & filters.Entity("url") & filters.Regex(r'(.*twitter)'), twitter))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.Regex(r'(.*twitter)')), guonei))

    # application.add_error_handler(self.error_handler)

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

