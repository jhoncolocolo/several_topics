El Microservicio de Biometría ha sido diseñado e implementado siguiendo los principios de la arquitectura REST (Representational State Transfer), lo que le permite ofrecer una interfaz de comunicación clara y sin estado. Forma parte integral del ecosistema de microservicios de nuestra organización, promoviendo el desacoplamiento, la escalabilidad y la resiliencia del sistema general.

La arquitectura interna del servicio se compone de las siguientes capas o elementos principales, cada uno con responsabilidades bien definidas:

1. Capa API (Capa de Exposición)
Descripción: Esta es la interfaz pública del microservicio. Se encarga de recibir todas las solicitudes entrantes de los sistemas cliente (consumidores externos). Su responsabilidad principal es validar la estructura y el formato de los requests entrantes según los JSON Schemas definidos, asegurar que los parámetros obligatorios estén presentes y que los tipos de datos sean correctos. También se encarga de formatear las respuestas salientes de acuerdo con los JSON Schemas de respuesta, garantizando la consistencia y la interoperabilidad.
Funcionalidad clave:
Manejo de rutas y métodos HTTP (POST para todos los endpoints).
Validación de identificacion, usuario, documento y pais en todos los requests.
Validación específica de vectorBiometricoFront y vectorBiometricoBack para el endpoint de registrarbiometria.
Serialización/deserialización de JSON.
Manejo de errores a nivel de API, retornando códigos de estado HTTP apropiados y mensajes de error claros.
2. Capa de Lógica de Negocio (Dominio)
Descripción: Esta capa es el "cerebro" del microservicio. Contiene la lógica central y las reglas de negocio específicas del dominio de la biometría. Es responsable de procesar las solicitudes validadas por la Capa API, aplicar las reglas para cada operación (verificar, registrar, consultar, eliminar) y coordinar con otras capas para cumplir con el objetivo de la solicitud. Aquí es donde se determina, por ejemplo, si una biometría ya existe, cómo debe ser registrada o cuál es su estado actual.
Funcionalidad clave:
Implementación de la lógica para verificarbiometria.
Aplicación de reglas para registrarbiometria (ej., unicidad del registro por usuario/documento).
Manejo de la lógica para consultarbiometriaPorusuario y consultarEstadobiometria.
Procesamiento de la solicitud de eliminarbiometria.
Orquestación de llamadas a la Capa de Acceso a Datos y Servicios Externos para obtener o persistir información.
3. Capa de Acceso a Datos y Servicios Externos (Integración)
Descripción: Esta capa actúa como una interfaz entre el microservicio y cualquier almacén de datos persistente o servicios externos. Su responsabilidad es gestionar la interacción con la base de datos donde se almacenan las plantillas biométricas y, si aplica, interactuar con otros microservicios o sistemas externos (por ejemplo, un servicio de autenticación biométrica de terceros, o un microservicio de gestión de usuarios para validaciones adicionales). Es crucial que esta capa maneje la recuperación y el almacenamiento seguro de los datos biométricos.
Funcionalidad clave:
Acceso a Base de Datos: Persistencia y recuperación de las plantillas biométricas asociadas a documento, usuario y pais.
Integración con Servicios de Autenticación/Comparación de Vectores: Comunicación con servicios especializados para realizar comparaciones de vectores biométricos (si el microservicio no realiza esta lógica internamente, sino que delega en un tercero). Esto implicaría enviar el vector biométrico y recibir un resultado de comparación.
Gestión de Credenciales: Utiliza y gestiona las credenciales de acceso a la base de datos y a los servicios externos de forma segura (como se mencionó en la sección de Requisitos Técnicos, usando gestores de secretos).
Manejo de errores específicos de integración con servicios externos (ej., timeouts, respuestas inesperadas).
Esta estructura de capas proporciona una clara separación de preocupaciones, lo que facilita el desarrollo, las pruebas, el mantenimiento y la escalabilidad del Microservicio de Biometría.




. Capa de Lógica de Negocio (Capa de Dominio)
Descripción: Esta capa es el núcleo funcional y el "cerebro" del Microservicio de Biometría. Su propósito principal es encapsular y ejecutar la lógica central de negocio y las reglas específicas del dominio de la biometría. Recibe las solicitudes ya validadas por la Capa API y determina cómo procesarlas, aplicando las políticas y criterios definidos (como la unicidad del registro o la determinación del estado de la biometría). No se ocupa de la exposición de la API o la persistencia de datos directamente, sino que orquesta el flujo de negocio y coordina con otras capas para cumplir con la solicitud.
Funcionalidad Clave:
Implementa la lógica para verificarbiometria: Aquí se decide, por ejemplo, si se debe consultar la base de datos para validar la existencia o el estado de una biometría.
Aplica las reglas de negocio para registrarbiometria: Por ejemplo, asegura la unicidad del registro biométrico por usuario/documento antes de permitir el almacenamiento, evitando duplicados innecesarios.
Gestiona el procesamiento para consultarbiometriaPorusuario y consultarEstadobiometria: Determina qué datos son necesarios y cómo deben ser recuperados y procesados para generar la respuesta adecuada.
Controla la ejecución de la lógica para eliminarbiometria, asegurando que el proceso se realice de acuerdo con las políticas internas.
Coordina la interacción con la Capa de Acceso a Datos y Servicios Externos para realizar operaciones de lectura o escritura de datos, o para interactuar con servicios externos requeridos por la lógica de negocio.
