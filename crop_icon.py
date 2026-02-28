import sys
import os

try:
    from PIL import Image, ImageDraw, ImageOps
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw, ImageOps

def make_circle_icon(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    
    # convert to grayscale and invert to find bbox of the black logo
    gray = img.convert("L")
    inv = ImageOps.invert(gray)
    bbox = inv.getbbox()
    
    if bbox:
        # crop to bounding box
        img = img.crop(bbox)
        
    # Make it a square based on the max dimension
    size = max(img.width, img.height)
    square_img = Image.new("RGBA", (size, size), (255, 255, 255, 0)) # transparent background
    
    # paste the cropped image in the center of the square
    square_img.paste(img, ((size - img.width) // 2, (size - img.height) // 2))
    
    # Generate a circular mask
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((2, 2, size-2, size-2), fill=255)
    
    # Apply mask
    result = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    result.paste(square_img, (0, 0), mask)
    
    # Ensure transparent background for anything white inside/outside if needed?
    # No, the user wants the content (which includes the white background inside the circle).
    # Since we pasted onto transparent with a circle mask, it's a circle.
    # The original image might have a slightly off-white background, but pasting it within the circle mask 
    # will cleanly cut it out as a circle.
    
    # Let's clean up any solid white background making it transparent around the circle? No the circle IS the icon.
    
    # Let's save a couple of sizes
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 512x512
    result_512 = result.resize((512, 512), Image.Resampling.LANCZOS)
    result_512.save(output_path, "PNG")
    
    print(f"Icon successfully generated at {output_path}")

if __name__ == "__main__":
    make_circle_icon(sys.argv[1], sys.argv[2])
