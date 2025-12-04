import pymysql

def get_connection():
    """连接 MySQL 数据库，返回连接对象"""
    connection = pymysql.connect(
        host="localhost",         # 或者你 Navicat 的服务器地址
        port=3306,                # 默认端口
        user="root",              # 改成你的 Navicat 用户名
        password="123456",  # 改成你的密码
        database="sign_language", # 你的数据库名
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


# 通用查询（SELECT）
def query(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    result = cursor.fetchall()
    conn.close()
    return result


# 通用执行（INSERT / UPDATE / DELETE）
def execute(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()


# --- 测试部分：运行此文件会测试数据库连接 ---
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("数据库连接成功！")
        conn.close()
    except Exception as e:
        print("数据库连接失败：", e)
