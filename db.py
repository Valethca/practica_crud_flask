import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="academico"
    )

# ==================== CARRERAS ====================

def listar_carreras_paginado(busqueda="", pagina=1, por_pagina=5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        offset = (pagina - 1) * por_pagina
        filtro = f"%{busqueda}%"
        cursor.execute(
            "SELECT COUNT(*) AS total FROM carreras WHERE nombre LIKE %s OR descripcion LIKE %s",
            (filtro, filtro)
        )
        total = cursor.fetchone()['total']

        sql = """
            SELECT c.*, COUNT(e.id) AS total_estudiantes
            FROM carreras c
            LEFT JOIN estudiantes e ON c.id = e.carrera_id
            WHERE c.nombre LIKE %s OR c.descripcion LIKE %s
            GROUP BY c.id
            ORDER BY c.id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql, (filtro, filtro, por_pagina, offset))
        return cursor.fetchall(), total
    finally:
        cursor.close()
        conn.close()

def obtener_todas_carreras():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, nombre FROM carreras ORDER BY nombre ASC")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def obtener_carrera(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM carreras WHERE id = %s", (id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def obtener_estudiantes_por_carrera(carrera_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM estudiantes WHERE carrera_id = %s", (carrera_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def crear_carrera(nombre, descripcion):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO carreras (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def actualizar_carrera(id, nombre, descripcion):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE carreras SET nombre = %s, descripcion = %s WHERE id = %s", (nombre, descripcion, id))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def eliminar_carrera(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM estudiantes WHERE carrera_id = %s", (id,))
        if cursor.fetchone()['total'] > 0:
            return False, "No se puede eliminar la carrera porque tiene estudiantes inscritos."
        cursor.execute("DELETE FROM carreras WHERE id = %s", (id,))
        conn.commit()
        return True, "Carrera eliminada correctamente."
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

# ==================== ESTUDIANTES ====================

def listar_estudiantes_paginado(busqueda="", carrera_id="", pagina=1, por_pagina=5):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        offset = (pagina - 1) * por_pagina
        condiciones = ["(e.apellido LIKE %s OR e.correo LIKE %s OR e.nombre LIKE %s)"]
        filtro = f"%{busqueda}%"
        parametros = [filtro, filtro, filtro]

        if carrera_id:
            condiciones.append("e.carrera_id = %s")
            parametros.append(carrera_id)

        where_sql = " AND ".join(condiciones)

        cursor.execute(f"SELECT COUNT(*) AS total FROM estudiantes e WHERE {where_sql}", tuple(parametros))
        total = cursor.fetchone()['total']

        sql = f"""
            SELECT e.*, c.nombre AS carrera_nombre
            FROM estudiantes e
            INNER JOIN carreras c ON e.carrera_id = c.id
            WHERE {where_sql}
            ORDER BY e.id DESC
            LIMIT %s OFFSET %s
        """
        parametros.extend([por_pagina, offset])
        cursor.execute(sql, tuple(parametros))
        return cursor.fetchall(), total
    finally:
        cursor.close()
        conn.close()

def obtener_estudiante(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM estudiantes WHERE id = %s", (id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def crear_estudiante(nombre, apellido, correo, carrera_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO estudiantes (nombre, apellido, correo, carrera_id) VALUES (%s, %s, %s, %s)",
            (nombre, apellido, correo, carrera_id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def actualizar_estudiante(id, nombre, apellido, correo, carrera_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE estudiantes SET nombre = %s, apellido = %s, correo = %s, carrera_id = %s WHERE id = %s",
            (nombre, apellido, correo, carrera_id, id)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

def eliminar_estudiante(id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM estudiantes WHERE id = %s", (id,))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
