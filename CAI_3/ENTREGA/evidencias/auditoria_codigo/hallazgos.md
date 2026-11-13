# CAI 3 — Fase 2: Auditoría revisando el código fuente

Security Team 2 (ST-2). Esta tabla confirma, con la línea exacta del código,
cada ataque demostrado en la Fase 1 (caja negra) y añade los fallos que
solo se detectan leyendo el código. Sirve de base para el Blue Team
(Fase 3) y para el informe final.

Clasificación de severidad: **Crítica / Alta / Media / Baja**, según el
impacto sobre confidencialidad, integridad o disponibilidad de historiales
clínicos y credenciales.

## Confirmación de los hallazgos del Red Team (Fase 1)

| ID | Vulnerabilidad | Fichero : línea | Evidencia Fase 1 | Severidad |
|----|-----------------|------------------|-------------------|-----------|
| RT-01 | Endpoint `/.well-known/jwt-key` publica la clave simétrica HS256 que firma los JWT, sin autenticación. Permite forjar tokens para cualquier usuario y scope. | `auth_server.py:195-197` | `07_jwt_key_expuesta.json`, `08_jwt_forjado.txt`, `09_api_con_jwt_forjado.json` | **Crítica** |
| RT-02 | `/setup-mfa` no exige sesión ni login y acepta `?user=` libre; devuelve el secreto TOTP (`db_seed`) de cualquier usuario en texto plano. | `auth_server.py:156-167`, `templates/setup_mfa.html:20` | `01_setup_mfa_rocio.html`, `01_setup_mfa_dr_gasca.html` | **Crítica** |
| RT-03 | PKCE opcional en el servidor (`CodeChallenge(required=False)`) y cliente público (`token_endpoint_auth_method: none`). El `code` viaja en la URL de redirección y, si se intercepta, se puede canjear sin `code_verifier`. | `auth_server.py:52,85,153` · `auth_client.py:25` | `02_login_headers.txt`, `03_ataque_pkce_token.json` | **Alta** |
| RT-04 | `POST /api/historial` solo exige `@require_oauth()` sin especificar scope: cualquier token válido (incluido uno de paciente con `paciente:leer`) puede escribir historiales. | `auth_client.py:112-113` | `04_rocio_get_historial.json`, `05_rocio_post_historial.json` | **Crítica** |
| RT-05 | Cookie `access_token` creada con `httponly=False`: el JWT queda accesible desde `document.cookie`, robable con una línea de JavaScript (XSS). | `auth_client.py:83-88` | `06_cookie_robable_js.jpg` | **Alta** |
| RT-06 | Mensajes de error distintos para "usuario no existe" vs "contraseña incorrecta": permite enumerar cuentas válidas. | `auth_server.py:179-183` | `10_enumeracion_usuarios.txt` | **Media** |
| RT-07 | `totp.verify(..., valid_window=1)` sin registrar los códigos ya consumidos: el mismo código de 6 dígitos se acepta más de una vez dentro de su ventana de validez. | `auth_server.py:185-187` | `11_totp_reutilizable.txt` | **Media** |
| RT-08 | `/logout` solo borra la cookie del navegador; no existe lista de revocación ni introspección, así que un JWT ya emitido sigue siendo válido hasta expirar (hasta 1h) aunque el usuario cierre sesión. | `auth_client.py:91-95` | `12_token_tras_logout.json` | **Alta** |
| RT-09 | *(Prueba negativa — correcto)* Un JWT con `alg: none` y sin firma es rechazado por Authlib/`jose` (`401 invalid_token`). El validador no sufre confusión de algoritmo. | `auth_client.py:44-52` | `13_jwt_alg_none.txt`, `13b_resultado_alg_none.json` | — (sin riesgo) |

## Hallazgos adicionales detectados solo en el código (no visibles en caja negra)

