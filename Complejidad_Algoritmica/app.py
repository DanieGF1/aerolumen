import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from datetime import datetime

from TF3 import construir_grafo, haversine
from backend_mysql import (
    register_user,
    validate_user,
    save_route_for_user,
    get_routes_for_user,
)


# ============================================
# Configuración de la página
# ============================================
st.set_page_config(
    page_title="AeroLumen",
    page_icon="✈️",
    layout="wide"
)

# ==================== ESTILOS ====================
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b3d 50%, #001f4d 100%) !important;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b3d 50%, #001f4d 100%) !important;
    }
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b3d 50%, #001f4d 100%) !important;
    }
    .block-container {
        background: transparent !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #00d4ff !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3) !important;
        font-weight: 700 !important;
    }
    
    .stMarkdown, p, span, label {
        color: #e0f7ff !important;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #00d4ff 0%, #0099ff 100%) !important;
        color: #000000 !important;
        border-radius: 8px !important;
        border: 1px solid #00d4ff !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 700 !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #00f0ff 0%, #00b3ff 100%) !important;
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    div[data-testid="column"]:nth-child(1) {
        background: rgba(0, 212, 255, 0.05) !important;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-right: 1rem !important;
    }

    .stMetric {
        background: rgba(0, 212, 255, 0.08) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================
# Estado de sesión: login
# ============================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if "resultado_ruta" not in st.session_state:
    st.session_state["resultado_ruta"] = None

def mostrar_login():
    st.title("AeroLumen")
    st.subheader("Inicia sesión o regístrate para usar el buscador de rutas aéreas")

    modo = st.radio("¿Qué quieres hacer?", ("Iniciar sesión", "Registrarme"))

    with st.form("auth_form"):
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Continuar")

        if submitted:
            if modo == "Iniciar sesión":
                if validate_user(email, password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = email
                    st.success("Inicio de sesión exitoso ✅")
                    st.rerun()
                else:
                    st.error("Correo o contraseña incorrectos")
            else:  # Registrarme
                ok, msg = register_user(email, password)
                if ok:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = email
                    st.success("Cuenta creada e inicio de sesión exitoso 🎉")
                    st.rerun()
                else:
                    st.error(msg)

if not st.session_state["logged_in"]:
    mostrar_login()
    st.stop()

# ============================================
# Cargar grafo
# ============================================
@st.cache_resource
def cargar_grafo():
    G, airports = construir_grafo()
    return G, airports

G, airports = cargar_grafo()

# ============================================
# Mapas con Folium
# ============================================
def crear_mapa_mundial():
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        min_zoom=1,
        max_zoom=18,
        tiles="CartoDB dark_matter",
        dragging=True,
        touch_zoom=True,
        double_click_zoom=True,
        zoom_control=True,
        scroll_wheel_zoom=True,
        max_bounds=True,
        min_lat=-85,
        max_lat=85,
        min_lon=-180,
        max_lon=180
    )
    return m

def crear_mapa_ruta(path, airports):
    lats = []
    lons = []

    for aid in path:
        info = airports[aid]
        lats.append(info["lat"])
        lons.append(info["lon"])

    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)

    lat_margin = (lat_max - lat_min) * 0.15 if lat_max != lat_min else 10
    lon_margin = (lon_max - lon_min) * 0.15 if lon_max != lon_min else 10

    sw = [lat_min - lat_margin, lon_min - lon_margin]
    ne = [lat_max + lat_margin, lon_max + lon_margin]

    m = folium.Map(
        location=[(lat_min + lat_max) / 2, (lon_min + lon_max) / 2],
        zoom_start=2,
        tiles="CartoDB dark_matter",
        min_zoom=2,
        max_zoom=18,
        dragging=True,
        touch_zoom=True,
        double_click_zoom=True,
        zoom_control=True,
        scroll_wheel_zoom=True,
        max_bounds=True,
        min_lat=lat_min - lat_margin,
        max_lat=lat_max + lat_margin,
        min_lon=lon_min - lon_margin,
        max_lon=lon_max + lon_margin
    )

    route_coords = list(zip(lats, lons))
    folium.PolyLine(
        locations=route_coords,
        color="#00d4ff",
        weight=4,
        opacity=0.9,
        popup="Ruta aérea",
        dash_array="5, 10"
    ).add_to(m)

    for i, aid in enumerate(path):
        info = airports[aid]
        lat = info["lat"]
        lon = info["lon"]

        if i == 0:
            color = "green"
            icon = "play"
            title = f"🟢 Origen: {info['name']}"
        elif i == len(path) - 1:
            color = "red"
            icon = "stop"
            title = f"🔴 Destino: {info['name']}"
        else:
            color = "blue"
            icon = "info-sign"
            title = f"🔵 Escala {i}: {info['name']}"

        folium.Marker(
            location=[lat, lon],
            tooltip=title,
            icon=folium.Icon(color=color, icon=icon, prefix="fa", icon_color="white")
        ).add_to(m)

    m.fit_bounds([sw, ne])
    return m

# ============================================
# Layout principal
# ============================================
# Barra superior
top_left, top_right = st.columns([6, 2])
with top_left:
    st.title("AeroLumen")
with top_right:
    st.write(f"👤 {st.session_state['username']}")
    if st.button("Cerrar sesión"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = None
        st.session_state["resultado_ruta"] = None
        st.rerun()

# Menú lateral: Rutas / Perfil
pagina = st.sidebar.radio("Menú", ["Buscar rutas", "Mi perfil"])

st.write("---")

# ============================================
# Página: Buscar rutas
# ============================================
if pagina == "Buscar rutas":
    st.write("Buscador de rutas aéreas usando Dijkstra.")

    opciones = []
    for aid, info in airports.items():
        etiqueta = f"{aid} - {info['name']} ({info['city']}, {info['country']})"
        opciones.append((etiqueta, aid))

    labels = [o[0] for o in opciones]
    label_to_id = {etq: aid for etq, aid in opciones}

    if not labels:
        st.error("No se cargaron aeropuertos. Revisa los archivos .dat.")
        st.stop()

    col_left, col_right = st.columns([3, 7])

    with col_left:
        st.subheader("Configuración de la ruta")

        origen_label = st.selectbox("Aeropuerto origen", labels, key="origen_sel")
        destino_label = st.selectbox(
            "Aeropuerto destino", labels, index=min(1, len(labels) - 1), key="destino_sel"
        )

        origen = label_to_id[origen_label]
        destino = label_to_id[destino_label]

        buscar = st.button("Buscar camino mínimo", use_container_width=True)

        if buscar:
            if origen not in G or destino not in G:
                st.error("Uno o ambos aeropuertos no existen en el grafo.")
            else:
                try:
                    path = nx.dijkstra_path(G, origen, destino, weight="weight")
                    dist = nx.dijkstra_path_length(G, origen, destino, weight="weight")
                except nx.NetworkXNoPath:
                    st.warning("No existe un camino entre esos aeropuertos.")
                else:
                    costo_km = 0.12
                    combustible_km = 0.004

                    st.session_state["resultado_ruta"] = {
                        "path": path,
                        "dist": dist,
                        "costo": dist * costo_km,
                        "combustible": dist * combustible_km,
                        "origen": origen,
                        "destino": destino,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }

        # Mostrar resumen cuando hay resultado
        resultado = st.session_state["resultado_ruta"]
        if resultado:
            path = resultado["path"]
            dist = resultado["dist"]
            costo_total = resultado["costo"]
            combustible_total = resultado["combustible"]
            origen_id = resultado["origen"]
            destino_id = resultado["destino"]

            st.write("---")
            st.subheader("Resumen del viaje")
            st.write(f"**Distancia total:** {dist:.2f} km")
            st.write(f"**Dinero gastado estimado:** ${costo_total:,.2f} USD")
            st.write(f"**Combustible usado estimado:** {combustible_total:.2f} galones")

            st.subheader("Ruta (aeropuerto por aeropuerto)")
            for aid in path:
                info = airports[aid]
                st.markdown(
                    f"- **{info['name']}** "
                    f"({info['city']}, {info['country']}) — ID: `{aid}`, IATA: `{info['iata']}`"
                )

            st.write("---")
            st.code(" -> ".join(path), language="text")
            st.caption("IDs de los aeropuertos en el orden del camino mínimo.")

            # 🎯 Botón para GUARDAR la ruta en el perfil
            if st.button("💾 Guardar esta ruta en mi perfil"):
                username = st.session_state["username"]
                info_origen = airports[origen_id]
                info_destino = airports[destino_id]

                route_info = {
                    "origen_id": origen_id,
                    "destino_id": destino_id,
                    "origen_name": info_origen["name"],
                    "destino_name": info_destino["name"],
                    "distancia_km": dist,
                    "costo": costo_total,
                    "combustible": combustible_total,
                    "path": path,
                    "fecha": resultado.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M"))
                }

                ok = save_route_for_user(username, route_info)
                if ok:
                    st.success("Ruta guardada en tu perfil ✅")
                else:
                    st.error("No se pudo guardar la ruta (¿usuario inválido?).")

    # Mostrar el mapa
    with col_right:
        st.subheader("Mapa de rutas aéreas")
        resultado = st.session_state["resultado_ruta"]
        if resultado:
            path = resultado["path"]
            m = crear_mapa_ruta(path, airports)
        else:
            m = crear_mapa_mundial()
        st_folium(m, width='100%', height=480)

# ============================================
# Página: Mi perfil
# ============================================
else:  # "Mi perfil"
    st.subheader("Mi perfil — rutas guardadas")

    username = st.session_state["username"]
    rutas = get_routes_for_user(username)

    if not rutas:
        st.info("Aún no has guardado ninguna ruta. Ve a 'Buscar rutas' y guarda una ✈️")
    else:
        for i, r in enumerate(rutas, start=1):
            st.markdown(f"### Ruta {i}")
            st.write(f"**Fecha:** {r.get('fecha', 'N/A')}")
            st.write(f"**Origen:** {r['origen_name']} (`{r['origen_id']}`)")
            st.write(f"**Destino:** {r['destino_name']} (`{r['destino_id']}`)")
            st.write(f"**Distancia:** {r['distancia_km']:.2f} km")
            st.write(f"**Costo estimado:** ${r['costo']:,.2f} USD")
            st.write(f"**Combustible estimado:** {r['combustible']:.2f} gal")

            st.code(r["path_text"], language="text")
            st.write("---")
