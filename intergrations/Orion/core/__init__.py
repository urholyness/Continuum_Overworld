# Farm 5.0 Agent System - Core Module
"""
Core framework for the Farm 5.0 Agent System.
Contains base classes and essential functionality for all agents.
"""

from .base_agent import BaseAgent, AgentStatus, AgentManager
from .task_scheduler import TaskScheduler

__version__ = "1.0.0"
__all__ = ["BaseAgent", "AgentStatus", "AgentManager", "TaskScheduler"]