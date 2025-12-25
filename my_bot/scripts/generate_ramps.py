import numpy as np
from PIL import Image
import os

def generate_ramps():
    # Image size (must be 2^n + 1)
    width = 129
    height = 129
    
    # Create an array of zeros
    data = np.zeros((height, width), dtype=np.uint8)
    
    # Create linear gradients for ramps
    # Ramp 1: Upward slope
    for y in range(height):
        for x in range(width):
            # Normalized x from 0 to 1
            nx = x / width
            
            # Simple ramp: height increases with x
            # Scale to 0-255 range
            val = int(nx * 255)
            data[y, x] = val

    # Create image
    img = Image.fromarray(data)
    
    # Ensure directory exists
    save_dir = os.path.expanduser('~/my_robot/src/my_bot/worlds')
    os.makedirs(save_dir, exist_ok=True)
    
    # Save as PNG
    img_path = os.path.join(save_dir, 'ramps.png')
    img.save(img_path)
    print(f"Ramps heightmap saved to: {img_path}")

if __name__ == "__main__":
    generate_ramps()
