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
