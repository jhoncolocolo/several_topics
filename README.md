```
sequenceDiagram
  autonumber
  participant P as Pipeline
  participant MS as Microservicio
  participant DB as Base de datos
  participant FGA as API de OpenFGA

  Note over P,MS: El Pipeline inicia el proceso con un parámetro (0, 1 o 2)

  P->>MS: Ejecutar migración(se_migro = 0 | 1 | 2)

  alt se_migro == 0 (no migrados)
    MS->>DB: SELECT * FROM USUARIO WHERE se_migro = 0
    DB-->>MS: Conjunto de usuarios no migrados
    MS->>MS: Cruza USUARIO_CUENTA y USUARIO_CLIENTE_TIPOPAIS<br/>Mapea a tuplas (dueno / ayudante / es_cliente)
    loop por usuario o por lote
      MS->>FGA: /writeTuples (crear tuplas)
      FGA-->>MS: Resultado (éxitos/errores, metadatos)
    end
    MS-->>P: Resumen customizado (creadas, fallidas, tiempos)
  else se_migro == 1
    MS->>DB: SELECT * FROM USUARIO ... (regla de negocio para 1)
    DB-->>MS: Conjunto de registros
    MS->>MS: Procesa según regla de negocio para 1 (p.ej. solo verificación)
    MS-->>P: Resumen (sin escritura o validaciones)
  else se_migro == 2
    MS->>DB: SELECT * FROM USUARIO ... (regla de negocio para 2)
    DB-->>MS: Conjunto de registros
    MS->>MS: Genera/actualiza tuplas según regla de negocio para 2
    MS->>FGA: /writeTuples (upsert/forzar)
    FGA-->>MS: Resultado (éxitos/errores)
    MS-->>P: Resumen customizado (reprocesados, actualizados)
  end

  Note over MS,FGA: OpenFGA valida contra el modelo y persiste las tuplas
```
