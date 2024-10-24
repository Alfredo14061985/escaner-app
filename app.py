from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

datos_globales = pd.DataFrame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set-user', methods=['POST'])
def set_user():
    usuario = request.form['usuario']
    flash(f'Usuario {usuario} registrado correctamente.')
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No se encontró el archivo.')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo.')
        return redirect(request.url)
    if file:
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(ruta_archivo)
        global datos_globales
        try:
            datos_globales = pd.read_csv(ruta_archivo)
            flash(f'Archivo {file.filename} cargado correctamente.')
        except Exception as e:
            flash(f'Error al cargar el archivo: {e}')
    return redirect(url_for('index'))

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        contenedor = request.form['contenedor']
        contenido_contenedor = datos_globales[datos_globales['Numero de contenedor'] == contenedor]
        if contenido_contenedor.empty:
            flash(f'No se encontró el contenedor {contenedor}.')
        else:
            return render_template('scan.html', contenedor=contenedor, contenido=contenido_contenedor.to_dict(orient='records'))
    return render_template('scan.html')

@app.route('/scan-article', methods=['POST'])
def scan_article():
    articulo = request.form['articulo']
    cantidad = int(request.form['cantidad'])
    contenedor = request.form['contenedor']
    if contenedor in datos_globales['Numero de contenedor'].values:
        for index, row in datos_globales.iterrows():
            if row['Numero de contenedor'] == contenedor and (row['Articulo'] == articulo or row['Codigo UPC'] == articulo):
                datos_globales.at[index, 'Cant. recibida'] += cantidad
                datos_globales.at[index, 'Diferencia'] = datos_globales.at[index, 'Cant. recibida'] - datos_globales.at[index, 'Cant. manifestada']
                flash(f'Artículo {articulo} escaneado correctamente.')
                break
        else:
            flash(f'Artículo {articulo} no encontrado en el contenedor {contenedor}.')
    else:
        flash(f'Contenedor {contenedor} no encontrado.')
    return redirect(url_for('scan', contenedor=contenedor))

if __name__ == '__main__':
    app.run(debug=True)

