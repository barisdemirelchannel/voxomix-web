#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /es/ /fr/ /de/ blog/index.html sayfalarını en/blog/index.html tabanından üretir.
# Kart başlık+açıklamalarını çevrilmiş yazı dosyalarından okur; nav/footer/chrome
# metnini per-lang sözlükten baker. Kullanım: python3 tools/build-blog-index.py es fr de
import re, html, os, sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = sys.argv[1:] or ['es', 'fr', 'de']
ALL = ['tr', 'en', 'es', 'fr', 'de']
LOCALE = {'es': 'es_ES', 'fr': 'fr_FR', 'de': 'de_DE'}

# Kart sırası = EN index sırası. (topic, slug-per-lang, category-key, read, date-per-lang)
POSTS = [
    {'key': 'pillar',  'read': 12,
     'slug': {'es': 'como-practicar-con-cualquier-cancion', 'fr': 'travailler-nimporte-quelle-chanson-guide', 'de': 'mit-jedem-song-zu-hause-ueben'},
     'date': {'es': '3 de agosto de 2026', 'fr': '3 août 2026', 'de': '3. August 2026'}},
    {'key': 'slow',    'read': 6,
     'slug': {'es': 'ralentizar-cancion-sin-cambiar-el-tono', 'fr': 'ralentir-une-chanson-sans-changer-la-hauteur', 'de': 'song-verlangsamen-ohne-tonhoehe'},
     'date': {'es': '27 de julio de 2026', 'fr': '27 juillet 2026', 'de': '27. Juli 2026'}},
    {'key': 'offline', 'read': 6,
     'slug': {'es': 'separacion-de-pistas-sin-conexion', 'fr': 'separation-de-pistes-hors-ligne', 'de': 'offline-stem-trennung'},
     'date': {'es': '20 de julio de 2026', 'fr': '20 juillet 2026', 'de': '20. Juli 2026'}},
    {'key': 'howto',   'read': 8,
     'slug': {'es': 'como-usar-voxomix', 'fr': 'comment-utiliser-voxomix', 'de': 'voxomix-verwenden'},
     'date': {'es': '13 de julio de 2026', 'fr': '13 juillet 2026', 'de': '13. Juli 2026'}},
]

# category-key -> per-lang label
CAT = {
    'pillar':  {'es': 'Guía completa', 'fr': 'Guide complet', 'de': 'Kompletter Guide'},
    'slow':    {'es': 'Guía', 'fr': 'Guide', 'de': 'Guide'},
    'offline': {'es': 'Comparativa', 'fr': 'Comparatif', 'de': 'Vergleich'},
    'howto':   {'es': 'Guía', 'fr': 'Guide', 'de': 'Guide'},
}

CHROME = {
    'es': {
        'title': 'Blog de VoxoMix — Guías y consejos',
        'desc': 'El blog de VoxoMix: guías, consejos y tutoriales sobre separación de pistas, detección de acordes, análisis de BPM y producción musical con IA para Mac.',
        'ogd': 'Guías y consejos sobre separación de pistas, detección de acordes y producción musical con IA para Mac.',
        'schema_desc': 'Guías y consejos sobre separación de pistas, detección de acordes, análisis de BPM y producción musical con IA para Mac.',
        'h1': 'Blog de VoxoMix', 'sub': 'Guías sobre separación de pistas, detección de acordes y producción musical con IA para Mac',
        'read_more': 'Leer más →', 'min': 'min de lectura', 'home': 'Inicio', 'blog': 'Blog',
    },
    'fr': {
        'title': 'Blog VoxoMix — Guides et conseils',
        'desc': "Le blog VoxoMix : guides, conseils et tutoriels sur la séparation de pistes, la détection d'accords, l'analyse du BPM et la production musicale par IA pour Mac.",
        'ogd': "Guides et conseils sur la séparation de pistes, la détection d'accords et la production musicale par IA pour Mac.",
        'schema_desc': "Guides et conseils sur la séparation de pistes, la détection d'accords, l'analyse du BPM et la production musicale par IA pour Mac.",
        'h1': 'Blog VoxoMix', 'sub': "Guides sur la séparation de pistes, la détection d'accords et la production musicale par IA pour Mac",
        'read_more': 'Lire la suite →', 'min': 'min de lecture', 'home': 'Accueil', 'blog': 'Blog',
    },
    'de': {
        'title': 'VoxoMix Blog — Guides & Tipps',
        'desc': 'Der VoxoMix-Blog: Guides, Tipps und Tutorials zu Stem-Trennung, Akkorderkennung, BPM-Analyse und KI-Musikproduktion für den Mac.',
        'ogd': 'Guides und Tipps zu Stem-Trennung, Akkorderkennung und KI-Musikproduktion für den Mac.',
        'schema_desc': 'Guides und Tipps zu Stem-Trennung, Akkorderkennung, BPM-Analyse und KI-Musikproduktion für den Mac.',
        'h1': 'VoxoMix Blog', 'sub': 'Guides zu Stem-Trennung, Akkorderkennung und KI-Musikproduktion für den Mac',
        'read_more': 'Weiterlesen →', 'min': 'Min. Lesezeit', 'home': 'Start', 'blog': 'Blog',
    },
}

