import json, datetime, os, re, base64, subprocess, html, unicodedata
import sys as _s
B = os.path.dirname(os.path.abspath(__file__)) + '/'; R = os.path.dirname(B.rstrip('/')) + '/'
_s.path.insert(0, B); _s.path.insert(0, R + '_build')
from nuevos import N, SRC, FECHA, precio as _pnuevo
from actualizar import nota as _nota
import datetime as _dt
import detalle as _det
A = R + '_ig/assets/'
D = os.environ.get('INF_DATOS', B + 'datos/').rstrip('/') + '/'  # datos privados fuera del repositorio
WA = _det.WA
import urllib.parse, secrets as _sec
def walink(t): return f'https://wa.me/{WA}?text=' + urllib.parse.quote(t)
cars = {x['id']: x for x in json.load(open(R + '_build/cars.json'))}
det = json.load(open(R + '_build/detalles.json'))
MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
def flarga(f): y, m, d = map(int, f.split('-')); return f'{d} de {MESES[m-1]} de {y}'
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
LOGO = b64(A + 'logo.png')
FONTS = f"""@font-face{{font-family:Mich;src:url(data:font/ttf;base64,{b64(A+'Michroma-Regular.ttf')})}}
@font-face{{font-family:Bric;src:url(data:font/ttf;base64,{b64(A+'Bricolage.ttf')})}}"""

def mill(v):  # millones -> "$104.900.000"
    return '$' + f"{round(v*1e6):,}".replace(',', '.')
def km(v): return f"{v:,}".replace(',', '.') + ' km'
e = html.escape
CASE = {'cx': 'CX', 'glc': 'GLC', 'glb': 'GLB', 'ix1': 'iX1', 'x1': 'X1', '4runner': '4Runner', 'st': 'ST', 'rs': 'RS', 'ls': 'LS', 'lx': 'LX', 'gt': 'GT',
        'hev': 'HEV', 'xs': 'XS', 'at': 'AT', 'awd': 'AWD', 'fwd': 'FWD', 'amg': 'AMG', 'tx': 'TX', 'sr5': 'SR5', 'fl': 'FL', 'z71': 'Z71', '4wd': '4WD', 'v8': 'V8',
        'se-g': 'SE-G', 'mhev': 'MHEV', 'f48': 'F48', 'sdrive': 'sDrive', 'xdrive30': 'xDrive30', 'ecvt': 'eCVT', 'at8': 'AT8', '18d': '18d', 'cx-5': 'CX-5', 'cx-30': 'CX-30', '1.0t': '1.0T'}
def nombre(c):
    w = [CASE.get(t.lower(), t) for t in c['modelo'].replace('Clase ', '').split()]
    return f"{c['marca']} {' '.join(w)}"

ORD = {2: 'Segunda', 3: 'Tercera', 4: 'Cuarta', 5: 'Quinta', 6: 'Sexta', 7: 'Séptima', 8: 'Octava'}
def ordinal(n): return ORD.get(n, f'{n}.ª')
def fcorta(f): y, m, d = map(int, f.split('-')); return f'{d} {MESES[m-1][:3]}'

