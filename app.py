from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import json
import uuid
from dotenv import load_dotenv
import os

load_dotenv()
from config import get_redis_connection

app = Flask(__name__)
app.secret_key = "secret_key"  # Cambiar en producción
r = get_redis_connection()

# ------------------------------
# Funciones auxiliares
# ------------------------------
def obtener_libros():
    libros = []
    for clave in r.scan_iter("libro:*"):
        libro = json.loads(r.get(clave))
        libros.append(libro)
    return libros

def obtener_libro(id_libro):
    clave = f"libro:{id_libro}"
    if r.exists(clave):
        return json.loads(r.get(clave))
    return None

# ------------------------------
# Rutas
# ------------------------------
@app.route("/")
def index():
    libros = obtener_libros()
    return render_template("index.html", libros=libros)

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        autor = request.form["autor"].strip()
        genero = request.form["genero"].strip()
        estado = request.form["estado"].strip().capitalize()

        if not titulo or not autor or not genero or estado not in ["Leído", "No leído"]:
            flash("Por favor completa todos los campos correctamente.", "error")
            return redirect(url_for("agregar"))

        id_libro = str(uuid.uuid4())
        clave = f"libro:{id_libro}"

        libro = {
            "id": id_libro,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado
        }

        r.set(clave, json.dumps(libro))
        flash("Libro agregado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("add.html")

@app.route("/editar/<id_libro>", methods=["GET", "POST"])
def editar(id_libro):
    libro = obtener_libro(id_libro)
    if not libro:
        flash("Libro no encontrado.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        nuevo_titulo = request.form["titulo"].strip()
        nuevo_autor = request.form["autor"].strip()
        nuevo_genero = request.form["genero"].strip()
        nuevo_estado = request.form["estado"].strip().capitalize()

        if nuevo_estado not in ["Leído", "No leído"]:
            flash("Estado inválido.", "error")
            return redirect(url_for("editar", id_libro=id_libro))

        libro.update({
            "titulo": nuevo_titulo,
            "autor": nuevo_autor,
            "genero": nuevo_genero,
            "estado": nuevo_estado
        })

        r.set(f"libro:{id_libro}", json.dumps(libro))
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", libro=libro)

@app.route("/eliminar/<id_libro>")
def eliminar(id_libro):
    clave = f"libro:{id_libro}"
    if r.delete(clave):
        flash("Libro eliminado correctamente.", "success")
    else:
        flash("No se encontró el libro especificado.", "error")
    return redirect(url_for("index"))

@app.route("/buscar", methods=["GET", "POST"])
def buscar():
    resultados = []
    if request.method == "POST":
        campo = request.form["campo"]
        termino = request.form["termino"].strip().lower()

        for clave in r.scan_iter("libro:*"):
            libro = json.loads(r.get(clave))
            if termino in libro[campo].lower():
                resultados.append(libro)
        if not resultados:
            flash("No se encontraron resultados.", "info")

    return render_template("search.html", resultados=resultados)

# ------------------------------
# Ejecutar servidor
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
