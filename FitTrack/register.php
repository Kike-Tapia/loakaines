<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = htmlspecialchars($_POST['name']);
    $email = filter_var($_POST['email'], FILTER_SANITIZE_EMAIL);
    $password = password_hash($_POST['password'], PASSWORD_BCRYPT);

    // Simula guardar los datos en una base de datos.
    echo "Usuario registrado: $name con correo $email.";
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registro - FitTrack</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h2>Crear Cuenta</h2>
    <form method="POST">
        <label for="name">Nombre</label>
        <input type="text" id="name" name="name" required>
        <label for="email">Correo Electrónico</label>
        <input type="email" id="email" name="email" required>
        <label for="password">Contraseña</label>
        <input type="password" id="password" name="password" required>
        <button type="submit">Registrarse</button>
    </form>
</body>
</html>
