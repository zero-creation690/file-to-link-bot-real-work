import os
from pyrogram import Client, filters
from pyrogram.types import Message
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get credentials from environment variables.
# The `or None` part ensures the script doesn't crash if a variable is missing,
# but the `int()` conversion will still raise an error, which is good for debugging.
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BIN_CHANNEL = os.environ.get("BIN_CHANNEL")

# Validate required environment variables
if not all([API_ID, API_HASH, BOT_TOKEN, BIN_CHANNEL]):
    logging.error("One or more required environment variables are missing.")
    # Exiting with code 1 will tell Koyeb that the application failed to start.
    exit(1)

# Convert string IDs to integers
try:
    API_ID = int(API_ID)
    BIN_CHANNEL = int(BIN_CHANNEL)
except (ValueError, TypeError) as e:
    logging.error(f"Failed to convert API_ID or BIN_CHANNEL to integer: {e}")
    exit(1)

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
        await message.reply_text("Hello! Send me any file (up to 2GB) and I will generate a permanent link for it.")

if __name__ == "__main__":
    logging.info("Starting bot...")
    app.run()
