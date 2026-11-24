# Medición de la web (Google Analytics 4). El ID va en _build/config.json -> {"ga": "G-XXXXXXX"}.
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
def ga_id(B):
    p = os.path.join(B, 'config.json')
    return (json.load(open(p)).get('ga') or '').strip() if os.path.exists(p) else ''
