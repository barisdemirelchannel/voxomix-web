#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# sitemap.xml'i tüm dillerle (tr/en/es/fr/de/it) yeniden üretir.
import os
WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = 'https://voxomix.com'
TODAY = '2026-10-19'

# post-key -> {lang: slug}
POSTS = {
  'sarkinin_piyano_akorlari': {'tr':'sarkinin-piyano-akorlarini-bulma', 'en':'how-to-find-the-piano-chords-of-a-song', 'es':'como-sacar-los-acordes-de-piano-de-una-cancion', 'fr':'trouver-les-accords-piano-dune-chanson', 'de':'klavierakkorde-eines-songs-herausfinden', 'it':'trovare-gli-accordi-per-pianoforte-di-una-canzone'},
  'bpm': {'tr':'sarkinin-bpmini-bulma', 'en':'how-to-find-the-bpm-of-a-song', 'es':'como-saber-el-bpm-de-una-cancion', 'fr':'trouver-le-bpm-dune-chanson', 'de':'bpm-eines-songs-herausfinden', 'it':'trovare-i-bpm-di-una-canzone'},
  'karaoke': {'tr':'sarkiyi-karaoke-yapma', 'en':'how-to-make-a-karaoke-version-of-any-song', 'es':'como-hacer-un-karaoke-de-cualquier-cancion', 'fr':'faire-une-version-karaoke-dune-chanson', 'de':'karaoke-version-eines-songs-erstellen', 'it':'fare-una-base-karaoke-da-una-canzone'},
  'key':     {'tr':'sarkinin-tonunu-degistirme','en':'how-to-change-the-key-of-a-song','es':'como-cambiar-el-tono-de-una-cancion','fr':'changer-la-tonalite-dune-chanson','de':'tonart-eines-songs-aendern','it':'cambiare-la-tonalita-di-una-canzone'},
  'vocals':  {'tr':'sarkidan-vokal-ayirma','en':'how-to-remove-vocals-from-a-song','es':'como-quitar-la-voz-de-una-cancion','fr':'supprimer-la-voix-dune-chanson','de':'gesang-aus-einem-song-entfernen','it':'rimuovere-la-voce-da-una-canzone'},
  'chords':  {'tr':'sarkinin-akorlarini-bulma','en':'how-to-find-the-chords-of-a-song','es':'como-encontrar-los-acordes-de-una-cancion','fr':'trouver-les-accords-dune-chanson','de':'akkorde-eines-songs-herausfinden','it':'trovare-gli-accordi-di-una-canzone'},
  'instrument': {'tr':'sarkidan-enstruman-ayirma','en':'how-to-remove-an-instrument-from-a-song','es':'como-quitar-un-instrumento-de-una-cancion','fr':'supprimer-un-instrument-dune-chanson','de':'instrument-aus-einem-song-entfernen','it':'rimuovere-uno-strumento-da-una-canzone'},
  'pillar':  {'tr':'sarkiyla-pratik-yapma-rehberi','en':'practice-any-song-complete-guide','es':'como-practicar-con-cualquier-cancion','fr':'travailler-nimporte-quelle-chanson-guide','de':'mit-jedem-song-zu-hause-ueben','it':'esercitarsi-con-qualsiasi-canzone-guida'},
  'slow':    {'tr':'sarki-hizini-dusurme-ses-bozulmadan','en':'slow-down-song-without-changing-pitch','es':'ralentizar-cancion-sin-cambiar-el-tono','fr':'ralentir-une-chanson-sans-changer-la-hauteur','de':'song-verlangsamen-ohne-tonhoehe','it':'rallentare-una-canzone-senza-cambiare-tono'},
  'offline': {'tr':'cevrimdisi-stem-ayirma','en':'offline-stem-separation','es':'separacion-de-pistas-sin-conexion','fr':'separation-de-pistes-hors-ligne','de':'offline-stem-trennung','it':'separazione-tracce-offline'},
  'howto':   {'tr':'voxomix-nasil-kullanilir','en':'how-to-use-voxomix','es':'como-usar-voxomix','fr':'comment-utiliser-voxomix','de':'voxomix-verwenden','it':'come-usare-voxomix'},
}
POST_MOD = {'sarkinin_piyano_akorlari':'2026-10-19','bpm':'2026-10-20','karaoke':'2026-10-14','key':'2026-09-16','vocals':'2026-09-07','chords':'2026-09-06','instrument':'2026-09-06','pillar':'2026-07-17','slow':'2026-07-17','offline':'2026-07-17','howto':'2026-09-07'}
POST_PRIO = {'sarkinin_piyano_akorlari':'0.8','bpm':'0.8','karaoke':'0.8','key':'0.8','vocals':'0.8','chords':'0.8','instrument':'0.8','pillar':'0.9','slow':'0.8','offline':'0.8','howto':'0.8'}

def base(lang): return B + ('' if lang=='tr' else '/'+lang)

rows = []
def U(loc, mod, freq, prio):
    rows.append(f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{mod}</lastmod>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>")

# Homepages
for lang in ['tr','en','es','fr','de','it']:
    mod = '2026-07-05' if lang in ('tr','en') else TODAY
    prio = '1.0' if lang=='tr' else '0.9'
    U(base(lang)+'/', mod, 'weekly', prio)
# About
for lang in ['tr','en','es','fr','de','it']:
    mod = '2026-07-05' if lang in ('tr','en') else TODAY
    U(base(lang)+'/hakkimizda', mod, 'monthly', '0.6')
# Blog indexes
for lang in ['tr','en','es','fr','de','it']:
    mod = '2026-09-06'
    U(base(lang)+'/blog/', mod, 'weekly', '0.7')
# Blog posts
for key, langs in POSTS.items():
    for lang in ['tr','en','es','fr','de','it']:
        mod = POST_MOD[key] if (lang in ('tr','en') or key in ('sarkinin_piyano_akorlari','bpm','karaoke','key','vocals','chords','instrument','howto')) else TODAY
        U(f"{base(lang)}/blog/{langs[lang]}", mod, 'monthly', POST_PRIO[key])
# Legal (tr + en only)
for slug in ['kullanim-sartlari','gizlilik','mesafeli-satis','teslimat-iade']:
    U(f"{B}/{slug}", '2026-07-05', 'yearly', '0.3')
    U(f"{B}/en/{slug}", '2026-07-05', 'yearly', '0.3')

out = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"
open(f"{WEB}/sitemap.xml","w",encoding="utf-8").write(out)
print(f"✓ sitemap.xml: {len(rows)} URL")
