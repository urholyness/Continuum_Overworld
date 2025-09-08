"""
Health check utilities for Comms Agents Switchboard.
"""

import os
import asyncio
import logging
from typing import Dict, Any
import httpx
import redis
import psycopg
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def check_services_health() -> Dict[str, str]:
    """Check health of all services."""
    health_checks = {
        "database": "unknown",
        "redis": "unknown",
        "chromadb": "unknown",
        "rabbitmq": "unknown",
        "celery": "unknown",
    }
    
    # Run health checks concurrently
    tasks = [
        check_database_health(),
        check_redis_health(),
        check_chromadb_health(),
        check_rabbitmq_health(),
        check_celery_health(),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Update health status
    for i, result in enumerate(results):
        service_name = list(health_checks.keys())[i]
        if isinstance(result, Exception):
            health_checks[service_name] = "unhealthy"
            logger.error(f"Health check failed for {service_name}: {result}")
        else:
            health_checks[service_name] = "healthy"
    
    return health_checks


async def check_database_health() -> bool:
    """Check PostgreSQL database health."""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.warning("DATABASE_URL not set")
            return False
        
        # Use asyncpg for health check
        async with psycopg.AsyncConnection.connect(database_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                result = await cur.fetchone()
                return result[0] == 1
                
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def check_redis_health() -> bool:
    """Check Redis health."""
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Create Redis client
        r = redis.from_url(redis_url)
        
        # Test connection
        r.ping()
        return True
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


async def check_chromadb_health() -> bool:
    """Check ChromaDB health."""
    try:
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8001")
        
        # Test HTTP connection
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://{chroma_host}:{chroma_port}/api/v2/heartbeat")
            return response.status_code == 200
            
    except Exception as e:
        logger.error(f"ChromaDB health check failed: {e}")
        return False


async def check_rabbitmq_health() -> bool:
    """Check RabbitMQ health."""
    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        rabbitmq_port = os.getenv("RABBITMQ_MANAGEMENT_PORT", "15672")
        
        # Test HTTP connection to management interface
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://{rabbitmq_host}:{rabbitmq_port}/api/overview")
            return response.status_code == 200
            
    except Exception as e:
        logger.error(f"RabbitMQ health check failed: {e}")
        return False


async def check_celery_health() -> bool:
    """Check Celery health."""
    try:
        # This is a basic check - in production you might want to check worker status
        # For now, we'll assume it's healthy if Redis is healthy
        return await check_redis_health()
        
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return False


async def check_specific_service(service_name: str) -> Dict[str, Any]:
    """Check health of a specific service."""
    health_checks = {
        "database": check_database_health,
        "redis": check_redis_health,
        "chromadb": check_chromadb_health,
        "rabbitmq": check_rabbitmq_health,
        "celery": check_celery_health,
    }
    
    if service_name not in health_checks:
        return {
            "status": "unknown",
            "error": f"Unknown service: {service_name}",
            "timestamp": None
        }
    
    try:
        start_time = asyncio.get_event_loop().time()
        is_healthy = await health_checks[service_name]()
        end_time = asyncio.get_event_loop().time()
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "response_time_ms": round(response_time, 2),
            "timestamp": asyncio.get_event_loop().time(),
            "error": None
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": asyncio.get_event_loop().time(),
            "response_time_ms": None
        }


def get_health_summary(health_status: Dict[str, str]) -> Dict[str, Any]:
    """Get a summary of health status."""
    total_services = len(health_status)
    healthy_services = sum(1 for status in health_status.values() if status == "healthy")
    unhealthy_services = sum(1 for status in health_status.values() if status == "unhealthy")
    unknown_services = sum(1 for status in health_status.values() if status == "unknown")
    
    overall_status = "healthy"
    if unhealthy_services > 0:
        overall_status = "unhealthy"
    elif unknown_services == total_services:
        overall_status = "unknown"
    
    return {
        "overall_status": overall_status,
        "total_services": total_services,
        "healthy_services": healthy_services,
        "unhealthy_services": unhealthy_services,
        "unknown_services": unknown_services,
        "health_percentage": round((healthy_services / total_services) * 100, 2) if total_services > 0 else 0
    }

