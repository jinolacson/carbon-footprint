# Real-Time Carbon Footprint Estimator

An AI-powered environmental impact analyzer that instantly displays the carbon footprint, decomposition time, and recyclability of items held up to your camera.

## Features

- ** Instant Carbon Footprint**: See CO2 emissions for any detected item
- ** Decomposition Time**: Learn how long items take to break down naturally
- ** Recyclability Status**: Know if items can be recycled
- ** Environmental Impact**: Compare to daily average carbon footprint (%)
- ** Visual Ratings**: Color-coded environmental ratings (Green=Excellent, Red=Very High)
- ** Voice Announcements**: Hear detailed environmental data for items
- **Real-time Detection**: Uses YOLO11 for accurate object recognition
- **Material Analysis**: Identifies material composition (plastic, metal, organic, etc.)

## How It Works

Hold any item up to your camera and instantly see:

**Example: Plastic Water Bottle**
- **Carbon Footprint**: 0.15 kg CO2e
- **Environmental Impact**: 0.9% of daily average
- **Decomposition Time**: 450 years
- **Material**: Plastic
- **Recyclable**: YES
- **Rating**: Good (Green box)

**Example: Laptop**
- **Carbon Footprint**: 350 kg CO2e (0.35 tonnes)
- **Environmental Impact**: 2,187% of daily average
- **Decomposition Time**: 1,000 years
- **Material**: Electronics
- **Recyclable**: YES
- **Rating**: Very High (Red box)

## Technical Stack

### AI & Computer Vision
- **YOLO11n** (`yolo11n.pt`) - Ultralytics' latest object detection model
  - Real-time inference for 80+ object classes
  - Lightweight variant optimized for speed
  - Auto-downloads on first run
- **OpenCV (cv2)** - Computer vision library
  - Camera capture and frame processing
  - Image manipulation and annotation
  - Multi-camera support (laptop, phone, external)

### Core Technologies
- **Python 3.x** - Primary programming language
- **Ultralytics** - YOLO model framework and inference engine
- **NumPy** - Array operations for image processing
- **Threading** - Non-blocking speech synthesis

### Speech & Accessibility
- **macOS `say` command** - Native text-to-speech engine
  - Blocking and non-blocking modes
  - 20-second timeout protection
  - Message truncation for reliability

### Detection Algorithms
- **Proximity Detection** - Custom algorithm to prioritize nearest objects
  - Bounding box area calculation (size percentage)
  - Center-weighted scoring system
  - Filters objects <2% of frame
- **Confidence Filtering** - Rejects detections below 50% certainty
- **Stability Tracking** - Requires 8 consecutive frames before announcement
- **Smart Cooldowns** - 10-second speech intervals, 30-second same-item delay

### Data Management
- **Custom Environmental Database** - 40+ items with verified metrics
  - Carbon footprint (kg CO2e)
  - Material composition
  - Decomposition timeframes
  - Recyclability status
- **Dynamic Rating System** - Color-coded impact levels (5 tiers)

### Architecture
```
carbon_footprint.py  → Main application (camera loop, UI, speech)
app.py              → Object detection engine (YOLO wrapper)
carbon_data.py      → Environmental database & calculations
list_cameras.py     → Camera discovery utility
```

## Environmental Ratings

Items are rated based on their carbon footprint:
-  **Excellent** (< 1 kg CO2e): Organic items, small products
-  **Good** (1-10 kg CO2e): Most recyclables, small electronics
-  **Moderate** (10-50 kg CO2e): Furniture, larger items
-  **High** (50-200 kg CO2e): Large furniture, appliances
-  **Very High** (> 200 kg CO2e): Vehicles, large electronics

## Camera Setup

### Using Your Phone Camera

You have several options to use your phone camera instead of laptop webcam:

#### **Option 1: macOS Continuity Camera (Easiest for iPhone users)**
1. Ensure iPhone and Mac are signed into the same iCloud account
2. Enable Bluetooth and Wi-Fi on both devices
3. Your iPhone will automatically appear as a camera option
4. Find your camera index:
   ```bash
   python list_cameras.py
   ```
