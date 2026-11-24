#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Marka kilidini (nav + altbilgi) ve favicon/manifest bağlarını her sayfaya işler.

NEDEN AYRI BİR ARAÇ: sayfaların çoğu üretiliyor (prerender-lang.py,
build-legal-lang.py, build-blog-index.py). Elle değiştirirsen ilk yeniden
üretimde kaybolur. İdempotenttir → her üretimden sonra çalıştır:

  python3 tools/prerender-lang.py es fr de it
  python3 tools/build-legal-lang.py
  python3 tools/inject-theme.py
  python3 tools/inject-marka.py
  python3 tools/inject-analytics.py
  python3 tools/build-sitemap.py

Kullanım: python3 tools/inject-marka.py [--check]
"""
import os, re, sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'google3b843533d74b7e6f.html'}

# 1050×246 → 26 px yükseklikte 111 px. width/height veriliyor ki yüklenirken
# düzen kaymasın (CLS); gerçek boyutu CSS'teki .brand-mark belirliyor.
MARKA = ('<img class="brand-mark brand-light" src="/assets/logo-yatay.svg" alt="VoxoMix" width="111" height="26">\n'
         '    <img class="brand-mark brand-dark" src="/assets/logo-yatay-koyu.svg" alt="VoxoMix" width="111" height="26">')

# nav-logo'nun İÇİ: ya eski (ikon + metin / renkli span), ya da zaten işlenmiş hâli.
ESKI_IC = (r'<img\s+src="[^"]*logo\.png"[^>]*>\s*'
           r'(?:VoxoMix|<span>Voxo<span style="color:[^"]*">Mix</span></span>)')
YENI_IC = r'(?:<img class="brand-mark[^>]*>\s*)+'
BLOK = re.compile(
    r'(<(a|div)\b[^>]*class="nav-logo"[^>]*>)\s*(?:' + ESKI_IC + r'|' + YENI_IC + r')\s*(</\2>)',
    re.S)
# Eşleşmeyen nav-logo bloğu kalırsa sessizce geçmesin diye ayrı tarama
HERHANGI = re.compile(r'<(a|div)\b[^>]*class="nav-logo"[^>]*>.*?</\1>', re.S)

IKON = ('<link rel="icon" href="/assets/favicon.ico" sizes="32x32">\n'
        '  <link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">\n'
        '  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">\n'
        '  <link rel="manifest" href="/site.webmanifest">')
IKON_RE = re.compile(r'\s*<link rel="icon"[^>]*>\s*<link rel="icon"[^>]*>\s*'
                     r'<link rel="apple-touch-icon"[^>]*>\s*<link rel="manifest"[^>]*>', re.S)
# ESKİ bağlar: 873 KB'lık assets/logo.png favicon olarak kullanılıyordu (32 px'de!).
# Gerçek favicon seti geldiği için bunlar siliniyor.
ESKI_IKON_RE = re.compile(r'\s*<link rel="(?:icon|apple-touch-icon)"[^>]*href="[^"]*logo\.png"[^>]*>', re.S)

check = '--check' in sys.argv
degisen = 0
eslesmeyen = []

for root, dirs, files in os.walk(WEB):
    dirs[:] = [d for d in dirs if d not in ('.git', '.wrangler', 'node_modules', '.claude', 'tools')]
    for fn in sorted(files):
        if not fn.endswith('.html') or fn in SKIP:
            continue
        p = os.path.join(root, fn)
        rel = os.path.relpath(p, WEB)
        s = open(p, encoding='utf-8').read()
        if '<head' not in s:
            continue
        orig = s

        # a) marka kilidi
        s, n = BLOK.subn(lambda m: m.group(1) + '\n    ' + MARKA + '\n  ' + m.group(3), s)
        kalan = [m.group(0) for m in HERHANGI.finditer(s) if 'brand-mark' not in m.group(0)]
        if kalan:
            eslesmeyen.append((rel, kalan[0][:120]))

        # b) favicon + manifest (her zaman tazele)
        s = IKON_RE.sub('', s)
        s = ESKI_IKON_RE.sub('', s)
        s = re.sub(r'(\s*</head>)', '\n  ' + IKON + r'\1', s, count=1)

        if s != orig:
            degisen += 1
            if not check:
                open(p, 'w', encoding='utf-8').write(s)

if eslesmeyen:
    print('!! beklenmedik nav-logo bloğu (%d dosya) — ELLE BAK:' % len(eslesmeyen))
    for rel, ornek in eslesmeyen[:6]:
        print('   %s\n     %s' % (rel, ornek))
    sys.exit(1)

print(('kontrol: %d sayfa güncel değil' if check else 'marka işlendi: %d sayfa') % degisen)
