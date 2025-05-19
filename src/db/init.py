# 定义一个数据库连接函数，我用的是mysql
# 编码为utf8mb4，ip为192.168.10.100，密码和账号为root
def get_db():
    import pymysql
    db = pymysql.connect(host='192.168.10.100',
                         user='root',
                         password='root',
                         db='KN',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
    return db