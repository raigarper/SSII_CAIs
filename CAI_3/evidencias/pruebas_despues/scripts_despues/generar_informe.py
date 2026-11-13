# -*- coding: utf-8 -*-
"""
Genera ST-2-CAI3-Parte1.pdf a partir de las evidencias recogidas en las
Fases 1-4 del CAI 3 - Parte 1.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image as RLImage, HRFlowable, ListFlowable, ListItem, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER

BASE = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_3"
OUT = os.path.join(BASE, "ST-2-CAI3-Parte1.pdf")
CODIGO_ENTREGA = "ST-2-CAI3-Parte1"


def _marca_agua_y_pie(canv, doc_):
    # Marca de agua "CONFIDENCIAL" en diagonal, en todas las paginas.
    canv.saveState()
    canv.setFont("Helvetica-Bold", 60)
    canv.setFillColor(colors.Color(0.82, 0.82, 0.82))
    canv.translate(A4[0] / 2, A4[1] / 2)
    canv.rotate(45)
    canv.drawCentredString(0, 0, "CONFIDENCIAL")
    canv.restoreState()

    # Pie de pagina, mismo formato que las entregas anteriores del equipo
    # (la portada, pagina 1, no lleva pie, igual que en ST-2-CAI2B.pdf).
    if canv.getPageNumber() > 1:
        canv.saveState()
        canv.setFont("Helvetica", 8)
        canv.setFillColor(colors.grey)
        pie = f"{CODIGO_ENTREGA} · Informe emitido por SecurTech Advisory para el Hospital · CONFIDENCIAL · Página {canv.getPageNumber()}"
        canv.drawCentredString(A4[0] / 2, 1.1 * cm, pie)
        canv.restoreState()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloPortada", fontSize=20, leading=26, spaceAfter=14, alignment=TA_CENTER, textColor=colors.HexColor("#1b3a5c")))
styles.add(ParagraphStyle(name="SubtituloPortada", fontSize=13, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#334a63")))
styles.add(ParagraphStyle(name="H1", fontSize=15, leading=19, spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#1b3a5c")))
styles.add(ParagraphStyle(name="H2", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=6, textColor=colors.HexColor("#1b3a5c")))
styles.add(ParagraphStyle(name="Cuerpo", fontSize=9.7, leading=13.5))
styles.add(ParagraphStyle(name="Codigo", fontName="Courier", fontSize=8, leading=10.5, backColor=colors.HexColor("#f2f2f2"), borderPadding=6))
styles.add(ParagraphStyle(name="Pie", fontSize=8, textColor=colors.grey))
styles.add(ParagraphStyle(name="Severidad", fontSize=9.5, leading=13, textColor=colors.white, alignment=TA_CENTER))

COLOR_CRIT = colors.HexColor("#b02a2a")
COLOR_ALTA = colors.HexColor("#c87d1f")
COLOR_MEDIA = colors.HexColor("#b8960b")
COLOR_BAJA = colors.HexColor("#4a7a2a")
COLOR_OK = colors.HexColor("#2f6f4e")

story = []


def h1(text):
    story.append(Paragraph(text, styles["H1"]))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#1b3a5c"), spaceAfter=6))


def h2(text):
    story.append(Paragraph(text, styles["H2"]))


def p(text):
    story.append(Paragraph(text, styles["Cuerpo"]))
    story.append(Spacer(1, 4))


def code(text):
    safe = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    story.append(Paragraph(safe.replace("\n", "<br/>"), styles["Codigo"]))
    story.append(Spacer(1, 6))


def img(path, width=13.5 * cm, caption=None):
    full = os.path.join(BASE, path)
    im = RLImage(full)
    ratio = im.imageHeight / im.imageWidth
    im.drawWidth = width
    im.drawHeight = width * ratio
    story.append(im)
    if caption:
        story.append(Paragraph(caption, styles["Pie"]))
    story.append(Spacer(1, 8))


def caja_conclusion(titulo, texto, tipo="info"):
    """Caja de conclusion con borde de color, igual que en entregas anteriores
    del equipo (verde=positivo, rojo=riesgo/critico, azul=informativo)."""
    fondo = {"ok": colors.HexColor("#e7f3ea"), "riesgo": colors.HexColor("#fbe9e9"),
             "info": colors.HexColor("#eaf1f8")}[tipo]
    borde = {"ok": colors.HexColor("#2f6f4e"), "riesgo": colors.HexColor("#b02a2a"),
             "info": colors.HexColor("#1b3a5c")}[tipo]
    contenido = Paragraph(f"<b>{titulo}</b><br/>{texto}", styles["Cuerpo"])
    t = Table([[contenido]], colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fondo),
        ("BOX", (0, 0), (-1, -1), 1.1, borde),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))


def severidad_badge(texto, color):
    t = Table([[Paragraph(texto, styles["Severidad"])]], colWidths=[2.6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


# ----------------------------------------------------------------------
# PORTADA
# ----------------------------------------------------------------------
story.append(Spacer(1, 4 * cm))
story.append(Paragraph("INFORME TÉCNICO DE CONSULTORÍA", styles["TituloPortada"]))
story.append(Paragraph(
    "Identificación, Autenticación y Autorización en una Entidad Hospitalaria<br/>"
    "(CAI 3 — Parte 1)", styles["SubtituloPortada"]))
story.append(Spacer(1, 1.2 * cm))
story.append(HRFlowable(width="60%", thickness=1, color=colors.HexColor("#1b3a5c"), hAlign="CENTER"))
story.append(Spacer(1, 1.2 * cm))

datos_portada = [
    ["Asignatura:", "Seguridad en Sistemas Informáticos y en Internet"],
    ["Equipo:", "Security Team 2 (ST-2)"],
    ["Autores:", "Raimundo García Pérez, Konstantinos Peridis, Luis Alarcón Conradi"],
    ["Fecha:", "13 de noviembre de 2026"],
    ["Código de entrega:", "ST-2-CAI3-Parte1"],
]
t = Table(datos_portada, colWidths=[4 * cm, 11 * cm])
t.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 10),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(t)
story.append(Spacer(1, 1.5 * cm))
story.append(Paragraph(
    "Resumen ejecutivo: se ha auditado el prototipo de Portal Médico del Hospital "
    "(Servidor de Identidad OAuth2 + FreeOTP en el puerto 8000, y Portal Médico/API "
    "en el puerto 8001). Se identificaron y demostraron <b>8 vulnerabilidades "
    "explotables</b> (4 críticas, 3 altas, 1 media-alta) que permitían, entre otras "
    "cosas, suplantar a cualquier usuario sin contraseña ni segundo factor, y que un "
    "paciente modificase historiales clínicos. Se corrigieron todas en una versión "
    "endurecida del código (carpeta <i>SourceCode_hardened</i>), y se verificó que "
    "los mismos ataques ya no funcionan, sin romper el uso legítimo del sistema.",
    styles["Cuerpo"]))
story.append(PageBreak())

# ----------------------------------------------------------------------
# 1. INTRODUCCION Y ARQUITECTURA
# ----------------------------------------------------------------------
h1("1. Introducción y arquitectura del sistema")
p("El Hospital desea añadir una capa de autenticación TOTP (FreeOTP) a su sistema "
  "de acceso a servicios, y usar OAuth 2.0 para segmentar el acceso por roles. El "
  "prototipo entregado por el Hospital consta de dos microservicios independientes:")
story.append(ListFlowable([
    ListItem(Paragraph("<b>Servidor de Identidad</b> (Authorization Server, puerto 8000): gestiona usuarios, "
                        "contraseñas (hash Argon2), el segundo factor TOTP y la emisión de tokens JWT.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>Portal Médico</b> (Cliente OAuth2 + API, puerto 8001): interfaz web y endpoints "
                        "<code>/api/historial</code> que consumen el token emitido por el servidor de identidad.", styles["Cuerpo"])),
], bulletType="bullet"))
p("Perfiles de prueba: <b>Rocío</b> (paciente, scope <i>paciente:leer</i>) y <b>Dr. Gasca</b> "
  "(médico, scopes <i>paciente:leer</i> + <i>medico:escribir</i>).")
p("Alcance de la consultoría, según el enunciado: no se evalúan bases de datos reales, "
  "gestión de cuentas, diseño visual (CSS), gestores de secretos externos ni sistemas de "
  "monitorización externa. Los datos viven en memoria (diccionarios de Python).")

h2("1.1 Metodología de trabajo")
story.append(ListFlowable([
    ListItem(Paragraph("<b>Fase 1 — Red Team (caja negra):</b> ataques desde fuera, sin modificar el código "
                        "fuente, usando el navegador, <code>curl</code> y scripts Python.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>Fase 2 — Auditoría de código:</b> se confirma cada hallazgo con la línea exacta del "
                        "código y se buscan fallos adicionales no visibles desde fuera.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>Fase 3 — Blue Team:</b> corrección del código en una copia independiente "
                        "(<i>SourceCode_hardened</i>), sin tocar el original.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>Fase 4 — Verificación:</b> se repiten los mismos ataques contra la versión corregida "
                        "y se comprueba que el uso legítimo sigue funcionando.", styles["Cuerpo"])),
], bulletType="1"))
story.append(PageBreak())

# ----------------------------------------------------------------------
# 2. APARTADO A) RED TEAM
# ----------------------------------------------------------------------
h1("2. Apartado a) — Perspectiva Red Team (Explotación)")
p("Se realizaron 9 pruebas de caja negra, sin modificar el código fuente en ningún "
  "momento. A continuación se detalla cada una con su evidencia.")

hallazgos_rt = [
    ("RT-01", "Clave de firma JWT expuesta públicamente", COLOR_CRIT, "CRÍTICA",
     "El endpoint <code>/.well-known/jwt-key</code> del Servidor de Identidad devuelve, sin "
     "autenticación, la clave simétrica HS256 con la que se firman todos los tokens JWT.",
     "Con la clave en la mano se fabricó un JWT para el Dr. Gasca (scope "
     "<i>medico:escribir</i>) sin pasar por login, password ni TOTP, y se usó para modificar "
     "un historial clínico con éxito (HTTP 200).",
     []),
    ("RT-02", "Secreto TOTP accesible sin autenticación", COLOR_CRIT, "CRÍTICA",
     "El endpoint <code>/setup-mfa?user=&lt;nombre&gt;</code> no exige ningún login y muestra el "
     "secreto TOTP y el código QR de cualquier usuario.",
     "Se obtuvieron los secretos TOTP de Rocío y del Dr. Gasca sin credenciales, lo que "
     "permite generar sus códigos de 6 dígitos como si se tuviera su móvil.", []),
    ("RT-03", "Flujo OAuth2 sin PKCE (code_challenge ausente)", COLOR_ALTA, "ALTA",
     "La redirección a <code>/oauth/authorize</code> no incluye <code>code_challenge</code> ni "
     "<code>code_challenge_method</code>: PKCE está desactivado "
     "(<code>CodeChallenge(required=False)</code>) y el cliente es público "
     "(<code>token_endpoint_auth_method: none</code>).",
     "Se completó un login legítimo y se interceptó el <code>code</code> de la redirección a "
     "<code>/callback</code>. El atacante canjeó ese código directamente en "
     "<code>/oauth/token</code> y obtuvo un <code>access_token</code> válido de la víctima, "
     "<b>sin conocer su contraseña ni su código TOTP</b>. Esta prueba responde directamente a "
     "la pregunta del enunciado sobre el riesgo de interceptar el <i>code</i> en /callback.",
     []),
    ("RT-04", "Escalada de privilegios en la API", COLOR_CRIT, "CRÍTICA",
     "<code>POST /api/historial</code> solo exige <code>@require_oauth()</code> sin especificar "
     "scope: cualquier token válido, incluso el de un paciente, puede escribir.",
     "Con el token de Rocío (paciente, scope <i>paciente:leer</i>) se modificó un historial "
     "médico mediante <code>POST /api/historial</code> (HTTP 200).", []),
    ("RT-05", "Token JWT accesible desde JavaScript", COLOR_ALTA, "ALTA",
     "La cookie <code>access_token</code> se crea con <code>httponly=False</code>: es legible "
     "desde <code>document.cookie</code>.",
     "Tras el login en el navegador real, el botón \"Inspeccionar Cookies desde JS\" de la "
     "propia aplicación mostró el JWT completo en <code>document.cookie</code>. En una app con "
     "una vulnerabilidad XSS, esto permitiría robar el token con una sola línea de JavaScript.",
     ["evidencias/red_team/capturas/06_cookie_robable_js.jpg"]),
    ("RT-06", "Enumeración de usuarios", COLOR_MEDIA, "MEDIA",
     "El login devuelve mensajes de error distintos para \"usuario inexistente\" y "
     "\"contraseña incorrecta\".",
     "Se comparon ambos mensajes: \"El usuario especificado no existe en la base de datos\" "
     "frente a \"Contraseña incorrecta para este usuario\", permitiendo distinguir cuentas "
     "válidas.", []),
    ("RT-07", "Código TOTP reutilizable (sin control anti-replay)", COLOR_MEDIA, "MEDIA",
     "<code>totp.verify(..., valid_window=1)</code> no registra los códigos ya consumidos.",
     "El mismo código de 6 dígitos del Dr. Gasca se usó dos veces seguidas y generó dos "
     "códigos de autorización distintos, es decir, el servidor lo aceptó en ambas ocasiones.",
     []),
    ("RT-08", "El logout no revoca el token", COLOR_ALTA, "ALTA",
     "<code>/logout</code> solo borra la cookie del navegador; no existe revocación ni "
     "introspección de tokens.",
     "Tras hacer logout, el mismo JWT (copiado antes de cerrar sesión) se siguió aceptando "
     "contra la API (HTTP 200), demostrando que un token robado sigue vivo hasta su "
     "expiración aunque el usuario \"cierre sesión\".", []),
    ("RT-09", "Confusión de algoritmo (alg: none)", COLOR_OK, "SIN RIESGO (verificado)",
     "Se construyó un JWT con cabecera <code>alg: none</code> y sin firma, para comprobar si "
     "el validador del cliente lo aceptaría.",
     "El resultado fue <code>HTTP 401 Unauthorized</code>: Authlib/<i>jose</i> rechaza "
     "correctamente el token. Esta prueba negativa demuestra que la auditoría también "
     "verificó controles que SÍ funcionaban, no solo buscó fallos.", []),
]

for rid, titulo, color, sev, causa, resultado, imagenes in hallazgos_rt:
    bloque = []
    fila = Table([[Paragraph(f"<b>{rid}. {titulo}</b>", styles["Cuerpo"]), severidad_badge(sev, color)]],
                  colWidths=[11.5 * cm, 3.5 * cm])
    fila.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    bloque.append(fila)
    bloque.append(Spacer(1, 3))
    bloque.append(Paragraph(f"<b>Causa:</b> {causa}", styles["Cuerpo"]))
    bloque.append(Paragraph(f"<b>Resultado del ataque:</b> {resultado}", styles["Cuerpo"]))
    bloque.append(Spacer(1, 6))
    story.append(KeepTogether(bloque))
    for im in imagenes:
        img(im, width=11 * cm)
    story.append(Spacer(1, 6))

story.append(PageBreak())

# ----------------------------------------------------------------------
# 3. APARTADO B) BLUE TEAM
# ----------------------------------------------------------------------
h1("3. Apartado b) — Perspectiva Blue Team (Hardening)")
p("Se corrigió el código de ambos servidores y las plantillas HTML en una copia "
  "independiente (<i>SourceCode_hardened/</i>), manteniendo intacto el original. "
  "Resumen de las correcciones aplicadas:")

correcciones = [
    ["ID", "Corrección aplicada"],
    ["RT-01", "Firma asimétrica RS256 (par de claves RSA). El servidor firma con la clave PRIVADA "
              "(nunca sale del proceso) y publica solo la clave PÚBLICA en "
              "<code>/.well-known/jwks.json</code>. Se verificó que un token forjado con otra clave "
              "privada es rechazado, aunque la clave pública real sea conocida."],
    ["RT-02", "<code>/setup-mfa</code> exige ahora la contraseña real del usuario antes de generar el "
              "QR, y ya no muestra el secreto TOTP en texto plano en la página."],
    ["RT-03", "PKCE obligatorio con S256 (<code>CodeChallenge(required=True)</code>) y cliente "
              "confidencial con <code>client_secret</code> verificado "
              "(<code>token_endpoint_auth_method: client_secret_basic</code>)."],
    ["RT-04", "<code>POST /api/historial</code> exige explícitamente el scope "
              "<code>medico:escribir</code>."],
    ["RT-05", "Cookie <code>access_token</code> con <code>httponly=True</code> y "
              "<code>samesite=Strict</code>. El nombre de usuario ya no se lee con JavaScript: lo "
              "inyecta el propio servidor Flask."],
    ["RT-06", "Mensaje de error único para cualquier fallo de login: \"Usuario, contraseña o "
              "código FreeOTP incorrectos.\""],
    ["RT-07", "Control anti-repetición: cada código TOTP consumido queda registrado y se "
              "rechaza si se reutiliza."],
    ["RT-08", "Nuevo endpoint <code>/oauth/revoke</code>: el logout (ahora por POST, no GET) "
              "revoca el <code>jti</code> del token en el servidor. La API consulta la revocación "
              "en cada petición."],
    ["Extra", "Bloqueo temporal (HTTP 429) tras 5 intentos de login fallidos sobre el mismo "
              "usuario (mitiga fuerza bruta)."],
    ["CODE-01", "<code>debug=False</code> en ambos servidores: se desactiva el depurador "
                "interactivo de Werkzeug."],
    ["CODE-04", "Rotación de refresh tokens (se invalida el anterior al emitir uno nuevo)."],
    ["CODE-05", "<code>expires_in</code> de la respuesta ajustado para coincidir con la "
                "caducidad real del JWT (antes indicaba 10 días cuando el token expiraba en 1h)."],
    ["CODE-06", "Se eliminaron las credenciales de prueba precargadas en el HTML de "
                "<code>login.html</code>."],
    ["CODE-07", "Cabeceras de seguridad: <code>Content-Security-Policy</code>, "
                "<code>X-Content-Type-Options</code>, <code>X-Frame-Options</code>, "
                "<code>Referrer-Policy</code>, <code>Cache-Control: no-store</code>."],
]
correcciones_wrapped = [correcciones[0]] + [
    [Paragraph(f"<b>{r[0]}</b>", styles["Cuerpo"]), Paragraph(r[1], styles["Cuerpo"])]
    for r in correcciones[1:]
]
tbl = Table(correcciones_wrapped, colWidths=[2 * cm, 13 * cm], repeatRows=1)
tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b3a5c")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 8.3),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f8")]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(tbl)
story.append(Spacer(1, 10))

h2("3.1 Incidencia detectada y corregida durante la propia verificación")
p("Al endurecer el Portal Médico con la cabecera <code>Content-Security-Policy: "
  "default-src 'self'</code>, los botones de la interfaz dejaron de funcionar: la CSP "
  "bloqueaba el <code>&lt;script&gt;</code> interno y los <code>onclick</code> en línea de "
  "<code>portal.html</code>. Se corrigió moviendo el JavaScript a un fichero externo "
  "(<code>static/portal.js</code>, mismo origen) y sustituyendo los <code>onclick</code> por "
  "<code>addEventListener</code>, sin necesidad de relajar la política CSP. Esto demuestra "
  "que cada corrección se verificó de extremo a extremo, no solo a nivel de código.")
story.append(PageBreak())

# ----------------------------------------------------------------------
# 4. VERIFICACION (ANTES / DESPUES)
# ----------------------------------------------------------------------
h1("4. Verificación — resultado antes / después")
p("Se repitieron exactamente los mismos ataques de la Fase 1 contra la versión corregida "
  "(SourceCode_hardened), en los mismos puertos (8000/8001).")

verif = [
    ["Ataque", "Antes", "Después"],
    ["RT-01 — Forjar JWT con la clave", "Conseguido", "Rechazado (401 invalid_token)"],
    ["RT-02 — Robar secreto TOTP sin login", "Conseguido", "Requiere contraseña real"],
    ["RT-03 — Interceptar code sin PKCE", "Conseguido", "PKCE+S256 obligatorio; code sin verifier no es canjeable"],
    ["RT-04 — Paciente escribe historial", "Conseguido (HTTP 200)", "Bloqueado (HTTP 403 insufficient_scope)"],
    ["RT-05 — Robar JWT desde JS", "Token visible en document.cookie", "Cookie HttpOnly: token no accesible por JS"],
    ["RT-06 — Enumerar usuarios", "Mensajes distintos", "Mensaje único"],
    ["RT-07 — Reutilizar código TOTP", "Aceptado dos veces", "Segundo uso rechazado (401)"],
    ["RT-08 — Token tras logout", "Seguía siendo válido", "Revocado; mismo token da 401 tras logout"],
    ["RT-09 — alg:none", "Ya rechazado (sin riesgo)", "Sigue rechazado (sin cambios necesarios)"],
    ["Extra — fuerza bruta", "Sin límite de intentos", "HTTP 429 al 6º intento fallido"],
]
verif_wrapped = [verif[0]] + [
    [Paragraph(cell, styles["Cuerpo"]) for cell in r] for r in verif[1:]
]
tblv = Table(verif_wrapped, colWidths=[5.2 * cm, 4.9 * cm, 5 * cm], repeatRows=1)
tblv.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b3a5c")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 8),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6f8")]),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
story.append(tblv)
story.append(Spacer(1, 12))

h2("4.1 Evidencia visual del uso legítimo tras la corrección")
p("Login legítimo de Rocío con usuario, contraseña y código FreeOTP real (obtenido con "
  "su propia contraseña, ya que /setup-mfa ahora la exige):")
img("evidencias/red_team/capturas/06b_login_exitoso_navegador.jpg", width=10 * cm)

p("Rocío (paciente) puede leer su historial, pero ya no puede modificarlo "
  "(HTTP 403 Forbidden / insufficient_scope):")
img("evidencias/pruebas_despues/capturas/10_rt04_bloqueado_403.jpg", width=11 * cm)

p("Cierre de sesión correcto (el servidor revoca el token, no solo borra la cookie):")
img("evidencias/pruebas_despues/capturas/15_logout_navegador.jpg", width=10 * cm)

story.append(PageBreak())

# ----------------------------------------------------------------------
# 5. APARTADO C) RECOMENDACIONES
# ----------------------------------------------------------------------
h1("5. Apartado c) — Recomendaciones para el Hospital")
story.append(ListFlowable([
    ListItem(Paragraph("Desplegar la versión corregida (<i>SourceCode_hardened</i>, adjunta en este "
                        "entregable) en un entorno de pruebas antes de pasar a producción.", styles["Cuerpo"])),
    ListItem(Paragraph("En un despliegue real, servir ambos servicios por HTTPS y eliminar la "
                        "variable <code>AUTHLIB_INSECURE_TRANSPORT</code> (solo válida para este "
                        "laboratorio en HTTP/localhost).", styles["Cuerpo"])),
    ListItem(Paragraph("Sustituir los secretos de desarrollo (<code>HOSPITAL_CLIENT_SECRET</code>, "
                        "<code>INTERNAL_API_KEY</code>, <code>FLASK_SECRET_KEY</code>) por valores "
                        "generados aleatoriamente y gestionados fuera del código (variables de entorno "
                        "del servidor, o un gestor de secretos si el hospital ya dispone de uno).", styles["Cuerpo"])),
    ListItem(Paragraph("Cuando se pase a una base de datos real, mantener el mismo modelo de "
                        "permisos por scope y añadir también allí los controles de bloqueo por "
                        "intentos fallidos y de revocación de tokens.", styles["Cuerpo"])),
    ListItem(Paragraph("Revisar periódicamente los registros de acceso (fuera del alcance de este "
                        "CAI) para detectar patrones de fuerza bruta o reutilización de tokens que "
                        "aquí solo se han podido probar de forma puntual.", styles["Cuerpo"])),
    ListItem(Paragraph("Mantener las pruebas automatizadas de este informe (carpeta "
                        "<code>evidencias/</code>) como base de un conjunto de pruebas de regresión "
                        "de seguridad para futuros cambios del portal.", styles["Cuerpo"])),
], bulletType="bullet"))
story.append(Spacer(1, 10))

caja_conclusion(
    "Conclusión apartado c):",
    "El prototipo recibido tenía 8 vulnerabilidades explotables (4 críticas, 3 altas, "
    "1 media-alta), que permitían desde suplantar a cualquier usuario sin contraseña "
    "hasta que un paciente alterase historiales médicos. Todas quedan corregidas en "
    "<i>SourceCode_hardened</i> y verificadas de extremo a extremo. Recomendación: no "
    "pasar a producción sin aplicar también las medidas de este apartado (HTTPS, "
    "gestión de secretos, monitorización).",
    tipo="riesgo",
)

story.append(PageBreak())

# ----------------------------------------------------------------------
# 6. CONCLUSIONES GLOBALES
# ----------------------------------------------------------------------
h1("6. Conclusiones Globales")
p("Esta consultoría demuestra que, en un sistema de identidad, autenticación y "
  "autorización, la seguridad no depende de un único mecanismo sino de la cadena "
  "completa: cifrado de los tokens, protocolo OAuth2 bien implementado (PKCE, cliente "
  "confidencial), control de permisos en la propia API, y manejo correcto del ciclo de "
  "vida de la sesión (expiración y revocación).")
story.append(ListFlowable([
    ListItem(Paragraph("<b>Un segundo factor (FreeOTP) no sirve de nada si se puede saltar</b>: "
                        "RT-02 permitía obtener el secreto TOTP de cualquier usuario sin ninguna "
                        "credencial, anulando por completo el valor del 2FA.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>OAuth2 sin PKCE es frágil incluso usando HTTPS</b>: la pregunta del "
                        "enunciado queda respondida con una prueba real (RT-03): un code "
                        "interceptado en /callback se cambia directamente por un token válido.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>Los scopes deben comprobarse en cada endpoint</b>, no basta con exigir "
                        "\"estar autenticado\": RT-04 demuestra que un paciente podía escribir "
                        "historiales médicos con su propio token legítimo.", styles["Cuerpo"])),
    ListItem(Paragraph("<b>\"Cerrar sesión\" debe significar algo en el servidor</b>, no solo en el "
                        "navegador: RT-08 muestra que sin revocación, un token robado sigue vivo "
                        "pese al logout.", styles["Cuerpo"])),
], bulletType="bullet"))

h2("Herramientas y librerías utilizadas")
p("Python 3.10, Flask 3.0.3, Authlib 1.3.2 (servidor y cliente OAuth2, JWT), "
  "<code>cryptography</code> (firma RS256), PyOTP 2.9.0 y qrcode 7.4.2 (TOTP/FreeOTP), "
  "Passlib + Argon2 (hash de contraseñas), OpenCV (lectura de códigos QR para las "
  "pruebas de verificación), Claude in Chrome (automatización de navegador para las "
  "evidencias visuales), <code>curl</code> y scripts Python propios para los ataques.")

h2("Relación de Anexos Entregados")
p("• <b>Anexo I:</b> <code>evidencias/auditoria_codigo/hallazgos.md</code> — tabla completa "
  "de las 16 vulnerabilidades identificadas, con fichero y línea de código.<br/>"
  "• <b>Anexo II:</b> <code>evidencias/red_team/</code> — capturas, respuestas HTTP y scripts "
  "de cada ataque de la Fase 1 (caja negra).<br/>"
  "• <b>Anexo III:</b> <code>evidencias/pruebas_despues/</code> — capturas, scripts y tabla "
  "comparativa de la Fase 4 (verificación antes/después).<br/>"
  "• <b>Anexo IV:</b> <code>SourceCode_hardened/</code> — proyecto completo corregido "
  "(Servidor de Identidad, Portal Médico, plantillas y <code>requirements.txt</code>).")

doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    title="ST-2-CAI3-Parte1", author="Security Team 2 (ST-2)",
)
doc.build(story, onFirstPage=_marca_agua_y_pie, onLaterPages=_marca_agua_y_pie)
print(f"PDF generado: {OUT}")
