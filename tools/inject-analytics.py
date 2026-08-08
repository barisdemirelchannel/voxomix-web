#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# assets/analytics.js etiketini her HTML sayfasının <head>'ine ekler.
#
# NEDEN AYRI BİR ARAÇ: sayfaların bir kısmı üretiliyor (prerender-en.py,
# prerender-lang.py, build-blog-index.py). Etiketi elle eklersen ilk yeniden
# üretimde kaybolur. Bu betik idempotenttir → her üretimden sonra tekrar çalıştır:
#
#   python3 tools/prerender-lang.py es fr de
#   python3 tools/inject-analytics.py
#
# Kullanım: python3 tools/inject-analytics.py [--check]
#   --check : hiçbir dosyayı değiştirmez, eksik olanları listeler (CI/doğrulama için)
import os, re, sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = 1  # analytics.js değişince artır → tarayıcı önbelleği tazelensin
TAG = '<script defer src="/assets/analytics.js?v=%d"></script>' % VERSION
MARKER = re.compile(r'<script[^>]+src="/assets/analytics\.js[^"]*"[^>]*>\s*</script>\s*')

# Google site doğrulama dosyası bir sayfa değil, tek satırlık token — dokunma.
SKIP = {'google3b843533d74b7e6f.html'}

check_only = '--check' in sys.argv
added, updated, ok, missing = [], [], 0, []

for root, dirs, files in os.walk(WEB):
    dirs[:] = [d for d in dirs if d not in ('.git', '.wrangler', 'node_modules', '.claude')]
    for name in sorted(files):
        if not name.endswith('.html') or name in SKIP:
            continue
        path = os.path.join(root, name)
        rel = os.path.relpath(path, WEB)
        src = open(path, encoding='utf-8').read()

        found = MARKER.search(src)
        if found and found.group(0).strip() == TAG:
            ok += 1
            continue
        if check_only:
            missing.append(rel)
            continue

        if found:                       # sürüm eskiyse etiketi tazele
            out = MARKER.sub(TAG + '\n', src, count=1)
            updated.append(rel)
        else:
            if '</head>' not in src:
                print('!! <head> yok, atlandi: %s' % rel)
                continue
            out = src.replace('</head>', '  ' + TAG + '\n</head>', 1)
            added.append(rel)
        open(path, 'w', encoding='utf-8').write(out)

if check_only:
    if missing:
        print('EKSIK (%d): %s' % (len(missing), ', '.join(missing)))
        sys.exit(1)
    print('OK — %d sayfanin hepsinde guncel etiket var.' % ok)
else:
    print('eklendi: %d · guncellendi: %d · zaten guncel: %d' % (len(added), len(updated), ok))
    for r in added:
        print('  + %s' % r)
    for r in updated:
        print('  ~ %s' % r)
