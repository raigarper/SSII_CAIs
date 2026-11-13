# CAI 3 — Fase 4: Verificación (antes / después)

Security Team 2 (ST-2). Se repiten exactamente los ataques de la Fase 1
contra `SourceCode_hardened/` (puertos 8000/8001, misma arquitectura).

## Resultado por vulnerabilidad

| ID | Ataque | Antes (SourceCode) | Después (SourceCode_hardened) | Evidencia |
|----|--------|---------------------|--------------------------------|-----------|
| RT-01 | Forjar JWT con la clave de firma | ✅ Conseguido (clave HS256 pública) | ❌ Rechazado (`401 invalid_token`); la clave privada RSA nunca sale del servidor | `01_jwks_publica.json`, `02_ataque_jwt_forjado_rechazado.json` |
| RT-02 | Robar el secreto TOTP sin login | ✅ Conseguido (sin credenciales) | ❌ Requiere la contraseña real; sin ella no se ve ni QR ni secreto | `03a/03b/03c_setup_mfa_*.html` |
| RT-03 | Interceptar el `code` y canjearlo sin PKCE | ✅ Conseguido (sin `code_challenge`) | ❌ El cliente ahora exige PKCE+S256 y cliente confidencial; un `code` sin su `code_verifier` no es canjeable | `07_pkce_presente.txt` |
| RT-04 | Paciente escribe un historial médico | ✅ Conseguido (`HTTP 200`) | ❌ Rechazado (`HTTP 403 insufficient_scope`) | `10_rt04_bloqueado_403.jpg` |
| RT-05 | Robar el JWT desde `document.cookie` | ✅ Token visible en JS | ❌ Cookie `HttpOnly`: `document.cookie` no contiene `access_token` | `11_rt05_lectura_ok_cookie_segura.jpg` |
| RT-06 | Enumerar usuarios por el mensaje de error | ✅ Mensajes distintos | ❌ Mensaje único: "Usuario, contraseña o código FreeOTP incorrectos." | `04_mensajes_error_unificados.txt` |
| RT-07 | Reutilizar el mismo código TOTP | ✅ Aceptado dos veces | ❌ El segundo uso es rechazado (`401`) | login 1→302, login 2→401 (ver consola Fase 4) |
| RT-08 | Usar un token tras hacer logout | ✅ Seguía siendo válido | ❌ `/logout` ahora revoca el `jti`; el mismo token da `401` después | `14_ciclo_revocacion_completo.txt`, `15_logout_navegador.jpg` |
| RT-09 | `alg: none` | ❌ Ya fallaba antes (no vulnerable) | ❌ Sigue fallando (sin cambios necesarios) | — |
| Extra | Bloqueo por fuerza bruta (5 intentos) | No existía | ✅ `HTTP 429` al sexto intento | `05_lockout.html` |

## Verificación del uso legítimo (no solo los ataques)

- Login completo de Rocío (usuario + contraseña + TOTP real obtenido legítimamente con su contraseña) → éxito, redirige al Portal con "Portal Médico (rocio)".
- Lectura del historial como Rocío (paciente) → `HTTP 200 OK`.
- Escritura del historial como Rocío → correctamente bloqueada (`403`, ver RT-04). Confirma que los permisos por rol funcionan sin romper el acceso de lectura del paciente.
- Flujo completo de login + token + logout con el Dr. Gasca (script `verificar_revocacion_logout.py`): login, uso del token, revocación, y verificación de que el token ya no sirve. Funciona de principio a fin.

## Incidencia detectada y corregida durante esta misma fase

Al verificar RT-05 en el navegador real, los botones de "Leer Historial",
"Modificar Historial" e "Inspeccionar Cookies" dejaron de responder. Causa:
la nueva cabecera `Content-Security-Policy: default-src 'self'` (una de las
mejoras de la Fase 3) bloqueaba el `<script>` interno y los `onclick` en
línea de `portal.html`. Solución: se movió el JavaScript a un fichero
externo `static/portal.js` (mismo origen, sin "unsafe-inline") y se
sustituyeron los `onclick` por `addEventListener`. Verificado de nuevo tras
el cambio: todos los botones funcionan correctamente y la CSP sigue activa
sin necesitar relajar ninguna regla.

## Conclusión

Las 8 vulnerabilidades demostradas en la Fase 1 (RT-01 a RT-08) quedan
bloqueadas en `SourceCode_hardened/`. El comportamiento legítimo del
sistema (login con 2FA, lectura/escritura según el rol, logout) sigue
funcionando correctamente.
