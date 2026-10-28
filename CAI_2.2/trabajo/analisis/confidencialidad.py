import numpy as np
from PIL import Image
from scipy import stats

def psnr(original, modificada):
    o = np.array(original, dtype=np.float64)
    m = np.array(modificada, dtype=np.float64)
    mse = np.mean((o - m) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * np.log10(255.0 / np.sqrt(mse))

def chi_cuadrado_pares(canal):
    hist = np.bincount(canal.flatten(), minlength=256).astype(float)
    chi2 = 0.0
    for k in range(128):
        n2k, n2k1 = hist[2*k], hist[2*k+1]
        esperado = (n2k + n2k1) / 2.0
        if esperado > 0:
            chi2 += ((n2k - esperado)**2) / esperado
    pval = 1 - stats.chi2.cdf(chi2, df=127)
    return chi2, pval

base = r"C:\Users\ADMiN\US\SSII\CAIs\CAI_2.2\trabajo"
original = Image.open(f"{base}\carrier_limpio.bmp").convert("RGB")

print(f"{'Version':<15} {'PSNR (dB)':<12} {'Chi2 R':<10} {'p-val R':<10} {'Chi2 G':<10} {'p-val G':<10} {'Chi2 B':<10} {'p-val B':<10}")
for nombre, fichero in [("Original", "carrier_limpio.bmp"),
                         ("Firma corta", "carrier_lsb_corta.bmp"),
                         ("Firma larga", "carrier_lsb_larga.bmp")]:
    img = Image.open(f"{base}\{fichero}").convert("RGB")
    p = psnr(original, img)
    arr = np.array(img)
    resultados = []
    for i in range(3):
        chi2, pval = chi_cuadrado_pares(arr[:,:,i])
        resultados.append((chi2, pval))
    print(f"{nombre:<15} {p:<12.2f} "
          f"{resultados[0][0]:<10.1f} {resultados[0][1]:<10.4f} "
          f"{resultados[1][0]:<10.1f} {resultados[1][1]:<10.4f} "
          f"{resultados[2][0]:<10.1f} {resultados[2][1]:<10.4f}")
