import pymysql

DB = {
    "host": "localhost",
    "user": "root",
    "password": "123456",   # 修改为你的密码
    "database": "sign_language",
    "charset": "utf8mb4"
}

def query_logs(role, user_id, target_user=None):
    conn = pymysql.connect(**DB)
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 权限控制
    if role == "normal":
        condition = f"user_id = {user_id}"
    elif role == "advanced":
        condition = f"user_id = {user_id}"
    elif role == "admin":
        condition = f"user_id = {target_user}" if target_user else "1=1"
    else:
        return {"status": "error", "msg": "未知角色"}

    sql = f"""
        SELECT id, user_id, recognized_word, confidence, create_time
        FROM recognition_logs
        WHERE {condition}
        ORDER BY create_time DESC
    """

    cursor.execute(sql)
    data = cursor.fetchall()
    conn.close()

    return {"status": "ok", "count": len(data), "data": data}
