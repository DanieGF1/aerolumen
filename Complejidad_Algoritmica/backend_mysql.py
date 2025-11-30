import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def get_user_profile(email: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT email, full_name, avatar_url, created_at
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        row = cursor.fetchone()
        return row
    except Error as e:
        print("Error en get_user_profile:", e)
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_user_profile(email: str, full_name: str, avatar_url: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET full_name = %s,
                avatar_url = %s
            WHERE email = %s
            """,
            (full_name, avatar_url, email),
        )
        conn.commit()
        return True
    except Error as e:
        print("Error en update_user_profile:", e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def register_user(email: str, password: str):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "Ese correo ya está registrado."
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
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return []

        user_id = row["id"]

        cursor.execute(
            """
            SELECT
                r.id,
                r.origen_id,
                r.origen_name,
                r.destino_id,
                r.destino_name,
                r.distancia_km,
                r.costo,
                r.combustible,
                r.path_text,
                r.fecha
            FROM routes r
            WHERE r.user_id = %s
            ORDER BY r.fecha DESC, r.id DESC
            """,
            (user_id,),
        )
        rows = cursor.fetchall()

        rutas = []
        for r in rows:
            rutas.append(
                {
                    "id": r["id"],
                    "origen_id": r["origen_id"],
                    "origen_name": r["origen_name"],
                    "destino_id": r["destino_id"],
                    "destino_name": r["destino_name"],
                    "distancia_km": float(r["distancia_km"]),
                    "costo": float(r["costo"]),
                    "combustible": float(r["combustible"]),
                    "path_text": r["path_text"],
                    "fecha": r["fecha"].strftime("%Y-%m-%d %H:%M:%S") if r["fecha"] else "",
                }
            )
        return rutas

    except Exception as e:
        print("Error en get_routes_for_user:", e)
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def delete_route_for_user(email: str, route_id: int) -> bool:
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        row = cursor.fetchone()
        if not row:
            return False

        user_id = row[0]

        cursor.execute(
            "DELETE FROM routes WHERE id = %s AND user_id = %s",
            (route_id, user_id),
        )
        conn.commit()

        return cursor.rowcount == 1
    except Exception as e:
        print("Error en delete_route_for_user:", e)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
