import math
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import db

app = Flask(__name__)
app.secret_key = "clave_secreta_practica_flask"

@app.route("/")
def index():
    return redirect(url_for("listar_carreras"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ==================== RUTAS CARRERAS ====================

@app.route("/carreras")
def listar_carreras():
    busqueda = request.args.get("q", "").strip()
    pagina = request.args.get("page", 1, type=int)
    por_pagina = 5
    
    carreras, total = db.listar_carreras_paginado(busqueda, pagina, por_pagina)
    total_paginas = math.ceil(total / por_pagina)
    
    return render_template(
        "carreras/lista.html",
        carreras=carreras,
        busqueda=busqueda,
        pagina=pagina,
        total_paginas=total_paginas
    )

@app.route("/carreras/nueva", methods=["GET", "POST"])
def nueva_carrera():
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form["descripcion"].strip()
        try:
            db.crear_carrera(nombre, descripcion)
            flash("Carrera creada con éxito.", "success")
            return redirect(url_for("listar_carreras"))
        except mysql.connector.IntegrityError:
            flash("Error: Ya existe una carrera con ese nombre.", "danger")
        except Exception as e:
            flash(f"Error al crear carrera: {e}", "danger")
            
    return render_template("carreras/form.html", carrera=None)

@app.route("/carreras/editar/<int:id>", methods=["GET", "POST"])
def editar_carrera(id):
    carrera = db.obtener_carrera(id)
    if not carrera:
        return render_template("404.html"), 404
        
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        descripcion = request.form["descripcion"].strip()
        try:
            db.actualizar_carrera(id, nombre, descripcion)
            flash("Carrera actualizada con éxito.", "success")
            return redirect(url_for("listar_carreras"))
        except mysql.connector.IntegrityError:
            flash("Error: Ya existe otra carrera con ese nombre.", "danger")
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
            
    return render_template("carreras/form.html", carrera=carrera)

@app.route("/carreras/detalle/<int:id>")
def detalle_carrera(id):
    carrera = db.obtener_carrera(id)
    if not carrera:
        return render_template("404.html"), 404
    estudiantes = db.obtener_estudiantes_por_carrera(id)
    return render_template("carreras/detalle.html", carrera=carrera, estudiantes=estudiantes)

@app.route("/carreras/eliminar/<int:id>", methods=["POST"])
def eliminar_carrera(id):
    exito, mensaje = db.eliminar_carrera(id)
    flash(mensaje, "success" if exito else "danger")
    return redirect(url_for("listar_carreras"))

# ==================== RUTAS ESTUDIANTES ====================

@app.route("/estudiantes")
def listar_estudiantes():
    busqueda = request.args.get("q", "").strip()
    carrera_id = request.args.get("carrera_id", "").strip()
    pagina = request.args.get("page", 1, type=int)
    por_pagina = 5
    
    estudiantes, total = db.listar_estudiantes_paginado(busqueda, carrera_id, pagina, por_pagina)
    carreras = db.obtener_todas_carreras()
    total_paginas = math.ceil(total / por_pagina)
    
    return render_template(
        "estudiantes/lista.html",
        estudiantes=estudiantes,
        carreras=carreras,
        busqueda=busqueda,
        carrera_id=carrera_id,
        pagina=pagina,
        total_paginas=total_paginas
    )

@app.route("/estudiantes/nuevo", methods=["GET", "POST"])
def nuevo_estudiante():
    carreras = db.obtener_todas_carreras()
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        apellido = request.form["apellido"].strip()
        correo = request.form["correo"].strip()
        carrera_id = request.form["carrera_id"]
        try:
            db.crear_estudiante(nombre, apellido, correo, carrera_id)
            flash("Estudiante registrado con éxito.", "success")
            return redirect(url_for("listar_estudiantes"))
        except mysql.connector.IntegrityError:
            flash("Error: El correo electrónico ya está registrado.", "danger")
        except Exception as e:
            flash(f"Error al registrar estudiante: {e}", "danger")
            
    return render_template("estudiantes/form.html", estudiante=None, carreras=carreras)

@app.route("/estudiantes/editar/<int:id>", methods=["GET", "POST"])
def editar_estudiante(id):
    estudiante = db.obtener_estudiante(id)
    if not estudiante:
        return render_template("404.html"), 404
    carreras = db.obtener_todas_carreras()
    
    if request.method == "POST":
        nombre = request.form["nombre"].strip()
        apellido = request.form["apellido"].strip()
        correo = request.form["correo"].strip()
        carrera_id = request.form["carrera_id"]
        try:
            db.actualizar_estudiante(id, nombre, apellido, correo, carrera_id)
            flash("Estudiante actualizado con éxito.", "success")
            return redirect(url_for("listar_estudiantes"))
        except mysql.connector.IntegrityError:
            flash("Error: El correo ya pertenece a otro estudiante.", "danger")
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
            
    return render_template("estudiantes/form.html", estudiante=estudiante, carreras=carreras)

@app.route("/estudiantes/eliminar/<int:id>", methods=["POST"])
def eliminar_estudiante(id):
    try:
        db.eliminar_estudiante(id)
        flash("Estudiante eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
    return redirect(url_for("listar_estudiantes"))

if __name__ == "__main__":
    app.run(debug=True)
