import os
from pyrogram import Client, filters
from pyrogram.types import Message
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Hardcoded credentials and IDs
# WARNING: DO NOT share these values or upload to a public repository.
API_ID = 20288994
API_HASH = "d702614912f1ad370a0d18786002adbf"
BOT_TOKEN = "8303908376:AAEL1dL0BjpmpbdYjZ5yQmgb1UJLa_OMbGk"
BIN_CHANNEL = -1002995694885

app = Client(
    "file_link_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.private & filters.media)
async def handle_file_upload(client: Client, message: Message):
    """
    Handles file uploads, forwards to a bin channel, and provides a permanent link.
    """
    logging.info(f"Received file from user {message.from_user.id}")
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
            disable_web_page_preview=True,
            quote=True
        )
        logging.info(f"Generated link for file ID {sent_message.message_id}")
    except Exception as e:
        logging.error(f"Error handling file upload: {e}")
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
            
            # The copy_message method is used to forward the file without a "Forwarded from" tag
            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=BIN_CHANNEL,
                message_id=file_message_id
            )
        except Exception as e:
            logging.error(f"Error fetching file from link: {e}")
            await message.reply_text(f"I couldn't find that file. An error occurred: `{e}`")
    else:
        # Welcome message for the regular /start command
        welcome_message = (
            "Hello! 👋\n\n"
            "I'm a file-to-link bot. I can help you generate permanent links for your files.\n\n"
            "Just send me any file (up to 2GB), and I will provide you with a unique link that you can share with anyone. "
            "When someone clicks the link, I will send them the file instantly."
        )
        await message.reply_text(welcome_message)

if __name__ == "__main__":
    logging.info("Starting bot...")
    app.run()

