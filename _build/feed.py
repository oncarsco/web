# Feeds de catálogo para Meta (pauta). Se generan en cada build:
#   feed/meta-vehiculos.csv  -> catálogo tipo "Vehículos" (anuncios de inventario automotriz)
#   feed/meta-productos.csv  -> catálogo tipo "Comercio electrónico" (alternativa si Vehículos no está disponible)
# Dirección: OnCars es virtual (no se atiende en la dirección registrada), por eso addr1 = 'Medellín'.
# Meta los lee por URL programada, así que se mantienen al día con cada sincronización del inventario.
import csv, os
SITE = 'https://oncarsco.com/'
UTM = '?utm_source=meta&utm_medium=catalogo'
IMG = 'https://http2.mlstatic.com/D_NQ_NP_2X_{}-F.jpg'
BODY = {'SUV / Camioneta': 'SUV', 'Automóvil': 'SEDAN', 'Pick-up': 'TRUCK'}
FUEL = {'Gasolina': 'GASOLINE', 'Diésel': 'DIESEL', 'Eléctrico': 'ELECTRIC', 'Híbrido': 'HYBRID',
        'Híbrido ligero': 'HYBRID', 'Híbrido / Diésel': 'HYBRID'}
DRIVE = {'Delantera': 'FWD', '4x4': '4X4', '4x2': '4X2', 'Trasera': 'RWD', 'AWD': 'AWD'}
FIRMA = 'Algunos buscan simplemente un carro, pero otros, buscan tomar decisiones inteligentes. Si ese es tu caso, hablemos.'


def _fotos(c, det):
    f = [IMG.format(x) for x in det.get('f', [])]
    return f or [SITE + c['foto']]


def _desc(c, det, nombre):
    base = det.get('d') or f"{c['marca']} {nombre} {c['anio']}, {c['km']:,} km.".replace(',', '.')
    return (base + ' Revisado por OnCars, con acompañamiento en el traspaso y opción de financiación. ' + FIRMA)[:4900]


def generar(R, out, det_all, slug, nombre):
    os.makedirs(R + 'feed', exist_ok=True)
    veh, prod = [], []
    for c in out:
        det = det_all.get(c['id'], {})
        fotos = _fotos(c, det)
        n = nombre(c)
        titulo = f"{c['marca']} {n} {det.get('v', '')} {c['anio']}".replace('  ', ' ').strip()
        url = SITE + 'carro/' + slug(c) + '/' + UTM
        desc = _desc(c, det, n)
        r = {'vehicle_id': c['id'], 'title': titulo, 'description': desc, 'url': url,
             'make': c['marca'], 'model': n, 'year': c['anio'],
             'mileage.value': c['km'], 'mileage.unit': 'KM',
             'body_style': BODY.get(c.get('tipo'), 'OTHER'),
             'price': f"{c['precio']} COP", 'exterior_color': det.get('co') or 'Otro',
             'state_of_vehicle': 'Used', 'condition': 'EXCELLENT',
             'transmission': 'Manual' if c.get('trans') == 'Mecánica' else 'Automatic',
             'fuel_type': FUEL.get(c.get('comb'), 'OTHER'),
             'drivetrain': DRIVE.get(det.get('tr'), 'Other'),
             'availability': 'available',
             'address.addr1': 'Medellín', 'address.city': 'Medellín', 'address.region': 'Antioquia', 'address.country': 'CO',
             'latitude': '6.2442', 'longitude': '-75.5812'}
        for i, u in enumerate(fotos[:20]):
            r[f'image[{i}].url'] = u
        veh.append(r)
        prod.append({'id': c['id'], 'title': titulo[:150], 'description': desc, 'availability': 'in stock',
                     'condition': 'used', 'price': f"{c['precio']} COP", 'link': url,
                     'image_link': fotos[0], 'additional_image_link': ','.join(fotos[1:11]),
                     'brand': c['marca'], 'google_product_category': '916',
                     'custom_label_0': c.get('tipo', ''), 'custom_label_1': str(c['anio']),
                     'custom_label_2': 'Hasta 80M' if c['precio'] <= 80e6 else ('80M a 120M' if c['precio'] <= 120e6 else 'Más de 120M')})
    nimg = max(len([k for k in r if k.startswith('image[')]) for r in veh)
    cols = ['vehicle_id', 'title', 'description', 'url', 'make', 'model', 'year', 'mileage.value', 'mileage.unit',
            'body_style', 'price', 'exterior_color', 'state_of_vehicle', 'condition', 'transmission', 'fuel_type',
            'drivetrain', 'availability', 'address.addr1', 'address.city', 'address.region', 'address.country', 'latitude', 'longitude'] \
        + [f'image[{i}].url' for i in range(nimg)]
    for nom, filas, cs in (('meta-vehiculos.csv', veh, cols), ('meta-productos.csv', prod, list(prod[0]))):
        with open(R + 'feed/' + nom, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=cs, extrasaction='ignore')
            w.writeheader(); w.writerows(filas)
    return len(veh)
