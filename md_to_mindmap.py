#!/usr/bin/env python3
"""
Markdown to Mind Map Converter
Style: XMind-like, no boxes, bezier curves, colored branches, text only.
"""

import re
import math
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_markdown(content: str) -> List[Tuple[int, str]]:
    """Parse markdown into (level, text) list."""
    lines = content.strip().split('\n')
    nodes: List[Tuple[int, str]] = []

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # Match heading: ## text
        m = re.match(r'^(#{1,})\s+(.+)$', line)
        if m:
            level = len(m.group(1)) - 1
            text = m.group(2).strip()
        else:
            # Match list item: (spaces)- text
            m2 = re.match(r'^(\s*)-\s+(.+)$', line)
            if m2:
                indent = len(m2.group(1))
                text = m2.group(2).strip()
                level = indent // 2 + 2
            else:
                continue

        # Strip markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'\*(.+?)\*',     r'\1', text)
        text = re.sub(r'^#{1,}\s*',     '',    text)
        text = text.strip()

        if text:
            nodes.append((level, text))

    if nodes:
        min_level = min(n[0] for n in nodes)
        nodes = [(lvl - min_level, txt) for lvl, txt in nodes]

    return nodes


def build_tree(nodes: List[Tuple[int, str]]) -> Dict:
    if not nodes:
        return {}
    root = {'text': nodes[0][1], 'level': 0, 'children': []}
    stack = [root]
    for level, text in nodes[1:]:
        node = {'text': text, 'level': level, 'children': []}
        while len(stack) > 1 and stack[-1]['level'] >= level:
            stack.pop()
        stack[-1]['children'].append(node)
        stack.append(node)
    return root


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

# 10 distinct branch colors
BRANCH_COLORS = [
    '#2E75B6',  # blue
    '#70AD47',  # green
    '#ED7D31',  # orange
    '#C00000',  # dark red
    '#7030A0',  # purple
    '#00B0F0',  # cyan
    '#FF0066',  # pink
    '#92D050',  # lime
    '#FFC000',  # amber
    '#00B050',  # dark green
]

ROOT_COLOR = '#1F1F1F'


