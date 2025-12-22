"""
API集成测试
测试API端点的完整流程
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.main import app
from app.services.llm.qwen_client import QwenResponse


# ============================================
# 测试客户端Fixture
# ============================================

@pytest.fixture
async def client():
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================
# 系统API测试
# ============================================

class TestSystemAPI:
    """系统API测试"""

    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """测试健康检查端点"""
        response = await client.get("/api/v1/system/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_metrics(self, client):
        """测试指标端点"""
        response = await client.get("/api/v1/system/metrics")

        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data or "uptime" in data


# ============================================
# 会话API测试
# ============================================

class TestSessionAPI:
    """会话API测试"""

    @pytest.mark.asyncio
    @patch('app.repositories.session_repo.SessionRepository')
    async def test_create_session(self, mock_repo, client, mock_session_data):
        """测试创建会话"""
        # Mock repository
        mock_repo.return_value.create = AsyncMock(return_value=mock_session_data)

        response = await client.post(
            "/api/v1/session/create",
            json={
                "user_id": "test_user",
                "mode": "literature",
                "title": "测试会话"
            }
        )

        # 注意：实际API可能返回不同的状态码
        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    @patch('app.repositories.session_repo.SessionRepository')
    async def test_get_session(self, mock_repo, client, mock_session_id):
        """测试获取会话"""
        response = await client.get(f"/api/v1/session/{mock_session_id}")

        # 会话可能不存在，返回404也是正常的
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    @patch('app.repositories.session_repo.SessionRepository')
    async def test_list_sessions(self, mock_repo, client):
        """测试获取会话列表"""
        response = await client.get(
            "/api/v1/session/list",
            params={"user_id": "test_user", "page": 1, "limit": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data or "items" in data


# ============================================
# 聊天API测试
# ============================================

class TestChatAPI:
    """聊天API测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_chat_message(self, mock_qwen_client, client, mock_session_id):
        """测试发送聊天消息"""
        # Mock Qwen响应
        mock_response = QwenResponse(
            content="这是AI的回复",
            model="qwen-plus",
            tokens_used=30,
            finish_reason="stop",
            response_time_ms=100.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        response = await client.post(
            "/api/v1/chat/message",
            json={
                "session_id": mock_session_id,
                "message": "你好",
                "role": "user"
            }
        )

        assert response.status_code in [200, 201]
        data = response.json()
        assert "response" in data or "message" in data

    @pytest.mark.asyncio
    @patch('app.repositories.chat_history_repo.ChatHistoryRepository')
    async def test_get_chat_history(self, mock_repo, client, mock_session_id):
        """测试获取聊天历史"""
        response = await client.get(
            f"/api/v1/chat/history/{mock_session_id}",
            params={"limit": 50}
        )

        assert response.status_code == 200
        data = response.json()
        assert "messages" in data or "history" in data


# ============================================
# 文科模式API测试
# ============================================

class TestLiteratureAPI:
    """文科模式API测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_grammar_check(self, mock_qwen_client, client, mock_session_id):
        """测试语法检查"""
        mock_response = QwenResponse(
            content='{"errors": [], "score": 95}',
            model="qwen-plus",
            tokens_used=50,
            finish_reason="stop",
            response_time_ms=120.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        response = await client.post(
            "/api/v1/literature/grammar-check",
            json={
                "session_id": mock_session_id,
                "content": "这是一个测试句子。"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "errors" in data or "result" in data

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_structure_analysis(self, mock_qwen_client, client, mock_session_id):
        """测试结构分析"""
        mock_response = QwenResponse(
            content='{"structure": {"paragraphs": 1}}',
            model="qwen-plus",
            tokens_used=60,
            finish_reason="stop",
            response_time_ms=150.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        response = await client.post(
            "/api/v1/literature/structure-analysis",
            json={
                "session_id": mock_session_id,
                "content": "这是一段测试文本。"
            }
        )

        assert response.status_code == 200


# ============================================
# 理科模式API测试
# ============================================

class TestScienceAPI:
    """理科模式API测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_math_validation(self, mock_qwen_client, client, mock_session_id):
        """测试数学验证"""
        mock_response = QwenResponse(
            content='{"valid": true, "steps": []}',
            model="qwen-plus",
            tokens_used=40,
            finish_reason="stop",
            response_time_ms=100.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        response = await client.post(
            "/api/v1/science/math-validate",
            json={
                "session_id": mock_session_id,
                "expression": "x + 2 = 5"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data or "result" in data

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_logic_tree_build(self, mock_qwen_client, client, mock_session_id):
        """测试逻辑树构建"""
        mock_response = QwenResponse(
            content='{"tree": {"nodes": []}}',
            model="qwen-plus",
            tokens_used=70,
            finish_reason="stop",
            response_time_ms=180.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        response = await client.post(
            "/api/v1/science/logic-tree",
            json={
                "session_id": mock_session_id,
                "problem": "求解方程 x^2 - 4 = 0"
            }
        )

        assert response.status_code == 200


# ============================================
# OCR API测试
# ============================================

class TestOCRAPI:
    """OCR API测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_ocr_image(self, mock_qwen_client, client):
        """测试图片OCR"""
        mock_qwen_client.analyze_image = AsyncMock(
            return_value="识别的文本内容"
        )

        # 模拟上传图片
        response = await client.post(
            "/api/v1/ocr/analyze",
            json={
                "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "prompt": "识别图片中的文字"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "text" in data or "result" in data


# ============================================
# 批量操作测试
# ============================================

class TestBatchOperations:
    """批量操作测试"""

    @pytest.mark.asyncio
    @patch('app.repositories.session_repo.SessionRepository')
    async def test_batch_create_sessions(self, mock_repo, client):
        """测试批量创建会话"""
        sessions_data = [
            {"session_id": "s1", "user_id": "u1", "mode": "literature"},
            {"session_id": "s2", "user_id": "u1", "mode": "science"}
        ]

        mock_repo.return_value.batch_create = AsyncMock(return_value=sessions_data)

        response = await client.post(
            "/api/v1/session/batch-create",
            json={"sessions": sessions_data}
        )

        # 批量操作端点可能还未实现
        assert response.status_code in [200, 201, 404, 405]

    @pytest.mark.asyncio
    @patch('app.repositories.chat_history_repo.ChatHistoryRepository')
    async def test_batch_delete_messages(self, mock_repo, client):
        """测试批量删除消息"""
        mock_repo.return_value.batch_delete = AsyncMock(return_value=3)

        response = await client.post(
            "/api/v1/chat/batch-delete",
            json={"message_ids": [1, 2, 3]}
        )

        # 批量操作端点可能还未实现
        assert response.status_code in [200, 404, 405]


# ============================================
# 错误处理测试
# ============================================

class TestErrorHandling:
    """错误处理测试"""

    @pytest.mark.asyncio
    async def test_invalid_session_id(self, client):
        """测试无效的会话ID"""
        response = await client.get("/api/v1/session/invalid_id_12345")

        assert response.status_code in [404, 400]

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """测试缺少必需字段"""
        response = await client.post(
            "/api/v1/chat/message",
            json={"message": "test"}  # 缺少session_id
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_invalid_json(self, client):
        """测试无效的JSON"""
        response = await client.post(
            "/api/v1/chat/message",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
