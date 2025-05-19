from flask import Flask, render_template, request, redirect, session, flash, jsonify
from db.init import execute_query
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于会话管理

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 登录页面路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            })

        # 查询用户信息
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        try:
            user = execute_query(query, (username, password))
        except Exception as e:
            logger.error(f"查询用户信息时出错: {e}")
            return jsonify({
                'success': False,
                'message': '服务器内部错误，请稍后重试'
            })

        if user:
            # 登录成功，将用户信息存入会话
            user = user[0]
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            return jsonify({
                'success': True,
                'message': '登录成功'
            })
        else:
            # 登录失败
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            })

    return render_template('login.html')

# 退出登录路由
@app.route('/logout')
def logout():
    # 清除会话信息
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)