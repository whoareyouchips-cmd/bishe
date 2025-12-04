import bcrypt
from database import query, execute


# 密码加密
def hash_password(password: str) -> str:
    password = password.encode("utf-8")
    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    return hashed.decode("utf-8")


# 密码验证
def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ------------------------------
# 注册接口
# ------------------------------
def register(username: str, password: str, role: str = "normal"):
    # 1. 判断用户是否已存在
    exists = query("SELECT id FROM users WHERE username=%s", (username,))
    if exists:
        return {"status": "error", "msg": "用户名已存在"}

    # 2. 加密密码
    hashed = hash_password(password)

    # 3. 插入数据库
    execute("""
        INSERT INTO users (username, password, role)
        VALUES (%s, %s, %s)
    """, (username, hashed, role))

    return {"status": "ok", "msg": "注册成功"}


# ------------------------------
# 登录接口
# ------------------------------
def login(username: str, password: str):
    # 1. 查询用户
    result = query("SELECT * FROM users WHERE username=%s", (username,))

    if not result:
        return {"status": "error", "msg": "用户不存在"}

    user = result[0]

    # 2. 验证密码
    if not check_password(password, user["password"]):
        return {"status": "error", "msg": "密码错误"}

    return {
        "status": "ok",
        "msg": "登录成功",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }


# ------------------------------
# 测试（直接运行 auth.py）
# ------------------------------
if __name__ == "__main__":
    print("=== 注册测试 ===")

    print(register("admin", "123456", "admin"))
    print(register("adv", "123456", "advanced"))
    print(register("user", "123456", "normal"))

    print("\n=== 登录测试 ===")
    print(login("test1", "123456"))
