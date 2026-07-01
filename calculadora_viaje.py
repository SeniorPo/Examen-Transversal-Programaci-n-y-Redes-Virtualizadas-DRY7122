
"""
Calculadora de Viaje: Chile <-> Argentina
------------------------------------------
Calcula la distancia real (fórmula de Haversine) entre una ciudad de
Chile y una ciudad de Argentina, estima la duración del viaje según
el medio de transporte elegido y genera una narrativa paso a paso
de la ruta, incluyendo el paso fronterizo cordillerano utilizado.

Autor: Actividad académica
"""

import math
import unicodedata



CIUDADES_CHILE = {
    "santiago":      (-33.4489, -70.6693),
    "valparaiso":    (-33.0472, -71.6127),
    "vina del mar":  (-33.0245, -71.5518),
    "rancagua":      (-34.1708, -70.7444),
    "talca":         (-35.4264, -71.6554),
    "chillan":       (-36.6066, -72.1034),
    "concepcion":    (-36.8201, -73.0444),
    "temuco":        (-38.7359, -72.5904),
    "valdivia":      (-39.8142, -73.2459),
    "osorno":        (-40.5738, -73.1339),
    "puerto montt":  (-41.4693, -72.9424),
    "coyhaique":     (-45.5752, -72.0662),
    "punta arenas":  (-53.1638, -70.9171),
    "la serena":     (-29.9027, -71.2519),
    "copiapo":       (-27.3668, -70.3323),
    "antofagasta":   (-23.6509, -70.3975),
    "calama":        (-22.4667, -68.9333),
    "iquique":       (-20.2141, -70.1522),
    "arica":         (-18.4783, -70.3126),
}

CIUDADES_ARGENTINA = {
    "buenos aires":  (-34.6037, -58.3816),
    "mendoza":       (-32.8908, -68.8272),
    "cordoba":       (-31.4201, -64.1888),
    "rosario":       (-32.9468, -60.6393),
    "san juan":      (-31.5375, -68.5364),
    "la rioja":      (-29.4131, -66.8558),
    "catamarca":     (-28.4696, -65.7852),
    "salta":         (-24.7859, -65.4117),
    "jujuy":         (-24.1858, -65.2995),
    "tucuman":       (-26.8083, -65.2176),
    "santa fe":      (-31.6333, -60.7000),
    "neuquen":       (-38.9516, -68.0591),
    "bariloche":     (-41.1335, -71.3103),
    "rio gallegos":  (-51.6230, -69.2168),
    "ushuaia":       (-54.8019, -68.3030),
    "rio grande":    (-53.7877, -67.7057),
}


PASOS_FRONTERIZOS = {
    "jama":               (-23.1900, -67.2800, 4200),
    "sico":               (-23.6500, -67.8500, 4079),
    "san francisco":      (-26.9300, -68.2400, 4726),
    "agua negra":         (-30.3300, -69.8100, 4780),
    "los libertadores":   (-32.8300, -70.0800, 3200),
    "pehuenche":          (-35.9800, -70.4000, 2553),
    "pino hachado":       (-38.6700, -70.9000, 1884),
    "cardenal samore":    (-40.7500, -71.6800, 1300),
    "huemules / rio mayo":(-45.6300, -71.4300, 590),
    "integracion austral":(-52.4200, -69.6800, 30),
}

CIUDAD_A_PASO = {
    "arica": "jama",
    "iquique": "jama",
    "calama": "jama",
    "antofagasta": "sico",
    "copiapo": "san francisco",
    "la serena": "agua negra",
    "valparaiso": "los libertadores",
    "vina del mar": "los libertadores",
    "santiago": "los libertadores",
    "rancagua": "los libertadores",
    "talca": "pehuenche",
    "chillan": "pehuenche",
    "concepcion": "pino hachado",
    "temuco": "pino hachado",
    "valdivia": "cardenal samore",
    "osorno": "cardenal samore",
    "puerto montt": "cardenal samore",
    "coyhaique": "huemules / rio mayo",
    "punta arenas": "integracion austral",
}



TRANSPORTES = {
    "1": {"nombre": "A pie",        "velocidad": 5,   "verbo": "caminas"},
    "2": {"nombre": "Bicicleta",    "velocidad": 16,  "verbo": "pedaleas"},
    "3": {"nombre": "Automóvil",    "velocidad": 85,  "verbo": "conduces"},
    "4": {"nombre": "Bus",          "velocidad": 75,  "verbo": "viajas en bus"},
    "5": {"nombre": "Avión",        "velocidad": 780,  "verbo": "vuelas"},
}


