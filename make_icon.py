"""
Generates assets/icon.ico for Sleash Browser.
Run once: python make_icon.py
Requires: pip install Pillow
"""

import os
from PIL import Image, ImageDraw, ImageFont

# ── Colours (matches browser dark theme) ─────────────────────────────────────
BG_DARK   = (26,  27,  38,  255)   # #1a1b26  — outer ring
BG_MID    = (36,  37,  58,  255)   # #24253a  — inner fill
ACCENT    = (122, 162, 247, 255)   # #7aa2f7  — blue highlight
WHITE     = (255, 255, 255, 255)
CLEAR     = (0,   0,   0,   0)

# ── Font search order ─────────────────────────────────────────────────────────
FONT_PATHS = [
    "C:/Windows/Fonts/segoeuib.ttf",   # Segoe UI Bold  (Windows 10/11)
    "C:/Windows/Fonts/arialbd.ttf",    # Arial Bold
    "C:/Windows/Fonts/calibrib.ttf",   # Calibri Bold
    "C:/Windows/Fonts/verdanab.ttf",   # Verdana Bold
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_icon(size: int) -> Image.Image:
    img  = Image.new("RGBA", (size, size), CLEAR)
    draw = ImageDraw.Draw(img)

    pad    = max(1, size // 16)
    radius = size // 5

    # ── Outer rounded rectangle (dark ring) ───────────────────────────────────
    draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=radius,
        fill=BG_DARK,
    )

    # ── Accent border ring ────────────────────────────────────────────────────
    bw = max(1, size // 20)           # border width
    draw.rounded_rectangle(
        [bw, bw, size - bw - 1, size - bw - 1],
        radius=radius - bw,
        outline=ACCENT,
        width=bw,
        fill=BG_MID,
    )

    # ── Letter "S" centred ───────────────────────────────────────────────────
    font_size = int(size * 0.58)
    font = load_font(font_size)

    # Measure
    bbox = draw.textbbox((0, 0), "S", font=font)
    tw   = bbox[2] - bbox[0]
    th   = bbox[3] - bbox[1]
    tx   = (size - tw) // 2 - bbox[0]
    ty   = (size - th) // 2 - bbox[1] - max(1, size // 20)   # slight upward nudge

    # Subtle shadow
    if size >= 48:
        shadow_offset = max(1, size // 64)
        draw.text(
            (tx + shadow_offset, ty + shadow_offset),
            "S",
            font=font,
            fill=(0, 0, 0, 120),
        )

    # Main letter
    draw.text((tx, ty), "S", font=font, fill=WHITE)

    # ── Small blue dot bottom-right (accent detail) ───────────────────────────
    if size >= 48:
        dot_r = max(2, size // 14)
        dot_x = size - pad - dot_r * 2 - bw
        dot_y = size - pad - dot_r * 2 - bw
        draw.ellipse(
            [dot_x, dot_y, dot_x + dot_r * 2, dot_y + dot_r * 2],
            fill=ACCENT,
        )

    return img


def main():
    os.makedirs("assets", exist_ok=True)

    sizes   = [256, 128, 64, 48, 32, 16]
    images  = [draw_icon(s) for s in sizes]
    out     = "assets/icon.ico"

    images[0].save(
        out,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[1:],
    )

    # Also save a PNG preview
    images[0].save("assets/icon_preview.png")

    print(f"✓  Icon saved  →  {out}")
    print(f"✓  Preview     →  assets/icon_preview.png")
    print(f"   Sizes: {sizes}")


if __name__ == "__main__":
    main()
