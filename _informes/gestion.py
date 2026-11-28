# Gestión de OnCars para las revisiones del informe (segunda, tercera…): lo que hicimos por el carro en el periodo.
# Uso: INF_DATOS=<carpeta> python3 _informes/gestion.py <base.json> AAAA-MM-DD MCO-xxx ...
#   base.json = {"cars": [...], "leads": [...], "citas": [...]}: documentos leídos de OnCars OS, cada uno {id, data} o plano.
# Se corre DESPUÉS de actualizar.py y ANTES de generar.py. Escribe el campo "gestion" en <INF_DATOS>/<id>.json.
# Solo guarda conteos y fechas: nunca nombres ni teléfonos de clientes (el informe va al dueño).
import json, os, sys, datetime
B = os.path.dirname(os.path.abspath(__file__)) + '/'
D = os.environ.get('INF_DATOS', B + 'datos/').rstrip('/') + '/'

def plano(x): return {'id': x.get('id'), **(x.get('data') or {})} if 'data' in x else x
def dia(s): return (s or '')[:10]

# Canales que siempre tiene un carro activo de OnCars, además de los que el equipo marque en el carro.
FIJOS = ['Mercado Libre', 'oncarsco.com (página propia del carro)', 'Catálogo de Facebook e Instagram']

def calcular(car, leads, citas, desde, hasta):
    ids = {car['id'], car.get('mlId')} | set(car.get('mlHistorial') or [])
    ids.discard(None)
    inicio =car.get('fechaIngreso') or car.get('fechaPublicacion') or desde
    L = []
    for l in leads:
        if l.get('carId') in ids: f = dia(l.get('fechaML') or l.get('fecha'))
        elif ids & set(l.get('otrosCarros') or []): f = dia(l.get('fecha'))
        else: continue
        L.append((f, l))
    per = [l for f, l in L if desde < f <= hasta]
    tot = [l for f, l in L if f >= inicio]
    C = [c for c in citas if c.get('carId') in ids and c.get('estado') != 'cancelada']
    canales = list(FIJOS)
    for c in car.get('canales') or []:
        if c != 'Mercado Libre' and c not in canales: canales.append(c)
    rep = car.get('fechaPublicacion') if (car.get('republicaciones') or 0) > 0 and desde < dia(car.get('fechaPublicacion')) <= hasta else None
    return {'desde': desde, 'hasta': hasta, 'inicio': inicio,
            'interesados': len(per), 'interesadosTotal': len(tot),
            'seguimiento': sum(1 for l in tot if l.get('etapa') not in (None, '', 'nuevo')),
            'citas': sum(1 for c in C if desde < dia(c.get('fecha')) <= hasta), 'citasTotal': sum(1 for c in C if dia(c.get('fecha')) >= inicio),
            'canales': canales, 'republicado': rep}

if __name__ == '__main__':
    base = json.load(open(sys.argv[1])); hoy = sys.argv[2]
    cars = {plano(c)['id']: plano(c) for c in base.get('cars', [])}
    leads = [plano(x) for x in base.get('leads', [])]; citas = [plano(x) for x in base.get('citas', [])]
    for i in sys.argv[3:]:
        f = D + i + '.json'; d = json.load(open(f))
        car = cars.get(i) or next((c for c in cars.values() if c.get('mlId') == i), None)
        if not car: print(i, 'no está en cars'); continue
        if (d.get('numero') or 1) < 2: print(i, 'primer informe: sin sección de gestión'); continue
        desde = (d.get('historial') or [{}])[-1].get('fecha') or hoy
        d['gestion'] = calcular(car, leads, citas, desde, hoy)
        json.dump(d, open(f, 'w'), ensure_ascii=False, indent=1)
        g = d['gestion']; print(i, f"interesados {g['interesados']} (total {g['interesadosTotal']}), citas {g['citas']}, republicado {g['republicado']}")
