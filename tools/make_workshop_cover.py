#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build 512x512 Steam Workshop covers for AutoSkillPointsForAgents.

Background is the official Total War: WARHAMMER III library hero art
(downloaded from Steam's CDN, no mod character art).  The skill-tree rune
badge and title are drawn locally.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(r"E:\dev\wh3mod")
ART = ROOT / "_analysis" / "wh3_library_hero.jpg"
OUT_DIR = Path(r"E:\dev\wh3mod\hero-auto-skill\workshop")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SIZE = 512
GOLD = (214, 171, 90)
GOLD_LIGHT = (250, 231, 178)
GOLD_DARK = (117, 73, 28)
INK = (15, 10, 7)
BLUE = (70, 155, 255)

CN_FONT = r"C:\Windows\Fonts\msyhbd.ttc"
CN_FALLBACK = r"C:\Windows\Fonts\simhei.ttf"
EN_FONT = r"C:\Windows\Fonts\constanb.ttf"
EN_FALLBACK = r"C:\Windows\Fonts\georgiab.ttf"


def font(path: str, fallback: str, size: int) -> ImageFont.FreeTypeFont:
    for p in (path, fallback):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    raise RuntimeError("no usable font")


def spaced(draw: ImageDraw.ImageDraw, xy, text, f, fill, spacing=2):
    widths = [draw.textlength(ch, font=f) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    x -= total / 2
    for ch, cw in zip(text, widths):
        draw.text((x, y), ch, font=f, fill=fill)
        x += cw + spacing


def radial_glow(canvas: Image.Image, center, radius, color=BLUE, alpha=70):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(10, 0, -1):
        r = int(radius * (1 + i * 0.10))
        a = int(alpha * (11 - i) / 10)
        d.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.22))
    canvas.alpha_composite(layer)


