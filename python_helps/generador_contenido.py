import os
import pathlib
import argparse

def concatenar_archivos(directorio_raiz, nombre_archivo_salida, exclusiones):
    """
    Recorre un directorio, concatena el contenido de los archivos de código 
    en un único archivo, añadiendo un encabezado con el nombre del archivo.

    Args:
        directorio_raiz (str): La ruta del directorio a recorrer.
        nombre_archivo_salida (str): El nombre del archivo de salida.
        exclusiones (list): Lista de nombres de archivos o directorios a ignorar.
    """
    
    # 1. Preparación de Rutas y Exclusiones
    ruta_salida = pathlib.Path(directorio_raiz) / nombre_archivo_salida
    
    # Lista de extensiones de archivos de código a incluir
    extensiones_a_incluir = ['.py', '.txt', '.json', '.html', '.css', '.js', '.ts', '.jsx', '.tsx', '.sh', '.yaml', '.yml', '.md', '.java', '.c', '.cpp', '.h', '.cs','.env','.ini','.lua'] 
    
    # Añadir exclusiones comunes por defecto
    exclusiones_base = {'__pycache__', '.git', 'node_modules', 'venv', '.vscode', 'dist', 'build'}
    # Combinar con las exclusiones proporcionadas por el usuario (si las hay)
    exclusiones_finales = exclusiones_base.union(set(exclusiones))

    print(f"Iniciando recorrido en: {directorio_raiz}")
    print(f"Archivo de salida: {ruta_salida}")
    print(f"Directorios/Archivos excluidos: {', '.join(exclusiones_finales)}")
    
    # 2. Recorrido y Concatenación
    with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
        
        # Usamos os.walk para recorrer el directorio y sus subdirectorios
        for directorio_actual, subdirectorios, archivos in os.walk(directorio_raiz, topdown=True):
            
            # --- MANEJO DE EXCLUSIONES DE DIRECTORIOS ---
            # Modificar subdirectorios 'in place' para que os.walk los ignore
            # Esto evita que os.walk entre en carpetas grandes o irrelevantes.
            subdirectorios[:] = [d for d in subdirectorios if d not in exclusiones_finales]
            
            ruta_directorio_actual = pathlib.Path(directorio_actual)

            for nombre_archivo in archivos:
                # --- MANEJO DE EXCLUSIONES DE ARCHIVOS ---
                if nombre_archivo in exclusiones_finales:
                    continue # Saltar este archivo

                ruta_completa_archivo = ruta_directorio_actual / nombre_archivo
                
                # Comprobar extensión y que no sea el propio archivo de salida
                if ruta_completa_archivo.suffix in extensiones_a_incluir and nombre_archivo != nombre_archivo_salida:
                    
                    try:
                        # Generar la ruta relativa para el encabezado
                        ruta_relativa = ruta_completa_archivo.relative_to(directorio_raiz)

                        # --- 1. Escribir el encabezado ---
                        encabezado = f"\n\n\n# =========================================================\n"
                        encabezado += f"# Archivo: {ruta_relativa}\n"
                        encabezado += f"# =========================================================\n"
                        archivo_salida.write(encabezado)

                        # --- 2. Escribir el contenido del archivo ---
                        with open(ruta_completa_archivo, 'r', encoding='utf-8') as archivo_entrada:
                            contenido = archivo_entrada.read()
                            archivo_salida.write(contenido)
                            
                        print(f"  [OK] Añadido: {ruta_relativa}")

                    except Exception as e:
                        error_msg = f"\n# ERROR AL LEER EL ARCHIVO: {ruta_relativa}\n# Error: {e}\n"
                        archivo_salida.write(error_msg)
                        print(f"  [FAIL] Error al leer {ruta_relativa}: {e}")

    print(f"\n¡Proceso completado! Contenido generado en: {ruta_salida}")


