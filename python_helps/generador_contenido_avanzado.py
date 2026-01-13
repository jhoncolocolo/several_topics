import os
import pathlib
import argparse

def obtener_archivos_a_incluir(directorio_raiz, extensiones, lista_archivos_custom):
    """
    Determina la lista final de archivos a incluir, ya sea por extensión o por lista custom.
    """
    archivos_a_procesar = set()
    
    # === 1. Lógica de Inclusión por Extensión ===
    if extensiones:
        # Asegurar formato de extensiones
        extensiones_a_incluir = [('.' + ext).replace('..', '.') for ext in extensiones]
        
        for directorio_actual, subdirectorios, archivos in os.walk(directorio_raiz, topdown=True):
            # Exclusiones de carpetas comunes
            subdirectorios[:] = [d for d in subdirectorios if d not in {'__pycache__', '.git', 'node_modules', 'venv', '.vscode', 'dist', 'build'}]
            
            for nombre_archivo in archivos:
                ruta_completa_archivo = pathlib.Path(directorio_actual) / nombre_archivo
                
                if ruta_completa_archivo.suffix in extensiones_a_incluir:
                    archivos_a_procesar.add(str(ruta_completa_archivo.resolve()))
    
    # === 2. Lógica de Inclusión por Lista Custom ===
    # Si hay una lista custom, sobreescribe/complementa la lógica de extensión
    if lista_archivos_custom:
        for nombre_archivo in lista_archivos_custom:
            ruta_custom = pathlib.Path(directorio_raiz) / nombre_archivo
            
            # Solo añadir si el archivo existe
            if ruta_custom.is_file():
                archivos_a_procesar.add(str(ruta_custom.resolve()))
            else:
                print(f"⚠️ Advertencia: Archivo custom no encontrado y omitido: {nombre_archivo}")

    return archivos_a_procesar

def concatenar_archivos_filtrados(directorio_raiz, nombre_archivo_salida, extensiones, lista_archivos_custom, exclusiones):
    """
    Función principal que concatena el contenido de los archivos seleccionados.
    """
    
    directorio_raiz_path = pathlib.Path(directorio_raiz)
    ruta_salida = directorio_raiz_path / nombre_archivo_salida
    archivos_a_procesar_abs = obtener_archivos_a_incluir(directorio_raiz, extensiones, lista_archivos_custom)

    print(f"Iniciando procesamiento en: {directorio_raiz}")
    print(f"Archivos únicos a procesar: {len(archivos_a_procesar_abs)}")
    
    # Preparamos las exclusiones de nombres de archivos
    exclusiones_nombres = set(exclusiones)
    if nombre_archivo_salida:
        exclusiones_nombres.add(nombre_archivo_salida)
        
    archivos_procesados_con_exito = 0

    with open(ruta_salida, 'w', encoding='utf-8') as archivo_salida:
        
        for ruta_abs_str in sorted(list(archivos_a_procesar_abs)):
            ruta_completa_archivo = pathlib.Path(ruta_abs_str)
            nombre_archivo = ruta_completa_archivo.name
            
            # Aplicar exclusiones de nombre de archivo o el propio archivo de salida
            if nombre_archivo in exclusiones_nombres:
                continue
                
            try:
                # Generar la ruta relativa para el encabezado
                # Usamos la ruta relativa para mantener la salida limpia
                ruta_relativa = ruta_completa_archivo.relative_to(directorio_raiz_path.resolve())

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
                archivos_procesados_con_exito += 1

            except Exception as e:
                error_msg = f"\n# ERROR AL LEER EL ARCHIVO: {ruta_relativa}\n# Error: {e}\n"
                archivo_salida.write(error_msg)
                print(f"  [FAIL] Error al leer {ruta_relativa}: {e}")

    print(f"\n¡Proceso completado! Se procesaron {archivos_procesados_con_exito} archivos. Contenido generado en: {ruta_salida}")


