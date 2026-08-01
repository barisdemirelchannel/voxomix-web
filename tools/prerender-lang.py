#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /es/ /fr/ /de/ statik sayfalarını (index + hakkimizda) /en/ tabanından üretir.
# Yapar: link öneki /en/ -> /LANG/ (yasal sayfalar hariç, onlar İngilizce /en/'de kalır),
#        head meta + hreflang(5 dil) + og/twitter + html lang değişimi,
#        gövdedeki data-i18n / data-i18n-html metinlerini hedef dilden bake.
# Kullanım: python3 tools/prerender-lang.py es fr de   (repo kökünden)
import re, html, os, sys

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = sys.argv[1:] or ['es', 'fr', 'de']
ALL = ['tr', 'en', 'es', 'fr', 'de']
LOCALE = {'tr': 'tr_TR', 'en': 'en_US', 'es': 'es_ES', 'fr': 'fr_FR', 'de': 'de_DE'}
# Yasal sayfa slug'ları — Türkçe dışında hep İngilizce (/en/) gösterilir.
LEGAL = ['kullanim-sartlari', 'gizlilik', 'mesafeli-satis', 'teslimat-iade']

# ---- i18n.js'ten bir dilin sözlüğünü oku ----
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

# ---- Sayfa başına, dil başına head meta ----
META = {
  'index': {
    'es': {
      'title': 'VoxoMix — Separa cualquier canción en pistas, acordes, BPM y letra',
      'desc': 'Separa cualquier canción en pistas de voz, batería, bajo e instrumentos con VoxoMix. Separación con IA, detección de acordes y BPM, letra y cambio de tono. Gratis en Mac y Windows.',
      'ogt': 'VoxoMix — Cada capa de una canción, en una sola app',
      'ogd': 'Separa cualquier canción en pistas de voz, batería, bajo e instrumentos con IA. Acordes, BPM, letra y cambio de tono. Empieza gratis en Mac y Windows.',
    },
    'fr': {
      'title': "VoxoMix — Séparez toute chanson en pistes, accords, BPM et paroles",
      'desc': "Séparez toute chanson en pistes de voix, batterie, basse et instruments avec VoxoMix. Séparation par IA, détection des accords et du BPM, paroles, changement de hauteur. Gratuit sur Mac et Windows.",
      'ogt': "VoxoMix — Chaque couche d'une chanson, dans une seule app",
      'ogd': "Séparez toute chanson en pistes de voix, batterie, basse et instruments avec l'IA. Accords, BPM, paroles et hauteur. Commencez gratuitement sur Mac et Windows.",
    },
    'de': {
      'title': 'VoxoMix — Jeden Song in Stems, Akkorde, BPM & Songtext trennen',
      'desc': 'Trenne jeden Song mit VoxoMix in Gesang-, Schlagzeug-, Bass- und Instrumenten-Stems. KI-Stem-Trennung, Akkord- & BPM-Erkennung, Songtext und Tonhöhe. Kostenlos auf Mac & Windows.',
      'ogt': 'VoxoMix — Jede Ebene eines Songs, in einer App',
      'ogd': 'Trenne jeden Song mit KI in Gesang-, Schlagzeug-, Bass- und Instrumenten-Stems. Akkorde, BPM, Songtext und Tonhöhe. Kostenlos starten auf Mac & Windows.',
    },
  },
  'hakkimizda': {
    'es': {
      'title': 'Nosotros — VoxoMix',
      'desc': 'La historia y la misión de VoxoMix: una app de escritorio con IA para músicos — separación de pistas, detección de acordes y letra.',
      'ogt': 'Nosotros — VoxoMix', 'ogd': 'La historia y la misión de VoxoMix.',
    },
    'fr': {
      'title': 'À propos — VoxoMix',
      'desc': "L'histoire et la mission de VoxoMix : une app de bureau IA pour musiciens — séparation de pistes, détection des accords et des paroles.",
      'ogt': 'À propos — VoxoMix', 'ogd': "L'histoire et la mission de VoxoMix.",
    },
    'de': {
      'title': 'Über uns — VoxoMix',
      'desc': 'Die Geschichte und Mission von VoxoMix: eine KI-Desktop-App für Musiker — Stem-Trennung, Akkord- und Songtext-Erkennung.',
      'ogt': 'Über uns — VoxoMix', 'ogd': 'Die Geschichte und Mission von VoxoMix.',
    },
  },
}

