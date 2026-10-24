# VoxoMix ilk ekran laptop maketi: uygulama görüntüsünden 16:10 ekran + açılı laptop (tek PNG/WebP).
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'assets', 'app-screenshot.png')
CIKTI = os.path.join(KOK, 'assets', 'hero-laptop.webp')
im = Image.open(KAYNAK).convert('RGBA')
zemin = Image.new('RGBA', im.size, (12, 12, 15, 255)); zemin.alpha_composite(im); im = zemin.convert('RGB')
panel = im.getpixel((200, 960))                     # pencere zemin rengi (iki bölüm arası boşluk)
X0, X1 = 80, 2144
ust = im.crop((X0, 40, X1, 885))                       # başlık, zaman çizelgesi, Tempo/Vokal/Davul/Bas
alt = im.crop((X0, 1772, X1, 2336))                    # Akor bulucu, Metronom, Ton + Sözler
cubuk = 64                                            # pencere çubuğu (trafik ışıkları)
icerik_h = cubuk + ust.height + 18 + alt.height
W = int(round(icerik_h * 1.6)); H = icerik_h
ekran = Image.new('RGB', (W, H), panel)
d = ImageDraw.Draw(ekran)
d.rectangle([0, 0, W, cubuk], fill=tuple(max(0, c - 6) for c in panel))
for i, r in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
    cx = 40 + i * 34; d.ellipse([cx - 11, cubuk // 2 - 11, cx + 11, cubuk // 2 + 11], fill=r)
ox = (W - ust.width) // 2
ekran.paste(ust, (ox, cubuk)); ekran.paste(alt, (ox, cubuk + ust.height + 18))
ekran = ekran.resize((1600, 1000), Image.LANCZOS)

# laptop çizimi (düz), sonra perspektif
S = 1.0
bez = 30; kenar = 6
LW, LH = 1600 + 2 * bez + 2 * kenar, 1000 + 2 * bez + 2 * kenar
GW = int(LW * 1.16); GH = 42
CW, CH = GW + 120, LH + GH + 160
tuval = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
lx = (CW - LW) // 2; ly = 40
# kapak: alüminyum kenar + siyah çerçeve
kap = Image.new('RGBA', (LW, LH), (0, 0, 0, 0)); kd = ImageDraw.Draw(kap)
kd.rounded_rectangle([0, 0, LW - 1, LH - 1], radius=46, fill=(64, 64, 70, 255))
kd.rounded_rectangle([kenar, kenar, LW - 1 - kenar, LH - 1 - kenar], radius=40, fill=(10, 10, 12, 255))
kd.ellipse([LW // 2 - 7, kenar + bez // 2 - 7, LW // 2 + 7, kenar + bez // 2 + 7], fill=(34, 34, 40, 255))
ekr = ekran.convert('RGBA')
# cam parlaması
par = Image.new('RGBA', ekr.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(par)
pd.polygon([(0, 0), (int(ekr.width * .42), 0), (int(ekr.width * .18), ekr.height), (0, ekr.height)], fill=(255, 255, 255, 18))
ekr.alpha_composite(par)
maske = Image.new('L', ekr.size, 0); ImageDraw.Draw(maske).rounded_rectangle([0, 0, ekr.width - 1, ekr.height - 1], radius=10, fill=255)
kap.paste(ekr, (kenar + bez, kenar + bez), maske)
tuval.alpha_composite(kap, (lx, ly))
# gövde: önden görünen ince yamuk + menteşe çentiği
gx = (CW - GW) // 2; gy = ly + LH - 4
gov = Image.new('RGBA', (GW, GH), (0, 0, 0, 0)); gd = ImageDraw.Draw(gov)
for y in range(GH):
    t = y / (GH - 1); c = int(150 - 95 * t)
    inset = int((1 - t) * GW * .025)
    gd.line([(inset, y), (GW - 1 - inset, y)], fill=(c, c, c + 6, 255))
gd.rounded_rectangle([GW // 2 - GW * .09, 0, GW // 2 + GW * .09, GH * .32], radius=6, fill=(40, 40, 46, 255))
gm = Image.new('L', (GW, GH), 0); ImageDraw.Draw(gm).rounded_rectangle([0, -30, GW - 1, GH - 1], radius=26, fill=255)
gov.putalpha(Image.fromarray(np.minimum(np.array(gov.split()[3]), np.array(gm))))
tuval.alpha_composite(gov, (gx, gy))

# perspektif: sağ kenar biraz geride (sağa doğru hafif küçülür) — rotateY ≈ -12°
def katsayi(kaynak, hedef):
    A = []; B = []
    for (x, y), (u, v) in zip(hedef, kaynak):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B += [u, v]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()
w, h = tuval.size
sag_kisalma = 0.085; genislik = 0.93
hedef = [(0, 0), (w * genislik, h * sag_kisalma * .55), (w * genislik, h * (1 - sag_kisalma * .45)), (0, h)]
duz = [(0, 0), (w, 0), (w, h), (0, h)]
acili = tuval.transform((int(w * genislik) + 2, h), Image.PERSPECTIVE, katsayi(duz, hedef), Image.BICUBIC)
# yumuşak zemin gölgesi
son = Image.new('RGBA', (acili.width + 80, acili.height + 60), (0, 0, 0, 0))
gol = Image.new('RGBA', son.size, (0, 0, 0, 0)); ImageDraw.Draw(gol).ellipse(
    [int(son.width * .10), int(ly + LH + GH - 10), int(son.width * .92), int(ly + LH + GH + 70)], fill=(0, 0, 0, 170))
gol = gol.filter(ImageFilter.GaussianBlur(28))
son.alpha_composite(gol); son.alpha_composite(acili, (40, 0))
kutu = son.getbbox(); son = son.crop(kutu)
son = son.resize((1400, int(son.height * 1400 / son.width)), Image.LANCZOS)
son.save(CIKTI, 'WEBP', quality=86, method=6)
print(son.size)
