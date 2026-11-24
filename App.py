import math
import re
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import db

app = Flask(__name__)
app.secret_key = "clave_secreta_practica_flask"

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.route("/")
def index():
    return redirect(url_for("listar_carreras"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ==================== CARRERAS ====================

@app.route("/carreras", methods=["GET"])
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
def crear_carrera():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        datos_form = {"nombre": nombre, "descripcion": descripcion}

        if not nombre or len(nombre) > 100 or len(descripcion) > 255:
            flash("Error: El nombre es obligatorio (máx. 100 caracteres) y la descripción máx. 255.", "danger")
            return render_template("carreras/form.html", carrera=datos_form)

        try:
            db.crear_carrera(nombre, descripcion)
            flash("Carrera creada con éxito.", "success")
            return redirect(url_for("listar_carreras"))
        except mysql.connector.IntegrityError:
            flash("Error: Ya existe una carrera con ese nombre.", "danger")
            return render_template("carreras/form.html", carrera=datos_form)
        except Exception as e:
            flash(f"Error al crear carrera: {e}", "danger")
            return render_template("carreras/form.html", carrera=datos_form)

    return render_template("carreras/form.html", carrera=None)

@app.route("/carreras/<int:id>/editar", methods=["GET", "POST"])
def editar_carrera(id):
    carrera = db.obtener_carrera(id)
    if not carrera:
        return render_template("404.html"), 404

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        datos_form = {"id": id, "nombre": nombre, "descripcion": descripcion}

        if not nombre or len(nombre) > 100 or len(descripcion) > 255:
            flash("Error: El nombre es obligatorio (máx. 100 caracteres) y la descripción máx. 255.", "danger")
            return render_template("carreras/form.html", carrera=datos_form)

        try:
            db.actualizar_carrera(id, nombre, descripcion)
            flash("Carrera actualizada con éxito.", "success")
            return redirect(url_for("listar_carreras"))
        except mysql.connector.IntegrityError:
            flash("Error: Ya existe otra carrera con ese nombre.", "danger")
            return render_template("carreras/form.html", carrera=datos_form)
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
            return render_template("carreras/form.html", carrera=datos_form)

    return render_template("carreras/form.html", carrera=carrera)

@app.route("/carreras/<int:id>", methods=["GET"])
def detalle_carrera(id):
    carrera = db.obtener_carrera(id)
    if not carrera:
        return render_template("404.html"), 404
    estudiantes = db.obtener_estudiantes_por_carrera(id)
    return render_template("carreras/detalle.html", carrera=carrera, estudiantes=estudiantes)

@app.route("/carreras/<int:id>/eliminar", methods=["POST"])
def eliminar_carrera(id):
    carrera = db.obtener_carrera(id)
    if not carrera:
        return render_template("404.html"), 404
    exito, mensaje = db.eliminar_carrera(id)
    flash(mensaje, "success" if exito else "warning")
    return redirect(url_for("listar_carreras"))

# ==================== ESTUDIANTES ====================

@app.route("/estudiantes", methods=["GET"])
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
def crear_estudiante():
    carreras = db.obtener_todas_carreras()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        correo = request.form.get("correo", "").strip()
        carrera_id = request.form.get("carrera_id", "").strip()
        datos_form = {
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "carrera_id": int(carrera_id) if carrera_id.isdigit() else ""
        }

        if not nombre or len(nombre) > 80 or not apellido or len(apellido) > 80:
            flash("Error: Nombre y apellido son obligatorios (máx. 80 caracteres).", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

        if not correo or len(correo) > 120 or not EMAIL_REGEX.match(correo):
            flash("Error: Ingrese un correo electrónico válido (máx. 120 caracteres).", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

        if not carrera_id.isdigit() or not db.obtener_carrera(int(carrera_id)):
            flash("Error: La carrera seleccionada no es válida.", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

        try:
            db.crear_estudiante(nombre, apellido, correo, int(carrera_id))
            flash("Estudiante registrado con éxito.", "success")
            return redirect(url_for("listar_estudiantes"))
        except mysql.connector.IntegrityError:
            flash("Error: El correo electrónico ya está registrado.", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)
        except Exception as e:
            flash(f"Error al registrar estudiante: {e}", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

    return render_template("estudiantes/form.html", estudiante=None, carreras=carreras)

@app.route("/estudiantes/<int:id>/editar", methods=["GET", "POST"])
def editar_estudiante(id):
    estudiante = db.obtener_estudiante(id)
    if not estudiante:
        return render_template("404.html"), 404
    carreras = db.obtener_todas_carreras()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        correo = request.form.get("correo", "").strip()
        carrera_id = request.form.get("carrera_id", "").strip()
        datos_form = {
            "id": id,
            "nombre": nombre,
            "apellido": apellido,
            "correo": correo,
            "carrera_id": int(carrera_id) if carrera_id.isdigit() else ""
        }

        if not nombre or len(nombre) > 80 or not apellido or len(apellido) > 80:
            flash("Error: Nombre y apellido son obligatorios (máx. 80 caracteres).", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

        if not correo or len(correo) > 120 or not EMAIL_REGEX.match(correo):
            flash("Error: Ingrese un correo electrónico válido (máx. 120 caracteres).", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

        if not carrera_id.isdigit() or not db.obtener_carrera(int(carrera_id)):
            flash("Error: La carrera seleccionada no es válida.", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

        try:
            db.actualizar_estudiante(id, nombre, apellido, correo, int(carrera_id))
            flash("Estudiante actualizado con éxito.", "success")
            return redirect(url_for("listar_estudiantes"))
        except mysql.connector.IntegrityError:
            flash("Error: El correo ya pertenece a otro estudiante.", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)
        except Exception as e:
            flash(f"Error al actualizar: {e}", "danger")
            return render_template("estudiantes/form.html", estudiante=datos_form, carreras=carreras)

    return render_template("estudiantes/form.html", estudiante=estudiante, carreras=carreras)

@app.route("/estudiantes/<int:id>/eliminar", methods=["POST"])
def eliminar_estudiante(id):
    estudiante = db.obtener_estudiante(id)
    if not estudiante:
        return render_template("404.html"), 404
    try:
        db.eliminar_estudiante(id)
        flash("Estudiante eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar: {e}", "danger")
    return redirect(url_for("listar_estudiantes"))

if __name__ == "__main__":
    app.run(debug=True)
