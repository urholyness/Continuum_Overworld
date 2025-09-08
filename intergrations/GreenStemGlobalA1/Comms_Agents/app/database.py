"""
Database configuration and connection management for Comms Agents.
"""

import os
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://comms_user:comms_password@localhost:5432/comms_db"
)

# SQLAlchemy configuration
engine = None
async_session = None

# Base class for models
Base = declarative_base()

# Metadata for database schema
metadata = MetaData()


async def init_db():
    """Initialize database connection and create tables."""
    global engine, async_session
    
    try:
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=os.getenv("DEBUG", "false").lower() == "true",
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        # Create async session factory
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT 1"))
        
        logger.info("Database connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    if not async_session:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def close_db():
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


@asynccontextmanager
async def get_db_context():
    """Context manager for database sessions."""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


async def execute_query(query: str, params: dict = None):
    """Execute a raw SQL query."""
    if not engine:
        raise RuntimeError("Database not initialized")
    
    async with engine.begin() as conn:
        if params:
            result = await conn.execute(query, params)
        else:
            result = await conn.execute(query)
        return result


async def health_check_db():
    """Check database health."""
    try:
        if not engine:
            return False
        
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Database models (these will be imported from separate files)
from app.models.posts import Post
from app.models.approvals import Approval
from app.models.events import Event
from app.models.campaigns import Campaign
from app.models.risk_logs import RiskLog
from app.models.knowledge_base import KnowledgeBase
from app.models.issue_cards import IssueCard
from app.models.agent_runs import AgentRun
from app.models.workflows import Workflow
from app.models.workflow_runs import WorkflowRun

# Export all models
__all__ = [
    "Base",
    "metadata",
    "init_db",
    "get_db",
    "close_db",
    "get_db_context",
    "execute_query",
    "health_check_db",
    "Post",
    "Approval",
    "Event",
    "Campaign",
    "RiskLog",
    "KnowledgeBase",
    "IssueCard",
    "AgentRun",
    "Workflow",
    "WorkflowRun",
]

