# -*- coding: utf-8 -*-
"""Yasal sayfaları en/ şablonundan es/fr/de/it'e üretir.

NEDEN VAR: de/fr/es/it ziyaretçisi İngilizce sözleşmeye yönleniyordu. AB'de
sözleşme öncesi bilgilendirmenin teklifin dilinde olması aranıyor (Fransa'da
Toubon yasası, İtalya'da tüketici mevzuatı bunu açıkça istiyor).

KAYNAK: çeviri gövdeleri tools/legal-i18n/<dil>/<slug>.html içinde durur;
şablon (nav, footer, head iskeleti) her zaman en/<slug>.html'dir. Yani
en/ sayfasını elle değiştirirsen BU ARACI TEKRAR ÇALIŞTIR.

KULLANIM: python3 tools/build-legal-lang.py [dil...]   (varsayılan: hepsi)
"""
import os, re, sys, html

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL = ['tr', 'en', 'es', 'fr', 'de', 'it']
LANGS = sys.argv[1:] or ['es', 'fr', 'de', 'it']
LOCALE = {'tr': 'tr_TR', 'en': 'en_US', 'es': 'es_ES', 'fr': 'fr_FR', 'de': 'de_DE', 'it': 'it_IT'}
SLUGS = ['gizlilik', 'kullanim-sartlari', 'mesafeli-satis', 'teslimat-iade']

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

def bake_body(page, d):
    def rh(m):
        return (m.group(1) + d[m.group(3)] + m.group(5)) if m.group(3) in d else m.group(0)
    page, nh = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n-html="([^"]+)"[^>]*>)(.*?)(</\2>)', rh, page, flags=re.S)
    def rt(m):
        return (m.group(1) + html.escape(d[m.group(3)], quote=False) + m.group(5)) if m.group(3) in d else m.group(0)
    page, nt = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)([^<]*)(</\2>)', rt, page)
    return page, nt, nh

def hreflang_block(slug):
    def href(l):
        return 'https://voxomix.com/' + ('' if l == 'tr' else l + '/') + slug
    rows = [f'  <link rel="alternate" hreflang="{l}" href="{href(l)}">' for l in ALL]
    rows.append(f'  <link rel="alternate" hreflang="x-default" href="{href("tr")}">')
    return "\n".join(rows)

def esc_attr(s):
    return s.replace('&', '&amp;').replace('"', '&quot;')

FIELD = re.compile(r'<!--(TITLE|DESC|H1|SUB|BODY)-->(.*?)<!--/\1-->', re.S)

def read_fragment(lang, slug):
    p = f"{WEB}/tools/legal-i18n/{lang}/{slug}.html"
    if not os.path.exists(p):
        return None
    raw = open(p, encoding='utf-8').read()
    f = {m.group(1): m.group(2).strip('\n') for m in FIELD.finditer(raw)}
    missing = [k for k in ('TITLE', 'DESC', 'H1', 'SUB', 'BODY') if k not in f]
    if missing:
        raise SystemExit(f"! {lang}/{slug}: eksik alan(lar) {missing}")
    for k in ('TITLE', 'DESC', 'H1', 'SUB'):
        f[k] = f[k].strip()
    return f

def build(lang, slug):
    frag = read_fragment(lang, slug)
    if frag is None:
        print(f"  {lang}/{slug}: çeviri yok, atlandı"); return False
    p = open(f"{WEB}/en/{slug}.html", encoding='utf-8').read()

    # 1) /en/ önekleri -> /LANG/ (yasal sayfalar artık kendi dilinde)
    p = p.replace('/en/', f'/{lang}/')
    # 2) html lang
    p = re.sub(r'<html lang="en">', f'<html lang="{lang}">', p, count=1)
    # 3) head meta
    p = re.sub(r'<title>.*?</title>', '<title>' + esc_attr(frag['TITLE']) + '</title>', p, count=1, flags=re.S)
    for pat in [r'(<meta name="description" content=")[^"]*(">)',
                r'(<meta property="og:description" content=")[^"]*(">)',
                r'(<meta name="twitter:description" content=")[^"]*(">)']:
        p = re.sub(pat, lambda x: x.group(1) + esc_attr(frag['DESC']) + x.group(2), p, count=1)
    for pat in [r'(<meta property="og:title" content=")[^"]*(">)',
                r'(<meta name="twitter:title" content=")[^"]*(">)']:
        p = re.sub(pat, lambda x: x.group(1) + esc_attr(frag['TITLE']) + x.group(2), p, count=1)
    p = re.sub(r'(<meta property="og:locale" content=")[^"]*(">)',
               lambda x: x.group(1) + LOCALE[lang] + x.group(2), p, count=1)
    # 4) canonical + hreflang (7 satır)
    p = re.sub(r'(<link rel="canonical" href=")[^"]*(">)',
               lambda x: x.group(1) + f'https://voxomix.com/{lang}/{slug}' + x.group(2), p, count=1)
    p = re.sub(r'(?:\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+">)+',
               "\n" + hreflang_block(slug), p, count=1)
    # 5) başlık + alt başlık
    p = re.sub(r'(<div class="page-header">\s*<h1>).*?(</h1>\s*<p>).*?(</p>)',
               lambda x: x.group(1) + frag['H1'] + x.group(2) + frag['SUB'] + x.group(3),
               p, count=1, flags=re.S)
    # 6) gövde
    new_body = '<div class="legal-content">\n' + frag['BODY'] + '\n  </div>'
    p, n = re.subn(r'<div class="legal-content">.*?\n  </div>', lambda m: new_body, p, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"! {lang}/{slug}: legal-content bloğu bulunamadı")
    # 7) nav/footer sözlük bake
    p, nt, nh = bake_body(p, load_dict(lang))

    os.makedirs(f"{WEB}/{lang}", exist_ok=True)
    open(f"{WEB}/{lang}/{slug}.html", 'w', encoding='utf-8').write(p)
    print(f"  {lang}/{slug}.html: {nt} metin bake")
    return True

def fix_hreflang_tr_en():
    """TR ve EN yasal sayfalarının hreflang setini 7 satıra çıkarır."""
    for slug in SLUGS:
        for f in (f"{WEB}/{slug}.html", f"{WEB}/en/{slug}.html"):
            s = open(f, encoding='utf-8').read()
            s2 = re.sub(r'(?:\s*<link rel="alternate" hreflang="[^"]+" href="[^"]+">)+',
                        "\n" + hreflang_block(slug), s, count=1)
            if s2 != s:
                open(f, 'w', encoding='utf-8').write(s2)
                print(f"  hreflang güncellendi: {os.path.relpath(f, WEB)}")

made = 0
for lang in LANGS:
    print(f"[{lang}]")
    for slug in SLUGS:
        if build(lang, slug): made += 1
fix_hreflang_tr_en()
print(f"bitti — {made} sayfa üretildi.")
