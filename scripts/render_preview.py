#!/usr/bin/env python3
"""Render README preview images from themes/hacker-theme.json.

Usage: python3 scripts/render_preview.py
Writes assets/preview.svg and assets/palette.svg.
"""
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
theme = json.loads((ROOT / "themes/hacker-theme.json").read_text())["themes"][0]["style"]
syn = {k: v for k, v in theme["syntax"].items()}

def c(key):
    return theme[key]

def s(key):
    return syn[key]["color"]

def style_attr(key):
    d = syn[key]
    out = f'fill="{d["color"]}"'
    if d.get("font_style") == "italic":
        out += ' font-style="italic"'
    if d.get("font_weight"):
        out += f' font-weight="{d["font_weight"]}"'
    return out

CODE = '''\
// the system is listening...
import { Terminal } from "./terminal";

const GLYPHS = "01#$%&@*<>/";
const SPEED_MS = 42;

interface Drop {
  x: number;
  y: number;
  trail: string[];
}

/** Green rain, falling forever. */
export class MatrixRain {
  private drops: Drop[] = [];

  constructor(private term: Terminal, cols = 80) {
    for (let x = 0; x < cols; x++) {
      this.drops.push({ x, y: 0, trail: [] });
    }
  }

  tick(): void {
    for (const drop of this.drops) {
      const ch = GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
      this.term.write(drop.x, drop.y++, ch, `rgb(${0}, 255, 0)`);
    }
    setTimeout(() => this.tick(), SPEED_MS);
  }
}'''

KEYWORDS = {"import", "from", "const", "let", "interface", "export", "class", "private",
            "constructor", "for", "of", "void", "new", "return"}
SPECIAL = {"this"}
CONSTS = {"true", "false", "null", "undefined"}
TYPES_BUILTIN = {"number", "string", "boolean", "void"}

TOKEN = re.compile(r'''
  (?P<doc>/\*\*.*?\*/) | (?P<comment>//.*) |
  (?P<string>"[^"]*"|`[^`]*`) | (?P<number>\b\d+\b) |
  (?P<ident>[A-Za-z_$][\w$]*) | (?P<op>\+\+|=>|[=<>+*\-]) |
  (?P<punct>[{}()\[\];:,.]) | (?P<ws>\s+) | (?P<other>.)
''', re.X)

def tokenize(line):
    toks = []
    for m in TOKEN.finditer(line):
        kind, text = m.lastgroup, m.group()
        role = None
        if kind == "doc": role = "comment.doc"
        elif kind == "comment": role = "comment"
        elif kind == "string": role = "string"
        elif kind == "number": role = "number"
        elif kind == "op": role = "operator"
        elif kind == "punct": role = "punctuation"
        elif kind == "ident":
            rest = line[m.end():]
            prev = line[:m.start()]
            if text in TYPES_BUILTIN and prev.rstrip().endswith(":"):
                role = "type.builtin"
            elif text in KEYWORDS: role = "keyword"
            elif text in SPECIAL: role = "variable.special"
            elif text in CONSTS: role = "boolean"
            elif text.isupper() and len(text) > 1: role = "constant"
            elif rest.startswith("("): role = "function"
            elif text[0].isupper(): role = "type"
            elif prev.endswith("."): role = "property"
            else: role = "variable"
        toks.append((text, role))
    return toks

FONT = "'JetBrains Mono','SF Mono','Fira Code',Menlo,Consolas,monospace"
FS, LH, CW = 14, 22, 14 * 0.6
lines = CODE.split("\n")
W = 1040
TITLE_H, TAB_H, STATUS_H, TERM_H = 36, 38, 26, 120
SIDE_W, GUTTER_W = 210, 52
code_top = TITLE_H + TAB_H + 14
H = code_top + len(lines) * LH + 14 + TERM_H + STATUS_H
ACTIVE = 25  # 1-based active line

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="{FS}">',
       f'<defs><clipPath id="win"><rect width="{W}" height="{H}" rx="12"/></clipPath>'
       f'<filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>',
       '<g clip-path="url(#win)">',
       f'<rect width="{W}" height="{H}" fill="{c("background")}"/>']

# title bar
out.append(f'<rect width="{W}" height="{TITLE_H}" fill="{c("title_bar.background")}"/>')
for i, col in enumerate(["#ff5f57", "#febc2e", "#28c840"]):
    out.append(f'<circle cx="{20 + i * 20}" cy="{TITLE_H / 2}" r="6" fill="{col}"/>')
