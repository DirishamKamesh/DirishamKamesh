#!/usr/bin/env python3
"""
render_heatmap_svg.py
Generates an animated contribution heatmap SVG from contributions.json.

Animations (pure CSS, no JavaScript):
  1. Diagonal wave reveal — cells appear with staggered delay
  2. Shimmer sweep — subtle light sweep across the grid
  3. Pulse/morph — high-level cells subtly breathe with glow
  4. Settles into stable readable state
"""

import json
import os
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(ROOT_DIR, "data", "contributions.json")
OUTPUT_PATH = os.path.join(ROOT_DIR, "contrib-heatmap.svg")

# Layout constants
CELL_SIZE = 11
CELL_GAP = 3
CELL_RADIUS = 2
COLS = 53
ROWS = 7
LEFT_LABEL_WIDTH = 32
TOP_LABEL_HEIGHT = 20
PADDING = 16

GRID_WIDTH = COLS * (CELL_SIZE + CELL_GAP) - CELL_GAP
GRID_HEIGHT = ROWS * (CELL_SIZE + CELL_GAP) - CELL_GAP
SVG_WIDTH = LEFT_LABEL_WIDTH + GRID_WIDTH + PADDING * 2
SVG_HEIGHT = TOP_LABEL_HEIGHT + GRID_HEIGHT + PADDING * 2 + 50

# Color palette
COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = {1: "Mon", 3: "Wed", 5: "Fri"}


CSS_STYLES = """
/* Base */
.heatmap-bg { fill: #0d1117; }
.heatmap-border { fill: none; stroke: #30363d; stroke-width: 1; }
.label { fill: #8b949e; font-family: -apple-system, 'Segoe UI', monospace; font-size: 10px; }
.stat-text { fill: #8b949e; font-family: -apple-system, 'Segoe UI', monospace; font-size: 11px; }
.stat-num { fill: #e6edf3; font-family: -apple-system, 'Segoe UI', monospace; font-size: 11px; font-weight: 600; }

/* 1. Diagonal wave reveal */
.cell {
  opacity: 0;
  transform-origin: center;
  animation: cellReveal 0.5s ease-out forwards;
}
@keyframes cellReveal {
  0%   { opacity: 0; transform: scale(0.4); }
  60%  { opacity: 1; transform: scale(1.05); }
  100% { opacity: 1; transform: scale(1); }
}

/* 2. Shimmer sweep */
.shimmer-bar {
  opacity: 0;
  animation: shimmerSweep 2.8s ease-in-out 3.2s 2;
}
@keyframes shimmerSweep {
  0%   { opacity: 0;    transform: translateX(-150%); }
  15%  { opacity: 0.13; }
  50%  { opacity: 0.09; }
  85%  { opacity: 0.13; }
  100% { opacity: 0;    transform: translateX(900%); }
}

/* 3. Pulse for level 3 cells */
.cell-l3 {
  animation: cellReveal 0.5s ease-out forwards,
             pulseSubtle 4.5s ease-in-out 4.5s 5;
}
@keyframes pulseSubtle {
  0%, 100% { opacity: 1;    filter: brightness(1); }
  50%      { opacity: 0.88; filter: brightness(1.1); }
}

/* 4. Glow pulse for level 4 cells */
.cell-l4 {
  animation: cellReveal 0.5s ease-out forwards,
             pulseGlow 3.8s ease-in-out 4.2s 6;
}
@keyframes pulseGlow {
  0%, 100% { opacity: 1;   filter: brightness(1)    drop-shadow(0 0 0px #39d353); }
  50%      { opacity: 0.9; filter: brightness(1.18)  drop-shadow(0 0 3px rgba(57,211,83,0.4)); }
}

/* Legend cells - no animation */
.legend-cell { opacity: 1; }
"""


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_grid(data):
    """Build a 53x7 grid from the weeks data."""
    grid = [[None for _ in range(ROWS)] for _ in range(COLS)]
    for week in data["weeks"]:
        wi = week["week_index"]
        if wi >= COLS:
            continue
        for day in week["days"]:
            dow = day["weekday"]
            if dow < ROWS:
                grid[wi][dow] = day
    return grid


def get_month_labels(data):
    """Determine where month labels should appear above the grid."""
    labels = []
    seen_months = set()
    for week in data["weeks"]:
        wi = week["week_index"]
        if wi >= COLS:
            continue
        for day in week["days"]:
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            month_key = (dt.year, dt.month)
            if month_key not in seen_months:
                seen_months.add(month_key)
                labels.append((wi, MONTH_NAMES[dt.month - 1]))
    return labels


