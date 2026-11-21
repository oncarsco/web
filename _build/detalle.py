# Páginas de detalle de cada carro: /carro/<slug>/index.html
# Lo llama build.py. Entradas: cars.json (con "notas" de OnCars OS) y detalles.json (datos de la publicación:
#   f = códigos de fotos de Mercado Libre, d = descripción, v = versión, co = color, hp, tr = tracción,
#   pa = pasajeros, pl = último dígito de placa, ud = único dueño, eq = equipamiento).
# Las fotos de la galería se muestran desde el CDN de imágenes; el cliente nunca sale de oncarsco.com.
import html, json, re, unicodedata, urllib.parse

SITE = 'https://oncarsco.com/'
WA = '573166279204'
TEL = '+573166279204'
FIRMA = 'Algunos buscan simplemente un carro, pero otros, buscan tomar decisiones inteligentes. Si ese es tu caso, hablemos.'
E = lambda s: html.escape(str(s if s is not None else ''), quote=True)
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.8 11.9 11.9 0 0 0 4.6 4c1.7.7 2.4.8 3.2.7a2.8 2.8 0 0 0 1.8-1.3 2.3 2.3 0 0 0 .2-1.3c-.1-.1-.2-.2-.4-.3z"/></svg>'
TEL_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>'

def slug(c):
    s = f"{c['marca']} {c['modelo']} {c['anio']} {c['id']}"
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

CASE = {'cx': 'CX', 'glc': 'GLC', 'glb': 'GLB', 'gla': 'GLA', 'ix1': 'iX1', 'x1': 'X1', '4runner': '4Runner', 'bmw': 'BMW'}
def _tok(w):
    lw = w.lower()
    if lw in CASE: return CASE[lw]
    m = re.match(r'([a-z]+)(-\d+)$', lw)
    if m and m.group(1) in CASE: return CASE[m.group(1)] + m.group(2)
    return w
def nombre(c):
    t = c['modelo'].split(); base = [t[0]]
    for w in t[1:]:
        if re.search(r'\d', w): break
        base.append(w)
    return ' '.join(_tok(w) for w in base)

def wa(t): return f'https://wa.me/{WA}?text=' + urllib.parse.quote(t)
def miles(n): return f'{int(n):,}'.replace(',', '.')
def foto(code, size='F'): return f'https://http2.mlstatic.com/D_NQ_NP_2X_{code}-{size}.webp'

# --- Observaciones: notas del equipo en OnCars OS, limpias para publicar ---
DROP = {'marca', 'referencia', 'version', 'precio', 'modelo', 'kilometraje', 'ubicacion', 'motor', 'transmision',
        'tipo de combustible', 'combustible', 'dueno', 'propietario', 'telefono', 'celular'}
FIX = [(r'repintadoos', 'repintados'), (r'repiontados', 'repintados'), (r'repontados', 'repintados'),
       (r'delanetero', 'delantero'), (r'\bsoat\b', 'SOAT'), (r'\btecno\b', 'tecnomecánica'), (r'\bsept\b', 'septiembre'),
       (r'\bautomatica\b', 'automática'), (r'\bhibrido\b', 'híbrido'), (r'\bSEG\b', 'SE-G')]
def _norm(k):
    return unicodedata.normalize('NFKD', k).encode('ascii', 'ignore').decode().lower().strip()
def _cap(s):
    s = s.strip().rstrip('.').strip()
    for a, b in FIX: s = re.sub(a, b, s, flags=re.I)
    return s[:1].upper() + s[1:] if s else s

def observaciones(notas):
    out = []
    for raw in (notas or '').replace('⁠', '').splitlines():
        l = raw.strip().lstrip('-•*·').strip().strip('*').strip()
        if not l or 'caracter' in _norm(l) or re.search(r'\d{7,}', l): continue
        if _norm(l) in ('sin detalles', 'vendido', 'vendida'): continue
        if ':' in l:
            k, v = [x.strip() for x in l.split(':', 1)]
            nk, nv = _norm(k), _norm(v)
            if nk in DROP or not v or nv in ('n/a', 'na', '-', 'x'): continue
            if nv in ('si', 'sí'): out.append(_cap(k)); continue
            if nv == 'no' and nk in ('reclamaciones', 'repintados', 'choques'): out.append('Sin ' + nk); continue
            if nk == 'placa':
                m = re.match(r'(\d)\s*(.*)', v)
                out.append('Placa terminada en ' + (m.group(1) + (' · ' + m.group(2) if m.group(2) else '') if m else v)); continue
            v = v.strip().rstrip('.')
            out.append(f'{_cap(k)}: {v[:1].upper() + v[1:]}')
        else:
            out.append(_cap(l))
    seen, res = set(), []
    for o in out:
        if _norm(o) not in seen: seen.add(_norm(o)); res.append(o)
    return res

