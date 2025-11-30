import streamlit as st
import networkx as nx
import folium
from streamlit_folium import st_folium
from datetime import datetime
import re
from perfil import mostrar_perfil
from TF3 import construir_grafo, haversine
from presentation import render_presentation
from backend_mysql import (
    register_user,
    validate_user,
    save_route_for_user,
    get_routes_for_user,
)
from perfil import mostrar_perfil


st.set_page_config(
    page_title="AeroLumen",
    page_icon="✈️",
    layout="wide"
)

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

    /* Columna izquierda de configuración */
    div[data-testid="column"]:nth-child(1) .stVerticalBlock {
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
        padding: 0.7rem !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.1) !important;
    }

    .stMetric label {
        font-size: 0.85rem !important;
    }

    .stMetric [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }

    .stMetric [data-testid="metricDeltaContainer"] {
        font-size: 1.05rem !important;
    }

    /* Navbar horizontal */
    .nav-radio > label {
        font-weight: 600 !important;
        color: #e0f7ff !important;
    }

    /* Tarjeta de leyenda encima del mapa */
    .legend-card {
        background: rgba(0, 12, 40, 0.85);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        display: inline-flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.75rem;
        border: 1px solid rgba(0, 212, 255, 0.3);
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.25);
        font-size: 0.85rem;
    }
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        display: inline-block;
        margin-right: 6px;
    }

    /* Timeline de aeropuertos */
    .timeline-container {
        position: relative;
        margin-top: 1.5rem;
        padding: 1.5rem 1rem 0.5rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(0, 212, 255, 0.15);
        background: rgba(0, 12, 40, 0.6);
        overflow-x: auto;
        white-space: nowrap;
    }
    .timeline-line {
        position: absolute;
        top: 50%;
        left: 5%;
        right: 5%;
        height: 2px;
        background: rgba(0, 212, 255, 0.4);
        z-index: 1;
    }
    .timeline-track {
        display: flex;
        align-items: flex-start;
        gap: 2rem;
        position: relative;
        z-index: 2;
    }
    .timeline-item {
        display: inline-flex;
        flex-direction: column;
        align-items: center;
        min-width: 140px;
    }
    .timeline-dot {
        width: 18px;
        height: 18px;
        border-radius: 999px;
        border: 2px solid #ffffff;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.7);
        margin-bottom: 0.4rem;
    }
    .timeline-card {
        background: rgba(2, 22, 60, 0.95);
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
        border: 1px solid rgba(0, 212, 255, 0.25);
        max-width: 220px;
        text-align: center;
    }
    .timeline-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #e0f7ff;
        margin-bottom: 0.2rem;
    }
    .timeline-meta {
        font-size: 0.72rem;
        color: #9dd9ff;
    }
    .timeline-role {
        font-size: 0.7rem;
        font-weight: 600;
        color: #00d4ff;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    /* Folium/Leaflet tooltip: remove default white wrapper */
    .leaflet-tooltip {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

 
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None

if "resultado_ruta" not in st.session_state:
    st.session_state["resultado_ruta"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "Principal"  


def mostrar_login():
    
    st.markdown(
        """
        <style>
        :root {
            --accent: #00d4ff;
            --danger: #ff4b81;
            --ok: #00ff99;
        }
        /* Contenedor principal sin rectángulo ni fondo */
        .login-wrapper {
            max-width: 680px;
            margin: 2.8rem auto 0 auto;
            padding: 0 0 1.2rem 0;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }
        .login-header {text-align:center; margin-bottom:1.4rem;}
        /* Logo agrandado */
        .login-logo {
            width: 130px; height: 130px; border-radius: 30px;
            display:flex;align-items:center;justify-content:center;
            background: radial-gradient(circle at 40% 30%, #052b55 0%, #03152b 70%);
            border: 3px solid var(--accent);
            font-size: 64px; color: var(--accent);
            margin: 0 auto 1rem auto; position: relative; overflow:hidden;
            box-shadow: 0 0 35px -2px rgba(0,212,255,.55), 0 0 8px rgba(0,212,255,.4) inset;
        }
        .login-logo:before {
            content:''; position:absolute; inset:0; border-radius:30px;
            background: linear-gradient(160deg, rgba(0,212,255,0.15), rgba(0,212,255,0) 40%);
            pointer-events:none;
        }
        .login-title {font-size: 2rem; font-weight:800; letter-spacing:.5px;}
        .login-subtitle {font-size:.95rem; color:#8ecfff;}
        /* Cards permanecen, pero un poco más sutiles */
        .section-card {background: transparent !important; border:none !important; padding:.3rem 0 .2rem 0; border-radius:0; margin-bottom:.4rem; box-shadow:none !important;}
        .strength-bar {height:10px; border-radius:6px; background:#132b40; overflow:hidden; border:1px solid rgba(0,212,255,0.25);}
        .strength-fill {height:100%; transition:width .35s ease;}
        .inline-note {font-size:.7rem; text-transform:uppercase; letter-spacing:.08em; font-weight:600; color:#77c9ff; margin-top:.35rem;}
        .small-link {font-size:.75rem; color:#8ecfff; text-decoration:none;}
        .small-link:hover {text-decoration:underline;}
        .pill-btn button {width:100%; border-radius:999px !important; padding:.68rem 0 !important; font-weight:700 !important; font-size:.95rem !important;}
        .tab-el {margin-top:.4rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="login-header">
          <div class="login-logo">✈️</div>
          <div class="login-title">AeroLumen</div>
          <div class="login-subtitle">Descubre y guarda rutas aéreas óptimas. Accede o crea tu cuenta.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab = st.tabs(["Iniciar sesión", "Registrarme"])

   
    def evaluar_fuerza(pw: str):
        if not pw:
            return 0, "Vacía", "linear-gradient(90deg,#1b3b55,#1b3b55)"
        reglas = [
            len(pw) >= 8,
            re.search(r"[A-Z]", pw) is not None,
            re.search(r"[a-z]", pw) is not None,
            re.search(r"\d", pw) is not None,
            re.search(r"[^A-Za-z0-9]", pw) is not None,
        ]
        score = sum(reglas)
        labels = ["Muy débil", "Débil", "Mejorable", "Media", "Fuerte", "Excelente"]
        colores = [
            "linear-gradient(90deg,#ff4b81,#ff2d60)",
            "linear-gradient(90deg,#ff8633,#ff4b00)",
            "linear-gradient(90deg,#ffc400,#ff9900)",
            "linear-gradient(90deg,#66d977,#32c95b)",
            "linear-gradient(90deg,#00d4ff,#0099ff)",
            "linear-gradient(90deg,#00ff99,#00d4ff)",
        ]
        return score, labels[score], colores[score]

    with login_tab:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        email_login = st.text_input("Correo electrónico", key="login_email", placeholder="usuario@dominio.com")
        pwd_login = st.text_input("Contraseña", type="password", key="login_pwd")
        recordar = st.checkbox("Recordarme", key="login_recordar")
        st.markdown('<div class="pill-btn">', unsafe_allow_html=True)
        login_submit = st.button("Iniciar sesión")
        st.markdown('</div>', unsafe_allow_html=True)
        if login_submit:
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email_login or ""):
                st.error("Formato de correo inválido.")
            elif not pwd_login:
                st.error("Ingresa tu contraseña.")
            else:
                with st.spinner("Verificando credenciales..."):
                    if validate_user(email_login, pwd_login):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = email_login
                        if recordar:
                            st.session_state["remember_email"] = email_login
                        st.success("Inicio de sesión exitoso ✅")
                        st.rerun()
                    else:
                        st.error("Correo o contraseña incorrectos")
        st.markdown('</div>', unsafe_allow_html=True)

    with register_tab:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        email_reg = st.text_input("Correo electrónico", key="reg_email", placeholder="nuevo@dominio.com")
        pwd_reg = st.text_input("Contraseña", type="password", key="reg_pwd")
        pwd_reg2 = st.text_input("Repite contraseña", type="password", key="reg_pwd2")
        score, etiqueta, color_grad = evaluar_fuerza(pwd_reg)
        st.markdown(
            f'<div class="strength-bar"><div class="strength-fill" style="width:{(score/5)*100}%;background:{color_grad}"></div></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f"<div class='inline-note'>Fuerza: {etiqueta}</div>", unsafe_allow_html=True)
        st.markdown('<div class="pill-btn">', unsafe_allow_html=True)
        reg_submit = st.button("Crear cuenta")
        st.markdown('</div>', unsafe_allow_html=True)
        if reg_submit:
            errores = []
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email_reg or ""):
                errores.append("Correo inválido")
            if score < 3:
                errores.append("Contraseña demasiado débil (mínimo media)")
            if pwd_reg != pwd_reg2:
                errores.append("Las contraseñas no coinciden")
            if errores:
                for e in errores:
                    st.error(e)
            else:
                with st.spinner("Creando cuenta..."):
                    ok, msg = register_user(email_reg, pwd_reg)
                    if ok:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = email_reg
                        st.success("Cuenta creada 🎉")
                        st.rerun()
                    else:
                        st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  



if not st.session_state["logged_in"]:
    mostrar_login()
    st.stop()


 

@st.cache_resource
def cargar_grafo():
    G, airports = construir_grafo()
    return G, airports


G, airports = cargar_grafo()


 

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
        max_lon=180,
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
        max_lon=lon_max + lon_margin,
    )

    # Dibujar cada arista con su peso (km) como tooltip
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        info_u = airports[u]
        info_v = airports[v]

        seg_coords = [
            [info_u["lat"], info_u["lon"]],
            [info_v["lat"], info_v["lon"]],
        ]

        # Obtener el peso de la arista desde el grafo (kilómetros)
        try:
            w = G[u][v].get("weight", None)
        except Exception:
            w = None

        label = f"{w:.2f} km" if isinstance(w, (int, float)) else "Distancia"

        folium.PolyLine(
            locations=seg_coords,
            color="#00d4ff",
            weight=4,
            opacity=0.9,
            dash_array="5, 10",
            tooltip=folium.Tooltip(
                f"<div style='background: rgba(2,22,60,0.9); padding: 6px 8px; border: 1px solid #00d4ff; border-radius: 6px; color:#e0f7ff; font-size:12px;'>\n"
                f"<strong>Tramo:</strong> {u} → {v}<br/>\n"
                f"<strong>Peso:</strong> {label}\n"
                f"</div>",
                sticky=True,
                direction="top",
            ),
        ).add_to(m)

    for i, aid in enumerate(path):
        info = airports[aid]
        lat = info["lat"]
        lon = info["lon"]

        if i == 0:
            color = "#00ff99"  # verde origen
            icon = "play"
            role = "ORIGEN"
        elif i == len(path) - 1:
            color = "#ff4b81"  # rojo destino
            icon = "stop"
            role = "DESTINO"
        else:
            color = "#00b3ff"  # cyan escalas
            icon = "info-sign"
            role = f"ESCALA {i}"

        tooltip_html = f"""
        <div style="background: rgba(10,14,39,0.95); border: 1px solid {color}; border-radius: 10px; padding: 10px 12px; color: #e0f7ff; box-shadow: 0 0 15px rgba(0,212,255,0.25);">
            <div style="font-size: 11px; font-weight: 700; letter-spacing: .05em; color: {color}; text-transform: uppercase; margin-bottom: 6px;">{role}</div>
            <div style="font-size: 13px; font-weight: 700;">{info['name']}</div>
            <div style="font-size: 11px; color: #9dd9ff;">{info['city']}, {info['country']}</div>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            tooltip=folium.Tooltip(tooltip_html, sticky=True, direction='top'),
            icon=folium.Icon(color="blue" if i not in (0, len(path)-1) else ("green" if i==0 else "red"), icon=icon, prefix="fa", icon_color="white"),
        ).add_to(m)

    m.fit_bounds([sw, ne])
    return m


# ============================================
# Timeline HTML
# ============================================


def render_timeline(path, airports):
    if not path:
        return ""

    items_html = ""
    for idx, aid in enumerate(path):
        info = airports[aid]
        if idx == 0:
            color = "#00ff99"
            role = "Origen"
        elif idx == len(path) - 1:
            color = "#ff4b81"
            role = "Destino"
        else:
            color = "#00b3ff"
            role = f"Escala {idx}"

        items_html += f"""
        <div class="timeline-item">
            <div class="timeline-dot" style="background:{color};"></div>
            <div class="timeline-card">
                <div class="timeline-role">{role}</div>
                <div class="timeline-title">{info['name']}</div>
                <div class="timeline-meta">
                    {info['city']}, {info['country']}<br/>
                    ID: {aid} · IATA: {info['iata']}
                </div>
            </div>
        </div>
        """

    html = f"""
    <div class="timeline-container">
        <div class="timeline-line"></div>
        <div class="timeline-track">
            {items_html}
        </div>
    </div>
    """
    return html


# ============================================
# Layout superior: logo + usuario + navbar
# ============================================


top_left, top_center, top_right = st.columns([1.5, 2, 2])
with top_left:
    cols_logo = st.columns([0.15, 0.85], gap="small")
    with cols_logo[0]:
        st.markdown(
            """
            <div style="
                width:42px;height:42px;border-radius:999px;
                border:2px solid #00d4ff;display:flex;
                align-items:center;justify-content:center;
                font-size:20px;color:#00d4ff;margin-top:0.25rem;">
                ✈️
            </div>
            """,
            unsafe_allow_html=True,
        )
    with cols_logo[1]:
        st.markdown(
            "<h2 style='margin:0;font-size:1.3rem;line-height:1;'>AeroLumen</h2>",
            unsafe_allow_html=True,
        )

with top_center:
    pass

with top_right:
    pass

st.write("")

col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
with col_nav1:
    if st.button("Principal", key="nav_principal", use_container_width=True):
        st.session_state["page"] = "Principal"
        st.rerun()
with col_nav2:
    if st.button("Búsqueda de rutas", key="nav_busqueda", use_container_width=True):
        st.session_state["page"] = "Búsqueda de rutas"
        st.rerun()
with col_nav3:
    if st.button("Perfil", key="nav_perfil", use_container_width=True):
        st.session_state["page"] = "Perfil"
        st.rerun()

st.markdown("<hr style='margin: 0.3rem 0;'>", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    .stButton>button {
        background: transparent !important;
        color: #000000 !important;
        border: 2px solid #00d4ff !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 700 !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        background: rgba(0, 212, 255, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3) !important;
        transform: translateY(-2px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


nav = st.session_state["page"]

# ============================================
# Página: Principal
# ============================================

if nav == "Principal":
    render_presentation()

# ============================================
# Presentación
# ============================================
# Búsqueda de rutas
# ============================================

elif nav == "Búsqueda de rutas":
   
    st.markdown(
        """
        <h3 style='text-align: left;'>¿UNA RUTA MÁS CORTA A TU DESTINO?</h3>
        
        Ingresa el origen y destino, y descubre los detalles de tu viaje.
        """,
        unsafe_allow_html=True,
    )

   
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
        st.markdown("<h3 style='text-align: left;'>INGRESA</h3>", unsafe_allow_html=True)

        origen_label = st.selectbox("Aeropuerto origen", labels, key="origen_sel")
        destino_label = st.selectbox(
            "Aeropuerto destino",
            labels,
            index=min(1, len(labels) - 1),
            key="destino_sel",
        )

        origen = label_to_id[origen_label]
        destino = label_to_id[destino_label]

        buscar = st.button("Buscar ruta minima", use_container_width=True)

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
                    
                    
                    litros_por_km = 0.03       
                    precio_litro = 0.75        

                    
                    galones_por_km = litros_por_km / 3.785
                    costo_combustible_km = litros_por_km * precio_litro  

                    
                    factor_tarifa = 6
                    tarifa_km = costo_combustible_km * factor_tarifa   

                    # Totales
                    litros_totales = dist * litros_por_km
                    combustible_total = litros_totales / 3.785          
                    precio_total = dist * tarifa_km                       

                    st.session_state["resultado_ruta"] = {
                        "path": path,
                        "dist": dist,
                        "costo": precio_total,
                        "combustible": combustible_total,
                        "origen": origen,
                        "destino": destino,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }

        resultado = st.session_state.get("resultado_ruta")

        if resultado:
            path = resultado["path"]
            dist = resultado["dist"]
            precio_total = resultado["costo"]
            combustible_total = resultado["combustible"]
            origen_id = resultado["origen"]
            destino_id = resultado["destino"]

            st.markdown("<hr style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
            st.subheader("DETALLES")

            colA, colB = st.columns(2)

            with colA:
                st.metric("Distancia", f"{dist:.2f} km")
                st.metric("Precio estimado del pasaje", f"${precio_total:,.2f} USD")

            with colB:
                st.metric("Combustible estimado", f"{combustible_total:.2f} gal")
                st.metric("Escalas", f"{len(path)-2 if len(path)>2 else 0}")

        

          
            num_stops = len(path)
            
            
            width_percent = min(95, max(60, 40 + (num_stops * 8)))
            
            timeline_html = f'<div style="background: transparent; padding: 3rem 0; position: relative; width: {width_percent}vw; margin: 0 0 0 -2rem;">'
            
            timeline_html += '<div style="position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #00ff99 0%, #00d4ff 50%, #ff4b81 100%); z-index: 1;"></div>'

            timeline_html += '<div style="display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 2; min-height: 240px; padding: 0 1rem;">'
            
            for i, aid in enumerate(path):
                info = airports[aid]
                
                if i == 0:
                    color = "#00ff99"
                    role = "ORIGEN"
                    is_endpoint = True
                elif i == len(path) - 1:
                    color = "#ff4b81"
                    role = "DESTINO"
                    is_endpoint = True
                else:
                    color = "#00d4ff"
                    role = f"ESCALA {i}"
                    is_endpoint = False
                
            
                if is_endpoint:
                    is_top = False  
                    top_offset = "0px"
                    position_style = "50%"
                    show_dot = False  
                else:
                    is_top = (i % 2 == 1)
                    top_offset = "50px" if is_top else "-50px"
                    position_style = f"calc(50% + {top_offset})"
                    show_dot = True  
                
                name_short = info['name'][:16]
                
                
                dot_html = f'<div style="width: 12px; height: 12px; border-radius: 50%; background: {color}; border: 2px solid #0a0e27; box-shadow: 0 0 10px {color}; position: absolute; top: 50%; transform: translateY(-50%); z-index: 3;"></div>' if show_dot else ''
                
                timeline_html += f'<div style="flex: 1; display: flex; flex-direction: column; align-items: center; position: relative; min-height: 240px;">{dot_html}<div style="background: rgba(10, 14, 39, 0.9); border: 1px solid {color}50; border-radius: 6px; padding: 0.75rem 1rem; text-align: center; min-width: 135px; position: absolute; top: {position_style}; transform: translateY(-50%); white-space: nowrap; box-shadow: 0 4px 12px rgba(0,0,0,0.3);"><div style="color: {color}; font-weight: bold; font-size: 0.65rem; margin-bottom: 0.35rem; text-transform: uppercase; letter-spacing: 0.05em;">{role}</div><div style="color: #e0f7ff; font-weight: 600; font-size: 0.75rem; margin-bottom: 0.2rem;">{name_short}</div><div style="color: #9dd9ff; font-size: 0.65rem;">{info["iata"]}</div></div></div>'
            
            timeline_html += '</div></div>'
            
            st.markdown(timeline_html, unsafe_allow_html=True)

            if st.button("Guardar esta ruta en mi perfil"):
                username = st.session_state["username"]
                info_origen = airports[origen_id]
                info_destino = airports[destino_id]

                route_info = {
                    "origen_id": origen_id,
                    "destino_id": destino_id,
                    "origen_name": info_origen["name"],
                    "destino_name": info_destino["name"],
                    "distancia_km": dist,
                    "costo": precio_total,
                    "combustible": combustible_total,
                    "path": path,
                    "fecha": resultado.get(
                        "fecha", datetime.now().strftime("%Y-%m-%d %H:%M")
                    ),
                }

                ok = save_route_for_user(username, route_info)
                if ok:
                    st.success("Ruta guardada en tu perfil ✅")
                else:
                    st.error("No se pudo guardar la ruta (¿usuario inválido?).")

   
    with col_right:
        st.subheader("MAPA DE LA RUTA AÉREA")

        # Leyenda arriba a la derecha, más pegada al mapa
        st.markdown(
            """
            <div class="legend-card" style="float: right; margin: 0 0 -1.4rem 1rem; position: relative; top: -12px;">
                <div><span class="legend-dot" style="background:#00ff99;"></span>Origen</div>
                <div><span class="legend-dot" style="background:#ff4b81;"></span>Destino</div>
                <div><span class="legend-dot" style="background:#00b3ff;"></span>Escalas</div>
                <div><span class="legend-dot" style="background:#00d4ff;"></span>Ruta aérea</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        resultado = st.session_state["resultado_ruta"]
        if resultado:
            path = resultado["path"]
            m = crear_mapa_ruta(path, airports)
        else:
            m = crear_mapa_mundial()

        st_folium(m, width="100%", height=460)

# ============================================
# Página: Perfil
# ============================================
else:  # Perfil
    username = st.session_state.get("username")
    if not username:
        st.error("No hay usuario activo. Inicia sesión nuevamente.")
    else:
        mostrar_perfil(username)
