# Farm 5.0 - Task Scheduler and Queue System
# scheduler.py

import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import heapq
import uuid
import json
from abc import ABC, abstractmethod

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"

@dataclass(order=True)
class ScheduledTask:
    """Represents a scheduled task"""
    priority: int = field(compare=True)
    scheduled_time: datetime = field(compare=True)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    agent_id: str = field(compare=False)
    task_type: str = field(compare=False)
    task_data: Dict[str, Any] = field(default_factory=dict, compare=False)
    retry_count: int = field(default=0, compare=False)
    max_retries: int = field(default=3, compare=False)
    status: TaskStatus = field(default=TaskStatus.PENDING, compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    completed_at: Optional[datetime] = field(default=None, compare=False)
    result: Optional[Dict[str, Any]] = field(default=None, compare=False)
    error: Optional[str] = field(default=None, compare=False)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "task_type": self.task_type,
            "task_data": self.task_data,
            "priority": self.priority,
            "status": self.status.value,
            "scheduled_time": self.scheduled_time.isoformat(),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "retry_count": self.retry_count,
            "error": self.error
        }

class TaskQueue:
    """Priority queue for task management"""
    
    def __init__(self):
        self._queue: List[ScheduledTask] = []
        self._task_map: Dict[str, ScheduledTask] = {}
        self._lock = asyncio.Lock()
    
    async def add_task(self, task: ScheduledTask) -> str:
        """Add a task to the queue"""
        async with self._lock:
            heapq.heappush(self._queue, task)
            self._task_map[task.task_id] = task
            return task.task_id
    
    async def get_next_task(self) -> Optional[ScheduledTask]:
        """Get the next task to execute"""
        async with self._lock:
            now = datetime.now()
            
            # Find tasks that are ready to run
            while self._queue:
                task = self._queue[0]
                
                if task.scheduled_time <= now and task.status == TaskStatus.PENDING:
                    heapq.heappop(self._queue)
                    task.status = TaskStatus.RUNNING
                    return task
                elif task.status != TaskStatus.PENDING:
                    # Remove completed/failed/cancelled tasks
                    heapq.heappop(self._queue)
                else:
                    # No tasks ready yet
                    break
            
            return None
    
    async def update_task_status(self, task_id: str, status: TaskStatus, 
                                result: Optional[Dict[str, Any]] = None,
                                error: Optional[str] = None):
        """Update task status"""
        async with self._lock:
            if task_id in self._task_map:
                task = self._task_map[task_id]
                task.status = status
                task.result = result
                task.error = error
                
                if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now()
    
    async def retry_task(self, task_id: str, delay_seconds: int = 60):
        """Retry a failed task"""
        async with self._lock:
            if task_id in self._task_map:
                task = self._task_map[task_id]
                if task.retry_count < task.max_retries:
                    task.retry_count += 1
                    task.status = TaskStatus.PENDING
                    task.scheduled_time = datetime.now() + timedelta(seconds=delay_seconds)
                    heapq.heappush(self._queue, task)
                    return True
        return False
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task"""
        async with self._lock:
            if task_id in self._task_map:
                task = self._task_map[task_id]
                if task.status == TaskStatus.PENDING:
                    task.status = TaskStatus.CANCELLED
                    return True
        return False
    
    async def get_pending_tasks(self, agent_id: Optional[str] = None) -> List[ScheduledTask]:
        """Get all pending tasks, optionally filtered by agent"""
        async with self._lock:
            tasks = []
            for task in self._task_map.values():
                if task.status == TaskStatus.PENDING:
                    if agent_id is None or task.agent_id == agent_id:
                        tasks.append(task)
            return sorted(tasks, key=lambda t: (t.priority, t.scheduled_time))

class RecurringTaskSchedule:
    """Define recurring task schedules"""
    
    def __init__(self, 
                 task_template: Dict[str, Any],
                 frequency: str,
                 start_time: Optional[datetime] = None,
                 end_time: Optional[datetime] = None):
        self.task_template = task_template
        self.frequency = frequency  # "daily", "weekly", "monthly", "hourly"
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.last_run = None
    
    def get_next_run_time(self) -> Optional[datetime]:
        """Calculate next run time based on frequency"""
        base_time = self.last_run or self.start_time
        
        if self.frequency == "hourly":
            next_time = base_time + timedelta(hours=1)
        elif self.frequency == "daily":
            next_time = base_time + timedelta(days=1)
        elif self.frequency == "weekly":
            next_time = base_time + timedelta(weeks=1)
        elif self.frequency == "monthly":
            # Simple approximation
            next_time = base_time + timedelta(days=30)
        else:
            return None
        
        if self.end_time and next_time > self.end_time:
            return None
        
        return next_time
    
    def create_task(self) -> ScheduledTask:
        """Create a new task instance from template"""
        return ScheduledTask(
            agent_id=self.task_template["agent_id"],
            task_type=self.task_template["task_type"],
            task_data=self.task_template.get("task_data", {}),
            priority=self.task_template.get("priority", TaskPriority.MEDIUM.value),
            scheduled_time=self.get_next_run_time() or datetime.now()
        )

class TaskScheduler:
    """Main task scheduler"""
    
    def __init__(self, agent_manager):
        self.agent_manager = agent_manager
        self.task_queue = TaskQueue()
        self.recurring_schedules: Dict[str, RecurringTaskSchedule] = {}
        self._running = False
        self._scheduler_task = None
        self.execution_history: List[Dict[str, Any]] = []
    
    async def start(self):
        """Start the scheduler"""
        if not self._running:
            self._running = True
            self._scheduler_task = asyncio.create_task(self._run_scheduler())
            
            # Schedule initial recurring tasks
            await self._schedule_recurring_tasks()
    
    async def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._scheduler_task:
            await self._scheduler_task
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        while self._running:
            try:
                # Get next task
                task = await self.task_queue.get_next_task()
                
                if task:
                    # Execute task
                    await self._execute_task(task)
                else:
                    # No tasks ready, wait a bit
                    await asyncio.sleep(1)
                
                # Check for new recurring tasks
                await self._schedule_recurring_tasks()
                
            except Exception as e:
                print(f"Scheduler error: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: ScheduledTask):
        """Execute a single task"""
        try:
            # Get the agent
            agent = self.agent_manager.get_agent(task.agent_id)
            if not agent:
                raise ValueError(f"Agent not found: {task.agent_id}")
            
            # Execute the task
            result = await agent.execute_task({
                "type": task.task_type,
                **task.task_data
            })
            
            # Update task status
            await self.task_queue.update_task_status(
                task.task_id,
                TaskStatus.COMPLETED,
                result=result
            )
            
            # Log execution
            self._log_execution(task, "success", result)
            
        except Exception as e:
            error_msg = str(e)
            await self.task_queue.update_task_status(
                task.task_id,
                TaskStatus.FAILED,
                error=error_msg
            )
            
            # Log execution
            self._log_execution(task, "failed", None, error_msg)
            
            # Retry if applicable
            if task.retry_count < task.max_retries:
                retry_delay = 60 * (task.retry_count + 1)  # Exponential backoff
                await self.task_queue.retry_task(task.task_id, retry_delay)
    
    async def _schedule_recurring_tasks(self):
        """Check and schedule recurring tasks"""
        now = datetime.now()
        
        for schedule_id, schedule in self.recurring_schedules.items():
            next_run = schedule.get_next_run_time()
            
            if next_run and next_run <= now:
                # Create and schedule the task
                task = schedule.create_task()
                await self.task_queue.add_task(task)
                schedule.last_run = now
    
    def _log_execution(self, task: ScheduledTask, status: str, 
                      result: Optional[Dict[str, Any]] = None,
                      error: Optional[str] = None):
        """Log task execution"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "task_type": task.task_type,
            "status": status,
            "duration": (task.completed_at - task.created_at).total_seconds() if task.completed_at else None,
            "retry_count": task.retry_count,
            "error": error
        }
        
        self.execution_history.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]
    
    async def schedule_task(self, agent_id: str, task_type: str,
                          task_data: Dict[str, Any] = None,
                          priority: TaskPriority = TaskPriority.MEDIUM,
                          scheduled_time: Optional[datetime] = None) -> str:
        """Schedule a one-time task"""
        task = ScheduledTask(
            agent_id=agent_id,
            task_type=task_type,
            task_data=task_data or {},
            priority=priority.value,
            scheduled_time=scheduled_time or datetime.now()
        )
        
        return await self.task_queue.add_task(task)
    
    def add_recurring_schedule(self, schedule_id: str, 
                             agent_id: str, task_type: str,
                             frequency: str,
                             task_data: Dict[str, Any] = None,
                             priority: TaskPriority = TaskPriority.MEDIUM):
        """Add a recurring task schedule"""
        template = {
            "agent_id": agent_id,
            "task_type": task_type,
            "task_data": task_data or {},
            "priority": priority.value
        }
        
        schedule = RecurringTaskSchedule(template, frequency)
        self.recurring_schedules[schedule_id] = schedule
    
    async def get_scheduled_tasks(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all scheduled tasks"""
        tasks = await self.task_queue.get_pending_tasks(agent_id)
        return [task.to_dict() for task in tasks]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0,
                "average_duration": 0,
                "by_agent": {}
            }
        
        total = len(self.execution_history)
        successful = len([e for e in self.execution_history if e["status"] == "success"])
        
        durations = [e["duration"] for e in self.execution_history if e["duration"]]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Stats by agent
        by_agent = {}
        for entry in self.execution_history:
            agent_id = entry["agent_id"]
            if agent_id not in by_agent:
                by_agent[agent_id] = {"total": 0, "success": 0, "failed": 0}
            
            by_agent[agent_id]["total"] += 1
            if entry["status"] == "success":
                by_agent[agent_id]["success"] += 1
            else:
                by_agent[agent_id]["failed"] += 1
        
        return {
            "total_executions": total,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "average_duration": avg_duration,
            "by_agent": by_agent
        }

# Example usage
def setup_default_schedules(scheduler: TaskScheduler):
    """Set up default recurring schedules"""
    
    # Daily email processing
    scheduler.add_recurring_schedule(
        "daily_email_processing",
        "email_manager_001",
        "process_inbox",
        "daily",
        priority=TaskPriority.HIGH
    )
    
    # Weekly market research
    scheduler.add_recurring_schedule(
        "weekly_market_research",
        "research_agent_001",
        "analyze_market",
        "weekly",
        task_data={"market": "AgTech"},
        priority=TaskPriority.MEDIUM
    )
    
    # Daily sales follow-ups
    scheduler.add_recurring_schedule(
        "daily_sales_followups",
        "sales_agent_001",
        "check_followups",
        "daily",
        priority=TaskPriority.HIGH
    )
    
    # Weekly performance review
    scheduler.add_recurring_schedule(
        "weekly_performance_review",
        "growth_agent_001",
        "weekly_review",
        "weekly",
        priority=TaskPriority.MEDIUM
    )
    
    # Hourly system metrics
    scheduler.add_recurring_schedule(
        "hourly_metrics",
        "analytics_agent_001",
        "collect_metrics",
        "hourly",
        priority=TaskPriority.LOW
    )
