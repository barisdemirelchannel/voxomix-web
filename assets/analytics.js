/* VoxoMix — site ölçümü (GA4 + açık rıza banner'ı)
 * ---------------------------------------------------------------------------
 * Tek dosya; her sayfanın <head>'ine `defer` ile bağlanır (tools/inject-analytics.py).
 *
 * TASARIM KARARI — GA4 YALNIZCA ONAY SONRASI YÜKLENİR.
 * Consent Mode'un yaygın kullanımı gtag'i baştan yükleyip "denied" durumunda
 * çerezsiz ping göndermektir. Burada bilerek yapmıyoruz: ziyaretçi "Reddet"
 * derse Google'a HİÇBİR istek gitmez. Sebep (a) banner metnindeki
 * "reddedersen veri gönderilmez" cümlesi böylece harfiyen doğru olur,
 * (b) markanın tamamı "verin cihazından çıkmaz" üzerine kurulu — pazarlama
 * sitesinin bunu çiğnemesi anlatıyı zayıflatır. Bedeli: reddedenler GA4'te
 * görünmez. Bu yüzden İNDİRME sayısı ayrıca Worker'da sunucu tarafında
 * tutulur (worker/index.js) — orası onaydan bağımsız ve eksiksizdir.
 *
 * KURULUM: aşağıdaki GA_ID'yi doldurun. Boş kaldığı sürece bu dosya hiçbir şey
 * yapmaz — ne banner çizer, ne istek atar. Yani ID gelmeden deploy etmek güvenlidir.
 */
