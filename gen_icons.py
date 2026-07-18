# -*- coding: utf-8 -*-
"""Генерация иконок Taska в высоком разрешении.
Дизайн: белая галочка на диагональном градиенте #10b981 -> #0ea5e9.
"""
from PIL import Image, ImageDraw
import os

C1 = (0x10, 0xb9, 0x81)   # зелёный (верх-лево)
C2 = (0x0e, 0xa5, 0xe9)   # синий (низ-право)
SS = 4                    # суперсэмплинг

RES = r"D:\Творчество\drive-mobile\android\app\src\main\res"
DIST = r"D:\Творчество\dist"


_grad_cache = {}


def gradient(size):
    """Диагональный градиент C1->C2: считается на карте 128px и растягивается —
    градиент гладкий, разницы не видно, а работает в сотни раз быстрее."""
    if size not in _grad_cache:
        small = 128
        img = Image.new("RGB", (small, small))
        px = img.load()
        for y in range(small):
            for x in range(small):
                t = (x + y) / (2 * (small - 1))
                px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(C1, C2))
        _grad_cache[size] = img.resize((size, size), Image.BILINEAR)
    return _grad_cache[size]


def rounded_mask(size, radius_frac):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    r = round(size * radius_frac)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=255)
    return m


def circle_mask(size):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([0, 0, size - 1, size - 1], fill=255)
    return m


def draw_check(img, cx_frac=0.5, cy_frac=0.5, scale=1.0):
    """Белая галочка. scale — доля стороны, которую занимает галочка."""
    size = img.width
    d = ImageDraw.Draw(img)
    w = size * scale
    # опорные точки галочки в долях её ширины (подобраны по старой иконке)
    pts = [(-0.28, 0.02), (-0.07, 0.23), (0.30, -0.20)]
    cx, cy = size * cx_frac, size * cy_frac
    p = [(cx + x * w, cy + y * w) for x, y in pts]
    lw = round(size * scale * 0.155)
    d.line(p, fill=(255, 255, 255, 255), width=lw, joint="curve")
    r = lw / 2
    for x, y in (p[0], p[2]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 255))


def make_full_icon(size, shape="rounded"):
    """Полная иконка: градиент + галочка, скруглённый квадрат или круг."""
    big = size * SS
    base = gradient(big).convert("RGBA")
    draw_check(base, scale=0.95)
    mask = rounded_mask(big, 0.225) if shape == "rounded" else circle_mask(big)
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    out.paste(base, (0, 0), mask)
    return out.resize((size, size), Image.LANCZOS)


def make_foreground(size):
    """Adaptive-иконка: градиент во весь квадрат + галочка в безопасной зоне."""
    big = size * SS
    base = gradient(big).convert("RGBA")
    draw_check(base, scale=0.62)  # безопасная зона ~61% канвы
    return base.resize((size, size), Image.LANCZOS)


def main():
    # --- Android mipmaps ---
    launcher = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    fg = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
    for dpi, s in launcher.items():
        folder = os.path.join(RES, "mipmap-" + dpi)
        os.makedirs(folder, exist_ok=True)
        make_full_icon(s, "rounded").save(os.path.join(folder, "ic_launcher.png"))
        make_full_icon(s, "circle").save(os.path.join(folder, "ic_launcher_round.png"))
        print("mipmap-%s: launcher %d" % (dpi, s))
    for dpi, s in fg.items():
        folder = os.path.join(RES, "mipmap-" + dpi)
        os.makedirs(folder, exist_ok=True)
        make_foreground(s).save(os.path.join(folder, "ic_launcher_foreground.png"))
        print("mipmap-%s: foreground %d" % (dpi, s))

    # --- PC ---
    master = make_full_icon(1024, "rounded")
    master.save(os.path.join(DIST, "icon.png"))
    print("dist/icon.png 1024")
    master.save(os.path.join(DIST, "icon.ico"),
                sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)])
    print("dist/icon.ico multi-size")

    # предпросмотр для проверки
    prev = make_full_icon(256, "rounded")
    prev.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview_icon.png"))
    fgprev = make_foreground(256)
    fgprev.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview_fg.png"))
    print("done")


if __name__ == "__main__":
    main()
