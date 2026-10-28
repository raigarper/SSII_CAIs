# -*- coding: utf-8 -*-
"""
Generador del informe final ST-2-CAI2B.pdf
Replica el estilo visual de los informes anteriores (ST-2-CAI0A, ST-2-CAI1B):
cabecera con titulo/metadatos, secciones numeradas, tablas con cabecera azul,
cajas de conclusion resaltadas, y anexo confidencial final.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas as rl_canvas
import os

BASE = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2"
TRABAJO = os.path.join(BASE, "trabajo")
OUT = os.path.join(BASE, "ST-2-CAI2B.pdf")

# ---------------------------------------------------------------- Paleta ---
AZUL_OSCURO = colors.HexColor("#1F3864")
AZUL_TABLA = colors.HexColor("#2E5395")
AZUL_CLARO = colors.HexColor("#DCE6F1")
GRIS_TEXTO = colors.HexColor("#222222")
VERDE_OK = colors.HexColor("#E2F0D9")
VERDE_BORDE = colors.HexColor("#548235")
ROJO_ALERTA = colors.HexColor("#FCE4E4")
ROJO_BORDE = colors.HexColor("#C00000")
GRIS_CONF = colors.HexColor("#EDEDED")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TituloInforme", fontName="Helvetica-Bold", fontSize=16,
                           textColor=AZUL_OSCURO, spaceAfter=4, leading=19))
styles.add(ParagraphStyle(name="Subtitulo", fontName="Helvetica", fontSize=11,
                           textColor=GRIS_TEXTO, spaceAfter=8, leading=14))
styles.add(ParagraphStyle(name="Meta", fontName="Helvetica", fontSize=8.5,
                           textColor=GRIS_TEXTO, leading=12))
styles.add(ParagraphStyle(name="H1", fontName="Helvetica-Bold", fontSize=13,
                           textColor=AZUL_OSCURO, spaceBefore=12, spaceAfter=6))
styles.add(ParagraphStyle(name="H2", fontName="Helvetica-Bold", fontSize=11,
                           textColor=AZUL_TABLA, spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle(name="Cuerpo", fontName="Helvetica", fontSize=9.3,
                           leading=12.6, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle(name="CuerpoPeq", fontName="Helvetica", fontSize=8.3,
                           leading=11, alignment=TA_JUSTIFY, spaceAfter=4))
styles.add(ParagraphStyle(name="Pie", fontName="Helvetica", fontSize=7.5,
                           textColor=colors.grey, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CajaTitulo", fontName="Helvetica-Bold", fontSize=9.5))
styles.add(ParagraphStyle(name="CajaCuerpo", fontName="Helvetica", fontSize=8.8, leading=11.5))
styles.add(ParagraphStyle(name="AnexoTitulo", fontName="Helvetica-Bold", fontSize=13,
                           textColor=colors.white, spaceAfter=6))
styles.add(ParagraphStyle(name="Mono", fontName="Courier", fontSize=7.6, leading=10))

# ----------------------------------------------------------- Utilidades ---
def tabla_estandar(data, colWidths=None, header_bg=AZUL_TABLA, font_size=8.2):
    data = [[c if isinstance(c, Paragraph) else Paragraph(str(c), styles["CuerpoPeq"]) for c in row]
            for row in data]
    t = Table(data, colWidths=colWidths, repeatRows=1)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0B0B0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FB")]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(style))
    return t

def caja(titulo, cuerpo_html, bg=AZUL_CLARO, borde=AZUL_TABLA):
    data = [[Paragraph(f"<b>{titulo}</b><br/>{cuerpo_html}", styles["CajaCuerpo"])]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg),
        ('BOX', (0, 0), (-1, -1), 1, borde),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t

def imagen_centrada(path, max_w_cm, max_h_cm=None):
    from PIL import Image as PILImage
    w, h = PILImage.open(path).size
    ratio = w / h
    width = max_w_cm * cm
    height = width / ratio
    if max_h_cm and height > max_h_cm * cm:
        height = max_h_cm * cm
        width = height * ratio
    return Image(path, width=width, height=height)

# ---------------------------------------------------------- Documento -----
doc = SimpleDocTemplate(
    OUT, pagesize=A4,
    topMargin=1.6*cm, bottomMargin=1.6*cm, leftMargin=1.6*cm, rightMargin=1.6*cm,
    title="ST-2-CAI2B", author="Security Team 2"
)

story = []

# ---- Cabecera / portada -----------------------------------------------
story.append(Paragraph("INFORME TÉCNICO DE CONSULTORÍA", styles["TituloInforme"]))
story.append(Paragraph(
    "Esteganografía en Imágenes Radiológicas y Auditoría de Cifrado de Firmas Digitalizadas "
    "(CAI 2 &ndash; Parte 2)", styles["Subtitulo"]))
story.append(HRFlowable(width="100%", thickness=1.2, color=AZUL_OSCURO, spaceAfter=6))
story.append(Paragraph(
    "<b>Asignatura:</b> Seguridad en Sistemas Informáticos y en Internet &nbsp;|&nbsp; "
    "<b>Equipo:</b> Security Team 2 (ST-2)<br/>"
    "<b>Autores:</b> Raimundo García Pérez, Konstantinos Peridis, Luis Alarcón Conradi<br/>"
    "<b>Fecha:</b> 27 de octubre de 2026 &nbsp;|&nbsp; <b>Código de entrega:</b> ST-2-CAI2B",
    styles["Meta"]))
story.append(HRFlowable(width="100%", thickness=0.6, color=colors.grey, spaceBefore=6, spaceAfter=10))

# ---- Resumen ejecutivo ---------------------------------------------------
story.append(Paragraph("Resumen Ejecutivo", styles["H1"]))
story.append(Paragraph(
    "A petición de la Dirección del Hospital, el equipo de SecurTech Advisory ha evaluado el uso de "
    "<b>esteganografía LSB</b> para insertar firmas ocultas en radiografías, ha realizado un "
    "<b>estegoanálisis forense</b> sobre una imagen sospechosa de fuga de información, y ha auditado "
    "la seguridad real del cifrado AES-256 aplicado a imágenes de firmas de médicos en un portátil "
    "sustraído. Los tres resultados principales son:", styles["Cuerpo"]))

story.append(caja(
    "a) Método LSB:",
    "Técnicamente viable para firmas de 128&ndash;512 caracteres (capacidad de sobra, imperceptible "
    "a nivel de señal: PSNR &gt; 74 dB), pero <b>extremadamente frágil</b>: un simple 1% de ruido "
    "aleatorio ya corrompe el mensaje, y cualquier recorte que altere el ancho de la imagen también "
    "lo destruye, aunque conserve físicamente los píxeles del mensaje.", bg=AZUL_CLARO, borde=AZUL_TABLA))
story.append(Spacer(1, 4))
story.append(caja(
    "b) Estegoanálisis forense:",
    "La imagen sospechosa (<i>Dibujo.bmp</i>) contenía realmente un mensaje oculto de 37.099 bytes "
    "&mdash;confirmado por dos métodos estadísticos independientes&mdash; que, al extraerlo, resultó "
    "ser un <b>plano de evacuación y extinción de incendios del edificio</b>: información de "
    "seguridad física filtrada de forma encubierta.", bg=AZUL_CLARO, borde=AZUL_TABLA))
story.append(Spacer(1, 4))
story.append(caja(
    "c) Cifrado AES-256 de las firmas sustraídas:",
    "<font color='#C00000'><b>NO se puede dar por segura la información.</b></font> Aunque la clave "
    "de 256 bits es inviable de romper por fuerza bruta, el fichero cifrado muestra la firma "
    "inequívoca del <b>modo de cifrado ECB</b>, que filtra el patrón visual del contenido original. "
    "Se ha logrado reconstruir el nombre, el NIF y la silueta de una firma manuscrita "
    "<b>sin descifrar nada y sin conocer la clave</b>.", bg=ROJO_ALERTA, borde=ROJO_BORDE))

story.append(PageBreak())

# ============================================================ SECCION 1 ===
story.append(Paragraph("1. Introducción y Objetivos", styles["H1"]))
story.append(Paragraph(
    "Esta consultoría es la continuación de CAI 2 &ndash; Parte 1 (cifrado de imágenes radiológicas "
    "y auditoría forense de VeraCrypt). Mientras aquella parte abordaba la <b>confidencialidad por "
    "cifrado</b>, esta Parte 2 aborda la <b>esteganografía</b>: ocultar información a simple vista "
    "dentro de imágenes, y detectarla cuando otros la usan. Se tratan tres consultas: (a) viabilidad "
    "del método LSB para firmar radiografías, (b) estegoanálisis forense de una imagen sospechosa de "
    "fuga de datos, y (c) seguridad real de imágenes de firmas de médicos cifradas con AES-256 en un "
    "equipo sustraído.", styles["Cuerpo"]))
story.append(Paragraph(
    "<b>Entorno y herramientas:</b> Virtual Steganographic Laboratory (VSL 1.1, Java 17), OpenSSL "
    "3.5.3, y scripts propios en Python 3.10 (Pillow, NumPy, SciPy) para estegoanálisis estadístico "
    "independiente, distorsiones y auditoría de cifrado. Todos los scripts se adjuntan como anexos "
    "digitales junto a este informe.", styles["Cuerpo"]))

# ============================================================ SECCION 2 ===
story.append(Paragraph("2. Apartado a) &mdash; Estudio del Método LSB", styles["H1"]))

story.append(Paragraph("2.1. Criterio 1: Tamaño de imagen necesario", styles["H2"]))
story.append(Paragraph(
    "Con 24 bits por píxel (3 bytes RGB), el método LSB dispone de 3 bits &laquo;libres&raquo; por "
    "píxel: capacidad (bytes) = ancho &times; alto &times; 3 / 8.", styles["Cuerpo"]))
t1 = tabla_estandar([
    ["Firma", "Lado mínimo imagen cuadrada", "Capacidad real a ese tamaño"],
    ["128 caracteres", "19 &times; 19 px", "135 bytes"],
    ["512 caracteres", "37 &times; 37 px", "513 bytes"],
    ["Imagen de prueba (512&times;512, generada)", "&mdash;", "98.304 bytes"],
], colWidths=[6*cm, 6*cm, 5*cm])
story.append(t1)
story.append(Spacer(1, 4))
story.append(Paragraph(
    "<b>Validación experimental:</b> se ocultaron dos firmas reales (133 y 432 caracteres) en una "
    "imagen portadora de prueba (512&times;512 px, 786.486 bytes). En ambos casos el fichero "
    "resultante pesó <b>exactamente lo mismo</b> que el original, y la extracción posterior recuperó "
    "el mensaje <b>bit a bit idéntico</b> al original (verificado con <i>diff</i>).", styles["Cuerpo"]))
story.append(caja("Conclusión Criterio 1:",
    "Cualquier radiografía real (cientos o miles de píxeles de lado) tiene capacidad de sobra para "
    "una firma de hasta 512 caracteres sin aumentar de tamaño. El tamaño de imagen nunca es el "
    "factor limitante.", bg=VERDE_OK, borde=VERDE_BORDE))

story.append(Paragraph("2.2. Criterio 2: Confidencialidad", styles["H2"]))
t2 = Table([
    [Paragraph(c, styles["CuerpoPeq"]) for c in row] for row in
    [["Versión", "PSNR (dB)", "Visible a simple vista", "Detectable por bit-plane"],
     ["Firma corta (133 c.)", "79,54", "No", "No"],
     ["Firma larga (432 c.)", "74,57", "No", "No"]]
], colWidths=[5*cm, 3*cm, 4.5*cm, 4.5*cm])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), AZUL_TABLA), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FB")]),
]))
story.append(t2)
story.append(Spacer(1, 5))
story.append(Paragraph(
    "El PSNR (relación señal/ruido de pico) mide numéricamente cuánto cambia la imagen; a partir de "
    "~40 dB se considera imperceptible. Ambos valores obtenidos son muy superiores. El test "
    "estadístico de <b>Chi-cuadrado de Pares de Valores</b> (Westfeld-Pfitzmann), en cambio, "
    "<b>no fue fiable</b> en nuestra imagen de prueba: dio indicios de alteración incluso en la "
    "imagen <u>original sin ningún mensaje</u>, porque esta ya tenía ruido/textura de fondo alto "
    "(deliberadamente, para simular una radiografía real). Esto demuestra que ningún test "
    "estadístico aislado es fiable al 100% &mdash; conclusión que se confirma en el apartado b).",
    styles["Cuerpo"]))
story.append(Paragraph(
    "<b>Mejora de confidencialidad propuesta y verificada:</b> cifrar el mensaje con AES-256-CBC "
    "(enlazando con CAI 2 &ndash; Parte 1) antes de ocultarlo. Si alguien detecta y extrae los bits "
    "LSB sin conocer la clave, obtiene únicamente datos binarios ilegibles; con la clave correcta, "
    "el mensaje se recupera idéntico al original. Verificado experimentalmente con OpenSSL "
    "(<font face='Courier' size='7.6'>openssl enc -aes-256-cbc</font>).", styles["Cuerpo"]))

story.append(Paragraph("2.3. Criterio 3: Robustez ante distorsiones", styles["H2"]))
t3 = Table([
    [Paragraph(c, styles["CuerpoPeq"]) for c in row] for row in
    [["Distorsión aplicada", "¿Mensaje recuperable?", "Motivo técnico"],
     ["Salt &amp; Pepper 1%", "No", "Basta 1 píxel alterado de cada 100 para corromper bits del mensaje"],
     ["Salt &amp; Pepper 1%→5%→10%→20% (acumulado)", "No (progresivamente peor)", "Incluso la cabecera de longitud del mensaje se corrompe"],
     ["Crop que excluye la zona del mensaje", "No (falla directamente)", "Los píxeles con el mensaje ya no existen en la imagen resultante"],
     ["Crop que cambia el ANCHO (aunque conserve la esquina del mensaje)", "No", "LSB secuencial lee fila a fila según el ancho; al cambiar el ancho se desincroniza la lectura desde la 2ª fila"],
     ["Crop que conserva el ancho completo", "Sí, íntegro", "El orden de lectura fila a fila coincide exactamente con el de la codificación"]]
], colWidths=[6.3*cm, 3.7*cm, 7*cm])
t3.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), AZUL_TABLA), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTSIZE', (0,0), (-1,-1), 7.6),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FB")]),
]))
story.append(t3)
story.append(Spacer(1, 5))
story.append(caja("Conclusión Criterio 3 y mejoras propuestas:",
    "El LSB secuencial simple es <b>extremadamente frágil</b>: no sobrevive ni al 1% de ruido ni a "
    "recortes que cambien la geometría de la imagen. Solo es adecuado si la imagen viaja intacta "
    "byte a byte (p. ej. en red interna sin recompresión), que es el escenario hospitalario descrito. "
    "Mejoras: (1) códigos de corrección de errores o repetición del mensaje para resistir ruido; "
    "(2) repartir el mensaje por toda la imagen, no solo al principio, para resistir recortes "
    "parciales; (3) si se prevé compresión o redimensionado, LSB no es viable y debe sustituirse por "
    "técnicas robustas en el dominio de la frecuencia (DCT, p. ej. F5).", bg=ROJO_ALERTA, borde=ROJO_BORDE))

story.append(PageBreak())

# ============================================================ SECCION 3 ===
story.append(Paragraph("3. Apartado b) &mdash; Estegoanálisis Forense", styles["H1"]))
story.append(Paragraph(
    "Se recibió <i>Dibujo.bmp</i> (338&times;338 px, 24 bits) como imagen sospechosa de contener "
    "información filtrada por un Jefe de Servicio. Siguiendo la recomendación del enunciado, se usó "
    "una herramienta <b>distinta de VSL</b> además de la propia VSL, para triangular resultados.",
    styles["Cuerpo"]))

story.append(Paragraph("3.1. Metodología aplicada", styles["H2"]))
story.append(Paragraph(
    "<b>Paso 1 &ndash; Estegoanálisis con VSL (LSB-RS, Fridrich):</b> resultado &laquo;no "
    "message&raquo;, con una estimación de 27.299 bytes. Este fue un <b>falso negativo</b>: el "
    "método RS pierde fiabilidad con tasas de ocultación muy altas, cercanas al límite de capacidad "
    "de la imagen.<br/><br/>"
    "<b>Paso 2 &ndash; Estegoanálisis independiente (script Python propio, no VSL):</b> comparación "
    "fila a fila entre el plano de bits menos significativo (LSB) y el inmediatamente superior "
    "(bit 1). En una imagen sin alterar ambos deberían coincidir; en las filas donde el LSB fue "
    "sobrescrito por un mensaje, la coincidencia cae a ~50% (ruido). Se detectó una transición neta "
    "en la fila 292 de 338, estimando <b>~37.011 bytes</b> ocultos.<br/><br/>"
    "<b>Paso 3 &ndash; Intento de BSM-SVM (VSL):</b> falló (<i>&laquo;Could not load SVM model "
    "file&raquo;</i>) porque ese módulo requiere un clasificador SVM pre-entrenado externamente que "
    "VSL no incluye por defecto; se documenta como limitación de la herramienta, no del análisis.<br/><br/>"
    "<b>Paso 4 &ndash; Extracción (VSL, decoder LSB.D):</b> confirmó un mensaje de <b>37.099 bytes</b>, "
    "en línea con la estimación independiente del Paso 2 (diferencia de solo 0,24%).",
    styles["Cuerpo"]))

t4 = tabla_estandar([
    ["Método", "Resultado", "Estimación (bytes)"],
    ["LSB-RS (VSL)", "&laquo;no message&raquo; (falso negativo)", "27.299 (descartado por el propio método)"],
    ["Comparación de planos de bits (Python, propio)", "Transición detectada en fila 292/338", "37.011"],
    ["Decoder LSB.D (VSL)", "Mensaje extraído con éxito", "37.099"],
], colWidths=[6.5*cm, 6.5*cm, 4*cm])
story.append(t4)

story.append(Paragraph("3.2. Resultado de la extracción", styles["H2"]))
story.append(Paragraph(
    "El contenido extraído no era texto plano, sino un archivo <b>ZIP</b> (identificado por su "
    "cabecera estándar <font face='Courier' size='7.6'>50 4B 03 04</font>, &laquo;PK&raquo;), que al "
    "descomprimirse reveló una imagen JPEG. El contenido de esa imagen (ver Anexo I, confidencial) es "
    "un <b>plano de evacuación y extinción de incendios</b> del edificio, con rutas de salida y "
    "ubicación de extintores/mangueras &mdash;información de seguridad física, no datos de pacientes, "
    "pero igualmente sensible para la entidad si cae en manos ajenas.", styles["Cuerpo"]))
story.append(caja("Conclusión apartado b):",
    "Se confirma la sospecha de la Dirección: la imagen contenía información filtrada de forma "
    "encubierta mediante esteganografía LSB, ocupando el 87% de la capacidad de la imagen. "
    "Recomendación: desplegar análisis RS/estadístico de forma rutinaria sobre imágenes salientes, "
    "combinando siempre varios métodos (uno solo, como se ha demostrado, puede dar falsos negativos).",
    bg=ROJO_ALERTA, borde=ROJO_BORDE))

story.append(PageBreak())

# ============================================================ SECCION 4 ===
story.append(Paragraph("4. Apartado c) &mdash; Seguridad del Cifrado AES-256 de las Firmas Sustraídas", styles["H1"]))
story.append(Paragraph(
    "Tras la sustracción de un portátil, se recuperaron 3 imágenes BMP con firmas escaneadas de "
    "médicos (nombre y NIF): <i>Firma2.bmp</i> y <i>Firma3.bmp</i> (descifradas) y "
    "<i>Firma1Cifrada.bmp</i> (cifrada con AES-256, clave de 32 caracteres aleatorios no almacenada "
    "en el equipo). Las tres imágenes comparten resolución 1280&times;800 px, 24 bits.",
    styles["Cuerpo"]))

story.append(Paragraph("4.1. La clave es segura: cálculo de fuerza bruta", styles["H2"]))
story.append(Paragraph(
    "Extrapolando la metodología y velocidades reales medidas en CAI 1 &ndash; Parte 2 (hardware "
    "modesto, ~13,9 MH/s) a un espacio de claves de 256 bits (2<super>256</super> &asymp; "
    "1,158&times;10<super>77</super> combinaciones):", styles["Cuerpo"]))
t5 = tabla_estandar([
    ["Escenario", "Tiempo estimado para romper la clave"],
    ["1 CPU portátil (hardware real medido)", "2,64 &times; 10<super>62</super> años"],
    ["Atacante 1.000 millones de veces más rápido (clúster GPU/ASIC hipotético extremo)", "2,64 &times; 10<super>53</super> años"],
    ["Edad del universo (referencia)", "1,38 &times; 10<super>10</super> años"],
], colWidths=[9*cm, 8*cm])
story.append(t5)
story.append(Spacer(1, 4))
story.append(Paragraph(
    "Incluso en el escenario más extremo planteado, el tiempo necesario sigue siendo "
    "<b>~1,9 &times; 10<super>43</super> veces la edad del universo</b>. La clave de 256 bits, en sí "
    "misma, es completamente segura frente a fuerza bruta.", styles["Cuerpo"]))

story.append(Paragraph("4.2. El verdadero problema: el modo de cifrado utilizado (ECB)", styles["H2"]))
story.append(Paragraph(
    "Se auditó <i>Firma1Cifrada.bmp</i> con un análisis de entropía y de repetición de bloques. "
    "Como control, se generaron datos verdaderamente aleatorios del mismo tamaño "
    "(<font face='Courier' size='7.6'>os.urandom</font>), que dieron una entropía de 7,9999 "
    "bits/byte (el máximo teórico es 8,0), como cabe esperar de un cifrado correcto. "
    "<i>Firma1Cifrada.bmp</i>, en cambio, dio solo <b>5,03 bits/byte</b>.", styles["Cuerpo"]))
story.append(Paragraph(
    "Analizando los 192.004 bloques de 16 bytes del fichero (16 bytes es el tamaño de bloque de "
    "AES), se encontró que <b>solo hay 6.817 bloques distintos</b>: un único patrón de 16 bytes se "
    "repite <b>153.043 veces (79,7% del fichero)</b>, y otro se repite 24.869 veces (12,9% más). "
    "Entre ambos suman el <b>92,6% del fichero completo</b>.", styles["Cuerpo"]))
story.append(caja("¿Por qué es esto tan grave?",
    "En el modo de cifrado <b>ECB (Electronic Codebook)</b>, cada bloque de texto plano se cifra de "
    "forma independiente: bloques de entrada idénticos producen siempre el mismo bloque cifrado. "
    "Las imágenes de firma tienen enormes zonas de fondo blanco (píxeles idénticos repetidos cientos "
    "de miles de veces) &mdash;en modo CBC o GCM, esta repetición sería estadísticamente imposible "
    "de observar con esta frecuencia, porque cada bloque se combina con el cifrado del bloque "
    "anterior (o un contador/nonce único). La frecuencia observada es la firma inequívoca de ECB.",
    bg=ROJO_ALERTA, borde=ROJO_BORDE))
story.append(Paragraph(
    "Para demostrarlo de forma concluyente, se reconstruyó una imagen asignando un tono de gris "
    "distinto a cada bloque cifrado distinto, respetando la geometría original de la imagen "
    "(1280&times;800 px). <b>El resultado revela el nombre, el NIF y la silueta de la firma "
    "manuscrita original, sin haber descifrado ni un solo byte y sin conocer la clave</b> "
    "(imagen completa en el Anexo II, confidencial, por contener datos personales reales).",
    styles["Cuerpo"]))

story.append(Paragraph("4.3. Respuesta a la consulta y recomendaciones", styles["H2"]))
story.append(caja("¿Podemos estar tranquilos?",
    "<font color='#C00000'><b>No.</b></font> Aunque la clave de 256 bits es inquebrantable por "
    "fuerza bruta, el modo de cifrado empleado (ECB) <b>no proporciona confidencialidad real</b> "
    "para contenido con patrones repetitivos como estas imágenes. Un atacante no necesita romper la "
    "clave: le basta con analizar la repetición de bloques para reconstruir información identificativa "
    "y sensible (nombre, NIF, forma de la firma).", bg=ROJO_ALERTA, borde=ROJO_BORDE))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Medidas adicionales recomendadas:</b>", styles["Cuerpo"]))
story.append(Paragraph(
    "1. <b>Cambiar el modo de cifrado</b>: nunca usar ECB; usar CBC con un IV aleatorio único por "
    "fichero, o preferiblemente un modo autenticado como <b>AES-GCM</b> (confidencialidad + "
    "integridad + detección de manipulación).<br/>"
    "2. <b>Cifrado de disco completo</b> (BitLocker/LUKS) como segunda capa, para que ni siquiera el "
    "sistema de ficheros quede expuesto tras el robo.<br/>"
    "3. <b>Gestión de claves en un gestor de secretos o HSM</b>, nunca en el propio equipo ni en "
    "texto plano.<br/>"
    "4. <b>Borrado remoto (MDM)</b> para portátiles con datos sensibles, activable tras notificación "
    "de robo.<br/>"
    "5. <b>Minimización de datos en endpoints</b>: las imágenes de firmas con NIF no deberían residir "
    "permanentemente en portátiles de campo, sino accederse bajo demanda desde un servidor central "
    "con control de acceso y registro de auditoría.", styles["Cuerpo"]))

story.append(PageBreak())

# ============================================================ SECCION 5 ===
story.append(Paragraph("5. Conclusiones Globales", styles["H1"]))
story.append(Paragraph(
    "Esta consultoría demuestra que la seguridad de la información no depende de un único mecanismo, "
    "sino de la combinación correcta de técnicas y su aplicación rigurosa:", styles["Cuerpo"]))
story.append(Paragraph(
    "&bull; <b>LSB es útil pero frágil</b>: adecuado para firmar imágenes en tránsito controlado "
    "dentro del hospital, pero no resiste procesado ni compresión; combinarlo con cifrado previo "
    "mejora la confidencialidad sin coste de tamaño.<br/>"
    "&bull; <b>Ningún método de estegoanálisis aislado es fiable</b>: el caso real analizado (Dibujo.bmp) "
    "habría pasado desapercibido si solo se hubiera confiado en LSB-RS; la combinación de métodos "
    "fue decisiva.<br/>"
    "&bull; <b>Una clave fuerte no implica un sistema seguro</b>: AES-256 con modo ECB es, en la "
    "práctica, tan débil frente a este tipo de contenido como un cifrado mucho más corto bien "
    "implementado. El <b>modo de operación</b> es tan importante como el tamaño de la clave.",
    styles["Cuerpo"]))

story.append(Paragraph("Bibliografía", styles["H2"]))
story.append(Paragraph(
    "&bull; Virtual Steganographic Laboratory (VSL) 1.1 &ndash; https://vsl.sourceforge.net/<br/>"
    "&bull; Fridrich, J., Goljan, M., Du, R. &ndash; <i>Reliable Detection of LSB Steganography in "
    "Color and Grayscale Images</i> (método RS).<br/>"
    "&bull; Westfeld, A., Pfitzmann, A. &ndash; <i>Attacks on Steganographic Systems</i> (Chi-cuadrado "
    "de Pares de Valores).<br/>"
    "&bull; NIST SP 800-38A &ndash; <i>Recommendation for Block Cipher Modes of Operation</i> "
    "(debilidades de ECB).<br/>"
    "&bull; Documentación oficial de OpenSSL 3.5 (<font face='Courier' size='7.6'>enc</font>).<br/>"
    "&bull; Informe previo del equipo: <i>CAI 2 &ndash; Parte 1, Informe Técnico de Cifrado y "
    "Auditoría Forense</i>, Security Team 2.", styles["CuerpoPeq"]))

story.append(Paragraph("Relación de Anexos Entregados", styles["H2"]))
story.append(Paragraph(
    "&bull; <b>Anexo I</b> (confidencial): plano de evacuación recuperado (apartado b) y hashes "
    "SHA-256.<br/>"
    "&bull; <b>Anexo II</b> (confidencial): imagen revelada por análisis de bloques ECB (apartado c), "
    "con nombre y NIF reales, y hashes SHA-256.<br/>"
    "&bull; Scripts Python: <font face='Courier' size='7.6'>estegoanalisis.py, localizar_mensaje2.py, "
    "confidencialidad.py, bitplane_propio.py, entropia.py, control_entropia.py, revelar_ecb.py</font>.<br/>"
    "&bull; Imágenes de prueba generadas y resultados intermedios (carpeta "
    "<font face='Courier' size='7.6'>trabajo/</font>).", styles["CuerpoPeq"]))

story.append(PageBreak())

# ======================================================= ANEXOS (confid) ==
def portada_anexo(titulo):
    t = Table([[Paragraph(titulo, styles["AnexoTitulo"])]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ROJO_BORDE),
        ('LEFTPADDING', (0,0), (-1,-1), 10), ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

story.append(portada_anexo("ANEXO I (CONFIDENCIAL) &mdash; Mensaje Oculto Recuperado, Apartado b)"))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Contenido extraído de <i>Dibujo.bmp</i> mediante el decoder LSB.D de VSL. Se trata de un plano "
    "de evacuación y extinción de incendios del edificio hospitalario.", styles["Cuerpo"]))
img1 = imagen_centrada(os.path.join(TRABAJO, "evidencias_apdo_b", "plano_evacuacion_recuperado.jpg"), 14, 10)
story.append(img1)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>SHA-256 Dibujo.bmp (portadora original):</b><br/>"
    "<font face='Courier' size='7.6'>1f06794a00b6a1b051abf0c3e5f462a3bced3459f6cb1a09a99e50c24d39831d</font><br/>"
    "<b>SHA-256 payload ZIP extraído (LSB):</b><br/>"
    "<font face='Courier' size='7.6'>8c1b0ddcfe99fa8b628d7c85e5b1055ad515c55f953db894f1526932c7e2bc11</font><br/>"
    "<b>SHA-256 imagen recuperada (a5fde.jpg):</b><br/>"
    "<font face='Courier' size='7.6'>acac67966db480e723f5642805a68dafb5f8fa661c43c52b8bb40bea6e83b9c3</font>",
    styles["CuerpoPeq"]))

story.append(PageBreak())
story.append(portada_anexo("ANEXO II (CONFIDENCIAL) &mdash; Revelado por Análisis de Bloques ECB, Apartado c)"))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Reconstrucción visual de <i>Firma1Cifrada.bmp</i> a partir, exclusivamente, de la repetición de "
    "bloques cifrados de 16 bytes (sin descifrar ningún dato, sin conocer la clave AES). Se asigna un "
    "tono de gris distinto a cada bloque cifrado distinto, respetando la geometría 1280&times;800 "
    "de la imagen original.", styles["Cuerpo"]))
img2 = imagen_centrada(os.path.join(TRABAJO, "apdo_c", "revelado_ECB_proporcion_correcta.png"), 15, 10)
story.append(img2)
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Identidad revelada:</b> Sara Barba Solís &mdash; NIF 34782082-H.<br/><br/>"
    "<b>SHA-256 Firma1Cifrada.bmp:</b><br/>"
    "<font face='Courier' size='7.6'>0e4d7664b1ba7ff0d91b8af73142c204815c64ecb40a9b97edd216e6a5663ecd</font><br/>"
    "<b>Bloques de 16 bytes totales / distintos:</b> 192.004 / 6.817<br/>"
    "<b>Bloque más repetido:</b> 153.043 ocurrencias (79,7% del fichero)<br/>"
    "<b>Entropía Shannon del fichero:</b> 5,03 bits/byte (control aleatorio de referencia: 7,9999 bits/byte)",
    styles["CuerpoPeq"]))

# ---------------------------------------------------------------- Footer --
def pie_pagina(canvas_obj, doc_obj):
    canvas_obj.saveState()
    canvas_obj.setFont('Helvetica', 7.5)
    canvas_obj.setFillColor(colors.grey)
    canvas_obj.drawCentredString(A4[0]/2, 1.0*cm,
        f"ST-2-CAI2B · Informe emitido por SecurTech Advisory para el Hospital · Página {doc_obj.page}")
    canvas_obj.restoreState()

doc.build(story, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("PDF generado en:", OUT)
