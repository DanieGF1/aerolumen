import streamlit as st
from backend_mysql import (
    get_user_profile,
    update_user_profile,
    get_routes_for_user,
    delete_route_for_user,
)

@st.cache_data
def load_profile_and_routes(username: str):
    profile = get_user_profile(username)
    rutas = get_routes_for_user(username)
    return profile, rutas


def mostrar_perfil(username: str):
    profile = get_user_profile(username)
    rutas = get_routes_for_user(username)

    full_name = profile.get("full_name") if profile else None
    avatar_url = profile.get("avatar_url") if profile else None
    created_at = profile.get("created_at") if profile else None

    header_left, header_right = st.columns([4, 2])

    with header_left:
        avatar_html = """
        <div style="
            width:140px;height:140px;border-radius:999px;
            border:3px solid #00d4ff;display:flex;
            align-items:center;justify-content:center;
            overflow:hidden;background:#021226;
        ">
        """
        if avatar_url:
            avatar_html += f'<img src="{avatar_url}" style="width:100%;height:100%;object-fit:cover;">'
        else:
            avatar_html += '<span style="font-size:38px;color:#00d4ff;">👤</span>'
        avatar_html += "</div>"

        cols = st.columns([0.16, 0.84])
        with cols[0]:
            st.markdown(avatar_html, unsafe_allow_html=True)
        with cols[1]:
            st.markdown(
                f"""
                <div style=\"display:flex; flex-direction:column; justify-content:center; min-height:140px; margin-left:1.75rem;\">
                  <div style="font-size:1.4rem;font-weight:700;color:#e0f7ff; line-height:1.2;">
                      {full_name or "Usuario sin nombre"}
                  </div>
                  <div style="color:#7fd3ff; margin-top:0.15rem;">{username}</div>
                  <div style="font-size:0.85rem;color:#6fa3d8; margin-top:0.15rem;">
                      Cuenta creada: {created_at if created_at else "N/D"}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if "show_edit_profile" not in st.session_state:
        st.session_state["show_edit_profile"] = False

    with header_right:
        st.write("")
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.session_state["resultado_ruta"] = None
            st.rerun()

        if st.button("Editar perfil", use_container_width=True):
            st.session_state["show_edit_profile"] = not st.session_state["show_edit_profile"]

    st.write("---")

    if st.session_state.get("show_edit_profile"):
        st.markdown(
            """
            <div style="
                background: rgba(2,22,60,0.95);
                border: 1px solid rgba(0,212,255,0.25);
                border-radius: 14px;
                padding: 1rem 1.5rem;
                box-shadow: 0 10px 28px rgba(0,0,0,0.45);
                margin-bottom: 1.2rem;
            ">
            <div style="font-weight:700; color:#00d4ff; margin-bottom:0.5rem;">
                Editar perfil
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c_left, c_center, c_right = st.columns([0.1, 0.8, 0.1])
        with c_center:
            with st.form("edit_profile_form"):
                new_full_name = st.text_input("Nombre completo", value=full_name or "")
                new_avatar_url = st.text_input(
                    "URL de tu foto de perfil (puede ser .jpg, .png, etc)",
                    value=avatar_url or "",
                    placeholder="https://.../mi-foto.jpg",
                )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("Guardar cambios")
                with col_btn2:
                    cancelar = st.form_submit_button("Cancelar")

                if submitted:
                    ok = update_user_profile(
                        username,
                        new_full_name.strip(),
                        new_avatar_url.strip(),
                    )
                    if ok:
                        st.success("Perfil actualizado ✅")
                        if profile is not None:
                            profile["full_name"] = new_full_name
                            profile["avatar_url"] = new_avatar_url
                        st.session_state["show_edit_profile"] = False
                        st.rerun()
                    else:
                        st.error("No se pudo actualizar el perfil.")

                if cancelar:
                    st.session_state["show_edit_profile"] = False
                    st.rerun()

    st.write("---")

    st.subheader("Resumen de mis rutas")

    if not rutas:
        st.info("Aún no has guardado ninguna ruta. Ve a **Búsqueda de rutas** y guarda tu primera ✈️")
        return

    total_rutas = len(rutas)
    total_km = sum(r["distancia_km"] for r in rutas)
    total_costo = sum(r["costo"] for r in rutas)
    total_comb = sum(r["combustible"] for r in rutas)
    max_route = max(rutas, key=lambda r: r["distancia_km"])
    min_route = min(rutas, key=lambda r: r["distancia_km"])

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Rutas guardadas", total_rutas)
    with c2:
        st.metric("Distancia total", f"{total_km:,.0f} km")
    with c3:
        st.metric("Gasto total estimado", f"${total_costo:,.2f} USD")
    with c4:
        st.metric("Combustible total", f"{total_comb:,.2f} gal")

    st.caption(
        f"Ruta más larga: {max_route['origen_name']} → {max_route['destino_name']} "
        f"({max_route['distancia_km']:.0f} km) · "
        f"Ruta más corta: {min_route['origen_name']} → {min_route['destino_name']} "
        f"({min_route['distancia_km']:.0f} km)"
    )

    st.write("---")

    st.subheader("Rutas guardadas")

    for i, r in enumerate(rutas, start=1):
        route_id = r["id"]

        with st.container():
            st.markdown(
                f"### Ruta {i}  &nbsp;&nbsp; "
                f"<span style='font-size:0.9rem;color:#7fd3ff;'>({r['fecha']})</span>",
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns([3, 3, 2])
            with c1:
                st.markdown("**Origen**")
                st.markdown(f"{r['origen_name']}  \nID: `{r['origen_id']}`")
            with c2:
                st.markdown("**Destino**")
                st.markdown(f"{r['destino_name']}  \nID: `{r['destino_id']}`")
            with c3:
                st.markdown("**Resumen**")
                st.write(f"Distancia: **{r['distancia_km']:.0f} km**")
                st.write(f"Precio estimado: **${r['costo']:,.2f}**")
                st.write(f"Combustible: **{r['combustible']:.2f} gal**")

            st.code(r["path_text"], language="text")

            col_del, _ = st.columns([1, 5])
            with col_del:
                if st.button(
                    "🗑 Eliminar ruta",
                    key=f"delete_route_{route_id}",
                    use_container_width=True,
                ):
                    ok = delete_route_for_user(username, route_id)
                    if ok:
                        st.success("Ruta eliminada ✅")
                        load_profile_and_routes.clear()
                        st.rerun()
                    else:
                        st.error("No se pudo eliminar la ruta.")

            st.write("---")