# ---- i18n.js sözlüğü (nav/footer data-i18n bake) ----
def load_dict(lang):
    lines = open(f"{WEB}/assets/i18n.js", encoding="utf-8").read().split("\n")
    start = next(i for i, l in enumerate(lines) if re.match(rf'\s*{lang}:\s*\{{', l))
    d = {}
    val_re = re.compile(r"^\s*'([a-zA-Z0-9_.]+)'\s*:\s*'((?:\\.|[^'\\])*)'\s*,?\s*$")
    depth = 0
    for l in lines[start:]:
        depth += l.count("{") - l.count("}")
        m = val_re.match(l)
        if m:
            d[m.group(1)] = (m.group(2).replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\"))
        if depth <= 0 and "}" in l and val_re.match(l) is None and l.strip().startswith("}"):
            break
    return d

def esc_attr(s): return s.replace('&', '&amp;').replace('"', '&quot;')
def esc_txt(s):  return html.escape(s, quote=False)

def post_meta(lang, slug):
    p = open(f"{WEB}/{lang}/blog/{slug}.html", encoding="utf-8").read()
    t = re.search(r'<title>(.*?)</title>', p, re.S).group(1)
    t = re.sub(r'\s*[—-]\s*VoxoMix Blog\s*$', '', t).strip()
    d = re.search(r'<meta name="description" content="(.*?)"', p, re.S).group(1)
    return t, d

def hreflang_block():
    def href(l): return 'https://voxomix.com/' + ('' if l == 'tr' else l + '/') + 'blog/'
    rows = [f'  <link rel="alternate" hreflang="{l}" href="{href(l)}">' for l in ALL]
    rows.append(f'  <link rel="alternate" hreflang="x-default" href="{href("tr")}">')
    return "\n".join(rows)

def bake_body(page, d):
    def rt(m):
        return (m.group(1) + esc_txt(d[m.group(3)]) + m.group(5)) if m.group(3) in d else m.group(0)
    page, _ = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)([^<]*)(</\2>)', rt, page)
    return page

def build(lang):
    c = CHROME[lang]; d = load_dict(lang)
    p = open(f"{WEB}/en/blog/index.html", encoding="utf-8").read()
    LEGAL = ['kullanim-sartlari', 'gizlilik', 'mesafeli-satis', 'teslimat-iade']
    p = p.replace('/en/', f'/{lang}/')
    for s in LEGAL: p = p.replace(f'/{lang}/{s}', f'/en/{s}')
    p = re.sub(r'<html lang="en">', f'<html lang="{lang}">', p, count=1)
    p = re.sub(r'<title>.*?</title>', f'<title>{esc_attr(c["title"])}</title>', p, count=1, flags=re.S)
    p = re.sub(r'(<meta name="description" content=")[^"]*(">)', lambda x: x.group(1)+esc_attr(c['desc'])+x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda x: x.group(1)+esc_attr(c['title'])+x.group(2), p, count=1)
    p = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)', lambda x: x.group(1)+esc_attr(c['title'])+x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', lambda x: x.group(1)+esc_attr(c['ogd'])+x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:locale" content=")[^"]*(">)', lambda x: x.group(1)+LOCALE[lang]+x.group(2), p, count=1)
    # hreflang
    p = re.sub(r'(?:\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+">)+', "\n"+hreflang_block(), p, count=1)
    # JSON-LD Blog + Breadcrumb
    p = p.replace('"description": "Guides and tips on stem separation, chord detection, BPM analysis and AI music production for Mac.",',
                  f'"description": "{esc_attr(c["schema_desc"])}",')
    p = p.replace('"inLanguage": "en"', f'"inLanguage": "{lang}"')
    p = p.replace('"name": "Home", "item": "https://voxomix.com/'+lang+'/"',
                  f'"name": "{c["home"]}", "item": "https://voxomix.com/{lang}/"')
    # page-header
    p = re.sub(r'(<div class="page-header">\s*<h1>).*?(</h1>\s*<p>).*?(</p>)',
               lambda m: m.group(1)+esc_txt(c['h1'])+m.group(2)+esc_txt(c['sub'])+m.group(3), p, count=1, flags=re.S)
    # cards
    def card(post):
        t, desc = post_meta(lang, post['slug'][lang])
        return (
            f'    <a class="blog-card" href="/{lang}/blog/{post["slug"][lang]}">\n'
            f'      <span class="cat">{esc_txt(CAT[post["key"]][lang])}</span>\n'
            f'      <h2>{esc_txt(t)}</h2>\n'
            f'      <p>{esc_txt(desc)}</p>\n'
            f'      <div class="meta">{esc_txt(post["date"][lang])} · ~{post["read"]} {esc_txt(c["min"])} · <span class="read">{esc_txt(c["read_more"])}</span></div>\n'
            f'    </a>'
        )
    cards = "\n".join(card(pp) for pp in POSTS)
    p = re.sub(r'<div class="blog-list">.*?</div>\s*(?=</div>\s*<footer)',
               '<div class="blog-list">\n' + cards + '\n  </div>\n', p, count=1, flags=re.S)
    # bake nav/footer data-i18n
    p = bake_body(p, d)
    os.makedirs(f"{WEB}/{lang}/blog", exist_ok=True)
    open(f"{WEB}/{lang}/blog/index.html", "w", encoding="utf-8").write(p)
    print(f"✓ {lang}/blog/index.html")

for lang in LANGS:
    build(lang)
print("bitti.")
