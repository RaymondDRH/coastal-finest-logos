#!/usr/bin/env python3
"""
Creates Coastal Finest logo download package with transparent versions.
Background removal: flood-fill from corners with color tolerance.
"""

import os
import shutil
import zipfile
from PIL import Image

SRC = "/home/raymond/raymond/coastal-finest/lovart-export"
OUT = "/home/raymond/raymond/coastal-finest/Coastal-Finest-Logos"
ZIP_PATH = "/home/raymond/raymond/coastal-finest/Coastal-Finest-Logos.zip"

# Color distance tolerance for background removal
TOLERANCE = 40


def color_dist(p1, p2):
    return sum((a - b) ** 2 for a, b in zip(p1[:3], p2[:3])) ** 0.5


def remove_background(img: Image.Image) -> Image.Image:
    """Flood-fill from all 4 corners to remove solid background color."""
    img = img.convert("RGBA")
    pixels = img.load()
    w, h = img.size

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    bg_color = pixels[0, 0][:3]

    visited = [[False] * h for _ in range(w)]
    queue = []

    for cx, cy in corners:
        c = pixels[cx, cy][:3]
        if color_dist(c, bg_color) <= TOLERANCE * 2:
            if not visited[cx][cy]:
                queue.append((cx, cy))
                visited[cx][cy] = True

    # BFS flood fill
    while queue:
        x, y = queue.pop()
        r, g, b, a = pixels[x, y]
        if color_dist((r, g, b), bg_color) <= TOLERANCE:
            pixels[x, y] = (r, g, b, 0)
            for nx, ny in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
                if 0 <= nx < w and 0 <= ny < h and not visited[nx][ny]:
                    visited[nx][ny] = True
                    queue.append((nx, ny))

    return img


def process():
    # Clean output dir
    if os.path.exists(OUT):
        shutil.rmtree(OUT)

    dirs = {
        "lettermark": os.path.join(OUT, "01-CFD-Lettermark"),
        "wordmark":   os.path.join(OUT, "02-Full-Wordmark"),
        "svg":        os.path.join(OUT, "03-SVG"),
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    # CFD Lettermark PNGs
    lettermark_files = {
        "Black-BG": "CFD Auto Detailing Logo Black Background.png",
        "White-BG": "CFD Auto Detailing Logo Fondo Blanco.png",
        "Gold-BG":  "CFD Auto Detailing Logo Fondo Dorado.png",
    }
    for label, fname in lettermark_files.items():
        src_path = os.path.join(SRC, fname)
        dst_path = os.path.join(dirs["lettermark"], f"CFD-Lettermark-{label}.png")
        shutil.copy2(src_path, dst_path)
        print(f"  Copied: {fname}")

    # Generate transparent lettermark from white bg (cleaner edges)
    print("  Removing background from CFD Lettermark (white)...")
    img = Image.open(os.path.join(SRC, "CFD Auto Detailing Logo Fondo Blanco.png"))
    transparent = remove_background(img)
    transparent.save(os.path.join(dirs["lettermark"], "CFD-Lettermark-Transparent.png"))
    print("  Saved: CFD-Lettermark-Transparent.png")

    # Full Wordmark PNGs
    wordmark_files = {
        "Black-BG": "Coastal Finest Detailing Logo Completo Fondo Negro.png",
        "White-BG": "Coastal Finest Detailing Logo Completo Fondo Blanco.png",
        "Gold-BG":  "Coastal Finest Detailing Logo Completo Fondo Dorado.png",
    }
    for label, fname in wordmark_files.items():
        src_path = os.path.join(SRC, fname)
        dst_path = os.path.join(dirs["wordmark"], f"Full-Wordmark-{label}.png")
        shutil.copy2(src_path, dst_path)
        print(f"  Copied: {fname}")

    # Generate transparent wordmark from white bg
    print("  Removing background from Full Wordmark (white)...")
    img = Image.open(os.path.join(SRC, "Coastal Finest Detailing Logo Completo Fondo Blanco.png"))
    transparent = remove_background(img)
    transparent.save(os.path.join(dirs["wordmark"], "Full-Wordmark-Transparent.png"))
    print("  Saved: Full-Wordmark-Transparent.png")

    # SVG files
    for i in range(1, 10):
        fname = f"SVG {i}.svg"
        src_path = os.path.join(SRC, fname)
        dst_path = os.path.join(dirs["svg"], f"SVG-{i}.svg")
        shutil.copy2(src_path, dst_path)
        print(f"  Copied: {fname}")

    # Create README
    readme = """# Coastal Finest Detailing — Logo Package

## Folder Structure

01-CFD-Lettermark/
  CFD-Lettermark-Black-BG.png    — CFD lettermark on black (#0A0A0A) background
  CFD-Lettermark-White-BG.png    — CFD lettermark on white background
  CFD-Lettermark-Gold-BG.png     — CFD lettermark on gold (#BB8F52) background
  CFD-Lettermark-Transparent.png — CFD lettermark with transparent background

02-Full-Wordmark/
  Full-Wordmark-Black-BG.png     — Full wordmark on black background
  Full-Wordmark-White-BG.png     — Full wordmark on white background
  Full-Wordmark-Gold-BG.png      — Full wordmark on gold background
  Full-Wordmark-Transparent.png  — Full wordmark with transparent background

03-SVG/
  SVG-1.svg through SVG-9.svg   — Original vector components from Lovart

## Brand Colors

- Black:  #0A0A0A
- Gold:   #BB8F52
- White:  #FFFFFF

## Usage

Use the Transparent version when placing logos over photos, colored backgrounds, or
any situation where you don't want a solid background behind the logo.

Use the colored backgrounds for social media, email headers, or print.
"""
    with open(os.path.join(OUT, "README.txt"), "w") as f:
        f.write(readme)

    # Create ZIP
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUT):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, os.path.dirname(OUT))
                zf.write(filepath, arcname)

    size_mb = os.path.getsize(ZIP_PATH) / 1024 / 1024
    print(f"\nZIP created: {ZIP_PATH} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    print("Building Coastal Finest logo package...")
    process()
    print("Done.")
