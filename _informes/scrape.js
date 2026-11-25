// Recolecta carros comparables en Mercado Libre para los informes de precio.
// Se ejecuta en el navegador de Claude, en una pestaña abierta en https://carros.mercadolibre.com.co/
// Antes de pegarlo, define: window.__CFG = [{id:'MCO-123', path:'mazda/cx-30', Y:2023, K:42000, inc:'grand touring', exc:'carbon|2\\.5', own:['4423632430', ...]}]
//   path = marca/modelo como aparece en la URL de búsqueda de Mercado Libre (p. ej. mercedes-benz/clase-glc, toyota/prado)
//   inc / exc = expresiones regulares (texto) para quedarse con la misma versión; own = ids numéricos de TODOS los carros de OnCars
// Corre en segundo plano. Consulta el avance con:  ({done:window.__infDone, err:window.__infErr})
// Resultado: JSON.stringify(window.__infOut)  -> {'MCO-123': {n,pt,a25,a40,a50,a75,sy,syn,nw,c,dup}}  (precios en millones)
(() => {
  const parse = html => {
    const d = new DOMParser().parseFromString(html, 'text/html');
    const items = [...d.querySelectorAll('li.ui-search-layout__item')].map(x => {
      const a = x.querySelector('a'), t = (x.querySelector('h3, .poly-component__title') || {}).innerText || '';
      const p = (x.querySelector('.poly-price__current .andes-money-amount__fraction') || {}).innerText || '';
      const at = [...x.querySelectorAll('.poly-attributes_list__item')].map(e => e.innerText.trim());
      const loc = (x.querySelector('.poly-component__location') || {}).innerText || '';
      const href = a ? a.href.split('#')[0] : '';
      return { t: t.trim(), p: +p.replace(/\./g, ''), y: +(at[0] || 0), km: +((at[1] || '').replace(/\D/g, '')), loc: loc.trim(), id: (href.match(/MCO-?(\d+)/) || ['', ''])[1] };
    });
    return { items, cap: /captcha|seguridad/i.test(d.title) };
  };
  const q = (arr, p) => { const s = [...arr].sort((a, b) => a - b); if (!s.length) return null; const i = (s.length - 1) * p, lo = Math.floor(i), hi = Math.ceil(i); return Math.round((s[lo] + (s[hi] - s[lo]) * (i - lo)) / 1e5) / 10 };
  const M = v => Math.round(v / 1e5) / 10;
  window.__infOut = {}; window.__infErr = []; window.__infDone = false;
  (async () => {
    for (const cf of window.__CFG) {
      let all = [];
      for (const y of [cf.Y - 1, cf.Y, cf.Y + 1]) {
        for (const pg of ['', '_Desde_49_NoIndex_True']) {
          try {
            const r = await fetch(`/${cf.path}/${y}/${pg}`, { credentials: 'include' }); const o = parse(await r.text());
            if (o.cap) { window.__infErr.push('CAPTCHA'); window.__infDone = 'captcha'; return }
            all = all.concat(o.items); if (o.items.length < 48) break;
          } catch (e) { window.__infErr.push(cf.id + ' ' + e.message) }
          await new Promise(r => setTimeout(r, 700));
        }
      }
      const own = new Set(cf.own || []), seen = new Set(), inc = new RegExp(cf.inc, 'i'), exc = new RegExp(cf.exc || '$^', 'i');
      const base = all.filter(it => { if (own.has(it.id) || seen.has(it.id)) return false; seen.add(it.id); return it.p > 5e6 && Math.abs(it.y - cf.Y) <= 1 });
      const used = base.filter(it => it.km >= 300), newd = base.filter(it => it.km < 300);
      const dupF = it => it.y === cf.Y && Math.abs(it.km - cf.K) <= 600;  // posible mismo carro publicado por otro vendedor
      const ver = used.filter(it => inc.test(it.t) && !exc.test(it.t));
      const ex = used.filter(it => !exc.test(it.t));
      let pool = ver.length >= 5 ? ver : ex.length >= 5 ? ex : used;
      const dups = pool.filter(dupF); pool = pool.filter(it => !dupF(it));
      const adj = pool.map(it => ({ ...it, a: it.p * (1 + 0.07 * (cf.Y - it.y)) * (1 + Math.max(-0.2, Math.min(0.2, 0.002 * ((it.km - cf.K) / 1000)))) }));
      const A = adj.map(x => x.a), a50 = q(A, .5) * 1e6;
      const close = [...adj].filter(x => x.p < a50 * 1.6 && x.p > a50 * 0.6).sort((a, b) => (Math.abs(a.y - cf.Y) * 40000 + Math.abs(a.km - cf.K)) - (Math.abs(b.y - cf.Y) * 40000 + Math.abs(b.km - cf.K))).slice(0, 6);
      window.__infOut[cf.id] = {
        n: pool.length, pt: ver.length >= 5 ? 'v' : 'm', a25: q(A, .25), a40: q(A, .4), a50: q(A, .5), a75: q(A, .75),
        sy: q(pool.filter(x => x.y === cf.Y).map(x => x.p), .5), syn: pool.filter(x => x.y === cf.Y).length,
        nw: newd.slice(0, 3).map(x => [x.y, M(x.p), x.t.slice(0, 50) + ' (0 km)']),
        c: close.map(x => [x.y, x.km, M(x.p), x.loc.split(' - ').pop().replace(' D.C.', ''), x.t.replace(/^\S+ /, '').slice(0, 50)]),
        dup: dups.slice(0, 4).map(x => ['MCO-' + x.id, x.km, M(x.p), x.loc.split(' - ').pop()])
      };
    }
    window.__infDone = true;
  })();
})();
