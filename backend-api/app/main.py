"""
Main FastAPI app for Wellness at Work backend.
"""
from fastapi import FastAPI, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from . import models, schemas, database, crud, auth
from .database import SessionLocal, engine
from .eye_tracker_service import eye_tracker_service
from typing import List
import logging
import json
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    logger.error(f"Validation error for {request.method} {request.url}: {exc.errors()}")
    logger.error(f"Request body: {body}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body.decode() if body else ""}
    )

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    """Health check endpoint."""
    return {"msg": "Wellness at Work API is running."}

@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get JWT token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/blinks/upload", response_model=schemas.BlinkDataOut)
def upload_blink(blink: schemas.BlinkDataCreate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Upload blink data for the current user."""
    logger.info(f"Received blink data: {blink}")
    logger.info(f"User: {current_user.email}")
    return crud.create_blink_data(db, user_id=current_user.id, blink=blink)

@app.get("/blinks/user", response_model=List[schemas.BlinkDataOut])
def get_user_blinks(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """Get all blink data for the current user."""
    return crud.get_blinks_for_user(db, user_id=current_user.id)

@app.websocket("/ws/eye-tracker/{token}")
async def websocket_eye_tracker(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time eye tracking"""
    await websocket.accept()
    
    try:
        # Verify JWT token
        try:
            payload = auth.verify_token(token)
            user_email = payload.get("sub")
            if not user_email:
                await websocket.send_text(json.dumps({"error": "Invalid token"}))
                return
                
            user = crud.get_user_by_email(db, email=user_email)
            if not user:
                await websocket.send_text(json.dumps({"error": "User not found"}))
                return
                
        except Exception as e:
            await websocket.send_text(json.dumps({"error": "Authentication failed"}))
            return
        
        logger.info(f"👤 Eye tracker WebSocket connected for user: {user.email}")
        
        # Callback function to send blink data
        async def send_blink_data(blink_data):
            try:
                # Save to database
                blink_create = schemas.BlinkDataCreate(
                    blink_count=blink_data["blink_count"],
                    timestamp=None  # Will be set to India time in crud
                )
                crud.create_blink_data(db, user_id=user.id, blink=blink_create)
                
                # Only send to WebSocket client if connection is still open
                try:
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_text(json.dumps(blink_data))
                        logger.info(f"📊 Sent blink data: {blink_data}")
                    else:
                        logger.info(f"📊 WebSocket closed, saved blink data to DB only: {blink_data}")
                except:
                    # WebSocket is closed, just save to database
                    logger.info(f"📊 WebSocket unavailable, saved blink data to DB only: {blink_data}")
                
            except Exception as e:
                logger.error(f"Error processing blink data: {e}")
        
        # Start eye tracking
        logger.info(f"🎬 Starting eye tracking for user: {user.email}")
        
        # Create a task for eye tracking
        tracking_task = asyncio.create_task(
            eye_tracker_service.start_tracking(send_blink_data)
        )
        
        # Create a task for listening to messages
        async def message_listener():
            try:
                while True:
                    message = await websocket.receive_text()
                    try:
                        data = json.loads(message)
                        if data.get("type") == "stop_command":
                            logger.info(f"🛑 Received stop command from user: {user.email}")
                            eye_tracker_service.stop_tracking()
                            await websocket.send_text(json.dumps({
                                "type": "stop_confirmed",
                                "message": "Eye tracker stopped successfully"
                            }))
                            return  # Exit the listener
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON message received: {message}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
            except WebSocketDisconnect:
                logger.info(f"👋 WebSocket disconnected for user: {user.email}")
            except Exception as e:
                logger.error(f"WebSocket message listener error: {e}")
        
        # Start message listener task
        message_task = asyncio.create_task(message_listener())
        
        # Wait for either tracking to complete or message listener to stop
        try:
            done, pending = await asyncio.wait(
                [tracking_task, message_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel any pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error in task coordination: {e}")
        
        # Get result from tracking task if completed
        result = None
        if tracking_task.done() and not tracking_task.cancelled():
            try:
                result = await tracking_task
            except Exception as e:
                logger.error(f"Eye tracking task error: {e}")
        
        if result and not result.get("success", True):
            await websocket.send_text(json.dumps({"error": result.get("message", "Failed to start eye tracking")}))
            return
        
    except WebSocketDisconnect:
        logger.info(f"👋 WebSocket disconnected for user: {user.email}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user.email}: {e}")
        try:
            await websocket.send_text(json.dumps({"error": f"Tracking error: {str(e)}"}))
        except:
            pass  # WebSocket might be closed
    finally:
        logger.info(f"🧹 Cleaning up eye tracker service for user: {user.email}")
        try:
            eye_tracker_service.stop_tracking()
            logger.info(f"✅ Eye tracker service cleaned up successfully for user: {user.email}")
        except Exception as e:
            logger.error(f"Error during cleanup for user {user.email}: {e}")
        
        # Ensure database connection is closed
        try:
            db.close()
        except:
            pass

@app.post("/eye-tracker/start")
async def start_eye_tracker(current_user: models.User = Depends(auth.get_current_user)):
    """Start eye tracking (alternative to WebSocket)"""
    # This could be used for simple start/stop without real-time data
    return {"message": "Use WebSocket endpoint /ws/eye-tracker/{token} for real-time tracking"}

@app.post("/eye-tracker/stop")
async def stop_eye_tracker(current_user: models.User = Depends(auth.get_current_user)):
    """Stop eye tracking"""
    eye_tracker_service.stop_tracking()
    return {"message": "Eye tracker stopped"} 