# test_db_connection.py
import os
from dotenv import load_dotenv
import pymysql

# 手动加载 .env 文件
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    print(f"❌ .env 文件不存在: {env_path}")
    exit(1)

load_dotenv(dotenv_path=env_path)

# 从环境变量获取数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_USER, DB_PASSWORD, DB_NAME]):
    print("❌ .env 中的 DB_USER, DB_PASSWORD 或 DB_NAME 未设置")
    exit(1)

print("尝试连接数据库:")
print(f"host={DB_HOST}, port={DB_PORT}, user={DB_USER}, db={DB_NAME}")

try:
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        # auth_plugin='caching_sha2_password'  # 明确指定认证插件
    )
    print("✅ 连接成功！")
    conn.close()
except pymysql.MySQLError as e:
    print("❌ 连接失败:")
    print(e)
