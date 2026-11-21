#!/usr/bin/env python3
"""OnCars · generador de carrusel de Instagram (4:5, 1080x1350).

Uso: python3 post.py spec.json carpeta_salida
spec.json:
{
  "titulo": "Suzuki Fronx", "version": "1.5 GLX Híbrida", "anio": 2025,
  "km": 8100, "precio": 84900000, "trans": "Automática", "comb": "Híbrido",
  "tipo": "SUV / Camioneta", "etiqueta": "Recién llegada",
  "puntos": [{"t": "Título corto", "d": "Una o dos líneas"}, ...],   (3 o 4)
  "fotos": ["foto_principal.jpg", "otra.jpg", ...]                   (1 a 3)
}
Genera 01.png, 02.png, ... en la carpeta de salida.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'assets')
W, H = 1080, 1350
Y = (245, 198, 67); BG = (13, 13, 13); TX = (237, 237, 237); MU = (191, 191, 191)
DIM = (140, 140, 140); LINE = (42, 42, 42); SURF = (24, 24, 24); GR = (89, 89, 89)
M = 72  # margen

def mich(size):
    return ImageFont.truetype(os.path.join(A, 'Michroma-Regular.ttf'), size)

def bri(size, wght=400):
    f = ImageFont.truetype(os.path.join(A, 'Bricolage.ttf'), size)
    try:
        f.set_variation_by_axes([min(96, max(12, size)), wght, 100])
    except Exception:
        pass
    return f

def miles(n):
    return f'{int(n):,}'.replace(',', '.')

def cover(img, w, h):
    iw, ih = img.size
    s = max(w / iw, h / ih)
    img = img.resize((max(w, round(iw * s)), max(h, round(ih * s))), Image.LANCZOS)
    iw, ih = img.size
    l, t = (iw - w) // 2, (ih - h) // 2
    return img.crop((l, t, l + w, t + h))

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(d, text, maker, size, maxw, minsize=30):
    while size > minsize and d.textlength(text, font=maker(size)) > maxw:
        size -= 2
    return maker(size)

def logo(base, x, y, w=150):
    lg = Image.open(os.path.join(A, 'logo.png')).convert('RGBA')
    lg = lg.resize((w, round(lg.height * w / lg.width)), Image.LANCZOS)
    base.alpha_composite(lg, (x, y))
    return lg.height

def header(base, d, n, tot):
    logo(base, M, 40, 130)
    f = bri(28, 500)
    t = f'{n} / {tot}'
    d.text((W - M - d.textlength(t, font=f), 62), t, font=f, fill=DIM)

def chip(d, x, y, text, font, fill=SURF, color=TX):
    tw = d.textlength(text, font=font)
    h = 64
    d.rounded_rectangle((x, y, x + tw + 44, y + h), radius=32, fill=fill)
    d.text((x + 22, y + h / 2), text, font=font, fill=color, anchor='lm')
    return tw + 44

def new():
    im = Image.new('RGBA', (W, H), BG + (255,))
    return im, ImageDraw.Draw(im)

# ---------- slides ----------
def s_portada(S, foto, n, tot):
    im, d = new()
    ph = cover(Image.open(foto).convert('RGB'), W, 780)
    im.paste(ph, (0, 150))
    # degradado inferior de la foto hacia el fondo
    g = Image.new('L', (1, 160))
    for i in range(160):
        g.putpixel((0, i), int(255 * (i / 159) ** 1.6))
    g = g.resize((W, 160))
    im.paste(Image.new('RGB', (W, 160), BG), (0, 930 - 160), g)
    header(im, d, n, tot)
    y = 900
    if S.get('etiqueta'):
        f = bri(30, 650)
        chip(d, M, y - 70, S['etiqueta'].upper(), f, fill=Y, color=BG)
    ft = fit(d, S['titulo'].upper(), mich, 74, W - 2 * M, 44)
    d.text((M, y + 20), S['titulo'].upper(), font=ft, fill=TX)
    fv = bri(40, 400)
    d.text((M, y + 120), f"{S.get('version', '')} · {S['anio']}".strip(' ·'), font=fv, fill=MU)
    fc = bri(32, 550); x = M; cy = y + 190
    for t in [f"{miles(S['km'])} km", S.get('trans'), S.get('comb')]:
        if t:
            x += chip(d, x, cy, t, fc) + 14
    fp = bri(92, 750)
    d.text((M, 1180), f"${miles(S['precio'])}", font=fp, fill=Y)
    fs = bri(30, 500)
    t = 'Desliza  →'
    d.text((W - M - d.textlength(t, font=fs), 1222), t, font=fs, fill=MU)
    return im

def s_foto(S, foto, n, tot):
    im, d = new()
    ph = cover(Image.open(foto).convert('RGB'), W, H)
    im.paste(ph, (0, 0))
    # oscurecer arriba y abajo para el texto
    sh = Image.new('L', (1, H))
    for i in range(H):
        a = 0
        if i < 220: a = int(170 * (1 - i / 220))
        if i > H - 300: a = int(200 * ((i - (H - 300)) / 300))
        sh.putpixel((0, i), a)
    im.paste(Image.new('RGB', (W, H), BG), (0, 0), sh.resize((W, H)))
    header(im, d, n, tot)
    f = mich(40)
    d.text((M, H - 150), S['titulo'].upper(), font=f, fill=TX)
    d.text((M, H - 92), f"{S['anio']} · {miles(S['km'])} km", font=bri(34, 500), fill=Y)
    return im

def s_ficha(S, foto, n, tot):
    im, d = new()
    header(im, d, n, tot)
    d.text((M, 170), 'FICHA RÁPIDA', font=bri(30, 650), fill=Y)
    cells = [('Año', str(S['anio'])), ('Kilometraje', f"{miles(S['km'])} km"),
             ('Transmisión', S.get('trans', '')), ('Combustible', S.get('comb', '')),
             ('Tipo', S.get('tipo', '')), ('Precio', f"${miles(S['precio'])}")]
    cw = (W - 2 * M - 2 * 18) // 3; ch = 150; y0 = 230
    for i, (k, v) in enumerate(cells):
        x = M + (i % 3) * (cw + 18); y = y0 + (i // 3) * (ch + 18)
        d.rounded_rectangle((x, y, x + cw, y + ch), radius=22, fill=SURF)
        d.text((x + 26, y + 26), k, font=bri(26, 500), fill=DIM)
        fv = fit(d, v, lambda s: bri(s, 700), 40, cw - 52, 24)
        d.text((x + 26, y + 76), v, font=fv, fill=Y if k == 'Precio' else TX)
    y = y0 + 2 * ch + 18 + 80
    d.text((M, y), 'POR QUÉ TE CONVIENE', font=bri(30, 650), fill=Y)
    y += 70
    ft, fd = bri(44, 700), bri(34, 400)
    for i, p in enumerate(S['puntos'][:4]):
        d.text((M, y + 4), f'0{i + 1}', font=mich(34), fill=Y)
        tl = wrap(d, p['t'], ft, W - 2 * M - 110)
        for l in tl:
            d.text((M + 110, y), l, font=ft, fill=TX); y += 54
        for l in wrap(d, p.get('d', ''), fd, W - 2 * M - 110)[:2]:
            d.text((M + 110, y + 4), l, font=fd, fill=MU); y += 44
        y += 34
    # franja de foto al pie
    top = max(y + 20, H - 260)
    band = cover(Image.open(foto).convert('RGB'), W, H - top)
    band = ImageEnhance.Brightness(band).enhance(0.8)
    im.paste(band, (0, top))
    g = Image.new('L', (1, 140))
    for i in range(140):
        g.putpixel((0, i), int(255 * (1 - i / 139) ** 1.4))
    im.paste(Image.new('RGB', (W, 140), BG), (0, top), g.resize((W, 140)))
    return im

def s_cta(S, foto, n, tot):
    im, d = new()
    ph = cover(Image.open(foto).convert('RGB'), W, 520)
    ph = ImageEnhance.Brightness(ph).enhance(0.55)
    im.paste(ph, (0, 0))
    g = Image.new('L', (1, 220))
    for i in range(220):
        g.putpixel((0, i), int(255 * (i / 219)))
    im.paste(Image.new('RGB', (W, 220), BG), (0, 300), g.resize((W, 220)))
    t = Image.new('L', (1, 180))
    for i in range(180):
        t.putpixel((0, i), int(200 * (1 - i / 179)))
    im.paste(Image.new('RGB', (W, 180), BG), (0, 0), t.resize((W, 180)))
    header(im, d, n, tot)
    y = 540
    d.text((M, y), '¿Te interesa?', font=mich(64), fill=TX)
    y += 110
    for l in wrap(d, f"Agenda una cita para ver {S['titulo']} {S['anio']} y resolver todas tus dudas. Financiación y seguro en el mismo proceso.", bri(40), W - 2 * M):
        d.text((M, y), l, font=bri(40), fill=MU); y += 54
    y += 40
    wa = Image.open(os.path.join(A, 'wa.png')).convert('RGBA').resize((96, 96), Image.LANCZOS)
    im.alpha_composite(wa, (M, y))
    d.text((M + 120, y + 48), '316 627 9204', font=bri(58, 750), fill=TX, anchor='lm')
    y += 140
    d.text((M, y), 'oncarsco.com', font=mich(38), fill=Y)
    y += 110
    d.line((M, y, W - M, y), fill=LINE, width=2)
    y += 40
    frase = 'Algunos buscan simplemente un carro, pero otros, buscan tomar decisiones inteligentes. Si ese es tu caso, hablemos.'
    for l in wrap(d, frase, bri(32, 400), W - 2 * M):
        d.text((M, y), l, font=bri(32, 400), fill=DIM); y += 44
    return im

def main(spec, out):
    S = json.load(open(spec, encoding='utf-8'))
    fotos = [f for f in S['fotos'] if os.path.exists(f)]
    assert fotos, 'falta la foto principal'
    plan = [('portada', fotos[0])] + [('foto', f) for f in fotos[1:3]] + [('ficha', fotos[0]), ('cta', fotos[0])]
    os.makedirs(out, exist_ok=True)
    fn = {'portada': s_portada, 'foto': s_foto, 'ficha': s_ficha, 'cta': s_cta}
    paths = []
    for i, (k, f) in enumerate(plan, 1):
        im = fn[k](S, f, i, len(plan)).convert('RGB')
        p = os.path.join(out, f'{i:02d}.png'); im.save(p, optimize=True); paths.append(p)
    print('\n'.join(paths))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
