import shutil
import subprocess
import tempfile
from pathlib import Path

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

PALET = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "panel2": "#1c2330",
        "line": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "faint": "#484f58",
        "amber": "#f5a623",
        "light": "#fff4d6",
        "red": "#ff4d4d",
        "green": "#3fb950",
        "cyan": "#58c4dc",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "panel2": "#eaeef2",
        "line": "#d1d9e0",
        "text": "#1f2328",
        "muted": "#59636e",
        "faint": "#afb8c1",
        "amber": "#bf8700",
        "light": "#fff8c5",
        "red": "#cf222e",
        "green": "#1a7f37",
        "cyan": "#0969da",
    },
}

_GLYPHS = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    ",": ["..", "..", "..", "..", "..", ".#", "#."],
    ":": [".", ".", "#", ".", ".", "#", "."],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "-": ["....", "....", "....", "####", "....", "....", "...."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "=": ["....", "....", "####", "....", "####", "....", "...."],
    "_": ["#####" if i == 6 else "....." for i in range(7)],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    ">": ["#...", ".#..", "..#.", "...#", "..#.", ".#..", "#..."],
    "<": ["...#", "..#.", ".#..", "#...", ".#..", "..#.", "...#"],
    "(": [".#", "#.", "#.", "#.", "#.", "#.", ".#"],
    ")": ["#.", ".#", ".#", ".#", ".#", ".#", "#."],
    "[": ["##", "#.", "#.", "#.", "#.", "#.", "##"],
    "]": ["##", ".#", ".#", ".#", ".#", ".#", "##"],
    "'": ["#", "#", ".", ".", ".", ".", "."],
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "|": ["#", "#", "#", "#", "#", "#", "#"],
    "·": [".", ".", ".", "#", ".", ".", "."],
    "▶": ["#...", "##..", "###.", "####", "###.", "##..", "#..."],
    "◀": ["...#", "..##", ".###", "####", ".###", "..##", "...#"],
    "▲": [".......", "...#...", "..###..", ".#####.", "#######", ".......", "......."],
    "▼": [".......", "#######", ".#####.", "..###..", "...#...", ".......", "......."],
    "█": ["#####"] * 7,
    "★": ["..#..", "..#..", "#####", ".###.", ".#.#.", "#...#", "....."],
}

_ACCENTED = {
    "İ": ("I", "..#..", None),
    "Ü": ("U", ".#.#.", None),
    "Ö": ("O", ".#.#.", None),
    "Ç": ("C", None, "..#.."),
    "Ş": ("S", None, "..#.."),
    "Ğ": ("G", ".###.", None),
}


def glyph(ch):
    ch = ch.upper() if ch not in ("ı", "i") else ("I" if ch == "ı" else "İ")
    if ch in _ACCENTED:
        base, top, bottom = _ACCENTED[ch]
        body = _GLYPHS[base]
        width = len(body[0])
        return [top or "." * width] + body + [bottom or "." * width]
    body = _GLYPHS.get(ch, _GLYPHS["?"])
    width = len(body[0])
    return ["." * width] + body + ["." * width]


def text_width(text, px, spacing=1):
    total = 0
    for i, ch in enumerate(text):
        total += len(glyph(ch)[0]) * px
        if i < len(text) - 1:
            total += spacing * px
    return total


def pixel_path(text, x, y, px, spacing=1):
    parts = []
    cursor = x
    for ch in text:
        rows = glyph(ch)
        width = len(rows[0])
        for r, row in enumerate(rows):
            c = 0
            while c < width:
                if row[c] == "#":
                    start = c
                    while c < width and row[c] == "#":
                        c += 1
                    run = c - start
                    gx = cursor + start * px
                    gy = y + (r - 1) * px
                    parts.append(f"M{gx:g} {gy:g}h{run * px:g}v{px:g}h{-run * px:g}z")
                else:
                    c += 1
        cursor += (width + spacing) * px
    return "".join(parts)


def pixel_text(text, x, y, px, fill, anchor="start", spacing=1, extra=""):
    w = text_width(text, px, spacing)
    if anchor == "middle":
        x = x - w / 2
    elif anchor == "end":
        x = x - w
    return f'<path d="{pixel_path(text, x, y, px, spacing)}" fill="{fill}" shape-rendering="crispEdges"{(" " + extra) if extra else ""}/>'


def svg(width, height, body, style="", defs="", label=""):
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"'
    head += f' aria-label="{label}">' if label else ">"
    out = [head]
    if label:
        out.append(f"<title>{label}</title>")
    if style:
        out.append(f"<style>{style}</style>")
    if defs:
        out.append(f"<defs>{defs}</defs>")
    out.append(body)
    out.append("</svg>")
    return "\n".join(out)


def write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def screenshot(target, out_png, width=900, height=400, wait_ms=1500, dark=False):
    if not str(target).startswith(("http://", "https://", "file:")):
        target = Path(target).resolve()
    out_png = Path(out_png).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    profile_dir = tempfile.mkdtemp(prefix="profil-chrome-")
    args = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        f"--user-data-dir={profile_dir}",
        f"--window-size={width},{height}",
        f"--virtual-time-budget={wait_ms}",
        f"--screenshot={out_png}",
    ]
    if dark:
        args.append("--force-dark-mode")
        args.append("--blink-settings=preferredColorScheme=0")
    args.append(target.as_uri() if isinstance(target, Path) and target.exists() else str(target))
    try:
        subprocess.run(args, check=True, capture_output=True, timeout=120)
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)
    return out_png


def snapshot(svg_path, out_png, width, height, t):
    svg_text = Path(svg_path).read_text(encoding="utf-8")
    out_png = Path(out_png).resolve()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    page = out_png.with_suffix(".snap.html")
    script = (
        "const t=" + str(t) + ";"
        "document.querySelectorAll('svg').forEach(s=>{if(s.pauseAnimations){s.pauseAnimations();s.setCurrentTime(t);}});"
        "document.getAnimations().forEach(a=>{a.pause();a.currentTime=t*1000;});"
    )
    html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<style>html,body{margin:0;background:transparent}</style></head><body>"
        + svg_text
        + "<script>"
        + script
        + "</script></body></html>"
    )
    page.write_text(html, encoding="utf-8")
    try:
        screenshot(page, out_png, width, height, wait_ms=800)
    finally:
        page.unlink(missing_ok=True)
    return out_png
