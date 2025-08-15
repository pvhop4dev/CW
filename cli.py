import os
import logging
from get_data.get_data import get_data_cw, get_data_stock, get_codes, get_driver, get_danh_sach, get_chi_so_chung
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def print_help():
    """Print help information."""
    help_text = """
📚 Hướng dẫn sử dụng:

🔹 Xem thông tin cổ phiếu:
   Nhập mã cổ phiếu (VD: VNM, FPT)

🔹 Xem thông tin chứng quyền:
   Nhập mã CW (8 ký tự, VD: FPTB1C001)

🔹 Xem chỉ số chứng khoán:
   Nhập VNINDEX, VN30, hoặc HNXINDEX

🔹 Xem danh sách mã:
   Nhập ALL

🔹 Thoát chương trình:
   Nhập exit hoặc quit

📌 Lưu ý:
• Nhập chính xác mã chứng khoán
• Dữ liệu được cập nhật theo thời gian thực
"""
    print(help_text)

def process_input(content):
    """Process user input and return the result."""
    content = content.strip().upper()
    driver = get_driver()
    try:
        # Process index
        if content in ["VNINDEX", "VN30", "HNXINDEX"]:
            map_data = get_chi_so_chung(content, driver)
            response = (
                f"\n {map_data['ma']}\n"
                f"G: {map_data['index']}\n"
                f"T: {map_data['thay_doi']}\n"
                f"TL: {map_data['ti_le_thay_doi']}\n"
            )
            return response
            
        # Process ALL command
        if content == "ALL":
            response = get_danh_sach(driver)
            return f"\n{response}\n"
            
        # Process CW code (8 characters)
        if len(content) == 8:
            data = get_data_cw(content, driver)
            response = (
                f"\n {data['code']}\n"
                f"G: {data['gia']}\n"
                f"T: {data['thay_doi']}\n"
                f"Base: {data['base_stock']}\n"
                f"HV: {data['gia_hoa_von']}\n"
                f"TL HV: {data['ti_le_gia_hoa_von']}\n"
                f"SNĐH: {data['so_ngay_den_han']}\n"
            )
            return response
            
        # Process stock code (3 characters)
        if len(content) == 3:
            data = get_data_stock(content, driver)
            response = (
                f"\n {data['code']}\n"
                f"G: {data['gia']}\n"
                f"T: {data['thay_doi']}\n"
                f"N: {data['nuoc_ngoai']}\n"
            )
            return response
            
        # Help command
        if content in ["HELP", "HUONGDAN"]:
            return ""
            
        # Invalid input
        return "\n❌ Mã không hợp lệ. Vui lòng nhập mã cổ phiếu (3 ký tự), mã CW (8 ký tự), hoặc các lệnh hỗ trợ.\nGõ HELP để xem hướng dẫn sử dụng.\n"
        
    except Exception as e:
        logger.error(f"Error processing input: {e}", exc_info=True)
        return "\n❌ Có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại.\n"

def main():
    """Main function to run the CLI application."""
    # Load environment variables
    load_dotenv()
    
    
    while True:
        try:
            user_input = input("Nhập: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'thoat']:
                break
                
            # Process the input
            if user_input.upper() in ['HELP', 'HUONGDAN']:
                print_help()
            else:
                result = process_input(user_input)
                print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            print("\n❌ Có lỗi không mong muốn xảy ra. Vui lòng thử lại.\n")

if __name__ == "__main__":
    main()
