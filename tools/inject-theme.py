#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tema altyapısını her HTML sayfasına ekler: <head> içine boya-öncesi betik,
nav'a tema düğmesi.

NEDEN AYRI BİR ARAÇ: sayfaların çoğu üretiliyor (prerender-lang.py,
build-legal-lang.py, build-blog-index.py). Elle eklersen ilk yeniden üretimde
kaybolur. Bu betik idempotenttir → her üretimden sonra çalıştır:

  python3 tools/prerender-lang.py es fr de it
  python3 tools/build-legal-lang.py
  python3 tools/inject-theme.py

Kullanım: python3 tools/inject-theme.py [--check]
"""
import os, re, sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'google3b843533d74b7e6f.html'}

# Boya öncesi çalışmalı: aksi hâlde koyu tercih edenlerde bir kare beyaz parlar.
# theme-color meta'sı da burada eşitlenir (tarayıcı çubuğu rengi).
HEAD = (
  '<script>/*tema*/(function(){var r=document.documentElement,D="dark",K="voxomix_theme";'
  'function paint(d){var m=document.querySelector(\'meta[name="theme-color"]\');'
  'if(m)m.content=d?"#08080a":"#faf8f4";}'
  'try{if(localStorage.getItem(K)===D){r.setAttribute("data-theme",D);}}catch(e){}'
  'paint(r.getAttribute("data-theme")===D);'
  # Devredilen dinleyici: düğme henüz ayrıştırılmamışken de bağlanabilsin diye
  # document üzerinde duruyor; böylece ayrı bir dosya ve sürüm artırımı gerekmiyor.
  'document.addEventListener("click",function(e){'
  'var b=e.target&&e.target.closest?e.target.closest("#theme-toggle"):null;if(!b)return;'
  'var dark=r.getAttribute("data-theme")===D;'
  'if(dark){r.removeAttribute("data-theme");}else{r.setAttribute("data-theme",D);}'
  'try{localStorage.setItem(K,dark?"light":D);}catch(x){}paint(!dark);});})();</script>'
)
HEAD_RE = re.compile(r'\s*<script>/\*tema\*/.*?</script>', re.S)

# İki simge de DOM'da; hangisinin görüneceğine CSS karar verir.
BTN = (
  '  <button class="theme-toggle" id="theme-toggle" type="button" aria-label="Tema" data-i18n-aria="nav.theme">\n'
  '    <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>\n'
  '    <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>\n'
  '  </button>\n'
)
BTN_RE = re.compile(r'[ \t]*<button class="theme-toggle".*?</button>\n', re.S)
# Düğme nav'ın içinde, CTA bağlantısından hemen önce durur.
CTA_RE = re.compile(r'([ \t]*<a [^>]*class="nav-cta[^"]*")')

check = '--check' in sys.argv
added_head = added_btn = 0
missing = []

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

        # 1) head betiği — her zaman tazele (sürüm değişebilir)
        s = HEAD_RE.sub('', s)
        s = re.sub(r'(<head[^>]*>)', lambda m: m.group(1) + '\n  ' + HEAD, s, count=1)

        # 2) nav düğmesi — varsa çıkar, CTA'dan önce yeniden koy
        s = BTN_RE.sub('', s)
        if CTA_RE.search(s):
            s = CTA_RE.sub(lambda m: BTN + m.group(1), s, count=1)
        else:
            missing.append(rel)

        if s != orig:
            if check:
                print('  eksik/eski:', rel)
            else:
                open(p, 'w', encoding='utf-8').write(s)
            added_head += 1

if missing:
    print('! nav-cta bulunamadı (düğme eklenemedi): %d dosya' % len(missing))
    for m in missing[:5]:
        print('   -', m)
print(('kontrol: %d sayfa güncel değil' if check else 'tema enjekte edildi: %d sayfa') % added_head)
