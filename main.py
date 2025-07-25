from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
from get_data.get_data import get_data_cw, get_codes, driver




unique_codes = get_codes(driver)
# unique_codes = ["CMBB2501","CMBB2502"]
data = []
i = 0
for code in unique_codes:
    try:
        i += 1
        print(f"Processing code {i}/{len(unique_codes)}: {code}")
        data.append(get_data_cw(code, driver))
    except Exception as e:
        print(f"Error processing code {code}: {e}")


driver.quit()


df = pd.DataFrame(data)
timex = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
filename = f"./data/data_{timex}.xlsx"
df.to_excel(filename, index=False)