class MindMapRenderer:
    """
    Two-pass layout:
      Pass 1 (_measure): compute text size and subtree height for each node.
      Pass 2 (_layout):  assign (x, y) coordinates top-down.

    Coordinate system:
      node['x']  = left edge of text
      node['y']  = top edge of text bounding box
      node['w']  = text width
      node['h']  = text height (may be multi-line)
      node['cy'] = vertical center  = y + h/2
      node['rx'] = right edge       = x + w
      node['sh'] = subtree height (space allocated, including gaps)
    """

    # Font sizes per level (0=root, 1=L1, 2=L2, 3+=leaf)
    FONT_SIZES = {0: 20, 1: 16, 2: 14, 3: 13, 4: 12}

    # Horizontal gap between parent right-edge and child left-edge
    COL_GAP = 45

    # Minimum vertical gap between adjacent leaf rows
    ROW_GAP = 10

    # Max characters per line before wrapping
    MAX_CHARS = 28

    def __init__(self):
        self._fonts: Dict[int, ImageFont.FreeTypeFont] = {}
        self._load_fonts()

    def _load_fonts(self):
        candidates = [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        for path in candidates:
            try:
                for lvl, sz in self.FONT_SIZES.items():
                    self._fonts[lvl] = ImageFont.truetype(path, sz)
                print(f"[Font] {path}")
                return
            except OSError:
                continue
        print("[Font] WARNING: fallback default font, Chinese may not render.")
        f = ImageFont.load_default()
        for lvl in self.FONT_SIZES:
            self._fonts[lvl] = f

    def _font(self, level: int) -> ImageFont.FreeTypeFont:
        key = min(level, max(self._fonts.keys()))
        return self._fonts.get(key, self._fonts[max(self._fonts.keys())])

    def _measure_text(self, text: str, level: int) -> Tuple[int, int]:
        """Return (width, height) of a single line."""
        bb = self._font(level).getbbox(text)
        return bb[2] - bb[0], bb[3] - bb[1]

    def _wrap_text(self, text: str, level: int) -> List[str]:
        """Wrap text to MAX_CHARS per line, respecting Chinese characters."""
        if len(text) <= self.MAX_CHARS:
            return [text]
        lines, cur = [], ""
        for ch in text:
            cur += ch
            if len(cur) >= self.MAX_CHARS:
                lines.append(cur)
                cur = ""
        if cur:
            lines.append(cur)
        return lines

    # ------------------------------------------------------------------
    # Pass 1: measure
    # ------------------------------------------------------------------

    def _measure(self, node: Dict):
        level = node['level']
        lines = self._wrap_text(node['text'], level)
        node['lines'] = lines

        # Single-line height reference
        _, lh = self._measure_text("国Ag", level)
        node['lh'] = lh  # line height

        # Node text box dimensions
        tw = max(self._measure_text(l, level)[0] for l in lines)
        th = lh * len(lines) + 3 * (len(lines) - 1)  # 3px inter-line gap
        node['w'] = tw
        node['h'] = th

        # Recurse
        for child in node['children']:
            self._measure(child)

        # Subtree height: space this node + all descendants need vertically
        if not node['children']:
            node['sh'] = th + self.ROW_GAP
        else:
            children_total = sum(c['sh'] for c in node['children'])
            node['sh'] = max(children_total, th + self.ROW_GAP)

    # ------------------------------------------------------------------
    # Pass 2: layout
    # ------------------------------------------------------------------

    def _layout(self, node: Dict, x: float, cy: float,
                color: str = ROOT_COLOR, branch_idx: int = 0):
        """
        x  = left edge of this node's text
        cy = vertical center of this node's text block
        """
        level = node['level']

        # Color assignment
        if level == 0:
            node['color'] = ROOT_COLOR
        elif level == 1:
            node['color'] = BRANCH_COLORS[branch_idx % len(BRANCH_COLORS)]
        else:
            node['color'] = color

        node['x']  = x
        node['cy'] = cy
        node['y']  = cy - node['h'] / 2.0
        node['rx'] = x + node['w']

        if not node['children']:
            return

        # Children start at x + this node's width + gap
        child_x = x + node['w'] + self.COL_GAP

        # Distribute children vertically, centered on cy
        total_sh = sum(c['sh'] for c in node['children'])
        cur_y = cy - total_sh / 2.0

        for i, child in enumerate(node['children']):
            child_cy = cur_y + child['sh'] / 2.0
            self._layout(child, child_x, child_cy, node['color'], i)
            cur_y += child['sh']

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _all_nodes(self, node: Dict) -> List[Dict]:
        result = [node]
        for c in node['children']:
            result.extend(self._all_nodes(c))
        return result

    def _bezier_point(self, t: float,
                      p0: Tuple[float, float],
                      p1: Tuple[float, float],
                      p2: Tuple[float, float],
                      p3: Tuple[float, float]) -> Tuple[float, float]:
        """Cubic bezier point at parameter t."""
        mt = 1 - t
        x = mt**3*p0[0] + 3*mt**2*t*p1[0] + 3*mt*t**2*p2[0] + t**3*p3[0]
        y = mt**3*p0[1] + 3*mt**2*t*p1[1] + 3*mt*t**2*p2[1] + t**3*p3[1]
        return x, y

    def _draw_bezier(self, draw: ImageDraw.ImageDraw,
                     x0: float, y0: float,
                     x1: float, y1: float,
                     color: str, width: int = 1, steps: int = 40):
        """Draw a cubic bezier from (x0,y0) to (x1,y1) with horizontal tangents."""
        # Control points: horizontal tangent at both ends
        cx = (x0 + x1) / 2.0
        p0 = (x0, y0)
        p1 = (cx, y0)
        p2 = (cx, y1)
        p3 = (x1, y1)

        pts = [self._bezier_point(i / steps, p0, p1, p2, p3)
               for i in range(steps + 1)]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=color, width=width)

    def _draw_connections(self, draw: ImageDraw.ImageDraw, node: Dict):
        """Draw bezier curves from this node to each child."""
        # Origin: right-center of parent text
        ox = node['rx']
        oy = node['cy']

        for child in node['children']:
            # Destination: left-center of child text
            dx = child['x']
            dy = child['cy']
            color = child['color']

            # Line width: thicker for higher-level connections
            lw = max(1, 3 - child['level'])

            self._draw_bezier(draw, ox, oy, dx, dy, color, width=lw)
            self._draw_connections(draw, child)

    def _draw_text_nodes(self, draw: ImageDraw.ImageDraw, nodes: List[Dict]):
        """Render all node texts."""
        for node in nodes:
            level = node['level']
            font  = self._font(level)
            color = node['color']
            tx    = node['x']
            ty    = node['y']
            lh    = node['lh']

            for line in node['lines']:
                draw.text((tx, ty), line, fill=color, font=font)
                ty += lh + 3

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def render(self, tree: Dict, output_path: str):
        if not tree:
            print("Empty tree.")
            return

        # Pass 1: measure all nodes
        self._measure(tree)

        # Pass 2: layout (root at x=60, vertically centered at 0)
        self._layout(tree, x=60, cy=0)

        # Collect all nodes and compute bounding box
        all_nodes = self._all_nodes(tree)

        min_x = min(n['x']           for n in all_nodes)
        max_x = max(n['x'] + n['w']  for n in all_nodes)
        min_y = min(n['y']           for n in all_nodes)
        max_y = max(n['y'] + n['h']  for n in all_nodes)

        margin = 60
        off_x  = margin - min_x
        off_y  = margin - min_y

        img_w = int(max_x - min_x + margin * 2)
        img_h = int(max_y - min_y + margin * 2)

        # Shift all coordinates
        def shift(n: Dict):
            n['x']  += off_x
            n['rx'] += off_x
            n['y']  += off_y
            n['cy'] += off_y
            for c in n['children']:
                shift(c)
        shift(tree)

        # Render
        img  = Image.new('RGB', (img_w, img_h), '#FFFFFF')
        draw = ImageDraw.Draw(img)

        # Draw connections first (behind text)
        self._draw_connections(draw, tree)

        # Draw text on top
        self._draw_text_nodes(draw, all_nodes)

        img.save(output_path, 'PNG')
        print(f"[Done] {output_path}  |  {img_w} x {img_h} px  |  {len(all_nodes)} nodes")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    input_file  = r'x:\ygling2008.github.io\test.md'
    output_file = r'x:\ygling2008.github.io\test.png'

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    nodes = parse_markdown(content)
    if not nodes:
        print("No nodes parsed!")
        return

    max_depth = max(n[0] for n in nodes)
    print(f"[Parse] {len(nodes)} nodes, max depth = {max_depth}")

    tree = build_tree(nodes)

    renderer = MindMapRenderer()
    renderer.render(tree, output_file)


if __name__ == '__main__':
    main()
