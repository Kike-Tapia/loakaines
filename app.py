from flask import Flask, render_template, request, jsonify
import mysql.connector
from pusher import Pusher

app = Flask(__name__)

# Configura tu conexión a la base de datos
con = mysql.connector.connect(
    host="localhost",
    user="tu_usuario",
    password="tu_contraseña",
    database="tu_base_de_datos"
)

# Configura Pusher
pusher_client = Pusher(
    app_id='tu_app_id',
    key='ffa9ea426828188c22c1',
    secret='tu_secret',
    cluster='us2',
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

    # Insertar el curso en la base de datos
    sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
    val = (nombre_curso, telefono)
    cursor.execute(sql, val)

    con.commit()

    # Emitir evento de Pusher para notificar sobre el nuevo curso
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
    cursor = con.cursor()
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

    # Actualizar el curso en la base de datos
    sql = "UPDATE tst0_cursos SET Nombre_Curso = %s, Telefono = %s WHERE Id_Curso = %s"
    val = (nombre_curso, telefono, curso_id)
    cursor.execute(sql, val)

    con.commit()

    # Emitir evento de Pusher para notificar sobre el curso modificado
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

    # Eliminar el curso de la base de datos
    sql = "DELETE FROM tst0_cursos WHERE Id_Curso = %s"
    cursor.execute(sql, (id,))
    
    con.commit()

    # Emitir evento de Pusher para notificar sobre el curso eliminado
    pusher_client.trigger("cursos-channel", "curso-eliminado", {"id": id})

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app
