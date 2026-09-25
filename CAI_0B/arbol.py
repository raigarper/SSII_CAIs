import hashlib

def md5_hash(data: str) -> str:
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def merkle_levels(letters: list[str]) -> list[list[str]]:
    if len(letters) != 8:
        raise ValueError("Se requieren exactamente 8 letras.")

    levels = [[md5_hash(char) for char in letters]]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        levels.append([
            md5_hash(cur[i] + cur[i + 1])
            for i in range(0, len(cur), 2)
        ])
    return levels

def print_tree(letters: list[str], title: str) -> list[list[str]]:
    print("=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)
    print(f"Entrada (Hojas 1-8): {'  '.join(letters)}\n")
    
    levels = merkle_levels(letters)
    labels = ["Hojas (Nivel 0)", "Nivel 1 (Pares)", "Nivel 2 (Subramas)", "Raíz (Nivel 3)"]
    
    for lvl_idx, lvl_hashes in enumerate(levels):
        print(f"[*] {labels[lvl_idx]}:")
        for i, h in enumerate(lvl_hashes):
            print(f"    - Nodo [{lvl_idx}][{i}]: {h}")
        print()
        
    print(f"[>>>] RAIZ DE MERKLE: {levels[-1][0]}\n")
    return levels

def main():
    # 1. Definición y cálculo del árbol original
    letras_orig = ['A', 'I', 'L', 'N', 'O', 'R', 'S', 'T']
    arbol_orig = print_tree(letras_orig, "Arbol de Merkle Original")

    # 2. Modificación exclusiva de la 7ª letra ('S' -> 'U')
    letras_mod = ['A', 'I', 'L', 'N', 'O', 'R', 'U', 'T']
    arbol_mod = print_tree(letras_mod, "Arbol de Merkle Modificado (Hoja 7: 'S' -> 'U')")

    # 3. Análisis de propagación (efecto avalancha en la rama de Merkle)
    print("=" * 80)
    print(" RESUMEN DE MODIFICACIONES: RUTA AFECTADA HACIA LA RAIZ")
    print("=" * 80)
    
    nombres_nodos = {
        (0, 6): "H7         (Hoja 7)",
        (1, 3): "H78        (Nivel 1)",
        (2, 1): "H5678      (Nivel 2)",
        (3, 0): "H12345678  (Raíz Merkle)"
    }
    
    print(f"{'Nodo':<22} | {'Hash Original':<32} | {'Hash Recalculado':<32}")
    print("-" * 92)
    
    total_recalculados = 0
    for lvl in range(len(arbol_orig)):
        for idx in range(len(arbol_orig[lvl])):
            h_old = arbol_orig[lvl][idx]
            h_new = arbol_mod[lvl][idx]
            if h_old != h_new:
                total_recalculados += 1
                nombre = nombres_nodos.get((lvl, idx), f"Nodo [{lvl}][{idx}]")
                print(f"{nombre:<22} | {h_old} | {h_new}")

    print("-" * 92)
    print(f"\n[+] Total de hashes que ha sido necesario recalcular: {total_recalculados} de 15 nodos.")
    print("[+] Observación: El 73.3% del árbol permanece intacto (propiedad de verificación eficiente).\n")

if __name__ == "__main__":
    main()