def _desc_html(d):
    d = (d or '').split('\n\n\n')[0].strip()
    return ''.join(f'<p>{E(p.strip())}</p>' for p in d.split('\n\n') if p.strip())

CSS = r'''
.crumb{padding:18px 0 0;font-size:14px;color:var(--dim)}.crumb a{color:var(--muted);text-decoration:none}.crumb a:hover{color:var(--text)}
.det{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:40px;padding:22px 0 56px;align-items:start}
@media (max-width:900px){.det{grid-template-columns:1fr;gap:22px}}
.gal{position:relative}
.track{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;border-radius:18px;background:var(--surface);scrollbar-width:none}
.track::-webkit-scrollbar{display:none}
.track img{flex:0 0 100%;width:100%;aspect-ratio:4/3;object-fit:cover;scroll-snap-align:start}
.gnav{position:absolute;top:calc(50% - 50px);width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:rgba(13,13,13,.75);color:var(--text);font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center}
.gnav.p{left:12px}.gnav.n{right:12px}
.gcount{position:absolute;right:12px;top:12px;background:rgba(13,13,13,.75);border-radius:999px;padding:4px 10px;font-size:13px;color:var(--muted)}
.thumbs{display:grid;grid-template-columns:repeat(8,1fr);gap:8px;margin-top:10px}
.thumbs button{padding:0;border:2px solid transparent;border-radius:10px;overflow:hidden;background:none;cursor:pointer;opacity:.65}
.thumbs button.on{border-color:var(--accent);opacity:1}
.thumbs img{aspect-ratio:4/3;object-fit:cover;width:100%}
@media (max-width:600px){.thumbs{display:none}.gnav{display:none}}
.side{position:sticky;top:90px}
@media (max-width:900px){.side{position:static}}
.side h1{font-family:var(--display);font-weight:400;font-size:clamp(24px,3vw,34px);line-height:1.15;margin:0}
.side .ver{color:var(--muted);margin:8px 0 0}
.side .pr{font-family:var(--display);font-size:clamp(26px,3.2vw,34px);color:var(--accent);margin:18px 0 0;font-variant-numeric:tabular-nums}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.pills span{border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:14px;color:var(--muted)}
.cta2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:22px}
.cta2 .btn{width:100%}.cta2 .full{grid-column:1/-1}
.note{color:var(--dim);font-size:14px;margin:14px 0 0}
.blk{padding:34px 0;border-top:1px solid var(--line)}
.blk h2{font-size:clamp(18px,2.2vw,24px);margin-bottom:16px}
.obs{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px}
@media (max-width:600px){.obs{grid-template-columns:1fr 1fr;gap:8px}.obs li{padding:10px 10px 10px 28px;font-size:14px}.obs li::before{left:11px;top:16px;width:8px;height:8px}}
.obs li{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px 12px 38px;position:relative;color:var(--text)}
.obs li::before{content:"";position:absolute;left:14px;top:18px;width:10px;height:10px;border-radius:50%;background:var(--accent)}
.desc p{color:var(--muted);max-width:75ch;margin:0 0 12px}
.ficha{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:0}
.ficha div{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.ficha dt{font-size:13px;color:var(--dim)}.ficha dd{margin:4px 0 0;font-weight:600}
.eqs{display:flex;flex-wrap:wrap;gap:8px}.eqs span{background:var(--surface-2);border-radius:999px;padding:7px 13px;font-size:14px;color:var(--muted)}
.cond{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.cond div{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:14px}
.cond b{display:block;margin-bottom:4px}.cond p{margin:0;color:var(--muted);font-size:14.5px}
.firma{font-family:var(--display);font-size:clamp(16px,2vw,20px);line-height:1.5;max-width:46ch;margin:0 0 18px}
.rel{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.rel a{display:block;text-decoration:none;background:var(--surface);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.rel a:hover{border-color:var(--steel)}
.rel img{aspect-ratio:4/3;object-fit:cover;width:100%}
.rel div{padding:12px 14px}.rel b{display:block}.rel span{color:var(--dim);font-size:14px}.rel em{font-style:normal;font-family:var(--display);display:block;margin-top:6px}
.mbar{display:none}
@media (max-width:700px){.mbar{display:grid;grid-template-columns:1fr 1fr;gap:8px;position:fixed;left:0;right:0;bottom:0;z-index:25;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(13,13,13,.96);border-top:1px solid var(--line)}.mbar .btn{width:100%}body{padding-bottom:76px}.waf{display:none}}
'''

