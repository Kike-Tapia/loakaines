from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
import datetime
import pytz

# Configuración de la app y de Pusher
app = Flask(__name__)
pusher_client = pusher.Pusher(
    app_id="1714541",
    key="2df86616075904231311",
    secret="2f91d936fd43d8e85a1a",
    cluster="us2",
    ssl=True
)

# Función de conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
    )

@app.route("/")
def index():
    return render_template("cursos.html")

@app.route("/cursos/buscar")
def buscar_cursos():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos")
    registros = cursor.fetchall()
    cursor.close()
    con.close()
    return make_response(jsonify(registros))

@app.route("/cursos/guardar", methods=["POST"])
def guardar_curso():
    con = get_db_connection()
    id_curso = request.form.get("id_curso")
    nombre_curso = request.form["nombre_curso"]
    telefono = request.form["telefono"]
    
    cursor = con.cursor()

    # Realizar una operación de actualización o inserción según el valor de id_curso
    if id_curso:
        sql = "UPDATE tst0_cursos SET Nombre_Curso = %s, Telefono = %s WHERE Id_Curso = %s"
        val = (nombre_curso, telefono, id_curso)
    else:
        sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
        val = (nombre_curso, telefono)
    
    cursor.execute(sql, val)
    con.commit()
    cursor.close()
    con.close()

    notificar_actualizacion_cursos()
    return make_response(jsonify({"status": "success"}))

@app.route("/cursos/eliminar", methods=["POST"])
def eliminar_curso():
    con = get_db_connection()
    id_curso = request.form["id_curso"]
    cursor = con.cursor()
    cursor.execute("DELETE FROM tst0_cursos WHERE Id_Curso = %s", (id_curso,))
    con.commit()
    cursor.close()
    con.close()

    notificar_actualizacion_cursos()
    return make_response(jsonify({"status": "success"}))

def notificar_actualizacion_cursos():
    try:
        # Llamada al método trigger de Pusher
        pusher_client.trigger('canalCursos', 'cursoActualizado', {})
    except Exception as e:
        print(f"Error al notificar actualización de curso: {e}")
