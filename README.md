```
 Problema detectado
La configuración original leía un único conjunto de credenciales o secretos de servicio desde un archivo YAML sin contemplar diferencias por país. Esto limitaba la capacidad del sistema para manejar entornos multi-país, ya que todos los módulos compartían un único conjunto de secretos, lo que causaba:

Dificultad para operar con servicios externos que requieren tokens o API keys diferentes por país.

Riesgo de colisión o mezcla de credenciales, especialmente si se reusaban nombres de módulo entre países.

Poca escalabilidad y flexibilidad ante nuevas necesidades regionales.

Además, el código original no tenía una forma clara de heredar valores por defecto ni de sobrescribirlos de forma controlada según el país.

✅ Solución implementada
La clase fue refactorizada para incorporar una estructura jerárquica de configuración por país, representada con objetos Pais, cada uno con su propio Map<String, Credencial> secrets.

Se implementaron las siguientes mejoras clave:

Carga jerárquica de secretos por país:

Se identifica un país default, cuyas credenciales sirven como base.

Cada país puede sobrescribir o extender esas credenciales sin afectar a otros.

Estrategia de herencia controlada:

Se clona el mapa de secretos del país por defecto para cada país, evitando referencias compartidas y efectos colaterales.

Se sobrescriben claves específicas si el país define sus propios secretos.

Enriquecimiento dinámico con secretos sensibles desde Azure Key Vault:

Se agrupan todas las credenciales por clientId.

Para cada clientId, se recuperan de Key Vault el token de aplicación y la API key.

Se asignan esos valores a todas las credenciales asociadas.

Validaciones contra null y mejora de resiliencia:

Se agregaron validaciones para evitar NullPointerException si Key Vault no devuelve valores.

Se loguean advertencias si no se encuentran los secretos esperados.

🎯 Beneficios logrados
Soporte nativo para múltiples países en la configuración de secretos.

Aislamiento seguro y controlado de credenciales por país.

Mayor escalabilidad al permitir añadir países sin duplicar lógica.

Mejora de la seguridad, al separar los valores estáticos (YAML) de los secretos sensibles (Key Vault).

Mayor resiliencia y facilidad para depuración ante fallos de configuración.
```



