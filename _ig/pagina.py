#!/usr/bin/env python3
"""Arma la página "OnCars · Post del día".
Uso: python3 pagina.py spec.json caption.txt carpeta_con_slides salida/index.html "<fecha en texto>"
Las imágenes se publican junto a la página como slides/01.png, slides/02.png, ...
"""
import html, json, os, sys
spec, cap, sd, out, fecha = sys.argv[1:6]
S = json.load(open(spec, encoding='utf-8'))
caption = open(cap, encoding='utf-8').read().strip()
slides = sorted(f for f in os.listdir(sd) if f.endswith('.png'))
imgs = '\n'.join(f'<figure><img src="slides/{f}" alt="Slide {i} de {len(slides)}: {html.escape(S["titulo"])} {S["anio"]}" loading="lazy"><figcaption>{i} / {len(slides)}</figcaption></figure>' for i, f in enumerate(slides, 1))
titulo = f'{S["titulo"]} {S["anio"]}'
page = f'''<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OnCars · Post del día</title>
<style>
:root{{--y:#F5C643;--bg:#0D0D0D;--s:#181818;--tx:#EDEDED;--mu:#BFBFBF;--dim:#8C8C8C;--line:#2A2A2A}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--tx);font:16px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:28px 18px 60px}}
.eb{{color:var(--y);font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;margin:0}}
h1{{font-size:28px;line-height:1.2;margin:6px 0 4px}}.sub{{color:var(--mu);margin:0 0 22px}}
.tira{{display:flex;gap:12px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:10px}}
figure{{margin:0;flex:0 0 78%;max-width:420px;scroll-snap-align:start}}
figure img{{width:100%;aspect-ratio:4/5;display:block;border-radius:12px;background:var(--s)}}
figcaption{{color:var(--dim);font-size:13px;margin-top:6px;text-align:center}}
.card{{background:var(--s);border:1px solid var(--line);border-radius:14px;padding:18px;margin-top:22px}}
pre{{white-space:pre-wrap;font:inherit;margin:0;color:var(--tx)}}
.btns{{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}}
button{{font:inherit;font-weight:700;border:0;border-radius:999px;padding:12px 20px;cursor:pointer;background:var(--y);color:#0D0D0D}}
button:focus-visible{{outline:3px solid var(--tx);outline-offset:2px}}
ol{{color:var(--mu);padding-left:20px;margin:8px 0 0}}li{{margin:4px 0}}
.ok{{color:var(--y);font-size:14px;min-height:20px;margin:8px 0 0}}
</style></head><body><main>
<p class="eb">Post del día · {html.escape(fecha)}</p>
<h1>{html.escape(titulo)}</h1>
<p class="sub">Carrusel 4:5 listo para Instagram. Desliza para ver las {len(slides)} imágenes.</p>
<div class="tira">{imgs}</div>
<div class="card"><p class="eb">Texto de la publicación</p><pre id="cap">{html.escape(caption)}</pre>
<div class="btns"><button id="copiar" type="button">Copiar texto</button></div><p class="ok" id="ok" role="status"></p></div>
<div class="card"><p class="eb">Cómo publicarlo</p><ol>
<li>En el celular, mantén presionada cada imagen y toca Guardar (en orden: 1, 2, 3…).</li>
<li>Toca Copiar texto.</li>
<li>En Instagram, crea una publicación, elige las imágenes en ese orden y pega el texto.</li></ol></div>
</main><script>
document.getElementById('copiar').addEventListener('click',async()=>{{const t=document.getElementById('cap').innerText,o=document.getElementById('ok');try{{await navigator.clipboard.writeText(t);o.textContent='Texto copiado'}}catch(e){{const r=document.createRange();r.selectNodeContents(document.getElementById('cap'));const s=getSelection();s.removeAllRanges();s.addRange(r);o.textContent='Texto seleccionado: cópialo'}}}});
</script></body></html>'''
os.makedirs(os.path.dirname(out) or '.', exist_ok=True)
open(out, 'w', encoding='utf-8').write(page)
print(out)
