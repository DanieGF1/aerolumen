import networkx as nx
import math

# ============================================
# 1. Lectura de archivos .dat
# ============================================
def leer_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# ============================================
# 2. Función de distancia 
# ============================================
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.asin(math.sqrt(a))

# ============================================
# 3. Construcción del grafo
# ============================================
def construir_grafo():
    airports_lines = leer_archivo("airports.dat")
    routes_lines = leer_archivo("routes.dat")

    airports = {}
    for line in airports_lines:
        partes = line.split(",")
        if len(partes) < 8:
            continue

        airport_id = partes[0]
        name = partes[1].replace('"', '')
        city = partes[2].replace('"', '')
        country = partes[3].replace('"', '')
        iata = partes[4].replace('"', '')

        try:
            lat = float(partes[6])
            lon = float(partes[7])
        except:
            continue

        airports[airport_id] = {
            "name": name,
            "city": city,
            "country": country,
            "iata": iata,
            "lat": lat,
            "lon": lon
        }

    G = nx.DiGraph()


    for aid, data in airports.items():
        G.add_node(aid, **data)


    for line in routes_lines:
        partes = line.split(",")
        if len(partes) < 6:
            continue

        src = partes[3]
        dst = partes[5]
        if src == "\\N" or dst == "\\N":
            continue
        if src in airports and dst in airports:
            G.add_edge(src, dst)

 
    for u, v in G.edges():
        a1 = airports[u]
        a2 = airports[v]
        dist = haversine(a1["lat"], a1["lon"], a2["lat"], a2["lon"])
        G[u][v]["weight"] = dist

    return G, airports


# ============================================
# Instalar

# pip install streamlit networkx matplotlib plotly

# Ejecutar con:

# streamlit run app.py
# ============================================