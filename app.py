from flask import Flask, render_template, request
import pusher
import mysql.connector
import datetime
import pytz

con = mysql.connector.connect(
    host="185.232.14.52",
    database="u760464709_tst_sep",
    user="u760464709_tst_sep_usr",
    password="dJ0CIAFF="
)

app = Flask(__name__)

@app.route("/")
def index():
    con.close()
    return render_template("app.html")

# Ruta para ver los cursos
@app.route("/cursos")
def cursos():
    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_cursos ORDER BY Id_Curso DESC")
    registros = cursor.fetchall()

    con.close()

    return render_template("cursos.html", registros=registros)

# Ruta para agregar un nuevo curso
@app.route("/cursos/guardar", methods=["POST"])
def cursosGuardar():
    if not con.is_connected():
        con.reconnect()
    
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    cursor = con.cursor()
    sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
    val = (nombre_curso, telefono)
    cursor.execute(sql, val)

    con.commit()
    con.close()
    
    return f"Curso '{nombre_curso}' guardado con éxito."

# Otras rutas relacionadas con los cursos
@app.route("/registrar_curso", methods=["GET"])
def registrar_curso():
    args = request.args

    if not con.is_connected():
        con.reconnect()

    cursor = con.cursor()

    sql = "INSERT INTO tst0_cursos (Nombre_Curso, Telefono) VALUES (%s, %s)"
    val = (args["nombre_curso"], args["telefono"])
    cursor.execute(sql, val)
    
    con.commit()
    con.close()

    pusher_client = pusher.Pusher(
        app_id="1714541",
        key="cda1cc599395d699a2af",
        secret="9e9c00fc36600060d9e2",
        cluster="us2",
        ssl=True
    )

    pusher_client.trigger("canalRegistrosCursos", "registroCurso", args)

    return args
