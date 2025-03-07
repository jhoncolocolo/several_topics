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
