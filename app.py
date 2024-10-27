from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
import datetime
import pytz

# Conexión a la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

# Configuración de Pusher
pusher_client = pusher.Pusher(
    app_id="1714541",
    key="2df86616075904231311",
    secret="2f91d936fd43d8e85a1a",
    cluster="us2",
    ssl=True
)

@app.route("/")
def index():
    return render_template("cursos.html")

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

@app.route("/cursos/buscar")
def buscar_cursos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos")
    registros = cursor.fetchall()

    con.close()
    return make_response(jsonify(registros))

@app.route("/cursos/guardar", methods=["POST"])
def guardar_curso():
    if not con.is_connected():
        con.reconnect()

    id_curso = request.form.get("id_curso")
    nombre_curso = request.form["nombre_curso"]
    telefono = request.form["telefono"]
    
    cursor = con.cursor()

    if id_curso:
        sql = """
        UPDATE tst0_cursos SET
        Nombre_Curso = %s,
        Telefono = %s
        WHERE Id_Curso = %s
        """
        val = (nombre_curso, telefono, id_curso)
    else:
        sql = """
        INSERT INTO tst0_cursos (Nombre_Curso, Telefono)
        VALUES (%s, %s)
        """
        val = (nombre_curso, telefono)
    
    cursor.execute(sql, val)
    con.commit()
    con.close()

    notificar_actualizacion_cursos()  # Notifica a los clientes
    return make_response(jsonify({}))

@app.route("/cursos/editar", methods=["GET"])
def editar_curso():
    if not con.is_connected():
        con.reconnect()

    id_curso = request.args.get("id_curso")
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos WHERE Id_Curso = %s", (id_curso,))
    registro = cursor.fetchone()
    con.close()

    return make_response(jsonify(registro))

@app.route("/cursos/eliminar", methods=["POST"])
def eliminar_curso():
    if not con.is_connected():
        con.reconnect()

    id_curso = request.form["id_curso"]
    cursor = con.cursor()
    cursor.execute("DELETE FROM tst0_cursos WHERE Id_Curso = %s", (id_curso,))
    con.commit()
    con.close()

    notificar_actualizacion_cursos()  # Notifica a los clientes
    return make_response(jsonify({}))

def notificar_actualizacion_cursos():
    # Envía una notificación a Pusher
    pusher_client.trigger('canalCursos', 'cursoActualizado', {})

if __name__ == "__main__":
    app.run(debug=True)
