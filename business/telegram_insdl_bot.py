import logging

from instaloader import instaloader
from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, Application, CallbackContext, \
    CallbackQueryHandler, MessageHandler, filters

from kernel.config import telegram_config

# 创建 Instaloader 实例
L = instaloader.Instaloader(download_video_thumbnails=False)

commands = [
    BotCommand(command='help', description='Show help message'),
    # BotCommand(command='token', description='please input your replicate token, you should sign up and get your API token: https://replicate.com/account/api-tokens'),
]


async def post_init(application: Application) -> None:
    """
    Post initialization hook for the bot.
    """
    await application.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "欢迎使用 Instagram 下载机器人！\n"
        "请发送 Instagram 帖子的链接，我将为您下载图片和视频。"
    )


async def get_instagram_link(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    link = update.message.text

    try:
        post = instaloader.Post.from_shortcode(L.context, link.split('/')[-2])
        await update.message.reply_text("请稍等，我将发送给您下载的内容。")

        logging.info(f"typename:{post.typename}")
        if post.typename == 'GraphSidecar':
            for node in post.get_sidecar_nodes():
                logging.info(f"display_url:{node.display_url}")
                if node.is_video:
                    await update.message.reply_document(document=node.video_url)
                else:
                    await update.message.reply_document(document=node.display_url)

        if post.typename == 'GraphImage':
            logging.info(f"post_url:{post.url}")
            await update.message.reply_document(document=post.url)
    except Exception as e:
        await update.message.reply_text(f"获取下载地址失败：{e}")


async def run():
    """
    Runs the bot indefinitely until the user presses Ctrl+C
    """
    application = ApplicationBuilder() \
        .token(telegram_config['ins_token']) \
        .concurrent_updates(True) \
        .post_init(post_init) \
        .build()

    application.add_handler(CommandHandler('start', start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_instagram_link))

    await application.initialize()
    await application.start()
    logging.info("start up successful ……")
    await application.updater.start_polling(drop_pending_updates=True)


async def start_task():
    """|coro|
    以异步方式启动
    """
    return await run()
