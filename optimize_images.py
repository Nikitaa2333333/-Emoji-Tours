import os
from PIL import Image

def optimize_images(directory):
    print(f"Starting aggressive optimization in {directory}...")
    for filename in os.listdir(directory):
        ext = filename.lower()
        if ext.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            file_path = os.path.join(directory, filename)
            try:
                with Image.open(file_path) as img:
                    # Preserve transparency (RGBA/LA)
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        # Keep as is to preserve alpha
                        pass
                    elif img.mode == "P":
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")
                    
                    width, height = img.size
                    
                    # Target name
                    base_name = os.path.splitext(filename)[0]
                    webp_name = f"{base_name}.webp"
                    webp_path = os.path.join(directory, webp_name)
                    
                    # Aggressive resizing: max 1200px for hero images, smaller for others
                    # But for now, let's keep it 1200px max for all to be safe but fast
                    max_width = 1200
                    if width > max_width:
                        new_height = int(height * (max_width / width))
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                        print(f"  Resized {filename} to {max_width}px width")

                    # Save as WebP with 70% quality (aggressive but usually looks fine)
                    img.save(webp_path, "WEBP", quality=70, method=6) # method 6 is slowest/best compression
                    
                    # If the original was not webp, we could delete it, but let's keep it for now
                    # unless it's a temp file.
                    print(f"  Optimized {filename} -> {webp_name}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # Optimize root images
    optimize_images(".")
    
    # Optimize images directory
    if os.path.exists("images"):
        optimize_images("images")
        
    print("Aggressive image optimization complete.")
