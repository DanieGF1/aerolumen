# backend_mysql.py
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),           
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "aerolumen")
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ==============================
# Usuarios
# ==============================
def register_user(email: str, password: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # ¿ya existe?
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "Ese correo ya está registrado."

        # insertar
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, password)
        )
        conn.commit()
        return True, "Usuario registrado correctamente."
    except Error as e:
        print("Error en register_user:", e)
        return False, "Error al registrar usuario en la base de datos."
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def validate_user(email: str, password: str) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        if not row:
            return False
        stored_password = row[0]
        return stored_password == password
    except Error as e:
        print("Error en validate_user:", e)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def get_user_id(email: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )
        row = cursor.fetchone()
        return row[0] if row else None
    except Error as e:
        print("Error en get_user_id:", e)
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

# ==============================
# Rutas guardadas
# ==============================
def save_route_for_user(email: str, route_info: dict) -> bool:
    conn = None
    cursor = None
    try:
        user_id = get_user_id(email)
        if user_id is None:
            return False

        path_list = route_info.get("path", [])
        path_text = " -> ".join(path_list)
        fecha_str = route_info.get("fecha")
        if not fecha_str:
            fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO routes (
                user_id, origen_id, origen_name,
                destino_id, destino_name,
                distancia_km, costo, combustible,
                path_text, fecha
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                route_info["origen_id"],
                route_info["origen_name"],
                route_info["destino_id"],
                route_info["destino_name"],
                route_info["distancia_km"],
                route_info["costo"],
                route_info["combustible"],
                path_text,
                fecha_str
            )
        )
        conn.commit()
        return True
    except Error as e:
        print("Error en save_route_for_user:", e)
        return False
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def get_routes_for_user(email: str):
    conn = None
    cursor = None
    try:
        user_id = get_user_id(email)
        if user_id is None:
            return []

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT
                origen_id, origen_name,
                destino_id, destino_name,
                distancia_km, costo, combustible,
                path_text, fecha
            FROM routes
            WHERE user_id = %s
            ORDER BY fecha DESC
            """,
            (user_id,)
        )
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print("Error en get_routes_for_user:", e)
        return []
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
