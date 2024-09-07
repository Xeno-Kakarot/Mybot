import yt_dlp
import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import Config  # Import configurations from config.py

# Initialize the Pyrogram client
app = Client("video_downloader", bot_token=Config.BOT_TOKEN)

# Helper function for downloading YouTube videos
def download_youtube_video(url, format="video"):
    ydl_opts = {
        "outtmpl": "downloads/%(title)s.%(ext)s",
        "cookiefile": "cookies.txt",  # Add your cookies file here for YouTube
    }

    if format == "audio":
        ydl_opts["format"] = "bestaudio"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_file = ydl.prepare_filename(info_dict)
    return video_file


# Helper function for downloading Instagram Reels
def download_instagram_reel(url):
    api_url = f"https://some-instagram-api.com/download?url={url}"  # Example
    response = requests.get(api_url)
    
    reel_file = "downloads/insta_reel.mp4"
    with open(reel_file, 'wb') as f:
        f.write(response.content)
    
    return reel_file


# Helper function for downloading Tera Box files
def download_tera_box(url):
    response = requests.get(url)
    
    file_name = "downloads/tera_box_file"
    with open(file_name, 'wb') as f:
        f.write(response.content)

    return file_name


# Command to download YouTube Shorts or videos
@app.on_message(filters.command("yt"))
async def youtube_handler(client, message):
    try:
        url = message.text.split(" ", 1)[1]
        
        with yt_dlp.YoutubeDL() as ydl:
            info_dict = ydl.extract_info(url, download=False)
            video_type = info_dict.get("categories", [])

        if "Shorts" in video_type:
            await message.reply_text("Downloading YouTube Short...")
            video_path = download_youtube_video(url)
            await message.reply_video(video_path)
        else:
            # Regular YouTube video: provide buttons for audio or video download
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("Download Audio", callback_data=f"audio|{url}"),
                 InlineKeyboardButton("Download Video", callback_data=f"video|{url}")]
            ])
            await message.reply_text("Select download format:", reply_markup=buttons)
    except IndexError:
        await message.reply_text("Please provide a valid YouTube URL.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


# Handle the inline button callbacks for audio/video download
@app.on_callback_query(filters.regex(r"^(audio|video)\|"))
async def youtube_callback(client, callback_query):
    format_type, url = callback_query.data.split("|")
    await callback_query.message.edit_text(f"Downloading YouTube {format_type}...")

    video_path = download_youtube_video(url, format=format_type)
    
    if format_type == "audio":
        await callback_query.message.reply_audio(video_path)
    else:
        await callback_query.message.reply_video(video_path)


# Command to download Instagram Reels automatically from a link
@app.on_message(filters.regex(r"https?://(www\.)?instagram\.com/reel/"))
async def insta_handler(client, message):
    url = message.text
    await message.reply_text("Downloading Instagram reel...")

    try:
        reel_path = download_instagram_reel(url)
        await message.reply_video(reel_path)
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


# Handle edited messages and delete if not from the owner
@app.on_message(filters.edited)
async def handle_edited_message(client, message: Message):
    if message.from_user.id != Config.OWNER_ID:
        await message.delete()
        await client.send_message(
            message.chat.id, 
            "Edited message deleted. Only the owner can edit messages."
        )


# Tera Box feature to download files from a link
@app.on_message(filters.command("tera_box"))
async def tera_box_handler(client, message):
    try:
        url = message.text.split(" ", 1)[1]
        await message.reply_text("Downloading from Tera Box...")
        
        # Call the Tera Box download function
        file_path = download_tera_box(url)
        await message.reply_document(file_path)
    except IndexError:
        await message.reply_text("Please provide a valid Tera Box link.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")


# Start the bot
app.run()
