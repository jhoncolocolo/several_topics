 ```
function timestampToDate(timestamp: number): string {
    const date = new Date(timestamp * 1000); // Convertir de segundos a milisegundos
    return date.toISOString(); // Formato ISO 8601
}

// Ejemplo de uso:
console.log(timestampToDate(1741379279)); // "2025-03-07T20:27:59.000Z"

```


```
function dateStringToTimestamp(dateString: string): number {
    const date = new Date(dateString.replace(" ", "T") + "Z"); // Convertir a formato ISO
    return Math.floor(date.getTime() / 1000); // Convertir de milisegundos a segundos
}

// Ejemplo de uso:
console.log(dateStringToTimestamp("2025-03-07 20:27:59")); // 1741379279



```

```
const fs = require('fs');

function generarCadenaAleatoria(longitud) {
  let resultado = '';
  const caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
  const caracteresLength = caracteres.length;
  for (let i = 0; i < longitud; i++) {
    resultado += caracteres.charAt(Math.floor(Math.random() * caracteresLength));
  }
  return resultado;
}

function codificarBase64(cadena) {
  return Buffer.from(cadena).toString('base64');
}

const numCadenas = 10000;
const longitudCadena = 64;
const nombreArchivo = 'data.ts';

let contenidoArchivo = `interface Data {\n  strings: string[];\n}\n\nconst data: Data = {\n  strings: [\n`;

for (let i = 0; i < numCadenas; i++) {
  const cadenaAleatoria = generarCadenaAleatoria(longitudCadena);
  const cadenaBase64 = codificarBase64(cadenaAleatoria);
  contenidoArchivo += `    "${cadenaBase64}",\n`;
}

contenidoArchivo = contenidoArchivo.slice(0, -2); // Elimina la última coma y salto de línea
contenidoArchivo += `\n  ]\n};\n\nexport default data;\n`;

fs.writeFile(nombreArchivo, contenidoArchivo, (err) => {
  if (err) {
    console.error('Error al escribir el archivo:', err);
  } else {
    console.log(`Se ha generado y escrito ${numCadenas} cadenas en ${nombreArchivo}`);
  }
});
```
```
import * as fs from "fs";
import path from "path";

// Archivo donde se guardarán los logs
const logPath = path.join(__dirname, "execution.log");
const logStream = fs.createWriteStream(logPath, { flags: "w" });

// Guardar la referencia original de console.log
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

// Sobrescribir console.log para capturar la salida
console.log = function (...args) {
    const message = args.map(arg => String(arg)).join(" ");
    logStream.write(`[LOG] ${message}\n`);
    originalConsoleLog.apply(console, args);
};

// Sobrescribir console.error para capturar errores
console.error = function (...args) {
    const message = args.map(arg => String(arg)).join(" ");
    logStream.write(`[ERROR] ${message}\n`);
    originalConsoleError.apply(console, args);
};

// Cerrar el archivo cuando el proceso termine
process.on("exit", () => {
    logStream.end();
});
```

```
//command node generador_since_cvs.js semilla input.csv data.ts
//dependencies  npm install csv-parser
 const fs = require('fs');
const csv = require('csv-parser');

const args = process.argv.slice(2);

if (args.length !== 3) {
  console.error('Uso: node generador_data_ts_csv.js <nombre_columna> <nombre_archivo_csv> <nombre_archivo_a_crear>');
  process.exit(1);
}

const nombreColumna = args[0].replace(/['"]/g, ''); // Elimina comillas simples y dobles
const nombreArchivoCSV = args[1];
const nombreArchivoTS = args[2];

const semillas = [];
let headers = null;

fs.createReadStream(nombreArchivoCSV)
  .pipe(csv())
  .on('headers', (headerList) => {
    // Normaliza los nombres de las columnas eliminando apóstrofes o comillas
    headers = headerList.map(header => header.replace(/['"]/g, ''));
    console.log('Nombres de columnas detectados:', headers);
  })
  .on('data', (row) => {
    // Normaliza las claves del objeto row para que coincidan con los encabezados limpiados
    const rowNormalized = {};
    for (const key in row) {
      const cleanKey = key.replace(/['"]/g, '');
      rowNormalized[cleanKey] = row[key];
    }

    let valorColumna = rowNormalized[nombreColumna];

    if (valorColumna !== undefined) {
      semillas.push(valorColumna);
    } else {
      console.error(`Advertencia: La columna '${nombreColumna}' no existe en la fila:`, row);
    }
  })
  .on('end', () => {
    let contenidoArchivo = `interface Data {\n  strings: string[];\n}\n\nconst data: Data = {\n  strings: [\n`;

    semillas.forEach((semilla) => {
      contenidoArchivo += `    "${semilla}",\n`;
    });

    contenidoArchivo = contenidoArchivo.slice(0, -2);
    contenidoArchivo += `\n  ]\n};\n\nexport default data;\n`;

    fs.writeFile(nombreArchivoTS, contenidoArchivo, (err) => {
      if (err) {
        console.error('Error al escribir el archivo:', err);
      } else {
        console.log(`Se ha generado y escrito ${semillas.length} cadenas en ${nombreArchivoTS}`);
      }
    });
  });

```
```
// generador_cadenas.ts
import crypto from 'crypto';

export const generate = (): string => {
  const byteSize = 120;
  const ramdomBytes = crypto.randomBytes(byteSize);
  return ramdomBytes.toString('base64');
};

function ejecutarOtraFuncion(cadenas: string[]) {
  // Aquí va la lógica de tu otra función
  console.log('Ejecutando otra función con las cadenas generadas:');
  console.log(cadenas);
  // Por ejemplo, podrías escribir las cadenas en un archivo:
  // fs.writeFileSync('cadenas.txt', cadenas.join('\n'));
}

function generarYCadenas(numCadenas: number) {
  const cadenas: string[] = [];
  for (let i = 0; i < numCadenas; i++) {
    cadenas.push(generate());
  }
  ejecutarOtraFuncion(cadenas);
}

// Leer el número desde la consola
const args = process.argv.slice(2);
if (args.length !== 1) {
  console.error('Uso: node generador_cadenas.js <numero_cadenas>');
  process.exit(1);
}

const numCadenas = parseInt(args[0], 10);
if (isNaN(numCadenas) || numCadenas <= 0) {
  console.error('El número de cadenas debe ser un entero positivo.');
  process.exit(1);
}

generarYCadenas(numCadenas);
```

