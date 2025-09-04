Para redactar el requerimiento para un equipo de DevOps, debes ser claro y conciso, detallando los pasos clave y las tecnologías involucradas. Aquí te muestro cómo podrías estructurar la solicitud para el pipeline, dividida en secciones para mayor claridad.

Requerimiento de Pipeline de CI/CD para Microservicio Java
Se solicita la creación de un pipeline de CI/CD para un microservicio desarrollado en Java 17 con Spring Boot. El objetivo es automatizar la compilación, empaquetado y despliegue del servicio en un servidor PQS, obteniendo las variables de configuración desde Azure Key Vault.

Pasos del Pipeline
Activación y Compilación:

El pipeline debe activarse automáticamente al realizar un push o un pull request a la rama principal (ej. main o develop) del repositorio de código.

Debe compilar el proyecto Spring Boot utilizando Maven o Gradle para generar un archivo JAR ejecutable.

Configuración de Variables de Entorno:

El pipeline debe conectarse a un Azure Key Vault para obtener los valores de cinco variables de entorno.

Las variables son:

AZURE_VAR_1

AZURE_VAR_2

AZURE_VAR_3

AZURE_VAR_4

AZURE_VAR_5

Estas variables deben ser inyectadas en el archivo de propiedades del proyecto (application.properties o application.yml) durante la fase de empaquetado o antes de la ejecución. Es fundamental que estos valores se mantengan seguros y no se expongan en los logs del pipeline.

Empaquetado y Publicación:

Una vez generado el JAR, el pipeline debe subir el artefacto al repositorio de artefactos JFrog Artifactory.

El nombre del artefacto debe seguir una convención estándar (ej. nombre-microservicio-version.jar).

Despliegue en Servidor PQS:

Después de la publicación en JFrog, el pipeline debe conectar al servidor PQS (via SSH, por ejemplo).

Debe descargar el JAR del repositorio de JFrog.

Debe detener el proceso actual del microservicio (si está en ejecución).

Debe iniciar el nuevo JAR, asegurándose de que el endpoint /hello-world esté accesible y retorne la respuesta esperada.

Consideraciones Adicionales
Se requiere que el equipo de DevOps defina y documente la estructura del archivo YAML del pipeline.

El pipeline debe incluir notificaciones de éxito o fallo a un canal de comunicación (ej. Slack, Teams, email).

Se espera que la configuración para la conexión a Azure Key Vault y JFrog se realice de forma segura, utilizando credenciales de servicio o service principals.

Este requerimiento es directo y proporciona toda la información necesaria para que el equipo de DevOps entienda qué se necesita construir y cómo debe funcionar el flujo de despliegue.
