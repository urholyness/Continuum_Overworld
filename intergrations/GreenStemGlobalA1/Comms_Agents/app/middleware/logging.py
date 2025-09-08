"""
Logging middleware for Comms Agents Switchboard.
"""

import time
import logging
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log details."""
        start_time = time.time()
        
        # Log request
        await self._log_request(request)
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            await self._log_response(request, response, process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"Error: {str(e)} - Duration: {process_time:.3f}s"
            )
            raise
    
    async def _log_request(self, request: Request):
        """Log incoming request details."""
        # Extract request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)
        
        # Filter sensitive headers
        sensitive_headers = {"authorization", "cookie", "x-api-key"}
        filtered_headers = {
            k: v for k, v in headers.items() 
            if k.lower() not in sensitive_headers
        }
        
        # Log request
        logger.info(
            f"Request: {method} {path}",
            extra={
                "request_method": method,
                "request_url": url,
                "request_path": path,
                "query_params": query_params,
                "headers": filtered_headers,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
    
    async def _log_response(self, request: Request, response: Response, process_time: float):
        """Log response details."""
        method = request.method
        path = request.url.path
        status_code = response.status_code
        
        # Determine log level based on status code
        if status_code >= 500:
            log_level = logging.ERROR
        elif status_code >= 400:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO
        
        # Log response
        logger.log(
            log_level,
            f"Response: {method} {path} - Status: {status_code} - Duration: {process_time:.3f}s",
            extra={
                "request_method": method,
                "request_path": path,
                "response_status": status_code,
                "response_time": process_time,
                "response_size": len(response.body) if hasattr(response, 'body') else 0,
            }
        )
        
        # Log slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"Slow request: {method} {path} took {process_time:.3f}s",
                extra={
                    "request_method": method,
                    "request_path": path,
                    "response_time": process_time,
                    "threshold": 1.0,
                }
            )

