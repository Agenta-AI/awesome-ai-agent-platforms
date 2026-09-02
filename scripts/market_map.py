#!/usr/bin/env python3
"""Generate the market-map SVG for awesome-ai-agent-platforms from the README.

Pure stdlib: parses the README for entries, downloads each GitHub org avatar,
embeds it base64 into a category-grouped SVG.

Usage: python3 scripts/market_map.py README.md media/market-map.svg
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
    "AI coworkers and teammates",
    "Agent builders and frameworks",
    "Workflow automation platforms",
    "Browser agents",
    "Coding agents",
]

text = README.read_text()
entries = {}  # category -> list of (name, org)
current = None
for line in text.splitlines():
    m = re.match(r"^## (.+)$", line)
    if m:
        current = m.group(1).strip() if m.group(1).strip() in CATEGORIES else None
        if current:
            entries[current] = []
        continue
    if current:
        e = re.match(r"^- \[([^\]]+)\]\(https://github\.com/([^/\)]+)", line)
        if e:
            entries[current].append((e.group(1), e.group(2)))

def avatar_b64(org):
    p = CACHE / f"{org}.png"
    if not p.exists():
        url = f"https://github.com/{org}.png?size=96"
        req = urllib.request.Request(url, headers={"User-Agent": "market-map-builder"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                p.write_bytes(r.read())
        except Exception as ex:
            print(f"WARN no avatar for {org}: {ex}", file=sys.stderr)
            return None
    return base64.b64encode(p.read_bytes()).decode()

# Layout constants
TILE = 108          # tile width
TILE_H = 96         # tile height (icon + label)
ICON = 52
PAD = 18            # inner padding of category box
GAP_Y = 26          # gap between boxes
HEADER = 74         # svg header area
BOX_TITLE = 40
W = 1440
COLS_WIDE = 12      # tiles per row in a full-width box

FILL = {
    "AI coworkers and teammates": "#EEF4FF",
    "Agent builders and frameworks": "#F0FBF4",
    "Workflow automation platforms": "#FFF7EC",
    "Browser agents": "#F7F0FF",
    "Coding agents": "#FDF0F3",
}
STROKE = {
    "AI coworkers and teammates": "#3B6FD4",
    "Agent builders and frameworks": "#2F9E5F",
    "Workflow automation platforms": "#D48A2F",
    "Browser agents": "#8A5FD4",
    "Coding agents": "#D4527A",
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

svg = []
y = HEADER
body = []
for cat in CATEGORIES:
    items = entries.get(cat, [])
    if not items:
        continue
    cols = min(COLS_WIDE, max(1, (W - 2 * PAD) // TILE))
    rows = -(-len(items) // cols)
    box_h = BOX_TITLE + rows * TILE_H + PAD
    body.append(
        f'<rect x="20" y="{y}" width="{W-40}" height="{box_h}" rx="14" '
        f'fill="{FILL[cat]}" stroke="{STROKE[cat]}" stroke-width="1.5"/>'
    )
    body.append(
        f'<text x="44" y="{y+28}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="19" font-weight="bold" fill="{STROKE[cat]}">{esc(cat)}'
        f'  <tspan font-weight="normal" font-size="14" fill="#667">({len(items)})</tspan></text>'
    )
    for i, (name, org) in enumerate(items):
        r, c = divmod(i, cols)
        cx = 44 + c * TILE + TILE // 2
        ty = y + BOX_TITLE + r * TILE_H
        b64 = avatar_b64(org)
        if b64:
            body.append(
                f'<image x="{cx-ICON//2}" y="{ty+6}" width="{ICON}" height="{ICON}" '
                f'href="data:image/png;base64,{b64}" clip-path="inset(0 round 10px)"/>'
            )
        else:
            body.append(
                f'<rect x="{cx-ICON//2}" y="{ty+6}" width="{ICON}" height="{ICON}" rx="10" fill="#ccd"/>'
            )
        label = name if len(name) <= 16 else name[:15] + "…"
        body.append(
            f'<text x="{cx}" y="{ty+6+ICON+18}" text-anchor="middle" '
            f'font-family="Helvetica, Arial, sans-serif" font-size="12" fill="#333">{esc(label)}</text>'
        )
    y += box_h + GAP_Y

H = y + 10
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
svg.append(f'<rect width="{W}" height="{H}" fill="white"/>')
svg.append(
    f'<text x="44" y="40" font-family="Helvetica, Arial, sans-serif" font-size="28" '
    f'font-weight="bold" fill="#111">The AI Agent Platform Landscape</text>'
)
total = sum(len(v) for v in entries.values())
svg.append(
    f'<text x="44" y="62" font-family="Helvetica, Arial, sans-serif" font-size="14" fill="#667">'
    f'{total} open-source and source-available projects · awesome-ai-agent-platforms</text>'
)
svg.extend(body)
svg.append("</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg))
print(f"OK {OUT} ({total} tiles, {H}px tall)")
