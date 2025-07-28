from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
import os
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('--disable-web-security')
chrome_options.add_argument('--allow-running-insecure-content')
chrome_options.add_argument('--headless=new')  # Use new headless mode
chrome_options.add_argument('--no-sandbox')  # Required for running in Docker/containers
chrome_options.add_argument('--disable-dev-shm-usage')  # Required for running in Docker/containers
chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
chrome_options.add_argument('--disable-software-rasterizer')  # Disable software rasterizer

service = ChromeService(ChromeDriverManager().install())

driver = webdriver.Chrome(
    service=service,
    options=chrome_options
)



def get_data_cw(code, driver):
    print(f"Processing code: {code}")
    driver.get(f"https://finance.vietstock.vn/chung-khoan-phai-sinh/{code}/cw-tong-quan.htm")
    time.sleep(0.5)  # Wait for the page to load
    gia = None
    selectors = [
        "#stockprice > span.price.txt-green",
        "#stockprice > span.price.txt-red",
        "#stockprice > span.price.txt-orange"
    ]
    for selector in selectors:
        try:
            gia = driver.find_element(By.CSS_SELECTOR, selector).text
            if gia:
                break
        except:
            continue
    thay_doi = driver.find_element(By.ID, "stockchange").text
    base_stock = driver.find_element(By.ID, "basestock").text
    gia_thuc_hien = driver.find_element(By.CSS_SELECTOR, "#page-content > div > div.row.m-b.stock-row > div.col-xs-24.col-md-14.m-b-xs.stock-cell > div.bt3.m-b > div > div.col-xs-24.col-sm-6.col-md-6.col-c-last.m-b > div > div > p:nth-child(2) > b").text
    gia_hoa_von = driver.find_element(By.ID, "breakeven").text
    khoi_luong = driver.find_element(By.ID, "totalvol").text
    so_ngay_den_han = driver.find_element(By.CSS_SELECTOR, "#page-content > div > div.row.m-b.stock-row > div.col-xs-24.col-md-14.m-b-xs.stock-cell > div.bt3.m-b > div > div:nth-child(3) > p:nth-child(5) > b").text

    gia = int(gia.replace(",", ""))
    gia_hoa_von= int(gia_hoa_von.replace(",", ""))
    base_stock = int(base_stock.replace(",", ""))
    gia_lech  = gia_hoa_von - base_stock
    ti_le_gia_hoa_von =  round((gia_hoa_von / base_stock - 1) * 100, 2)
    return {
        "code": code,
        "gia": gia,
        "thay_doi": thay_doi,
        "base_stock": base_stock,
        "gia_thuc_hien": gia_thuc_hien,
        "gia_hoa_von": gia_hoa_von,
        "gia_lech": gia_lech,
        "khoi_luong": khoi_luong,
        "ti_le_gia_hoa_von": str(ti_le_gia_hoa_von) + "%",
        "so_ngay_den_han": so_ngay_den_han,
        "dang_chu_y": ""
    }


def get_codes(driver):
    driver.get("https://banggia.vndirect.com.vn/chung-khoan/chung-quyen")
    time.sleep(0.5)  # Đợi trang load và JS render xong

    content = driver.page_source
    codes = re.findall(r'\b[A-Z]{4}\d{4}\b', content)
    unique_codes = sorted(set(codes))

    with open("codes.txt", "w", encoding="utf-8") as f:
        f.write('[' + ','.join(f'"{code}"' for code in unique_codes) + ']')

    print("Total unique codes found:", len(unique_codes))
    # unique_codes = ["CHPG2502","CMBB2407"]
    return unique_codes



def get_data_stock(code, driver):
    print(f"Processing code: {code}")
    driver.get(f"https://finance.vietstock.vn/{code}/ho-so-doanh-nghiep.htm")
    time.sleep(0.5)  # Wait for the page to load
    gia = None
    selectors = [
        "#stockprice > span.txt-orange.price",
        "#stockprice > span.txt-red.price",
        "#stockprice > span.txt-green.price"
    ]
    for selector in selectors:
        try:
            gia = driver.find_element(By.CSS_SELECTOR, selector).text
            if gia:
                break
        except:
            continue
    gia = int(gia.replace(",", ""))
    thay_doi = driver.find_element(By.ID, "stockchange").text
    nuoc_ngoai = driver.find_element(By.ID, "foreignBuy").text


    return {
        "code": code,
        "gia": gia,
        "thay_doi": thay_doi,
        "nuoc_ngoai": nuoc_ngoai
    }
 # Read CSV file with proper delimiter and column names