def rune_badge(size: int = 190) -> Image.Image:
    """A gold/blue skill-tree medallion with a check mark."""
    pad = 24
    full = size + pad * 2
    badge = Image.new("RGBA", (full, full), (0, 0, 0, 0))
    d = ImageDraw.Draw(badge)
    c = (full // 2, full // 2)
    r = size // 2 - 6

    # blue glow + dark disc
    glow = Image.new("RGBA", badge.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((c[0] - r - 10, c[1] - r - 10, c[0] + r + 10, c[1] + r + 10), fill=BLUE + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    badge.alpha_composite(glow)
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=(8, 16, 28, 245))
    d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), outline=GOLD_DARK + (255,), width=7)
    d.ellipse((c[0] - r + 5, c[1] - r + 5, c[0] + r - 5, c[1] + r - 5), outline=GOLD + (255,), width=2)
    d.ellipse((c[0] - r + 13, c[1] - r + 13, c[0] + r - 13, c[1] + r - 13), outline=GOLD_LIGHT + (110,), width=1)

    # runic ticks
    import math

    for i in range(12):
        a = math.radians(i * 30 + 15)
        x1 = c[0] + math.cos(a) * (r - 14)
        y1 = c[1] + math.sin(a) * (r - 14)
        x2 = c[0] + math.cos(a) * (r - 24)
        y2 = c[1] + math.sin(a) * (r - 24)
        d.line((x1, y1, x2, y2), fill=GOLD + (190,), width=2)

    # check mark: thick and bright so it reads as a tick, not a clock hand
    pts = [
        (c[0] - r * 0.40, c[1] + r * 0.03),
        (c[0] - r * 0.08, c[1] + r * 0.30),
        (c[0] + r * 0.44, c[1] - r * 0.34),
    ]
    d.line(pts, fill=(0, 0, 0, 230), width=max(11, size // 11), joint="curve")
    d.line(pts, fill=GOLD_LIGHT + (255,), width=max(8, size // 16), joint="curve")
    # rounded joints
    for x, y in (pts[0], pts[1], pts[2]):
        d.ellipse((x - max(5, size // 28), y - max(5, size // 28),
                   x + max(5, size // 28), y + max(5, size // 28)),
                  fill=GOLD_LIGHT + (255,))

    # small rune nodes around the ring, deliberately not connected to the centre
    for ang in (-135, -45, 135):
        a = math.radians(ang)
        nx = c[0] + math.cos(a) * (r + 2)
        ny = c[1] + math.sin(a) * (r + 2)
        d.ellipse((nx - 8, ny - 8, nx + 8, ny + 8), fill=(10, 25, 45, 255), outline=GOLD + (255,), width=2)
        d.ellipse((nx - 3, ny - 3, nx + 3, ny + 3), fill=BLUE + (255,))
    return badge


def base(centering=(0.55, 0.5)) -> Image.Image:
    im = Image.open(ART).convert("RGB")
    bg = ImageOps.fit(im, (SIZE, SIZE), method=Image.LANCZOS, centering=centering)
    bg = ImageEnhance.Brightness(bg).enhance(0.88)
    bg = ImageEnhance.Contrast(bg).enhance(1.10)
    canvas = bg.convert("RGBA")
    canvas.alpha_composite(Image.new("RGBA", canvas.size, (6, 10, 23, 40)))

    grad = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(170):
        gd.line((0, y, SIZE, y), fill=(0, 0, 0, int(160 * (1 - y / 170))))
    for y in range(350, SIZE):
        gd.line((0, y, SIZE, y), fill=(0, 0, 0, int(200 * (y - 350) / (SIZE - 350))))
    canvas.alpha_composite(grad)

    # vignette
    mask = Image.new("L", (SIZE, SIZE), 0)
    vd = ImageDraw.Draw(mask)
    vd.ellipse((-SIZE * 0.25, -SIZE * 0.25, SIZE * 1.25, SIZE * 1.25), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(SIZE * 0.18))
    inv = mask.point(lambda v: int((255 - v) * 185 / 255))
    dark = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    dark.putalpha(inv)
    canvas.alpha_composite(dark)
    return canvas


def border(canvas: Image.Image):
    d = ImageDraw.Draw(canvas)
    d.rectangle((8, 8, SIZE - 9, SIZE - 9), outline=GOLD_DARK + (255,), width=4)
    d.rectangle((11, 11, SIZE - 12, SIZE - 12), outline=GOLD + (255,), width=2)
    d.rectangle((17, 17, SIZE - 18, SIZE - 18), outline=GOLD_LIGHT + (120,), width=1)
    for cx, cy in ((15, 15), (SIZE - 16, 15), (15, SIZE - 16), (SIZE - 16, SIZE - 16)):
        d.polygon([(cx, cy - 7), (cx + 7, cy), (cx, cy + 7), (cx - 7, cy)],
                  fill=GOLD_LIGHT + (255,), outline=GOLD_DARK + (255,))


def title(canvas: Image.Image, badge_pos):
    d = ImageDraw.Draw(canvas)
    f_small = font(EN_FONT, EN_FALLBACK, 11)
    spaced(d, (SIZE // 2, 26), "TOTAL WAR : WARHAMMER III", f_small, (0, 0, 0, 220), 2)
    spaced(d, (SIZE // 2, 24), "TOTAL WAR : WARHAMMER III", f_small, GOLD_LIGHT + (245,), 2)

    # skill-tree badge top-left
    badge = rune_badge(168)
    canvas.alpha_composite(badge, badge_pos)

    # bottom plaque
    d.rounded_rectangle((22, 368, SIZE - 23, 500), radius=10, fill=(8, 6, 5, 210))
    d.rounded_rectangle((22, 368, SIZE - 23, 500), radius=10, outline=GOLD_DARK + (255,), width=2)
    d.rounded_rectangle((26, 372, SIZE - 27, 496), radius=8, outline=GOLD + (120,), width=1)

    f_main = font(CN_FONT, CN_FALLBACK, 58)
    d.text((SIZE // 2, 408 + 3), "自动加点", font=f_main, fill=(0, 0, 0, 235),
           stroke_width=4, stroke_fill=(0, 0, 0, 235), anchor="mm")
    d.text((SIZE // 2, 408), "自动加点", font=f_main, fill=GOLD_LIGHT + (255,),
           stroke_width=3, stroke_fill=INK + (255,), anchor="mm")

    f_sub = font(CN_FONT, CN_FALLBACK, 19)
    d.text((SIZE // 2, 456), "事务官 / 领主", font=f_sub, fill=(225, 210, 180, 245), anchor="ma")
    f_en = font(EN_FONT, EN_FALLBACK, 10)
    spaced(d, (SIZE // 2, 482), "AUTO SKILL POINTS FOR AGENTS", f_en, GOLD + (235,), 2)
    border(canvas)


def main():
    a = base((0.55, 0.5))
    title(a, (18, 18))
    a.save(OUT_DIR / "cover_daemon.png")

    b = base((0.40, 0.55))
    title(b, (326, 18))
    b.save(OUT_DIR / "cover_mage.png")

    print("saved", OUT_DIR / "cover_daemon.png", a.size)
    print("saved", OUT_DIR / "cover_mage.png", b.size)


if __name__ == "__main__":
    main()
