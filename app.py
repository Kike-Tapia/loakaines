from flask import Flask, render_template, request, jsonify, make_response
import mysql.connector
import pusher

# Configuración de la conexión a la base de datos
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

@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

# Ruta para guardar un nuevo curso
@app.route("/cursos/guardar", methods=["POST"])
def cursos_guardar():
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    if not con.is_connected():
        con.reconnect()

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

# Ruta para buscar cursos
@app.route("/cursos/buscar")
def buscar_cursos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tst0_cursos ORDER BY Id_Curso DESC")
    registros = cursor.fetchall()

    return jsonify(registros)

# Ruta para modificar un curso
@app.route("/cursos/modificar", methods=["POST"])
def cursos_modificar():
    curso_id = request.form["id"]
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    if not con.is_connected():
        con.reconnect()

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

# Ruta para eliminar un curso
@app.route("/cursos/eliminar/<int:id>", methods=["DELETE"])
def cursos_eliminar(id):
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    sql = "DELETE FROM tst0_cursos WHERE Id_Curso = %s"
    cursor.execute(sql, (id,))
    con.commit()

    # Notificación a Pusher
    pusher_client.trigger("cursos-channel", "curso-eliminado", {"id": id})

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)