def esc_attr(s):  # meta content attribute güvenli
    return s.replace('&', '&amp;').replace('"', '&quot;')

def bake_body(page, d):
    def rh(m):
        return (m.group(1) + d[m.group(3)] + m.group(5)) if m.group(3) in d else m.group(0)
    page, nh = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n-html="([^"]+)"[^>]*>)(.*?)(</\2>)', rh, page, flags=re.S)
    def rt(m):
        return (m.group(1) + html.escape(d[m.group(3)], quote=False) + m.group(5)) if m.group(3) in d else m.group(0)
    page, nt = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)([^<]*)(</\2>)', rt, page)
    return page, nt, nh

def hreflang_block(suffix):  # suffix: '' (index) veya 'hakkimizda'
    def href(l):
        base = 'https://voxomix.com/'
        return base + ('' if l == 'tr' else l + '/') + suffix
    rows = [f'  <link rel="alternate" hreflang="{l}" href="{href(l)}">' for l in ALL]
    rows.append(f'  <link rel="alternate" hreflang="x-default" href="{href("tr")}">')
    return "\n".join(rows)

def build(page_key, src_name, out_name, suffix, lang):
    d = load_dict(lang)
    m = META[page_key][lang]
    p = open(f"{WEB}/en/{src_name}", encoding="utf-8").read()

    # 1) Link öneki /en/ -> /LANG/  (sonra yasal olanları /en/'e geri al)
    p = p.replace('/en/', f'/{lang}/')
    for slug in LEGAL:
        p = p.replace(f'/{lang}/{slug}', f'/en/{slug}')

    # 2) html lang
    p = re.sub(r'<html lang="en">', f'<html lang="{lang}">', p, count=1)

    # 3) head meta (title/desc/og/twitter/locale)
    p = re.sub(r'<title>.*?</title>', f'<title>{esc_attr(m["title"])}</title>', p, count=1, flags=re.S)
    p = re.sub(r'(<meta name="description" content=")[^"]*(">)', lambda x: x.group(1) + esc_attr(m['desc']) + x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:title" content=")[^"]*(">)', lambda x: x.group(1) + esc_attr(m['ogt']) + x.group(2), p, count=1)
    p = re.sub(r'(<meta name="twitter:title" content=")[^"]*(">)', lambda x: x.group(1) + esc_attr(m['ogt']) + x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:description" content=")[^"]*(">)', lambda x: x.group(1) + esc_attr(m['ogd']) + x.group(2), p, count=1)
    p = re.sub(r'(<meta name="twitter:description" content=")[^"]*(">)', lambda x: x.group(1) + esc_attr(m['ogd']) + x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:locale" content=")[^"]*(">)', lambda x: x.group(1) + LOCALE[lang] + x.group(2), p, count=1)

    # 4) hreflang bloğu -> 5 dil + x-default
    p = re.sub(r'(?:\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+">)+',
               "\n" + hreflang_block(suffix), p, count=1)

    # 5) gövde bake
    p, nt, nh = bake_body(p, d)

    os.makedirs(f"{WEB}/{lang}", exist_ok=True)
    open(f"{WEB}/{lang}/{out_name}", "w", encoding="utf-8").write(p)
    print(f"  {lang}/{out_name}: {nt} metin + {nh} html bake")

for lang in LANGS:
    if lang not in META['index']:
        print(f"! {lang} için META tanımı yok, atlandı"); continue
    print(f"[{lang}]")
    build('index', 'index.html', 'index.html', '', lang)
    build('hakkimizda', 'hakkimizda.html', 'hakkimizda.html', 'hakkimizda', lang)
print("bitti.")
