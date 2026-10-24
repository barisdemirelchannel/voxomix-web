# VoxoMix ilk ekran laptop maketi: kullanıcının verdiği MacBook çerçevesine (tools/macbook-cerceve.webp,
# ekranı saydam) uygulama görüntüsünü oturtur → assets/hero-laptop.webp. Çalıştır: python3 tools/hero-laptop.py
from PIL import Image, ImageDraw
import os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'assets', 'app-screenshot.png')
CERCEVE = os.path.join(KOK, 'tools', 'macbook-cerceve.webp')
CIKTI = os.path.join(KOK, 'assets', 'hero-laptop.webp')
# çerçevedeki ekran: beyaz menü çubuğu (y 66–89) + saydam alan (x 261–1743, y 90–976). Menü çubuğu da örtülür.
EX0, EY0, EX1, EY1 = 260, 66, 1744, 978

im = Image.open(KAYNAK).convert('RGBA')
zemin = Image.new('RGBA', im.size, (12, 12, 15, 255)); zemin.alpha_composite(im); im = zemin.convert('RGB')
panel = im.getpixel((200, 960))                       # pencere zemin rengi
X0, X1 = 80, 2144
ust = im.crop((X0, 40, X1, 885))                       # başlık, zaman çizelgesi, Tempo/Vokal/Davul/Bas
alt = im.crop((X0, 1772, X1, 2336))                    # Akor bulucu, Metronom, Ton + Sözler
cubuk = 64                                            # pencere çubuğu (trafik ışıkları)
icerik_h = cubuk + ust.height + 18 + alt.height
EW, EH = EX1 - EX0, EY1 - EY0
W = int(round(icerik_h * EW / EH)); H = icerik_h
ekran = Image.new('RGB', (W, H), panel)
d = ImageDraw.Draw(ekran)
d.rectangle([0, 0, W, cubuk], fill=tuple(max(0, c - 6) for c in panel))
for i, r in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
    cx = 40 + i * 34; d.ellipse([cx - 11, cubuk // 2 - 11, cx + 11, cubuk // 2 + 11], fill=r)
ox = (W - ust.width) // 2
ekran.paste(ust, (ox, cubuk)); ekran.paste(alt, (ox, cubuk + ust.height + 18))
ekran = ekran.resize((EW, EH), Image.LANCZOS).convert('RGBA')
# cam parlaması
par = Image.new('RGBA', ekran.size, (0, 0, 0, 0))
ImageDraw.Draw(par).polygon([(0, 0), (int(EW * .40), 0), (int(EW * .16), EH), (0, EH)], fill=(255, 255, 255, 14))
ekran.alpha_composite(par)

cerceve = Image.open(CERCEVE).convert('RGBA')
son = Image.new('RGBA', cerceve.size, (0, 0, 0, 0))
son.alpha_composite(ekran, (EX0, EY0))                 # ekran arkada, çerçeve önde (kenarlar çerçeveye otursun)
son.alpha_composite(cerceve)
son.alpha_composite(ekran.crop((0, 0, EW, 90 - EY0)), (EX0, EY0))   # beyaz menü çubuğunun üstünü de uygulama kaplasın
son = son.crop(son.getbbox())
son = son.resize((1400, int(son.height * 1400 / son.width)), Image.LANCZOS)
son.save(CIKTI, 'WEBP', quality=88, method=6)
print(son.size)
