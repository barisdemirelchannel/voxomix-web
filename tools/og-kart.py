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

# Marka kılavuzu s.6 "Koyu zemin (ikon)": #24202F → #110F16 (yukarıdan aşağı).
# İlk yazışta sitenin kendi koyu zeminini (#12121A → #08080A) kullanmıştım; kılavuzun
# değerleri bunlar, ikon tuvaliyle de aynı olsun diye değiştirildi.
TOP, BOTTOM = (0x24, 0x20, 0x2F), (0x11, 0x0F, 0x16)

# MARKA KILAVUZU s.2/s.6 kanal renkleri (koyu zemin değerleri) — sitenin kendi
# --kanal değişkeni DEĞİL. İlk yazışta style.css'ten almıştım; iki fark vardı:
#  · tonlar birkaç birim kayıktı (ör. bas site #1FC8B0, kılavuz #22C9B8)
#  · 6. renk olarak kayıt kırmızısı (#F0546A) giriyordu; kılavuzun altıncısı
#    "Diğer" moru (#A99BDB). Kırmızı marka çalışmasında bilerek çıkarılmıştı.
KANAL = [
    ((0x8B, 0x6C, 0xFF), 0.00, 0.14),   # Vokal
    ((0x3F, 0x8C, 0xFF), 0.17, 0.31),   # Davul
    ((0x22, 0xC9, 0xB8), 0.34, 0.48),   # Bas
    ((0x5C, 0xD1, 0x7A), 0.51, 0.65),   # Telli
    ((0xF3, 0xA7, 0x3F), 0.68, 0.82),   # Tuşlu
    ((0xA9, 0x9B, 0xDB), 0.85, 1.00),   # Diğer
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
