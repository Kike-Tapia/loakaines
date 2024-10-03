from flask import Flask, render_template, request
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

@app.route("/")
def index():
    return render_template("app.html")

@app.route("/alumnos")
def alumnos():
    return render_template("alumnos.html")

@app.route("/alumnos/guardar", methods=["POST"])
def alumnosGuardar():
    matricula = request.form["txtMatriculaFA"]
    nombreapellido = request.form["txtNombreApellidoFA"]
    return f"Matrícula {matricula} Nombre y Apellido {nombreapellido}"

@app.route("/buscar")
def buscar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_cursos ORDER BY Id_Curso DESC")
    registros = cursor.fetchall()

    # Convertir registros a un formato adecuado para JSON
    resultados = []
    for registro in registros:
        resultados.append({
            "Id_Curso": registro[0],
            "Nombre_Curso": registro[1],
            "Telefono": registro[2]
        })

    con.close()

    return {"cursos": resultados}  # Retornar como JSON

@app.route("/registrar", methods=["POST"])
def registrar():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()

    # Obtener datos de la solicitud
    nombre_curso = request.form["nombre_curso"]
    telefono = request.form["telefono"]

    sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
    val = (nombre_curso, telefono)
    cursor.execute(sql, val)

    con.commit()
    con.close()

    # Configurar Pusher
    pusher_client = pusher.Pusher(
        app_id="1714541",
        key="cda1cc599395d699a2af",
        secret="9e9c00fc36600060d9e2",
        cluster="us2",
        ssl=True
    )

    # Enviar notificación de nuevo registro
    pusher_client.trigger("canalRegistrosCursos", "registroCurso", {
        "Nombre_Curso": nombre_curso,
        "Telefono": telefono
    })

    return {"status": "success", "Nombre_Curso": nombre_curso, "Telefono": telefono}

if __name__ == "__main__":
    app.run(debug=True)

