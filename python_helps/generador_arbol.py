import os
import argparse

# Caracteres de estilo para dibujar el árbol
PREFIX_DIR = "│   "
PREFIX_FILE_LAST = "└── "
PREFIX_FILE = "├── "

def generar_arbol(directorio_raiz, exclusiones, extensiones_a_incluir, output_file=None):
    """
    Genera un árbol de directorios recursivamente, aplicando filtros de inclusión y exclusión.
    
    Args:
        directorio_raiz (str): La ruta del directorio a recorrer.
        exclusiones (list): Lista de nombres de archivos o directorios a ignorar.
        extensiones_a_incluir (list): Lista de extensiones de archivos a incluir (Ej: ['.py', '.tf']).
        output_file (str, optional): Nombre del archivo de salida donde guardar el árbol.
    """
    
    # 1. Preparación de Filtros
    exclusiones_base = {'.git', '__pycache__', 'node_modules', 'venv', '.vscode', '.idea'}
    exclusiones_finales = exclusiones_base.union(set(exclusiones))
    
    # Asegurar que las extensiones pasadas por el usuario comienzan con un punto
    filtro_extensiones = [('.' + ext).replace('..', '.') for ext in extensiones_a_incluir]
    
    # Modo de filtrado
    modo_filtrado = bool(filtro_extensiones)
    
    # Mostrar información del modo
    print(f"Generando árbol para: {directorio_raiz}")
    if modo_filtrado:
        print(f"Modo: Filtrado (Solo extensiones: {', '.join(filtro_extensiones)})")
    else:
        print("Modo: Completo (No se aplicó filtro de extensión)")
    print(f"Exclusiones aplicadas: {', '.join(exclusiones_finales)}\n")

    # Abrir archivo de salida si se especifica
    with open(output_file, 'w', encoding='utf-8') if output_file else None as f_out:
        
        def imprimir(linea):
            """Función auxiliar para imprimir en consola y en archivo si está abierto."""
            print(linea)
            if f_out:
                f_out.write(linea + '\n')

        imprimir(f"{os.path.basename(directorio_raiz)}/")
        
        # Función recursiva para recorrer directorios
        def recorrer(ruta_actual, prefijo=""):
            try:
                contenidos = sorted(os.listdir(ruta_actual))
            except Exception:
                return

            # Aplicar exclusiones (si el nombre es el archivo de salida o está en la lista)
            contenidos = [c for c in contenidos if c not in exclusiones_finales and c != os.path.basename(output_file or "")]
            
            elementos_visibles = []
            
            # Pre-filtrar archivos si estamos en modo de filtrado
            for nombre in contenidos:
                ruta_completa = os.path.join(ruta_actual, nombre)
                
                if os.path.isdir(ruta_completa):
                    # Si es directorio, siempre lo incluimos para poder entrar y ver si hay archivos que cumplen el filtro dentro
                    elementos_visibles.append(nombre)
                elif not modo_filtrado or os.path.splitext(nombre)[1] in filtro_extensiones:
                    # Si es archivo, lo incluimos si no hay filtro O si cumple el filtro
                    elementos_visibles.append(nombre)

            num_contenidos = len(elementos_visibles)
            
            for i, nombre in enumerate(elementos_visibles):
                ruta_completa = os.path.join(ruta_actual, nombre)
                
                es_ultimo = (i == num_contenidos - 1)

                if os.path.isdir(ruta_completa):
                    # --- Es un Directorio ---
                    dir_prefijo = PREFIX_FILE_LAST if es_ultimo else PREFIX_FILE
                    imprimir(f"{prefijo}{dir_prefijo}{nombre}/")
                    
                    # Llamada recursiva
                    nuevo_prefijo = prefijo + ("   " if es_ultimo else PREFIX_DIR)
                    recorrer(ruta_completa, nuevo_prefijo)
                
                else:
                    # --- Es un Archivo ---
                    archivo_prefijo = PREFIX_FILE_LAST if es_ultimo else PREFIX_FILE
                    imprimir(f"{prefijo}{archivo_prefijo}{nombre}")

        recorrer(directorio_raiz)

# --- Configuración y Ejecución ---

def main():
    parser = argparse.ArgumentParser(
        description="""
        🌳 Generador de Árbol de Directorios. Muestra la estructura de archivos 
        y carpetas con indentación, permitiendo filtros de inclusión y exclusión.
        """,
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-d', '--directorio', 
        type=str, 
        required=True, 
        help="El directorio raíz del proyecto a recorrer (Ej: my_project)."
    )

    parser.add_argument(
        '-e', '--exclude',
        nargs='*',
        default=[],
        help="Lista de nombres de directorios/archivos a excluir (Ej: -e logs .DS_Store)."
    )
    
    # Argumento de Filtro de Extensión (NUEVO y OPCIONAL)
    parser.add_argument(
        '-x', '--extensiones',
        nargs='*',
        default=[],
        help="Lista de **extensiones** de archivos a incluir (Ej: -x py tf). Si se omite, se muestran TODOS los archivos."
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help="Opcional. Nombre del archivo de salida para guardar el árbol generado (Ej: arbol.txt)."
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directorio):
        print(f"Error: El directorio '{args.directorio}' no existe o la ruta es incorrecta.")
        return

    generar_arbol(args.directorio, args.exclude, args.extensiones, args.output)

if __name__ == "__main__":
    main()

"""
# 🌳 Generador de Árbol de Directorios Avanzado (`generador_arbol_filtrado.py`)

Esta herramienta de Python crea una representación visual de la estructura de directorios (formato `tree` en ASCII), con la flexibilidad de **filtrar archivos por extensión** o **excluir elementos** específicos.

## ⚙️ Uso

Ejecuta el script desde la línea de comandos en el mismo directorio donde se encuentra `generador_arbol_filtrado.py`.

### Argumentos Principales

| Opción Larga | Opción Corta | Estado | Descripción |
| :--- | :--- | :--- | :--- |
| `--directorio` | `-d` | **OBLIGATORIO** | **Ruta del directorio** raíz a recorrer (Ej: `mi_proyecto`). |
| `--output` | `-o` | OPCIONAL | **Nombre del archivo** para guardar la salida (Ej: `arbol.txt`). Si se omite, se imprime en consola. |
| `--exclude` | `-e` | OPCIONAL | Lista de nombres de directorios/archivos a **excluir** (Ej: `-e logs .DS_Store`). |
| `--extensiones` | `-x` | OPCIONAL | **Filtro de extensiones** de archivos a incluir (Ej: `-x py tf`). Si se omite, se muestran **TODOS** los archivos. |

---

### 1. 🥇 Modo Por Defecto (Árbol Completo)

Este modo muestra **todos** los archivos y directorios (excepto las exclusiones base como `.git`, `venv`, etc.). No requiere filtros ni exclusiones.

```bash
python generador_arbol_filtrado.py -d pongamonos_serios_mejorado
"""
## python generador_arbol.py -d pongamonos_serios_mejorado -o arbol_limpio.txt -e .terraform .env .terraform.lock.hcl terraform.tfstate lambda.zip .pytest_cache terraform.tfstate.backup
