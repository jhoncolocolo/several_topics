# several_topics

```
Informe General: Comparación de Gestión de Configuración y Costos

Escenario Actual (Microsoft Azure App Configuration con Caché Java):

Gestión de Configuración: Un microservicio realiza llamadas al servicio Azure App Configuration para obtener los parámetros de configuración.
Gestión de Caché: La aplicación Java implementa una lógica de caché local. Esta caché tiene un ciclo de vida (ej., una hora), y la recarga de la caché se activa generalmente por la primera solicitud después de la expiración del TTL o por un evento específico.
Costos (Estimación): Se incurre en costos por cada llamada realizada al servicio Azure App Configuration. Si, por ejemplo, la caché se recarga cada hora debido a la primera solicitud de un usuario, y tienes un volumen significativo de usuarios, esto puede generar un número considerable de llamadas diarias al servicio de configuración, lo que se traduce en costos directos por esas solicitudes. Además, la lógica de caché debe ser implementada y mantenida dentro de la aplicación Java.
Escenario Propuesto (AWS AppConfig con Agente):

Gestión de Configuración: Se utilizará AWS AppConfig para almacenar y gestionar las configuraciones. El microservicio interactuará con el AWS AppConfig Agent.
Gestión de Caché: El AWS AppConfig Agent gestiona automáticamente una caché local en la instancia donde se ejecuta el microservicio. El agente realiza un polling asíncrono al servicio AppConfig para verificar actualizaciones en un intervalo configurable. Las lecturas de configuración posteriores a la primera (dentro del intervalo de polling y sin cambios en la configuración) se realizan directamente desde la caché local del agente.
Costos (Estimación):
Solicitudes de configuración: Se cobra por cada solicitud que llega al servicio AWS AppConfig. La primera solicitud de una instancia por configuración (o después de una actualización) generará un costo. Las lecturas desde la caché local del agente no generan costos de solicitud.
Configuraciones Recibidas: Se cobra cada vez que el agente descarga datos de configuración actualizados.
Beneficio: El uso del agente y su caché local reduce significativamente la cantidad de llamadas directas al servicio AppConfig, lo que disminuye los costos en comparación con un escenario donde cada solicitud (o un evento periódico frecuente) dispara una llamada al servicio de configuración.
URL de Precios de AWS AppConfig:

Puedes encontrar la información detallada de los precios de AWS AppConfig en la página oficial de AWS Systems Manager:

https://aws.amazon.com/es/systems-manager/pricing/

(Busca la sección específica de "Application Configuration Manager (AppConfig)")

URL de Precios de Azure App Configuration:

Puedes encontrar la información detallada de los precios de Azure App Configuration en la página oficial de Azure:

https://azure.microsoft.com/es-es/pricing/details/app-configuration/

Conclusión General:

La migración a AWS AppConfig con su agente integrado y gestión de caché local tiene el potencial de reducir significativamente los costos asociados a la recuperación de configuración en comparación con un modelo donde la caché se gestiona a nivel de aplicación y cada solicitud (o un evento periódico) puede generar una llamada al servicio de configuración. AWS AppConfig está diseñado para optimizar las llamadas al servicio, cobrando principalmente por la obtención inicial de la configuración y por las actualizaciones, mientras que las lecturas frecuentes se sirven desde la caché local sin incurrir en costos adicionales por solicitud. Esto se traduce en una gestión de configuración más eficiente y potencialmente más económica para aplicaciones con un alto volumen de lecturas de configuración.
```
