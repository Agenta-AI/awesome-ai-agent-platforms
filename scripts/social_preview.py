#!/usr/bin/env python3
"""Generate the social-preview banner SVG (1280x640) from the README.

Same data source and design tokens as the market map. CI renders it to PNG
with rsvg-convert (GitHub social previews must be raster images).

Usage: python3 scripts/social_preview.py README.md media/social-preview.svg
"""
import base64
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

README = Path(sys.argv[1])
OUT = Path(sys.argv[2])
CACHE = Path(tempfile.gettempdir()) / "market-map-avatars"
CACHE.mkdir(parents=True, exist_ok=True)

CATEGORIES = [
    ("AI coworkers and teammates", "AI coworkers", "#2a78d6"),
    ("Agent builders and frameworks", "Agent builders", "#1baf7a"),
    ("Workflow automation platforms", "Automation", "#eda100"),
    ("Browser agents", "Browser agents", "#008300"),
    ("Coding agents", "Coding agents", "#4a3aa7"),
]
FULL = [c[0] for c in CATEGORIES]

text = README.read_text()
entries = {}
current = None
for line in text.splitlines():
    m = re.match(r"^## (.+)$", line)
    if m:
        current = m.group(1).strip() if m.group(1).strip() in FULL else None
        if current:
            entries[current] = []
        continue
    if current:
        e = re.match(r"^- \[([^\]]+)\]\(https://github\.com/([^/\)]+)", line)
        if e:
            entries[current].append(e.group(2))

def avatar_b64(org):
    p = CACHE / f"{org}.png"
    if not p.exists():
        url = f"https://github.com/{org}.png?size=96"
        req = urllib.request.Request(url, headers={"User-Agent": "banner-builder"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                p.write_bytes(r.read())
        except Exception:
            return None
    return base64.b64encode(p.read_bytes()).decode()

total = sum(len(v) for v in entries.values())

# Pick 26 logos proportionally across categories, keeping list order.
PICK = 26
picked = []
for cat in FULL:
    orgs = entries.get(cat, [])
    share = max(1, round(len(orgs) * PICK / max(total, 1)))
    picked.extend(orgs[:share])
picked = picked[:PICK]

PAGE = "#f9f9f7"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
FONT = "DejaVu Sans, Verdana, sans-serif"

W, H = 1280, 640
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    '<defs><clipPath id="lc"><rect x="0" y="0" width="64" height="64" rx="12"/></clipPath></defs>',
    f'<rect width="{W}" height="{H}" fill="{PAGE}"/>',
]
# Top accent strip: five category colors
seg = W / 5
for i, (_, _, color) in enumerate(CATEGORIES):
    svg.append(f'<rect x="{i * seg:.0f}" y="0" width="{seg:.0f}" height="8" fill="{color}"/>')

svg.append(
    f'<text x="64" y="150" font-family="{FONT}" font-size="58" font-weight="bold" '
    f'fill="{INK}">Awesome AI Agent Platforms</text>'
)
svg.append(
    f'<text x="64" y="205" font-family="{FONT}" font-size="26" fill="{INK2}">'
    f'{total} open-source AI coworkers, agent builders, automation platforms,</text>'
)
svg.append(
    f'<text x="64" y="240" font-family="{FONT}" font-size="26" fill="{INK2}">'
    f'browser agents, and coding agents, with licenses.</text>'
)

# Category chips row
x = 64
cy = 296
for full, short, color in CATEGORIES:
    n = len(entries.get(full, []))
    label = f"{short} {n}"
    w = 34 + len(label) * 11
    svg.append(f'<circle cx="{x + 14}" cy="{cy}" r="7" fill="{color}"/>')
    svg.append(
        f'<text x="{x + 30}" y="{cy + 6}" font-family="{FONT}" font-size="19" '
        f'fill="{INK}">{label}</text>'
    )
    x += w + 26

# Logo grid: 2 rows x 13, 64px logos
GX, GY, STEP = 64, 356, 89
for i, org in enumerate(picked):
    r, c = divmod(i, 13)
    lx, ly = GX + c * STEP, GY + r * STEP
    b64 = avatar_b64(org)
    if not b64:
        continue
    svg.append(
        f'<g transform="translate({lx},{ly})">'
        f'<image x="0" y="0" width="64" height="64" clip-path="url(#lc)" '
        f'href="data:image/png;base64,{b64}"/>'
        f'<rect x="0.5" y="0.5" width="63" height="63" rx="12" fill="none" '
        f'stroke="rgba(11,11,11,0.10)"/></g>'
    )
rest = total - len(picked)
svg.append(
    f'<text x="{GX}" y="{GY + 2 * STEP + 20}" font-family="{FONT}" font-size="20" '
    f'fill="{MUTED}">and {rest} more · aiagentplatforms.dev · '
    f'github.com/Agenta-AI/awesome-ai-agent-platforms</text>'
)
svg.append("</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg))
print(f"OK {OUT} ({len(picked)} logos shown of {total})")