(function () {
  'use strict';

  // ---- YAPILANDIRMA --------------------------------------------------------
  // GA4 → Yönetici → Veri akışları → Web akışı → "Ölçüm Kimliği" (G- ile başlar).
  // Mülk: "voxomix.com" · akış: "voxomix.com — web" (akış no 15404955615), 8 Ağu 2026.
  var GA_ID = 'G-1N6R4SZ3TY';

  var STORE_KEY = 'voxomix_consent';      // 'granted' | 'denied'
  var STORE_VER = 'voxomix_consent_v';    // metin/kapsam değişirse tekrar sorulur
  var CURRENT_V = '1';

  if (!GA_ID) return;

  // ---- Dil tespiti (i18n.js'teki path mantığının küçük kopyası) -------------
  // i18n.js'e bağımlı olmamak bilinçli: bu dosya head'de, o body sonunda yükleniyor.
  function pageLang() {
    var seg = location.pathname.split('/')[1];
    return (seg === 'en' || seg === 'es' || seg === 'fr' || seg === 'de') ? seg : 'tr';
  }
  var LANG = pageLang();

  // ---- Banner metinleri ----------------------------------------------------
  // Not: "veri gönderilmez" iddiası ancak GA4 onay sonrası yüklendiği için doğru.
  var T = {
    tr: {
      body: 'Sitenin nasıl kullanıldığını anlamak için analiz çerezleri kullanmak istiyoruz. Reddedersen çerez yerleştirilmez ve hiçbir veri gönderilmez.',
      note: 'VoxoMix uygulaması her hâlükârda çevrimdışı çalışır — müzik dosyaların bilgisayarından çıkmaz.',
      ok: 'Kabul et', no: 'Reddet', more: 'Gizlilik Politikası', privacy: '/gizlilik.html'
    },
    en: {
      body: 'We would like to use analytics cookies to understand how this site is used. If you decline, no cookies are set and no data is sent.',
      note: 'The VoxoMix app works offline either way — your music files never leave your computer.',
      ok: 'Accept', no: 'Decline', more: 'Privacy Policy', privacy: '/en/gizlilik.html'
    },
    es: {
      body: 'Nos gustaría usar cookies analíticas para entender cómo se usa este sitio. Si las rechazas, no se instala ninguna cookie ni se envía ningún dato.',
      note: 'La app de VoxoMix funciona sin conexión en cualquier caso: tus archivos de música nunca salen de tu ordenador.',
      ok: 'Aceptar', no: 'Rechazar', more: 'Política de privacidad', privacy: '/en/gizlilik.html'
    },
    fr: {
      body: "Nous souhaitons utiliser des cookies de mesure d'audience pour comprendre l'usage du site. Si vous refusez, aucun cookie n'est déposé et aucune donnée n'est envoyée.",
      note: "L'application VoxoMix fonctionne hors ligne dans tous les cas — vos fichiers audio ne quittent jamais votre ordinateur.",
      ok: 'Accepter', no: 'Refuser', more: 'Politique de confidentialité', privacy: '/en/gizlilik.html'
    },
    de: {
      body: 'Wir möchten Analyse-Cookies verwenden, um zu verstehen, wie diese Website genutzt wird. Wenn du ablehnst, werden keine Cookies gesetzt und keine Daten gesendet.',
      note: 'Die VoxoMix-App funktioniert ohnehin offline — deine Musikdateien verlassen deinen Computer nie.',
      ok: 'Akzeptieren', no: 'Ablehnen', more: 'Datenschutz', privacy: '/en/gizlilik.html'
    }
  }[LANG];

  // ---- Depolama (özel sekmede localStorage patlayabilir) -------------------
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function storedChoice() {
    return get(STORE_VER) === CURRENT_V ? get(STORE_KEY) : null;
  }

  // ---- gtag iskeleti -------------------------------------------------------
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  // Savunma amaçlı: gtag herhangi bir yoldan yüklenirse varsayılan "reddedildi" olsun.
  gtag('consent', 'default', {
    ad_storage: 'denied',
    ad_user_data: 'denied',
    ad_personalization: 'denied',
    analytics_storage: 'denied'
  });

  var gaLoaded = false;
  function loadGA() {
    if (gaLoaded) return;
    gaLoaded = true;
    gtag('consent', 'update', { analytics_storage: 'granted' });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
    gtag('js', new Date());
    // page_language: aynı sayfanın 5 dil sürümünü raporda ayırt edebilmek için.
    gtag('config', GA_ID, { page_language: LANG });
  }

  // ---- Olay gönderimi ------------------------------------------------------
  // Onay yoksa sessizce düşer; kuyruğa alınmaz (reddedeni sonradan göndermek yanlış olur).
  function track(name, params) {
    if (!gaLoaded) return;
    gtag('event', name, params || {});
  }

  // ---- Banner --------------------------------------------------------------
  function styleOnce() {
    if (document.getElementById('vx-consent-css')) return;
    var css = document.createElement('style');
    css.id = 'vx-consent-css';
    css.textContent = [
      '#vx-consent{position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;',
      'background:#16151f;border:1px solid #2a2938;border-radius:14px;padding:18px 20px;',
      'box-shadow:0 12px 40px rgba(0,0,0,.5);color:#f0f0f0;',
      "font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:14px;line-height:1.55;",
      'display:flex;gap:18px;align-items:center;flex-wrap:wrap;max-width:1040px;margin:0 auto}',
      '#vx-consent p{margin:0;flex:1 1 420px;min-width:260px}',
      '#vx-consent .vx-note{display:block;color:#888;font-size:13px;margin-top:4px}',
      '#vx-consent a{color:#6c5ce7}',
      '#vx-consent .vx-actions{display:flex;gap:10px;flex:0 0 auto}',
      '#vx-consent button{font:inherit;font-weight:700;cursor:pointer;border-radius:10px;',
      'padding:11px 20px;border:1px solid #2a2938;background:transparent;color:#f0f0f0}',
      '#vx-consent button.vx-ok{background:#6c5ce7;border-color:#6c5ce7;color:#fff}',
      '#vx-consent button:hover{opacity:.88}',
      '[data-vx-consent-reset]{font:inherit;font-weight:600;cursor:pointer;border-radius:8px;',
      'padding:7px 14px;border:1px solid #2a2938;background:transparent;color:inherit}',
      '[data-vx-consent-reset]:hover{opacity:.8}',
      '@media(max-width:600px){#vx-consent{padding:16px}#vx-consent .vx-actions{width:100%}',
      '#vx-consent button{flex:1}}'
    ].join('');
    document.head.appendChild(css);
  }

  function showBanner() {
    styleOnce();
    var box = document.createElement('div');
    box.id = 'vx-consent';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-live', 'polite');

    var p = document.createElement('p');
    p.appendChild(document.createTextNode(T.body + ' '));
    var a = document.createElement('a');
    a.href = T.privacy; a.textContent = T.more;
    p.appendChild(a);
    var note = document.createElement('span');
    note.className = 'vx-note'; note.textContent = T.note;
    p.appendChild(note);

    var actions = document.createElement('div');
    actions.className = 'vx-actions';
    var no = document.createElement('button');
    no.type = 'button'; no.textContent = T.no;
    var ok = document.createElement('button');
    ok.type = 'button'; ok.className = 'vx-ok'; ok.textContent = T.ok;

    function decide(choice) {
      set(STORE_KEY, choice);
      set(STORE_VER, CURRENT_V);
      box.remove();
      // Tercih gizlilik sayfasından DEĞİŞTİRİLDİYSE yeniden yükle: gtag bir kez
      // yüklendikten sonra geri alınamaz, "kabul → ret" ancak temiz sayfada geçerli olur.
      if (reopened) { location.reload(); return; }
      if (choice === 'granted') loadGA();
    }
    no.addEventListener('click', function () { decide('denied'); });
    ok.addEventListener('click', function () { decide('granted'); });

    actions.appendChild(no); actions.appendChild(ok);
    box.appendChild(p); box.appendChild(actions);
    document.body.appendChild(box);
  }

  // ---- Tıklama ölçümü ------------------------------------------------------
  // Delege dinleyici: sayfa üretici betiklerle yeniden yazıldığında bozulmasın diye
  // butonlara tek tek özel attribute eklemiyoruz, href deseninden yakalıyoruz.
  function wireClicks() {
    document.addEventListener('click', function (e) {
      var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
      if (!a) return;
      var href = a.getAttribute('href') || '';

      // Gerçek indirme: /download/mac | /download/win  → Worker 302'ye gider.
      var dl = href.match(/^\/download\/(mac|win)\b/);
      if (dl) {
        track('download_click', {
          os: dl[1],
          page_language: LANG,
          placement: placementOf(a)
        });
        return;
      }
      // İndirme bölümüne götüren CTA'lar (hero, nav, plan kartları, deneme kutusu).
      if (/#download$/.test(href)) {
        track('cta_click', { page_language: LANG, placement: placementOf(a) });
      }
    }, true);
  }

  // ---- "Çerez tercihimi değiştir" (gizlilik sayfasındaki düğme) -------------
  // KVKK ve GDPR onayın geri alınmasının verilmesi kadar kolay olmasını istiyor.
  // Düğme HTML'de `hidden` duruyor; ölçüm kapalıyken (GA_ID boş) hiç görünmüyor,
  // çünkü o durumda geri alınacak bir onay da yok.
  var reopened = false;
  function wireResetControl() {
    var btn = document.querySelector('[data-vx-consent-reset]');
    if (!btn) return;
    styleOnce();
    var block = btn.closest('[data-vx-consent-block]') || btn;
    block.hidden = false;
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      try {
        localStorage.removeItem(STORE_KEY);
        localStorage.removeItem(STORE_VER);
      } catch (e2) {}
      reopened = true;
      if (!document.getElementById('vx-consent')) showBanner();
    });
  }

  // Butonun sayfadaki yerini etiketle — "hangi CTA çalışıyor" sorusunun cevabı bu.
  function placementOf(a) {
    if (a.closest('nav')) return 'nav';
    if (a.closest('.hero')) return 'hero';
    if (a.closest('.plan-card')) return 'plan';
    if (a.closest('.download-card')) return 'download_card';
    return 'other';
  }

  // ---- Başlat --------------------------------------------------------------
  function start() {
    wireClicks();
    wireResetControl();
    var choice = storedChoice();
    if (choice === 'granted') loadGA();
    else if (choice !== 'denied') showBanner();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
