# from flask import Flask, render_template, jsonify
# import mysql.connector

# app = Flask(__name__)
# app.config["JSON_AS_ASCII"] = False
# app.config["TEMPLATES_AUTO_RELOAD"] = True

# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'rootroot',
#     'database': 'taipei_day_trip'
# }

# def fetch_images(cursor, attraction_id):
#     cursor.execute("SELECT image_url FROM attraction_images WHERE attraction_id = %s", (attraction_id,))
#     return [row['image_url'] for row in cursor.fetchall()]

# # ...其他部分保持不變
# def convert_to_dict(record):
#     return {
#         "id": record['id'],
#         "name": record['name'],
#         "category": record['CAT'],
#         "description": record['description'],
#         "address": record['address'],
#         "transport": record['direction'],
#         "mrt": record['MRT'],
#         "lat": record['latitude'],
#         "lng": record['longitude'],
#         "images": []  # 我們稍後會填充這個部分
#     }

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/booking")
# def booking():
#     return render_template("booking.html")

# @app.route("/thankyou")
# def thankyou():
#     return render_template("thankyou.html")

# @app.route("/api/attractions", methods=['GET'])
# def api_attractions():
#     try:
#         db = mysql.connector.connect(**db_config)
#         cursor = db.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM attractions")
#         attractions = cursor.fetchall()

#         attractions_json = []
#         for attraction in attractions:
#             attraction_dict = convert_to_dict(attraction)
#             attraction_dict['images'] = fetch_images(cursor, attraction['id'])
#             attractions_json.append(attraction_dict)

#     except mysql.connector.Error as err:
#         print("Database error: {}".format(err))
#         return jsonify({"error": "Database error"}), 500
#     finally:
#         cursor.close()
#         db.close()

#     output = {
#         "nextPage": 1,
#         "data": attractions_json
#     }
#     return jsonify(output)

# @app.route("/api/attraction/<int:attractionId>", methods=['GET'])
# def api_attraction(attractionId):
#     try:
#         db = mysql.connector.connect(**db_config)
#         cursor = db.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM attractions WHERE id = %s", (attractionId,))
#         attraction = cursor.fetchone()

#         if attraction:
#             attraction_dict = convert_to_dict(attraction)
#             attraction_dict['images'] = fetch_images(cursor, attraction['id'])
#             return jsonify(attraction_dict)
#         else:
#             return jsonify({"error": "Attraction not found"}), 404

#     except mysql.connector.Error as err:
#         print("Database error: {}".format(err))
#         return jsonify({"error": "Database error"}), 500
#     finally:
#         cursor.close()
#         db.close()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=3000)
from flask import Flask, render_template, jsonify
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
    'database': 'taipei_day_trip'
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
    try:
        db = mysql.connector.connect(**db_config)
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM attractions")
        attractions = cursor.fetchall()
        attractions_json = [convert_to_dict(attraction, cursor) for attraction in attractions]
        
        output = {
            "nextPage": 1,
            "data": attractions_json
        }
        return jsonify(output)
    except mysql.connector.Error as err:
        print("Database error: {}".format(err))
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    finally:
        cursor.close()
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

        # 取得數據庫库不重複的捷運站名稱
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
