# Informes de precio de mercado para los dueños

Este repositorio es público. Por eso aquí solo están las herramientas: los datos de cada informe (búsqueda, recomendación,
clave del PDF) viven en OnCars OS, colección `informes`, campo `semilla`, y los PDF publicados van cifrados.

- `semilla.py`: trae los datos de OnCars OS a archivos locales (`importar`) y los devuelve (`exportar`).
- `nuevos.py`: precios de carros nuevos (revisar cada mes).
- `scrape.js`: recolecta comparables en Mercado Libre desde el navegador.
- `actualizar.py`: arma el informe nuevo o la actualización (reglas de recomendación dentro).
- `generar.py`: produce el PDF cifrado (AES-256, clave de 6 dígitos por carro, la misma en cada actualización) en
  `informes/<token>/` y escribe `indice.json` en la carpeta de datos.
- Carpeta de datos: variable `INF_DATOS` (por defecto `_informes/datos/`, ignorada por git). Nunca subir datos ni indice.json.
- El PDF trae dos botones que abren WhatsApp hacia OnCars con la respuesta del dueño (acepta el precio o propone otro).
  El equipo la registra en OnCars OS, que muestra los precios pendientes de actualizar en Mercado Libre.
