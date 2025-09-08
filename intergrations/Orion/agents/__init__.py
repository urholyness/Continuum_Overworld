# Farm 5.0 Agent System - Agents Module
"""
Contains all agent implementations for the Farm 5.0 system.
Each agent is responsible for specific business functions.
"""

from .email_management import EmailManagementAgent
from .sales_outreach import SalesOutreachAgent

__version__ = "1.0.0"
__all__ = ["EmailManagementAgent", "SalesOutreachAgent"]