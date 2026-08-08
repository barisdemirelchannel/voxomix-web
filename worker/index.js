/* voxomix.com — Worker
 * ---------------------------------------------------------------------------
 * Tek işi var: /download/mac ve /download/win sabit yollarını GitHub'daki
 * SON sürümün doğru dosyasına 302 ile yönlendirmek. Diğer her istek statik
 * dosyalara (ASSETS) düşer — site davranışı değişmez.
 *
 * NEDEN VAR:
 *   1) İndirme linki artık sürüme bağlı değil. Bugüne kadar 5 index.html'de
 *      elle güncelleniyordu ve iki kez üst üste tutmadı (önce v1.2.2'de,
 *      sonra v1.3.1'de kaldı) → ziyaretçi eski sürümü indirdi, üstüne bir de
 *      auto-update çekti. Sıra bağımlılığı da kalkıyor: dosya release'e
 *      yüklenmeden link "güncel" görünemez, çünkü sabit link diye bir şey yok.
 *   2) İndirme sayısı sunucu tarafında sayılabiliyor (count()). Reklam
 *      engelleyici bunu gizleyemez; GA4'teki download_click ise yalnızca
 *      çerez onayı vermiş ziyaretçileri görür.
 *
 * ⚠️ NEDEN GitHub API DEĞİL: api.github.com kimliksiz istekte saatte 60 ile
 * sınırlı ve limit IP başına. Worker'lar paylaşımlı IP'lerden çıktığı için bu
 * yol üretimde sürekli 403 yer (yerel testte de anında yedi). Onun yerine
 * electron-updater'ın zaten her sürüme yüklediği feed dosyaları okunuyor:
 * bunlar api.github.com değil github.com üzerinden, oran sınırı olmadan
 * ve `releases/latest/download/` sayesinde sürümden bağımsız erişilebiliyor.
 */

const REPO = 'barisdemirelchannel/voxomix-releases';
const LATEST = `https://github.com/${REPO}/releases/latest/download`;
// Feed okunamazsa insan gözüyle bakılabilecek release sayfası — ziyaretçi asla
// boş ekranla kalmasın. (Kırık indirme, yanlış sürümden beterdir.)
const FALLBACK = `https://github.com/${REPO}/releases/latest`;
const CACHE_TTL = 600; // sn

// os -> [feed dosyası, aranan uzantı]
const TARGETS = {
  mac: { feed: 'latest-mac.yml', ext: '.dmg' }, // feed'in `path`'i zip'tir (auto-update dosyası);
  win: { feed: 'latest.yml', ext: '.exe' },     // insanın indireceği dosyayı `files` listesinden seçiyoruz
};
const ALIASES = { macos: 'mac', osx: 'mac', windows: 'win', exe: 'win', dmg: 'mac' };

/* electron-updater feed'inden sürüm + dosya adlarını çıkar.
 * Tam YAML ayrıştırıcı gereksiz: dosyanın şeması sabit ve iki satır deseni yetiyor. */
function parseFeed(text) {
  const version = (text.match(/^version:\s*(.+)$/m) || [])[1];
  const files = [...text.matchAll(/^\s*-\s*url:\s*(.+)$/gm)].map((m) => m[1].trim());
  return { version: version ? version.trim() : null, files };
}

async function resolveAsset(os) {
  const target = TARGETS[os];
  const res = await fetch(`${LATEST}/${target.feed}`, {
    headers: { 'User-Agent': 'voxomix-web-worker' },
    // github.com kendi cache başlıklarını gönderiyor; kenar önbelleğini biz belirleyelim.
    cf: { cacheTtl: CACHE_TTL, cacheEverything: true },
  });
  if (!res.ok) return null;

  const { version, files } = parseFeed(await res.text());
  const name = files.find((f) => f.toLowerCase().endsWith(target.ext));
  if (!name) return null;

  // Sürüm etiketi kurmuyoruz: `releases/latest/download/<ad>` zaten son sürüme çözülüyor.
  return { url: `${LATEST}/${encodeURIComponent(name)}`, version, name };
}

/* Günlük indirme sayacı.
 * KV bağlı değilse sessizce atlanır → Worker KV olmadan da çalışır.
 * Bilinçli basitlik: oku-artır-yaz yarışında eşzamanlı indirmelerde birkaç
 * artış kaybolabilir. Günde onlarca indirmede bu fark önemsiz; kesin sayım
 * Durable Object ister ve bu aşamada karşılığı yok. */
async function count(env, os, version) {
  if (!env.DOWNLOADS) return;
  try {
    const day = new Date().toISOString().slice(0, 10);
    const key = `dl:${day}:${os}:${version || 'unknown'}`;
    const current = parseInt((await env.DOWNLOADS.get(key)) || '0', 10);
    await env.DOWNLOADS.put(key, String(current + 1), {
      expirationTtl: 60 * 60 * 24 * 400, // ~13 ay
    });
  } catch {
    // Sayım asla indirmeyi engellememeli.
  }
}

function redirect(url, extra = {}) {
  return new Response(null, {
    status: 302,
    headers: {
      Location: url,
      // Sürüm değişince tarayıcı eski hedefi hatırlamasın.
      'Cache-Control': 'no-store',
      // Bu yollar sayfa değil; arama sonuçlarında görünmesinler.
      'X-Robots-Tag': 'noindex',
      ...extra,
    },
  });
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const match = url.pathname.match(/^\/download\/([a-z0-9]+)\/?$/i);

    if (match) {
      const raw = match[1].toLowerCase();
      const os = TARGETS[raw] ? raw : ALIASES[raw];
      if (!os) return redirect(new URL('/#download', url).toString());

      const asset = await resolveAsset(os);
      if (!asset) return redirect(FALLBACK);

      ctx.waitUntil(count(env, os, asset.version));
      return redirect(asset.url, { 'X-VoxoMix-Version': asset.version || '' });
    }

    // /download veya /download/ → ana sayfadaki indirme bölümü
    if (/^\/download\/?$/.test(url.pathname)) {
      return redirect(new URL('/#download', url).toString());
    }

    return env.ASSETS.fetch(request);
  },
};
