import os
import time
import requests
import logging
from tqdm import tqdm
from pyrogram import Client, filters
from datetime import datetime, timedelta

# 🔹 Telegram Bot Credentials
API_ID = 25637343
API_HASH = "70fb79a89ec2d30cab05704e817e5be6"
BOT_TOKEN = "7339282485:AAE5EtsGRTbv6XFtY14ZLubJV6n7eA1fuOg"

# 🔹 APIs
TERABOX_API = "http://ashlynn.serv00.net/terapre.php?url="

# 🔹 Download Folder
DOWNLOAD_PATH = "downloads"
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# 🔹 Logging Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# 🔹 Pyrogram Bot Client
bot = Client("terabox_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🔹 Start Command
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 Welcome! Send me one or more TeraBox links, and I'll fetch the videos for you.")

# 🔹 Process TeraBox Links
@bot.on_message(filters.text)
async def process_terabox_links(client, message):
    user_message = message.text.strip()
    links = user_message.split()

    if not all("terabox" in link for link in links):
        await message.reply_text("❌ Please send valid TeraBox links.")
        return

    await message.reply_text(f"⏳ Processing {len(links)} links, please wait...")

    for link in links:
        await message.reply_text(f"🔍 Fetching video for: {link}...")

        # 🔹 Get Video Link from TeraBox API
        api_url = f"{TERABOX_API}{link}"
        response = requests.get(api_url)

        if response.status_code == 200:
            video_link = response.text.strip()

            if video_link.startswith("http"):
                file_name = video_link.split("/")[-1]
                file_path = os.path.join(DOWNLOAD_PATH, file_name)

                # 🔹 Check File Size (Max 4GB)
                file_size = get_file_size(video_link)
                if file_size > 4 * 1024 * 1024 * 1024:
                    await message.reply_text(f"⚠️ File is too large for Telegram. Download it here: {video_link}")
                    continue
                
                # 🔹 Download and Upload to Telegram
                await message.reply_text("📥 Downloading video, please wait...")
                download_video(video_link, file_path)

                await message.reply_text("📤 Uploading video to Telegram...")
                await send_video(client, message.chat.id, file_path, file_name)

                # ✅ Auto-delete file after upload
                os.remove(file_path)
            else:
                await message.reply_text("⚠️ Failed to fetch video link. Try again later.")
        else:
            await message.reply_text("🚨 Error fetching video from TeraBox.")

# 🔹 Function to Download Video
def download_video(url, save_path):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))

    with open(save_path, "wb") as file, tqdm(
        desc="Downloading",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(1024 * 1024):
            file.write(chunk)
            bar.update(len(chunk))

# 🔹 Function to Upload Video to Telegram
async def send_video(client, chat_id, file_path, file_name):
    with open(file_path, "rb") as video_file:
        await client.send_video(chat_id, video=video_file, caption=f"🎥 {file_name}")

# 🔹 Function to Get File Size
def get_file_size(url):
    response = requests.head(url)
    return int(response.headers.get("content-length", 0))

# 🔹 Start Bot
bot.run()
