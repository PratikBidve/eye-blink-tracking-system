"""
WebSocket-based Eye Tracker Service with video streaming and real-time blink detection
"""
import cv2
import mediapipe as mp
import numpy as np
import asyncio
import base64
from datetime import datetime
import pytz
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

class EyeTrackerService:
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.blink_count = 0
        self.last_blink_count = -1
        self.EAR_THRESH = 0.25  # Increased sensitivity for faster blinks
        self.CONSEC_FRAMES = 1  # Reduced to detect very fast blinks
        self.frame_counter = 0
        self.blink_cooldown = 0  # Prevent double counting
        self.india_tz = pytz.timezone('Asia/Kolkata')
        self.send_video = True
        
    def euclidean_dist(self, pt1, pt2):
        return np.linalg.norm(np.array(pt1) - np.array(pt2))

    def eye_aspect_ratio(self, eye_landmarks):
        A = self.euclidean_dist(eye_landmarks[1], eye_landmarks[5])
        B = self.euclidean_dist(eye_landmarks[2], eye_landmarks[4])
        C = self.euclidean_dist(eye_landmarks[0], eye_landmarks[3])
        return (A + B) / (2.0 * C)

    def encode_frame(self, frame):
        """Encode frame to base64 for WebSocket transmission"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return frame_base64

    async def start_tracking(self, callback: Callable[[dict], None], send_video: bool = True):
        """Start eye tracking with optional video streaming"""
        if self.is_running:
            logger.warning("Eye tracker already running, stopping first...")
            self.stop_tracking()
            # Give a moment for cleanup
            await asyncio.sleep(0.1)
            
        try:
            # Try to release any existing camera first
            if self.cap:
                self.cap.release()
                self.cap = None
                await asyncio.sleep(0.1)
            
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                logger.error("Could not open camera")
                return {"success": False, "message": "Could not open camera"}
                
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
                
            self.is_running = True
            self.send_video = send_video
            self.blink_count = 0
            self.last_blink_count = -1
            self.frame_counter = 0
            self.blink_cooldown = 0
            
            logger.info("🚀 Starting eye tracker service with video streaming")
            
            with mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            ) as face_mesh:
                
                while self.is_running:
                    ret, frame = self.cap.read()
                    if not ret:
                        break
                    
                    # Flip frame horizontally for mirror effect
                    frame = cv2.flip(frame, 1)
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_mesh.process(rgb)

                    # Draw face mesh and detect blinks
                    if results.multi_face_landmarks:
                        h, w, _ = frame.shape
                        for face_landmarks in results.multi_face_landmarks:
                            # Draw face mesh
                            mp_drawing.draw_landmarks(
                                frame, face_landmarks, mp_face_mesh.FACEMESH_CONTOURS,
                                None, mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1)
                            )
                            
                            # Extract eye landmarks
                            left_eye = [(int(face_landmarks.landmark[i].x * w), 
                                       int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE]
                            right_eye = [(int(face_landmarks.landmark[i].x * w), 
                                        int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE]
                            
                            # Draw eye contours
                            cv2.polylines(frame, [np.array(left_eye)], True, (255, 0, 0), 2)
                            cv2.polylines(frame, [np.array(right_eye)], True, (255, 0, 0), 2)
                            
                            # Calculate eye aspect ratio
                            left_ear = self.eye_aspect_ratio(left_eye)
                            right_ear = self.eye_aspect_ratio(right_eye)
                            ear = (left_ear + right_ear) / 2.0
                            
                            # Improved blink detection logic for fast blinks
                            if self.blink_cooldown > 0:
                                self.blink_cooldown -= 1
                            
                            if ear < self.EAR_THRESH:
                                self.frame_counter += 1
                            else:
                                # Blink detected when coming out of closed state
                                if self.frame_counter >= self.CONSEC_FRAMES and self.blink_cooldown == 0:
                                    self.blink_count += 1
                                    self.blink_cooldown = 3  # 3-frame cooldown to prevent double counting
                                self.frame_counter = 0
                    
                    # Add overlay text
                    cv2.putText(frame, f'Blinks: {self.blink_count}', (30, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    cv2.putText(frame, f'Status: {"Detecting..." if self.is_running else "Stopped"}', 
                               (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    
                    # Get current India time
                    current_time = datetime.now(self.india_tz)
                    time_str = current_time.strftime('%H:%M:%S IST')
                    cv2.putText(frame, time_str, (30, frame.shape[0] - 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Send data via WebSocket
                    message_data = {
                        "type": "frame_data",
                        "blink_count": self.blink_count,
                        "timestamp": current_time.isoformat(),
                        "ear_threshold": self.EAR_THRESH,
                        "frame_counter": self.frame_counter
                    }
                    
                    # Add video frame if streaming enabled
                    if self.send_video:
                        message_data["video_frame"] = self.encode_frame(frame)
                    
                    # Send blink count update when it changes
                    if self.blink_count != self.last_blink_count:
                        message_data["blink_changed"] = True
                        self.last_blink_count = self.blink_count
                    
                    try:
                        await callback(message_data)
                    except Exception as e:
                        logger.error(f"Error sending data via callback: {e}")
                        # If we can't send data, stop tracking to prevent spam
                        logger.info("🛑 Stopping tracker due to callback error")
                        break
                    
                    # Control frame rate (~30 FPS)
                    await asyncio.sleep(0.033)
                    
        except Exception as e:
            logger.error(f"Eye tracker error: {e}")
            return {"success": False, "message": f"Eye tracking failed: {str(e)}"}
        finally:
            self.stop_tracking()
            
        return {"success": True, "message": "Eye tracking completed"}

    def stop_tracking(self):
        """Stop eye tracking"""
        logger.info("🛑 Stopping eye tracker service...")
        self.is_running = False
        
        if self.cap:
            try:
                self.cap.release()
                logger.info("📷 Camera released successfully")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
            finally:
                self.cap = None
        
        # Reset counters
        self.blink_count = 0
        self.last_blink_count = -1
        self.frame_counter = 0
        self.blink_cooldown = 0
        
        logger.info("🛑 Eye tracker service stopped and cleaned up")

    def get_status(self):
        """Get current tracking status"""
        return {
            "is_running": self.is_running,
            "blink_count": self.blink_count,
            "send_video": self.send_video
        }

# Global instance
eye_tracker_service = EyeTrackerService()
