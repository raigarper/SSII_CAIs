import itertools

def generar_variantes_casing(palabra: str):
    """Devuelve variantes de mayúsculas/minúsculas de la palabra."""
    return [palabra.lower(), palabra.capitalize(), palabra.upper()]

def main():
    elementos = ["arturo", "ruiz", "gasca"]
    candidatos = set()

    # 1. Permutaciones de 3 palabras (ej. Arturo*Ruiz*Gasca, Arturo*RuizGasca, ArturoRuiz*Gasca...)
    for p in itertools.permutations(elementos, 3):
        for w0 in generar_variantes_casing(p[0]):
            for w1 in generar_variantes_casing(p[1]):
                for w2 in generar_variantes_casing(p[2]):
                    # Con asterisco como separador completo
                    candidatos.add(f"{w0}*{w1}*{w2}")
                    # Con asterisco solo en una de las uniones
                    candidatos.add(f"{w0}*{w1}{w2}")
                    candidatos.add(f"{w0}{w1}*{w2}")
                    # Con asterisco al principio o al final
                    candidatos.add(f"*{w0}{w1}{w2}")
                    candidatos.add(f"{w0}{w1}{w2}*")
                    candidatos.add(f"*{w0}*{w1}*{w2}*")

    # 2. Permutaciones de 2 palabras (ej. Arturo*Ruiz, Arturo*Gasca, Ruiz*Gasca...)
    for p in itertools.permutations(elementos, 2):
        for w0 in generar_variantes_casing(p[0]):
            for w1 in generar_variantes_casing(p[1]):
                candidatos.add(f"{w0}*{w1}")
                candidatos.add(f"*{w0}*{w1}")
                candidatos.add(f"{w0}*{w1}*")
                candidatos.add(f"{w0}{w1}*")
                candidatos.add(f"*{w0}{w1}")

    # 3. Palabras sueltas con asterisco
    for el in elementos:
        for w in generar_variantes_casing(el):
            candidatos.add(f"{w}*")
            candidatos.add(f"*{w}")
            candidatos.add(f"*{w}*")

    # Guardar en archivo
    output_path = "diccionario_arturo.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        for c in sorted(candidatos):
            f.write(c + "\n")

    print(f"[+] Diccionario generado con éxito: {output_path}")
    print(f"[+] Total de combinaciones generadas: {len(candidatos)}")

if __name__ == "__main__":
    main()
