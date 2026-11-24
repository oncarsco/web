# Medición de la web (Google Analytics 4). El ID va en _build/config.json -> {"ga": "G-XXXXXXX"}.
# Píxel de Meta: config.json -> {"fb": "<id>"}. Eventos: PageView, ViewContent (página de carro, content_ids = id del
#   catálogo 'OnCars · Inventario', content_type vehicle), Contact (WhatsApp o llamada), Lead (formularios).
# Si no hay ID, no se inserta nada. Eventos que se registran:
#   whatsapp_click / call_click  (ubicacion: tarjeta, detalle, barra_movil, flotante, encabezado, formulario, otro; car_id, car_name, value)
#   ver_detalles  (desde el catálogo de la página principal)
#   view_item     (al abrir la página de un carro)
#   form_submit   (formularios de vender / asesoría, por el botón que abre WhatsApp)
import json, os
def snippet(ga, car=None):
    if not ga: return ''
    car_js = json.dumps(car or {}, ensure_ascii=False)
    return f'''<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}
gtag('js',new Date());gtag('config','{ga}');
(()=>{{const CAR={car_js};
if(CAR.id)gtag('event','view_item',{{currency:'COP',value:CAR.precio,items:[{{item_id:CAR.id,item_name:CAR.nombre,item_brand:CAR.marca,item_category:CAR.tipo,price:CAR.precio}}]}});
const where=a=>a.closest('.mbar')?'barra_movil':a.closest('.waf')?'flotante':a.closest('header')?'encabezado':a.closest('.card,article')?'tarjeta':a.closest('form,.form')?'formulario':CAR.id?'detalle':'otro';
const info=a=>{{const art=a.closest('[data-id]');const id=art?art.dataset.id:CAR.id;const n=art?art.dataset.name:CAR.nombre;const v=art?Number(art.dataset.price):CAR.precio;return id?{{car_id:id,car_name:n,value:v,currency:'COP'}}:{{}}}};
document.addEventListener('click',e=>{{const a=e.target.closest('a');if(!a)return;const h=a.getAttribute('href')||'';
if(h.includes('wa.me')){{const w=where(a);gtag('event','whatsapp_click',{{ubicacion:w,...info(a)}});if(a.classList.contains('wasend'))gtag('event','form_submit',{{formulario:(a.closest('form')||{{}}).id||''}})}}
else if(h.startsWith('tel:'))gtag('event','call_click',{{ubicacion:where(a),...info(a)}});
else if(h.includes('carro/')&&!CAR.id)gtag('event','ver_detalles',info(a));}},{{capture:true}});}})();
</script>
'''
def pixel(fb, car=None):
    if not fb: return ''
    car_js = json.dumps(car or {}, ensure_ascii=False)
    return f'''<script>
!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','{fb}');fbq('track','PageView');
(()=>{{const CAR={car_js};
const ci=a=>{{const art=a.closest('[data-id]');const id=art?art.dataset.id:CAR.id;const v=art?Number(art.dataset.price):CAR.precio;return id?{{content_ids:[id],content_type:'vehicle',value:v,currency:'COP'}}:{{}}}};
if(CAR.id)fbq('track','ViewContent',{{content_ids:[CAR.id],content_type:'vehicle',content_name:CAR.nombre,value:CAR.precio,currency:'COP'}});
document.addEventListener('click',e=>{{const a=e.target.closest('a');if(!a)return;const h=a.getAttribute('href')||'';
if(h.includes('wa.me')){{if(a.classList.contains('wasend'))fbq('track','Lead',ci(a));else fbq('track','Contact',ci(a))}}
else if(h.startsWith('tel:'))fbq('track','Contact',ci(a));}},{{capture:true}});}})();
</script>
<noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id={fb}&ev=PageView&noscript=1"/></noscript>
'''
def fb_id(B):
    p = os.path.join(B, 'config.json')
    return (json.load(open(p)).get('fb') or '').strip() if os.path.exists(p) else ''
def ga_id(B):
    p = os.path.join(B, 'config.json')
    return (json.load(open(p)).get('ga') or '').strip() if os.path.exists(p) else ''
