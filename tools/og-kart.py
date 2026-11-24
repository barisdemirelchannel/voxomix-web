#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""assets/og-card.png üretir — bağlantı önizlemesi (og:image / twitter:image).

NEDEN VAR: eski og görseli promo-banner.png idi; eski logoyu, eski marka yazısını
ve eski uygulama arayüzünü taşıyordu, üstelik 1254×1254 kareydi (önizlemeler
1,91:1 bekler, kare olan kırpılır). Bu kart dilden bağımsızdır — metin yok, yalnız
marka kilidi + kanal renkleri şeridi. Böylece 6 dilin hepsinde aynı dosya kullanılır.

Kullanım: python3 tools/og-kart.py
"""
import os
from PIL import Image

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630

# Site koyu temasının zemini (--bg #08080a) ile üst tarafta hafif açılma
TOP, BOTTOM = (18, 18, 26), (8, 8, 10)

# style.css'teki --kanal ile aynı diziliş: renk aralıkları yüzde olarak
KANAL = [
    ((139, 108, 255), 0.00, 0.14),   # --st-vokal
    ((61, 139, 255), 0.17, 0.31),    # --st-davul
    ((31, 200, 176), 0.34, 0.48),    # --st-bas
    ((79, 208, 106), 0.51, 0.65),    # --st-tel
    ((245, 165, 36), 0.68, 0.82),    # --st-klavye
    ((240, 84, 106), 0.85, 1.00),    # --st-kayit
]

def main():
    kart = Image.new("RGB", (W, H), BOTTOM)
    # dikey geçiş
    px = kart.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(round(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c

    # marka kilidi (koyu zemin çeşidi: yazı beyaz)
    logo = Image.open(os.path.join(WEB, "assets/logo-yatay-koyu.png")).convert("RGBA")
    hedef_g = 560
    oran = hedef_g / logo.width
    logo = logo.resize((hedef_g, round(logo.height * oran)), Image.LANCZOS)
    # görsel olarak ortala: şeridin üstündeki alanın merkezine koy
    serit_y, serit_h = H - 96, 10
    alan_h = serit_y
    kart.paste(logo, ((W - logo.width) // 2, (alan_h - logo.height) // 2), logo)

    # kanal renkleri şeridi — style.css'teki --kanal ile aynı oranlar
    kenar = 140
    serit_g = W - 2 * kenar
    for renk, bas, bit in KANAL:
        x0 = kenar + round(serit_g * bas)
        x1 = kenar + round(serit_g * bit)
        for y in range(serit_y, serit_y + serit_h):
            for x in range(x0, x1):
                px[x, y] = renk

    cikti = os.path.join(WEB, "assets/og-card.png")
    kart.save(cikti, "PNG", optimize=True)
    print("og-card.png: %d×%d · %d bayt" % (W, H, os.path.getsize(cikti)))

main()
