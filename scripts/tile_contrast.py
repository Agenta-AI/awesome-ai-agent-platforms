"""Shared helper: decide whether a logo needs a dark tile background.

A logo that is white or transparent-light disappears on a light tile. We
composite the avatar over white and measure the fraction of meaningfully dark
pixels; below 2 percent, the logo is invisible on light and gets a dark tile.
Requires Pillow; without it, every tile stays light (safe fallback).
"""

def needs_dark_tile(path):
    try:
        from PIL import Image
        im = Image.open(path).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        gray = bg.convert("L")
        px = list(gray.getdata())
        dark = sum(1 for v in px if v < 200) / max(len(px), 1)
        return dark < 0.02
    except Exception:
        return False
