import discord
from discord.ext import commands
from get_data.get_data import get_data_cw,get_data_stock, get_codes, driver, get_danh_sach, get_chi_so_chung

intents = discord.Intents.default()
intents.message_content = True  # Cần bật nếu muốn đọc nội dung tin nhắn

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {bot.user}")

@bot.command()
async def s(ctx):
    full_text = ctx.message.content
    args = full_text[len("!s"):].strip().upper()
    data = 0
    if args == "VNINDEX":
        map_data =  get_chi_so_chung("VNINDEX", driver)
        ma = map_data["ma"]
        index = map_data["index"]
        thay_doi = map_data["thay_doi"]
        ti_le_thay_doi = map_data["ti_le_thay_doi"]
        data = f"Ma:{ma}, Index: {index}, Thay đổi: {thay_doi}, Tỷ lệ thay đổi: {ti_le_thay_doi}"
    elif args == "VN30":
        map_data = get_chi_so_chung("VN30", driver)
        ma = map_data["ma"]
        index = map_data["index"]
        thay_doi = map_data["thay_doi"]
        ti_le_thay_doi = map_data["ti_le_thay_doi"]
        data = f"Ma:{ma}, Index: {index}, Thay đổi: {thay_doi}, Tỷ lệ thay đổi: {ti_le_thay_doi}"
    elif args == "HNXINDEX":
        map_data = get_chi_so_chung("HNXINDEX", driver)
        ma = map_data["ma"]
        index = map_data["index"]
        thay_doi = map_data["thay_doi"]
        ti_le_thay_doi = map_data["ti_le_thay_doi"]
        data = f"Ma:{ma}, Index: {index}, Thay đổi: {thay_doi}, Tỷ lệ thay đổi: {ti_le_thay_doi}"
    elif args == "ALL":
       data = get_danh_sach(driver)
    elif len(args) == 8:
        data = get_data_cw(args, driver)
    elif len(args) == 3:
        data = get_data_stock(args, driver)
    else:
        await ctx.send("Vui lòng nhập mã cổ phiếu hợp lệ hoặc danh sách mã cổ phiếu.")
        return
    
    await ctx.send(f"Dữ liệu: {data}")

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

bot_token = os.getenv("DISCORD_TOKEN")
if not bot_token:
    raise ValueError("DISCORD_TOKEN environment variable is not set")

print(bot_token)
bot.run(bot_token)