def main():
    parser = argparse.ArgumentParser(
        description="""
        📝 Herramienta para concatenar el contenido de todos los archivos de código 
        en un único archivo de texto. Útil para análisis o transferencias de código.
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

    # Argumento del Archivo de Salida
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        default='contenido_total.txt', 
        help="Nombre del archivo donde se guardará el contenido. Por defecto: contenido_total.txt."
    )
    
    # Argumento de Exclusiones (nuevo)
    parser.add_argument(
        '-e', '--exclude',
        nargs='*', # Permite cero o más argumentos
        default=[],
        help="Lista de nombres de directorios/archivos a excluir, separados por espacios (Ej: -e node_modules logs secret.py)."
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directorio):
        print(f"Error: El directorio '{args.directorio}' no existe o la ruta es incorrecta.")
        return

    concatenar_archivos(args.directorio, args.output, args.exclude)


if __name__ == "__main__":
    main()

## Forma de ejecución para todos los archivos y excluyendo : python generador_contenido.py -d  pongamonos_serios -o resumen_codigo.txt -e .pytest_cache .terraform .terraform.lock.hcl lambda_funcion.zip lambda.zip
"""
Comando de Ejecución para Archivos .tfAhora puedes usar el nuevo parámetro -x para filtrar solo los archivos de Terraform.Comando de Filtrado (Solo Archivos .tf y .hcl)Si quieres recorrer la carpeta infraestructura (asumiendo que ese es tu directorio de Terraform), y solo incluir archivos con extensión .tf y .hcl:Bashpython generador_contenido.py -d infraestructura -o terraform_code.txt -x tf hcl
Comando con Filtro y ExclusiónSi, además, quieres excluir cualquier archivo llamado secrets.tf:Bashpython generador_contenido.py -d infraestructura -o terraform_code.txt -x tf hcl -e secrets.tf
📄 Archivo de Documentación Actualizado (README.md)He añadido la nueva opción al README.md.Markdown# 📁 Generador de Contenido de Proyecto

Herramienta de Python para **concatenar** todo el código de un proyecto en un **único archivo de texto**. Útil para análisis o transferencias de código.

## ⚙️ Uso

Asegúrate de ejecutar el script desde la línea de comandos en el mismo directorio donde se encuentra `generador_contenido.py`.

### 1. Comando Básico (Solo Directorio)

Recorre el directorio `example` y genera el archivo de salida con el nombre por defecto (`contenido_total.txt`).

| Opción Larga | Opción Corta | Descripción |
| :--- | :--- | :--- |
| `--directorio` | `-d` | **Ruta del directorio** del proyecto. **(OBLIGATORIO)** |

```bash
python generador_contenido.py --directorio example
# O
python generador_contenido.py -d example
2. Comando para Filtro de Extensiones Específicas (NUEVO)Ideal para incluir solo archivos de un tipo específico, como .tf o .json.Opción LargaOpción CortaDescripción--extensiones-xLista de extensiones a incluir (Ej: -x tf hcl json). No requiere el punto.Ejemplo (Solo archivos de Terraform):Bashpython generador_contenido.py -d infraestructura -o terraform.txt -x tf hcl
3. Comando Personalizado (Archivo de Salida)Permite especificar el nombre del archivo de salida.Opción LargaOpción CortaDescripción--output-oNombre del archivo de salida (Por defecto: contenido_total.txt).Bashpython generador_contenido.py -d example -o resumen.txt
4. Comando con Exclusiones (Ignorar Carpetas/Archivos)Permite excluir directorios o archivos específicos, separados por espacios.Opción LargaOpción CortaDescripción--exclude-eLista de nombres a ignorar (Ej: -e node_modules logs secret.py).Bash# Excluir la carpeta 'services' y el archivo 'requirements.txt'
python generador_contenido.py -d example -o codigo_completo.txt -e services requirements.txt
"""
# ejecutar la concatenación de archivos del directorio llamado archivos por fuera de el debe existir el archivo generador_contenido.py y todo lo concatenara en el archivo llamado archivos.txt excluyendo los archivos o directorios services o requirements.txt 
#python generador_contenido.py -d archivos -o archivos.txt -e services requirements.txt