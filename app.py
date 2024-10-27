from flask import Flask, render_template, request, jsonify
import mysql.connector
import pusher

app = Flask(__name__)

# Configuración de la base de datos
DB_CONFIG = {
    'host': "185.232.14.52",
    'database': "u760464709_tst_sep",
    'user': "u760464709_tst_sep_usr",
    'password': "dJ0CIAFF="
}

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
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/")
def index():
    return render_template("index.html")  # Cambia a tu archivo HTML principal si es necesario

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

@app.route("/cursos/guardar", methods=["POST"])
def cursos_guardar():
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    con = None
    cursor = None

    try:
        con = connect_db()
        cursor = con.cursor()

        # Inserta el nuevo curso
        sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
        cursor.execute(sql, (nombre_curso, telefono))
        con.commit()

        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "nuevo-curso", {
            "nombre_curso": nombre_curso,
            "telefono": telefono
        })

        return jsonify({"status": "success", "nombre_curso": nombre_curso})

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

@app.route("/cursos/buscar", methods=["GET"])
def buscar_cursos():
    con = None
    cursor = None

    try:
        con = connect_db()
        cursor = con.cursor(dictionary=True)

        # Selecciona todos los cursos
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

@app.route("/cursos/modificar", methods=["POST"])
def cursos_modificar():
    curso_id = request.form["id"]
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    con = None
    cursor = None

    try:
        con = connect_db()
        cursor = con.cursor()

        # Actualiza el curso
        sql = "UPDATE tst0_cursos SET Nombre_Curso = %s, Telefono = %s WHERE Id_Curso = %s"
        cursor.execute(sql, (nombre_curso, telefono, curso_id))
        con.commit()

        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "curso-modificado", {
            "id": curso_id,
            "nombre_curso": nombre_curso,
            "telefono": telefono
        })

        return jsonify({"status": "success", "nombre_curso": nombre_curso})

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

@app.route("/cursos/eliminar/<int:id>", methods=["DELETE"])
def cursos_eliminar(id):
    con = None
    cursor = None

    try:
        con = connect_db()
        cursor = con.cursor()

        # Elimina el curso
        sql = "DELETE FROM tst0_cursos WHERE Id_Curso = %s"
        cursor.execute(sql, (id,))
        con.commit()

        # Notificación a Pusher
        pusher_client.trigger("cursos-channel", "curso-eliminado", {"id": id})

        return jsonify({"status": "success"})

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": f"Error en la conexión: {err}"}), 500
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

if __name__ == "__main__":
    app.run(debug=True)
