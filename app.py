from flask import Flask, render_template, request, jsonify, make_response
import mysql.connector
import datetime
import pytz

def cursosBuscar():
    # Conexión a la base de datos
    con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
    )

    # if not con.is_connected():
        # con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos")
    cursos = cursor.fetchall()
    con.close()

    return make_response(jsonify(cursos))

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

@app.route("/cursos/guardar", methods=["POST"])
def cursos_guardar():
    # if not con.is_connected():
        # con.reconnect()

    id_curso = request.form.get("id_curso")
    nombre_curso = request.form["nombre_curso"]
    telefono = request.form["telefono"]

    cursor = con.cursor()

    if id_curso:  # Si existe un ID, actualizamos
        sql = """
        UPDATE tst0_cursos SET
        Nombre_Curso = %s,
        Telefono = %s
        WHERE Id_Curso = %s
        """
        val = (nombre_curso, telefono, id_curso)
    else:  # Si no existe, insertamos un nuevo curso
        sql = """
        INSERT INTO tst0_cursos (Nombre_Curso, Telefono)
        VALUES (%s, %s)
        """
        val = (nombre_curso, telefono)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    return make_response(jsonify({"success": True}))

@app.route("/cursos/buscar", methods=["GET"])
def cursos_buscar():
    return make_response(jsonify(cursosBuscar()))

@app.route("/cursos/editar", methods=["GET"])
def cursos_editar():
    if not con.is_connected():
        con.reconnect()

    id_curso = request.args["id_curso"]

    cursor = con.cursor(dictionary=True)
    sql = "SELECT Id_Curso, Nombre_Curso, Telefono FROM tst0_cursos WHERE Id_Curso = %s"
    cursor.execute(sql, (id_curso,))
    curso = cursor.fetchone()
    con.close()

    return make_response(jsonify(curso))

@app.route("/cursos/eliminar", methods=["POST"])
def cursos_eliminar():
    if not con.is_connected():
        con.reconnect()

    id_curso = request.form["id_curso"]

    cursor = con.cursor()
    sql = "DELETE FROM tst0_cursos WHERE Id_Curso = %s"
    cursor.execute(sql, (id_curso,))
    con.commit()
    con.close()

    return make_response(jsonify({"success": True}))

if __name__ == "__main__":
    app.run(debug=True)
