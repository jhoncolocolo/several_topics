import os
import argparse

# Lista de extensiones por defecto si el usuario no especifica ninguna (amplia cobertura de código y texto)
DEFAULT_EXTENSIONES = [
    '.py', '.txt', '.json', '.html', '.css', '.js', '.ts', '.jsx', '.tsx', 
    '.sh', '.yaml', '.yml', '.md', '.java', '.c', '.cpp', '.h', '.cs', 
    '.go', '.php', '.xml', '.sql', '.tf', '.ini', '.cfg', '.log', '.rs'
]

def listar_archivos_por_extension(directorio_raiz, extensiones, exclusiones):
    """
    Recorre un directorio y lista archivos, usando una lista de extensiones 
    muy amplia por defecto si no se especifican extensiones.
    
    Args:
        directorio_raiz (str): La ruta del directorio a recorrer.
        extensiones (list): Lista de extensiones de archivos a incluir (Ej: ['tf', 'hcl']).
        exclusiones (list): Lista de nombres de archivos o directorios a ignorar.
    """
    
    archivos_encontrados = []
    
    # Si no se dan extensiones, usamos la lista de extensiones por defecto
    if not extensiones:
        extensiones_a_incluir = DEFAULT_EXTENSIONES
        print("⚠️ Modo por defecto: No se especificaron extensiones. Se buscarán archivos de código/texto comunes.")
    else:
        # Asegurar que las extensiones pasadas por el usuario comienzan con un punto
        extensiones_a_incluir = [('.' + ext).replace('..', '.') for ext in extensiones]
    
    # Exclusiones de directorios/archivos base (fijas, recomendadas) + las del usuario
    exclusiones_base = {'.git', 'node_modules', 'venv', '__pycache__', '.vscode', '.idea'}
    exclusiones_finales = exclusiones_base.union(set(exclusiones))
    
    print(f"Buscando archivos con {len(extensiones_a_incluir)} extensiones en: {directorio_raiz}")
    print(f"Elementos base excluidos: {', '.join(exclusiones_base)}")
    if exclusiones:
        print(f"Elementos adicionales excluidos por el usuario: {', '.join(exclusiones)}\n")
    else:
        print("\nNo hay exclusiones adicionales del usuario.")
    
    # --- Recorrido del Directorio ---
    
    for directorio_actual, subdirectorios, archivos in os.walk(directorio_raiz, topdown=True):
        
        # Excluir subdirectorios (modificando subdirectorios 'in place')
        subdirectorios[:] = [d for d in subdirectorios if d not in exclusiones_finales]
        
        for nombre_archivo in archivos:
            
            # Excluir archivos específicos
            if nombre_archivo in exclusiones_finales:
                continue

            # Comprobar si la extensión del archivo está en nuestra lista de inclusión
            if os.path.splitext(nombre_archivo)[1] in extensiones_a_incluir:
                
                # Construir la ruta relativa
                ruta_completa = os.path.join(directorio_actual, nombre_archivo)
                ruta_relativa = os.path.relpath(ruta_completa, directorio_raiz)
                
                archivos_encontrados.append(ruta_relativa)
                
    # --- Presentación de Resultados ---
    if archivos_encontrados:
        print(f"\n✅ Archivos Encontrados ({len(archivos_encontrados)}):\n")
        for ruta in archivos_encontrados:
            print(ruta)
        
        # Opcional: Escribir la lista en un archivo de texto
        # El nombre del archivo ahora reflejará si se usó un filtro o el modo por defecto
        filtro_nombre = '_'.join(extensiones).replace('.', '') if extensiones else 'default_code'
        nombre_lista_output = f"lista_de_{filtro_nombre}.txt"
        ruta_output = os.path.join(directorio_raiz, nombre_lista_output)
        with open(ruta_output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(archivos_encontrados))
        
        print(f"\n¡Lista guardada en: {ruta_output}")
    else:
        print("❌ No se encontraron archivos con los filtros especificados.")


def main():
    parser = argparse.ArgumentParser(
        description="""
        Lista archivos en un directorio. Por defecto, incluye archivos de código comunes 
        y no requiere filtros de extensión ni exclusiones.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Argumento del Directorio (obligatorio)
    parser.add_argument(
        '-d', '--directorio', 
        type=str, 
        required=True, 
        help="El directorio raíz del proyecto a recorrer (Ej: example)."
    )
    
    # Argumento de Extensiones (AHORA ES OPCIONAL)
    parser.add_argument(
        '-x', '--extensiones',
        nargs='+',
        default=[], # El valor por defecto es una lista vacía, lo que activa el modo por defecto
        help="Lista de **extensiones** de archivos a incluir (Ej: tf hcl). Si se omite, se usa una lista amplia por defecto."
    )

    # Argumento de Exclusiones (OPCIONAL)
    parser.add_argument(
        '-e', '--exclude',
        nargs='*',
        default=[], # El valor por defecto es una lista vacía, lo que significa que solo se aplican las exclusiones base
        help="Lista de nombres de directorios/archivos a excluir (Ej: -e logs secret.tf)."
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directorio):
        print(f"Error: El directorio '{args.directorio}' no existe o la ruta es incorrecta.")
        return

    listar_archivos_por_extension(args.directorio, args.extensiones, args.exclude)


if __name__ == "__main__":
    main()

"""
# 🚀 Listador de Archivos Flexible por Extensión (`listar_archivos_default.py`)

Esta herramienta de Python lista todos los archivos dentro de un directorio que coinciden con ciertos criterios, con un **foco en la simplicidad**.

Si solo se proporciona el directorio, el script opera en **modo por defecto**, incluyendo la mayoría de los archivos de código y texto comunes sin necesidad de filtros explícitos.

## ⚙️ Uso

Ejecuta el script desde la línea de comandos en el mismo directorio donde se encuentra `listar_archivos_default.py`.

### Argumentos Principales

| Opción Larga | Opción Corta | Estado | Descripción |
| :--- | :--- | :--- | :--- |
| `--directorio` | `-d` | **OBLIGATORIO** | **Ruta del directorio** raíz a recorrer (Ej: `mi_proyecto`). |
| `--extensiones` | `-x` | OPCIONAL | **Filtro de extensiones** a incluir (Ej: `-x py tf`). Si se omite, se usa una lista amplia por defecto. |
| `--exclude` | `-e` | OPCIONAL | **Lista de nombres** de directorios/archivos a excluir (Ej: `-e backups secret.tf`). |

---

### 1. 🥇 Modo Por Defecto (Ejecución Mínima)

Es el modo de operación más sencillo. Solo requiere el directorio. El script automáticamente:
* Incluye la mayoría de las extensiones de archivos de código y texto comunes.
* Excluye directorios comunes de sistemas y dependencias (`.git`, `node_modules`, `venv`, etc.).

**Comando:**

```bash
python listar_archivos_default.py -d pongamonos_serios_mejorado
"""