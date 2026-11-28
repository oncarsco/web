# Precios de carros nuevos (millones COP) para la sección "Carros nuevos que compiten".
# Dos fuentes por modelo, lado a lado en el informe:
#   oficial = precio "desde" publicado en la página oficial de la marca en Colombia (precio sugerido al público)
#   ml      = publicación 0 km más barata de esa versión en Mercado Libre (concesionarios), descartando precios atípicos
# None = esa fuente no publica precio para el modelo. Un modelo sin ninguna de las dos no sale en el informe.
# Revisar y actualizar cada mes (la tarea de informes lo hace el primer informe de cada mes; ver LEEME.md).
FECHA = {"oficial": "nov. 2026", "ml": "nov. 2026"}
P = {  # nombre: (oficial, ml, página oficial)
 "Renault Duster 2026": (85.99, 83.27, "renault.com.co"),
 "Chevrolet Tracker 2026": (89.94, 75.99, "chevrolet.com.co"),
 "Kia Stonic 2026": (81.99, 81.79, "kia.com.co"),
 "Volkswagen T-Cross Trendline AT 2026": (84.99, 79.99, "volkswagen.co"),
 "Volkswagen Nivus Comfortline AT 2026": (79.99, 84.99, "volkswagen.co"),
 "Renault Stepway 2026": (86.63, 77.69, "renault.com.co"),
 "Renault Kardian 2026": (79.99, 79.99, "renault.com.co"),
 "Kia K3 Cross 2026": (78.99, 78.79, "kia.com.co"),
 "Suzuki Fronx GLX híbrida 2027": (98.99, 85.89, "suzukiautos.com.co"),
 "Suzuki Swift híbrido 2027": (69.99, None, "suzukiautos.com.co"),
 "Kia Picanto 2026": (57.99, 57.79, "kia.com.co"),
 "Renault Kwid 2026": (49.99, 49.0, "renault.com.co"),
 "Hyundai Grand i10 2026": (59.99, 56.99, "hyundaicolombia.co"),
 "Chevrolet Onix 2026": (79.99, 62.99, "chevrolet.com.co"),
 "Chevrolet Onix Sedán 2026": (73.79, None, "chevrolet.com.co"),
 "Renault Sandero 2026": (None, None, ""),  # ya no está en el portafolio de Renault Colombia
 "Hyundai HB20 2026": (68.99, 70.49, "hyundaicolombia.co"),
 "Mazda 2 Sport 2026": (76.95, None, "mazda.com.co"),
 "Honda City 2026": (75.9, None, "autos.honda.com.co"),
 "Kia Seltos 2.0 AT 2027": (109.99, 107.99, "kia.com.co"),
 "Chery Tiggo 7 Pro MHEV 2026": (109.99, None, "chery.com.co"),
 "Chery Tiggo 4 CSH híbrida 2026": (104.99, None, "chery.com.co"),
 "Changan CS55 Plus Turbo 2026": (119.99, None, "changan.com.co"),
 "Hyundai Tucson 2026": (116.99, 125.0, "hyundaicolombia.co"),
 "Mazda CX-30 2026": (108.15, 108.15, "mazda.com.co"),
 "Volkswagen Taos Comfortline 2026": (106.99, 104.99, "volkswagen.co"),
 "Toyota Yaris Cross 2026": (126.9, 125.9, "toyota.com.co"),
 "Toyota Corolla 2026": (109.9, 109.9, "toyota.com.co"),
 "Toyota Corolla Cross 2026": (139.9, 139.9, "toyota.com.co"),
 "Kia Sportage Desire 2027": (125.99, 121.99, "kia.com.co"),
 "Kia Sportage Vibrant HEV 2027": (139.99, 139.87, "kia.com.co"),
 "Ford Territory Híbrida Trend 2027": (139.99, None, "ford.com.co"),
 "Ford Territory Híbrida Titanium 2027": (168.99, None, "ford.com.co"),
 "Ford Bronco Sport Outer Banks 2025": (154.99, 128.99, "ford.com.co"),
 "Ford Bronco Sport Badlands 2026": (166.99, 166.99, "ford.com.co"),
 "Ford Explorer 2.3 Active 2026": (214.99, 209.99, "ford.com.co"),
 "Ford Explorer ST 2026": (274.99, 259.99, "ford.com.co"),
 "Mazda CX-5 nueva 2026": (157.85, 157.84, "mazda.com.co"),
 "Mazda CX-50 2026": (143.3, 143.3, "mazda.com.co"),
 "Peugeot 3008 Allure 2026": (149.99, None, "peugeot.co"),
 "Peugeot 2008 Híbrida 2027": (109.99, None, "peugeot.co"),
 "Renault Arkana Hybrid 2026": (109.99, None, "renault.com.co"),
 "Hyundai Kona Híbrida 2026": (131.99, 113.99, "hyundaicolombia.co"),
 "Volkswagen Tiguan Life 2026": (124.99, 124.99, "volkswagen.co"),
 "Chevrolet Captiva Híbrida 2026": (154.99, 143.5, "chevrolet.com.co"),
 "Renault Koleos 2026": (149.99, 136.24, "renault.com.co"),
 "BYD Yuan Up 2026": (None, 94.0, "byd.com/co"),
 "BYD Song Plus DM-i 2026": (None, None, "byd.com/co"),
 "Tesla Model Y 2026": (None, None, "tesla.com/es_CO"),
 "Peugeot 5008 Allure 2026": (169.99, 169.99, "peugeot.co"),
 "Hyundai Santa Fe Híbrida 2026": (185.99, None, "hyundaicolombia.co"),
 "Toyota RAV4 2026": (207.5, 234.5, "toyota.com.co"),
 "Mazda CX-60 2026": (199.0, 199.0, "mazda.com.co"),
 "Kia Sorento HEV 2026": (229.99, 216.79, "kia.com.co"),
 "Mazda CX-90 2026": (217.0, 217.0, "mazda.com.co"),
 "Toyota Fortuner 2026": (242.9, 242.9, "toyota.com.co"),
 "Hyundai Palisade Híbrida 2026": (249.99, 248.99, "hyundaicolombia.co"),
 "Chevrolet Traverse 2026": (284.99, 233.99, "chevrolet.com.co"),
 "Chevrolet Tahoe 2026": (379.99, 343.99, "chevrolet.com.co"),
 "Toyota Land Cruiser Prado 2026 (desde)": (315.9, 354.9, "toyota.com.co"),
 "Toyota Hilux 2026 (desde)": (196.5, 259.5, "toyota.com.co"),
 "Toyota Hilux Chasis 2.4 4x4 2026": (176.9, 176.9, "toyota.com.co"),
 "Ford Ranger 2026": (165.99, 185.99, "ford.com.co"),
 "Chevrolet Colorado 2026": (195.49, None, "chevrolet.com.co"),
 "Mercedes-Benz GLA 250 2027": (214.9, 198.2, "mercedes-benz.com.co"),
 "Mercedes-Benz GLC 300 2027": (299.9, 268.0, "mercedes-benz.com.co"),
 "BMW X1 sDrive18i 2027": (184.9, None, "bmw.com.co"),
 "BMW iX1 eDrive20 2027": (214.9, None, "bmw.com.co"),
 "Kia EV5 2027": (139.99, 137.89, "kia.com.co"),
 "Changan CS35 Plus Turbo 2026": (99.99, None, "changan.com.co"),
 "GAC Emzoom 2026": (94.99, None, "gacmotorcolombia.com"),
}
# Nombres viejos que ya están en semillas de informes: apuntan al modelo vigente.
ALIAS = {
 "Chery Tiggo 4 HEV 2026": "Chery Tiggo 4 CSH híbrida 2026",
 "Ford Territory Híbrida Titanium 2026": "Ford Territory Híbrida Titanium 2027",
 "BYD Yuan Up DM-i 2026": "BYD Yuan Up 2026",
 "BMW X1 sDrive18i 2026": "BMW X1 sDrive18i 2027",
 "BMW iX1 eDrive25 2026": "BMW iX1 eDrive20 2027",
}

def precio(n):
    """(nombre vigente, oficial, ml) o None si el modelo no tiene ningún precio."""
    n = ALIAS.get(n, n)
    if n not in P: return None
    of, ml, _ = P[n]
    return (n, of, ml) if (of or ml) else None

# Compatibilidad: N[nombre] = (precio de referencia, fuente). La referencia es el precio oficial; si la marca no publica, el de Mercado Libre.
SRC = {"L": f"Precio oficial de la marca ({FECHA['oficial']})", "M": f"Concesionario en Mercado Libre, 0 km ({FECHA['ml']})"}
N = {}
for _n in list(P) + list(ALIAS):
    _p = precio(_n)
    if _p: N[_n] = (_p[1], "L") if _p[1] else (_p[2], "M")
