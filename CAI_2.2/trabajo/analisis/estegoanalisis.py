"""
Estegoanalisis independiente de VSL para Dibujo.bmp.
Tres pruebas distintas, ninguna depende del formato interno de VSL:
 1. Chi-cuadrado de Pares de Valores (Westfeld-Pfitzmann) -> deteccion estadistica.
 2. Bit-plane slicing del LSB -> inspeccion visual de estructura/aleatoriedad.
 3. Busqueda libre de texto ASCII/UTF-8 imprimible en el flujo de bits LSB,
    probando varios ordenes de lectura (por si el mensaje no empieza en el pixel 0,0).
"""
import numpy as np
from PIL import Image
import sys

PATH = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\Dibujo.bmp"
OUTDIR = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\trabajo\analisis"

img = Image.open(PATH).convert("RGB")
arr = np.array(img)
h, w, _ = arr.shape
print(f"Imagen: {w}x{h}, {arr.size} bytes de pixel data")

# ---------------------------------------------------------------
# PRUEBA 1: Chi-cuadrado de Pares de Valores (Chi-square attack)
# ---------------------------------------------------------------
# Idea: en una imagen limpia, los valores "pareja" (2k, 2k+1) de cada
# canal NO tienen por que tener frecuencias parecidas. Pero cuando se
# aplica LSB simple sobre TODA la imagen, el bit menos significativo se
# vuelve ~aleatorio, y entonces las frecuencias de 2k y 2k+1 se igualan
# (test de Westfeld-Pfitzmann). Si el chi-cuadrado da muy bajo (mensaje
# ocupando gran parte de la imagen), es sospechoso de LSB masivo.
def chi_cuadrado_pares(canal):
    hist = np.bincount(canal.flatten(), minlength=256).astype(float)
    chi2 = 0.0
    for k in range(128):
        n2k, n2k1 = hist[2*k], hist[2*k+1]
        esperado = (n2k + n2k1) / 2.0
        if esperado > 0:
            chi2 += ((n2k - esperado)**2) / esperado
    # p-valor aproximado con 127 grados de libertad (chi2 muy bajo -> sospechoso)
    from scipy import stats
    pval = 1 - stats.chi2.cdf(chi2, df=127)
    return chi2, pval

try:
    from scipy import stats
    tiene_scipy = True
except ImportError:
    tiene_scipy = False

print("\n=== PRUEBA 1: Chi-cuadrado de Pares de Valores ===")
for i, nombre in enumerate(["R", "G", "B"]):
    canal = arr[:, :, i]
    if tiene_scipy:
        chi2, pval = chi_cuadrado_pares(canal)
        print(f"Canal {nombre}: chi2={chi2:.2f}  p-valor={pval:.4f}  "
              f"({'SOSPECHOSO (posible LSB masivo)' if pval > 0.9 else 'sin indicios claros'})")
    else:
        print("scipy no disponible, omitiendo p-valor (se instalaria bajo confirmacion)")

# ---------------------------------------------------------------
# PRUEBA 2: Bit-plane slicing del LSB (inspeccion visual)
# ---------------------------------------------------------------
print("\n=== PRUEBA 2: Bit-plane slicing (LSB) ===")
lsb_plane = (arr & 1) * 255  # bit 0 de cada canal, amplificado a 0/255 para verlo
Image.fromarray(lsb_plane.astype(np.uint8)).save(f"{OUTDIR}/dibujo_lsb_plane.png")
# Tambien el plano del bit mas significativo, como referencia de "lo normal"
msb_plane = ((arr >> 7) & 1) * 255
Image.fromarray(msb_plane.astype(np.uint8)).save(f"{OUTDIR}/dibujo_msb_plane.png")
print(f"Guardado: {OUTDIR}/dibujo_lsb_plane.png  (si hay texto/figuras visibles, hay mensaje)")
print(f"Guardado: {OUTDIR}/dibujo_msb_plane.png  (referencia: deberia verse la silueta real)")

# ---------------------------------------------------------------
# PRUEBA 3: Busqueda libre de texto imprimible en el flujo LSB
# ---------------------------------------------------------------
print("\n=== PRUEBA 3: Busqueda de texto ASCII/UTF-8 en los bits LSB ===")

def extraer_bits(array_canal_orden):
    bits = (array_canal_orden & 1).flatten()
    return bits

def bits_a_bytes(bits):
    n = len(bits) - (len(bits) % 8)
    bits = bits[:n].reshape(-1, 8)
    pesos = np.array([128,64,32,16,8,4,2,1])
    return (bits * pesos).sum(axis=1).astype(np.uint8)

def buscar_ascii_imprimible(data_bytes, longitud_min=8):
    texto_actual = []
    encontrados = []
    for b in data_bytes:
        if 32 <= b <= 126:
            texto_actual.append(chr(b))
        else:
            if len(texto_actual) >= longitud_min:
                encontrados.append("".join(texto_actual))
            texto_actual = []
    if len(texto_actual) >= longitud_min:
        encontrados.append("".join(texto_actual))
    return encontrados

ordenes = {
    "RGB intercalado (orden natural fila a fila)": arr,
    "Solo canal R": arr[:, :, 0],
    "Solo canal G": arr[:, :, 1],
    "Solo canal B": arr[:, :, 2],
}

algo_encontrado = False
for nombre, datos in ordenes.items():
    bits = extraer_bits(datos)
    bytes_ = bits_a_bytes(bits)
    cadenas = buscar_ascii_imprimible(bytes_, longitud_min=8)
    if cadenas:
        algo_encontrado = True
        print(f"[{nombre}] -> {len(cadenas)} cadena(s) ASCII >=8 caracteres encontradas:")
        for c in cadenas[:5]:
            print(f"    '{c}'")
    else:
        print(f"[{nombre}] -> ninguna cadena ASCII imprimible de 8+ caracteres seguidos")

print("\n=== CONCLUSION PRELIMINAR ===")
if not algo_encontrado:
    print("No se ha encontrado texto legible directo en los bits LSB con ningun orden probado.")
else:
    print("Se han encontrado posibles fragmentos de texto -> revisar manualmente.")
