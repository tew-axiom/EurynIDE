#!/usr/bin/env python
"""
应用启动诊断脚本
用于检测应用启动时可能遇到的问题
"""

import sys
import os
import json

# 设置 Python 路径
sys.path.insert(0, '/app')
os.environ.setdefault('PYTHONPATH', '/app')

print("=" * 60)
print("🔍 开始应用启动诊断...")
print("=" * 60)

# 1. 检查环境变量
print("\n1️⃣ 检查环境变量...")
required_vars = ['DATABASE_URL', 'REDIS_URL', 'ENVIRONMENT']
optional_vars = ['QWEN_API_KEY', 'PORT', 'CORS_ORIGINS']

for var in required_vars:
    value = os.getenv(var)
    if value:
        # 隐藏敏感信息
        if 'URL' in var or 'KEY' in var:
            display_value = value[:20] + "..." if len(value) > 20 else value
        else:
            display_value = value
        print(f"   ✅ {var} = {display_value}")
    else:
        print(f"   ❌ {var} 未设置")

for var in optional_vars:
    value = os.getenv(var)
    if value:
        if 'KEY' in var:
            display_value = value[:10] + "..." if len(value) > 10 else value
        else:
            display_value = value
        print(f"   ℹ️  {var} = {display_value}")
    else:
        print(f"   ⚠️  {var} 未设置（可选）")

# 2. 测试导入配置
print("\n2️⃣ 测试导入配置...")
try:
    from app.config import settings
    print(f"   ✅ 配置加载成功")
    print(f"   - 应用名称: {settings.app_name}")
    print(f"   - 环境: {settings.environment}")
    print(f"   - 端口: {settings.port}")
    print(f"   - CORS Origins: {settings.cors_origins}")
    print(f"   - Qwen API Key: {'已设置' if settings.qwen_api_key else '未设置'}")
except Exception as e:
    print(f"   ❌ 配置加载失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. 测试数据库连接
print("\n3️⃣ 测试数据库连接...")
db_ok = False
db_error = None
try:
    import asyncio
    from app.database.connection import check_db_connection

    async def test_db():
        result = await check_db_connection()
        return result

    db_ok = asyncio.run(test_db())
    if db_ok:
        print(f"   ✅ 数据库连接正常")
    else:
        print(f"   ❌ 数据库连接失败")
except Exception as e:
    db_error = str(e)
    print(f"   ❌ 数据库测试失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 测试 Redis 连接
print("\n4️⃣ 测试 Redis 连接...")
redis_ok = False
redis_error = None
try:
    from app.cache.redis_client import check_redis_connection

    async def test_redis():
        result = await check_redis_connection()
        return result

    redis_ok = asyncio.run(test_redis())
    if redis_ok:
        print(f"   ✅ Redis 连接正常")
    else:
        print(f"   ❌ Redis 连接失败")
except Exception as e:
    redis_error = str(e)
    print(f"   ❌ Redis 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 5. 测试导入主应用
print("\n5️⃣ 测试导入主应用...")
app_ok = False
route_count = 0
try:
    from app.main import app
    app_ok = True
    route_count = len(app.routes)
    print(f"   ✅ FastAPI 应用导入成功")
    print(f"   - 应用标题: {app.title}")
    print(f"   - 应用版本: {app.version}")
    print(f"   - 路由数量: {route_count}")
except Exception as e:
    print(f"   ❌ 应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 6. 模拟健康检查
print("\n6️⃣ 模拟健康检查端点...")
health_check_result = {
    "status": "healthy" if (db_ok and redis_ok) else "unhealthy",
    "version": settings.app_version,
    "environment": settings.environment,
    "services": {
        "database": "up" if db_ok else "down",
        "redis": "up" if redis_ok else "down",
    },
    "diagnostics": {
        "config_loaded": True,
        "app_imported": app_ok,
        "route_count": route_count,
        "qwen_api_key_set": bool(settings.qwen_api_key),
        "database_error": db_error,
        "redis_error": redis_error,
    }
}

print("\n" + "=" * 60)
print("📊 健康检查结果 (JSON):")
print("=" * 60)
print(json.dumps(health_check_result, indent=2, ensure_ascii=False))
print("=" * 60)

if health_check_result["status"] == "healthy":
    print("✅ 诊断完成！应用应该可以正常启动。")
else:
    print("⚠️  诊断发现问题，但应用仍会尝试启动。")
    print("   请检查上述错误信息。")

print("=" * 60)
