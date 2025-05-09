import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# --- Phần 1: Thu thập giá trị chuyển nhượng cầu thủ ---

# Đọc dữ liệu từ results.csv
df = pd.read_csv("results.csv")
df.columns = df.columns.str.lower()  # Đảm bảo cột được viết thường

# Lọc cầu thủ có thời gian thi đấu > 900 phút
df_filtered = df[df["minutes"] > 900]
players_needed = set(df_filtered["player"].str.strip())

# Cấu hình Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
service = Service(executable_path=r"C:\Users\VIETTELSTORE\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(options=chrome_options, service=service)

# URL của các trang cần truy cập
base_url = "https://www.footballtransfers.com/us/values/players/most-valuable-soccer-players/playing-in-uk-premier-league/"

# Danh sách để lưu kết quả
transfer_data = []

# Lấy dữ liệu từ các trang 1 đến 22
for page in range(1, 23):
    driver.get(f"{base_url}{page}")
    time.sleep(3)

    # Lấy tất cả tên cầu thủ và giá trị chuyển nhượng
    players = driver.find_elements(By.XPATH, "//td[contains(@class, 'td-player')]//a")
    values = driver.find_elements(By.XPATH, "//td[contains(@class, 'text-center')]//span[contains(@class, 'player-tag')]")

    for player, value in zip(players, values):
        player_name = player.text.strip()
        transfer_value = value.text.strip()

        # Kiểm tra nếu cầu thủ có trong danh sách đã lọc
        if player_name.lower() in [p.lower() for p in players_needed]:
            transfer_data.append({
                "Player": player_name,
                "Value": transfer_value
            })

# Lưu kết quả vào file CSV
transfer_df = pd.DataFrame(transfer_data)
transfer_df.to_csv("transfer_values.csv", index=False)

# Đóng trình duyệt
driver.quit()

print("Lấy dữ liệu thành công và lưu vào file 'transfer_values.csv'.")