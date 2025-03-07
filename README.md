 ```
import { execSync, spawn } from "child_process";
import path from "path";

// Parámetros constantes
const validToken = "789456";
const validSeed = "ASDASDASDASDSA";

// Ruta del script compilado
const scriptPath = path.join(__dirname, "dist", "index.test.local.js");

// Función para generar la fecha y hora actual en formato YYYY-MM-DD HH:mm:ss
function getCurrentDateTime(): string {
    const now = new Date();
    return now.toISOString().replace("T", " ").substring(0, 19);
}

// Compilar TypeScript antes de ejecutar
console.log("Compilando TypeScript...");
try {
    execSync("npm run build", { stdio: "inherit" });
    console.log("Compilación completada.\n");
} catch (error) {
    console.error("Error al compilar TypeScript. Revisa los errores.");
    process.exit(1);
}

// Ejecutar el script en un bucle con nuevas fechas cada 5 segundos
setInterval(() => {
    const dateTime = getCurrentDateTime();
    console.log(`Ejecutando con fecha y hora: ${dateTime}`);

    const process = spawn("node", [scriptPath, validToken, validSeed, dateTime], {
        stdio: "inherit", // Para mostrar la salida en la consola
    });

    process.on("exit", (code) => {
        console.log(`Proceso finalizado con código: ${code}`);
    });
}, 5000); // Ejecutar cada 5 segundos

```


```
"scripts": {
    "build": "tsc",
    "test": "node dist/tests/index.test.js",
    "run-with-datetime": "tsc && node dist/run_with_datetime.js"
}

```