def linea_tiempo(P):
    """SVG con el rango competitivo (banda), tu precio (línea) y la recomendación de cada informe."""
    W, H, L, R, T, Bm = 172, 50, 14, 4, 7, 9  # mm
    vals = [v for x in P for v in (x['a25'], x['a75'], x['precio'], x.get('rec'), x.get('acordado')) if v]
    lo, hi = min(vals) * 0.97, max(vals) * 1.03
    n = len(P)
    PAD = 12  # deja aire a los lados para las etiquetas de los puntos
    X = lambda i: L + PAD + (W - L - R - 2 * PAD) * (i / (n - 1) if n > 1 else 0.5)
    Y = lambda v: T + (H - T - Bm) * (1 - (v - lo) / (hi - lo))
    band = ' '.join(f'{X(i):.1f},{Y(x["a75"]):.1f}' for i, x in enumerate(P)) + ' ' + ' '.join(f'{X(i):.1f},{Y(x["a25"]):.1f}' for i, x in reversed(list(enumerate(P))))
    line = ' '.join(f'{X(i):.1f},{Y(x["precio"]):.1f}' for i, x in enumerate(P))
    g = []
    for k in range(4):  # guías horizontales
        v = lo + (hi - lo) * (k + 0.5) / 4
        g.append(f'<line x1="{L}" x2="{W-R}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="#EEE" stroke-width=".2"/><text x="{L-1.5}" y="{Y(v)+1:.1f}" text-anchor="end" font-size="2.4" fill="#8A8A8A">{fmtm(v)}</text>')
    pts = []
    for i, x in enumerate(P):
        cx, cy = X(i), Y(x['precio'])
        pts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.1" fill="#0D0D0D"/><text x="{cx:.1f}" y="{cy-2.2:.1f}" text-anchor="middle" font-size="2.6" font-weight="700" fill="#0D0D0D">{fmtm(x["precio"])}</text>')
        if x.get('rec') and x['rec'] < x['precio'] - 0.05:
            ry = Y(x['rec'])
            pts.append(f'<circle cx="{cx:.1f}" cy="{ry:.1f}" r="1" fill="#fff" stroke="#B8860B" stroke-width=".5"/><text x="{cx:.1f}" y="{ry+3.6:.1f}" text-anchor="middle" font-size="2.3" fill="#8A6500">rec. {fmtm(x["rec"])}</text>')
        lbl = 'Primer informe' if i == 0 else ('Hoy' if i == n - 1 else ordinal(i + 1) + ' revisión')
        pts.append(f'<text x="{cx:.1f}" y="{H-4:.1f}" text-anchor="middle" font-size="2.5" fill="#595959">{lbl}</text><text x="{cx:.1f}" y="{H-1:.1f}" text-anchor="middle" font-size="2.3" fill="#8A8A8A">{fcorta(x["fecha"])}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm" xmlns="http://www.w3.org/2000/svg" font-family="Bric">{"".join(g)}'
            f'<polygon points="{band}" fill="#F5C643" fill-opacity=".45"/><polyline points="{line}" fill="none" stroke="#0D0D0D" stroke-width=".6"/>{"".join(pts)}</svg>')

def fmtm(v): return f'{v:.1f}'.rstrip('0').rstrip('.').replace('.', ',') + ' M'

