"""Builds the flight-strip SVGs used by README.md.

Run:  uv run --with fonttools --with brotli build.py

To add a project, append to STRIPS and add its <a><img></a> line to README.md.
"""

import base64
import io
import textwrap
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).parent
OUT = ROOT / "assets"

INK = "#16202B"
PENCIL = "#D4322C"

# Strip colour says what kind of traffic it is: (holder, paper)
BAYS = {
    "agents": ("#2F6FB5", "#DCE9F7"),
    "markets": ("#C98A12", "#FBEFC4"),
    "web": ("#C2476B", "#F8DDE3"),
    "tower": ("#39424E", "#F4F6F3"),
}

STRIPS = [
    dict(
        repo="kai",
        bay="agents",
        kind=["Python"],
        remarks="A control tower for AI agents in the terminal, with MCP built in.",
    ),
    dict(
        repo="ai-news-mcp",
        bay="agents",
        kind=["Python"],
        remarks="Collects AI news from 23 sources into a local store any MCP client can query.",
    ),
    dict(
        repo="sinotrade-api",
        bay="markets",
        kind=["TypeScript", "Python"],
        remarks="Live Taiwan and US quotes, K-lines and paper trading on the Shioaji SDK.",
    ),
    dict(
        repo="dwen-cms",
        bay="web",
        kind=["TypeScript", "MDX"],
        remarks="My site, run with AI agents: they draft and open PRs, I decide what ships.",
    ),
]


def font_face(family: str, weight: int, filename: str) -> str:
    """Subset a font to Basic Latin and return an @font-face rule with it inlined.

    SVGs shown through <img> cannot load outside files, so the font travels inside.
    """
    font = TTFont(ROOT / "fonts" / filename)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern"]
    sub = subset.Subsetter(options)
    sub.populate(unicodes=range(0x20, 0x7F))
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def styles(*faces: str) -> str:
    return (
        "<style>"
        + "".join(faces)
        + ".b{font-family:'B612',Verdana,sans-serif;font-weight:700}"
        ".r{font-family:'B612',Verdana,sans-serif;font-weight:400}"
        ".m{font-family:'B612 Mono',ui-monospace,monospace;font-weight:400}"
        ".mark{stroke-dasharray:1;stroke-dashoffset:1;animation:draw .8s .5s ease-out forwards}"
        "@keyframes draw{to{stroke-dashoffset:0}}"
        "@media (prefers-reduced-motion:reduce){.mark{animation:none;stroke-dashoffset:0}}"
        "</style>"
    )


def holder(w: int, h: int, bay: str) -> str:
    """The plastic holder with its paper strip, plus the grip on the left tab."""
    hold, paper = BAYS[bay]
    return (
        f'<rect width="{w}" height="{h}" rx="7" fill="{hold}"/>'
        f'<rect x="11" y="{h / 2 - 14}" width="3" height="28" rx="1.5" fill="#fff" opacity=".45"/>'
        f'<rect x="24" y="7" width="{w - 31}" height="{h - 14}" rx="2" fill="{paper}"/>'
    )


def rule(x1, y1, x2, y2) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.5"/>'


def strip_svg(s: dict, faces: list[str]) -> str:
    w, h = 760, 104
    lines = textwrap.wrap(s["remarks"], 39)
    assert len(lines) <= 3, s["repo"]
    first = 57 - (len(lines) - 1) * 10.5
    remarks = "".join(
        f'<text class="r" x="414" y="{first + i * 21}" font-size="15.5" fill="{INK}">{escape(t)}</text>'
        for i, t in enumerate(lines)
    )
    kind = "".join(
        f'<text class="m" x="284" y="{(57 if len(s["kind"]) == 1 else 46) + i * 22}" font-size="14" fill="{INK}">{escape(t)}</text>'
        for i, t in enumerate(s["kind"])
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        f"<title>{escape(s['repo'])}: {escape(s['remarks'])}</title>"
        + styles(*faces)
        + holder(w, h, s["bay"])
        + rule(270, 7, 270, h - 7)
        + rule(400, 7, 400, h - 7)
        + f'<text class="b" x="40" y="50" font-size="23" fill="{INK}">{escape(s["repo"].upper())}</text>'
        + f'<text class="r" x="40" y="76" font-size="14" fill="{INK}" opacity=".72">{s["bay"]}</text>'
        + kind
        + remarks
        + "</svg>"
    )


def hero_svg(faces: list[str]) -> str:
    w, h = 760, 250
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        "<title>Duncan (Hung-Yu Wen). I build agent systems for the terminal and for the markets.</title>"
        + styles(*faces)
        + holder(w, h, "tower")
        + rule(520, 7, 520, h - 7)
        + rule(520, 86, w - 7, 86)
        + rule(520, 165, w - 7, 165)
        + f'<text class="b" x="44" y="112" font-size="88" letter-spacing="-1" fill="{INK}">DUNCAN</text>'
        # the controller's grease-pencil mark, drawn once on load
        + f'<path class="mark" pathLength="1" d="M46 138 C 112 129, 176 145, 242 135 S 352 130, 428 137" '
        f'fill="none" stroke="{PENCIL}" stroke-width="6" stroke-linecap="round"/>'
        + f'<text class="r" x="46" y="184" font-size="19" fill="{INK}">I build agent systems for the terminal</text>'
        + f'<text class="r" x="46" y="210" font-size="19" fill="{INK}">and for the markets.</text>'
        + f'<text class="b" x="540" y="54" font-size="21" fill="{INK}">Hung-Yu Wen</text>'
        + f'<text class="m" x="540" y="135" font-size="26" fill="{INK}">TPE</text>'
        + f'<text class="r" x="606" y="134" font-size="16" fill="{INK}">Taiwan</text>'
        + f'<text class="m" x="540" y="211" font-size="14.5" fill="{INK}">duncan-wen.aibbm.org</text>'
        + "</svg>"
    )


def main() -> None:
    OUT.mkdir(exist_ok=True)
    bold = font_face("B612", 700, "B612-Bold.ttf")
    regular = font_face("B612", 400, "B612-Regular.ttf")
    mono = font_face("B612 Mono", 400, "B612Mono-Regular.ttf")
    faces = [bold, regular, mono]

    (OUT / "hero.svg").write_text(hero_svg(faces))
    for s in STRIPS:
        (OUT / f"strip-{s['repo']}.svg").write_text(strip_svg(s, faces))
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name}\t{f.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
