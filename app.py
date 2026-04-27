"""
Object Detection Engine
Simple YOLO-based object detection with text-to-speech support
"""

import cv2
from ultralytics import YOLO
import os
import platform
import subprocess
from collections import Counter
import threading


# =========================
# CONFIG
# =========================
YOLO_MODEL_PATH = "yolo11n.pt"  # Path to YOLO model


# =========================
# OBJECT DETECTOR
# =========================
class SceneDescriptor:
    def __init__(self, model_path=YOLO_MODEL_PATH):
        """
        Initialize the object detector with YOLO model.
        
        Args:
            model_path: Path to YOLO model
        """
        self.model_path = model_path
        self.yolo_model = None
        
        # Load YOLO model
        if os.path.exists(model_path):
            print(f"Loading YOLO model from {model_path}...")
            self.yolo_model = YOLO(model_path)
            print("YOLO model loaded successfully!")
        else:
            print(f"Warning: YOLO model not found at {model_path}")
            print("Downloading default YOLO model...")
            self.yolo_model = YOLO('yolo11n.pt')
    
    def detect_objects(self, image):
        """
        Detect objects in the image using YOLO.
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            dict: Contains detected objects, their counts, and positions
        """
        if self.yolo_model is None:
            return {"objects": [], "counts": {}, "details": []}
        
        # Run YOLO detection
        results = self.yolo_model(image, verbose=False)
        
        detected_objects = []
        object_details = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class name and confidence
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                confidence = float(box.conf[0])
                
                # Get bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Determine position in frame
                img_height, img_width = image.shape[:2]
                position = self._get_position_description(center_x, center_y, img_width, img_height)
                
                detected_objects.append(class_name)
                object_details.append({
                    "name": class_name,
                    "confidence": confidence,
                    "position": position,
                    "bbox": [x1, y1, x2, y2]
                })
        
        # Count occurrences
        object_counts = dict(Counter(detected_objects))
        
        return {
            "objects": detected_objects,
            "counts": object_counts,
            "details": object_details
        }
    
    def _get_position_description(self, x, y, width, height):
        """Describe the position of an object in the frame."""
        # Divide frame into 9 sections (3x3 grid)
        h_third = width / 3
        v_third = height / 3
        
        # Horizontal position
        if x < h_third:
            h_pos = "left"
        elif x < 2 * h_third:
            h_pos = "center"
        else:
            h_pos = "right"
        
        # Vertical position
        if y < v_third:
            v_pos = "top"
        elif y < 2 * v_third:
            v_pos = "middle"
        else:
            v_pos = "bottom"
        
        if h_pos == "center" and v_pos == "middle":
            return "in the center"
        elif h_pos == "center":
            return f"at the {v_pos}"
        elif v_pos == "middle":
            return f"on the {h_pos}"
        else:
            return f"in the {v_pos} {h_pos}"
    
    def speak(self, text, threaded=False):
        """
        Convert text to speech.
        
        Args:
            text: Text to speak
            threaded: If True, speak in background thread (recommended for live video)
        """
        if threaded:
            # Use threading to prevent blocking the video loop
            thread = threading.Thread(target=self._speak_internal, args=(text,))
            thread.daemon = True
            thread.start()
        else:
            self._speak_internal(text)
    
    def _speak_internal(self, text):
        """Internal speech method with error recovery."""
        # Truncate very long messages to prevent timeouts
        max_words = 50
        words = text.split()
        
        if len(words) > max_words:
            text = ' '.join(words[:max_words]) + "..."
            print(f"  Message truncated from {len(words)} to {max_words} words")
        
        print(f"\n Speaking: {text}\n")
        
        # Try macOS 'say' command first (most reliable on Mac)
        if platform.system() == 'Darwin':  # macOS
            try:
                subprocess.run(['say', text], check=True, timeout=20)
                return
            except subprocess.TimeoutExpired:
                print(f"  Speech timeout - message too long")
                # Try a shorter version
                short_text = ' '.join(text.split()[:20])
                try:
                    subprocess.run(['say', short_text], check=True, timeout=10)
                    return
                except:
                    pass
            except (subprocess.SubprocessError, FileNotFoundError) as e:
                print(f" macOS 'say' command failed: {e}")
        
        # Fallback: just print the message
        print(f"\n [TTS unavailable] {text}\n")
    
    def visualize_detection(self, image, detection_data):
        """
        Draw bounding boxes and labels on the image.
        
        Args:
            image: OpenCV image
            detection_data: Detection results
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        for detail in detection_data["details"]:
            x1, y1, x2, y2 = map(int, detail["bbox"])
            name = detail["name"]
            confidence = detail["confidence"]
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{name} {confidence:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return annotated
