"""
List Available Cameras
Helper script to find camera indices
"""

import cv2


def list_cameras(max_cameras=5):
    """Test camera indices to find available cameras."""
    print("\n" + "="*60)
    print("AVAILABLE CAMERAS")
    print("="*60)
    
    available = []
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"\n Camera {i} - AVAILABLE")
            print(f"   Resolution: {width}x{height}")
            print(f"   FPS: {fps}")
            
            available.append(i)
            cap.release()
        else:
            print(f"\n Camera {i} - Not available")
    
    print("\n" + "="*60)
    
    if available:
        print(f"\n Found {len(available)} camera(s): {available}")
        print("\n To use a specific camera:")
        print(f"   python carbon_footprint.py {available[0]}  # Laptop camera")
        if len(available) > 1:
            print(f"   python carbon_footprint.py {available[1]}  # Phone/External camera")
    else:
        print("\n  No cameras found!")
    
    print("\n" + "="*60)
    return available


if __name__ == "__main__":
    import sys
    
    max_check = 5
    if len(sys.argv) > 1:
        try:
            max_check = int(sys.argv[1])
        except:
            pass
    
    list_cameras(max_check)
