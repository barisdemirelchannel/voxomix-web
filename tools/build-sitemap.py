#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# sitemap.xml'i tüm dillerle (tr/en/es/fr/de) yeniden üretir.
import os
WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = 'https://voxomix.com'
TODAY = '2026-08-02'

# post-key -> {lang: slug}
POSTS = {
  'pillar':  {'tr':'sarkiyla-pratik-yapma-rehberi','en':'practice-any-song-complete-guide','es':'como-practicar-con-cualquier-cancion','fr':'travailler-nimporte-quelle-chanson-guide','de':'mit-jedem-song-zu-hause-ueben'},
  'slow':    {'tr':'sarki-hizini-dusurme-ses-bozulmadan','en':'slow-down-song-without-changing-pitch','es':'ralentizar-cancion-sin-cambiar-el-tono','fr':'ralentir-une-chanson-sans-changer-la-hauteur','de':'song-verlangsamen-ohne-tonhoehe'},
  'offline': {'tr':'cevrimdisi-stem-ayirma','en':'offline-stem-separation','es':'separacion-de-pistas-sin-conexion','fr':'separation-de-pistes-hors-ligne','de':'offline-stem-trennung'},
  'howto':   {'tr':'voxomix-nasil-kullanilir','en':'how-to-use-voxomix','es':'como-usar-voxomix','fr':'comment-utiliser-voxomix','de':'voxomix-verwenden'},
}
POST_MOD = {'pillar':'2026-07-17','slow':'2026-07-17','offline':'2026-07-17','howto':'2026-07-13'}
POST_PRIO = {'pillar':'0.9','slow':'0.8','offline':'0.8','howto':'0.8'}

def base(lang): return B + ('' if lang=='tr' else '/'+lang)

rows = []
def U(loc, mod, freq, prio):
    rows.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>")

# Homepages
for lang in ['tr','en','es','fr','de']:
    mod = '2026-07-05' if lang in ('tr','en') else TODAY
    prio = '1.0' if lang=='tr' else '0.9'
    U(base(lang)+'/', mod, 'weekly', prio)
# About
for lang in ['tr','en','es','fr','de']:
    mod = '2026-07-05' if lang in ('tr','en') else TODAY
    U(base(lang)+'/hakkimizda', mod, 'monthly', '0.6')
# Blog indexes
for lang in ['tr','en','es','fr','de']:
    mod = '2026-08-02'
    U(base(lang)+'/blog/', mod, 'weekly', '0.7')
# Blog posts
for key, langs in POSTS.items():
    for lang in ['tr','en','es','fr','de']:
        mod = POST_MOD[key] if lang in ('tr','en') else TODAY
        U(f"{base(lang)}/blog/{langs[lang]}", mod, 'monthly', POST_PRIO[key])
# Legal (tr + en only)
for slug in ['kullanim-sartlari','gizlilik','mesafeli-satis','teslimat-iade']:
    U(f"{B}/{slug}", '2026-07-05', 'yearly', '0.3')
    U(f"{B}/en/{slug}", '2026-07-05', 'yearly', '0.3')

out = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"
open(f"{WEB}/sitemap.xml","w",encoding="utf-8").write(out)
print(f"✓ sitemap.xml: {len(rows)} URL")
