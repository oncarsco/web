# Genera index.html, sitemap.xml y robots.txt de oncarsco.com.
# Uso: python3 _build/build.py "19 de noviembre de 2026"   (desde la raíz del repo)
# Entrada: _build/cars.json = lista de carros {id, marca, modelo, anio, km, precio, tipo, comb, trans, url, foto, orden}
#   foto = "fotos/hq/<id>.jpg" (el archivo debe existir); orden = AAAAMMDD de publicación (para "Más recientes").
import json,os,sys
B=os.path.dirname(os.path.abspath(__file__))+'/'; R=os.path.dirname(B.rstrip('/'))+'/'
out=json.load(open(B+'cars.json'))
for c in out: assert os.path.exists(R+c['foto']),'falta foto '+c['foto']
upd=sys.argv[1]
sys.path.insert(0,B); import detalle, shutil, analitica
GA=analitica.ga_id(B)
for c in out: c['p']=detalle.slug(c)
pub=[{k:v for k,v in c.items() if k!='notas'} for c in out]
tpl=open(B+'template.html').read()
t=tpl.replace('/*CARS*/[]',json.dumps(pub,ensure_ascii=False)).replace('/*UPDATED*/',upd).replace('</head>',analitica.snippet(GA)+'</head>',1)
SITE='https://oncarsco.com/'
# Entrega: en Medellín se entrega sin costo; a otras ciudades se lleva y el traslado lo paga el comprador (costo variable, no se publica tarifa).
SHIP={"@type":"OfferShippingDetails","shippingDestination":{"@type":"DefinedRegion","addressCountry":"CO","addressRegion":"ANT"},
      "shippingRate":{"@type":"MonetaryAmount","value":0,"currency":"COP"},
      "deliveryTime":{"@type":"ShippingDeliveryTime","handlingTime":{"@type":"QuantitativeValue","minValue":0,"maxValue":3,"unitCode":"DAY"},"transitTime":{"@type":"QuantitativeValue","minValue":0,"maxValue":1,"unitCode":"DAY"}}}