out.append(f'<text x="{W / 2}" y="{TITLE_H / 2 + 5}" text-anchor="middle" fill="{c("text.muted")}" font-size="13">hacker-theme — matrix.ts</text>')
out.append(f'<rect y="{TITLE_H - 1}" width="{W}" height="1" fill="{c("border")}"/>')

# sidebar
body_h = H - TITLE_H - STATUS_H
out.append(f'<rect y="{TITLE_H}" width="{SIDE_W}" height="{body_h}" fill="{c("panel.background")}"/>')
out.append(f'<rect x="{SIDE_W}" y="{TITLE_H}" width="1" height="{body_h}" fill="{c("border")}"/>')
tree = [("▾ hacker-theme", 0, "text", False), ("▾ src", 1, "text", False),
        ("matrix.ts", 2, "text", True), ("terminal.ts", 2, "modified", False),
        ("glitch.ts", 2, "created", False), ("▸ assets", 1, "text", False),
        ("extension.toml", 1, "text.muted", False), ("README.md", 1, "text.muted", False)]
for i, (name, depth, color, sel) in enumerate(tree):
    y = TITLE_H + 18 + i * 26
    if sel:
        out.append(f'<rect x="6" y="{y - 4}" width="{SIDE_W - 12}" height="24" rx="4" fill="{c("element.selected")}"/>')
    out.append(f'<text x="{16 + depth * 14}" y="{y + 12}" fill="{c(color)}" font-size="13">{escape(name)}</text>')

# tab bar
ex = SIDE_W + 1
out.append(f'<rect x="{ex}" y="{TITLE_H}" width="{W - ex}" height="{TAB_H}" fill="{c("tab_bar.background")}"/>')
out.append(f'<rect x="{ex}" y="{TITLE_H}" width="130" height="{TAB_H}" fill="{c("tab.active_background")}"/>')
out.append(f'<rect x="{ex}" y="{TITLE_H}" width="130" height="2" fill="{c("text.accent")}"/>')
out.append(f'<text x="{ex + 22}" y="{TITLE_H + 24}" fill="{c("text")}" font-size="13">matrix.ts</text>')
out.append(f'<text x="{ex + 152}" y="{TITLE_H + 24}" fill="{c("text.muted")}" font-size="13">terminal.ts</text>')
out.append(f'<circle cx="{ex + 252}" cy="{TITLE_H + 19}" r="3" fill="{c("modified")}"/>')
out.append(f'<rect x="{ex}" y="{TITLE_H + TAB_H - 1}" width="{W - ex}" height="1" fill="{c("border")}"/>')

# editor
ed_top = TITLE_H + TAB_H
ed_h = H - ed_top - STATUS_H - TERM_H
out.append(f'<rect x="{ex}" y="{ed_top}" width="{W - ex}" height="{ed_h}" fill="{c("editor.background")}"/>')
ay = code_top + (ACTIVE - 1) * LH
out.append(f'<rect x="{ex}" y="{ay}" width="{W - ex}" height="{LH}" fill="{c("editor.active_line.background")}"/>')
tx = ex + GUTTER_W + 14
# selection on the active line ("Math.floor"), drawn behind the text
sel_line = lines[ACTIVE - 1]
sx = sel_line.index("Math")
out.append(f'<rect x="{tx + sx * CW}" y="{ay + 2}" width="{len("Math.floor") * CW}" height="{LH - 4}" rx="2" fill="{theme["players"][0]["selection"]}"/>')
for i, line in enumerate(lines, 1):
    y = code_top + (i - 1) * LH + 16
    ln_col = c("editor.active_line_number") if i == ACTIVE else c("editor.line_number")
    out.append(f'<text x="{ex + GUTTER_W - 8}" y="{y}" text-anchor="end" fill="{ln_col}">{i}</text>')
    indent = len(line) - len(line.lstrip(" "))
    for lvl in range(0, indent, 2):
        gx = tx + lvl * CW + 1
        out.append(f'<rect x="{gx}" y="{y - 16}" width="1" height="{LH}" fill="{c("editor.indent_guide")}"/>')
    # pin every token to its column so layout is identical in any monospace font
    col, spans = 0, []
    for t, role in tokenize(line):
        if t.strip():
            spans.append(f'<tspan x="{tx + col * CW:.1f}" textLength="{len(t) * CW:.1f}" '
                         f'lengthAdjust="spacingAndGlyphs" {style_attr(role) if role else ""}>{escape(t)}</tspan>')
        col += len(t)
    out.append(f'<text y="{y}" fill="{c("editor.foreground")}">{"".join(spans)}</text>')
