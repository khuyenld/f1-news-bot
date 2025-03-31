import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio

# Load biến môi trường từ .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID của kênh text

# Khởi tạo bot với intents cần thiết
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Danh sách các tin nhắn đã lên lịch
scheduled_messages = []

# Lệnh để lên lịch gửi tin nhắn
@bot.command()
async def schedule(ctx, date: str, time: str, *, message: str):
    """Lên lịch gửi tin nhắn. Ví dụ: !schedule 04-04-2025 09:00 Chào buổi sáng!"""
    try:
        # Chuyển đổi ngày giờ thành datetime object
        send_time = datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M")
        
        # Kiểm tra nếu thời gian hợp lệ
        now = datetime.now()
        if send_time <= now:
            await ctx.send("⚠️ Thời gian không hợp lệ! Hãy nhập một thời điểm trong tương lai.")
            return
        
        # Lưu vào danh sách lịch trình
        scheduled_messages.append((send_time, message, ctx.channel.id))
        await ctx.send(f"✅ Đã lên lịch gửi tin nhắn vào **{date} {time}**.")
    
    except ValueError:
        await ctx.send("❌ Sai định dạng! Dùng lệnh như sau: `!schedule DD-MM-YYYY HH:MM Nội dung`")

# Kiểm tra tin nhắn đã lên lịch
@tasks.loop(seconds=10)
async def check_scheduled_messages():
    """Kiểm tra và gửi tin nhắn đúng giờ"""
    now = datetime.now()
    for item in scheduled_messages[:]:
        send_time, message, channel_id = item
        if now >= send_time:
            channel = bot.get_channel(channel_id)
            if channel:
                await channel.send(f"@everyone {message}")  # Mention everyone
            scheduled_messages.remove(item)  # Xóa khỏi danh sách sau khi gửi

# Bắt đầu kiểm tra khi bot khởi động
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} đã online!")
    check_scheduled_messages.start()

# Chạy bot
bot.run(TOKEN)
