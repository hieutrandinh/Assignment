import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Load dữ liệu
df = pd.read_csv('results.csv')
df = df[df['Minutes'] > 900]

# Setup Selenium
driver = webdriver.Chrome()

transfer_values = {}

for player in df['Player']:
    search_url = f"https://www.footballtransfers.com/us/search?query={player.replace(' ', '%20')}"
    driver.get(search_url)
    time.sleep(2)

    try:
        # Click vào cầu thủ đầu tiên trong kết quả tìm kiếm
        player_link = driver.find_element(By.CSS_SELECTOR, 'a.player-name-link')
        player_link.click()
        time.sleep(2)
        # Lấy giá trị chuyển nhượng
        value_elem = driver.find_element(By.CSS_SELECTOR, 'div.transfer-value')
        value = value_elem.text
    except:
        value = 'N/a'

    transfer_values[player] = value

driver.quit()

# Thêm vào dataframe
df['Transfer Value'] = df['Player'].map(transfer_values)

# Lưu file
df.to_csv('transfer_results.csv', index=False)
