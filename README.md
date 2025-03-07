 ```
 const { execSync } = require('child_process');

const parametrosBase = "789456 ASDASDASDASDSA";
const fechaBase = "2023-10-27"; // Mantén la fecha constante

// Generar horas variadas (ejemplo: de 10:00 a 14:00 con incrementos de 1 hora)
for (let hora = 10; hora <= 14; hora++) {
  const horaFormateada = hora.toString().padStart(2, '0'); // Asegura dos dígitos para la hora
  const fechaHora = `"${fechaBase} ${horaFormateada}:30:00"`; // Formato de fecha y hora

  const comando = `node dist/index.test.local.js ${parametrosBase} ${fechaHora}`;

  console.log(`Ejecutando: ${comando}`);

  try {
    const resultado = execSync(comando, { encoding: 'utf-8' });
    console.log(resultado); // Imprime la salida del script principal
  } catch (error) {
    console.error(`Error al ejecutar: ${comando}`);
    console.error(error.stderr); // Imprime el error
  }
}

console.log("Ciclo completado.");
```
