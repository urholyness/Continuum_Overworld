"""
Metrics middleware for Prometheus monitoring in Comms Agents Switchboard.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Simple in-memory metrics (in production, use proper Prometheus client)
_metrics = {
    "http_requests_total": {},
    "http_request_duration_seconds": {},
    "http_request_size_bytes": {},
    "http_response_size_bytes": {},
    "http_requests_in_progress": 0,
}


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()
        
        # Increment requests in progress
        _metrics["http_requests_in_progress"] += 1
        
        # Extract request information
        method = request.method
        path = request.url.path
        status_code = 500  # Default to error
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            process_time = time.time() - start_time
            
            # Collect metrics
            self._collect_metrics(method, path, status_code, process_time, request, response)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            status_code = 500
            
            # Collect error metrics
            self._collect_metrics(method, path, status_code, process_time, request, None)
            
            raise
        
        finally:
            # Decrement requests in progress
            _metrics["http_requests_in_progress"] -= 1
    
    def _collect_metrics(self, method: str, path: str, status_code: int, 
                         process_time: float, request: Request, response: Response):
        """Collect various metrics from the request/response."""
        # Request count
        key = f"{method}_{path}_{status_code}"
        _metrics["http_requests_total"][key] = _metrics["http_requests_total"].get(key, 0) + 1
        
        # Request duration
        _metrics["http_request_duration_seconds"][key] = process_time
        
        # Request size (approximate)
        request_size = len(str(request.url)) + len(str(dict(request.headers)))
        if hasattr(request, 'body'):
            try:
                body = await request.body()
                request_size += len(body)
            except:
                pass
        
        _metrics["http_request_size_bytes"][key] = request_size
        
        # Response size
        if response:
            response_size = len(response.body) if hasattr(response, 'body') else 0
            _metrics["http_response_size_bytes"][key] = response_size


def get_metrics() -> dict:
    """Get current metrics for Prometheus scraping."""
    return _metrics


def format_prometheus_metrics() -> str:
    """Format metrics in Prometheus text format."""
    lines = []
    
    # HTTP requests total
    for key, value in _metrics["http_requests_total"].items():
        method, path, status = key.split("_", 2)
        lines.append(f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {value}')
    
    # HTTP request duration
    for key, value in _metrics["http_request_duration_seconds"].items():
        method, path, status = key.split("_", 2)
        lines.append(f'http_request_duration_seconds{{method="{method}",path="{path}",status="{status}"}} {value}')
    
    # HTTP request size
    for key, value in _metrics["http_request_size_bytes"].items():
        method, path, status = key.split("_", 2)
        lines.append(f'http_request_size_bytes{{method="{method}",path="{path}",status="{status}"}} {value}')
    
    # HTTP response size
    for key, value in _metrics["http_response_size_bytes"].items():
        method, path, status = key.split("_", 2)
        lines.append(f'http_response_size_bytes{{method="{method}",path="{path}",status="{status}"}} {value}')
    
    # HTTP requests in progress
    lines.append(f'http_requests_in_progress {_metrics["http_requests_in_progress"]}')
    
    return "\n".join(lines)


def reset_metrics():
    """Reset all metrics (useful for testing)."""
    global _metrics
    _metrics = {
        "http_requests_total": {},
        "http_request_duration_seconds": {},
        "http_request_size_bytes": {},
        "http_response_size_bytes": {},
        "http_requests_in_progress": 0,
    }

