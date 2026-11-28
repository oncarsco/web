# Informes de precio de mercado para los dueños

Este repositorio es público. Por eso aquí solo están las herramientas: los datos de cada informe (búsqueda, recomendación,
clave del PDF) viven en OnCars OS, colección `informes`, campo `semilla`, y los PDF publicados van cifrados.

- `semilla.py`: trae los datos de OnCars OS a archivos locales (`importar`) y los devuelve (`exportar`).
- `nuevos.py`: precios de carros nuevos con dos fuentes: precio oficial en la página de cada marca y 0 km más barato en
  Mercado Libre (revisar cada mes; `FECHA` dice cuándo se revisaron).
- `scrape.js`: recolecta comparables en Mercado Libre desde el navegador.
- `actualizar.py`: arma el informe nuevo o la revisión (reglas de recomendación dentro). Guarda `historial` (todos los
  informes anteriores) y `numero` (1 = primer informe, 2 = segunda revisión…).
- `gestion.py`: para las revisiones, cuenta lo que hizo OnCars por el carro en el periodo (interesados, seguimiento,
  citas, canales, republicación) a partir de leads, citas y cars de OnCars OS. Solo conteos, nunca datos de clientes.
  Las revisiones traen una página extra "seguimiento de tu carro" con esa gestión y la línea de tiempo del precio.
- `generar.py`: produce el PDF cifrado (AES-256, clave de 6 dígitos por carro, la misma en cada actualización) en
  `informes/<token>/` y escribe `indice.json` en la carpeta de datos.
- Carpeta de datos: variable `INF_DATOS` (por defecto `_informes/datos/`, ignorada por git). Nunca subir datos ni indice.json.
- El PDF trae dos botones que abren WhatsApp hacia OnCars con la respuesta del dueño (acepta el precio o propone otro).
  El equipo la registra en OnCars OS, que muestra los precios pendientes de actualizar en Mercado Libre.
- `corregir.py`: cuando el dueño decide el precio, prepara la versión corregida del mismo informe (mismo análisis,
  con el precio acordado y el registro de la decisión). Luego se genera con `generar.py`. Ninguna versión se borra:
  OnCars OS guarda la lista en `informes/<id>.versiones`.
