# Versión corregida de un informe: cuando el dueño decide el precio (acepta, propone otro o mantiene), se genera una
# nueva versión del MISMO informe (mismo análisis de mercado) que deja registrada la decisión. El original no se borra.
# Uso: INF_DATOS=<carpeta> python3 _informes/corregir.py MCO-xxx ...   (antes: semilla.py importar; después: generar.py <ids>)
import json, os, sys, secrets
B = os.path.dirname(os.path.abspath(__file__)) + '/'
D = os.environ.get('INF_DATOS', B + 'datos/').rstrip('/') + '/'
for i in sys.argv[1:]:
    f = D + i + '.json'; d = json.load(open(f)); dc = d.get('decision')
    if not dc or dc.get('estado') == 'anulada' or dc.get('informe') != d.get('fecha'):
        print(i, 'sin decisión para este informe'); continue
    if (d.get('acuerdo') or {}).get('id') == dc.get('id'):
        print(i, 'ya tiene su versión corregida'); continue
    d['tokenOriginal'] = d.get('tokenOriginal') or d['token']
    d['acuerdo'] = dc; d['token'] = secrets.token_hex(8)
    json.dump(d, open(f, 'w'), ensure_ascii=False, indent=1); print(i, 'listo para generar', dc['tipo'], dc['precio'])
