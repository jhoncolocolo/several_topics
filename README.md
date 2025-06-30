SELECT usuario,
       identificador_registro,
       identificador_sucursal,
       fecha_modificacion
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY usuario
               ORDER BY fecha_modificacion DESC
           ) AS rn
    FROM registro_usuario_sucursal
) AS sub
WHERE rn = 1;
