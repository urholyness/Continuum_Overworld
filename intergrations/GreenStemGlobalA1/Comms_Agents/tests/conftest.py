"""
Test configuration and fixtures for Comms Agents.
"""

import pytest
import asyncio
from typing import AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base


# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_comms_db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

# Create test session factory
TestingSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db_setup():
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_db_setup) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture
def client(db_session: AsyncSession) -> TestClient:
    """Create a test client with database dependency override."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_scribe_input():
    """Sample input for Scribe agent tests."""
    return {
        "issue_card_path": "issue_cards/eudr_smallholders.md",
        "audience": "buyer",
        "tone": "boardroom",
        "campaign_id": None,
        "metadata": {}
    }


@pytest.fixture
def sample_signal_input():
    """Sample input for Signal agent tests."""
    return {
        "focus_regions": ["Kenya", "EU"],
        "topics": ["EUDR", "Trade"],
        "sources": None,
        "time_window": "24h"
    }


@pytest.fixture
def sample_sentinel_input():
    """Sample input for Sentinel agent tests."""
    return {
        "content": "Sample content for risk assessment",
        "jurisdiction": "EU",
        "platform": "linkedin",
        "audience": "buyer"
    }


@pytest.fixture
def sample_liaison_input():
    """Sample input for Liaison agent tests."""
    return {
        "target_profile": "John Doe",
        "campaign_goal": "introduction",
        "hooks": ["mutual interest in agriculture", "shared background"],
        "platform": "linkedin",
        "metadata": {}
    }


@pytest.fixture
def sample_conductor_input():
    """Sample input for Conductor agent tests."""
    return {
        "platform": "linkedin",
        "content": "Sample content to schedule",
        "when": "tomorrow 09:00",
        "campaign_id": None,
        "metadata": {}
    }


@pytest.fixture
def sample_analyst_input():
    """Sample input for Analyst agent tests."""
    return {
        "campaign_id": None,
        "post_id": None,
        "time_range": "7d",
        "metrics": ["engagement", "reach", "conversions"]
    }


@pytest.fixture
def sample_cartographer_input():
    """Sample input for Cartographer agent tests."""
    return {
        "path": "issue_cards/eudr_smallholders.md",
        "tags": ["EUDR", "Kenya", "smallholders"],
        "source_type": "issue_card",
        "metadata": {}
    }


# Mock data fixtures
@pytest.fixture
def mock_post_data():
    """Mock post data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "platform": "linkedin",
        "content": "Test post content",
        "status": "pending",
        "scheduled_at": None,
        "published_at": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "metadata": {},
        "tags": ["test", "sample"]
    }


@pytest.fixture
def mock_campaign_data():
    """Mock campaign data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Test Campaign",
        "description": "A test campaign for testing purposes",
        "status": "active",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "meta": {"target_audience": ["buyers"]},
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_workflow_data():
    """Mock workflow data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174002",
        "name": "Test Workflow",
        "description": "A test workflow for testing purposes",
        "steps": {"step1": "action1", "step2": "action2"},
        "status": "active",
        "schedule_cron": "0 9 * * *",
        "last_run_at": None,
        "next_run_at": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


# Utility functions for testing
def create_test_user():
    """Create a test user for authentication tests."""
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True
    }


def create_test_token(user_id: str = "test-user-123"):
    """Create a test JWT token."""
    from app.utils.auth import create_access_token
    return create_access_token(data={"sub": user_id})


# Async test utilities
@pytest.fixture
def async_client():
    """Create an async test client."""
    from httpx import AsyncClient
    return AsyncClient(app=app, base_url="http://test")


# Database utilities
async def clean_test_db():
    """Clean up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(autouse=True)
async def auto_clean_db():
    """Automatically clean database before each test."""
    await clean_test_db()
    yield
    await clean_test_db()

