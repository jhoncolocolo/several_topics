# several_topics

```
 function transformIdentificationForcing(input) {
  // 1 Eliminar guiones del input
  const normalized = input.toUpperCase().replace(/-/g, "");

  // 2 Buscar la posición de "E8"
  const index = normalized.indexOf("E8");
  if (index === -1) {
    return "Invalid format";
  }

  // 3 Extraer la parte después de "E8"
  const rawSuffix = normalized.substring(index + 2);

  // 4 Eliminar ceros solo si hay un dígito diferente de cero después
  const suffix = rawSuffix.replace(/^0+(?!$)/, "");

  // 5 Validar que la parte de la cédula que va después de E-8- si tenga entre 1 y 6 dígitos
  if (!/^\d{1,6}$/.test(suffix)) {
    return "Invalid format";
  }

  // 6 Construir la salida con "E-" y "8" separadas.
  return "E-" + suffix;
}
```
