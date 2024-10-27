from flask import Flask, render_template, request, jsonify
import mysql.connector
import pusher
import datetime
import pytz

app = Flask(__name__)

# Configuración de Pusher
pusher_client = pusher.Pusher(
    app_id="1714541",
    key="2df86616075904231311",
    secret="2f91d936fd43d8e85a1a",
    cluster="us2",
    ssl=True
)

# Función para establecer una conexión a la base de datos
def connect_db():
    return mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF=",
        connection_timeout=10
    )

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

# Ruta para guardar un nuevo curso
@app.route("/cursos/guardar", methods=["POST"])
def cursos_guardar():
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]
    con = None

    try:
        con = connect_db()
        cursor = con.cursor()

        # Inicia una transacción
        con.start_transaction()
        
        # Ejecuta la inserción
        sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
        val = (nombre_curso, telefono)
        cursor.execute(sql, val)
        
        # Confirma la transacción
        con.commit()

        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "nuevo-curso", {
            "nombre_curso": nombre_curso,
            "telefono": telefono
        })

        return jsonify({"status": "success", "nombre_curso": nombre_curso})

    except mysql.connector.Error as err:
        if con:
            con.rollback()  # Revertir en caso de error
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

# Ruta para buscar cursos
@app.route("/cursos/buscar")
def buscar_cursos():
    con = None
    try:
        con = connect_db()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tst0_cursos ORDER BY Id_Curso DESC")
        registros = cursor.fetchall()
        return jsonify(registros)

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

# Ruta para modificar un curso
@app.route("/cursos/modificar", methods=["POST"])
def cursos_modificar():
    curso_id = request.form["id"]
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]
    con = None

    try:
        con = connect_db()
        cursor = con.cursor()

        # Inicia una transacción
        con.start_transaction()
        
        # Ejecuta la actualización
        sql = "UPDATE tst0_cursos SET Nombre_Curso = %s, Telefono = %s WHERE Id_Curso = %s"
        val = (nombre_curso, telefono, curso_id)
        cursor.execute(sql, val)
        
        # Confirma la transacción
        con.commit()

        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "curso-modificado", {
            "id": curso_id,
            "nombre_curso": nombre_curso,
            "telefono": telefono
        })

        return jsonify({"status": "success", "nombre_curso": nombre_curso})

    except mysql.connector.Error as err:
        if con:
            con.rollback()  # Revertir en caso de error
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

# Ruta para eliminar un curso
@app.route("/cursos/eliminar/<int:id>", methods=["DELETE"])
def cursos_eliminar(id):
    con = None
    try:
        con = connect_db()
        cursor = con.cursor()

        # Inicia una transacción
        con.start_transaction()
        
        # Ejecuta la eliminación
        sql = "DELETE FROM tst0_cursos WHERE Id_Curso = %s"
        cursor.execute(sql, (id,))
        
        # Confirma la transacción
        con.commit()

        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "curso-eliminado", {"id": id})

        return jsonify({"status": "success"})

    except mysql.connector.Error as err:
        if con:
            con.rollback()  # Revertir en caso de error
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

if __name__ == "__main__":
    app.run(debug=True)
