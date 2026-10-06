#!/usr/bin/env python3
"""
make_info_card.py
Generates a neofetch-style terminal info card SVG for Dirisham Kamesh.

Features:
- Dark terminal window chrome (titlebar with red/yellow/green control dots)
- Terminal prompt & line-by-line animated CSS reveal
- Responsive & clean monospace layout
- Exact skill alignment (C, Java, JS, HTML/CSS, React, Node, Express, PostgreSQL, Supabase, Firebase, Git, GitHub)
"""

import os
import xml.etree.ElementTree as ET

def generate_info_card_svg():
    width = 440
    height = 370

    # Information key-value pairs matching user's exact background
    items = [
        ("$ whoami", "Dirisham Kamesh"),
        ("$ role", "CSE Student · Developer"),
        ("$ languages", "C [Strong] · Java · JavaScript"),
        ("$ frontend", "HTML5 · CSS3 · React.js · UI/UX · Canvas"),
        ("$ backend", "Node.js · Express.js · REST APIs"),
        ("$ database", "PostgreSQL · Supabase · Firebase"),
        ("$ tools", "Git · GitHub · Netlify · Render"),
        ("$ learning", "DSA · Java · Advanced CSS · MERN"),
        ("$ target", "Full-Stack Internship"),
    ]

    # Calculate line heights and positions
    top_bar_height = 36
    line_start_y = 65
    line_spacing = 31

    # Generate keyframe animations and lines
    styles = """
        @keyframes lineReveal {
            from {
                opacity: 0;
                transform: translateX(-10px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0; }
        }
        .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5px; rx: 10px; }
        .topbar { fill: #161b22; rx: 10px; }
        .topbar-divider { stroke: #30363d; stroke-width: 1px; }
        .dot-red { fill: #ff5f56; }
        .dot-yellow { fill: #ffbd2e; }
        .dot-green { fill: #27c93f; }
        .title { fill: #8b949e; font-family: 'Fira Code', Consolas, 'Courier New', monospace; font-size: 13px; font-weight: 600; }
        
        .info-group {
            opacity: 0;
            animation: lineReveal 0.4s ease-out forwards;
        }
        
        .cmd { fill: #7ee787; font-family: 'Fira Code', Consolas, 'Courier New', monospace; font-size: 13px; font-weight: 700; }
        .val { fill: #c9d1d9; font-family: 'Fira Code', Consolas, 'Courier New', monospace; font-size: 12.5px; font-weight: 400; }
        .accent { fill: #58a6ff; font-weight: 600; }
        .highlight { fill: #d2a8ff; }
        .cursor { fill: #7ee787; animation: blink 1s infinite; }
    """

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <style>
{styles}
    </style>
  </defs>

  <!-- Window Container -->
  <rect class="bg" x="1" y="1" width="{width - 2}" height="{height - 2}" />
  
  <!-- Window Header -->
  <rect class="topbar" x="1" y="1" width="{width - 2}" height="{top_bar_height}" />
  <line class="topbar-divider" x1="1" y1="{top_bar_height}" x2="{width - 1}" y2="{top_bar_height}" />
  
  <!-- Window Controls -->
  <circle class="dot-red" cx="18" cy="18" r="6" />
  <circle class="dot-yellow" cx="38" cy="18" r="6" />
  <circle class="dot-green" cx="58" cy="18" r="6" />
  <text class="title" x="{width / 2}" y="22" text-anchor="middle">dirisham@developer-terminal ~ neofetch</text>

  <!-- Content lines -->
'''

    for idx, (cmd, val) in enumerate(items):
        y = line_start_y + idx * line_spacing
        delay_ms = 100 + idx * 180

        # Special styling for values
        val_class = "val"
        if "whoami" in cmd:
            val_markup = f'<tspan class="accent">{val}</tspan>'
        elif "role" in cmd:
            val_markup = f'<tspan class="highlight">{val}</tspan>'
        else:
            val_markup = val

        svg += f'''  <g class="info-group" style="animation-delay: {delay_ms}ms;">
    <text x="20" y="{y}">
      <tspan class="cmd">{cmd}</tspan>
      <tspan class="{val_class}" x="135">{val_markup}</tspan>
    </text>
  </g>
'''

    # Blinking prompt line at bottom
    cursor_y = line_start_y + len(items) * line_spacing
    cursor_delay = 100 + len(items) * 180
    svg += f'''  <g class="info-group" style="animation-delay: {cursor_delay}ms;">
    <text x="20" y="{cursor_y}">
      <tspan class="cmd">$</tspan>
      <tspan class="cursor" x="35">▌</tspan>
    </text>
  </g>
</svg>
'''

    out_path = "info-card.svg"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved info card to {os.path.abspath(out_path)}")

if __name__ == "__main__":
    generate_info_card_svg()