def pagina_seguimiento(X_, c, titulo, num, hist, p, r, keep, lo, hi, m, dias):
    """Página de las revisiones (2.ª, 3.ª…): lo que hizo OnCars por el carro y cómo ha evolucionado el precio."""
    g = X_.get('gestion') or {}
    hoy = {'fecha': X_['fecha'], 'precio': p, 'rec': None if keep else r, 'a25': lo, 'a75': hi, 'n': m['n']}
    P = [h for h in hist if h and h.get('fecha') and h.get('a25')] + [hoy]
    ult = P[-2] if len(P) > 1 else {}
    desde = g.get('desde') or ult.get('fecha') or X_['fecha']
    periodo = (_dt.date.fromisoformat(X_['fecha']) - _dt.date.fromisoformat(desde)).days
    # tarjetas
    def card(v, t, s=''): return f'<div class="kp"><b>{v}</b><span>{t}</span>{f"<i>{s}</i>" if s else ""}</div>'
    cards = ''
    if g:
        cards = (card(g.get('interesados', 0), 'personas preguntaron por tu carro', f'en los últimos {periodo} días')
                 + card(g.get('interesadosTotal', 0), 'interesados en total', 'desde que lo publicamos')
                 + card(g.get('citasTotal', 0), 'citas y visitas agendadas', 'desde que lo publicamos')
                 + card(dias, 'días en vitrina', f'desde el {fcorta(g["inicio"])}' if g.get('inicio') else ''))
    acc = []
    if g.get('canales'): acc.append(f"Tu carro está publicado en {', '.join(g['canales'][:-1])} y {g['canales'][-1]}." if len(g['canales']) > 1 else f"Tu carro está publicado en {g['canales'][0]}.")
    if g.get('republicado'): acc.append(f"El {flarga(g['republicado'][:10])} lo republicamos en Mercado Libre para que vuelva a salir entre las publicaciones recientes.")
    if g.get('interesadosTotal'):
        acc.append(f"Le hicimos seguimiento por WhatsApp o llamada a {g.get('seguimiento', 0)} de las {g['interesadosTotal']} personas que han preguntado por tu carro." if g.get('seguimiento')
                   else f"Atendimos a las {g['interesadosTotal']} personas que han preguntado por tu carro.")
    if g and not g.get('interesados'):
        acc.append('En estos días no llegaron interesados nuevos. Con carros comparables publicados a menor precio, el comprador suele escribirle primero a esos: por eso revisamos el precio contigo.' if not keep and p > hi
                   else 'En estos días no llegaron interesados nuevos; seguimos impulsando la publicación y te avisamos en cuanto alguien pregunte.')
    if ult.get('acordado') and ult.get('decisionFecha'):
        acc.append(f"El {flarga(ult['decisionFecha'])} " + ('aceptaste el precio recomendado y lo publicamos en ' if ult.get('decision') == 'acepta' else 'nos pediste publicarlo en ' if ult.get('decision') == 'propone' else 'decidiste mantener el precio en ') + mill(ult['acordado']) + '; lo actualizamos en todos los canales.')
    acc.append(f"Volvimos a revisar el mercado: hoy analizamos {m['n']} carros comparables publicados" + (f" (en la revisión anterior eran {ult['n']})." if ult.get('n') else '.'))
    accs = ''.join(f'<li>{e(a)}</li>' for a in acc)
    # lectura del precio en el tiempo
    p0 = P[0]
    lect = (f"Desde el primer informe, el {flarga(p0['fecha'])}, el rango competitivo pasó de {mill(p0['a25'])} – {mill(p0['a75'])} a {mill(lo)} – {mill(hi)}"
            + (f", y tu precio de {mill(p0['precio'])} a {mill(p)}." if abs(p0['precio'] - p) >= 0.05 else f", y tu precio se ha mantenido en {mill(p)}."))
    if p > hi + 0.05: lect += ' Hoy tu carro está por encima del rango donde se publica la mayoría de comparables.'
    elif p >= lo: lect += ' Hoy tu carro está dentro del rango competitivo.'
    else: lect += ' Hoy tu carro está por debajo de la mayoría de comparables.'
    filas = ''.join(f"<tr><td>{'Primer informe' if i == 0 else ('Esta revisión' if i == len(P) - 1 else ordinal(i + 1) + ' revisión')}</td><td>{fcorta(x['fecha'])}</td>"
                    f"<td class=n>{mill(x['precio'])}</td><td class=n>{mill(x['a25'])} – {mill(x['a75'])}</td><td class=n>{x.get('n') or '—'}</td>"
                    f"<td class=n>{('Acordado ' + mill(x['acordado'])) if x.get('acordado') else ('Mantener' if not x.get('rec') else mill(x['rec']))}</td></tr>" for i, x in enumerate(P))
    gest = (f"""<div class="sec" style="padding-top:7mm"><h2>LO QUE HICIMOS POR TU CARRO</h2><div class="kps">{cards}</div><ul class="why acc">{accs}</ul></div>""")
    return f"""<div class="pg">
<header class="sm"><img src="data:image/png;base64,{LOGO}"><div class="r"><b>{e(titulo.upper())}</b>{ordinal(num)} revisión · seguimiento de tu carro</div></header>
{gest}
<div class="sec"><h2>CÓMO HA EVOLUCIONADO EL PRECIO</h2><div class="tl">{linea_tiempo(P)}</div>
<div class="leg"><i></i>Rango competitivo del mercado en cada revisión · <b style="color:#0D0D0D">●</b> tu precio publicado · <b style="color:#B8860B">○</b> precio recomendado</div>
<p class="why" style="margin:3mm 0 2.5mm">{e(lect)}</p>
<table><tr><th>Informe</th><th>Fecha</th><th class=n>Tu precio</th><th class=n>Rango competitivo</th><th class=n>Comparables</th><th class=n>Recomendación</th></tr>{filas}</table></div>
<footer class="mini"><div>OnCars · {ordinal(num)} revisión del informe de precio · {e(titulo)}</div><div class="ct">Página 2 de 3</div></footer>
</div>"""

