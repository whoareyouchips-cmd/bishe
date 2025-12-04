# query_logs_api.py
from scripts.log_query_service import query_logs

def test_query():
    print("=== 管理员查全部 ===")
    print(query_logs(role="admin", user_id=2))

    print("\n=== 管理员查某个用户 ===")
    print(query_logs(role="admin", user_id=2, target_user=3))

    print("\n=== 高级用户只能查自己的 ===")
    print(query_logs(role="advanced", user_id=3))

    print("\n=== 普通用户只能查自己的 ===")
    print(query_logs(role="normal", user_id=4))

if __name__ == "__main__":
    test_query()
