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
from tabulate import tabulate
from openpyxl import load_workbook
year = 2024 #注意改年分 (2010-2012年的球隊分區有變動) 2024年後會有變動
# 連接到 MySQL 資料庫
conn = mysql.connector.connect(
    host="localhost",     # MySQL 伺服器地址 (通常為本地使用 localhost)
    user="root",  # MySQL 使用者名
    password="123456",  # MySQL 密碼
    database="mlb"   # 要連接的資料庫
)

cursor = conn.cursor()
#根據數據的欄位非當年的會少一欄位
if year ==2024:
    cursor.execute(f"DROP TABLE IF EXISTS mlb_{year}_standings")  # users2 是資料表名稱
    conn.commit()  # 確保刪除操作已儲存
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS mlb_{year}_standings (
        `id` INT(10) NOT NULL AUTO_INCREMENT COMMENT '流水號',
        `TEAM` VARCHAR(255) NOT NULL COLLATE 'utf8_general_ci',
        `W` INT(10) NULL DEFAULT NULL,
        `L` INT(10) NULL DEFAULT NULL,
        `PCT` DECIMAL(15,4) NULL DEFAULT NULL,
        `GB` VARCHAR(255) NULL DEFAULT NULL,
        `HOME` VARCHAR(10) NULL DEFAULT NULL,
        `AWAY` VARCHAR(10) NULL DEFAULT NULL,
        `RS` INT(10) NULL DEFAULT NULL,
        `RA` INT(10) NULL DEFAULT NULL,
        `DIFF` VARCHAR(10) NULL DEFAULT NULL,
        `STRK` VARCHAR(10) NULL DEFAULT NULL,
        `L10` VARCHAR(10) NULL DEFAULT NULL,
        `POFF` VARCHAR(10) NULL DEFAULT NULL,
        `ModifyTime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (`TEAM`) USING BTREE,
        INDEX `id` (`id`) USING BTREE
        ) 
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
    ''')
    conn.commit()
else:
    cursor.execute(f"DROP TABLE IF EXISTS mlb_{year}_standings")  # users2 是資料表名稱
    conn.commit()  # 確保刪除操作已儲存
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS mlb_{year}_standings (
        `id` INT(10) NOT NULL AUTO_INCREMENT COMMENT '流水號',
        `TEAM` VARCHAR(255) NOT NULL COLLATE 'utf8_general_ci',
        `W` INT(10) NULL DEFAULT NULL,
        `L` INT(10) NULL DEFAULT NULL,
        `PCT` DECIMAL(15,4) NULL DEFAULT NULL,
        `GB` VARCHAR(255) NULL DEFAULT NULL,
        `HOME` VARCHAR(10) NULL DEFAULT NULL,
        `AWAY` VARCHAR(10) NULL DEFAULT NULL,
        `RS` INT(10) NULL DEFAULT NULL,
        `RA` INT(10) NULL DEFAULT NULL,
        `DIFF` VARCHAR(10) NULL DEFAULT NULL,
        `STRK` VARCHAR(10) NULL DEFAULT NULL,
        `L10` VARCHAR(10) NULL DEFAULT NULL,
        `ModifyTime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (`TEAM`) USING BTREE,
        INDEX `id` (`id`) USING BTREE
        ) 
        COLLATE='utf8_general_ci'
        ENGINE=InnoDB
    ''')
    conn.commit()

chrome_options = Options()
chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
chrome_options.add_argument("--headless")  # Run in headless mode if not already doing so
import time
# Set the path to your ChromeDriver
path = "C:/Users/Tony/Desktop/chromedriver-win32/chromedriver.exe"
service = Service(executable_path=path)

# 自動下載並使用最新的 ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Print the current server time
current_time = datetime.now()
print(current_time)
team_data_dict = {}
TEAM_NAME_LIST_DATA = []
try:
    #以下定義網址會根據年分變更
    def switch_case(value):
        base_url = "https://www.espn.com/mlb/standings"
    # 設置年份對應的 URL
        cases = {year: f"{base_url}/_/season/{year}" for year in range(2010, 2025)}
        cases[2024] = base_url  # 特殊處理 2024
    # 返回對應 URL 或默認值
        return cases.get(value, "Invalid year")

# 測試
    print("測試")
    print(switch_case(2023))  # Output: https://www.espn.com/mlb/standings/_/season/2023
    print(switch_case(2024))  # Output: https://www.espn.com/mlb/standings
    print(switch_case(2009))  # Output: Invalid year


    
    driver.get(switch_case(year))
    #等待抓取內容
    time.sleep(3)
    wait = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/nav/ul/li[1]/a')))
    team_standings = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//*[@id="fittPageContainer"]/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[2]/td/div/span[3]/a/abbr'))) 
    TEAM_NAME_LIST_DATA = []
    
# Scrape team names for all rows
    #分區問題處理(球隊有可能會搬家或變更區域)
    team_section1_number = team_section2_number = team_section3_number = team_section4_number = team_section5_number = team_section6_number = 5
    section_change_yet = (2012, 2011, 2010)
    if year in section_change_yet:
        team_section3_number = 4
        team_section5_number = 6
    else:
        team_section3_number = team_section5_number = 5
    #特殊處理某些年份的欄位的 FULL XPATH 會有不同   
    year_particular_span = (2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010)
    if year in year_particular_span:
        span = 3 
    else:
        span = 4  
    #爬取球隊名稱                                                  
    for i in range(team_section1_number):  # Scrape 5 teams in each section 1
        xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[{i+2}]/td/div/span[{span}]/a'
        team_names = driver.find_elements(By.XPATH, xpath)
        short_memory = [element.text for element in team_names] #檢查文字內容是否為空白
        if not short_memory or all(not element.strip() for element in short_memory):
            span_change = 4
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[{i+2}]/td/div/span[{span_change}]/a'
            team_names = driver.find_elements(By.XPATH, xpath)
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
        else:
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
    print(TEAM_NAME_LIST_DATA)
    for i in range(team_section2_number):  # Scrape 5 teams in each section 2
        xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[{i+8}]/td/div/span[{span}]/a'
        team_names = driver.find_elements(By.XPATH, xpath)
        short_memory = [element.text for element in team_names] #檢查文字內容是否為空白
        if not short_memory or all(not element.strip() for element in short_memory):
            span_change = 4
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[{i+8}]/td/div/span[{span_change}]/a'
            team_names = driver.find_elements(By.XPATH, xpath)
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
        else:
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
    
    for i in range(team_section3_number):  # Scrape 5 teams in each section 3
        xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[{i+14}]/td/div/span[{span}]/a'
        team_names = driver.find_elements(By.XPATH, xpath)
        short_memory = [element.text for element in team_names] #檢查文字內容是否為空白
        if not short_memory or all(not element.strip() for element in short_memory):
            span_change = 4
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/table/tbody/tr[{i+14}]/td/div/span[{span_change}]/a'
            team_names = driver.find_elements(By.XPATH, xpath)
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
        else:
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
    for i in range(team_section4_number):  # Scrape 5 teams in each section 4
        xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+2}]/td/div/span[{span}]/a'
        team_names = driver.find_elements(By.XPATH, xpath)
        short_memory = [element.text for element in team_names] #檢查文字內容是否為空白
        if not short_memory or all(not element.strip() for element in short_memory):
            span_change = 4
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+2}]/td/div/span[{span_change}]/a'
            team_names = driver.find_elements(By.XPATH, xpath)
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
        else:
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
    for i in range(team_section5_number):  # Scrape 5 teams in each section 5
        xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+8}]/td/div/span[{span}]/a'
        team_names = driver.find_elements(By.XPATH, xpath)
        short_memory = [element.text for element in team_names] #檢查文字內容是否為空白
        if not short_memory or all(not element.strip() for element in short_memory):
            span_change = 4
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+8}]/td/div/span[{span_change}]/a'
            team_names = driver.find_elements(By.XPATH, xpath)
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
        else:
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
    for i in range(team_section6_number):  # Scrape 5 teams in each section 6
        if team_section5_number == 6:
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+15}]/td/div/span[{span}]/a'
        else:
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+14}]/td/div/span[{span}]/a'
        team_names = driver.find_elements(By.XPATH, xpath)
        short_memory = [element.text for element in team_names] #檢查文字內容是否為空白
        if not short_memory or all(not element.strip() for element in short_memory):
            span_change = 4
            if team_section5_number == 6:
                xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+15}]/td/div/span[{span_change}]/a'
            else:
                xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/table/tbody/tr[{i+14}]/td/div/span[{span_change}]/a'
            team_names = driver.find_elements(By.XPATH, xpath)
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
        else:
            TEAM_NAME_LIST_DATA.extend([element.text for element in team_names])
# Print out the collected team names
    for name in TEAM_NAME_LIST_DATA:
        print(name)
    all_team_data = []
   #爬取球隊戰績資料
   #當年會多一欄位(晉級季後賽機率POFF)
    if year == 2024:
        column_number = 12
    else :
        column_number = 11
    for i in range(team_section1_number):
        for j in range(column_number):
            player_row_data = []      
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/div/div[2]/table/tbody/tr[{2+i}]/td[{1+j}]/span'
            player_elements3= driver.find_elements(By.XPATH, xpath)    
            player_element_number1 = [element.text for element in player_elements3]         
            all_team_data.append(player_element_number1[0])
    for i in range(team_section2_number):
        for j in range(column_number):
            player_row_data = []
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/div/div[2]/table/tbody/tr[{8+i}]/td[{1+j}]/span'
            player_elements3= driver.find_elements(By.XPATH, xpath)    
            player_element_number1 = [element.text for element in player_elements3]         
            all_team_data.append(player_element_number1[0]) 
    for i in range(team_section3_number):
        for j in range(column_number):
            player_row_data = []            
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[1]/div/div[2]/div/div[2]/table/tbody/tr[{14+i}]/td[{1+j}]/span'
            player_elements3= driver.find_elements(By.XPATH, xpath)    
            player_element_number1 = [element.text for element in player_elements3]         
            all_team_data.append(player_element_number1[0])  
    for i in range(team_section4_number):
        for j in range(column_number):
            player_row_data = []
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/div/div[2]/table/tbody/tr[{2+i}]/td[{1+j}]/span'
            player_elements3= driver.find_elements(By.XPATH, xpath)    
            player_element_number1 = [element.text for element in player_elements3]         
            all_team_data.append(player_element_number1[0])  
    for i in range(team_section5_number):
        for j in range(column_number):
            player_row_data = []
            xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/div/div[2]/table/tbody/tr[{8+i}]/td[{1+j}]/span'
            player_elements3= driver.find_elements(By.XPATH, xpath)    
            player_element_number1 = [element.text for element in player_elements3]         
            all_team_data.append(player_element_number1[0]) 
    for i in range(team_section6_number):
        for j in range(column_number):
            player_row_data = [] 
            if team_section5_number == 6:
                xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/div/div[2]/table/tbody/tr[{15+i}]/td[{1+j}]/span'             
            else:
                xpath = f'/html/body/div[1]/div/div/div/div/main/div[2]/div[2]/div/div/section/div/section/div[2]/div/section/div[2]/div/div[2]/div/div[2]/table/tbody/tr[{14+i}]/td[{1+j}]/span'
            player_elements3= driver.find_elements(By.XPATH, xpath)    
            player_element_number1 = [element.text for element in player_elements3]         
            all_team_data.append(player_element_number1[0])  
    print(all_team_data)
    chunk_size = column_number 
    team_data = [all_team_data[i:i + chunk_size]for i in range(0,len(all_team_data) , chunk_size)]
        #--檢查print(sub_all_player_data)
    if year == 2024:
        column_names = ['W', 'L', 'PCT', 'GB', 'HOME', 'AWAY', 'RS', 'RA', 'DIFF', 'STRK', 'L10', 'POFF']
    else:
        column_names = ['W', 'L', 'PCT', 'GB', 'HOME', 'AWAY', 'RS', 'RA', 'DIFF', 'STRK', 'L10']
    df_stats = pd.DataFrame(team_data, columns=column_names)
    df_name = pd.DataFrame(TEAM_NAME_LIST_DATA, columns=['TEAM']) 
   
    df_final = pd.concat([ df_name, df_stats], axis=1)

    print(tabulate(df_final, headers='keys', tablefmt='pretty'))                    
except TimeoutException:
    print()
except Exception as e:
    print()
finally:
    print()
print(df_final.head())  # 預覽前 5 行數據
excel_file = f'mlb_history_{year}_standings.xlsx'
with pd.ExcelWriter(excel_file,engine='openpyxl') as writer:
    df_final.to_excel(writer, sheet_name=f'Sheet{year}', index=False)
                
#塞進資料庫
try:
    # Replace data in MySQL table with the data from df_final
    if year == 2024:

        cursor.executemany(f"""
            REPLACE INTO mlb_{year}_standings 
            (TEAM, W, L, PCT, GB, HOME, AWAY, RS, RA, DIFF, STRK, L10, POFF) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, df_final.values.tolist())
    else:
        cursor.executemany(f"""
            REPLACE INTO mlb_{year}_standings 
            (TEAM, W, L, PCT, GB, HOME, AWAY, RS, RA, DIFF, STRK, L10) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, df_final.values.tolist())
    conn.commit()
    print("Data inserted successfully!")
except mysql.connector.Error as e:
    print(f"Error occurred: {e}")
finally:
    cursor.close()
    conn.close()