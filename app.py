from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
PROYECTOS_DIR = BASE_DIR / "proyectos"
PROYECTOS_DIR.mkdir(exist_ok=True)

def cargar_proyectos():
    proyectos = {}
    for f in PROYECTOS_DIR.glob("*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            proyectos[data["proyecto"]] = data
    return proyectos


@app.route("/")
def index():
    return render_template("index.html", title="Inicio")


@app.route("/existentes")
def existentes():
    proyectos = cargar_proyectos()
    proyecto_sel = request.args.get("proyecto")
    numero_parte_sel = request.args.get("numero_parte")
    return render_template(
        "existentes.html",
        proyectos=proyectos,
        proyecto_sel=proyecto_sel,
        numero_parte_sel=numero_parte_sel,
        title="Proyectos Existentes"
    )


@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        proyecto = request.form["proyecto"].strip()
        numero_parte = request.form["numero_parte"].strip()
        tipo_maquina = request.form["tipo_maquina"].strip()
        herramientas = [h.strip() for h in request.form.getlist("herramientas[]") if h.strip()]

        if not proyecto or not numero_parte or not tipo_maquina:
            return "Faltan datos.", 400

        path = PROYECTOS_DIR / f"{proyecto.replace(' ', '_')}.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"proyecto": proyecto, "tipo_maquina": tipo_maquina, "partes": {}}

        data["partes"][numero_parte] = herramientas

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return redirect(url_for("existentes"))
    return render_template("nuevo.html", title="Nuevo Proyecto")


@app.route("/editar", methods=["GET", "POST"])
def editar():
    proyecto = request.args.get("proyecto")
    numero_parte = request.args.get("numero_parte")
    path = PROYECTOS_DIR / f"{proyecto.replace(' ', '_')}.json"
    if not path.exists():
        return "Proyecto no encontrado", 404

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    tipo_maquina = data.get("tipo_maquina", "")
    herramientas = data["partes"].get(numero_parte, [])

    if request.method == "POST":
        tipo_maquina = request.form.get("tipo_maquina", "").strip()
        nuevas_herramientas = [h.strip() for h in request.form.get("herramientas", "").split(",") if h.strip()]
        data["tipo_maquina"] = tipo_maquina
        data["partes"][numero_parte] = nuevas_herramientas

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return redirect(url_for("existentes", proyecto=proyecto))

    return render_template(
        "editar.html",
        proyecto=proyecto,
        numero_parte=numero_parte,
        tipo_maquina=tipo_maquina,
        herramientas=herramientas,
        title="Editar Proyecto"
    )


@app.route("/eliminar")
def eliminar():
    proyecto = request.args.get("proyecto")
    numero_parte = request.args.get("numero_parte")
    path = PROYECTOS_DIR / f"{proyecto.replace(' ', '_')}.json"

    if not path.exists():
        return "Proyecto no encontrado", 404

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if numero_parte in data["partes"]:
        del data["partes"][numero_parte]

    if not data["partes"]:
        path.unlink()
    else:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return redirect(url_for("existentes"))


# 🔹 ESTA ES LA PARTE IMPORTANTE 🔹
# Escucha en todas las IPs locales (para acceder desde otro dispositivo en la misma red)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
