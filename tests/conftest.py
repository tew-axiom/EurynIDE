"""
Pytest配置文件
提供测试fixtures和配置
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.database.connection import Base
from app.config import settings


# ============================================
# 测试数据库配置
# ============================================

# 使用测试数据库URL
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_k12"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """
    创建事件循环
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """
    创建测试数据库引擎
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    创建测试数据库会话
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


# ============================================
# Mock数据Fixtures
# ============================================

@pytest.fixture
def mock_user_id() -> str:
    """Mock用户ID"""
    return "test_user_123"


@pytest.fixture
def mock_session_id() -> str:
    """Mock会话ID"""
    return "test_session_456"


@pytest.fixture
def mock_session_data(mock_user_id: str, mock_session_id: str) -> dict:
    """Mock会话数据"""
    return {
        "session_id": mock_session_id,
        "user_id": mock_user_id,
        "mode": "literature",
        "title": "测试会话",
        "grade_level": "middle",
        "subject": "语文"
    }


@pytest.fixture
def mock_chat_message_data(mock_session_id: str) -> dict:
    """Mock聊天消息数据"""
    return {
        "session_id": mock_session_id,
        "role": "user",
        "content": "这是一条测试消息",
        "message_type": "text",
        "tokens_used": 10,
        "model_used": "qwen-plus"
    }


@pytest.fixture
def mock_analysis_data(mock_session_id: str) -> dict:
    """Mock分析数据"""
    return {
        "session_id": mock_session_id,
        "analysis_type": "grammar",
        "content_version": 1,
        "content_hash": "abc123",
        "results": {
            "errors": [],
            "score": 95
        },
        "processing_time_ms": 100,
        "tokens_used": 50,
        "model_used": "qwen-plus"
    }


# ============================================
# API测试Fixtures
# ============================================

@pytest.fixture
def mock_qwen_response():
    """Mock Qwen API响应"""
    from app.services.llm.qwen_client import QwenResponse

    return QwenResponse(
        content="这是一个测试响应",
        model="qwen-plus",
        tokens_used=20,
        finish_reason="stop",
        response_time_ms=150.0
    )


@pytest.fixture
def mock_tools():
    """Mock工具定义"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "获取天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]


@pytest.fixture
def mock_tool_functions():
    """Mock工具函数"""
    def get_weather(city: str) -> dict:
        return {
            "city": city,
            "temperature": 25,
            "condition": "晴天"
        }

    return {
        "get_weather": get_weather
    }


# ============================================
# 测试配置
# ============================================

def pytest_configure(config):
    """
    Pytest配置钩子
    """
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "asyncio: 异步测试"
    )


# ============================================
# 测试辅助函数
# ============================================

def assert_dict_contains(actual: dict, expected: dict) -> None:
    """
    断言字典包含期望的键值对

    Args:
        actual: 实际字典
        expected: 期望的键值对
    """
    for key, value in expected.items():
        assert key in actual, f"键 '{key}' 不存在于实际字典中"
        assert actual[key] == value, f"键 '{key}' 的值不匹配: 期望 {value}, 实际 {actual[key]}"


def assert_list_length(actual: list, expected_length: int) -> None:
    """
    断言列表长度

    Args:
        actual: 实际列表
        expected_length: 期望长度
    """
    assert len(actual) == expected_length, f"列表长度不匹配: 期望 {expected_length}, 实际 {len(actual)}"
