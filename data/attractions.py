# import json
# import mysql.connector
# import re

# # 讀取JSON檔案
# with open('./taipei-attractions.json', 'r', encoding='utf-8') as file:
#     data = json.load(file)

# # 連接到 MySQL 資料庫
# db_connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="rootroot",
#     database="taipei_day_trip"
# )
# cursor = db_connection.cursor()

# # 建立或修改景點資料表
# create_table_query = '''
#     CREATE TABLE IF NOT EXISTS attractions (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(255),
#         description TEXT,
#         latitude FLOAT,
#         longitude FLOAT,
#         MRT VARCHAR(255)  -- 新增 MRT 欄位
#     )
# '''
# cursor.execute(create_table_query)

# # 建立儲存圖片URL的資料表
# create_image_table_query = '''
#     CREATE TABLE IF NOT EXISTS attraction_images (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         attraction_id INT,
#         image_url TEXT,
#         FOREIGN KEY (attraction_id) REFERENCES attractions(id)
#     )
# '''
# cursor.execute(create_image_table_query)

# # 插入基本資料和圖片URL
# for attraction in data['result']['results']:
#     insert_query = '''
#         INSERT INTO attractions (name,description, latitude, longitude, MRT)  -- 更新這裡
#         VALUES (%s, %s, %s, %s, %s)  -- 更新這裡
#     '''
#     values = (
#         attraction['name'],
#         attraction['description'],
#         float(attraction['latitude']),
#         float(attraction['longitude']),
#         attraction['MRT']  # 新增 MRT 資料
#     )
#     cursor.execute(insert_query, values)
#     last_id = cursor.lastrowid
    
#     # 分析並過濾圖片URL
#     image_urls = attraction['file'].split("https://")
#     jpg_png_urls = [url for url in image_urls if re.search(r'(?:jpg|png)$', url)]
    
#     for url in jpg_png_urls:
#         insert_image_query = '''
#             INSERT INTO attraction_images (attraction_id, image_url)
#             VALUES (%s, %s)
#         '''
#         cursor.execute(insert_image_query, (last_id, "https://" + url))

# # 提交並關閉資料庫連接
# db_connection.commit()
# cursor.close()
# db_connection.close()
from dotenv import load_dotenv
import os
import json
import mysql.connector
import re  # 引入正則表達式模組

# 讀取JSON檔案
with open("./taipei-attractions.json", 'r', encoding='utf-8') as file:
    data = json.load(file)
    
load_dotenv(dotenv_path='../.env')
password = os.environ.get("PASSWORD")

# 連接到 MySQL 資料庫
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password= password,
    database="taipei_day_trip_2"
)
cursor = db_connection.cursor()

# 建立或修改景點資料表
create_table_query = '''
    CREATE TABLE IF NOT EXISTS attractions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        description TEXT,
        latitude FLOAT,
        longitude FLOAT,
        MRT VARCHAR(255),
        rate INT,
        direction TEXT,
        date DATE,
        avBegin DATE,
        avEnd DATE,
        address VARCHAR(255),
        REF_WP VARCHAR(50),
        langinfo VARCHAR(50),
        SERIAL_NO VARCHAR(50),
        CAT VARCHAR(50),
        MEMO_TIME TEXT,
        POI CHAR(1),
        idpt VARCHAR(255)
    )
'''
cursor.execute(create_table_query)

# 建立儲存圖片URL的資料表
create_image_table_query = '''
    CREATE TABLE IF NOT EXISTS attraction_images (
        id INT AUTO_INCREMENT PRIMARY KEY,
        attraction_id INT,
        image_url TEXT,
        FOREIGN KEY (attraction_id) REFERENCES attractions(id)
    )
'''
cursor.execute(create_image_table_query)

# 插入資料
for attraction in data['result']['results']:
    insert_query = '''
        INSERT INTO attractions (name, description, latitude, longitude, MRT, rate, direction, date, avBegin, avEnd, address, REF_WP, langinfo, SERIAL_NO, CAT, MEMO_TIME, POI, idpt)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    values = (
        attraction['name'],
        attraction['description'],
        float(attraction['latitude']),
        float(attraction['longitude']),
        attraction['MRT'],
        attraction['rate'],
        attraction['direction'],
        attraction['date'],
        attraction['avBegin'],
        attraction['avEnd'],
        attraction['address'],
        attraction['REF_WP'],
        attraction['langinfo'],
        attraction['SERIAL_NO'],
        attraction['CAT'],
        attraction['MEMO_TIME'],
        attraction['POI'],
        attraction['idpt']
    )
    cursor.execute(insert_query, values)
    last_id = cursor.lastrowid

    # 分析並過濾圖片URL
    image_urls = attraction['file'].split("https://")
    jpg_png_urls = [url for url in image_urls if re.search(r'(?:jpg|png)$', url, re.IGNORECASE)]

    
    for url in jpg_png_urls:
        insert_image_query = '''
            INSERT INTO attraction_images (attraction_id, image_url)
            VALUES (%s, %s)
        '''
        cursor.execute(insert_image_query, (last_id, "https://" + url))

# 提交並關閉資料庫連接
db_connection.commit()
cursor.close()
db_connection.close()
