# Los datos de cada informe NO se guardan en este repositorio (es público). Viven en OnCars OS, colección informes,
# campo "semilla". Este script los pasa de OnCars OS a archivos locales y de vuelta.
#   python3 _informes/semilla.py importar informes.json   (informes.json = lista de documentos {id, data} leídos de OnCars OS)
#   python3 _informes/semilla.py exportar MCO-xxx ...      (imprime {id: {url, archivo, fecha, tipo, precio, rec, a25, a75, n, clave, semilla}})
# Carpeta de trabajo: variable INF_DATOS (por defecto _informes/datos/, que está en .gitignore).
import json, os, sys
B = os.path.dirname(os.path.abspath(__file__)) + '/'
D = os.environ.get('INF_DATOS', B + 'datos/').rstrip('/') + '/'
CAMPOS = ('busqueda', 'nuevos', 'fecha', 'precio', 'rec', 'token', 'clave')
if sys.argv[1] == 'importar':
    os.makedirs(D, exist_ok=True); n = 0
    for doc in json.load(open(sys.argv[2])):
        s = (doc.get('data') or doc).get('semilla')
        if not s: continue
        json.dump({'id': doc['id'], **s}, open(D + doc['id'] + '.json', 'w'), ensure_ascii=False, indent=1); n += 1
    print('importados', n)
else:
    idx = json.load(open(D + 'indice.json')); out = {}
    for i in sys.argv[2:]:
        d = json.load(open(D + i + '.json')); r = idx[i]
        out[i] = {k: r[k] for k in ('url', 'archivo', 'fecha', 'tipo', 'precio', 'rec', 'a25', 'a75', 'n', 'clave')}
        out[i]['semilla'] = {**{k: d.get(k) for k in CAMPOS}, 'mercado': {k: d['mercado'][k] for k in ('a25', 'a75', 'n')}}
    print(json.dumps(out, ensure_ascii=False))
