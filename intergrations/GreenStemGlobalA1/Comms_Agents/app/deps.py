"""
Dependencies and data models for Comms Agents Switchboard.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


class Audience(str, Enum):
    """Target audience for content."""
    POLICY = "policy"
    INVESTOR = "investor"
    BUYER = "buyer"
    PUBLIC = "public"


class Tone(str, Enum):
    """Content tone and style."""
    BOARDROOM = "boardroom"
    POLICY_BRIEF = "policy-brief"
    FIELD_NOTES = "field-notes"
    VISION_THREAD = "vision-thread"
    HUMOR_LIGHT = "humor-light"


class Platform(str, Enum):
    """Social media platforms."""
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    EMAIL = "email"
    BUFFER = "buffer"


class Status(str, Enum):
    """Post status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class Severity(str, Enum):
    """Event severity levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Input Models
class ScribeIn(BaseModel):
    """Input for Scribe agent."""
    issue_card_path: str = Field(..., description="Path to issue card file")
    audience: Audience = Field(..., description="Target audience")
    tone: Tone = Field(..., description="Content tone and style")
    campaign_id: Optional[UUID] = Field(None, description="Associated campaign ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SignalIn(BaseModel):
    """Input for Signal agent."""
    focus_regions: Optional[List[str]] = Field(None, description="Geographic regions to focus on")
    topics: Optional[List[str]] = Field(None, description="Topics to monitor")
    sources: Optional[List[str]] = Field(None, description="News sources to scan")
    time_window: Optional[str] = Field("24h", description="Time window for scanning")


class SentinelIn(BaseModel):
    """Input for Sentinel agent."""
    content: str = Field(..., description="Content to risk assess")
    jurisdiction: str = Field(..., description="Legal jurisdiction")
    platform: Platform = Field(..., description="Target platform")
    audience: Audience = Field(..., description="Target audience")


class LiaisonIn(BaseModel):
    """Input for Liaison agent."""
    target_profile: str = Field(..., description="Target profile or contact")
    campaign_goal: str = Field(..., description="Campaign objective")
    hooks: List[str] = Field(..., description="Engagement hooks")
    platform: Platform = Field(..., description="Platform for outreach")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class ConductorIn(BaseModel):
    """Input for Conductor agent."""
    platform: Platform = Field(..., description="Target platform")
    content: str = Field(..., description="Content to schedule")
    when: str = Field(..., description="Scheduling time")
    campaign_id: Optional[UUID] = Field(None, description="Associated campaign")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AnalystIn(BaseModel):
    """Input for Analyst agent."""
    campaign_id: Optional[UUID] = Field(None, description="Campaign to analyze")
    post_id: Optional[UUID] = Field(None, description="Specific post to analyze")
    time_range: Optional[str] = Field("7d", description="Analysis time range")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to analyze")


class CartographerIn(BaseModel):
    """Input for Cartographer agent."""
    path: str = Field(..., description="Path to document or content")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for categorization")
    source_type: str = Field("document", description="Type of source")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


# Output Models
class ScribeOut(BaseModel):
    """Output from Scribe agent."""
    linkedin_post: str = Field(..., description="LinkedIn post content")
    x_thread: List[str] = Field(..., description="X (Twitter) thread content")
    comments_pack: List[str] = Field(..., description="Engagement comments")
    citations: List[str] = Field(..., description="Source citations")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SignalOut(BaseModel):
    """Output from Signal agent."""
    pulse_digest: str = Field(..., description="Summary of current events")
    engage_now: List[Dict[str, str]] = Field(..., description="Immediate engagement opportunities")
    trending_topics: List[str] = Field(..., description="Trending topics")
    risk_alerts: List[str] = Field(..., description="Risk alerts")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class SentinelOut(BaseModel):
    """Output from Sentinel agent."""
    risk: RiskLevel = Field(..., description="Risk assessment level")
    notes: List[str] = Field(..., description="Risk assessment notes")
    recommendations: List[str] = Field(..., description="Risk mitigation recommendations")
    compliance_check: Dict[str, bool] = Field(..., description="Compliance check results")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class LiaisonOut(BaseModel):
    """Output from Liaison agent."""
    email: Optional[str] = Field(None, description="Email draft")
    linkedin_comment: Optional[str] = Field(None, description="LinkedIn comment draft")
    twitter_reply: Optional[str] = Field(None, description="Twitter reply draft")
    dm_draft: Optional[str] = Field(None, description="Direct message draft")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ConductorOut(BaseModel):
    """Output from Conductor agent."""
    scheduled_id: UUID = Field(..., description="Scheduled post ID")
    utm: str = Field(..., description="UTM tracking parameters")
    status: Status = Field(..., description="Scheduling status")
    scheduled_at: datetime = Field(..., description="Scheduled time")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class AnalystOut(BaseModel):
    """Output from Analyst agent."""
    kpis: Dict[str, Any] = Field(..., description="Key performance indicators")
    insights: List[str] = Field(..., description="Performance insights")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    trends: Dict[str, Any] = Field(..., description="Trend analysis")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class CartographerOut(BaseModel):
    """Output from Cartographer agent."""
    entities: List[str] = Field(..., description="Extracted entities")
    vectors: int = Field(..., description="Number of vectors created")
    summary: str = Field(..., description="Content summary")
    tags: List[str] = Field(..., description="Generated tags")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


# Database Models
class Post(BaseModel):
    """Database model for posts."""
    id: UUID
    platform: Platform
    content: str
    status: Status
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
    tags: List[str]

    class Config:
        from_attributes = True


class Approval(BaseModel):
    """Database model for approvals."""
    id: UUID
    post_id: UUID
    approver_id: Optional[str]
    approved: Optional[bool]
    approved_at: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class Event(BaseModel):
    """Database model for events."""
    id: UUID
    kind: str
    source: str
    payload: Dict[str, Any]
    severity: Severity
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class Campaign(BaseModel):
    """Database model for campaigns."""
    id: UUID
    name: str
    description: Optional[str]
    status: str
    start_date: Optional[str]
    end_date: Optional[str]
    meta: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskLog(BaseModel):
    """Database model for risk logs."""
    id: UUID
    post_id: UUID
    level: RiskLevel
    category: str
    notes: Dict[str, Any]
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class KnowledgeBase(BaseModel):
    """Database model for knowledge base."""
    id: UUID
    title: str
    content: str
    source_path: Optional[str]
    source_type: str
    tags: List[str]
    metadata: Dict[str, Any]
    embedding_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IssueCard(BaseModel):
    """Database model for issue cards."""
    id: UUID
    title: str
    summary: str
    content: str
    priority: str
    status: str
    tags: List[str]
    sources: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentRun(BaseModel):
    """Database model for agent runs."""
    id: UUID
    agent_name: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class Workflow(BaseModel):
    """Database model for workflows."""
    id: UUID
    name: str
    description: Optional[str]
    steps: Dict[str, Any]
    status: str
    schedule_cron: Optional[str]
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkflowRun(BaseModel):
    """Database model for workflow runs."""
    id: UUID
    workflow_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    results: Dict[str, Any]
    error_message: Optional[str]
    execution_time_ms: Optional[int]

    class Config:
        from_attributes = True


# Response Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Success response."""
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

