from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import webdriver_manager
import pandas as pd
import numpy as np
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime
import mysql.connector

# 連接到 MySQL 資料庫
conn = mysql.connector.connect(
    host="localhost",     # MySQL 伺服器地址 (通常為本地使用 localhost)
    user="root",  # MySQL 使用者名
    password="123456",  # MySQL 密碼
    database="mlb"   # 要連接的資料庫
)

cursor = conn.cursor()

# Step 1: 刪除原有資料
cursor.execute("DROP TABLE IF EXISTS mlb_2020_pitching")  # users2 是資料表名稱
conn.commit()  # 確保刪除操作已儲存
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mlb_2020_pitching (
    `id` INT(10) NOT NULL AUTO_INCREMENT COMMENT '流水號',
    `team` VARCHAR(255) NULL DEFAULT NULL COLLATE 'utf8_general_ci',
	`data-player-uid` VARCHAR(255) UNIQUE NOT NULL COLLATE 'utf8_general_ci',
	`GP` INT(10) NULL DEFAULT NULL,
	`GS` INT(10) NULL DEFAULT NULL,
	`QS` INT(10) NULL DEFAULT NULL,
	`W` INT(10) NULL DEFAULT NULL,
	`L` INT(10) NULL DEFAULT NULL,
	`SV` INT(10) NULL DEFAULT NULL,
	`HLD` INT(10) NULL DEFAULT NULL,
	`IP` DECIMAL(15,4) NULL DEFAULT NULL,
	`H` INT(10) NULL DEFAULT NULL,
	`ER` INT(10) NULL DEFAULT NULL,
	`HR` INT(10) NULL DEFAULT NULL,
	`BB` INT(10) NULL DEFAULT NULL,
	`K` INT(10) NULL DEFAULT NULL,
	`K/9` DECIMAL(15,4) NULL DEFAULT NULL,
	`P/S` DECIMAL(15,4) NULL DEFAULT NULL,
	`WAR` DECIMAL(15,4) NULL DEFAULT NULL,
	`WHIP` DECIMAL(15,4) NULL DEFAULT NULL,
    `ERA` DECIMAL(15,4) NULL DEFAULT NULL,
    `ModifyTime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`data-player-uid`) USING BTREE,
    INDEX `id` (`id`) USING BTREE
    )
    COLLATE='utf8_general_ci'
    ENGINE=InnoDB
''')


chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--headless")  # Run in headless mode if not already doing so


import time
# Set the path to your ChromeDriver
path = "C:/Users/Tony/Desktop/chromedriver-win32/chromedriver.exe"
service = Service(executable_path=path)
driver = webdriver.Chrome(service=service, options=chrome_options)

sheet_name = ['Chicago White Sox','Cleveland Guardians','Detroit Tigers','Kansas City Royals','Minnesota Twins',
              'Baltimore Orioles','Boston Red Sox','New York Yankees','Tampa Bay Rays','Toronto Blue Jays',
              'Houston Astros','Los Angeles Angels','Oakland Athletics','Seattle Mariners','Texas Rangers',
              'Chicago Cubs','Cincinnati Reds','Milwaukee Brewers','Pittsburgh Pirates','St. Louis Cardinals',
              'Atlanta Braves','Miami Marlins','New York Mets','Philadelphia Phillies','Washington Nationals',
              'Arizona Diamondbacks','Colorado Rockies','Los Angeles Dodgers','San Diego Padres','San Francisco Giants'
              ]

web_link_list = [
                {
                    'team': 'Chicago White Sox',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/chw/season/2020/seasontype/2'
                },
                {
                    'team': 'Cleveland Guardians',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/cle/season/2020/seasontype/2'
                },
                {
                    'team': 'Detroit Tigers',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/det/season/2020/seasontype/2'
                },
                {
                    'team': 'Kansas City Royals',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/kc/season/2020/seasontype/2'
                },
                {
                    'team': 'Minnesota Twins',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/min/season/2020/seasontype/2'
                },
                {
                    'team': 'Baltimore Orioles',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/bal/season/2020/seasontype/2'
                },
                {
                    'team': 'Boston Red Sox',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/bos/season/2020/seasontype/2'
                },
                {
                    'team': 'New York Yankees',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/nyy/season/2020/seasontype/2'
                },
                {
                    'team': 'Tampa Bay Rays',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/tb/season/2020/seasontype/2'
                },
                {
                    'team': 'Toronto Blue Jays',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/tor/season/2020/seasontype/2'
                },
                {
                    'team': 'Houston Astros',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/hou/season/2020/seasontype/2'
                },
                {
                    'team': 'Los Angeles Angels',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/laa/season/2020/seasontype/2'
                },
                {
                    'team': 'Oakland Athletics',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/oak/season/2020/seasontype/2'
                },
                {
                    'team': 'Seattle Mariners',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sea/season/2020/seasontype/2'
                },
                {
                    'team': 'Texas Rangers',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/tex/season/2020/seasontype/2'
                },
                {
                    'team': 'Chicago Cubs',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/chc/season/2020/seasontype/2'
                },
                {
                    'team': 'Cincinnati Reds',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/cin/season/2020/seasontype/2'
                },
                {
                    'team': 'Milwaukee Brewers',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/mil/season/2020/seasontype/2'
                },
                {
                    'team': 'Pittsburgh Pirates',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/pit/season/2020/seasontype/2'
                },
                {
                    'team': 'St. Louis Cardinals',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/stl/season/2020/seasontype/2'
                },
                {
                    'team': 'Atlanta Braves',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/atl/season/2020/seasontype/2'
                },
                {
                    'team': 'Miami Marlins',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/mia/season/2020/seasontype/2'
                },
                {
                    'team': 'New York Mets',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/nym/season/2020/seasontype/2'
                },
                {
                    'team': 'Philadelphia Phillies',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/phi/season/2020/seasontype/2'
                },
                {
                    'team': 'Washington Nationals',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/wsh/season/2020/seasontype/2'
                },
                {
                    'team': 'Arizona Diamondbacks',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/ari/season/2020/seasontype/2'
                },
                {
                    'team': 'Colorado Rockies',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/col/season/2020/seasontype/2'
                },
                {
                    'team': 'Los Angeles Dodgers',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/lad/season/2020/seasontype/2'
                },
                {
                    'team': 'San Diego Padres',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sd/season/2020/seasontype/2'
                },
                {
                    'team': 'San Francisco Giants',
                    'url': 'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sf/season/2020/seasontype/2'
                }
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/chw',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/cle/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/det/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/kc/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/min',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/bal/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/bos',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/nyy/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/tb',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/tor',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/hou/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/laa',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/oak',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sea',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/tex',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/chc',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/cin',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/mil/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/pit',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/stl',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/atl/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/mia',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/nym/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/phi/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/wsh',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/ari',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/col',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/lad/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sd/season/2024/seasontype/2',
#                  'https://www.espn.com/mlb/team/stats/_/type/pitching/name/sf'
                 ]
# Initialize an empty dictionary to hold data for each team

# Print the current server time
current_time = datetime.now()
print(current_time)


team_data_dict = {}
# for k in range(0):
for k in range(len(web_link_list)):
    subWebLinkItem = web_link_list[k]
    try:
    
        driver.get(subWebLinkItem['url'])
        print("Page loaded successfully."+ subWebLinkItem['url'])
        time.sleep(3)
        wait = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="fittPageContainer"]/div[2]/div/div[5]/div/div/section/div/div[6]/div[2]/table/thead/tr/th')))
# 獲取文字資料
    #element = driver.find_elements(By., 'data-player-uid')  # 根據需要選擇合適的元素
        player_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "AnchorLink"))) 
        player_elements1 = driver.find_elements(By.XPATH, '//a[@class="AnchorLink fw-bold"]')
        player_elements2 = driver.find_elements(By.XPATH, '//a[@class="AnchorLink"]')
    #player_elements3 = driver.find_elements(By.XPATH, '//td[@class="Table__TD"]/span')
    
    
        all_player_elements = player_elements1 + player_elements2 
    
    
        player_names = [element.text for element in all_player_elements]
        new_player_names = list(dict.fromkeys(player_names)) 
        print(len(new_player_names))
        #--檢查for name in new_player_names:
           #print(name)

        all_player_data = []
    
        for i in range(len(new_player_names)):
            for j in range(18):
                player_row_data = []
                xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div/div[5]/div/div/section/div/div[6]/div[2]/div/div[2]/table/tbody/tr[{i+1}]/td[{j+1}]/span'
                player_elements3= driver.find_elements(By.XPATH, xpath)
                player_element_number1 = [element.text for element in player_elements3]
                all_player_data.append(player_element_number1[0])
           
        chunk_size = 18
        sub_all_player_data = [all_player_data[i:i + chunk_size]for i in range(0,len(all_player_data) , chunk_size)]
        #--檢查print(sub_all_player_data)
        column_names = ['GP', 'GS', 'QS', 'W', 'L', 'SV', 'HLD', 'IP', 'H', 'ER', 'HR', 'BB', 'K', 'K/9', 'P/S', 'WAR', 'WHIP', 'ERA']
        df_stats = pd.DataFrame(sub_all_player_data, columns=column_names)
        df_name = pd.DataFrame(new_player_names, columns=['data-player-uid']) 
        team_name = []
        for k in range(len(new_player_names)):
            team_name.append(subWebLinkItem['team'])
        df_team_name = pd.DataFrame({'team': team_name})
        df_final = pd.concat([df_team_name, df_name, df_stats], axis=1)

        team_data_dict[subWebLinkItem['team']] = df_final

        #print("Page loaded Finished " + subWebLinkItem['team'])
        #team_data_dict_serializable = {team: df.to_dict(orient='records') for team, df in team_data_dict.items()}
        #print("Page loaded. Finished team_data_dict: " + json.dumps(team_data_dict_serializable, indent=4))
        time.sleep(20)
    except TimeoutException:
        print(f"Timeout occurred for {sheet_name[k]}")
    except Exception as e:
        print(f"An error occurred for {sheet_name[k]}: {e}")
        # Store team data into the dictionary
    finally:
        # driver.quit()
    # if player_elements3:
    # # 提取所有元素的文本
    #      number = [element.text for element in player_elements3]
    #      print(number)
        print("### Data Done " + subWebLinkItem['team'] + " ###")
        print("Data Player UID:", new_player_names) 
    #print("Data Player statics:", player_element_number1) 
  #  for index, title in enumerate(element, start=1):  # 為每個標題編號
  #      print(f"{index}. {title.text}")
  #  title_texts = [title.text for title in element]
  #  print("抓取的標題：", title_texts)
   # df = pd.DataFrame(new_player_names, columns=['data-player-uid'])
   # df = pd.DataFrame(player_element_number1, columns=[f"Column {i+1}" for i in range(17)]) 
   # new_df = pd.DataFrame((pd.DataFrame(player_element_number1, columns=['GP','AB','R','H','2B','3B','HR','RBI','TB','BB','SO','SB','AVG','OBP','SLG','OPS','WAR'])))
      #  titles = WebDriverWait(driver, 10).until(
          #  EC.presence_of_all_elements_located((By.CLASS_NAME, 'Table__TD'))
     #   )
# 輸出到 Excel 文件
# Print the current server time
current_time = datetime.now()
print(current_time)
    
excel_file = 'player_uids_2020_pitching.xlsx'
    # df_final.to_excel(excel_file, index=False, engine='openpyxl')
with pd.ExcelWriter(excel_file,engine='openpyxl') as writer:
    for team, df in team_data_dict.items():
        df.to_excel(writer, sheet_name=team, index=False)
        data = [
            tuple(
            [
                *row[:18],  # Add values up to WAR as is
                row[18] if row[18] not in ('INF', '---') else None,  # WHIP conditional handling
                row[19] if row[19] not in ('INF', '---') else None   # ERA conditional handling
            ]
                )
            for row in df[['team', 'data-player-uid', 'GP', 'GS', 'QS', 'W', 'L', 'SV', 'HLD', 'IP', 'H', 'ER', 'HR', 'BB', 'K', 'K/9', 'P/S', 'WAR', 'WHIP', 'ERA']].values
        ]
        # data = [tuple(x) for x in df[['data-player-uid', 'GP', 'GS', 'QS', 'W', 'L', 'SV', 'HLD', 'IP', 'H', 'ER', 'HR', 'BB', 'K', 'K/9', 'P/S', 'WAR', 'WHIP', 'ERA']].values]
# data = [('Alice', 30), ('Bob', 25), ('Charlie', 35), ('David', 22)]
        cursor.executemany("""
        REPLACE INTO mlb_2020_pitching (team, `data-player-uid`, GP, `GS`, QS, W, L, SV, HLD, IP, H, ER, HR, BB, K, `K/9`, `P/S`, `WAR`, `WHIP`, `ERA`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """, data)
        conn.commit()
time.sleep(15)
# 查詢資料表中的所有資料，確認是否插入成功
cursor.execute("SELECT * FROM mlb_2020_pitching")

# 獲取所有的查詢結果
rows = cursor.fetchall()

# 打印查詢結果
for row in rows:
    print(row)

# 關閉游標和資料庫連接
cursor.close()
conn.close()


print("Data scraping complete. Excel file saved.")

# Print the current server time
current_time = datetime.now()
print(current_time)