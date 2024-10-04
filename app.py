@app.route("/cursos")
def cursos():
    return render_template("cursos.html")

@app.route("/cursos/guardar", methods=["POST"])
def cursos_guardar():
    id_curso = request.form["txtIdCurso"]
    nombre_curso = request.form["txtNombreCurso"]
    telefono = request.form["txtTelefono"]

    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor()

    # Insertar el curso en la base de datos
    sql = "INSERT INTO tst0_cursos (Id_Curso, Nombre_Curso, Telefono) VALUES (%s, %s, %s)"
    val = (id_curso, nombre_curso, telefono)
    cursor.execute(sql, val)

    con.commit()

    # Disparar evento de Pusher (si lo necesitas)
    pusher_client.trigger("registrosCursos", "cursoRegistrado", {
        "id_curso": id_curso,
        "nombre_curso": nombre_curso,
        "telefono": telefono
    })

    return jsonify({"status": "success", "curso": nombre_curso})

@app.route("/cursos/buscar")
def cursos_buscar():
    if not con.is_connected():
        con.reconnect()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM tst0_cursos ORDER BY Id_Curso DESC")
    registros = cursor.fetchall()
    
    return jsonify(registros)
