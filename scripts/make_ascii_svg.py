#!/usr/bin/env python3
"""
make_ascii_svg.py
Converts processed photo or generates a futuristic developer terminal ASCII artwork SVG (avi-ascii.svg).

Features:
- Pure CSS keyframe animated row-by-row matrix/terminal typing reveal
- Responsive SVG output (matches info-card style & proportions)
- Green/Cyan terminal color palette (#39d353, #58a6ff)
- Custom ASCII character density mapping
"""

import os
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ASCII_CHARS = " .:-=+*#%@"

def text_to_ascii_grid(image_path):
    img = Image.open(image_path).convert('L')
    w, h = img.size
    if hasattr(img, 'get_flattened_data'):
        pixels = list(img.get_flattened_data())
    else:
        pixels = list(img.getdata())
    
    grid = []
    for y in range(h):
        row = []
        for x in range(w):
            val = pixels[y * w + x]
            char_idx = int((val / 255) * (len(ASCII_CHARS) - 1))
            row.append(ASCII_CHARS[char_idx])
        grid.append("".join(row))
    return grid

def generate_default_developer_ascii():
    """Generates a stylish Cyberpunk Terminal Developer ASCII portrait grid."""
    art = [
        "               .----------------.               ",
        "              |  dirisham@dev  |               ",
        "               '----------------'               ",
        "                       ||                       ",
        "            .──────────────────────.            ",
        "           /   ____________________   \\          ",
        "          |   |  >_ C              |   |         ",
        "          |   |  >_ Java           |   |         ",
        "          |   |  >_ JavaScript     |   |         ",
        "          |   |  >_ React          |   |         ",
        "          |   |  >_ Node.js        |   |         ",
        "          |   |____________________|   |         ",
        "           \\                          /          ",
        "            '────────────────────────'           ",
        "                     ||      ||                  ",
        "                .────┴───────┴────.              ",
        "               /                   \\             ",
        "              /   [ FULL-STACK ]    \\            ",
        "             /     BUILD & DEBUG     \\           ",
        "            /________________________\\          ",
        "           [==========================]          ",
        "           |  C  | JAVA | JS | REACT  |          ",
        "           '--------------------------'          "
    ]
    return art

def render_ascii_svg(ascii_lines, out_path="avi-ascii.svg"):
    width = 380
    height = 370
    
    max_cols = max(len(line) for line in ascii_lines) if ascii_lines else 40
    num_rows = len(ascii_lines)
    
    # Calculate font size & line height to fit bounds nicely
    font_size = min(12, int(width * 1.6 / max_cols)) if max_cols > 0 else 10
    line_height = int(font_size * 1.25)
    
    start_y = int((height - (num_rows * line_height)) / 2) + font_size

    css_rules = """
        @keyframes rowReveal {
            from {
                opacity: 0;
                transform: translateY(4px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes neonGlow {
            0%, 100% { fill: #39d353; filter: drop-shadow(0 0 2px rgba(57, 211, 83, 0.4)); }
            50% { fill: #58a6ff; filter: drop-shadow(0 0 4px rgba(88, 166, 255, 0.6)); }
        }
        .bg { fill: #0d1117; stroke: #30363d; stroke-width: 1.5px; rx: 10px; }
        .topbar { fill: #161b22; rx: 10px; }
        .topbar-divider { stroke: #30363d; stroke-width: 1px; }
        .dot-red { fill: #ff5f56; }
        .dot-yellow { fill: #ffbd2e; }
        .dot-green { fill: #27c93f; }
        .title { fill: #8b949e; font-family: 'Fira Code', Consolas, monospace; font-size: 13px; font-weight: 600; }

        .ascii-row {
            font-family: 'Fira Code', Consolas, 'Courier New', monospace;
            font-size: """ + str(font_size) + """px;
            fill: #39d353;
            white-space: pre;
            opacity: 0;
            animation: rowReveal 0.3s ease-out forwards;
        }
        .ascii-highlight {
            fill: #58a6ff;
            font-weight: bold;
        }
        .ascii-tag {
            fill: #7ee787;
        }
    """

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="{height}">
  <defs>
    <style>
{css_rules}
    </style>
  </defs>

  <!-- Container -->
  <rect class="bg" x="1" y="1" width="{width - 2}" height="{height - 2}" />
  
  <!-- Header -->
  <rect class="topbar" x="1" y="1" width="{width - 2}" height="36" />
  <line class="topbar-divider" x1="1" y1="36" x2="{width - 1}" y2="36" />
  <circle class="dot-red" cx="18" cy="18" r="6" />
  <circle class="dot-yellow" cx="38" cy="18" r="6" />
  <circle class="dot-green" cx="58" cy="18" r="6" />
  <text class="title" x="{width / 2}" y="22" text-anchor="middle">dirisham@ascii-portrait ~ terminal</text>

  <!-- ASCII Content -->
'''

    for idx, line in enumerate(ascii_lines):
        y = start_y + idx * line_height
        delay_ms = 80 + idx * 45
        
        # Escape XML entities
        escaped_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        svg += f'  <text class="ascii-row" x="{width / 2}" y="{y}" text-anchor="middle" style="animation-delay: {delay_ms}ms;">{escaped_line}</text>\n'

    svg += '</svg>\n'

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Saved ASCII SVG to {os.path.abspath(out_path)}")

def main():
    processed_photo = "data/processed_photo.png"
    if HAS_PIL and os.path.exists(processed_photo):
        print(f"Loading processed photo from {processed_photo}...")
        ascii_grid = text_to_ascii_grid(processed_photo)
    else:
        print("Generating default terminal ASCII portrait...")
        ascii_grid = generate_default_developer_ascii()

    render_ascii_svg(ascii_grid, "avi-ascii.svg")

if __name__ == "__main__":
    main()
