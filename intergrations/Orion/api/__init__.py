# Farm 5.0 Agent System - API Module
"""
FastAPI backend service for the Farm 5.0 Agent System.
Provides REST endpoints for agent management and monitoring.
"""

from .main import app

__version__ = "1.0.0"
__all__ = ["app"]