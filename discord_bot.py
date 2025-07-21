import discord
from get_data.get_data import get_data_cw, get_data_stock, get_codes, driver, get_danh_sach, get_chi_so_chung

import os
from dotenv import load_dotenv


load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập với tên: {client.user}")

@client.event
async def on_message(message):
    # Không trả lời tin nhắn của chính bot
    if message.author == client.user:
        return

    # Lấy nội dung tin nhắn
    content = message.content.strip().upper()
    print(f"Processing message: {content}")
    try:
        # Xử lý chỉ số
        if content in ["VNINDEX", "VN30", "HNXINDEX"]:
            map_data = get_chi_so_chung(content, driver)
            response = f"Ma:{map_data['ma']}, Index: {map_data['index']}, Thay đổi: {map_data['thay_doi']}, Tỷ lệ thay đổi: {map_data['ti_le_thay_doi']}"
            await message.channel.send(response)
            return

        # Xử lý danh sách
        if content == "ALL":
            response = get_danh_sach(driver)
            await message.channel.send(response)
            return

        # Xử lý mã chứng khoán
        if len(content) == 8:  # Mã CW
            data = get_data_cw(content, driver)
            response = f"Mã: {data['code']}, Giá: {data['gia']}, Thay đổi: {data['thay_doi']}, Cơ sở: {data['base_stock']}, Giá hòa vốn: {data['gia_hoa_von']}, Tỷ lệ hòa vốn: {data['ti_le_gia_hoa_von']}, Số ngày đến hạn: {data['so_ngay_den_han']}"
            await message.channel.send(response)
            return

        if len(content) == 3:  # Mã cổ phiếu thường
            data = get_data_stock(content, driver)
            response = f"Mã: {data['code']}, Giá: {data['gia']}, Thay đổi: {data['thay_doi']}, Nước ngoài: {data['nuoc_ngoai']}"
            await message.channel.send(response)
            return

        # Nếu không hợp lệ
        await message.channel.send("Vui lòng nhập mã cổ phiếu hợp lệ hoặc danh sách mã cổ phiếu.")

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.channel.send("Xảy ra lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.")


# Get token and run bot
bot_token = os.getenv("DISCORD_TOKEN")
if not bot_token:
    raise ValueError("DISCORD_TOKEN environment variable is not set")


if __name__ == "__main__":
    print("Bot is running...")
    client.run(bot_token)
    