# Venta definitiva: después de la entrega no se aceptan devoluciones.
RET={"@type":"MerchantReturnPolicy","applicableCountry":"CO","returnPolicyCategory":"https://schema.org/MerchantReturnNotPermitted"}
faq=json.load(open(B+'faq.json'))
ld={"@context":"https://schema.org","@graph":[
 {"@type":"AutoDealer","@id":SITE+"#oncars","name":"OnCars","alternateName":"OnCars Concesionario virtual","url":SITE,"logo":SITE+"img/logo.png","image":SITE+"img/og.jpg",
  "description":"Concesionario virtual en Medellín: carros usados, venta de carros en consignación, asesoría de compra, financiación y seguros.",
  "telephone":"+57 316 627 9204","priceRange":"$$","currenciesAccepted":"COP",
  "address":{"@type":"PostalAddress","addressLocality":"Medellín","addressRegion":"Antioquia","addressCountry":"CO"},
  "areaServed":[{"@type":"City","name":"Medellín"},{"@type":"AdministrativeArea","name":"Valle de Aburrá"}],
  "contactPoint":{"@type":"ContactPoint","telephone":"+57 316 627 9204","contactType":"sales","availableLanguage":"es"},
  "sameAs":["https://www.mercadolibre.com.co/pagina/oncarscolombia","https://www.instagram.com/oncars.co/","https://www.tiktok.com/@oncars.co","https://maps.app.goo.gl/oDvahX1icmHbk4XJ8"],
  "hasMap":"https://maps.app.goo.gl/oDvahX1icmHbk4XJ8",
  "hasOfferCatalog":{"@type":"OfferCatalog","name":"Asesoría de compra de carro","itemListElement":[
   {"@type":"Offer","name":n,"price":pr,"priceCurrency":"COP","itemOffered":{"@type":"Service","name":n,"description":d,"areaServed":"Medellín"}}
   for n,pr,d in [("Revisión de un carro",200000,"Revisión de precio e informe de historial vehicular (reclamaciones, accidentes, propietarios, RUNT, SIMIT, multas y prenda) de un carro que ya encontraste."),
                  ("Asesoría de compra",600000,"Definimos qué carro te conviene, comparamos opciones y te acompañamos en la compra."),
                  ("Te lo conseguimos",1200000,"Buscamos, verificamos y negociamos el carro por ti. Peritaje aparte.")]]}},
 {"@type":"WebSite","@id":SITE+"#web","url":SITE,"name":"OnCars","inLanguage":"es-CO","publisher":{"@id":SITE+"#oncars"}},
 {"@type":"ItemList","name":"Carros usados disponibles en OnCars","numberOfItems":len(out),"itemListElement":[
   {"@type":"ListItem","position":i+1,"item":{"@type":"Car","name":f"{c['marca']} {c['modelo']} {c['anio']}","brand":{"@type":"Brand","name":c['marca']},
    "model":c['modelo'],"vehicleModelDate":str(c['anio']),"mileageFromOdometer":{"@type":"QuantitativeValue","value":c['km'],"unitCode":"KMT"},
    "vehicleTransmission":c.get('trans'),"fuelType":c.get('comb'),"bodyType":c.get('tipo'),"itemCondition":"https://schema.org/UsedCondition",
    "image":SITE+c['foto'],"url":SITE+'carro/'+c['p']+'/',
    "offers":{"@type":"Offer","price":c['precio'],"priceCurrency":"COP","availability":"https://schema.org/InStock","url":SITE+'carro/'+c['p']+'/',"seller":{"@id":SITE+"#oncars"},"shippingDetails":SHIP,"hasMerchantReturnPolicy":RET}}}
   for i,c in enumerate(sorted(out,key=lambda c:-c['orden']))]},
 {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
]}
t=t.replace('/*JSONLD*/',json.dumps(ld,ensure_ascii=False).replace('</','<\\/'))
open(R+'index.html','w').write(t)
from datetime import date
# Páginas de detalle (se regeneran completas: las de carros que ya no están desaparecen)
det=json.load(open(B+'detalles.json')) if os.path.exists(B+'detalles.json') else {}
css=tpl.split('<style>',1)[1].split('</style>',1)[0]
shutil.rmtree(R+'carro',ignore_errors=True)
for c in out:
    sl,h=detalle.pagina(c,det.get(c['id'],{}),css,out)
    h=h.replace('</head>',analitica.snippet(GA,{'id':c['id'],'nombre':c['marca']+' '+detalle.nombre(c)+' '+str(c['anio']),'marca':c['marca'],'tipo':c.get('tipo',''),'precio':c['precio']})+'</head>',1)
    os.makedirs(R+'carro/'+sl,exist_ok=True); open(R+'carro/'+sl+'/index.html','w').write(h)
sin=[c['id'] for c in out if c['id'] not in det]
if sin: print('sin detalles de la publicación:',' '.join(sin))
open(R+'404.html','w').write('<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Este carro ya no está disponible | OnCars</title><meta name="robots" content="noindex"><meta http-equiv="refresh" content="4;url=/#carros"><style>body{margin:0;background:#0D0D0D;color:#EDEDED;font:17px/1.5 system-ui,sans-serif;display:grid;place-items:center;min-height:100vh;text-align:center;padding:24px}a{color:#0D0D0D;background:#F5C643;padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:700;display:inline-block;margin-top:16px}</style></head><body><div><img src="/img/logo.png" alt="OnCars" style="height:44px;margin:0 auto 18px"><h1 style="font-size:22px;margin:0">Este carro ya no está disponible</h1><p style="color:#BFBFBF">Puede que ya se haya vendido. Mira los carros que tenemos hoy.</p><a href="/#carros">Ver carros disponibles</a></div></body></html>')
urls=[(SITE,'1.0','daily')]+[(SITE+'carro/'+c['p']+'/','0.8','weekly') for c in out]
open(R+'sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{u}</loc><lastmod>{date.today()}</lastmod><changefreq>{f}</changefreq><priority>{p}</priority></url>' for u,p,f in urls)+'</urlset>\n')
open(R+'robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n')
print('ok',len(out))