5. Run with phone camera:
   ```bash
   python carbon_footprint.py 1
   ```

#### **Option 2: IP Webcam (Android/iPhone)**
1. Install IP Webcam app on your phone
2. Start the server in the app
3. Note the IP address (e.g., `http://192.168.1.100:8080`)
4. Modify `carbon_footprint.py` to use IP stream:
   ```python
   cap = cv2.VideoCapture('http://192.168.1.100:8080/video')
   ```

#### **Option 3: USB Connection (Android)**
1. Enable USB debugging on Android
2. Connect via USB cable
3. Use DroidCam or similar app
4. Camera will appear as index 1 or 2

### Finding Available Cameras

Run the camera detection script:
```bash
python list_cameras.py
```

This will show all available cameras and their indices.

### Running with Specific Camera

```bash
# Default (laptop camera)
python carbon_footprint.py

# Phone/external camera (usually index 1)
python carbon_footprint.py 1

# Other camera
python carbon_footprint.py 2
```

It provides context:
> "The room is set up for a birthday party with decorations and a cake on the table, ready for celebration."

**With Memory Layer:**

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify YOLO model:**
   The app will automatically download the YOLO11 model on first run.

## Usage

### Carbon Footprint Analyzer (Main App)
```bash
python carbon_footprint.py
```

**How to use:**
1. Hold any item up to your camera
2. Wait for detection (green/orange/red box appears)
3. View environmental data in the info panel
4. Hear audio announcement with full details

**Controls:**
- `s` - Toggle speech announcements on/off
- `q` - Quit

**What you'll see:**
- **Visual**: Color-coded bounding boxes by environmental rating
- **Info Panel**: Carbon footprint, impact %, decomposition time, material, recyclability
- **Audio**: Complete environmental analysis spoken aloud

### Supported Items

The analyzer recognizes 30+ common items:
- **Electronics**: Phone, laptop, keyboard, mouse
- **Food**: Fruits, sandwiches, pizza
- **Containers**: Bottles, cups, bags, backpacks
- **Furniture**: Chairs, tables, couches
- **Vehicles**: Cars, bicycles, motorcycles
- And more!

## Examples

### Example 1: Plastic Bottle
Hold a water bottle to the camera:
```
Item: BOTTLE
Carbon: 0.15 kg CO2e
Impact: 0.9% of daily avg
Decompose: 450 years
Material: plastic
Recyclable: YES
Rating: Good
```

### Example 2: Smartphone
Hold your phone to the camera:
```
Item: CELL PHONE
Carbon: 55.00 kg CO2e
Impact: 343.8% of daily avg
Decompose: 1,000 years
Material: electronics
Recyclable: YES
Rating: High
```

### Example 3: Apple
Hold an apple to the camera:
```
Item: APPLE
Carbon: 0.08 kg CO2e
Impact: 0.5% of daily avg
Decompose: 1 month
Material: organic
Recyclable: YES
Rating: Excellent
```

### Example 4: Car
Point camera at a vehicle:
```
Item: CAR
Carbon: 24.0 tonnes CO2e
Impact: 999% of daily avg
Decompose: 200 years
Material: metal/plastic
Recyclable: YES
Rating: Very High
```

### Example 3: Street Scene
**Objects Detected:** car, person, traffic light, crosswalk  
**Context Description:** "This is a busy street intersection. There are vehicles and pedestrians present. A traffic light is visible - use caution when crossing."

## Architecture

1. **Object Detection Layer** (YOLO11)
   - Real-time object recognition from camera feed
   - Accurate bounding box localization
   - Supports 30+ common items

2. **Environmental Data Layer** (carbon_data.py)
   - Carbon footprint database (kg CO2e for each item)
   - Decomposition time estimates (days to 1M+ years)
   - Material composition data
   - Recyclability information

3. **Impact Analysis Layer**
   - Calculates environmental impact percentage
   - Compares to average daily carbon footprint (16 kg CO2e)
   - Generates environmental ratings (Excellent to Very High)
   - Color-codes items by impact level

