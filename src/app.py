from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'KN'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# 注册接口
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # 检查用户名是否已存在
    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    if user:
        return jsonify({"error": "Username already exists"}), 400

    # 哈希密码
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        # 开始事务
        mysql.connection.begin()

        # 插入用户信息
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed.decode('utf-8')))
        user_id = cur.lastrowid

        # 插入用户详细信息
        cur.execute("INSERT INTO user_info (user_id, name, phone) VALUES (%s, %s, %s)",
                    (user_id, name, phone))

        # 提交事务
        mysql.connection.commit()

        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

    except Exception as e:
        # 回滚事务
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


# 登录接口
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.password, ui.name, ui.phone 
        FROM users u
        LEFT JOIN user_info ui ON u.id = ui.user_id
        WHERE u.username = %s
    """, (username,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    # 验证密码
    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # 密码正确，返回用户信息（实际应用中可能返回token）
        user.pop('password')  # 不要返回密码
        return jsonify({"message": "Login successful", "user": user}), 200
    else:
        return jsonify({"error": "Invalid password"}), 401


if __name__ == '__main__':
    app.run(debug=True)