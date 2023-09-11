from flask import Flask, render_template, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv

# 設定 Flask 應用
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

load_dotenv()
password = os.environ.get("PASSWORD")

# 資料庫連接設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': password,
    'database': 'taipei_day_trip_2'
}

# 從 attraction_images 表格中獲取景點的圖片 URLs
def fetch_images(cursor, attraction_id):
    cursor.execute("SELECT image_url FROM attraction_images WHERE attraction_id = %s", (attraction_id,))
    return [row['image_url'] for row in cursor.fetchall()]

# 轉換資料庫記錄為字典
def convert_to_dict(record, cursor):
    return {
        "id": record['id'],
        "name": record['name'],
        "category": record['CAT'],
        "description": record['description'],
        "address": record['address'],
        "transport": record['direction'],
        "mrt": record['MRT'],
        "lat": record['latitude'],
        "lng": record['longitude'],
        "images": fetch_images(cursor, record['id'])  # 調用 fetch_images
    }

# 路由
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/booking")
def booking():
    return render_template("booking.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/api/attractions", methods=['GET'])
def api_attractions():
    cursor = None  # 初始化為 None
    db = None  # 初始化為 None
    try:
        page = int(request.args.get('page', 0))
        keyword = request.args.get('keyword')

        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        
        # 總數
        count_query = "SELECT COUNT(*) FROM attractions"
        if keyword:
            count_query += " WHERE name LIKE %s OR mrt = %s"
        cursor.execute(count_query, ("%"+keyword+"%", keyword) if keyword else ())
        
        total_count = cursor.fetchone()['COUNT(*)']

        sql_query = "SELECT * FROM attractions"
        sql_params = []
        
        if keyword:
            sql_query += " WHERE name LIKE %s OR mrt = %s"
            sql_params.append("%" + keyword + "%")
            sql_params.append(keyword)  # 添加這一行

        sql_query += " LIMIT %s, 12"
        sql_params.append(page * 12)

        cursor.execute(sql_query, tuple(sql_params))  # 將列表轉為元組

        attractions = cursor.fetchall()
        attractions_json = [convert_to_dict(attraction, cursor) for attraction in attractions]

        nextPage = None
        
        if (page + 1) * 12 < total_count:
            nextPage = page + 1
            
        output = {
            "nextPage": nextPage,
            "data": attractions_json
        }

        return jsonify(output)

    except mysql.connector.Error as err:
        print("資料庫錯誤: {}".format(err))
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    finally:
        if cursor:  # 檢查 cursor 是否已賦值
            cursor.close()
        if db:  # 檢查 db 是否已賦值
            db.close()


@app.route("/api/attraction/<int:attractionId>", methods=['GET'])
def api_attraction(attractionId):
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attractions WHERE id = %s", (attractionId,))
        attraction = cursor.fetchone()
        if attraction:
            attraction_json = convert_to_dict(attraction, cursor)
            output = {
                "data": attraction_json
            }
            return jsonify(output)
        else:
            return jsonify({"error": "Attraction not found"}), 404
    except mysql.connector.Error as err:
        print("Database error: {}".format(err))
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/api/mrts", methods=['GET'])
def api_mrts():
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)

        # 取得數據庫裡不重複的捷運站名稱，且
        cursor.execute("SELECT MRT, COUNT(*) as cnt FROM attractions GROUP BY MRT ORDER BY cnt DESC")
        mrt_names = [row['MRT'] for row in cursor.fetchall()]

        # 將捷運站名稱格式化為JSON
        # mrts_json = [{"name": name} for name in mrt_names]
        mrts_json =  ({"data": mrt_names})
        return jsonify(mrts_json)
    
    except mysql.connector.Error as err:
        print("Database error: {}".format(err))
        return jsonify({"error": "Database error"}), 500
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
