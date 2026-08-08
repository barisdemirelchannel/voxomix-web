#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# İndirme sayılarını KV'den okur ve gün/platform kırılımıyla yazdırır.
#
# Worker her indirme için AYRI bir anahtar yazıyor (dl:GUN:os:surum:uuid), o
# yüzden sayım = anahtarları saymak. Bu bilinçli: tek anahtarı oku-artır-yaz
# yapan ilk sürüm KV'nin bayat okuması yüzünden eksik sayıyordu (ölçüldü).
#
# Kullanım:
#   python3 tools/download-stats.py            # son 30 gün
#   python3 tools/download-stats.py 7          # son 7 gün
import json, subprocess, sys, os
from collections import defaultdict
from datetime import date, timedelta

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30

out = subprocess.run(
    ['npx', '--yes', 'wrangler', 'kv', 'key', 'list', '--binding', 'DOWNLOADS', '--remote'],
    cwd=WEB, capture_output=True, text=True,
    env={**os.environ, 'CLOUDFLARE_ACCOUNT_ID': os.environ.get('CLOUDFLARE_ACCOUNT_ID', 'f1ee988b1da98919fe8952b00577090b')},
)
start = out.stdout.find('[')
if start < 0:
    print('KV listesi okunamadi:\n' + (out.stderr or out.stdout))
    sys.exit(1)

keys = [k['name'] for k in json.loads(out.stdout[start:])]

# dl:2026-08-09:mac:1.3.2:<uuid>
per_day = defaultdict(lambda: defaultdict(int))
per_version = defaultdict(int)
for k in keys:
    parts = k.split(':')
    if len(parts) < 5 or parts[0] != 'dl':
        continue
    per_day[parts[1]][parts[2]] += 1
    per_version[parts[3]] += 1

cutoff = (date.today() - timedelta(days=DAYS - 1)).isoformat()
days = sorted([d for d in per_day if d >= cutoff])

print(f'\nVoxoMix indirmeleri — son {DAYS} gun  (kaynak: sunucu tarafi, reklam engelleyiciden etkilenmez)\n')
print(f'{"Gun":<12}{"Mac":>7}{"Windows":>10}{"Toplam":>9}')
print('-' * 38)
tm = tw = 0
for d in days:
    m, w = per_day[d].get('mac', 0), per_day[d].get('win', 0)
    tm += m; tw += w
    print(f'{d:<12}{m:>7}{w:>10}{m + w:>9}')
print('-' * 38)
print(f'{"TOPLAM":<12}{tm:>7}{tw:>10}{tm + tw:>9}')
if per_version:
    print('\nSurume gore: ' + ' · '.join(f'{v}: {n}' for v, n in sorted(per_version.items())))
print()
