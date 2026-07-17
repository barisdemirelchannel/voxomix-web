#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# /en/index.html gövdesini i18n.js'in `en` sözlüğünden İngilizce'ye bake eder.
# data-i18n attribute'ları korunur (JS idempotent kalır). Head meta'ları elle bakımlı.
# Kullanım: python3 tools/prerender-en.py   (repo kökünden)
import re, html, os
WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lines = open(f"{WEB}/assets/i18n.js", encoding="utf-8").read().split("\n")
en_start = next(i for i,l in enumerate(lines) if re.match(r'\s*en:\s*\{', l))
en = {}
val_re = re.compile(r"^\s*'([a-zA-Z0-9_.]+)'\s*:\s*'((?:\\.|[^'\\])*)'\s*,?\s*$")
for l in lines[en_start+1:]:
    if re.match(r'^\s*\}\s*$', l): break
    m = val_re.match(l)
    if m:
        en[m.group(1)] = m.group(2).replace("\\'","'").replace('\\"','"').replace("\\\\","\\")
page = open(f"{WEB}/en/index.html", encoding="utf-8").read()
def repl_html(m):
    return (m.group(1)+en[m.group(3)]+m.group(5)) if m.group(3) in en else m.group(0)
page,nh = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n-html="([^"]+)"[^>]*>)(.*?)(</\2>)', repl_html, page, flags=re.S)
def repl_text(m):
    return (m.group(1)+html.escape(en[m.group(3)],quote=False)+m.group(5)) if m.group(3) in en else m.group(0)
page,nt = re.subn(r'(<([a-zA-Z0-9]+)\b[^>]*\bdata-i18n="([^"]+)"[^>]*>)([^<]*)(</\2>)', repl_text, page)
open(f"{WEB}/en/index.html","w",encoding="utf-8").write(page)
print(f"bake: {nt} metin + {nh} html öğesi")
