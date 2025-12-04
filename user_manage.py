from database import query, execute
from permission import require_role


# ------------------------------
# 获取所有用户（只有管理员能做）
# ------------------------------
def admin_get_all_users(admin_user):
    check = require_role(admin_user["role"], ["admin"])
    if check["status"] != "ok":
        return check

    users = query("SELECT id, username, role, nickname, create_time FROM users")
    return {"status": "ok", "data": users}


# ------------------------------
# 删除用户（只有管理员能做）
# ------------------------------
def admin_delete_user(admin_user, target_user_id):
    check = require_role(admin_user["role"], ["admin"])
    if check["status"] != "ok":
        return check

    execute("DELETE FROM users WHERE id=%s", (target_user_id,))
    return {"status": "ok", "msg": "用户已删除"}


# ------------------------------
# 修改用户角色（只有管理员能做）
# ------------------------------
def admin_update_role(admin_user, target_user_id, new_role):
    check = require_role(admin_user["role"], ["admin"])
    if check["status"] != "ok":
        return check

    if new_role not in ["normal", "admin", "advanced"]:
        return {"status": "error", "msg": "角色不合法"}

    execute("UPDATE users SET role=%s WHERE id=%s", (new_role, target_user_id))
    return {"status": "ok", "msg": f"角色已更新为 {new_role}"}


# ------------------------------
# 管理员重置用户密码（可选功能）
# ------------------------------
import bcrypt
def admin_reset_password(admin_user, target_user_id, new_password="123456"):
    check = require_role(admin_user["role"], ["admin"])
    if check["status"] != "ok":
        return check

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    execute("UPDATE users SET password=%s WHERE id=%s", (hashed, target_user_id))

    return {"status": "ok", "msg": "密码已重置为 123456"}


# ------------------------------
# 测试功能（直接运行 user_manage.py）
# ------------------------------
if __name__ == "__main__":
    # 模拟管理员
    admin = {"id": 1, "username": "admin", "role": "admin"}

    print("=== 查看全部用户 ===")
    print(admin_get_all_users(admin))

    print("\n=== 修改用户角色（用户2 → 高级） ===")
    print(admin_update_role(admin, 2, "advanced"))

    print("\n=== 删除用户（用户3） ===")
    print(admin_delete_user(admin, 3))

    print("\n=== 重置用户密码（用户2） ===")
    print(admin_reset_password(admin, 2))