def generate_svg(data):
    grid = build_grid(data)
    month_labels = get_month_labels(data)
    total = data["total_contributions"]
    current_streak = data["current_streak"]
    longest_streak = data["longest_streak"]

    gx = PADDING + LEFT_LABEL_WIDTH
    gy = PADDING + TOP_LABEL_HEIGHT

    parts = []

    # ── SVG root ────────────────────────────────────────────────────────
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" '
        f'width="{SVG_WIDTH}" height="{SVG_HEIGHT}">'
    )

    # ── Defs: styles + gradient ─────────────────────────────────────────
    parts.append("<defs>")
    parts.append(f"<style>{CSS_STYLES}</style>")
    parts.append(
        '<linearGradient id="shimmerGrad" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#ffffff" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#ffffff" stop-opacity="0.08"/>'
        '<stop offset="1" stop-color="#ffffff" stop-opacity="0"/>'
        '</linearGradient>'
    )
    parts.append("</defs>")

    # ── Background ──────────────────────────────────────────────────────
    parts.append(f'<rect class="heatmap-bg" x="0" y="0" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="8"/>')
    parts.append(f'<rect class="heatmap-border" x="0.5" y="0.5" width="{SVG_WIDTH-1}" height="{SVG_HEIGHT-1}" rx="8"/>')

    # ── Month labels ────────────────────────────────────────────────────
    for wi, name in month_labels:
        x = gx + wi * (CELL_SIZE + CELL_GAP)
        y = PADDING + 12
        parts.append(f'<text class="label" x="{x}" y="{y}">{name}</text>')

    # ── Day labels ──────────────────────────────────────────────────────
    for dow, name in DAY_NAMES.items():
        y = gy + dow * (CELL_SIZE + CELL_GAP) + CELL_SIZE - 1
        parts.append(f'<text class="label" x="{PADDING}" y="{y}" text-anchor="start">{name}</text>')

    # ── Contribution cells ──────────────────────────────────────────────
    for wi in range(COLS):
        for dow in range(ROWS):
            day = grid[wi][dow]
            if day is None:
                continue

            level = day["level"]
            color = COLORS.get(level, COLORS[0])
            x = gx + wi * (CELL_SIZE + CELL_GAP)
            y = gy + dow * (CELL_SIZE + CELL_GAP)

            # Diagonal delay for wave reveal
            delay_s = (wi + dow) * 0.018

            if level >= 4:
                css_class = "cell cell-l4"
                # Two animation delays: reveal + pulse
                style = f"animation-delay: {delay_s:.3f}s, {delay_s:.3f}s"
            elif level == 3:
                css_class = "cell cell-l3"
                style = f"animation-delay: {delay_s:.3f}s, {delay_s:.3f}s"
            else:
                css_class = "cell"
                style = f"animation-delay: {delay_s:.3f}s"

            parts.append(
                f'<rect class="{css_class}" x="{x}" y="{y}" '
                f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{CELL_RADIUS}" '
                f'fill="{color}" style="{style}"/>'
            )

    # ── Shimmer overlay ─────────────────────────────────────────────────
    parts.append(
        f'<rect class="shimmer-bar" x="{gx}" y="{gy}" '
        f'width="50" height="{GRID_HEIGHT}" rx="4" '
        f'fill="url(#shimmerGrad)"/>'
    )

    # ── Legend ──────────────────────────────────────────────────────────
    legend_y = gy + GRID_HEIGHT + 18
    legend_x = gx + GRID_WIDTH - 140

    parts.append(f'<text class="label" x="{legend_x}" y="{legend_y + 9}">Less</text>')
    for i in range(5):
        lx = legend_x + 30 + i * (CELL_SIZE + 3)
        parts.append(
            f'<rect class="legend-cell" x="{lx}" y="{legend_y}" '
            f'width="{CELL_SIZE}" height="{CELL_SIZE}" rx="{CELL_RADIUS}" '
            f'fill="{COLORS[i]}"/>'
        )
    parts.append(
        f'<text class="label" x="{legend_x + 30 + 5 * (CELL_SIZE + 3) + 2}" '
        f'y="{legend_y + 9}">More</text>'
    )

    # ── Stats ───────────────────────────────────────────────────────────
    stats_y = legend_y + 24
    parts.append(
        f'<text class="stat-text" x="{gx}" y="{stats_y}">'
        f'<tspan class="stat-num">{total}</tspan> contributions in the last year'
        f'  ·  Current streak: <tspan class="stat-num">{current_streak}</tspan> day{"s" if current_streak != 1 else ""}'
        f'  ·  Longest streak: <tspan class="stat-num">{longest_streak}</tspan> days'
        f'</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    print("Loading contribution data...")
    data = load_data()

    print("Generating heatmap SVG...")
    svg_content = generate_svg(data)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Saved heatmap to {OUTPUT_PATH}")
    print(f"  SVG dimensions: {SVG_WIDTH} x {SVG_HEIGHT}")


if __name__ == "__main__":
    main()
