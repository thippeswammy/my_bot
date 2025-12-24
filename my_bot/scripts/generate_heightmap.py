#!/usr/bin/env python3
import numpy as np
from PIL import Image
import os

def generate_heightmap(filename, width=513, height=513):
    # Set seed for deterministic noise
    np.random.seed(42)
    # Create a blank image
    img = np.zeros((height, width), dtype=np.uint8)

    # Simple gradient hill
    for y in range(height):
        for x in range(width):
            # Distance from center
            dx = x - width // 2
            dy = y - height // 2
            dist = np.sqrt(dx*dx + dy*dy)
            
            # Create a hill in the center
            val = max(0, 255 - dist * 0.8)
            
            # Add some roughness/noise
            noise = np.random.randint(0, 20)
            val = min(255, max(0, val + noise))
            
            img[y, x] = int(val)

    # Save
    image = Image.fromarray(img, mode='L')
    image.save(filename)
    print(f"Generated heightmap: {filename}")

if __name__ == "__main__":
    # Ensure directory exists
    script_dir = os.path.dirname(os.path.realpath(__file__))
    worlds_dir = os.path.join(script_dir, '../worlds')
    if not os.path.exists(worlds_dir):
        os.makedirs(worlds_dir)
    
    target_file = os.path.join(worlds_dir, 'heightmap.png')
    generate_heightmap(target_file)