cx = tx + (sx + len("Math.floor")) * CW
out.append(f'<rect x="{cx}" y="{ay + 3}" width="2" height="{LH - 6}" fill="{theme["players"][0]["cursor"]}" filter="url(#glow)"/>')

# terminal panel
ty = H - STATUS_H - TERM_H
out.append(f'<rect x="{ex}" y="{ty}" width="{W - ex}" height="{TERM_H}" fill="{c("terminal.background")}"/>')
out.append(f'<rect x="{ex}" y="{ty}" width="{W - ex}" height="1" fill="{c("border")}"/>')
a = lambda n: c(f"terminal.ansi.{n}")
term_lines = [
    [("~/hacker-theme", a("cyan")), (" on ", a("bright_black")), ("main", a("magenta")), (" ❯ ", a("green")), ("npm run rain", c("terminal.foreground"))],
    [("✓", a("green")), (" compiled ", c("terminal.foreground")), ("matrix.ts", a("yellow")), (" in ", a("bright_black")), ("42ms", a("blue"))],
    [("⚠", a("yellow")), (" 1 warning: ", a("yellow")), ("unused variable ", c("terminal.foreground")), ("`trail`", a("bright_cyan"))],
    [("ACCESS GRANTED", a("bright_green")), (" — welcome back, operator.", a("green"))],
]
for i, parts in enumerate(term_lines):
    spans = "".join(f'<tspan fill="{col}">{escape(t)}</tspan>' for t, col in parts)
    out.append(f'<text x="{ex + 18}" y="{ty + 30 + i * 22}" xml:space="preserve" font-size="13">{spans}</text>')

# status bar
sy = H - STATUS_H
out.append(f'<rect y="{sy}" width="{W}" height="{STATUS_H}" fill="{c("status_bar.background")}"/>')
out.append(f'<rect y="{sy}" width="{W}" height="1" fill="{c("border")}"/>')
out.append(f'<text x="16" y="{sy + 17}" font-size="12" xml:space="preserve"><tspan fill="{c("text.accent")}">● </tspan><tspan fill="{c("text.muted")}">main</tspan><tspan fill="{c("error")}">   ✕ 0</tspan><tspan fill="{c("warning")}">   ⚠ 1</tspan></text>')
out.append(f'<text x="{W - 16}" y="{sy + 17}" text-anchor="end" font-size="12" xml:space="preserve" fill="{c("text.muted")}">Ln {ACTIVE}, Col {sx + 11}   TypeScript   Hacker Theme</text>')
out.append("</g>")
out.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{c("border")}"/>')
out.append("</svg>")
(ROOT / "assets/preview.svg").write_text("\n".join(x for x in out if x) + "\n")

# palette strip
swatches = [("Neon", s("keyword")), ("Acid", s("function")), ("Cyan", s("type")),
            ("Amber", s("string")), ("Orange", s("number")), ("Violet", s("variable.special")),
            ("Comment", s("comment")), ("Text", c("editor.foreground")), ("Void", c("editor.background"))]
SW, SH, GAP = 104, 120, 10
PW = len(swatches) * (SW + GAP) + GAP
p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{SH + 2 * GAP}" viewBox="0 0 {PW} {SH + 2 * GAP}" font-family="{FONT}">',
     f'<rect width="{PW}" height="{SH + 2 * GAP}" rx="12" fill="{c("background")}"/>']
for i, (name, col) in enumerate(swatches):
    x = GAP + i * (SW + GAP)
    p.append(f'<rect x="{x}" y="{GAP}" width="{SW}" height="{SH}" rx="8" fill="{col}" stroke="{c("border")}"/>')
    p.append(f'<rect x="{x}" y="{GAP + SH - 44}" width="{SW}" height="44" fill="{c("panel.background")}" opacity="0.92"/>')
    p.append(f'<text x="{x + 10}" y="{GAP + SH - 26}" font-size="12" fill="{c("text")}">{name}</text>')
    p.append(f'<text x="{x + 10}" y="{GAP + SH - 10}" font-size="11" fill="{c("text.muted")}">{col}</text>')
p.append("</svg>")
(ROOT / "assets/palette.svg").write_text("\n".join(p) + "\n")
print("wrote assets/preview.svg and assets/palette.svg")
