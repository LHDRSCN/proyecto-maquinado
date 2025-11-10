from flask import Flask, render_template, url_for

app = Flask(__name__)

# 🏠 Página principal
@app.route('/')
def index():
    return render_template('index.html', title='Inicio')

# 📂 Página de proyectos existentes
@app.route('/existentes')
def existentes():
    return render_template('existentes.html', title='Proyectos Existentes')

# ➕ Página para registrar nuevo proyecto
@app.route('/nuevo')
def nuevo():
    return render_template('nuevo.html', title='Nuevo Proyecto')

# 🚀 Punto de inicio
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
