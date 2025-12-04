# permission.py

def require_role(user_role: str, allowed_roles: list):
    """
    检查当前用户的角色是否有权限执行某个操作
    user_role: 当前用户角色 (normal/admin/advanced)
    allowed_roles: 允许执行该操作的角色列表
    """

    if user_role not in allowed_roles:
        return {
            "status": "error",
            "msg": f"权限不足，需要角色：{allowed_roles}，当前角色：{user_role}"
        }

    return {"status": "ok"}
