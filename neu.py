import discord
from discord.ext import commands
from gtts import gTTS
import asyncio
import os
import time
import platform
from keep_alive import keep_alive

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
SPAM_DELAY = 1  # Thời gian tối thiểu giữa 2 lần !talk

# Tự phát hiện đường dẫn FFMPEG
if platform.system() == "Windows":
    FFMPEG_PATH = os.path.join(os.path.dirname(__file__), "bin", "ffmpeg.exe")
else:
    FFMPEG_PATH = "ffmpeg"  # Linux (Render) sẽ dùng ffmpeg cài sẵn
# ===========================================

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Lưu thời gian cuối cùng mỗi user dùng !talk
last_talk_time = {}

# ======= LỆNH TALK =======
@bot.command()
async def talk(ctx, *, text: str):
    now = time.time()
    last_time = last_talk_time.get(ctx.author.id, 0)

    # Chống spam
    if now - last_time < SPAM_DELAY:
        await ctx.send(f"⏳ Vui lòng đợi {SPAM_DELAY} giây giữa các lần !talk")
        return
    last_talk_time[ctx.author.id] = now

    # Kiểm tra user có trong voice không
    if ctx.author.voice is None:
        await ctx.send("❌ Bạn phải ở trong voice channel để dùng lệnh này.")
        return

    voice_channel = ctx.author.voice.channel

    # Nếu bot chưa join thì join
    if ctx.voice_client is None:
        await voice_channel.connect()
    elif ctx.voice_client.channel != voice_channel:
        await ctx.voice_client.move_to(voice_channel)

    # Tạo file âm thanh từ văn bản
    file_path = os.path.join(os.path.dirname(__file__), "tts.mp3")
    tts = gTTS(text=text, lang="vi")
    tts.save(file_path)

    # Phát âm thanh
    vc = ctx.voice_client
    if vc.is_playing():
        vc.stop()
    vc.play(discord.FFmpegPCMAudio(executable=FFMPEG_PATH, source=file_path))
    await ctx.send(f"🗣️ Bot đang nói: **{text}**")

@bot.command()
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Bot đã rời voice channel.")

keep_alive()
bot.run(TOKEN)
