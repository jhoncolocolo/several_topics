WITH UltimosRegistrosSucursal AS (
    SELECT
        usuario,
        identificador_registro,
        identificador_sucursal,
        CAST(MAX(fecha_modificacion) AS TIMESTAMP(0)) AS ultima_fecha_modificacion_truncada
    FROM
        registro_usuario_sucursal
    GROUP BY
        usuario,
        identificador_registro,
        identificador_sucursal
),
UltimosRegistrosOficina AS (
    SELECT
        usuario,
        identificador_registro,
        identificador_sucursal,
        CAST(MAX(fecha_modificacion) AS TIMESTAMP(0)) AS ultima_fecha_modificacion_truncada
    FROM
        registro_usuario_sucursal_oficina
    GROUP BY
        usuario,
        identificador_registro,
        identificador_sucursal
)
SELECT
    urs.usuario,
    urs.identificador_registro,
    urs.identificador_sucursal,
    urs.ultima_fecha_modificacion_truncada
FROM
    UltimosRegistrosSucursal urs
LEFT JOIN
    UltimosRegistrosOficina uro ON
        urs.usuario = uro.usuario AND
        urs.identificador_registro = uro.identificador_registro AND
        urs.identificador_sucursal = uro.identificador_sucursal AND
        urs.ultima_fecha_modificacion_truncada = uro.ultima_fecha_modificacion_truncada
WHERE
    uro.usuario IS NULL -- Esto significa que no se encontró una coincidencia en UltimosRegistrosOficina
ORDER BY
    urs.usuario,
    urs.identificador_registro,
    urs.identificador_sucursal;