4. **Presentation Layer**
   - Real-time visual overlay with detailed info
   - Color-coded bounding boxes
   - Text-to-speech announcements
   - Item stability detection (prevents repeated announcements)

## How Carbon Footprint is Calculated

**Carbon Footprint (CO2e):**
- Measured in kg or tonnes of CO2 equivalent
- Based on lifecycle analysis (production, use, disposal)
- Examples:
  - Plastic bottle: 0.15 kg (manufacturing)
  - Laptop: 350 kg (full production chain)
  - Car: 24,000 kg (lifetime emissions)

**Environmental Impact %:**
```
Impact % = (Item Carbon Footprint / Daily Average) × 100
Daily Average = 16 kg CO2e per person
```

Example: Laptop (350 kg) = 2,187% of daily average

**Decomposition Time:**
- Organic: Days to months
- Paper: 2-6 months
- Plastic: 20-450 years
- Electronics: 500-1,000 years
- Glass/Ceramics: 1,000,000+ years (essentially never)

## Adding New Items

Edit `carbon_data.py` to add more items:

```python
CARBON_FOOTPRINT = {
    'your_item': {
        'footprint': 10.0,  # kg CO2e
        'material': 'plastic',
        'decompose_years': 100,
        'recyclable': True
    }
}
```

## Configuration

Edit settings in `carbon_footprint.py`:

```python
speech_cooldown = 4  # Seconds between announcements
stability_threshold = 5  # Frames before announcing item
frame_skip = 2  # Process every Nth frame
```

Edit `carbon_data.py` for environmental data:

```python
daily_avg = 16.0  # Average daily carbon footprint (kg CO2e)
```

## Troubleshooting

**"Cannot access camera"**
- Check camera permissions in System Preferences > Security & Privacy
- Make sure no other app is using the camera

**"Error getting AI description"**
- Verify Ollama is running: `ollama serve`
- Check if the model is installed: `ollama list`
- Test Ollama: `ollama run llama3.2-vision`

**Text-to-speech not working**
- Install pyttsx3: `pip install pyttsx3`
**Text-to-speech not working**
- Check system volume
- Test with: `say "test"` in Terminal (macOS)
- Speech should announce after item is stable for 5 frames

**Item not detected**
- Hold item closer to camera
- Ensure good lighting
- Item must be in YOLO's training dataset
- Add custom items to `carbon_data.py`

**Wrong carbon footprint data**
- Database uses average/estimated values
- Edit `carbon_data.py` to update specific items
- Values are for reference only

## API Usage

Use the carbon footprint analyzer programmatically:

```python
from carbon_data import get_item_data, calculate_environmental_impact

# Get data for an item
data = get_item_data('bottle')
print(f"Carbon: {data['footprint']} kg CO2e")
print(f"Decomposes in: {data['decompose_years']} years")
print(f"Recyclable: {data['recyclable']}")

# Calculate impact
impact = calculate_environmental_impact(data['footprint'])
print(f"Impact: {impact:.1f}% of daily average")
```

## Data Sources

Carbon footprint estimates based on:
- Lifecycle Assessment (LCA) studies
- EPA environmental databases
- Academic research on product carbon footprints
- Material decomposition research

**Note**: Values are estimates for educational purposes. Actual carbon footprints vary based on production methods, location, and usage patterns.

## Future Enhancements

- [ ] Expanded item database (500+ items)
- [ ] Real-time API integration for up-to-date carbon data
- [ ] Barcode scanning for precise product data
- [ ] Comparison mode (compare 2 items side-by-side)
- [ ] Daily/weekly carbon tracking
- [ ] Alternative suggestions (lower-impact alternatives)
- [ ] Regional carbon grid intensity
- [ ] Water footprint analysis
- [ ] Eco-score integration

## Educational Impact

This tool helps users:
- **Understand** the hidden environmental cost of everyday items
- **Make informed** purchasing decisions
- **Recognize** the importance of recycling
- **Appreciate** the longevity of waste in landfills
- **Compare** carbon footprints across products

## License

MIT License - Free to use for educational and environmental awareness purposes.

