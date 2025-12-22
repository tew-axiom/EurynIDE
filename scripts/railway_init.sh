#!/bin/bash
# Railway 初始化脚本
# 在 Railway 部署后自动运行数据库迁移

set -e

echo "🚀 开始 Railway 部署初始化..."

# 设置 Python 路径
export PYTHONPATH=/app:$PYTHONPATH
echo "📍 PYTHONPATH 设置为: $PYTHONPATH"

# 等待数据库就绪
echo "⏳ 等待数据库连接..."
python -c "
import asyncio
import asyncpg
import os
import time
import sys

# 确保可以导入 app 模块
sys.path.insert(0, '/app')

async def wait_for_db():
    db_url = os.getenv('DATABASE_URL', '')
    if not db_url:
        print('❌ DATABASE_URL 未设置')
        exit(1)

    # 转换 postgres:// 为 postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    # 移除 +asyncpg 后缀用于连接测试
    test_url = db_url.replace('+asyncpg', '')

    max_retries = 30
    for i in range(max_retries):
        try:
            conn = await asyncpg.connect(test_url)
            await conn.close()
            print('✅ 数据库连接成功')
            return
        except Exception as e:
            print(f'⏳ 等待数据库... ({i+1}/{max_retries})')
            time.sleep(2)

    print('❌ 数据库连接超时')
    exit(1)

asyncio.run(wait_for_db())
"

# 运行数据库迁移
echo "📦 运行数据库迁移..."
cd /app && alembic upgrade head

echo "✅ Railway 初始化完成！"