def pagina(X_):
    c = cars[X_['id']]; m = X_['mercado']; rec = X_['rec']; nuevos = X_['nuevos']; nota = X_['nota']; d = det.get(X_['id'], {})
    c = {**c, 'precio': round(X_['precio'] * 1e6), 'km': X_['km']}
    p = X_['precio']; dias = X_['dias']; upd = X_.get('tipo') == 'actualizacion'; prev = X_.get('previo') or {}
    # (nombre, precio de referencia, oficial, 0 km en Mercado Libre); la referencia es el oficial, o el de ML si la marca no publica
    nv = sorted([(q[0], q[1] or q[2], q[1], q[2]) for q in (_pnuevo(n) for n in nuevos) if q], key=lambda x: x[1])
    num = X_.get('numero') or (len(X_.get('historial') or []) + 1 if upd else 1)
    hist = list(X_.get('historial') or ([prev] if upd and prev else []))
    keep = rec is None or rec >= p
    r = p if keep else rec
    lo, hi = m['a25'], m['a75']
    ac = X_.get('acuerdo')  # versión corregida: el dueño ya decidió el precio
    pa = ac['precio'] / 1e6 if ac else p
    if ac: nota = _nota(cars[X_['id']], pa, m, (r if (not keep and pa > r + 0.05) else None), nuevos)
    pts = [p, r, lo, hi, pa] + [x[1] for x in nv[:2]]
    smin, smax = min(pts) * 0.96, max(pts) * 1.03
    X = lambda v: (v - smin) / (smax - smin) * 100
    # barra de rango
    marks = f"""<div class="band" style="left:{X(lo):.1f}%;width:{X(hi)-X(lo):.1f}%"></div>
<div class="mk cur" style="left:{X(pa):.1f}%"><span>{'Precio acordado' if ac else 'Precio actual'}<br><b>{mill(pa)}</b></span></div>"""
    if not keep and not (ac and abs(r - pa) < 0.05):
        marks += f'<div class="mk rec" style="left:{X(r):.1f}%"><span>Recomendado<br><b>{mill(r)}</b></span></div>'
    if nv:
        nmin = nv[0]
        xn = X(nmin[1]); top_clash = abs(xn - X(pa)) < 20
        bot_clash = (not keep) and abs(xn - X(r)) < 20
        pos = 'top:-8.2mm' if not top_clash else ('top:8.6mm' if not bot_clash else 'top:16.5mm')
        marks += f'<div class="mk new" style="left:{xn:.1f}%"><span style="{pos}">Nuevo desde<br><b>{mill(nmin[1])}</b></span></div>'
    comps = ''.join(f"<tr><td>{e(x[4])}</td><td>{km(x[1])}</td><td>{e(x[3])}</td><td class=n>{mill(x[2])}</td></tr>" for x in m['c'][:6])
    news = ''.join(f"<tr><td>{e(n)}</td><td class=n>{mill(of) if of else '<span class=s>No publica</span>'}</td><td class=n>{mill(ml) if ml else '<span class=s>Sin publicaciones</span>'}</td></tr>" for n, v, of, ml in nv)
    if keep:
        verdict = f"""<div class="verdict ok"><div class="lbl">Recomendación</div><div class="big">Mantener {mill(p)}</div>
<div class="sub">{('Tu precio ya está por debajo de la mayoría de carros comparables: hoy el precio no es lo que frena la venta.' if p < lo else 'El precio está dentro del rango competitivo del mercado.')}</div></div>"""
    else:
        dif = p - r
        verdict = f"""<div class="verdict"><div class="lbl">Precio recomendado de publicación</div><div class="big">{mill(r)}</div>
<div class="sub">Ajuste de {mill(dif)} ({str(round(dif/p*100,1)).replace('.',',')} %) frente al precio actual de {mill(p)}.</div></div>"""
    if ac:
        dec_txt = {'acepta': 'Es el precio que te recomendamos y lo confirmaste', 'propone': 'Lo elegiste tú', 'mantiene': 'Decidiste mantener el precio'}[ac['tipo']]
        verdict = f"""<div class="verdict"><div class="lbl">Precio acordado contigo</div><div class="big">{mill(pa)}</div>
<div class="sub">{dec_txt} el {flarga(ac['fecha'][:10])} por WhatsApp.{'' if keep or abs(r - pa) < 0.05 else ' Recomendado por OnCars: ' + mill(r) + '.'}</div></div>"""
    t = dias
    tiempo = (f"{t} días" if t >= 2 else "menos de 2 días")
    titulo = c['marca'] + ' ' + _det.nombre(c) + ' ' + str(c['anio'])
    version = d.get('v') or re.sub(re.escape(_det.nombre(c)), '', c['modelo'].replace('Clase ',''), flags=re.I).strip(' -')
    version = ' '.join(CASE.get(t.lower(), t) for t in version.split())
    info = ' · '.join(x for x in [version, km(c['km']), c.get('trans', ''), c.get('comb', ''), d.get('tr', '') and ('Tracción ' + d['tr'].lower() if d.get('tr') not in ('Delantera',) else 'Tracción delantera')] if x)
    seguimiento = pagina_seguimiento(X_, c, titulo, num, hist, p, r, keep, lo, hi, m, dias) if upd else ''
    ref = X_['id']
    base = f"Hola, soy el dueño del {titulo} (ref. {ref})."
    codigo = lambda tipo, v: f"\n\nCódigo OnCars: {ref}|{tipo}|{round(v * 1e6)}"
    if keep:
        b1 = ('Mantener ' + mill(p), base + f" Apruebo mantener el precio en {mill(p)}." + codigo('mantiene', p))
    else:
        b1 = ('Acepto ' + mill(r), base + f" Apruebo publicarlo en {mill(r)}, el precio recomendado." + codigo('acepta', r))
    responder = 'https://oncarsco.com/informes/responder.html?' + urllib.parse.urlencode({'t': titulo, 'r': ref, 'rec': round(r * 1e6) if not keep else 0, 'act': round(p * 1e6)})
    decide = f"""<div class="sec"><div class="dec"><h2>TU DECISIÓN</h2><p class="why" style="margin:0 0 3mm">Si estás de acuerdo, toca el primer botón. Si prefieres otro precio, toca "Proponer otro precio": se abre una página donde escribes el valor y le das "Enviar propuesta". En los dos casos se abre WhatsApp con tu decisión lista para enviarnos desde tu número, y actualizamos el precio en la web, Mercado Libre y redes.</p>
<div class="btns"><a class="b1" href="{e(walink(b1[1]))}">{e(b1[0])}</a><a class="b2" href="{e(responder)}">Proponer otro precio</a></div></div></div>"""
    if ac:
        pos_txt = (f"A este precio tu carro queda por encima del rango competitivo ({mill(lo)} – {mill(hi)}). Lo publicamos así porque es tu decisión; en la próxima revisión te mostramos cómo está respondiendo el mercado." if pa > hi + 0.05
                   else f"A este precio tu carro queda dentro del rango competitivo del mercado ({mill(lo)} – {mill(hi)})." if pa >= lo
                   else "A este precio tu carro queda por debajo de la mayoría de carros comparables, lo que suele acelerar la venta.")
        rows = [('Informe original', flarga(X_['fecha'])), ('Precio publicado en ese momento', mill(p)),
                ('Recomendación de OnCars', 'Mantener ' + mill(p) if keep else mill(r)),
                ('Tu decisión', {'acepta': 'Aceptaste el precio recomendado', 'propone': 'Propusiste otro precio', 'mantiene': 'Decidiste mantener el precio'}[ac['tipo']]),
                ('Precio acordado', mill(pa)), ('Fecha de la decisión', flarga(ac['fecha'][:10])), ('Canal', 'WhatsApp, desde tu número registrado con OnCars'),
                ('Próxima revisión del mercado', 'En dos semanas, con una actualización de este informe')]
        tr = ''.join(f"<tr><td>{e(a)}</td><td class=n>{e(b)}</td></tr>" for a, b in rows)
        cambiar = 'https://oncarsco.com/informes/responder.html?' + urllib.parse.urlencode({'t': titulo, 'r': ref, 'rec': 0, 'act': round(pa * 1e6)})
        decide = f"""<div class="sec"><div class="dec"><h2>REGISTRO DE TU DECISIÓN</h2><table>{tr}</table>
<p class="why" style="margin:3mm 0">{e(pos_txt)}</p><div class="btns"><a class="b2" href="{e(cambiar)}">Quiero cambiar el precio</a></div></div></div>"""
    npag = 3 if upd else 2
    sig = 'Algunos buscan simplemente un carro, pero otros, buscan tomar decisiones inteligentes. Si ese es tu caso, hablemos.'
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>{FONTS}
@page{{size:A4;margin:0}}*{{box-sizing:border-box}}body{{margin:0;font:10.5pt/1.45 Bric,sans-serif;color:#0D0D0D;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.pg{{width:210mm;height:297mm;position:relative;overflow:hidden}}
header{{background:#0D0D0D;color:#fff;padding:12mm 14mm 9mm;display:flex;justify-content:space-between;align-items:flex-end}}
header img{{height:15mm}}header .r{{text-align:right;font-size:8.5pt;color:#BFBFBF}}header .r b{{display:block;font:9.5pt Mich;color:#F5C643;letter-spacing:.5px;margin-bottom:1mm}}
.car{{padding:7mm 14mm 0}}h1{{font:17pt/1.2 Mich;margin:0 0 1.5mm;letter-spacing:.3px}}.meta{{color:#595959;font-size:9.5pt}}
.row{{display:flex;gap:5mm;padding:5mm 14mm 0}}
.verdict{{flex:1.15;background:#0D0D0D;color:#fff;border-radius:3mm;padding:5mm 6mm;border-left:2.2mm solid #F5C643}}
.verdict.ok{{border-left-color:#BFBFBF}}.lbl{{font-size:8pt;color:#BFBFBF;text-transform:uppercase;letter-spacing:.8px}}
.big{{font:18pt/1.25 Mich;color:#F5C643;margin:1.5mm 0}}.verdict.ok .big{{color:#fff}}.sub{{font-size:9pt;color:#D9D9D9}}
.facts{{flex:1;border:.3mm solid #D9D9D9;border-radius:3mm;padding:4mm 5mm;font-size:9pt}}
.facts div{{display:flex;justify-content:space-between;padding:1.1mm 0;border-bottom:.2mm solid #EEE}}.facts div:last-child{{border:0}}.facts b{{font-weight:700}}
h2{{font:9.5pt Mich;letter-spacing:.4px;margin:0 0 2.5mm;color:#0D0D0D}}
.sec{{padding:6mm 14mm 0}}.note{{font-size:10pt;margin:0}}
.scale{{position:relative;height:36mm;margin:2mm 3mm 0}}.axis{{position:absolute;top:12mm;left:0;right:0;height:1.2mm;background:#E6E6E6;border-radius:1mm}}
.band{{position:absolute;top:10.6mm;height:4mm;background:#F5C643;opacity:.55;border-radius:1mm}}
.mk{{position:absolute;top:8.5mm;width:0;height:7.5mm;border-left:.6mm solid #0D0D0D}}
.mk span{{position:absolute;transform:translateX(-50%);white-space:nowrap;font-size:7.5pt;text-align:center;color:#595959;line-height:1.2}}
.mk b{{color:#0D0D0D;font-size:8pt}}.cur span,.new span{{top:-8.2mm}}.rec span{{top:8.6mm}}
.rec{{border-left-color:#B8860B}}.rec b{{color:#8A6500}}.new{{border-left:.6mm dashed #595959}}
.cur span{{transform:translateX(-50%)}}
.leg{{font-size:7.5pt;color:#595959;margin:1mm 3mm 0}}.leg i{{display:inline-block;width:6mm;height:2.5mm;background:#F5C643;opacity:.55;vertical-align:middle;margin-right:1.5mm;border-radius:.5mm}}
table{{width:100%;border-collapse:collapse;font-size:8.8pt}}th{{text-align:left;font-weight:600;color:#595959;font-size:7.8pt;text-transform:uppercase;letter-spacing:.5px;border-bottom:.4mm solid #0D0D0D;padding:1.2mm 1.5mm}}
td{{padding:1.4mm 1.5mm;border-bottom:.2mm solid #E6E6E6}}td.n,th.n{{text-align:right;white-space:nowrap;font-weight:600}}td.s{{color:#595959;font-size:7.6pt}}
.two{{display:flex;gap:6mm}}.two>div{{flex:1}}
.why{{font-size:9pt;color:#333;margin:0}}.why li{{margin-bottom:1.2mm}}
footer{{position:absolute;bottom:0;left:0;right:0;background:#0D0D0D;color:#BFBFBF;padding:5mm 14mm;font-size:8pt;display:flex;justify-content:space-between;align-items:center;gap:8mm}}
footer.mini{{padding:3mm 14mm;font-size:7.5pt}}header.sm{{padding:7mm 14mm 6mm}}header.sm img{{height:10mm}}footer .sig{{color:#fff;font-size:9pt;max-width:120mm}}footer .ct{{text-align:right;white-space:nowrap}}footer .ct b{{color:#F5C643}}
.dec{{border:.4mm solid #F5C643;border-radius:3mm;padding:4mm 5mm;background:#FFFBEA}}.btns{{display:flex;gap:4mm}}.btns a{{flex:1;display:block;text-align:center;text-decoration:none;border-radius:2mm;padding:3mm 2mm;font:8.5pt Mich;letter-spacing:.3px}}.b1{{background:#0D0D0D;color:#F5C643}}.b2{{background:#fff;color:#0D0D0D;border:.4mm solid #0D0D0D}}
.chg{{border:.3mm solid #D9D9D9;border-radius:3mm;padding:4mm 5mm}}
.kps{{display:flex;gap:3mm;margin:1mm 0 4mm}}.kp{{flex:1;background:#0D0D0D;color:#fff;border-radius:2.5mm;padding:3.5mm 3.5mm 3mm}}.kp b{{display:block;font:20pt/1 Mich;color:#F5C643;margin-bottom:1.5mm}}.kp span{{display:block;font-size:8.3pt;line-height:1.25}}.kp i{{display:block;font-style:normal;font-size:7.3pt;color:#BFBFBF;margin-top:1mm}}
.acc li{{margin-bottom:1.6mm}}.tl{{margin:1mm 0 0}}.method{{position:absolute;bottom:22mm;left:14mm;right:14mm;font-size:7.2pt;color:#7A7A7A;line-height:1.35}}
</style></head><body><div class="pg">
<header><img src="data:image/png;base64,{LOGO}"><div class="r"><b>{('VERSIÓN CORREGIDA · ' if ac else '') + (ordinal(num).upper() + ' REVISIÓN DEL INFORME DE PRECIO' if upd else ('INFORME DE PRECIO' if ac else 'INFORME DE PRECIO DE MERCADO'))}</b>Medellín, {flarga(ac['fecha'][:10] if ac else X_['fecha'])}</div></header>
<div class="car"><h1>{e(titulo)}</h1><div class="meta">{e(info)}</div></div>
<div class="row">{verdict}
<div class="facts"><div><span>{'Precio antes del acuerdo' if ac else 'Precio publicado hoy'}</span><b>{mill(p)}</b></div>
<div><span>Tiempo en vitrina</span><b>{e(tiempo)}</b></div>
<div><span>Carros comparables analizados</span><b>{m['n']}</b></div>
<div><span>Rango competitivo</span><b style='white-space:nowrap'>{mill(lo)} – {mill(hi)}</b></div></div></div>
<div class="sec"><h2>DÓNDE ESTÁ TU CARRO FRENTE AL MERCADO</h2>
<div class="scale"><div class="axis"></div>{marks}</div>
<div class="leg"><i></i>Rango donde se publica la mitad central de los carros comparables, ajustados al año y kilometraje de tu carro.</div></div>
<div class="sec"><p class="note">{e(nota)}</p></div>
<div class="sec two"><div><h2>CARROS SIMILARES EN VENTA HOY</h2>
<table><tr><th>Versión</th><th>Recorrido</th><th>Ciudad</th><th class=n>Precio</th></tr>{comps}</table></div></div>
<footer class="mini"><div>OnCars · {(ordinal(num) + ' revisión del informe') if upd else 'Informe'} de precio · {e(titulo)}</div><div class="ct">Página 1 de {npag}</div></footer>
</div>{seguimiento}<div class="pg">
<header class="sm"><img src="data:image/png;base64,{LOGO}"><div class="r"><b>{e(titulo.upper())}</b>Continuación del informe</div></header>
<div class="sec" style="padding-top:8mm"><h2>CARROS NUEVOS QUE COMPITEN EN ESE PRESUPUESTO</h2>
<p class="why" style="margin:0 0 3mm">Con lo que cuesta tu carro, el comprador también puede mirar estos modelos nuevos. Por eso un usado necesita quedar claramente por debajo, compensando con equipamiento, versión o tamaño. Mostramos dos referencias: el precio oficial que publica cada marca en su página y el carro 0 km más barato de esa versión que ofrecen los concesionarios en Mercado Libre.</p>
<table><tr><th>Modelo</th><th class=n>Precio oficial de la marca</th><th class=n>0 km en Mercado Libre</th></tr>{news}</table></div>
<div class="sec"><h2>POR QUÉ IMPORTA EL PRECIO</h2><ul class="why">
<li>El comprador de hoy compara tu carro con decenas de publicaciones iguales y también con carros nuevos con garantía de fábrica, que hoy llegan con precios muy competitivos.</li>
<li>Los carros publicados dentro del rango competitivo reciben más contactos y se venden en menos tiempo; los que están arriba del rango acumulan días y terminan negociándose más abajo.</li></ul></div>
{decide}<div class="sec"><h2>LO QUE SIGUE</h2><ul class="why">
<li>{('Mientras tanto reforzamos la exposición: pauta con el catálogo de Meta, contenido en redes y seguimiento a cada persona que pregunte.' if keep else 'Mientras tanto seguimos impulsando la publicación en todos nuestros canales.')}</li>
{'' if ac else '<li>En dos semanas volvemos a revisar el mercado y te enviamos una actualización de este informe.</li>'}
<li>Cualquier duda sobre este informe la resolvemos contigo por WhatsApp o llamada.</li></ul></div>
<div class="method">Metodología: publicaciones activas en Mercado Libre Colombia consultadas el {flarga(X_['fecha'])}, del mismo modelo y versión, con un año de diferencia como máximo. Cada precio se ajustó al año y kilometraje de tu carro para poder compararlos. Son precios de publicación, no de cierre: en la negociación suelen bajar. Carros nuevos: precio oficial "desde" publicado en la página de cada marca en Colombia ({FECHA['oficial']}) y publicación 0 km más barata de esa versión en Mercado Libre ({FECHA['ml']}); pueden variar por versión, bonos, promociones y fecha.</div>
<footer><div class="sig">{sig}</div><div class="ct">OnCars · Concesionario virtual<br><b>316 627 9204</b> · oncarsco.com</div></footer>
</div></body></html>"""

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9.\- ]+', ' ', s)).strip()

def archivo(X_):
    c = cars[X_['id']]; k = X_['km']
    pre = 'Actualizacion informe de precio' if X_.get('tipo') == 'actualizacion' else 'Informe de precio'
    if X_.get('acuerdo'): pre += ' corregido'
    return f"{pre} - {slug(c['marca']+' '+_det.nombre(c))} {c['anio']} - {k//1000 if k>=1000 else k}{' mil' if k>=1000 else ''} km.pdf"

def generar(path):
    X_ = json.load(open(path))
    out_dir = R + 'informes/' + X_['token'] + '/'; os.makedirs(out_dir, exist_ok=True)
    name = archivo(X_); tmp = '/tmp/inf_' + X_['token'] + '.html'
    open(tmp, 'w').write(pagina(X_))
    plano = '/tmp/inf_' + X_['token'] + '.pdf'
    subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--no-pdf-header-footer',
                    f'--print-to-pdf={plano}', 'file://' + tmp], capture_output=True, timeout=120)
    # El PDF público queda cifrado (AES-256): solo abre con la clave de 6 dígitos que va en el mensaje al dueño.
    subprocess.run(['qpdf', '--encrypt', X_['clave'], _sec.token_hex(16), '256', '--modify=none', '--',
                    plano, out_dir + name], capture_output=True, timeout=60)
    os.remove(tmp); os.path.exists(plano) and os.remove(plano)
    ok = os.path.exists(out_dir + name)
    m = X_['mercado']
    return {'carId': X_['id'], 'url': 'https://oncarsco.com/informes/' + X_['token'] + '/' + name.replace(' ', '%20'), 'archivo': name,
            'fecha': X_['fecha'], 'tipo': X_.get('tipo', 'inicial'), 'precio': round(X_['precio'] * 1e6), 'rec': round(X_['rec'] * 1e6) if X_['rec'] else None,
            'a25': round(m['a25'] * 1e6), 'a75': round(m['a75'] * 1e6), 'n': m['n'], 'clave': X_['clave'], 'corregido': (X_.get('acuerdo') or {}).get('fecha'), 'numero': X_.get('numero') or 1, 'ok': ok}

if __name__ == '__main__':
    # Uso: python3 _informes/generar.py [MCO-xxx ...]   (sin argumentos: todos los de _informes/datos)
    import glob
    ids = _s.argv[1:]
    files = [D + f'{i}.json' for i in ids] if ids else sorted(f for f in glob.glob(D + '*.json') if not f.endswith('indice.json'))
    idx_p = D + 'indice.json'; idx = json.load(open(idx_p)) if os.path.exists(idx_p) else {}
    for f in files:
        r = generar(f); idx[r['carId']] = r; print(r['carId'], r['ok'], r['archivo'])
    json.dump(idx, open(idx_p, 'w'), ensure_ascii=False, indent=1)