def normalizar(texto: str) -> str:
    """Quita tildes y pasa a minúsculas para poder comparar nombres de ciudades."""
    texto = texto.strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Calcula la distancia en línea recta (ortodrómica) entre dos puntos, en km."""
    R = 6371.0  
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def km_a_millas(km: float) -> float:
    return km * 0.621371


def formatear_duracion(horas: float) -> str:
    """Convierte horas decimales en un string legible de días/horas/minutos."""
    total_minutos = round(horas * 60)
    dias, resto = divmod(total_minutos, 24 * 60)
    hrs, minutos = divmod(resto, 60)
    partes = []
    if dias:
        partes.append(f"{dias} día(s)")
    if hrs:
        partes.append(f"{hrs} hora(s)")
    if minutos or not partes:
        partes.append(f"{minutos} minuto(s)")
    return ", ".join(partes)


def buscar_ciudad(nombre: str, diccionario: dict):
    clave = normalizar(nombre)
    return diccionario.get(clave), clave


def elegir_transporte() -> dict:
    print("\nMedios de transporte disponibles:")
    for k, v in TRANSPORTES.items():
        print(f"  {k}. {v['nombre']} (~{v['velocidad']} km/h)")
    while True:
        opcion = input("Elige el número del medio de transporte: ").strip()
        if opcion in TRANSPORTES:
            return TRANSPORTES[opcion]
        print("Opción inválida, intenta nuevamente.")


def construir_narrativa(origen_nombre, destino_nombre, transporte,
                         usa_paso, paso_nombre, paso_altitud,
                         dist1_km, dist2_km, dist_total_km):
    verbo = transporte["verbo"]
    nombre_transporte = transporte["nombre"].lower()
    narrativa = []
    narrativa.append(
        f"Tu viaje comienza en {origen_nombre.title()}, Chile. "
        f"Desde aquí, {verbo} en dirección a la Cordillera de los Andes, "
        f"utilizando la ruta hacia el este."
    )

    if usa_paso:
        narrativa.append(
            f"Etapa 1: Recorres aproximadamente {dist1_km:,.1f} km "
            f"({km_a_millas(dist1_km):,.1f} mi) desde {origen_nombre.title()} "
            f"hasta el Paso Fronterizo {paso_nombre.title()}, ubicado a unos "
            f"{paso_altitud:,} metros sobre el nivel del mar."
        )
        narrativa.append(
            f"Etapa 2: Cruzas la frontera internacional en el Paso "
            f"{paso_nombre.title()}, realizando el control aduanero y "
            f"migratorio entre Chile y Argentina."
        )
        narrativa.append(
            f"Etapa 3: Ya en territorio argentino, continúas {verbo} "
            f"{dist2_km:,.1f} km ({km_a_millas(dist2_km):,.1f} mi) más "
            f"hasta llegar a {destino_nombre.title()}, Argentina."
        )
    else:
        narrativa.append(
            f"Al viajar en {nombre_transporte}, tomas una ruta aérea directa "
            f"que sobrevuela la Cordillera de los Andes, cubriendo "
            f"{dist_total_km:,.1f} km ({km_a_millas(dist_total_km):,.1f} mi) "
            f"en línea recta hasta {destino_nombre.title()}, Argentina."
        )

    narrativa.append(
        f"Finalmente, llegas a destino: {destino_nombre.title()}, Argentina. "
        f"¡Viaje completado en {nombre_transporte}!"
    )
    return "\n\n".join(narrativa)




def main():
    print("=" * 70)
    print(" CALCULADORA DE VIAJE: CHILE <-> ARGENTINA ".center(70, "="))
    print("=" * 70)
    print("Escribe 's' en cualquier momento en 'Ciudad de Origen' para salir.\n")

    while True:
        origen_raw = input("Ciudad de Origen (Chile): ").strip()
        if normalizar(origen_raw) == "s":
            print("\n¡Hasta luego! Gracias por usar la calculadora de viaje.")
            break

        origen_coords, origen_clave = buscar_ciudad(origen_raw, CIUDADES_CHILE)
        if not origen_coords:
            print(f"⚠ '{origen_raw}' no está en la librería de ciudades de Chile. "
                  f"Ciudades disponibles: {', '.join(c.title() for c in CIUDADES_CHILE)}\n")
            continue

        destino_raw = input("Ciudad de Destino (Argentina): ").strip()
        if normalizar(destino_raw) == "s":
            print("\n¡Hasta luego! Gracias por usar la calculadora de viaje.")
            break

        destino_coords, destino_clave = buscar_ciudad(destino_raw, CIUDADES_ARGENTINA)
        if not destino_coords:
            print(f"⚠ '{destino_raw}' no está en la librería de ciudades de Argentina. "
                  f"Ciudades disponibles: {', '.join(c.title() for c in CIUDADES_ARGENTINA)}\n")
            continue

        transporte = elegir_transporte()

        lat1, lon1 = origen_coords
        lat2, lon2 = destino_coords

        
        usa_paso = transporte["nombre"] != "Avión"

        if usa_paso:
            paso_clave = CIUDAD_A_PASO.get(origen_clave, "los libertadores")
            paso_lat, paso_lon, paso_alt = PASOS_FRONTERIZOS[paso_clave]
            dist1 = haversine_km(lat1, lon1, paso_lat, paso_lon)
            dist2 = haversine_km(paso_lat, paso_lon, lat2, lon2)
            dist_total = dist1 + dist2
        else:
            paso_clave, paso_alt = None, None
            dist1 = dist2 = 0
            dist_total = haversine_km(lat1, lon1, lat2, lon2)

        millas_total = km_a_millas(dist_total)
        horas_viaje = dist_total / transporte["velocidad"]
        duracion_str = formatear_duracion(horas_viaje)

        print("\n" + "-" * 70)
        print(f"RESUMEN DEL VIAJE: {origen_clave.title()} (Chile) → {destino_clave.title()} (Argentina)")
        print("-" * 70)
        print(f"Medio de transporte : {transporte['nombre']}")
        print(f"Distancia total      : {dist_total:,.1f} km  /  {millas_total:,.1f} millas")
        print(f"Duración estimada    : {duracion_str}")
        print("-" * 70)
        print("\nNARRATIVA DEL VIAJE:\n")
        print(construir_narrativa(
            origen_clave, destino_clave, transporte,
            usa_paso, paso_clave, paso_alt,
            dist1, dist2, dist_total
        ))
        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()