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

try:
    from tile_contrast import needs_dark_tile
except ImportError:
    def needs_dark_tile(path):
        return False

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

# Design tokens (validated reference dataviz palette).
# Color is an accent on each category header, in fixed slot order; text stays
# in ink tokens; containers are recessive surfaces with hairline borders.
PAGE = "#f9f9f7"        # page plane
SURFACE = "#fcfcfb"     # card surface
INK = "#0b0b0b"         # primary ink
INK2 = "#52514e"        # secondary ink
MUTED = "#898781"       # muted labels
HAIRLINE = "#e1e0d9"    # hairline border on the page plane
FONT = 'system-ui, -apple-system, &quot;Segoe UI&quot;, sans-serif'
ACCENT = {              # categorical slots 1-5, fixed order
    "AI coworkers and teammates": "#2a78d6",
    "Agent builders and frameworks": "#1baf7a",
    "Workflow automation platforms": "#eda100",
    "Browser agents": "#008300",
    "Coding agents": "#4a3aa7",
}

# Layout on an 8px grid
W = 1440
MARGIN = 40             # page margin
CARD_PAD = 24           # card inner padding
TILE_W = 128
TILE_H = 104            # 48 logo + gap + up to 2 label lines
LOGO = 48
CARD_TITLE_H = 48
CARD_GAP = 24
HEADER_H = 104

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def wrap_label(name, max_chars=15):
    """Split a long name onto two lines at the space nearest the middle."""
    if len(name) <= max_chars or " " not in name:
        return [name]
    spaces = [i for i, ch in enumerate(name) if ch == " "]
    mid = min(spaces, key=lambda i: abs(i - len(name) // 2))
    return [name[:mid], name[mid + 1:]]

svg = []
body = []
defs = (
    '<defs><clipPath id="logoclip">'
    f'<rect x="0" y="0" width="{LOGO}" height="{LOGO}" rx="9"/>'
    "</clipPath></defs>"
)

y = HEADER_H
inner_w = W - 2 * MARGIN
cols = (inner_w - 2 * CARD_PAD) // TILE_W

for cat in CATEGORIES:
    items = entries.get(cat, [])
    if not items:
        continue
    rows = -(-len(items) // cols)
    card_h = CARD_TITLE_H + rows * TILE_H + CARD_PAD
    # Card: recessive surface, hairline border
    body.append(
        f'<rect x="{MARGIN}" y="{y}" width="{inner_w}" height="{card_h}" rx="12" '
        f'fill="{SURFACE}" stroke="{HAIRLINE}" stroke-width="1"/>'
    )
    # Category accent chip + title in primary ink, count in muted ink
    ax = MARGIN + CARD_PAD
    body.append(
        f'<rect x="{ax}" y="{y + 22}" width="12" height="12" rx="4" fill="{ACCENT[cat]}"/>'
    )
    body.append(
        f'<text x="{ax + 22}" y="{y + 33}" font-family="{FONT}" font-size="17" '
        f'font-weight="600" fill="{INK}">{esc(cat)}'
        f'<tspan font-weight="400" font-size="13" fill="{MUTED}" dx="8">{len(items)}</tspan></text>'
    )
    for i, (name, org) in enumerate(items):
        r, c = divmod(i, cols)
        tx = MARGIN + CARD_PAD + c * TILE_W + (TILE_W - LOGO) // 2
        ty = y + CARD_TITLE_H + r * TILE_H + 8
        b64 = avatar_b64(org)
        tile = [f'<g transform="translate({tx},{ty})">']
        if b64:
            tile_bg = "#16181d" if needs_dark_tile(CACHE / f"{org}.png") else "#ffffff"
            tile.append(
                f'<rect x="0" y="0" width="{LOGO}" height="{LOGO}" rx="9" fill="{tile_bg}"/>'
            )
            tile.append(
                f'<image x="0" y="0" width="{LOGO}" height="{LOGO}" '
                f'clip-path="url(#logoclip)" href="data:image/png;base64,{b64}"/>'
            )
            tile.append(
                f'<rect x="0.5" y="0.5" width="{LOGO - 1}" height="{LOGO - 1}" rx="9" '
                f'fill="none" stroke="rgba(11,11,11,0.10)" stroke-width="1"/>'
            )
        else:
            tile.append(
                f'<rect x="0" y="0" width="{LOGO}" height="{LOGO}" rx="9" '
                f'fill="{PAGE}" stroke="{HAIRLINE}"/>'
            )
        tile.append("</g>")
        body.extend(tile)
        cx = tx + LOGO // 2
        for li, line in enumerate(wrap_label(name)):
            body.append(
                f'<text x="{cx}" y="{ty + LOGO + 17 + li * 14}" text-anchor="middle" '
                f'font-family="{FONT}" font-size="12" fill="{INK2}">{esc(line)}</text>'
            )
    y += card_h + CARD_GAP

H = y + MARGIN - CARD_GAP + 24
svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="Market map of the AI agent platform landscape">'
)
svg.append(defs)
svg.append(f'<rect width="{W}" height="{H}" fill="{PAGE}"/>')
total = sum(len(v) for v in entries.values())
svg.append(
    f'<text x="{MARGIN}" y="46" font-family="{FONT}" font-size="26" '
    f'font-weight="700" fill="{INK}">The AI agent platform landscape</text>'
)
svg.append(
    f'<text x="{MARGIN}" y="72" font-family="{FONT}" font-size="14" fill="{INK2}">'
    f'{total} open-source and source-available projects, grouped by main use · '
    f'github.com/Agenta-AI/awesome-ai-agent-platforms</text>'
)
svg.extend(body)
svg.append("</svg>")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(svg))
print(f"OK {OUT} ({total} tiles, {H}px tall)")
