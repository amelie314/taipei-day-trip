from flask import Flask, render_template, jsonify, request
import mysql.connector
import os
import re
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from jwt import encode
from jwt import decode
import datetime
from functools import wraps  #token驗證


# 設定 Flask 應用
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

secret_key = os.environ.get("SECRET_KEY")
app.config["SECRET_KEY"]= secret_key

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
    
# 編碼 JWT 函式
def encode_auth_token(user_id, username, email):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
            'iat': datetime.datetime.utcnow(),
            'sub': {
                'user_id': user_id,
                'username': username,
                'email': email
            }
        }
        return encode(payload, app.config["SECRET_KEY"], algorithm='HS256')
    except Exception as e:
        return e
    
# 解碼 JWT 函式
def decode_token(token):
    try:
        # 在這裡，'你的JWT密鑰' 應該和你用於編碼 JWT 的密鑰相同
        decoded_data = decode(token, app.config["SECRET_KEY"], algorithms=['HS256'])
        return decoded_data['sub'], None  # 回傳解碼後的資料和 None（代表沒有錯誤）
    except Exception as e:
        return None, str(e)  # 回傳 None 和錯誤訊息

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        token = request.headers.get('Authorization')
        # 去除 Bearer 但我剛才消除了
        # token = auth_header.split(" ")[1] if auth_header else None

        if not token:
            return jsonify({'message': 'Token 缺失'}), 403
        
        try:
            user_data, err = decode_token(token)  # 使用 decode_token 函數
            if err:
                raise Exception(err)
        except Exception as e:
            return jsonify({'message': f'Token 無效或過期: {str(e)}'}), 403
        return f(user_data, *args, **kwargs)
    return decorated

# 註冊
@app.route("/api/user", methods=["POST"])
def register():
    # 取得請求資料
    data = request.json
    name = data.get("name") 
    email = data.get("email")
    password = data.get("password")

    # 驗證 email
    if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({"error": True, "message": "無"}), 400
    
    # 驗證密碼長度
    if not password or len(password) < 8:
        return jsonify({"error": True, "message": "密碼必須至少有8個字元"}), 400

    # 密碼加密
    hashed_password = generate_password_hash(password, method='sha256')
    
    # 連接資料庫
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    
    try:
        # 檢查 Email 是否已存在
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({"error": True, "message": "註冊失敗，Email 可能已被使用。"}), 400

        # 新增使用者
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        db.commit()
        return jsonify({"ok": True}), 200
    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": True, "message": str(err)}), 500
    except Exception as err:
        db.rollback()
        return jsonify({"error": True, "message": "伺服器內部錯誤"}), 500
    finally:
        cursor.close()
        db.close()

# 登入
@app.route("/api/user/auth", methods=['PUT'])
def login():
    # 取得請求資料
    data = request.json
    email = data.get('email')
    password = data.get('password')

    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            
            token = encode_auth_token(user['id'], user['name'], user['email'])
            
            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': '登入失敗，Email 或密碼錯誤。'}), 400
    except mysql.connector.Error as err:
        print(f"資料庫錯誤：{err}")
        return jsonify({'error': str(err)}), 500
    except Exception as err:
        print(f"伺服器錯誤：{err}")
        return jsonify({'error': '伺服器錯誤'}), 500
    finally:
        cursor.close()
        db.close()

# 取得使用者資料        
@app.route("/api/user/auth", methods=['GET'])
@token_required  # 如果你有 token 驗證的裝飾器
def get_user_auth(user_data=None):  # 更改名稱，user_data 從裝飾器中獲取
    
    print
    
    if not user_data:
        return jsonify({"data": None}), 200
    
    return jsonify({"data": user_data}), 200
 
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/booking")
def booking():
    return render_template("booking.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")

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