def pagina(c, det, base_css, todos):
    s = slug(c); url = SITE + f'carro/{s}/'
    nb = nombre(c)
    t = f"{c['marca']} {nb} {c['anio']}"
    codes = det.get('f') or []
    imgs = [foto(x) for x in codes] or [SITE + c['foto']]
    obs = observaciones(c.get('notas', ''))
    ficha = [('Año', c['anio']), ('Kilometraje', miles(c['km']) + ' km'), ('Transmisión', c.get('trans')),
             ('Combustible', c.get('comb')), ('Versión', det.get('v')), ('Potencia', det.get('hp')),
             ('Tracción', det.get('tr')), ('Color', det.get('co')), ('Pasajeros', det.get('pa')),
             ('Tipo', c.get('tipo')), ('Placa terminada en', det.get('pl')),
             ('Único dueño', 'Sí' if det.get('ud') == 'Sí' else None)]
    ficha = [(k, v) for k, v in ficha if v not in (None, '')]
    eq = det.get('eq') or []
    msg_ver = f'Hola OnCars, me interesa el {t} que vi en la página web ({url}). ¿Podemos agendar para verlo?'
    msg_fin = f'Hola OnCars, quiero financiar el {t} de ${miles(c["precio"])} que vi en la página web. ¿Qué necesito?'
    # carros relacionados: mismo tipo y precio parecido
    rel = sorted([x for x in todos if x['id'] != c['id']],
                 key=lambda x: (x.get('tipo') != c.get('tipo'), abs(x['precio'] - c['precio'])))[:3]
    rel_html = ''.join(f'<a href="/carro/{slug(x)}/"><img src="/{E(x["foto"])}" alt="{E(x["marca"]+" "+x["modelo"]+" "+str(x["anio"]))}" loading="lazy"><div><b>{E(x["marca"])} {E(nombre(x))}</b><span>{x["anio"]} · {miles(x["km"])} km</span><em>${miles(x["precio"])}</em></div></a>' for x in rel)
    desc_txt = re.sub(r'\s+', ' ', (det.get('d') or '').split('\n\n\n')[0])[:150]
    meta_desc = f"{t} usado en Medellín: {miles(c['km'])} km, {c.get('trans','').lower()}, {c.get('comb','').lower()}. Precio ${miles(c['precio'])}. Fotos reales, financiación y seguro con OnCars."
    ld = {"@context": "https://schema.org", "@type": "Car", "name": t, "url": url,
          "brand": {"@type": "Brand", "name": c['marca']}, "model": c['modelo'], "vehicleModelDate": str(c['anio']),
          "mileageFromOdometer": {"@type": "QuantitativeValue", "value": c['km'], "unitCode": "KMT"},
          "vehicleTransmission": c.get('trans'), "fuelType": c.get('comb'), "bodyType": c.get('tipo'),
          "color": det.get('co'), "itemCondition": "https://schema.org/UsedCondition",
          "image": imgs[:6], "description": desc_txt or meta_desc,
          "offers": {"@type": "Offer", "price": c['precio'], "priceCurrency": "COP", "availability": "https://schema.org/InStock",
                     "url": url, "seller": {"@type": "AutoDealer", "name": "OnCars", "telephone": "+57 316 627 9204", "url": SITE}}}
    if not ld['color']: del ld['color']
    ldb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Inicio", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "Carros disponibles", "item": SITE + "#carros"},
        {"@type": "ListItem", "position": 3, "name": t, "item": url}]}
    gal = ''.join(f'<img src="{E(u)}" alt="{E(t)}, foto {i+1} de {len(imgs)}" {"fetchpriority=high" if i==0 else "loading=lazy"} referrerpolicy="no-referrer">' for i, u in enumerate(imgs))
    th = ''.join(f'<button type="button" data-i="{i}" aria-label="Ver foto {i+1}"{" class=on" if i==0 else ""}><img src="{E(u)}" alt="" loading="lazy" referrerpolicy="no-referrer"></button>' for i, u in enumerate(imgs[:8]))
    obs_html = f'<section class="blk" aria-labelledby="h-obs"><h2 id="h-obs">Observaciones de OnCars</h2><ul class="obs">{"".join(f"<li>{E(o)}</li>" for o in obs)}</ul></section>' if obs else ''
    desc_html = f'<section class="blk" aria-labelledby="h-desc"><h2 id="h-desc">Descripción</h2><div class="desc">{_desc_html(det.get("d"))}</div></section>' if det.get('d') else ''
    eq_html = f'<section class="blk" aria-labelledby="h-eq"><h2 id="h-eq">Equipamiento</h2><div class="eqs">{"".join(f"<span>{E(x)}</span>" for x in eq)}</div></section>' if eq else ''
    return s, f'''<!DOCTYPE html>
<html lang="es-CO">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(t)} usado en Medellín · ${miles(c['precio'])} | OnCars</title>
<meta name="description" content="{E(meta_desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#0D0D0D">
<meta property="og:type" content="product"><meta property="og:locale" content="es_CO"><meta property="og:site_name" content="OnCars">
<meta property="og:url" content="{url}"><meta property="og:title" content="{E(t)} · ${miles(c['precio'])} | OnCars">
<meta property="og:description" content="{E(meta_desc)}"><meta property="og:image" content="{SITE}{E(c['foto'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE}{E(c['foto'])}">
<link rel="icon" href="/img/icon.png"><link rel="apple-touch-icon" href="/img/icon.png">
<link rel="preconnect" href="https://http2.mlstatic.com">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Michroma&family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700&display=swap" rel="stylesheet">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>
<script type="application/ld+json">{json.dumps(ldb, ensure_ascii=False)}</script>
<style>{base_css}{CSS}</style>
</head>
<body>
<header><div class="wrap nav">
  <a class="brand" href="/"><img src="/img/logo.png" alt="OnCars"><span>Concesionario<br>virtual</span></a>
  <nav class="links"><a href="/#carros">Carros disponibles</a><a href="/#vende">Vende tu carro</a><a href="/#asesoria">Asesoría de compra</a><a href="/#financiacion">Financiación y seguros</a></nav>
  <a class="btn wa" href="{E(wa(msg_ver))}" target="_blank" rel="noopener">{WA_SVG}Escríbenos</a>
</div></header>
<main class="wrap">
  <nav class="crumb" aria-label="Ruta"><a href="/#carros">← Todos los carros</a></nav>
  <div class="det">
    <div class="gal">
      <div class="track" id="track" tabindex="0" aria-label="Fotos del {E(t)}">{gal}</div>
      <button class="gnav p" type="button" data-d="-1" aria-label="Foto anterior">‹</button><button class="gnav n" type="button" data-d="1" aria-label="Foto siguiente">›</button>
      <span class="gcount" id="gcount">1 / {len(imgs)}</span>
      <div class="thumbs" id="thumbs">{th if len(imgs) > 1 else ''}</div>
    </div>
    <aside class="side">
      <p class="eyebrow">{E(c.get('tipo',''))} · {c['anio']}</p>
      <h1>{E(c['marca'])} {E(nb)}</h1>
      <p class="ver">{E(det.get('v') or '')}</p>
      <p class="pr">${miles(c['precio'])}</p>
      <div class="pills"><span>{c['anio']}</span><span>{miles(c['km'])} km</span><span>{E(c.get('trans'))}</span><span>{E(c.get('comb'))}</span>{f"<span>{E(det['tr'])}</span>" if det.get('tr') else ''}</div>
      <div class="cta2">
        <a class="btn wa full" href="{E(wa(msg_ver))}" target="_blank" rel="noopener">{WA_SVG}Lo quiero ver</a>
        <a class="btn" href="tel:{TEL}">{TEL_SVG}Llamar</a>
        <a class="btn acc" href="{E(wa(msg_fin))}" target="_blank" rel="noopener">Financiarlo</a>
      </div>
      <p class="note">Te lo mostramos con cita previa. Concesionario virtual en Medellín · WhatsApp y llamadas al 316 627 9204.</p>
    </aside>
  </div>
  {obs_html}
  {desc_html}
  <section class="blk" aria-labelledby="h-ficha"><h2 id="h-ficha">Ficha técnica</h2><dl class="ficha">{"".join(f"<div><dt>{E(k)}</dt><dd>{E(v)}</dd></div>" for k, v in ficha)}</dl></section>
  {eq_html}
  <section class="blk" aria-labelledby="h-cond"><h2 id="h-cond">Cómo compras con OnCars</h2><div class="cond">
    <div><b>Lo ves antes de decidir</b><p>Agenda una cita para verlo y probarlo. Puedes llevarlo a peritaje.</p></div>
    <div><b>Financiación y seguro</b><p>Te ayudamos con el crédito y la póliza en el mismo proceso.</p></div>
    <div><b>Entrega</b><p>En Medellín, sin costo. A otras ciudades lo llevamos; el traslado lo asume el comprador.</p></div>
    <div><b>Venta definitiva</b><p>Después de la entrega no se aceptan devoluciones. Por eso te mostramos todo antes.</p></div>
  </div></section>
  <section class="blk"><p class="firma">{FIRMA}</p><a class="btn wa" href="{E(wa(msg_ver))}" target="_blank" rel="noopener">{WA_SVG}Hablemos por WhatsApp</a></section>
  {f'<section class="blk" aria-labelledby="h-rel"><h2 id="h-rel">También te puede interesar</h2><div class="rel">{rel_html}</div><p style="margin-top:18px"><a class="btn" href="/#carros">Ver todos los carros</a></p></section>' if rel_html else ''}
</main>
<footer><div class="wrap foot"><img src="/img/logo.png" alt="OnCars"><nav><a href="/#carros">Carros</a><a href="/#vende">Vende tu carro</a><a href="/#asesoria">Asesoría</a><a href="/#financiacion">Financiación</a></nav><div>ONCARS S.A.S. · Medellín, Colombia · WhatsApp 316 627 9204</div></div></footer>
<div class="mbar"><a class="btn wa" href="{E(wa(msg_ver))}" target="_blank" rel="noopener">{WA_SVG}Lo quiero ver</a><a class="btn" href="tel:{TEL}">{TEL_SVG}Llamar</a></div>
<a class="waf" href="{E(wa(msg_ver))}" target="_blank" rel="noopener" aria-label="Escríbenos por WhatsApp">{WA_SVG}</a>
<script>
(()=>{{const tr=document.getElementById('track'),cnt=document.getElementById('gcount'),th=[...document.querySelectorAll('#thumbs button')],n=tr.children.length;
const cur=()=>Math.round(tr.scrollLeft/tr.clientWidth);
const go=i=>{{i=(i+n)%n;tr.scrollTo({{left:i*tr.clientWidth,behavior:'smooth'}})}};
tr.addEventListener('scroll',()=>{{const i=cur();cnt.textContent=(i+1)+' / '+n;th.forEach((b,k)=>b.classList.toggle('on',k===i))}},{{passive:true}});
document.querySelectorAll('.gnav').forEach(b=>b.addEventListener('click',()=>go(cur()+Number(b.dataset.d))));
th.forEach(b=>b.addEventListener('click',()=>go(Number(b.dataset.i))));
tr.addEventListener('keydown',e=>{{if(e.key==='ArrowRight')go(cur()+1);if(e.key==='ArrowLeft')go(cur()-1)}});
if(n<2)document.querySelectorAll('.gnav,.gcount').forEach(x=>x.hidden=true);
[...tr.querySelectorAll('img')].forEach((im,i)=>im.addEventListener('error',()=>{{if(i===0)im.src='/{E(c['foto'])}';else im.remove()}}));}})();
</script>
</body>
</html>
'''
