"""
FastAPI application entrypoint.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from chatty.core.database import create_tables
from chatty.core.logging import configure_logging, get_logger
from chatty.core.middleware import ErrorLoggingMiddleware, LoggingMiddleware
from chatty.core.config import settings
from chatty.core.metrics import MetricsMiddleware, get_metrics_response
from chatty.routers import health, hello, users, chatrooms, messages, chatroom_participants

# Configure logging
configure_logging()
logger = get_logger("main")

# Create Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=settings.socketio_cors_origins,
    async_mode='asgi'
)

# Socket.IO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection."""
    logger.info(f"Client {sid} connected")

@sio.event
async def disconnect(sid):
    """Handle client disconnection."""
    logger.info(f"Client {sid} disconnected")

@sio.event
async def join(sid, data):
    """Handle client joining a chatroom."""
    try:
        user_id = data.get('user_id')
        chatroom_id = data.get('chatroom_id')
        
        if not user_id or not chatroom_id:
            await sio.emit('error', {'message': 'user_id and chatroom_id are required'}, room=sid)
            return
        
        # Join the room using chatroom_id as the room identifier
        await sio.enter_room(sid, chatroom_id)
        logger.info(f"Client {sid} (user {user_id}) joined chatroom {chatroom_id}")
        
        # Acknowledge the join
        await sio.emit('joined', {'chatroom_id': chatroom_id}, room=sid)
        
    except Exception as e:
        # TODO: Implement proper error handling for Socket.IO events
        logger.error(f"Error in join event: {e}")
        await sio.emit('error', {'message': 'An error occurred'}, room=sid)

@sio.event
async def leave(sid, data):
    """Handle client leaving a chatroom."""
    try:
        user_id = data.get('user_id')
        chatroom_id = data.get('chatroom_id')
        
        if not user_id or not chatroom_id:
            await sio.emit('error', {'message': 'user_id and chatroom_id are required'}, room=sid)
            return
        
        # Leave the room
        await sio.leave_room(sid, chatroom_id)
        logger.info(f"Client {sid} (user {user_id}) left chatroom {chatroom_id}")
        
        # Acknowledge the leave
        await sio.emit('left', {'chatroom_id': chatroom_id}, room=sid)
        
    except Exception as e:
        # TODO: Implement proper error handling for Socket.IO events
        logger.error(f"Error in leave event: {e}")
        await sio.emit('error', {'message': 'An error occurred'}, room=sid)

app = FastAPI(
    title=settings.app_name,
    description="Chatty Backend experimentation",
    version=settings.app_version,
    debug=settings.debug,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(LoggingMiddleware)

# Optional Prometheus metrics
if settings.enable_metrics:
    app.add_middleware(MetricsMiddleware)

    @app.get("/metrics")
    async def metrics():
        return get_metrics_response()

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    logger.info("Starting up Chatty Backend application", 
                app_env=settings.app_env, 
                database_url=settings.database_url.split("@")[-1] if "@" in settings.database_url else "sqlite")
    
    # Only drop and recreate tables in development
    if settings.is_development:
        from chatty.core.database import Base, engine
        Base.metadata.drop_all(bind=engine)  # Drop all existing tables
        logger.info("Existing database tables dropped (development mode)")
    
    create_tables()
    logger.info("Database tables created/verified successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Shutting down Chatty Backend application")

# Create Socket.IO ASGI app
socketio_app = socketio.ASGIApp(sio, app)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(hello.router, prefix="/hello", tags=["hello"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chatrooms.router, prefix="/chatrooms", tags=["chatrooms"])
app.include_router(messages.router, prefix="/messages", tags=["messages"])
app.include_router(chatroom_participants.router, prefix="/chatroom-participants", tags=["chatroom-participants"])

# Set Socket.IO server in messages router for event emission
messages.set_socketio_server(sio)

# Mount Socket.IO app
app.mount('/socket.io/', socketio_app)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to Chatty Backend!"}

