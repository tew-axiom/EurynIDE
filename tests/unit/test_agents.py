"""
Agent单元测试
测试各种Agent的核心功能
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.services.agents.base import BaseAgent
from app.services.llm.qwen_client import QwenResponse


# ============================================
# BaseAgent测试
# ============================================

class TestBaseAgent:
    """BaseAgent基础测试"""

    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """测试Agent初始化"""
        # 创建一个简单的Agent子类
        class TestAgent(BaseAgent):
            async def process(self, input_data: str) -> dict:
                return {"result": input_data}

        agent = TestAgent()
        assert agent is not None
        assert hasattr(agent, 'process')

    @pytest.mark.asyncio
    async def test_agent_process(self):
        """测试Agent处理方法"""
        class TestAgent(BaseAgent):
            async def process(self, input_data: str) -> dict:
                return {"result": f"processed: {input_data}"}

        agent = TestAgent()
        result = await agent.process("test input")

        assert result is not None
        assert "result" in result
        assert result["result"] == "processed: test input"


# ============================================
# GrammarChecker测试
# ============================================

class TestGrammarChecker:
    """语法检查Agent测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_grammar_check_basic(self, mock_qwen_client):
        """测试基础语法检查"""
        from app.services.agents.literature.grammar_checker import GrammarChecker

        # Mock Qwen响应
        mock_response = QwenResponse(
            content='{"errors": [], "score": 100}',
            model="qwen-plus",
            tokens_used=50,
            finish_reason="stop",
            response_time_ms=100.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        # 创建Agent并测试
        agent = GrammarChecker()
        result = await agent.check_grammar("这是一个正确的句子。")

        assert result is not None
        assert "errors" in result
        assert isinstance(result["errors"], list)

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_grammar_check_with_errors(self, mock_qwen_client):
        """测试检测语法错误"""
        from app.services.agents.literature.grammar_checker import GrammarChecker

        # Mock包含错误的响应
        mock_response = QwenResponse(
            content='{"errors": [{"type": "typo", "position": 0, "suggestion": "正确"}], "score": 80}',
            model="qwen-plus",
            tokens_used=60,
            finish_reason="stop",
            response_time_ms=120.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        agent = GrammarChecker()
        result = await agent.check_grammar("错误的句子")

        assert result is not None
        assert "errors" in result
        assert len(result["errors"]) > 0


# ============================================
# MathValidator测试
# ============================================

class TestMathValidator:
    """数学验证Agent测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_validate_math_expression(self, mock_qwen_client):
        """测试数学表达式验证"""
        from app.services.agents.science.math_validator import MathValidator

        # Mock响应
        mock_response = QwenResponse(
            content='{"valid": true, "steps": []}',
            model="qwen-plus",
            tokens_used=40,
            finish_reason="stop",
            response_time_ms=90.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        agent = MathValidator()
        result = await agent.validate("x + 2 = 5")

        assert result is not None
        assert "valid" in result

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_validate_invalid_expression(self, mock_qwen_client):
        """测试无效数学表达式"""
        from app.services.agents.science.math_validator import MathValidator

        mock_response = QwenResponse(
            content='{"valid": false, "errors": ["语法错误"]}',
            model="qwen-plus",
            tokens_used=45,
            finish_reason="stop",
            response_time_ms=95.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        agent = MathValidator()
        result = await agent.validate("x +++ 2")

        assert result is not None
        assert "valid" in result
        assert result["valid"] is False


# ============================================
# ChatAgent测试
# ============================================

class TestChatAgent:
    """聊天Agent测试"""

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_chat_basic(self, mock_qwen_client):
        """测试基础聊天功能"""
        from app.services.agents.common.chat_agent import ChatAgent

        mock_response = QwenResponse(
            content="你好！我是AI助手。",
            model="qwen-plus",
            tokens_used=30,
            finish_reason="stop",
            response_time_ms=80.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        agent = ChatAgent()
        result = await agent.chat("你好")

        assert result is not None
        assert "response" in result or isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.services.llm.qwen_client.qwen_client')
    async def test_chat_with_context(self, mock_qwen_client):
        """测试带上下文的聊天"""
        from app.services.agents.common.chat_agent import ChatAgent

        mock_response = QwenResponse(
            content="根据之前的对话，我理解你的问题。",
            model="qwen-plus",
            tokens_used=50,
            finish_reason="stop",
            response_time_ms=100.0
        )
        mock_qwen_client.complete = AsyncMock(return_value=mock_response)

        agent = ChatAgent()
        context = [
            {"role": "user", "content": "第一个问题"},
            {"role": "assistant", "content": "第一个回答"}
        ]
        result = await agent.chat("第二个问题", context=context)

        assert result is not None


# ============================================
# 工具函数测试
# ============================================

class TestTextTools:
    """文本工具测试"""

    def test_tokenize_text(self):
        """测试文本分词"""
        from app.utils.text_tools import tokenize_text

        text = "我爱自然语言处理"
        tokens = tokenize_text(text)

        assert tokens is not None
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_calculate_similarity(self):
        """测试相似度计算"""
        from app.utils.text_tools import calculate_similarity

        text1 = "我爱编程"
        text2 = "我喜欢编程"

        similarity = calculate_similarity(text1, text2)

        assert similarity is not None
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # 应该有一定相似度

    def test_extract_keywords(self):
        """测试关键词提取"""
        from app.utils.text_tools import extract_keywords

        text = "人工智能是未来科技发展的重要方向"
        keywords = extract_keywords(text, top_k=3)

        assert keywords is not None
        assert isinstance(keywords, list)
        assert len(keywords) <= 3


class TestMathTools:
    """数学工具测试"""

    def test_parse_math_expression(self):
        """测试数学表达式解析"""
        from app.utils.math_tools import parse_math_expression

        result = parse_math_expression("x**2 + 2*x + 1")

        assert result is not None
        assert result["success"] is True
        assert "expr" in result
        assert "latex" in result

    def test_validate_formula(self):
        """测试公式验证"""
        from app.utils.math_tools import validate_formula

        result = validate_formula("x**2 + 1", expected_variables=["x"])

        assert result is not None
        assert "valid" in result
        assert result["valid"] is True

    def test_solve_equation(self):
        """测试方程求解"""
        from app.utils.math_tools import solve_equation

        result = solve_equation("x**2 - 4 = 0", "x")

        assert result is not None
        assert result["success"] is True
        assert "solutions" in result


class TestDiffTools:
    """差分工具测试"""

    def test_compute_diff(self):
        """测试差分计算"""
        from app.utils.diff_tools import compute_diff

        old_text = "hello world"
        new_text = "hello python"

        result = compute_diff(old_text, new_text, granularity="word")

        assert result is not None
        assert hasattr(result, 'changes')
        assert hasattr(result, 'similarity')
        assert 0.0 <= result.similarity <= 1.0

    def test_get_change_summary(self):
        """测试变更摘要"""
        from app.utils.diff_tools import compute_diff, get_change_summary

        old_text = "line1\nline2"
        new_text = "line1\nline3"

        diff_result = compute_diff(old_text, new_text, granularity="line")
        summary = get_change_summary(diff_result)

        assert summary is not None
        assert "total_changes" in summary
        assert "additions" in summary
        assert "deletions" in summary


# ============================================
# 运行测试
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