| ID | Vulnerabilidad | Fichero : línea | Impacto | Severidad |
|----|-----------------|------------------|---------|-----------|
| CODE-01 | `app.run(..., debug=True)` en ambos servidores activa el depurador interactivo de Werkzeug. Si una petición provoca una excepción no controlada, se expone una consola capaz de ejecutar código Python arbitrario (protegida solo por un PIN). | `auth_server.py:200`, `auth_client.py:123` | Posible ejecución remota de código | **Crítica** (si se expusiera fuera de localhost) |
| CODE-02 | `os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"` desactiva la exigencia de HTTPS de Authlib en ambos servidores. Necesario en este laboratorio (todo corre en HTTP local), pero debe quedar documentado como configuración exclusiva de desarrollo. | `auth_server.py:2`, `auth_client.py:2` | Transmisión de tokens y credenciales sin cifrar si se usara en red real | **Media** (alcance de laboratorio) |
| CODE-03 | El cliente (`JWTBearerValidator.authenticate_token`) decodifica el JWT sin exigir explícitamente `iss` o `aud` esperados ni restringir la lista de algoritmos aceptados; solo llama a `claims.validate()` genérico. | `auth_client.py:44-52` | Un token emitido para otro cliente/issuer podría aceptarse si cambiara la configuración | **Baja** (mitigado hoy porque la clave es única, pero debe reforzarse junto con RT-01) |
| CODE-04 | Los refresh tokens emitidos (`TOKENS`) nunca se purgan ni revocan (`revoke_old_credential` está vacío) y `INCLUDE_NEW_REFRESH_TOKEN = False` evita la rotación. | `auth_server.py:114-124` | Un refresh token robado una vez es válido indefinidamente | **Media** |
| CODE-05 | Inconsistencia entre el `exp` real del JWT (1h, línea 135) y el campo `expires_in` devuelto en la respuesta de `/oauth/token` (864000 s = 10 días, observado en la evidencia `03_ataque_pkce_token.json`). Es un valor por defecto de Authlib que no se ha sobrescrito para coincidir con el token real. | `auth_server.py:126-137` | Los clientes que confíen en `expires_in` (en vez de decodificar el JWT) gestionarán mal la caducidad | **Baja** |
| CODE-06 | `login.html` precarga usuario y contraseña en claro en botones de "autocompletar" y en los `value` de los campos del formulario. Útil para pruebas del CAI, pero sería una fuga de credenciales si llegara a producción. | `templates/login.html:14-24` | Exposición de contraseñas reales en el HTML servido | **Media** (aceptable solo como entorno de pruebas, debe eliminarse) |
| CODE-07 | `/api/historial` (POST) no implementa ninguna protección CSRF explícita más allá de `SameSite=Lax` en la cookie; al inyectar el bearer automáticamente desde la cookie (`inject_bearer_from_cookie`), una petición cross-site simple (GET) podría aprovecharse en navegadores que no respeten `SameSite` correctamente. | `auth_client.py:97-102` | Falsificación de petición entre sitios sobre una API que modifica datos clínicos | **Baja-Media** |

## Resumen de severidad

- **Críticas:** RT-01, RT-02, RT-04, CODE-01 → 4
- **Altas:** RT-03, RT-05, RT-08 → 3
- **Medias:** RT-06, RT-07, CODE-02, CODE-04, CODE-06 → 5
- **Bajas:** CODE-03, CODE-05, CODE-07 → 3
- **Sin riesgo (verificado):** RT-09 → 1

## Trazabilidad con el enunciado (Apartado a)

- **Escalada de privilegios en la API** → RT-04.
- **Exposición del token en el navegador** → RT-05 (y RT-08, el token sigue vivo tras logout).
- **PKCE durante la redirección** → RT-03: confirmado que **no se usa** `code_challenge`. Riesgo si se intercepta el `code` en `/callback`: un atacante lo canjea directamente en `/oauth/token` y obtiene un `access_token` válido suplantando a la víctima, sin necesitar su contraseña ni su código TOTP (demostrado en `03_ataque_pkce_token.json`).
