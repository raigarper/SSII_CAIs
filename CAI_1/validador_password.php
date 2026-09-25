<?php
/**
 * Anexo V: Módulo de Validación y Registro de Usuarios (validador_password.php).
 * Implementa control técnico previo según la Política de Seguridad de CAI 1.
 */

/**
 * Valida el cumplimiento estricto de las 4 directivas corporativas:
 * 1. Longitud mínima de 8 caracteres.
 * 2. Al menos una letra mayúscula y al menos una letra minúscula.
 * 3. Al menos un dígito numérico (0-9).
 * 4. Al menos un símbolo del repertorio permitido por la entidad.
 *
 * @param string $password
 * @return bool True si cumple la totalidad de las reglas, False en caso contrario.
 */
function validatePasswordPolicy($password) {
    // Regla 1: Longitud mínima de 8 caracteres
    if (strlen($password) < 8) {
        return false;
    }

    // Regla 2a: Presencia simultánea de mayúsculas y minúsculas
    if (!preg_match('/[A-Z]/', $password) || !preg_match('/[a-z]/', $password)) {
        return false;
    }

    // Regla 2b: Al menos un dígito numérico
    if (!preg_match('/[0-9]/', $password)) {
        return false;
    }

    // Regla 2c: Al menos un símbolo permitido (!@#$%&*^() -={}[]\:;<>?,./)
    // Se incluye el espacio si está presente en la directiva
    if (!preg_match('/[!@#$%&*^()\-={}[\]\\\\:;<>?,.\/ ]/', $password)) {
        return false;
    }

    return true;
}

/**
 * Registra un usuario aplicando validación previa, salting individual y SHA-256.
 *
 * @param string $username
 * @param string $password
 * @return int 0: Éxito, 1: Violación de política, 2: Error de base de datos.
 */
function addNewUser($username, $password) {
    global $connection;

    // 1. Barrera técnica previa: Rechaza contraseñas no conformes
    if (!validatePasswordPolicy($password)) {
        return 1; // Código de error: Incumplimiento de la política
    }

    // 2. Saneamiento básico contra inyecciones SQL (según material de clase)
    $username = str_replace("'", "''", $username);

    // 3. Mitigación criptográfica recomendada: Generación de Salt aleatorio y SHA-256
    // En lugar de SHA-1 sin salt, usamos SHA-256 concatenando la sal criptográfica
    $salt = bin2hex(random_bytes(8)); // Genera 16 caracteres hexadecimales (seguro)
    $password_hash = hash('sha256', $password . $salt);

    // Inserción en la tabla de control de acceso (incluyendo columna salt)
    $q = "INSERT INTO " . TBL_USERS . " (username, password, salt) VALUES ('$username', '$password_hash', '$salt')";
    $result = mysql_query($q, $connection);

    if ($result) {
        return 0; // Inserción completada correctamente
    } else {
        return 2; // Error de ejecución en el motor SQL
    }
}
?>