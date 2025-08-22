```
SELECT
  -- Usa la función COUNT y un CASE para contar los registros del 17 de agosto
  COUNT(CASE WHEN DAY(FECHA) = 17 THEN 1 ELSE NULL END) AS Registros_Dia_17,

  -- Cuenta los registros del 18 de agosto
  COUNT(CASE WHEN DAY(FECHA) = 18 THEN 1 ELSE NULL END) AS Registros_Dia_18,

  -- Cuenta los registros del 19 de agosto
  COUNT(CASE WHEN DAY(FECHA) = 19 THEN 1 ELSE NULL END) AS Registros_Dia_19

FROM TABLA_REGISTROS
WHERE
  -- Filtra por el rango de fechas para mejorar el rendimiento
  DATE(FECHA) BETWEEN '2025-08-17' AND '2025-08-19'
  AND DETALLE IN ('detalle 1', 'detalle 2', 'detalle 3');
```
