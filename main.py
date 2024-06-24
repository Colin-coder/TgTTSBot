import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application, MessageHandler, filters
import os
from dotenv import load_dotenv
import edge_tts
import datetime

VOICE = "zh-CN-XiaoxiaoNeural"
# OUTPUT_FILE = "test.mp3"

VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-liaoning-XiaobeiNeural",
    "zh-CN-shaanxi-XiaoniNeural",
    "zh-HK-HiuGaaiNeural",
    "zh-HK-HiuMaanNeural",
    "zh-HK-WanLungNeural",
    "zh-TW-HsiaoChenNeural",
    "zh-TW-HsiaoYuNeural",
    "zh-TW-YunJheNeural",
]

# 加载.env文件中的环境变量
load_dotenv()

async def doTTS(update: Update) -> str:
    """Main function"""
    text = update.message.text
    print("get tts text:", text)

    # 获取当前时间
    print("use tts voices: " + VOICE)
    communicate = edge_tts.Communicate(text, VOICE)
    now = datetime.datetime.now()
    time_str = "./cache/" + now.strftime("%H%M%S")
    await communicate.save(time_str)
    return time_str

async def get_tts_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = await doTTS(update)
    print(name)
    text = convert_to_telegram_supported_chars(name)
    # await context.bot.send_message(chat_id=context.job.chat_id,
    #                                 text=f"receive image succeed: {ocr_str}",
    #                                 parse_mode="MarkdownV2")
    await update.message.reply_text(f"receive tts text succeed: {text}")
    await update.message.reply_audio(audio=open(name, 'rb'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("👋 直接发送文字来获取tts结果",
                                    parse_mode="MarkdownV2")
    

async def list_voices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    result = ""
    for index, voice in enumerate(VOICES):
        result += f"{index}. {voice}\n"
    lists_text = convert_to_telegram_supported_chars(result)
    await update.message.reply_text(lists_text,
                                    parse_mode="MarkdownV2")

async def choose_voices(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""

    global VOICE
    index = int(context.args[0])
    VOICE = VOICES[index]

    await update.message.reply_text("success to choose voices: " + convert_to_telegram_supported_chars(VOICE),
                                    parse_mode="MarkdownV2")

async def start_boot(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=context.job.chat_id, text="🚀 *TTS启动中\.\.\.*",
                                   parse_mode="MarkdownV2")
    time.sleep(1)
    await context.bot.send_message(chat_id=context.job.chat_id, text="🎮 *TTS启动完成\!*",
                                   parse_mode="MarkdownV2")

# 替换特殊字符，适配tg发送消息的格式要求
SPECIAL_CHARS = [
    '\\',
    '_',
    '*',
    '[',
    ']',
    '(',
    ')',
    '~',
    '`',
    '>',
    '<',
    '&',
    '#',
    '+',
    '-',
    '=',
    '|',
    '{',
    '}',
    '.',
    '!'
]
def convert_to_telegram_supported_chars(input_string):
    for char in SPECIAL_CHARS:
        input_string = input_string.replace(char, f'\{char}')
    return input_string


def main() -> None:
    tg_api_token = os.getenv('TG_API_TOKEN')
    tg_chat_id = os.getenv('TG_CHAT_ID')
    tg_api_base_url = os.getenv('TG_API_BASE_URL', 'https://api.telegram.org/bot')
    
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().connect_timeout(30).read_timeout(30).base_url(
        base_url=tg_api_base_url).token(tg_api_token).build()
    job_queue = application.job_queue
    job_queue.run_once(start_boot, chat_id=tg_chat_id, when=2)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler(["list"], list_voices))
    application.add_handler(CommandHandler("c", choose_voices))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_tts_audio))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