```

import * as fs from "fs";
import path from "path";

// Leer el argumento de la línea de comandos
const enableLogging = process.argv[3] === "true";

let logStream: fs.WriteStream | null = null;

if (enableLogging) {
    // Archivo donde se guardarán los logs
    const logPath = path.join(__dirname, "execution.log");
    logStream = fs.createWriteStream(logPath, { flags: "w" });
}

// Guardar la referencia original de console.log
const originalConsoleLog = console.log;
const originalConsoleError = console.error;

// Sobrescribir console.log si está activado
if (enableLogging && logStream) {
    console.log = function (...args) {
        const message = args.map(arg => String(arg)).join(" ");
        logStream.write(`[LOG] ${message}\n`);
        originalConsoleLog.apply(console, args);
    };

    console.error = function (...args) {
        const message = args.map(arg => String(arg)).join(" ");
        logStream.write(`[ERROR] ${message}\n`);
        originalConsoleError.apply(console, args);
    };

    // Cerrar el archivo cuando el proceso termine
    process.on("exit", () => {
        logStream?.end();
    });
}
```

```
// ciclo_minutos.ts

function generarCicloMinutos(fechaInicio: Date, fechaFin: Date): void {
  let fechaActual: Date = new Date(fechaInicio);

  while (fechaActual <= fechaFin) {
    console.log(fechaActual.toISOString().slice(0, 16)); // Imprime la fecha y hora actual hasta el minuto

    // Incrementa un minuto
    fechaActual.setMinutes(fechaActual.getMinutes() + 1);
  }
}

// Leer los argumentos de la consola
const args: string[] = process.argv.slice(2);

if (args.length !== 2) {
  console.error(
    'Uso: node ciclo_minutos.js <fecha_inicio_iso> <fecha_fin_iso>'
  );
  console.error(
    'Ejemplo: node ciclo_minutos.js "2024-10-27T00:00" "2024-10-27T23:59"'
  );
  process.exit(1);
}

const fechaInicioISO: string = args[0] + ':00.000Z'; // Añade segundos y milisegundos para crear Date
const fechaFinISO: string = args[1] + ':00.000Z'; // Añade segundos y milisegundos para crear Date

const fechaInicio: Date = new Date(fechaInicioISO);
const fechaFin: Date = new Date(fechaFinISO);

if (isNaN(fechaInicio.getTime()) || isNaN(fechaFin.getTime())) {
  console.error('Fechas inválidas. Use formato ISO 8601 (YYYY-MM-DDTHH:MM).');
  process.exit(1);
}

generarCicloMinutos(fechaInicio, fechaFin);
```

```
<!DOCTYPE html>
<html>
<head>
  <title>Generar Minutos Alrededor</title>
</head>
<body>

  <label for="miInputDateTime">Selecciona fecha y hora:</label>
  <input type="datetime-local" id="miInputDateTime" value="2024-10-27T23:59">

  <br><br>

  <button id="generarBtn">Generar Minutos</button>

  <br><br>

  <textarea id="print" rows="10" cols="50"></textarea>

  <script>
    function aleatorios() {
      return "asdasdas";
    }

    function generarMinutosAlrededor(fechaHoraString) {
      const fechaHora = new Date(fechaHoraString);
      const minutosAlrededor = [];

      // Dos minutos antes
      for (let i = 2; i > 0; i--) {
        const nuevaFecha = new Date(fechaHora);
        nuevaFecha.setMinutes(fechaHora.getMinutes() - i);
        minutosAlrededor.push(nuevaFecha);
      }

      // Minuto actual
      minutosAlrededor.push(fechaHora);

      // Dos minutos después
      for (let i = 1; i <= 2; i++) {
        const nuevaFecha = new Date(fechaHora);
        nuevaFecha.setMinutes(fechaHora.getMinutes() + i);
        minutosAlrededor.push(nuevaFecha);
      }

      return minutosAlrededor;
    }

    const inputDateTime = document.getElementById("miInputDateTime");
    const textareaPrint = document.getElementById("print");
    const generarBtn = document.getElementById("generarBtn");

    generarBtn.addEventListener("click", () => {
      let fechaHora = inputDateTime.value;
      fechaHora = fechaHora + "Z"; // Asegurar que la fecha y hora estén en formato UTC
      const minutosGenerados = generarMinutosAlrededor(fechaHora);

      let textoTextArea = "";
      minutosGenerados.forEach((fecha) => {
        const timestamp = fecha.getTime();
        const fechaISO = fecha.toISOString().slice(0, 16);
        const textoAleatorio = aleatorios();
        textoTextArea += timestamp + " --- " + fechaISO + " --- " + textoAleatorio + "\n";
      });

      textareaPrint.value = textoTextArea;
    });
  </script>

</body>
</html>
```
