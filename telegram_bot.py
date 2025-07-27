import os
import asyncio
import logging
from functools import partial
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from get_data.get_data import get_data_cw, get_data_stock, get_codes, driver, get_danh_sach, get_chi_so_chung
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable is not set")

# Command handlers
async def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    welcome_text = (
        "🤖 *Chào mừng đến với Bot Chứng Khoán!*\n\n"
        "📌 *Các lệnh hỗ trợ:*\n"
        "• Gõ mã cổ phiếu (VD: `VNM`, `FPT`) - Xem thông tin cổ phiếu\n"
        "• Gõ mã CW (8 ký tự) - Xem thông tin chứng quyền\n"
        "• Gõ `VNINDEX`, `VN30`, `HNXINDEX` - Xem chỉ số\n"
        "• Gõ `ALL` - Xem danh sách mã\n"
        "• /help - Xem hướng dẫn sử dụng"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "📚 *Hướng dẫn sử dụng:*\n\n"
        "🔹 *Xem thông tin cổ phiếu:*\n"
        "Gõ mã cổ phiếu (VD: `VNM`, `FPT`)\n\n"
        "🔹 *Xem thông tin chứng quyền:*\n"
        "Gõ mã CW (8 ký tự, VD: `FPTB1C001`)\n\n"
        "🔹 *Xem chỉ số chứng khoán:*\n"
        "Gõ `VNINDEX`, `VN30`, hoặc `HNXINDEX`\n\n"
        "🔹 *Xem danh sách mã:*\n"
        "Gõ `ALL`\n\n"
        "📌 *Lưu ý:*\n"
        "• Nhập chính xác mã chứng khoán\n"
        "• Dữ liệu được cập nhật theo thời gian thực"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle user messages."""
    content = update.message.text.strip().upper()
    chat_id = update.effective_chat.id
    
    # Show typing action
    await context.bot.send_chat_action(chat_id=chat_id, action="typing")
    
    try:
        # Process index
        if content in ["VNINDEX", "VN30", "HNXINDEX"]:
            map_data = await asyncio.to_thread(get_chi_so_chung, content, driver)
            response = (
                f"📊 *{map_data['ma']}*\n"
                f"📈 Giá: `{map_data['index']}`\n"
                f"🔄 Thay đổi: `{map_data['thay_doi']}`\n"
                f"📉 Tỷ lệ: `{map_data['ti_le_thay_doi']}`"
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            return
            
        # Process ALL command
        if content == "ALL":
            response = await asyncio.to_thread(get_danh_sach, driver)
            if len(response) > 4096:  # Telegram message length limit
                for x in range(0, len(response), 4096):
                    await update.message.reply_text(response[x:x+4096], parse_mode='Markdown')
            else:
                await update.message.reply_text(response, parse_mode='Markdown')
            return
            
        # Process CW code (8 characters)
        if len(content) == 8:
            data = await asyncio.to_thread(get_data_cw, content, driver)
            response = (
                f"📌 *{data['code']}*\n"
                f"💰 Giá: `{data['gia']}`\n"
                f"🔄 Thay đổi: `{data['thay_doi']}`\n"
                f"🏢 Cơ sở: `{data['base_stock']}`\n"
                f"⚖️ Giá hòa vốn: `{data['gia_hoa_von']}`\n"
                f"📊 Tỷ lệ hòa vốn: `{data['ti_le_gia_hoa_von']}`\n"
                f"⏳ Số ngày đến hạn: `{data['so_ngay_den_han']}`"
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            return
            
        # Process stock code (3 characters)
        if len(content) == 3:
            data = await asyncio.to_thread(get_data_stock, content, driver)
            response = (
                f"📈 *{data['code']}*\n"
                f"💰 Giá: `{data['gia']}`\n"
                f"🔄 Thay đổi: `{data['thay_doi']}`\n"
                f"🌍 Nước ngoài: `{data['nuoc_ngoai']}`"
            )
            await update.message.reply_text(response, parse_mode='Markdown')
            return
            
        # Invalid input
        await update.message.reply_text(
            "❌ Mã không hợp lệ. Vui lòng nhập mã cổ phiếu (3 ký tự), mã CW (8 ký tự), hoặc các lệnh hỗ trợ.\n"
            "Gõ /help để xem hướng dẫn sử dụng."
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại sau."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Handle all text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()