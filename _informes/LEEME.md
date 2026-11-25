# Informes de precio de mercado para los dueños

- `datos/<MCO-id>.json`: lo que alimenta cada informe (búsqueda en Mercado Libre, carros nuevos que compiten, estadísticas, recomendación, nota). Sin datos personales del dueño.
- `nuevos.py`: precios de carros nuevos (revisar cada mes).
- `scrape.js`: recolecta comparables en Mercado Libre desde el navegador.
- `actualizar.py`: arma el informe nuevo o la actualización (reglas de recomendación dentro).
- `generar.py`: produce el PDF en `informes/<token>/` y actualiza `indice.json`.
- Los PDF se sirven en oncarsco.com/informes/<token>/ (rutas no indexadas: robots.txt) y se registran en la base de OnCars OS, colección `informes`, donde el equipo los descarga y los envía por WhatsApp.
