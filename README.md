```
SELECT r.*
FROM registro_usuario_sucursal r
WHERE fecha_modificacion = (
    SELECT MAX(r2.fecha_modificacion)
    FROM registro_usuario_sucursal r2
    WHERE r2.usuario = r.usuario
);
```