def main():
    parser = argparse.ArgumentParser(
        description="""
        📝 Herramienta flexible para concatenar el contenido de archivos de código en un único archivo de texto.
        Permite filtrar por extensión o por una lista de archivos específicos.
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
    
    # Argumento de Filtro por Extensión
    parser.add_argument(
        '-x', '--extensiones',
        nargs='*', # Permite cero o más argumentos
        default=[],
        help="Filtro por **extensiones** de archivos a incluir (Ej: -x tf hcl). **IGNORADO si se usa -i**."
    )
    
    # Argumento de Inclusión por Lista Custom (NUEVO)
    parser.add_argument(
        '-i', '--include',
        nargs='*', # Permite cero o más argumentos
        default=[],
        help="**Lista custom** de archivos a incluir, con rutas relativas al directorio raíz (Ej: -i main.tf modules/network/vars.tf). **Si se usa, IGNORA -x**."
    )
    
    # Argumento de Exclusiones
    parser.add_argument(
        '-e', '--exclude',
        nargs='*', # Permite cero o más argumentos
        default=[],
        help="Lista de nombres de archivos a excluir (Ej: -e secret.py, o directorios si se usa -x)."
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directorio):
        print(f"Error: El directorio '{args.directorio}' no existe o la ruta es incorrecta.")
        return
        
    # Lógica de priorización de inclusión: -i tiene prioridad sobre -x
    if args.include:
        extensiones_usadas = [] # No usamos extensiones si -i está presente
        lista_archivos_custom = args.include
    else:
        extensiones_usadas = args.extensiones
        lista_archivos_custom = []

    if not extensiones_usadas and not lista_archivos_custom:
        print("Error: Debes especificar archivos a incluir usando -x (extensiones) o -i (lista custom).")
        return

    concatenar_archivos_filtrados(
        args.directorio, 
        args.output, 
        extensiones_usadas, 
        lista_archivos_custom, 
        args.exclude
    )


if __name__ == "__main__":
    main()

    ## generar archivos especificos python generador_contenido_avanzado.py -d archivos -o archivos.txt -e non-exists-file.txt
"""
 Comandos de Ejecución
 Guarda el código anterior como generador_contenido_avanzado.py.1. 
 Opción: Concatenar por Extensión (Ejemplo: Todos los .tf)
 Este es el mismo que antes,
  usa -x. Recorrerá el directorio infra buscando todo lo que termine en .tf o .hcl.
 Bash
 python generador_contenido_avanzado.py -d infra -o terraform_bundle.txt -x tf hcl
2. Opción: Concatenar por Lista Custom 
(Ejemplo: Archivos Específicos) Esta es la nueva opción con -i. 
Ignora la opción -x y solo procesa los archivos que tú listes con su ruta relativa.Comando:
Bash
python generador_contenido_avanzado.py -d example -o code_review.txt -i src/models/escribir_o_borrar_tupla_peticion.py src/procesadores/procesador_tabla1.py requirements.txt

📄 Archivo de Documentación Actualizado (README.md)
Actualicé el README.md para reflejar la nueva y mejorada lógica de inclusión.
Markdown# 📁 Generador de Contenido de Proyecto Avanzado

Herramienta de Python para **concatenar** el contenido de archivos filtrados por **extensión** 
o por **lista custom** en un único archivo de texto.

## ⚙️ Uso

Asegúrate de ejecutar el script desde la línea de comandos.

### Argumentos Principales

| Opción Larga | Opción Corta | Descripción |
| :--- | :--- | :--- |
| `--directorio` | `-d` | **Ruta del directorio** del proyecto. **(OBLIGATORIO)** |
| `--output` | `-o` | **Nombre del archivo** de salida (Por defecto: `contenido_total.txt`). |

***

### 1. ⚙️ Filtrado por Lista de Archivos Custom (`--include` / `-i`)

Esta opción tiene **prioridad** y es para incluir archivos específicos, ignorando cualquier filtro de extensión (`-x`).

| Opción Larga | Opción Corta | Descripción |
| :--- | :--- | :--- |
| `--include` | `-i` | **Lista custom de archivos** a incluir, con rutas relativas al directorio raíz (Ej: `-i main.py configs/db.json`). |

**Ejemplo:** Solo incluir dos archivos de la lista `example`.
```bash
python generador_contenido_avanzado.py -d example -o review.txt -i src/models/escribir_o_borrar_tupla_peticion.py lambda_function.py
2. 🔍 Filtrado por Extensión (--extensiones / -x)
Esta opción se usa cuando no especificas archivos custom con -i. 
Recorre todo el árbol de directorios (excluyendo carpetas comunes) 
y filtra por la extensión.
Opción Larga
Opción Corta
Descripción--extensiones-xLista de extensiones a incluir (Ej: -x tf hcl json).
 No requiere el punto.
 --exclude-eLista de nombres de archivos a excluir (Ej: -e secret.py).
 Ejemplo (Solo archivos de Terraform):
 Bash
python generador_contenido_avanzado.py -d infra -o terraform.txt -x tf hcl -e secrets.tf
"""