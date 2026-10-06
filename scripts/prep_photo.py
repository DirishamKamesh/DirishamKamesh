#!/usr/bin/env python3
"""
prep_photo.py
Preprocesses an image file for ASCII conversion.
- Resizes to target character dimensions
- Enhances contrast & grayscale
- Outputs data/processed_photo.png
"""

import sys
import os
from PIL import Image, ImageEnhance

def process_image(image_path, target_width=90):
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)

    img = Image.open(image_path)
    
    # Convert RGBA to RGB with dark background if transparent
    if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
        alpha = img.convert('RGBA').split()[-1]
        bg = Image.new("RGB", img.size, (13, 17, 23))
        bg.paste(img, mask=alpha)
        img = bg
    else:
        img = img.convert('RGB')

    # Convert to grayscale
    img = img.convert('L')

    # Enhance contrast for sharp ASCII rendering
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Calculate aspect ratio (terminal characters are roughly 1:2 width:height ratio)
    w, h = img.size
    aspect_ratio = h / w
    target_height = int(target_width * aspect_ratio * 0.55)

    img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    os.makedirs("data", exist_ok=True)
    out_path = "data/processed_photo.png"
    img_resized.save(out_path)
    print(f"Processed image saved to {os.path.abspath(out_path)} ({target_width}x{target_height})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <path_to_image> [target_width]")
        sys.exit(1)
    
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    process_image(sys.argv[1], width)
