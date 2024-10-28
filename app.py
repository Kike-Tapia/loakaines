from flask import Flask, render_template, request, jsonify
import pusher
import mysql.connector
import datetime
import pytz

app = Flask(__name__)

# Configuración de la base de datos
con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

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

@app.route("/cursos/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos ORDER BY Id_Curso DESC")
    registros = cursor.fetchall()
    cursor.close()

    return jsonify(registros)

@app.route("/cursos/guardar", methods=["POST"])
def guardar():
    if not con.is_connected():
        con.reconnect()

    id_curso = request.form.get("id_curso")
    nombre_curso = request.form.get("nombre_curso")
    telefono = request.form.get("telefono")
    cursor = con.cursor()

    if id_curso:  # Si existe id, actualiza el curso
        cursor.execute("""
            UPDATE tst0_cursos SET Nombre_Curso=%s, Telefono=%s WHERE Id_Curso=%s
        """, (nombre_curso, telefono, id_curso))
    else:  # Si no, inserta un nuevo curso
        cursor.execute("""
            INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)
        """, (nombre_curso, telefono))

    con.commit()
    cursor.close()

    # Notifica a través de Pusher
    pusher_client.trigger('canalCursos', 'cursoActualizado', {})

    return jsonify({"status": "success"})

@app.route("/cursos/editar")
def editar():
    id_curso = request.args.get("id_curso")
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos WHERE Id_Curso = %s", (id_curso,))
    curso = cursor.fetchone()
    cursor.close()

    return jsonify(curso)

@app.route("/cursos/eliminar", methods=["POST"])
def eliminar():
    id_curso = request.form.get("id_curso")
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("DELETE FROM tst0_cursos WHERE Id_Curso = %s", (id_curso,))
    con.commit()
    cursor.close()

    # Notifica a través de Pusher
    pusher_client.trigger('canalCursos', 'cursoActualizado', {})

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
