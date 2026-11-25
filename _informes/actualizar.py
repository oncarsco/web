# Crea el archivo de datos de un informe nuevo o de una actualización a partir de lo que devolvió scrape.js.
# Uso: python3 _informes/actualizar.py resultados.json AAAA-MM-DD [MCO-xxx ...]
#   resultados.json = JSON.stringify(window.__infOut) guardado en un archivo
# Para cada carro: toma precio, km y fecha de publicación de _build/cars.json, calcula la recomendación con las reglas
# de abajo, escribe la nota y guarda _informes/datos/<id>.json (si ya había un informe, queda como "actualizacion"
# con el anterior en "previo"). Para un carro nuevo, crear antes una semilla
# <INF_DATOS>/<id>.json con {"id":..., "fecha":null, "busqueda":{"path","inc","exc"}, "nuevos":[nombres de nuevos.py]}. Luego correr: python3 _informes/generar.py <ids>
import json, sys, os, datetime, secrets, math
B = os.path.dirname(os.path.abspath(__file__)) + '/'; R = os.path.dirname(B.rstrip('/')) + '/'
sys.path.insert(0, B)
D = os.environ.get('INF_DATOS', B + 'datos/').rstrip('/') + '/'  # datos privados: NO van al repositorio (.gitignore); viven en OnCars OS, informes/<id>.datos
from nuevos import N

def precio_bonito(v):  # redondea hacia abajo a x.900.000 (en millones)
    return math.floor(v + 0.1) - 0.1 if v >= 20 else round(v, 1)

def recomendar(p, m, dias):
    """Reglas (millones COP):
    - Si el precio ya está en la mitad baja del mercado (<= a50): mantener.
    - Si lleva menos de 15 días y está dentro del rango (<= a75): mantener por ahora.
    - Si no: llevarlo al percentil 40 (un poco por debajo del centro) o al 25 si lleva más de 90 días.
    - Nunca se recomienda subir el precio."""
    if m['a50'] is None: return None
    if p <= m['a50']: return None
    if dias < 15 and p <= m['a75']: return None
    obj = m['a25'] if dias > 90 else m['a40']
    r = precio_bonito(obj)
    return r if r < p - 0.5 else None

def nota(car, p, m, rec, nuevos):
    mod = f"{car['marca']} {car['modelo']}".split(' ')[:3]
    c = m['c']; pr = sorted(x[2] for x in c) if c else []
    rango = f"entre {fmt(pr[0])} y {fmt(pr[-1])} millones" if pr else ''
    nmin = min((N[n][0] for n in nuevos), default=None)
    s = f"Hoy hay {m['n']} carros comparables publicados; los más parecidos al tuyo están {rango}." if rango else f"Hoy hay {m['n']} carros comparables publicados."
    if rec: s += f" A {fmt(p)} millones el tuyo queda por encima de la mayoría; alrededor de {fmt(rec)} entra en el grupo que más contactos recibe."
    elif p < m['a25']: s += " Tu precio ya está por debajo de la mayoría."
    else: s += " Tu precio está dentro del rango competitivo."
    if nmin and nmin <= p * 1.1: s += f" Con ese presupuesto también se consigue un carro nuevo desde {fmt(nmin)} millones."
    return s

def fmt(v): return (f"{v:.1f}".rstrip('0').rstrip('.')).replace('.', ',')

if __name__ == '__main__':
    res = json.load(open(sys.argv[1])); fecha = sys.argv[2]; ids = sys.argv[3:] or list(res)
    cars = {x['id']: x for x in json.load(open(R + '_build/cars.json'))}
    hoy = datetime.date.fromisoformat(fecha)
    for i in ids:
        car = cars[i]; m = res[i]; p = car['precio'] / 1e6; o = str(car['orden'])
        dias = (hoy - datetime.date(int(o[:4]), int(o[4:6]), int(o[6:]))).days
        fp = D + f'{i}.json'; old = json.load(open(fp)) if os.path.exists(fp) else None
        if not old or not old.get('nuevos') or not old.get('busqueda'):
            print('FALTA configurar', i, '(busqueda y nuevos): créalo a mano la primera vez'); continue
        rec = recomendar(p, m, dias)
        d = {**old, 'fecha': fecha, 'precio': p, 'km': car['km'], 'anio': car['anio'], 'dias': dias, 'rec': rec, 'mercado': m,
             'nota': nota(car, p, m, rec, old['nuevos']), 'token': secrets.token_hex(8), 'clave': (old or {}).get('clave') or f'{secrets.randbelow(900000)+100000}'}
        if old.get('fecha'):  # ya había informe: esta es una actualización
            d.update(tipo='actualizacion', tokenAnterior=old.get('token'),
                     previo={'fecha': old['fecha'], 'precio': old['precio'], 'rec': old.get('rec'), 'a25': old['mercado']['a25'], 'a75': old['mercado']['a75'], 'n': old['mercado']['n']})
        else:  # carro nuevo: primer informe (el archivo semilla solo trae id, busqueda y nuevos)
            d.update(tipo='inicial', previo=None)
        json.dump(d, open(fp, 'w'), ensure_ascii=False, indent=1)
        print(i, 'rec', rec, 'dias', dias)
