import os
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Hardcoded credentials and IDs
API_ID = 20288994
API_HASH = "d702614912f1ad370a0d18786002adbf"
BOT_TOKEN = "8303908376:AAEL1dL0BjpmpbdYjZ5yQmgb1UJLa_OMbGk"
BIN_CHANNEL = -1002995694885
CHANNEL = "https://t.me/AV_BOTz_UPDATE" # Your updates channel link
START_TIME = time.time()

# Dummy database placeholders (you would replace this with a real DB)
async def get_total_users():
    return 100 # Replace with actual DB query

async def get_total_files():
    return 500 # Replace with actual DB query

app = Client(
    "file_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.command("ping"))
async def ping_command(client, message):
    uptime = time.time() - START_TIME
    uptime_minutes = int(uptime / 60)
    uptime_seconds = int(uptime % 60)
    await message.reply_text(f"🚀 Bot is running!\nUptime: `{uptime_minutes}` minutes, `{uptime_seconds}` seconds.")

@app.on_message(filters.private & filters.command("stats"))
async def stats_command(client, message):
    total_users = await get_total_users()
    total_files = await get_total_files()
    await message.reply_text(f"📊 **Bot Statistics**\n\nTotal Users: `{total_users}`\nTotal Files Stored: `{total_files}`")


@app.on_message(filters.private & filters.media)
async def handle_file_upload(client: Client, message: Message):
    """
    Handles file uploads, forwards to a bin channel, and provides a permanent link.
    """
    logging.info(f"Received media from user {message.from_user.id}")

    if not (message.document or message.video or message.photo or message.audio):
        await message.reply_text("This is not a supported file type. Please send a document, video, photo, or audio file.")
        logging.warning("Received an unsupported media type.")
        return

    try:
        sent_message = await client.forward_messages(
            chat_id=BIN_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=message.message_id
        )

        if not sent_message or not hasattr(sent_message, 'message_id'):
            logging.error("Forwarding message failed. Returned object has no 'message_id'.")
            await message.reply_text("An error occurred while storing your file. Please check bot's channel permissions.")
            return

        bot_username = (await client.get_me()).username
        permanent_link = f"https://t.me/{bot_username}?start=file_{sent_message.message_id}"
        
        await message.reply_text(
            f"✅ **File uploaded successfully!**\n\nYour permanent link is ready:\n🔗 {permanent_link}",
            disable_web_page_preview=True,
            quote=True
        )
        logging.info(f"Generated link for file ID {sent_message.message_id}")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await message.reply_text(f"An error occurred: `{e}`")

@app.on_message(filters.private & filters.command("start"))
async def handle_start_command(client: Client, message: Message):
    """
    Handles the /start command, including permanent file links.
    """
    if len(message.command) > 1 and message.command[1].startswith("file_"):
        logging.info(f"User {message.from_user.id} requested file from link.")
        try:
            file_message_id = int(message.command[1].replace("file_", ""))
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=BIN_CHANNEL,
                message_id=file_message_id
            )
        except Exception as e:
            logging.error(f"Error fetching file from link: {e}")
            await message.reply_text(f"I couldn't find that file. An error occurred: `{e}`")
    else:
        welcome_message = (
            "Hello! 👋\n\n"
            "I'm a file-to-link bot. I can help you generate permanent links for your files.\n\n"
            "Just send me any file (up to 2GB), and I will provide you with a unique link that you can share. "
            "When someone clicks the link, I will send them the file instantly."
        )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Visit Channel", url=CHANNEL)
                ]
            ]
        )
        await message.reply_text(welcome_message, reply_markup=keyboard)

if __name__ == "__main__":
    logging.info("Starting bot...")
    app.run()
