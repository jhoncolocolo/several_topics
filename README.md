```
Optimización de Costos por Verificación de Identidad con Biometría Facial
Contexto Actual de Verificación de Identidad
Actualmente, el proceso de verificación de identidad con el "Verificador de Identidades" implica dos escenarios principales con costos muy diferentes:

Primer Registro Biométrico (Costoso): Cuando una persona realiza una transacción por primera vez y aún no tiene su biometría facial registrada, se le solicita tanto su cédula de identidad (anverso y reverso) como un vector biométrico (una "selfie" o foto en tiempo real). Esta información se envía al "Verificador de Identidades". Una vez validada, la plantilla biométrica (el vector procesado de la selfie) se guarda en nuestra base de datos, específicamente en Azure Cosmos DB. Este proceso inicial es el más costoso para nosotros.

Verificación sin Biometría Registrada (El Más Costoso): Si un usuario necesita verificar su identidad y aún no tiene su plantilla biométrica guardada en Cosmos DB, la única alternativa es recurrir a OTPs (contraseñas de un solo uso) enviadas por correo electrónico o mensaje de texto al celular. Este método es, con diferencia, el más caro por cada transacción, ya que se incurre en un costo recurrente por cada OTP generado y enviado.

En contraste, cuando la plantilla biométrica ya está guardada en Cosmos DB, las verificaciones posteriores son mucho más económicas:

Verificación con Biometría Registrada (Más Barata): Una vez que la plantilla biométrica de una persona está en Cosmos DB, las futuras verificaciones son simples y baratas. Solo se toma una nueva selfie (vector biométrico actual) al usuario. Luego, nuestro sistema envía por vía POST el número de cédula y el vector biométrico guardado en Cosmos DB al "Verificador de Identidades". El proveedor compara estos dos vectores para confirmar la identidad, resultando en un costo significativamente menor.
El Objetivo: Eliminar los Costos de OTPs y Optimizar
Nuestro objetivo es reducir drásticamente los costos operativos asociados a la verificación de identidad. Al incentivar y asegurar que los usuarios registren su plantilla biométrica facial (selfie y cédula) la primera vez, lograremos dos cosas fundamentales:

Eliminar los Costos de OTPs: Evitaremos la necesidad de usar el costoso método de OTPs para las verificaciones de usuarios no registrados.
Reducir el Costo por Transacción: Tras el registro inicial, todas las futuras verificaciones se realizarán utilizando el método biométrico de bajo costo (comparación de vectores), aprovechando la capacidad de Azure Cosmos DB para almacenar y acceder a las plantillas de manera eficiente.
En resumen, la biometría facial nos permitirá convertir un gasto recurrente y elevado (OTPs) en una inversión inicial (primer registro) que desbloquea verificaciones futuras mucho más baratas y eficientes.

Diagrama de Flujo: Proceso de Verificación de Identidad y Costos
Fragmento de código

graph TD
    subgraph Usuario
        A[Inicia Transacción] --> B{Plantilla Biométrica Registrada?};
    end

    B -- NO --> C[Requiere Verificación];
    B -- SÍ --> I[Toma Selfie (Vector Biométrico Actual)];

    subgraph Proceso SIN Biometría Registrada (Costo Alto)
        C --> D[Método OTP];
        D --> E[Envía OTP a Correo/Celular];
        E --> F[Verificación de Identidad por OTP];
        F --> G[Costo: ALTO por Transacción];
    end

    subgraph Proceso CON Biometría Registrada (Costo Bajo)
        I --> J[Envía # Cédula + Vector de Cosmos DB + Vector Actual];
        J --> K[Verificador de Identidades (Compara Vectores)];
        K --> L[Verificación de Identidad Exitosa];
        L --> M[Costo: BAJO por Transacción];
    end

    subgraph Primer Registro Biométrico (Costo Único Inicial)
        H[Usuario Envía Cédula + Selfie (Vector Biométrico)] --> N[Validación y Procesamiento];
        N --> O[Guarda Plantilla Biométrica en Azure Cosmos DB];
        O --> P[Costo: ALTO ÚNICO (por primera vez)];
    end

    style G fill:#f9f,stroke:#333,stroke-width:2px;
    style M fill:#9f9,stroke:#333,stroke-width:2px;
    style P fill:#ff9,stroke:#333,stroke-width:2px;

    B -- "NO, Primera Vez" --> H;
Explicación del Diagrama:

Ruta de Primer Registro (Costo Único Inicial): Cuando un usuario no tiene plantilla biométrica, se sigue el camino Usuario -> Requiere Verificación -> Usuario Envía Cédula + Selfie. Esto lleva a la Validación y Procesamiento y se Guarda Plantilla Biométrica en Azure Cosmos DB. Este es el Costo ALTO ÚNICO de la primera vez.
Ruta sin Biometría Registrada (Costo ALTO por Transacción): Si la plantilla no está registrada y no es el primer registro (ej., el usuario no completó el primer registro), se recurre al Método OTP, que implica Envía OTP a Correo/Celular y Verificación de Identidad por OTP. Esto resulta en un Costo ALTO por Transacción.
Ruta con Biometría Registrada (Costo BAJO por Transacción): Una vez que la Plantilla Biométrica está Registrada (sí), el usuario se Toma Selfie (Vector Biométrico Actual). Nuestro sistema Envía # Cédula + Vector de Cosmos DB + Vector Actual al Verificador de Identidades, que Compara Vectores para una Verificación de Identidad Exitosa. Esto genera un Costo BAJO por Transacción, que es el escenario deseado.
Este diagrama y explicación deberían dar una visión clara del problema de costos actual y cómo la biometría facial, apoyada en Cosmos DB, es la solución clave para optimizar.
```
