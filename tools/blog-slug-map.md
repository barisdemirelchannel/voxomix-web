# VoxoMix Blog — Diller Arası Slug Haritası

Her yazının her dildeki URL slug'ı. İç linkleri (`/LANG/blog/<slug>`) ve hreflang'i
bu tabloya göre eşle. hreflang seti HER zaman 7 satır: tr, en, es, fr, de, it, x-default(=tr).
URL kalıbı: TR = `https://voxomix.com/blog/<tr>` · diğerleri = `https://voxomix.com/<lang>/blog/<slug>`.

| Konu | tr | en | es | fr | de | it |
|---|---|---|---|---|---|---|
| Çevrimdışı stem ayırma | cevrimdisi-stem-ayirma | offline-stem-separation | separacion-de-pistas-sin-conexion | separation-de-pistes-hors-ligne | offline-stem-trennung | separazione-tracce-offline |
| Şarkı hızını düşürme | sarki-hizini-dusurme-ses-bozulmadan | slow-down-song-without-changing-pitch | ralentizar-cancion-sin-cambiar-el-tono | ralentir-une-chanson-sans-changer-la-hauteur | song-verlangsamen-ohne-tonhoehe | rallentare-una-canzone-senza-cambiare-tono |
| Pillar — şarkıyla pratik | sarkiyla-pratik-yapma-rehberi | practice-any-song-complete-guide | como-practicar-con-cualquier-cancion | travailler-nimporte-quelle-chanson-guide | mit-jedem-song-zu-hause-ueben | esercitarsi-con-qualsiasi-canzone-guida |
| VoxoMix nasıl kullanılır | voxomix-nasil-kullanilir | how-to-use-voxomix | como-usar-voxomix | comment-utiliser-voxomix | voxomix-verwenden | come-usare-voxomix |
| Şarkıdan vokal ayırma (YENİ) | sarkidan-vokal-ayirma | how-to-remove-vocals-from-a-song | como-quitar-la-voz-de-una-cancion | supprimer-la-voix-dune-chanson | gesang-aus-einem-song-entfernen | rimuovere-la-voce-da-una-canzone |

## og:locale
tr→tr_TR · en→en_US · es→es_ES · fr→fr_FR · de→de_DE · it→it_IT

## Kurallar (çevirilerde ihlal etme)
- Yasal linkler (kullanim-sartlari, gizlilik, mesafeli-satis, teslimat-iade): TR dışında **hep `/en/...`** (İngilizce). Öneki değiştirme.
- Nav/blog/hakkimizda/logo linkleri: `/en/` → `/<lang>/`.
- Rakip/şirket ismi YOK · sahte istatistik YOK · abartı YOK · VoxoMix'i kötüleme YOK.
- Tüm JSON-LD şema (Article/BreadcrumbList/FAQPage/Person/WebPage) korunur; sadece metin DEĞERLERİ çevrilir, yapı+URL'ler hedef dile göre güncellenir.
- `<html lang>`, `<title>`, meta description, canonical, og:url, og:locale, hreflang → hedef dile göre.
- `.nav-lang` öğesine dokunma (JS çok-dilli seçiciye yükseltiyor).
