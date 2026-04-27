"""
Carbon Footprint Database
Material properties, decomposition times, and environmental impact data
"""

# Carbon footprint data in kg CO2e (CO2 equivalent)
CARBON_FOOTPRINT = {
    # Plastics
    'bottle': {'footprint': 0.15, 'material': 'plastic', 'decompose_years': 450, 'recyclable': True},
    'plastic bag': {'footprint': 0.01, 'material': 'plastic', 'decompose_years': 20, 'recyclable': True},
    'cup': {'footprint': 0.02, 'material': 'plastic/paper', 'decompose_years': 50, 'recyclable': True},
    'cell phone': {'footprint': 55.0, 'material': 'electronics', 'decompose_years': 1000, 'recyclable': True},
    'laptop': {'footprint': 350.0, 'material': 'electronics', 'decompose_years': 1000, 'recyclable': True},
    'keyboard': {'footprint': 15.0, 'material': 'plastic/electronics', 'decompose_years': 500, 'recyclable': True},
    'mouse': {'footprint': 5.0, 'material': 'plastic/electronics', 'decompose_years': 500, 'recyclable': True},
    
    # Stationery
    'scissors': {'footprint': 0.5, 'material': 'metal/plastic', 'decompose_years': 100, 'recyclable': True},
    'pencil': {'footprint': 0.02, 'material': 'wood/graphite', 'decompose_years': 50, 'recyclable': False},
    'pen': {'footprint': 0.05, 'material': 'plastic', 'decompose_years': 450, 'recyclable': False},
    'ruler': {'footprint': 0.1, 'material': 'plastic/wood', 'decompose_years': 100, 'recyclable': False},
    'eraser': {'footprint': 0.01, 'material': 'rubber', 'decompose_years': 50, 'recyclable': False},
    
    # Food items
    'apple': {'footprint': 0.08, 'material': 'organic', 'decompose_years': 0.08, 'recyclable': True},  # ~1 month
    'banana': {'footprint': 0.07, 'material': 'organic', 'decompose_years': 0.25, 'recyclable': True},  # ~3 months
    'orange': {'footprint': 0.05, 'material': 'organic', 'decompose_years': 0.15, 'recyclable': True},
    'sandwich': {'footprint': 0.8, 'material': 'organic', 'decompose_years': 0.08, 'recyclable': False},
    'hot dog': {'footprint': 1.5, 'material': 'organic', 'decompose_years': 0.08, 'recyclable': False},
    'pizza': {'footprint': 2.0, 'material': 'organic', 'decompose_years': 0.08, 'recyclable': False},
    
    # Containers
    'wine glass': {'footprint': 0.5, 'material': 'glass', 'decompose_years': 1000000, 'recyclable': True},
    'backpack': {'footprint': 25.0, 'material': 'fabric/plastic', 'decompose_years': 200, 'recyclable': False},
    'handbag': {'footprint': 20.0, 'material': 'fabric/leather', 'decompose_years': 50, 'recyclable': False},
    'suitcase': {'footprint': 40.0, 'material': 'plastic/fabric', 'decompose_years': 100, 'recyclable': False},
    'book': {'footprint': 2.5, 'material': 'paper', 'decompose_years': 2, 'recyclable': True},
    'vase': {'footprint': 1.0, 'material': 'ceramic/glass', 'decompose_years': 1000000, 'recyclable': False},
    
    # Furniture
    'chair': {'footprint': 100.0, 'material': 'wood/plastic', 'decompose_years': 1000, 'recyclable': False},
    'couch': {'footprint': 300.0, 'material': 'fabric/wood', 'decompose_years': 1000, 'recyclable': False},
    'dining table': {'footprint': 200.0, 'material': 'wood', 'decompose_years': 1000, 'recyclable': False},
    'potted plant': {'footprint': 5.0, 'material': 'organic/ceramic', 'decompose_years': 1000000, 'recyclable': False},
    
    # Vehicles (lifetime footprint)
    'car': {'footprint': 24000.0, 'material': 'metal/plastic', 'decompose_years': 200, 'recyclable': True},
    'bicycle': {'footprint': 96.0, 'material': 'metal', 'decompose_years': 100, 'recyclable': True},
    'motorcycle': {'footprint': 1000.0, 'material': 'metal/plastic', 'decompose_years': 150, 'recyclable': True},
    'truck': {'footprint': 35000.0, 'material': 'metal/plastic', 'decompose_years': 200, 'recyclable': True},
    'bus': {'footprint': 40000.0, 'material': 'metal/plastic', 'decompose_years': 200, 'recyclable': True},
    
    # Default for unknown items
    'default': {'footprint': 5.0, 'material': 'mixed', 'decompose_years': 100, 'recyclable': False}
}


def get_item_data(item_name):
    """
    Get carbon footprint data for an item.
    
    Args:
        item_name: Name of the detected object
        
    Returns:
        dict: Item environmental data
    """
    item_name = item_name.lower()
    return CARBON_FOOTPRINT.get(item_name, CARBON_FOOTPRINT['default'].copy())


def format_decomposition_time(years):
    """
    Format decomposition time in human-readable format.
    
    Args:
        years: Decomposition time in years
        
    Returns:
        str: Formatted time string
    """
    if years >= 1000000:
        return "Never (1M+ years)"
    elif years >= 1000:
        return f"{int(years):,} years"
    elif years >= 1:
        return f"{int(years)} years"
    elif years >= 0.08:  # About 1 month
        months = int(years * 12)
        return f"{months} month{'s' if months != 1 else ''}"
    else:
        days = int(years * 365)
        return f"{days} day{'s' if days != 1 else ''}"


def calculate_environmental_impact(footprint_kg):
    """
    Calculate environmental impact as a percentage relative to daily activities.
    
    Args:
        footprint_kg: Carbon footprint in kg CO2e
        
    Returns:
        float: Impact percentage
    """
    # Average person's daily carbon footprint: ~16 kg CO2e
    daily_avg = 16.0
    percentage = (footprint_kg / daily_avg) * 100
    return min(percentage, 999.0)  # Cap at 999%


def get_environmental_rating(footprint_kg):
    """
    Get environmental rating based on carbon footprint.
    
    Args:
        footprint_kg: Carbon footprint in kg CO2e
        
    Returns:
        tuple: (rating, color_bgr)
    """
    if footprint_kg < 1:
        return "Excellent", (0, 255, 0)  # Green
    elif footprint_kg < 10:
        return "Good", (0, 200, 0)  # Light green
    elif footprint_kg < 50:
        return "Moderate", (0, 165, 255)  # Orange
    elif footprint_kg < 200:
        return "High", (0, 100, 255)  # Dark orange
    else:
        return "Very High", (0, 0, 255)  # Red
