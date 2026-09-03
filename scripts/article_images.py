#!/usr/bin/env python3
"""Generate article images for the dev.to post and the site.

Emits two SVGs from the same design tokens as the market map:
  media/article-cover.svg   1600x680  (dev.to cover / banner)
  media/categories.svg      1200x720  (in-article taxonomy diagram)

CI renders both to PNG with rsvg-convert. Pure stdlib.

Usage: python3 scripts/article_images.py
"""
import base64
import sys
import tempfile
import urllib.request
from pathlib import Path

OUT = Path("media")
OUT.mkdir(parents=True, exist_ok=True)
CACHE = Path(tempfile.gettempdir()) / "market-map-avatars"
CACHE.mkdir(parents=True, exist_ok=True)

# Design tokens (validated dataviz palette).
PAGE = "#f9f9f7"
SURFACE = "#ffffff"
INK = "#16181d"
INK2 = "#52514e"
MUTED = "#8a8880"
HAIR = "#e6e5df"
FONT = "Helvetica, Arial, sans-serif"
CATS = [
    ("AI coworkers", 12, "#2a78d6", "Persistent agents you delegate real work to."),
    ("Agent builders", 16, "#1baf7a", "Frameworks and visual tools to build agents."),
    ("Workflow automation", 14, "#eda100", "Repeatable processes with AI steps."),
    ("Browser agents", 2, "#008300", "Agents that operate a web browser."),
    ("Coding agents", 5, "#4a3aa7", "Agents that read, edit, and ship code."),
]
TOTAL = sum(c[1] for c in CATS)
# Representative orgs across categories for the cover logo strip.
COVER_ORGS = [
    "danny-avila", "langchain-ai", "langgenius", "n8n-io",
    "browser-use", "All-Hands-AI", "crewAIInc", "Skyvern-AI",
]


def avatar(org):
    p = CACHE / f"{org}.png"
    if not p.exists():
        url = f"https://github.com/{org}.png?size=128"
        req = urllib.request.Request(url, headers={"User-Agent": "article-img"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                p.write_bytes(r.read())
        except Exception as ex:
            print(f"WARN {org}: {ex}", file=sys.stderr)
            return None, False
    raw = p.read_bytes()
    mime = "image/jpeg" if raw[:3] == b"\xff\xd8\xff" else "image/png"
    # dark tile if the logo is near-white/transparent
    dark = False
    try:
        from PIL import Image
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        bg.alpha_composite(im)
        g = bg.convert("L")
        px = list(g.getdata())
        dark = (sum(1 for v in px if v < 200) / max(len(px), 1)) < 0.02
    except Exception:
        pass
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}", dark


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- Cover 1600x680 ----------
W, H = 1600, 680
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
s.append('<defs><clipPath id="lc"><rect x="0" y="0" width="84" height="84" rx="18"/></clipPath></defs>')
s.append(f'<rect width="{W}" height="{H}" fill="{PAGE}"/>')
seg = W / 5
for i, (_, _, color, _) in enumerate(CATS):
    s.append(f'<rect x="{i*seg:.0f}" y="0" width="{seg:.0f}" height="10" fill="{color}"/>')
# Left column
s.append(f'<text x="72" y="118" font-family="{FONT}" font-size="22" font-weight="bold" letter-spacing="2" fill="{MUTED}">OPEN SOURCE  ·  {TOTAL} PROJECTS</text>')
s.append(f'<text x="70" y="214" font-family="{FONT}" font-size="76" font-weight="bold" fill="{INK}">The AI agent</text>')
s.append(f'<text x="70" y="298" font-family="{FONT}" font-size="76" font-weight="bold" fill="{INK}">platform landscape</text>')
s.append(f'<text x="72" y="360" font-family="{FONT}" font-size="30" fill="{INK2}">AI coworkers, agent builders, workflow automation,</text>')
s.append(f'<text x="72" y="400" font-family="{FONT}" font-size="30" fill="{INK2}">browser agents, and coding agents, with licenses.</text>')
# category dots row
x = 74
for name, _, color, _ in CATS:
    s.append(f'<circle cx="{x+9}" cy="470" r="9" fill="{color}"/>')
    s.append(f'<text x="{x+28}" y="478" font-family="{FONT}" font-size="24" fill="{INK}">{esc(name)}</text>')
    x += 28 + len(name) * 13 + 34
s.append(f'<text x="72" y="612" font-family="{FONT}" font-size="26" font-weight="bold" fill="{INK2}">aiagentplatforms.dev</text>')
# Right logo panel: 2 cols x 4 rows of 84px tiles
gx, gy, step = 1150, 150, 106
for i, org in enumerate(COVER_ORGS):
    r, c = divmod(i, 2)
    tx, ty = gx + c * (step + 20), gy + r * step
    b64, dark = avatar(org)
    if not b64:
        continue
    bg = "#16181d" if dark else "#ffffff"
    s.append(f'<g transform="translate({tx},{ty})">')
    s.append(f'<rect x="0" y="0" width="84" height="84" rx="18" fill="{bg}"/>')
    s.append(f'<image x="0" y="0" width="84" height="84" clip-path="url(#lc)" href="{b64}"/>')
    s.append(f'<rect x="0.5" y="0.5" width="83" height="83" rx="18" fill="none" stroke="rgba(16,24,40,0.10)"/>')
    s.append('</g>')
s.append("</svg>")
(OUT / "article-cover.svg").write_text("\n".join(s))
print("OK media/article-cover.svg")

# ---------- Categories diagram 1200x760 ----------
W2, H2 = 1200, 760
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}">']
s.append(f'<rect width="{W2}" height="{H2}" fill="{PAGE}"/>')
s.append(f'<text x="56" y="80" font-family="{FONT}" font-size="42" font-weight="bold" fill="{INK}">Five categories, {TOTAL} platforms</text>')
s.append(f'<text x="56" y="120" font-family="{FONT}" font-size="24" fill="{INK2}">Grouped by the job each tool does.</text>')
cy = 168
row_h = 108
for name, count, color, blurb in CATS:
    s.append(f'<rect x="56" y="{cy}" width="{W2-112}" height="{row_h-16}" rx="16" fill="{SURFACE}" stroke="{HAIR}"/>')
    s.append(f'<rect x="56" y="{cy}" width="8" height="{row_h-16}" rx="4" fill="{color}"/>')
    s.append(f'<text x="92" y="{cy+42}" font-family="{FONT}" font-size="30" font-weight="bold" fill="{INK}">{esc(name)}</text>')
    s.append(f'<text x="92" y="{cy+76}" font-family="{FONT}" font-size="23" fill="{INK2}">{esc(blurb)}</text>')
    s.append(f'<text x="{W2-92}" y="{cy+52}" text-anchor="end" font-family="{FONT}" font-size="40" font-weight="bold" fill="{color}">{count}</text>')
    cy += row_h
(OUT / "categories.svg").write_text("\n".join(s))
print("OK media/categories.svg")
# trigger: render article images
