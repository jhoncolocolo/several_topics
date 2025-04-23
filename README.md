# several_topics

Vamos a desglosar cómo sería el cobro de AWS AppConfig en tu escenario específico con cuatro aplicaciones y cuatro microservicios, donde cada microservicio consulta su respectiva aplicación de configuración y la caché se refresca cada hora.

Tu Escenario:

Cuatro Aplicaciones en AppConfig: pagos, préstamos, compras, seguridad.
Cuatro Microservicios: pagos, préstamos, compras, seguridad.
Relación: Cada microservicio consulta la configuración de su aplicación AppConfig con el mismo nombre.
Frecuencia de "Refresco" (Polling): Cada microservicio (a través del AWS AppConfig Agent) verificará si hay actualizaciones de su configuración cada hora (24 veces al día).
Proceso de Cobro Detallado:

Vamos a analizar el costo para una sola aplicación y su microservicio correspondiente, y luego lo multiplicaremos por cuatro (asumiendo un comportamiento similar en cada par).

Para una Aplicación (Ejemplo: pagos) y su Microservicio:

Solicitud Inicial: La primera vez que el microservicio pagos (o más precisamente, la instancia donde se ejecuta el agente del microservicio pagos) solicita la configuración de la aplicación pagos, se genera:

1 Solicitud de Configuración: Costo = $0.0000002
1 Configuración Recibida: Costo = $0.0008
Polling Horario (Refresco de la "Caché"): Para mantener la "caché" actualizada cada hora, el agente del microservicio pagos realizará un poll al servicio AppConfig cada hora. En un día habrá 24 polls. Cada poll es una Solicitud de Configuración.

24 Solicitudes de Configuración por día: Costo = 24 * $0.0000002 = $0.0000048
Recepción de Configuración por Polling (si no hay cambios): Si en la mayoría de estos 24 polls diarios no hay cambios en la configuración de la aplicación pagos, no se generará costo de "Configuración Recibida" para esos polls. El agente simplemente verificará y usará su caché local.

Recepción de Configuración por Actualización (si la configuración cambia): Si la configuración de la aplicación pagos cambia durante el día (por ejemplo, una vez), entonces en el poll que ocurra después del cambio, el agente recibirá la nueva configuración, generando un costo de 1 Configuración Recibida: Costo = $0.0008. La frecuencia de estos cambios dependerá de tu dinámica de despliegue de configuración. Para este ejemplo, asumamos que la configuración cambia una vez al día.

Costo Diario Estimado para una Aplicación y su Microservicio:

Costo de Solicitud Inicial (amortizado en el primer día): $0.0000002
Costo de Configuración Recibida Inicial (amortizado en el primer día): $0.0008
Costo de Polling Diario (24 solicitudes): $0.0000048
Costo de Configuración Recibida por Actualización Diaria (asumiendo 1 cambio): $0.0008
Costo Total Diario por Par (Aplicación + Microservicio): $0.0000002 + $0.0008 + $0.0000048 + $0.0008 = $0.001605

Costo Total Diario Estimado para las Cuatro Aplicaciones y Microservicios:

Si cada uno de los cuatro pares (pagos, préstamos, compras, seguridad) tiene un comportamiento similar, el costo total diario estimado sería:

$0.001605/par * 4 pares = $0.00642

Costo Mensual Estimado:

$0.00642/día * 30 días ≈ $0.1926

Costo Anual Estimado:

$0.00642/día * 365 días ≈ $2.3433

Puntos Clave del Cobro:

Solicitudes: Se cobra por cada verificación horaria (poll) que realiza cada microservicio a su respectiva aplicación.
Recepciones: Se cobra principalmente la primera vez que cada microservicio obtiene la configuración y cada vez que la configuración cambia y el agente la descarga. Si la configuración no cambia durante los polls horarios, no hay costo adicional por recepción.
Por Destino: Estos costos se aplican por cada instancia de tu microservicio. Si tienes múltiples instancias del microservicio pagos, cada una tendrá su propio ciclo de solicitudes y recepciones. Los cálculos anteriores asumen una instancia por microservicio. Si tienes más instancias, debes multiplicar los costos por el número de instancias por microservicio.
En resumen:

El cobro se basa en la actividad de cada microservicio al interactuar con su aplicación de configuración. La estrategia de refrescar la caché cada hora generará 24 solicitudes de configuración por día por cada instancia de cada microservicio. El costo de recepción se incurrirá inicialmente y cada vez que la configuración cambie.

Recuerda que estos son cálculos estimados basados en las suposiciones de una instancia por microservicio y una actualización de configuración por día por aplicación. Los costos reales pueden variar según el número de instancias y la frecuencia con la que actualices tus configuraciones.

```
 
```
