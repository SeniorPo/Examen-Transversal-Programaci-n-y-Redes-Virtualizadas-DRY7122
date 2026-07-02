#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ítem 3 - Sitio web con gestión de usuarios y contraseñas en hash (SQLite)
--------------------------------------------------------------------------
- Importa librerías para gestión de claves (hash) y base de datos SQL.
- Crea un sitio web con Flask que corre en el puerto 5800.
- Almacena usuarios y contraseñas (hasheadas) en una base de datos SQLite
  (usuarios.db), visible con DB Browser for SQLite.
- Permite validar usuarios mediante un comando de terminal (CLI) además
  del formulario web de login.

Uso:
    python3 sitio_login_examen.py iniciar-db      -> crea la BD y los usuarios
    python3 sitio_login_examen.py validar "Mario Aravena" "hola.123"
                                                    -> valida por consola
    python3 sitio_login_examen.py servidor        -> levanta el sitio web
                                                       en http://localhost:5800
"""

import sys
import sqlite3

# --- Gestión de claves (hash) ----------------------------------------------
from werkzeug.security import generate_password_hash, check_password_hash

# --- Sitio web ---------------------------------------------------------------
from flask import Flask, request, render_template_string

# --- Configuración general ---------------------------------------------------
NOMBRE_BD = "usuarios.db"
PUERTO = 5800

# Integrantes del examen y su contraseña (elegida): "hola.123"
INTEGRANTES = [
    ("Mario Aravena", "hola.123"),
    ("Fabian Gajardo", "hola.123"),
]

app = Flask(__name__)


# ---------------------------------------------------------------------------
# BASE DE DATOS SQL: creación de tabla y carga de usuarios con hash
# ---------------------------------------------------------------------------

def obtener_conexion():
    conexion = sqlite3.connect(NOMBRE_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def iniciar_db():
    """Crea la tabla 'usuarios' y guarda a los integrantes con su
    contraseña convertida a hash (nunca en texto plano)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)

    for nombre, password in INTEGRANTES:
        hash_password = generate_password_hash(password)
        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, password_hash) VALUES (?, ?)",
                (nombre, hash_password)
            )
            print(f"Usuario creado: {nombre}  |  hash: {hash_password}")
        except sqlite3.IntegrityError:
            print(f"El usuario '{nombre}' ya existe en la base de datos, se omite.")

    conexion.commit()
    conexion.close()
    print(f"\nBase de datos '{NOMBRE_BD}' lista. Ábrela con DB Browser for SQLite "
          f"para ver la tabla 'usuarios' con los nombres y los hash de contraseña.")


def validar_usuario(nombre: str, password: str) -> bool:
    """Busca al usuario en la BD y compara el hash de la contraseña ingresada
    con el hash almacenado."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT password_hash FROM usuarios WHERE nombre = ?", (nombre,))
    fila = cursor.fetchone()
    conexion.close()

    if fila is None:
        return False
    return check_password_hash(fila["password_hash"], password)


# ---------------------------------------------------------------------------
# SITIO WEB (Flask) - puerto 5800
# ---------------------------------------------------------------------------

PLANTILLA_INICIO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Examen - Login Seguro</title>
    <style>
        body { font-family: Arial, sans-serif; background:#f4f4f9; display:flex;
               justify-content:center; align-items:center; height:100vh; margin:0; }
        .caja { background:white; padding:2rem 3rem; border-radius:10px;
                box-shadow:0 4px 10px rgba(0,0,0,0.15); text-align:center; }
        input { display:block; width:100%; margin:.5rem 0; padding:.5rem; box-sizing:border-box; }
        button { padding:.6rem 1.2rem; background:#2c3e50; color:white; border:none;
                 border-radius:5px; cursor:pointer; }
        .mensaje { margin-top:1rem; font-weight:bold; }
        .ok { color: green; }
        .error { color: crimson; }
    </style>
</head>
<body>
    <div class="caja">
        <h2>Ingreso al Sitio - Examen</h2>
        <form method="POST" action="/login">
            <input type="text" name="nombre" placeholder="Nombre de usuario" required>
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Ingresar</button>
        </form>
        {% if mensaje %}
            <p class="mensaje {{ 'ok' if exito else 'error' }}">{{ mensaje }}</p>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def inicio():
    return render_template_string(PLANTILLA_INICIO, mensaje=None, exito=False)


@app.route("/login", methods=["POST"])
def login():
    nombre = request.form.get("nombre", "").strip()
    password = request.form.get("password", "")

    if validar_usuario(nombre, password):
        mensaje = f"✔ Bienvenido/a, {nombre}. Autenticación exitosa."
        exito = True
    else:
        mensaje = "✘ Usuario o contraseña incorrectos."
        exito = False

    return render_template_string(PLANTILLA_INICIO, mensaje=mensaje, exito=exito)


# ---------------------------------------------------------------------------
# COMANDO DE TERMINAL PARA VALIDAR USUARIOS (sin pasar por el navegador)
# ---------------------------------------------------------------------------

def mostrar_ayuda():
    print(__doc__)


def main():
    if len(sys.argv) < 2:
        mostrar_ayuda()
        return

    comando = sys.argv[1]

    if comando == "iniciar-db":
        iniciar_db()

    elif comando == "validar":
        if len(sys.argv) != 4:
            print('Uso correcto: python3 sitio_login_examen.py validar "Nombre Apellido" "contraseña"')
            return
        nombre, password = sys.argv[2], sys.argv[3]
        if validar_usuario(nombre, password):
            print(f"✔ VALIDADO: el usuario '{nombre}' y la contraseña son correctos.")
        else:
            print(f"✘ RECHAZADO: usuario o contraseña incorrectos para '{nombre}'.")

    elif comando == "servidor":
        print(f"Iniciando sitio web en http://localhost:{PUERTO}  (Ctrl+C para detener)")
        app.run(host="0.0.0.0", port=PUERTO, debug=True)

    else:
        mostrar_ayuda()


if __name__ == "__main__":
    main()