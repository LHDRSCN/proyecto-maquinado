from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)

# 🔹 Ruta de red donde se guardará la base de datos
DB_PATH = Path(r"\\synserver_scn\DATASCNProject\BkpBDS_SQL\Proyectos\proyectos.db")

# ---------------------------------------------------------------------
# 📦 FUNCIONES DE BASE DE DATOS
# ---------------------------------------------------------------------

def crear_tablas():
    """Crea las tablas si no existen."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE,
                tipo_maquina TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS partes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proyecto_id INTEGER,
                numero_parte TEXT,
                FOREIGN KEY(proyecto_id) REFERENCES proyectos(id)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS herramientas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parte_id INTEGER,
                nombre TEXT,
                FOREIGN KEY(parte_id) REFERENCES partes(id)
            )
        """)
        conn.commit()

def obtener_proyectos():
    """Obtiene todos los proyectos."""
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, nombre, tipo_maquina FROM proyectos")
        return c.fetchall()

def obtener_partes(proyecto_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id, numero_parte FROM partes WHERE proyecto_id=?", (proyecto_id,))
        return c.fetchall()

def obtener_herramientas(parte_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT nombre FROM herramientas WHERE parte_id=?", (parte_id,))
        return [h[0] for h in c.fetchall()]

# ---------------------------------------------------------------------
# 🌐 RUTAS FLASK
# ---------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html", title="Inicio")

@app.route("/existentes")
def existentes():
    proyectos = []
    for p in obtener_proyectos():
        partes = obtener_partes(p[0])
        proyectos.append({
            "id": p[0],
            "nombre": p[1],
            "tipo_maquina": p[2],
            "partes": [
                {"id": parte[0], "numero_parte": parte[1], "herramientas": obtener_herramientas(parte[0])}
                for parte in partes
            ]
        })
    return render_template("existentes.html", proyectos=proyectos, title="Proyectos Existentes")

@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        nombre = request.form["proyecto"].strip()
        numero_parte = request.form["numero_parte"].strip()
        tipo_maquina = request.form["tipo_maquina"].strip()
        herramientas = [h.strip() for h in request.form.getlist("herramientas[]") if h.strip()]

        if not nombre or not numero_parte or not tipo_maquina:
            return "Faltan datos.", 400

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO proyectos (nombre, tipo_maquina) VALUES (?, ?)", (nombre, tipo_maquina))
            conn.commit()

            c.execute("SELECT id FROM proyectos WHERE nombre=?", (nombre,))
            proyecto_id = c.fetchone()[0]

            c.execute("INSERT INTO partes (proyecto_id, numero_parte) VALUES (?, ?)", (proyecto_id, numero_parte))
            parte_id = c.lastrowid

            for h in herramientas:
                c.execute("INSERT INTO herramientas (parte_id, nombre) VALUES (?, ?)", (parte_id, h))
            conn.commit()

        return redirect(url_for("existentes"))

    return render_template("nuevo.html", title="Nuevo Proyecto")

@app.route("/editar", methods=["GET", "POST"])
def editar():
    proyecto_id = request.args.get("proyecto_id")
    parte_id = request.args.get("parte_id")

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT nombre, tipo_maquina FROM proyectos WHERE id=?", (proyecto_id,))
        proyecto = c.fetchone()
        c.execute("SELECT numero_parte FROM partes WHERE id=?", (parte_id,))
        parte = c.fetchone()
        herramientas = obtener_herramientas(parte_id)

    if request.method == "POST":
        tipo_maquina = request.form["tipo_maquina"].strip()
        nuevas_herramientas = [h.strip() for h in request.form.get("herramientas", "").split(",") if h.strip()]

        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("UPDATE proyectos SET tipo_maquina=? WHERE id=?", (tipo_maquina, proyecto_id))
            c.execute("DELETE FROM herramientas WHERE parte_id=?", (parte_id,))
            for h in nuevas_herramientas:
                c.execute("INSERT INTO herramientas (parte_id, nombre) VALUES (?, ?)", (parte_id, h))
            conn.commit()

        return redirect(url_for("existentes"))

    return render_template("editar.html",
        proyecto_id=proyecto_id,
        parte_id=parte_id,
        proyecto=proyecto[0],
        tipo_maquina=proyecto[1],
        numero_parte=parte[0],
        herramientas=herramientas,
        title="Editar Proyecto"
    )

@app.route("/eliminar")
def eliminar():
    parte_id = request.args.get("parte_id")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM herramientas WHERE parte_id=?", (parte_id,))
        c.execute("DELETE FROM partes WHERE id=?", (parte_id,))
        conn.commit()
    return redirect(url_for("existentes"))

# ---------------------------------------------------------------------
# 🚀 EJECUCIÓN DEL SERVIDOR
# ---------------------------------------------------------------------
if __name__ == "__main__":
    crear_tablas()
    print(f"📁 Base de datos: {DB_PATH}")
    app.run(host="0.0.0.0", port=5000, debug=True)