danh_sach_df = pd.read_csv("danh_sach.csv")

def get_danh_sach(driver):
    full_danh_muc = ""
    tong_thay_doi = 0
    
   

    # Process each row in the DataFrame
    for _, row in danh_sach_df.iterrows():
        ma = str(row["ma"]).strip().upper()
        so_luong = int(row["so_luong"])
        
        if ma.startswith("C") and len(ma) == 8:
            try:
                data_cw = get_data_cw(ma, driver)
                gia = data_cw["gia"]
                thay_doi = data_cw["thay_doi"]
                gia_thay_doi = thay_doi.split('(')[0].strip()
                gia_thay_doi = int(gia_thay_doi.replace(",", ""))
                
                tong_thay_doi += gia_thay_doi * so_luong
                
                full_danh_muc += f"{ma}  {gia} {thay_doi} {so_luong}\n"
            except Exception as e:
                print(f"Error processing code {ma}: {e}")
        else:
            try:
                data_stock = get_data_stock(ma, driver)
                gia = data_stock["gia"]
                so_luong = int(so_luong)
                thay_doi = data_stock["thay_doi"]
                gia_thay_doi = thay_doi.split('(')[0].strip()
                gia_thay_doi = int(gia_thay_doi.replace(",", ""))
                tong_thay_doi += gia_thay_doi * so_luong

                full_danh_muc += f"{ma} {gia} {thay_doi} {so_luong}\n"
            except Exception as e:
                print(f"Error processing code {ma}: {e}")
                
    vnindex = get_chi_so_chung("VNINDEX", driver)
    full_danh_muc += f"VNINDEX: {vnindex['index']} {vnindex['thay_doi']} ({vnindex['ti_le_thay_doi']})\n"
    vn30 = get_chi_so_chung("VN30", driver)
    full_danh_muc += f"VN30: {vn30['index']} {vn30['thay_doi']} ({vn30['ti_le_thay_doi']})\n"


    tong_thay_doi = int(tong_thay_doi)
    tong_thay_doi = f"{tong_thay_doi:,}"
    full_danh_muc += f"Tổng thay đổi: {tong_thay_doi}\n"
    print(full_danh_muc)
    return full_danh_muc


def get_chi_so_chung(ma, driver):
    exchange = 0
    ma = ma.strip().upper()
    if ma == "VNINDEX":
        exchange = 1
    elif ma == "VN30":
        exchange = 4
    elif ma == "HNXINDEX":
        exchange = 2
    elif ma == "UPCOM":
        exchange = 3
    elif ma == "HNX30":
        exchange = 5
    else:
        raise ValueError("Mã chỉ số không hợp lệ. Vui lòng sử dụng VNINDEX, VN30, HNX, UPCOM hoặc HNX30.")
    url= f"https://finance.vietstock.vn/ket-qua-giao-dich?exchange={exchange}"
    print(f"Fetching data for index: {ma}")
    driver.get(url)
    time.sleep(0.5)  # Wait for the page to load
    index = driver.find_element(By.CSS_SELECTOR, "#trading-result > div > div.row > div.col-sm-10.col-md-10 > div > div.v-cell.col-110.text-center > h2 > b").text

    thay_doi = driver.find_element(By.CSS_SELECTOR, "#trading-result > div > div.row > div.col-sm-10.col-md-10 > div > div.v-cell.col-110.text-center > div > span:nth-child(1)").text
    ti_le_thay_doi = driver.find_element(By.CSS_SELECTOR, "#trading-result > div > div.row > div.col-sm-10.col-md-10 > div > div.v-cell.col-110.text-center > div > span.m-l").text
    print(f"Ma:{ma}, Index: {index}, Thay đổi: {thay_doi}, Tỷ lệ thay đổi: {ti_le_thay_doi}")
    return {
        "ma": ma,
        "index": index,
        "thay_doi": thay_doi,
        "ti_le_thay_doi": ti_le_thay_doi
    }