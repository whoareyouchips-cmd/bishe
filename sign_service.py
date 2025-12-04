from database import query, execute
from permission import require_role


def add_word(word: str, video_path: str, user):
    """
    添加手语词汇，只有管理员和高级用户能执行
    user: 登录成功后 auth.login() 返回的 user 字典
    """

    # 检查权限
    check = require_role(user["role"], ["admin", "advanced"])
    if check["status"] != "ok":
        return check

    # 插入数据库
    execute("""
        INSERT INTO sign_words (word, video_path, level, created_by)
        VALUES (%s, %s, %s, %s)
    """, (word, video_path, "custom", user["id"]))

    return {"status": "ok", "msg": "词汇添加成功"}
if __name__ == "__main__":
    # 假设管理员用户
    admin_user = {"id": 1, "username": "admin", "role": "admin"}

    # 假设普通用户
    normal_user = {"id": 2, "username": "user", "role": "normal"}

    print("管理员尝试添加：")
    print(add_word("你好", "/videos/hello.mp4", admin_user))

    print("\n普通用户尝试添加：")
    print(add_word("谢谢", "/videos/thanks.mp4", normal_user))
