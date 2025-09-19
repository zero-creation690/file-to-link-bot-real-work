# main.py

import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Get credentials from environment variables
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BIN_CHANNEL = int(os.environ.get("BIN_CHANNEL"))

app = Client(
    "file_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.media)
async def handle_file_upload(client: Client, message: Message):
    try:
        sent_message = await client.forward_messages(
            chat_id=BIN_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=message.message_id
        )
        bot_username = (await client.get_me()).username
        permanent_link = f"https://t.me/{bot_username}?start=file_{sent_message.message_id}"
        await message.reply_text(
            f"✅ **File uploaded successfully!**\n\nYour permanent link is ready:\n🔗 {permanent_link}",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: `{e}`")

@app.on_message(filters.private & filters.command("start"))
async def handle_start_command(client: Client, message: Message):
    if len(message.command) > 1 and message.command[1].startswith("file_"):
        try:
            file_message_id = int(message.command[1].replace("file_", ""))
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=BIN_CHANNEL,
                message_id=file_message_id
            )
        except Exception as e:
            await message.reply_text(f"I couldn't find that file. An error occurred: `{e}`")
    else:
        await message.reply_text("Hello! Send me any file (up to 2GB) and I will generate a permanent link for it.")

app.run()
