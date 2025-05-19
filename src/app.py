from functools import wraps
from flask import Flask, request, jsonify, make_response, render_template
from flask_mysqldb import MySQL
import bcrypt
from flask import Flask, send_from_directory
from flask_cors import CORS  # 导入 CORS


app = Flask(__name__)

CORS(app)  # 启用 CORS


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'KN'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


# 认证装饰器：检查请求头中的用户名是否有效
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 从请求头获取用户名（示例：Authorization: Username <username>）
        if 'Authorization' not in request.headers:
            return jsonify({"error": "Authorization header is missing"}), 401
        username = request.headers['Authorization'].split(' ')[1]
        if not username:
            return jsonify({"error": "Username token is missing"}), 401

        # 验证用户名是否存在于数据库
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if not user:
            return jsonify({"error": "Invalid username token"}), 401
        return f(username, *args, **kwargs)

    return decorated


# 注册接口（保持不变）
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    if cur.fetchone():
        return jsonify({"error": "Username already exists"}), 400

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        mysql.connection.begin()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed.decode('utf-8')))
        user_id = cur.lastrowid
        cur.execute("INSERT INTO user_info (user_id, name, phone) VALUES (%s, %s, %s)",
                    (user_id, name, phone))
        mysql.connection.commit()
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id,
            "token": username  # 返回用户名作为令牌
        }), 201
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()


# 登录接口（返回用户名作为令牌）
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.id, u.password, ui.name, ui.phone 
        FROM users u
        LEFT JOIN user_info ui ON u.id = ui.user_id
        WHERE u.username = %s
    """, (username,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        # 直接返回用户名作为令牌（明文，仅适用于简单场景）
        return jsonify({
            "message": "Login successful",
            "token": username,  # 令牌为用户名
            "user": {
                "id": user['id'],
                "username": username,
                "name": user['name'],
                "phone": user['phone']
            }
        }), 200
    else:
        return jsonify({"error": "Invalid password"}), 401


# 查询当前用户信息（通过用户名令牌认证）
@app.route('/user', methods=['GET'])
@auth_required
def get_current_user(username):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.id, u.username, ui.name, ui.phone 
        FROM users u
        LEFT JOIN user_info ui ON u.id = ui.user_id
        WHERE u.username = %s
    """, (username,))
    user = cur.fetchone()
    cur.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user}), 200


# 根据用户 ID 查询（需携带用户名令牌）
@app.route('/user/<int:user_id>', methods=['GET'])
@auth_required
def get_user_by_id(username, user_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT u.id, u.username, ui.name, ui.phone 
        FROM users u
        LEFT JOIN user_info ui ON u.id = ui.user_id
        WHERE u.id = %s
    """, (user_id,))
    user = cur.fetchone()
    cur.close()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user}), 200


# 静态文件路由 - CSS 和图片
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('templates/css', path)

@app.route('/images/<path:path>')
def send_images(path):
    return send_from_directory('templates/images', path)

# 页面路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index_shortcut():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/list2')
def list2():
    return render_template('list2.html')

@app.route('/list3')
def list3():
    return render_template('list3.html')

@app.route('/list4')
def list4():
    return render_template('list4.html')

@app.route('/list5')
def list5():
    return render_template('list5.html')

if __name__ == '__main__':
    app.run(debug=True)