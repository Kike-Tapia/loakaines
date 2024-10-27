from flask import Flask, render_template, request, jsonify
import mysql.connector
import pusher
import time

app = Flask(__name__)

# Configuración de Pusher
pusher_client = pusher.Pusher(
    app_id="1714541",
    key="2df86616075904231311",
    secret="2f91d936fd43d8e85a1a",
    cluster="us2",
    ssl=True
)

# Configuración de conexión a la base de datos con un tiempo de espera personalizado
def get_db_connection(retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        try:
            con = mysql.connector.connect(
                host="185.232.14.52",
                database="u760464709_tst_sep",
                user="u760464709_tst_sep_usr",
                password="dJ0CIAFF=",
                connection_timeout=10  # Tiempo de espera de 10 segundos
            )
            if con.is_connected():
                return con
        except mysql.connector.Error as err:
            attempt += 1
            time.sleep(delay)  # Espera antes de intentar de nuevo
    return None

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

# Ruta para guardar un nuevo curso
@app.route("/cursos/guardar", methods=["POST"])
def cursos_guardar():
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    con = get_db_connection()
    if not con:
        return jsonify({"status": "error", "message": "Error en la conexión a la base de datos"}), 500

    try:
        cursor = con.cursor()
        sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
        val = (nombre_curso, telefono)
        cursor.execute(sql, val)
        con.commit()
        
        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "nuevo-curso", {
            "nombre_curso": nombre_curso,
            "telefono": telefono
        })

        return jsonify({"status": "success", "nombre_curso": nombre_curso})

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        con.close()

# Ruta para buscar cursos
@app.route("/cursos/buscar")
def buscar_cursos():
    con = get_db_connection()
    if not con:
        return jsonify({"status": "error", "message": "Error en la conexión a la base de datos"}), 500

    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tst0_cursos ORDER BY Id_Curso DESC")
        registros = cursor.fetchall()
        return jsonify(registros)

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        con.close()

# Ruta para modificar un curso
@app.route("/cursos/modificar", methods=["POST"])
def cursos_modificar():
    curso_id = request.form["id"]
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    con = get_db_connection()
    if not con:
        return jsonify({"status": "error", "message": "Error en la conexión a la base de datos"}), 500

    try:
        cursor = con.cursor()
        sql = "UPDATE tst0_cursos SET Nombre_Curso = %s, Telefono = %s WHERE Id_Curso = %s"
        val = (nombre_curso, telefono, curso_id)
        cursor.execute(sql, val)
        con.commit()
        
        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "curso-modificado", {
            "id": curso_id,
            "nombre_curso": nombre_curso,
            "telefono": telefono
        })

        return jsonify({"status": "success", "nombre_curso": nombre_curso})

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        con.close()

# Ruta para eliminar un curso
@app.route("/cursos/eliminar/<int:id>", methods=["DELETE"])
def cursos_eliminar(id):
    con = get_db_connection()
    if not con:
        return jsonify({"status": "error", "message": "Error en la conexión a la base de datos"}), 500

    try:
        cursor = con.cursor()
        sql = "DELETE FROM tst0_cursos WHERE Id_Curso = %s"
        cursor.execute(sql, (id,))
        con.commit()
        
        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "curso-eliminado", {"id": id})

        return jsonify({"status": "success"})

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        con.close()

if __name__ == "__main__":
    app.run(debug=True)
