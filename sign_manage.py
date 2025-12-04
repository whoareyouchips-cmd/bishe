from database import query, execute
from permission import require_role


# ------------------------------
# 1. 查看所有词汇（所有角色可用）
# ------------------------------
def get_all_words():
    words = query("""
        SELECT id, word, video_path, level, created_by, create_time
        FROM sign_words
    """)
    return {"status": "ok", "data": words}


# ------------------------------
# 2. 添加词汇（管理员、高级用户）
# ------------------------------
def add_word(word, video_path, user):
    check = require_role(user["role"], ["admin", "advanced"])
    if check["status"] != "ok":
        return check

    execute("""
        INSERT INTO sign_words (word, video_path, level, created_by)
        VALUES (%s, %s, %s, %s)
    """, (word, video_path, "custom", user["id"]))

    return {"status": "ok", "msg": "词汇添加成功"}


# ------------------------------
# 3. 修改词汇（管理员、高级用户）
# ------------------------------
def update_word(word_id, new_word, new_video_path, user):
    check = require_role(user["role"], ["admin", "advanced"])
    if check["status"] != "ok":
        return check

    execute("""
        UPDATE sign_words
        SET word=%s, video_path=%s
        WHERE id=%s
    """, (new_word, new_video_path, word_id))

    return {"status": "ok", "msg": "词汇更新成功"}


# ------------------------------
# 4. 删除词汇（只有管理员）
# ------------------------------
def delete_word(word_id, user):
    check = require_role(user["role"], ["admin"])
    if check["status"] != "ok":
        return check

    execute("DELETE FROM sign_words WHERE id=%s", (word_id,))
    return {"status": "ok", "msg": "词汇已删除"}


# ------------------------------
# 5. 搜索词汇（所有角色）
# ------------------------------
def search_word(keyword):
    result = query("""
        SELECT id, word, video_path, level, created_by, create_time
        FROM sign_words
        WHERE word LIKE %s
    """, (f"%{keyword}%",))
    return {"status": "ok", "data": result}


# ------------------------------
# 测试（直接运行 sign_manage.py）
# ------------------------------
if __name__ == "__main__":
    admin = {"id": 2, "username": "admin", "role": "admin"}
    advanced = {"id": 3, "username": "adv", "role": "advanced"}
    normal = {"id": 1, "username": "test1", "role": "normal"}

    print("=== 管理员尝试添加 ===")
    print(add_word("你好", "/videos/hello.mp4", admin))

    print("\n=== 高级用户尝试添加 ===")
    print(add_word("谢谢", "/videos/thanks.mp4", advanced))

    print("\n=== 普通用户尝试添加 ===")
    print(add_word("对不起", "/videos/sorry.mp4", normal))
