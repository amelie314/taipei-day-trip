from flask import Flask, render_template, jsonify, request
import requests
import mysql.connector
import re
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from jwt import encode, decode
from functools import wraps  #token驗證
import datetime
import random

# 設定 Flask 應用
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True

# 一定要先有 dotenv
load_dotenv()

secret_key = os.environ.get("SECRET_KEY")
app.config["SECRET_KEY"]= secret_key

password = os.environ.get("PASSWORD")
app_id = os.environ.get("APP_ID")
app_key = os.environ.get("APP_KEY")
partner_key = os.environ.get("PARTNER_KEY")
merchant_id = os.environ.get("MERCHANT_ID")

tappay_domain = "https://sandbox.tappaysdk.com"  

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
def generate_order_number():
    current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # 獲取當前的日期和時間
    random_digits = "".join([str(random.randint(0, 9)) for _ in range(4)])  # 生成4位隨機數字
    return current_time + random_digits  # 連接日期時間和隨機數字作為訂單編號

    
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
        token = encode(payload, app.config["SECRET_KEY"], algorithm='HS256')
        return token
        
    except Exception as e:
        return str(e) # 回傳錯誤訊息
    
# 解碼 JWT 函式
def decode_token(token):
    try:
        if isinstance(token, str):
            token = token.encode('utf-8')
        
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
            return jsonify({"message": 'Token 缺失'}), 403
        
        try:
            user_data, err = decode_token(token)  # 使用 decode_token 函數
            
            
            if err:
                raise Exception(err)
            
        except Exception as e:
            return jsonify({"message": f'Token 無效或過期: {str(e)}'}), 403
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

    # 連接資料庫 
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)

    try:
        # 找出 email 對應的使用者
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):            
            token = encode_auth_token(user['id'], user['name'], user['email'])
            
            return jsonify({'token': token}), 200
        else:
            return jsonify({"error": True, "message" : '登入失敗，Email 或密碼錯誤。'}), 400
    except mysql.connector.Error as err:
        print(f"資料庫錯誤：{err}")
        return jsonify({"error": True, "message" : "資料庫錯誤"}), 500
    except TypeError as err:
        print(f"類型錯誤：{err}")
        return jsonify({"error": True, "message" :  '伺服器錯誤：不可序列化的物件'}), 500
    except Exception as err:
        print(f"未知錯誤：{err}")
        return jsonify({"error": True, "message" :  str(err)}), 500
    finally:
        cursor.close()
        db.close()

# 取得使用者資料        
@app.route("/api/user/auth", methods=['GET'])
# @token_required
def get_user_auth(user_data=None):  # 更改名稱，user_data 從裝飾器中獲取
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"data": None}), 200
        
    try:
        user_data, err = decode_token(token)  # 使用 decode_token 函數
        
        if err:
            raise Exception(err)
        
        if not user_data:
            return jsonify({"data": None}), 200
        
        return jsonify(
            {"data":
                {
                    "id": user_data.get("user_id"),
                    "name": user_data.get("username"),
                    "email": user_data.get("email")
                }
            }
        ), 200
        
    except Exception as e:
        return jsonify({"data": None}), 200
    

 
@app.route("/")
def index():
    return render_template("index.html")

# @app.route("/booking")
# def booking():
#     return render_template("booking.html")
@app.route("/booking")
def booking(): 
    print(app_id)
    print(app_key)
    return render_template("booking.html", app_id = app_id, app_key = app_key)


#取得尚未確認的預定行程
@app.route("/api/booking", methods=['GET'])
@token_required
def get_booking(user_data):
    user_id = user_data['user_id']
    
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    
    try:
        # 從bookings表格中擷取預定資訊
        cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
        booking_data = cursor.fetchone()
        
        if not booking_data:
            return jsonify({"data": None}), 200
        
        # 從attractions表格中獲取景點資訊
        cursor.execute("SELECT * FROM attractions WHERE id = %s", (booking_data['attraction_id'],))
        attraction_data = cursor.fetchone()
        
        response_data = {
            "data": {
                "attraction": {
                    "id": attraction_data['id'],
                    "name": attraction_data['name'],
                    "address": attraction_data['address'],
                    "image": fetch_images(cursor, attraction_data['id'])[0]  # 只取第一張圖片
                },
                "date": booking_data['date'].strftime('%Y-%m-%d'),  # 確保日期是字符串
                "time": booking_data['time'],
                "price": booking_data['price']
            }
        }
        
        return jsonify(response_data), 200
    except mysql.connector.Error as err:
        print(f"資料庫錯誤：{err}")
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    except Exception as err:
        print(f"伺服器錯誤：{err}")
        return jsonify({"error": True, "message": str(err)}), 500
    finally:
        cursor.close()
        db.close()
        
#建立新的預定行程       
@app.route("/api/booking", methods=['POST'])
@token_required
def create_booking(user_data):
    user_id = user_data['user_id']
    data = request.json

    attraction_id = data.get("attractionId")
    date = data.get("date")
    time = data.get("time")
    price = data.get("price")

    # 檢查輸入資料是否完整
    if not all([attraction_id, date, time, price]):
        return jsonify({"error": True, "message": "輸入不完整"}), 400

    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
    existing_booking = cursor.fetchone()
    
    try:
        if existing_booking:
            cursor.execute("UPDATE bookings SET attraction_id = %s, date = %s, time = %s, price = %s WHERE user_id = %s",
                      (attraction_id, date, time, price, user_id))
        else:
            cursor.execute("INSERT INTO bookings (user_id, attraction_id, date, time, price) VALUES (%s, %s, %s, %s, %s)",
                      (user_id, attraction_id, date, time, price))
        db.commit()

        return jsonify({"ok": True}), 200
    except mysql.connector.Error as err:
        print(f"資料庫錯誤：{err}")
        db.rollback()
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    except Exception as e:
        print(f"伺服器錯誤：{e}")
        db.rollback()
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        cursor.close()
        db.close()

