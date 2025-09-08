"""
Tests for Scribe agent.
"""

import pytest
from app.deps import ScribeIn, ScribeOut
from agents.scribe import ScribeAgent


def test_scribe_agent_initialization():
    """Test Scribe agent initialization."""
    agent = ScribeAgent()
    assert agent is not None
    assert hasattr(agent, 'llm_client')
    assert hasattr(agent, 'system_prompt')


def test_scribe_agent_system_prompt_loading():
    """Test system prompt loading."""
    agent = ScribeAgent()
    assert agent.system_prompt is not None
    assert len(agent.system_prompt) > 0
    assert "Scribe" in agent.system_prompt


@pytest.mark.asyncio
async def test_scribe_agent_run():
    """Test Scribe agent run method."""
    agent = ScribeAgent()
    
    payload = ScribeIn(
        issue_card_path="issue_cards/eudr_smallholders.md",
        audience="buyer",
        tone="boardroom"
    )
    
    result = await agent.run(payload)
    
    assert isinstance(result, ScribeOut)
    assert result.linkedin_post is not None
    assert result.x_thread is not None
    assert result.comments_pack is not None
    assert result.citations is not None


def test_scribe_input_validation():
    """Test Scribe input validation."""
    # Valid input
    valid_input = ScribeIn(
        issue_card_path="issue_cards/eudr_smallholders.md",
        audience="buyer",
        tone="boardroom"
    )
    assert valid_input.issue_card_path == "issue_cards/eudr_smallholders.md"
    assert valid_input.audience.value == "buyer"
    assert valid_input.tone.value == "boardroom"


def test_scribe_output_structure():
    """Test Scribe output structure."""
    output = ScribeOut(
        linkedin_post="Test LinkedIn post",
        x_thread=["Tweet 1", "Tweet 2"],
        comments_pack=["Comment 1", "Comment 2", "Comment 3"],
        citations=["https://example.com"],
        metadata={"test": "data"}
    )
    
    assert output.linkedin_post == "Test LinkedIn post"
    assert len(output.x_thread) == 2
    assert len(output.comments_pack) == 3
    assert len(output.citations) == 1
    assert output.metadata["test"] == "data"

