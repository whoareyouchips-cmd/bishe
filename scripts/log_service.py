import pymysql

def get_conn():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="123456",  # 修改为你的密码
        database="sign_language",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

def add_log(user_id, word, confidence=1.0):
    conn = get_conn()
    cursor = conn.cursor()

    sql = """
        INSERT INTO recognition_logs (user_id, recognized_word, confidence)
        VALUES (%s, %s, %s)
    """

    try:
        cursor.execute(sql, (user_id, word, confidence))
        conn.commit()
        return {"status": "ok", "msg": "日志已写入"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}
    finally:
        cursor.close()
        conn.close()
