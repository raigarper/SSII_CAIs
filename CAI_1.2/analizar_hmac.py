import sys
import math

def calcular_tiempos_y_seguridad(velocidad_hashes_segundo: float):
    # Clave de 32 bits
    espacio_32 = 2**32
    espacio_medio = 2**31
    
    t_medio_seg = espacio_medio / velocidad_hashes_segundo
    t_peor_seg = espacio_32 / velocidad_hashes_segundo
    
    # Atacante x1000
    vel_atacante = velocidad_hashes_segundo * 1000
    t_atacante_medio_seg = espacio_medio / vel_atacante
    
    # Clave segura para resistir 10 años frente al atacante x1000
    segundos_10_anos = 10 * 365.25 * 86400
    combinaciones_necesarias = vel_atacante * segundos_10_anos
    bits_minimos = math.ceil(math.log2(combinaciones_necesarias))
    
    print("\n" + "=" * 60)
    print(" RESULTADOS MATEMÁTICOS PARA EL INFORME")
    print("=" * 60)
    print(f"Velocidad medida en Kali: {velocidad_hashes_segundo:,.0f} H/s")
    print(f"Tiempo medio (clave 32 bits): {t_medio_seg:.4f} s ({t_medio_seg/60:.2f} min)")
    print(f"Tiempo peor (clave 32 bits) : {t_peor_seg:.4f} s ({t_peor_seg/60:.2f} min)")
    print("-" * 60)
    print(f"Velocidad Atacante (x1000)  : {vel_atacante:,.0f} H/s")
    print(f"Tiempo medio Atacante (32b) : {t_atacante_medio_seg:.6f} s")
    print("-" * 60)
    print(f"Bits mínimos teóricos para 10 años: {bits_minimos} bits")
    print(f"Recomendación estándar del NIST/RFC: 128 o 256 bits")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        v = float(sys.argv[1])
        calcular_tiempos_y_seguridad(v)
    else:
        print("Uso: python analizar_hmac.py <velocidad_hashes_por_segundo>")
        print("Ejemplo: python analizar_hmac.py 5000000")