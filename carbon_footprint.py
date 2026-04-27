"""
Real-Time Carbon Footprint Estimator
Analyzes items via camera and displays their environmental impact
"""

from app import SceneDescriptor
from carbon_data import (
    get_item_data, 
    format_decomposition_time, 
    calculate_environmental_impact,
    get_environmental_rating
)
import cv2
import time


def run_carbon_footprint_analyzer(camera_index=0):
    """
    Real-time carbon footprint analysis from camera feed.
    
    Args:
        camera_index: Camera to use (0=laptop, 1=phone/external, 2=other)
    """
    print("\n" + "="*60)
    print("REAL-TIME CARBON FOOTPRINT ESTIMATOR")
    print("="*60)
    print("Hold items up to the camera to see their environmental impact")
    print("Press 's' to toggle speech, 'q' to quit, 'c' to switch camera")
    print("="*60)
    
    descriptor = SceneDescriptor()
    cap = cv2.VideoCapture(camera_index)
    
    # Verify camera opened successfully
    if not cap.isOpened():
        print(f" Error: Could not open camera {camera_index}")
        print("💡 Try a different camera index (0, 1, 2...)")
        return
    
    # Settings
    current_camera = camera_index
    last_speech_time = 0
    speech_cooldown = 10  # seconds between speech announcements
    speech_enabled = True
    is_speaking = False  # Track if currently speaking
    frame_skip = 3  # Process every 3rd frame
    frame_count = 0
    
    # Track items to avoid repeat announcements
    last_announced_item = None
    current_item = None
    item_stable_count = 0
    stability_threshold = 8  # frames needed before announcing (2-3 seconds)
    
    print(f"\n Starting environmental impact analyzer...")
    print(f" Camera: {camera_index} ({'Laptop' if camera_index == 0 else 'External/Phone'})")
    print(f"Speech: {'ENABLED' if speech_enabled else 'DISABLED'}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        img_height, img_width = frame.shape[:2]
        
        if frame_count % frame_skip == 0:
            # Detect objects in current frame
            detection = descriptor.detect_objects(frame)
            
            # Analyze items for environmental impact
            items_analysis = []
            
            for detail in detection['details']:
                obj_name = detail['name']
                confidence = detail.get('confidence', 0)
                
                # Skip person detections - only analyze objects
                if obj_name.lower() == 'person':
                    continue
                
                # Skip low confidence detections (less than 50%)
                if confidence < 0.5:
                    continue
                
                # Calculate object size (larger = closer to camera)
                x1, y1, x2, y2 = detail['bbox']
                bbox_width = x2 - x1
                bbox_height = y2 - y1
                bbox_area = bbox_width * bbox_height
                
                # Calculate normalized size (percentage of frame)
                frame_area = img_width * img_height
                size_percentage = (bbox_area / frame_area) * 100
                
                # Calculate distance from center (centered objects likely being presented)
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                frame_center_x = img_width / 2
                frame_center_y = img_height / 2
                distance_from_center = ((center_x - frame_center_x)**2 + (center_y - frame_center_y)**2)**0.5
                max_distance = ((img_width/2)**2 + (img_height/2)**2)**0.5
                center_score = 1 - (distance_from_center / max_distance)
                
                # Skip very small/distant objects (less than 2% of frame)
                if size_percentage < 2:
                    continue
                
                # Get environmental data
                env_data = get_item_data(obj_name)
                
                # Calculate impact metrics
                footprint = env_data['footprint']
                impact_pct = calculate_environmental_impact(footprint)
                decompose_time = format_decomposition_time(env_data['decompose_years'])
                rating, color = get_environmental_rating(footprint)
                
                items_analysis.append({
                    'name': obj_name,
                    'confidence': confidence,
                    'footprint': footprint,
                    'material': env_data['material'],
                    'decompose_time': decompose_time,
                    'recyclable': env_data['recyclable'],
                    'impact_pct': impact_pct,
                    'rating': rating,
                    'color': color,
                    'bbox': detail['bbox'],
                    'position': detail['position'],
                    'size_percentage': size_percentage,
                    'center_score': center_score,
                    'proximity_score': size_percentage * (1 + center_score)  # Combined score
                })
            
            # Create annotated frame
            annotated = frame.copy()
            
            # First pass: determine the nearest object
            nearest_item_name = None
            if items_analysis:
                items_sorted_temp = sorted(items_analysis, key=lambda x: x['proximity_score'], reverse=True)
                nearest_item_name = items_sorted_temp[0]['name']
            
            # Draw info for each item
            for item in items_analysis:
                x1, y1, x2, y2 = map(int, item['bbox'])
                color = item['color']
                
                # Highlight the nearest item with thicker border
                is_nearest = (item['name'] == nearest_item_name)
                thickness = 4 if is_nearest else 2
                
                # Draw bounding box
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)
                
                # Item name, confidence, and rating
                conf_pct = int(item.get('confidence', 0) * 100)
                label = f"{item['name']} ({conf_pct}%)"
                if is_nearest:
                    label += " [NEAREST]"
                cv2.putText(annotated, label, (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Carbon footprint (only show for nearest item to reduce clutter)
                if is_nearest:
                    if item['footprint'] >= 1000:
                        footprint_text = f"{item['footprint']/1000:.1f}t CO2e"
                    else:
                        footprint_text = f"{item['footprint']:.2f}kg CO2e"
                    
                    cv2.putText(annotated, footprint_text, (x1, y2 + 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Display summary overlay
            if items_analysis:
                # Sort by proximity (nearest/largest object first)
                items_sorted = sorted(items_analysis, key=lambda x: x['proximity_score'], reverse=True)
                primary_item = items_sorted[0]
                
                # Debug info
                print(f"  Nearest: {primary_item['name']} (size: {primary_item['size_percentage']:.1f}% of frame)", end='\r')
                
                # Create info panel
                panel_height = 200
                panel_width = 400
                panel = annotated[0:panel_height, 0:panel_width].copy()
                overlay = panel.copy()
                cv2.rectangle(overlay, (0, 0), (panel_width, panel_height), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.7, panel, 0.3, 0, panel)
                annotated[0:panel_height, 0:panel_width] = panel
                
                # Display info
                y_offset = 25
                line_height = 22
                
                # Item name
                cv2.putText(annotated, f"Item: {primary_item['name'].upper()}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_offset += line_height + 5
                
                # Carbon footprint
                if primary_item['footprint'] >= 1000:
                    footprint_display = f"{primary_item['footprint']/1000:.1f} tonnes CO2e"
                else:
                    footprint_display = f"{primary_item['footprint']:.2f} kg CO2e"
                
                cv2.putText(annotated, f"Carbon: {footprint_display}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
                y_offset += line_height
                
                # Environmental impact
                cv2.putText(annotated, f"Impact: {primary_item['impact_pct']:.1f}% of daily avg", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
                y_offset += line_height
                
                # Decomposition time
                cv2.putText(annotated, f"Decompose: {primary_item['decompose_time']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
                y_offset += line_height
                
                # Material
                cv2.putText(annotated, f"Material: {primary_item['material']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
                y_offset += line_height
                
                # Recyclable
                recycle_text = "YES" if primary_item['recyclable'] else "NO"
                recycle_color = (0, 255, 0) if primary_item['recyclable'] else (0, 0, 255)
                cv2.putText(annotated, f"Recyclable: {recycle_text}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, recycle_color, 2)
                y_offset += line_height
                
                # Rating
                cv2.putText(annotated, f"Rating: {primary_item['rating']}", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, primary_item['color'], 2)
                y_offset += line_height
                
                # Object proximity indicator
                cv2.putText(annotated, f"Distance: {primary_item['size_percentage']:.1f}% of frame", 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
                
                # Speech announcement
                current_time = time.time()
                
                # Check if item is stable (same item for multiple frames)
                if primary_item['name'] == current_item:
                    item_stable_count += 1
                else:
                    # New item detected
                    current_item = primary_item['name']
                    item_stable_count = 1
                
                # Announce if:
                # 1. Item is stable (seen for enough frames)
                # 2. Speech cooldown has passed
                # 3. It's a different item from last announcement OR enough time passed
                # 4. Not currently speaking
                should_announce = (
                    speech_enabled and 
                    not is_speaking and
                    item_stable_count >= stability_threshold and
                    (current_time - last_speech_time) >= speech_cooldown and
                    (primary_item['name'] != last_announced_item or 
                     (current_time - last_speech_time) >= speech_cooldown * 3)
                )
                
                if should_announce:
                    
                    # Create announcement
                    announcement = f"{primary_item['name']}. "
                    announcement += f"Carbon footprint: {footprint_display}. "
                    announcement += f"{primary_item['impact_pct']:.0f} percent of daily average. "
                    announcement += f"Decomposes in {primary_item['decompose_time']}. "
                    
                    if primary_item['recyclable']:
                        announcement += "Recyclable."
                    else:
                        announcement += "Not recyclable."
                    
                    print(f"\n {announcement}")
                    is_speaking = True
                    descriptor.speak(announcement, threaded=False)  # Blocking speech
                    is_speaking = False
                    last_speech_time = current_time
                    last_announced_item = primary_item['name']
                    # Keep item_stable_count high to prevent immediate re-announcement
            
            else:
                # No items detected or all items too small/distant
                cv2.putText(annotated, "Hold an object CLOSE to the camera", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(annotated, "(Objects must be >2% of frame)", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 200), 2)
            
            # Display frame
            cv2.imshow("Carbon Footprint Analyzer - 's'=speech, 'q'=quit", annotated)
        else:
            cv2.imshow("Carbon Footprint Analyzer - 's'=speech, 'q'=quit", frame)
        
        # Handle keyboard input
        key = cv2.waitKey(30) & 0xFF  # 30ms delay (~30 FPS)
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            speech_enabled = not speech_enabled
            status = "ENABLED" if speech_enabled else "DISABLED"
            print(f"\n🔊 Speech: {status}")
    
    cap.release()
    cv2.destroyAllWindows()


def main():
    """Main entry point."""
    import sys
    
    print("\n" + "="*60)
    print("ENVIRONMENTAL IMPACT ANALYZER")
    print("="*60)
    print("\nDiscover the carbon footprint of everyday items")
    print("="*60)
    
    # Parse camera index from command line
    camera_index = 0  # Default to laptop camera
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
            print(f"\n Using camera index: {camera_index}")
        except ValueError:
            print(f"\n  Invalid camera index. Using default (0)")
    
    print("\n Camera options:")
    print("   0 = Laptop webcam (default)")
    print("   1 = iPhone/External camera (Continuity Camera)")
    print("   2 = Other connected camera")
    print("\n   Usage: python carbon_footprint.py [camera_index]")
    print("   Example: python carbon_footprint.py 1")
    print("\n" + "="*60)
    
    try:
        run_carbon_footprint_analyzer(camera_index)
    except KeyboardInterrupt:
        print("\n\nAnalyzer stopped")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
