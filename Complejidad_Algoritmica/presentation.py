import streamlit as st


def render_hero():
    st.markdown(
        """
        <div style="text-align:center; margin-top: 0.5rem; margin-bottom: 1.25rem;">
            <div style="font-size: 2rem; font-weight: 800; color: #00d4ff; text-shadow: 0 0 14px rgba(0,212,255,0.35);">
                🌍 ✈️ Encuentra la mejor ruta aérea en segundos
            </div>
            <div style="font-size: 1.05rem; color: #9dd9ff; margin-top: 0.35rem;">
                Optimiza tu viaje con algoritmos de búsqueda inteligente.
            </div>
            <div style="font-size: 0.95rem; color: #e0f7ff; margin-top: 0.6rem; max-width: 780px; margin-left: auto; margin-right: auto;">
                AeroLumen te permite descubrir rutas aéreas óptimas basadas en el algoritmo de Dijkstra, 
                calculando distancias, escalas, costos y combustible estimado por pasajero.
            </div>
            <div style="margin-top: 1rem;">
                <a href="#" id="go-search" style="display:inline-block; padding: 10px 16px; border-radius: 10px; background: linear-gradient(90deg, #00d4ff, #00b3ff); color:#001228; font-weight: 800; text-decoration:none; box-shadow: 0 0 20px rgba(0,212,255,0.25);">➡️ Ir al buscador de rutas</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col = st.columns([1,1,1])[1]
    with col:
        if st.button("Ir al buscador de rutas", use_container_width=True):
            st.session_state["page"] = "Búsqueda de rutas"
            st.rerun()


def render_que_es():
    st.markdown(
        """
        <div style="background: rgba(0, 12, 40, 0.6); border: 1px solid rgba(0, 212, 255, 0.15); border-radius: 12px; padding: 1rem;">
            <h3 style="margin-top:0;">¿Qué es AeroLumen?</h3>
            <p style="margin:0.4rem 0; color:#e0f7ff;">
                AeroLumen es una plataforma educativa que calcula rutas aéreas óptimas entre miles de aeropuertos del mundo.
                Usamos el algoritmo de Dijkstra para encontrar el camino más eficiente y estimamos distancia, precio del pasaje y consumo de combustible por pasajero.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_features():
    st.markdown("<h3>Características principales</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("Cálculo de rutas con Dijkstra", "Encuentra el camino más corto entre aeropuertos."),
        ("Estimación de costos realistas", "Precio del pasaje basado en consumo y modelo tarifario."),
        ("Visualización en mapa interactivo", "Mapa mundial con marcadores y ruta resaltada."),
        ("Línea de tiempo del recorrido", "Recorrido claro de aeropuerto a aeropuerto."),
    ]

    cols = [c1, c2, c3, c4]
    for (title, desc), col in zip(cards, cols):
        with col:
            st.markdown(
                f"""
                <div style="background: rgba(2, 22, 60, 0.95); border: 1px solid rgba(0, 212, 255, 0.25); border-radius: 12px; padding: 0.9rem; height: 140px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
                    <div style="color:#e0f7ff; font-weight:700;">{title}</div>
                    <div style="color:#9dd9ff; font-size:0.9rem; margin-top:0.35rem;">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_team():
    st.markdown("<h3>Equipo</h3>", unsafe_allow_html=True)


    team = [
        {
            "nombre": "Daniela Gomez",
            "rol": "Colaborador",
            "github": "https://github.com/DanieGF1"  
        },
        {
            "nombre": "Piero Elescano",
            "rol": "Colaborador",
            "github": "https://github.com/PieroHugo"
        },
        {
            "nombre": "Jorge Guevara",
            "rol": "Colaborador",
            "github": "http://github.com/Jorgito170"
        },
    ]

    if not team:
        st.info(".")
        return

    cols = st.columns(len(team)) if len(team) <= 3 else st.columns(3)
    for i, miembro in enumerate(team):
        col = cols[i % len(cols)]
        with col:
           
            gh = miembro.get('github', '').strip()
            username = gh.rstrip('/').split('/')[-1] if gh else ''
            avatar = f"https://github.com/{username}.png" if username else ""

            st.markdown(
                f"""
                <div style='background: rgba(2,22,60,0.9); border:1px solid rgba(0,212,255,0.25); border-radius:12px; padding:0.95rem; margin-bottom:0.9rem; text-align:center;'>
                    <div style='display:flex; align-items:center; justify-content:center; margin-bottom:0.55rem;'>
                        <img src='{avatar}' alt='avatar {username}' style='width:64px;height:64px;border-radius:999px;border:2px solid #00d4ff; box-shadow:0 0 10px rgba(0,212,255,0.25);' />
                    </div>
                    <div style='font-weight:700; color:#e0f7ff; font-size:0.95rem;'>{miembro['nombre']}</div>
                    <div style='color:#00d4ff; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em; margin-top:0.15rem;'>{miembro['rol']}</div>
                    <div style='margin-top:0.45rem;'>
                        <a href='{miembro['github']}' target='_blank' style='color:#9dd9ff; font-size:0.75rem; text-decoration:none;'>@{username}</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )



def render_footer():
    st.markdown(
        """
        <div style="margin-top: 1rem; text-align:center; color:#9dd9ff;">
            <div>Proyecto creado por GRUPO 7</div>
            <div>Complejidad Algorítmica</div>
            <div>AeroLumen © 2025</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_effect():
    st.markdown(
        """
        <div style="text-align:center;font-size:80px;opacity:0.18;">
            ✈️
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_presentation():
    """Renderiza la página Principal usando componentes modulares."""
    render_hero()
    st.write("")
    render_que_es()
    st.write("")
    render_features()
    st.write("")
    render_team()
    st.write("")
    render_effect()
    render_footer()