# @app.route("/thankyou")
# def thankyou():
#     return render_template("thankyou.html")
@app.route("/thankyou")
def thankyou():
    order_number = request.args.get('number')  # 從查詢字串取得訂單編號
    if not order_number:
        return "訂單編號缺失", 400
    # 這裡可以做更多與訂單編號相關的操作，例如從資料庫裡查詢該訂單的詳細資訊等
    return render_template("thankyou.html", order_number=order_number)


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
#刪除預定行程
@app.route("/api/booking", methods=['DELETE'])
@token_required
def delete_booking(user_data):
    user_id = user_data['user_id']

    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)

    try:
        # 從bookings表格中刪除該使用者的預定資訊
        cursor.execute("DELETE FROM bookings WHERE user_id = %s", (user_id,))
        db.commit()

        # 檢查是否真的刪除了資料
        if cursor.rowcount == 0:
            return jsonify({"error": True, "message": "找不到預定資料或已被刪除"}), 400

        return jsonify({"ok": True}), 200
    except mysql.connector.Error as err:
        print(f"資料庫錯誤：{err}")
        db.rollback()
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    except Exception as e:
        print(f"伺服器錯誤：{e}")
        db.rollback()
        return jsonify({"error": True, "message": str(e)}), 500
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


@app.route("/api/orders", methods=['POST'])
@token_required
def create_order(user_data):
    
    data = request.json

    prime = data.get("prime")
    order_data = data.get("order")

    tappay_response = requests.post(
        f"{tappay_domain}/tpc/payment/pay-by-prime",
        json={
            "prime": prime,
            "partner_key": partner_key,
            "merchant_id": merchant_id,
            "details": "旅遊行程訂單",
            "amount": order_data["price"],
            "cardholder": {
                "phone_number": order_data["contact"]["phone"],
                "name": order_data["contact"]["name"],
                "email": order_data["contact"]["email"]
            }
        },
        headers={
                 "x-api-key": partner_key
        }
    )

    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)

    try:
        order_number = generate_order_number()  # 生成訂單編號
        
        if tappay_response.json().get("status") == 0:
            # 如果 TapPay 交易成功
            # 儲存訂單資料到 orders 表格
            cursor.execute("INSERT INTO orders (user_id, price, date, time, status, order_number) VALUES (%s, %s, %s, %s, %s, %s)",
                           (user_data["user_id"], order_data["price"], order_data["trip"]["date"], order_data["trip"]["time"], '已付款', order_number))
        else:
            cursor.execute("INSERT INTO orders (user_id, price, date, time, status, order_number) VALUES (%s, %s, %s, %s, %s, %s)",
                           (user_data["user_id"], order_data["price"], order_data["trip"]["date"], order_data["trip"]["time"], '未付款', order_number))
        
        db.commit()

        # 獲取剛剛插入的訂單的ID
        order_id = cursor.lastrowid

        # 更新 bookings 表格的 order_id 欄位
        cursor.execute("UPDATE bookings SET order_id = %s WHERE user_id = %s", (order_id, user_data["user_id"]))
        db.commit()

        # 儲存聯絡人資料到 contacts 表格
        cursor.execute("INSERT INTO contacts (order_id, name, email, phone) VALUES (%s, %s, %s, %s)",
                    (order_id, order_data["contact"]["name"], order_data["contact"]["email"], order_data["contact"]["phone"]))
        db.commit()

        return jsonify({"ok": True, "order_number": order_number}), 200

    except mysql.connector.Error as err:
        db.rollback()
        return jsonify({"error": True, "message": str(err)}), 500
    except Exception as e:
        db.rollback()
        return jsonify({"error": True, "message": str(e)}), 500
    finally:
        cursor.close()
        db.close()

@app.route("/api/order/<orderNumber>", methods=['GET'])
@token_required
def get_order_by_number(user_data, orderNumber):
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor(dictionary=True)
    
    try:
        # 從 orders 表格中擷取訂單資訊
        cursor.execute("SELECT * FROM orders WHERE order_number = %s AND user_id = %s", (orderNumber, user_data["user_id"]))
        order = cursor.fetchone()

        if not order:
            return jsonify({"data": None}), 200

        # 從 contacts 表格中擷取聯絡人資訊
        cursor.execute("SELECT * FROM contacts WHERE order_id = %s", (order["id"],))
        contact = cursor.fetchone()

        # 從 bookings 表格和 attractions 表格中擷取景點資訊
        cursor.execute("SELECT * FROM bookings INNER JOIN attractions ON bookings.attraction_id = attractions.id WHERE order_id = %s", (order["id"],))
        booking = cursor.fetchone()

        response_data = {
            "data": {
                "number": order["order_number"],
                "price": order["price"],
                "trip": {
                    "attraction": {
                        "id": booking["id"],
                        "name": booking["name"],
                        "address": booking["address"],
                        "image": fetch_images(cursor, booking["id"])[0]  # 只取第一張圖片
                    },
                    "date": booking["date"].strftime('%Y-%m-%d'),  # 確保日期是字符串
                    "time": booking["time"]
                },
                "contact": {
                    "name": contact["name"],
                    "email": contact["email"],
                    "phone": contact["phone"]
                },
                "status": order["status"]
            }
        }
        
        return jsonify(response_data), 200
    except mysql.connector.Error as err:
        print(f"資料庫錯誤：{err}")
        return jsonify({"error": True, "message": "資料庫錯誤"}), 500
    except Exception as err:
        print(f"伺服器錯誤：{err}")
        return jsonify({"error": True, "message": str(err)}), 500
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)




