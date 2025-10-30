"""
Prometheus metrics integration for monitoring.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request
from fastapi.responses import PlainTextResponse
import time

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'socketio_active_connections',
    'Number of active Socket.IO connections'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Number of active database connections'
)

MESSAGE_COUNT = Counter(
    'messages_total',
    'Total number of messages sent',
    ['chatroom_id']
)

USER_COUNT = Gauge(
    'users_total',
    'Total number of registered users'
)

CHATROOM_COUNT = Gauge(
    'chatrooms_total',
    'Total number of chatrooms'
)


class MetricsMiddleware:
    """Middleware to collect Prometheus metrics."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        start_time = time.time()
        
        # Process request
        response_sent = False
        
        async def send_wrapper(message):
            nonlocal response_sent
            if not response_sent and message["type"] == "http.response.start":
                response_sent = True
                
                # Record metrics
                duration = time.time() - start_time
                method = request.method
                path = request.url.path
                status_code = message["status"]
                
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=path,
                    status_code=status_code
                ).inc()
                
                REQUEST_DURATION.labels(
                    method=method,
                    endpoint=path
                ).observe(duration)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def get_metrics_response() -> PlainTextResponse:
    """Get Prometheus metrics response."""
    data = generate_latest()
    return PlainTextResponse(data, media_type=CONTENT_TYPE_LATEST)


def update_user_count(count: int) -> None:
    """Update user count metric."""
    USER_COUNT.set(count)


def update_chatroom_count(count: int) -> None:
    """Update chatroom count metric."""
    CHATROOM_COUNT.set(count)


def increment_message_count(chatroom_id: str) -> None:
    """Increment message count for a chatroom."""
    MESSAGE_COUNT.labels(chatroom_id=chatroom_id).inc()


def update_active_connections(count: int) -> None:
    """Update active Socket.IO connections count."""
    ACTIVE_CONNECTIONS.set(count)
