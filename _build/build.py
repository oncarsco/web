# Genera index.html, sitemap.xml y robots.txt de oncarsco.com.
# Uso: python3 _build/build.py "19 de noviembre de 2026"   (desde la raíz del repo)
# Entrada: _build/cars.json = lista de carros {id, marca, modelo, anio, km, precio, tipo, comb, trans, url, foto, orden}
#   foto = "fotos/hq/<id>.jpg" (el archivo debe existir); orden = AAAAMMDD de publicación (para "Más recientes").
import json,os,sys
B=os.path.dirname(os.path.abspath(__file__))+'/'; R=os.path.dirname(B.rstrip('/'))+'/'
out=json.load(open(B+'cars.json'))
for c in out: assert os.path.exists(R+c['foto']),'falta foto '+c['foto']
upd=sys.argv[1]
t=open(B+'template.html').read().replace('/*CARS*/[]',json.dumps(out,ensure_ascii=False)).replace('/*UPDATED*/',upd)
SITE='https://oncarsco.com/'
faq=json.load(open(B+'faq.json'))
ld={"@context":"https://schema.org","@graph":[
 {"@type":"AutoDealer","@id":SITE+"#oncars","name":"OnCars","alternateName":"OnCars Concesionario virtual","url":SITE,"logo":SITE+"img/logo.png","image":SITE+"img/og.jpg",
  "description":"Concesionario virtual en Medellín: carros usados, venta de carros en consignación, asesoría de compra, financiación y seguros.",
  "telephone":"+57 316 627 9204","priceRange":"$$","currenciesAccepted":"COP",
  "address":{"@type":"PostalAddress","addressLocality":"Medellín","addressRegion":"Antioquia","addressCountry":"CO"},
  "areaServed":[{"@type":"City","name":"Medellín"},{"@type":"AdministrativeArea","name":"Valle de Aburrá"}],
  "contactPoint":{"@type":"ContactPoint","telephone":"+57 316 627 9204","contactType":"sales","availableLanguage":"es"},
  "sameAs":["https://www.mercadolibre.com.co/pagina/oncarscolombia","https://www.instagram.com/oncars.co/","https://www.tiktok.com/@oncars.co"],
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
    "image":SITE+c['foto'],"url":c['url'],
    "offers":{"@type":"Offer","price":c['precio'],"priceCurrency":"COP","availability":"https://schema.org/InStock","url":c['url'],"seller":{"@id":SITE+"#oncars"}}}}
   for i,c in enumerate(sorted(out,key=lambda c:-c['orden']))]},
 {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
]}
t=t.replace('/*JSONLD*/',json.dumps(ld,ensure_ascii=False).replace('</','<\\/'))
open(R+'index.html','w').write(t)
from datetime import date
open(R+'sitemap.xml','w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE}</loc><lastmod>{date.today()}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url></urlset>\n')
open(R+'robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n')
print('ok',len(out))
