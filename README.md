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


import org.springframework.http.HttpEntity;
import org.springframework.http.ResponseEntity;
import org.springframework.web.client.RestTemplate;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.HttpHeaders; // Asumiendo que HttpHeaders es necesario
import java.time.Duration;

// Clase principal donde se encuentra el método original
public class MyService {

    // Estas variables se asumen definidas en la clase o inyectadas
    private long connectionTimeout = 5000; // Ejemplo de valor
    private long readTimeout = 10000;      // Ejemplo de valor
    private String uri = "http://example.com/api"; // Ejemplo de URI
    private HttpHeaders headers = new HttpHeaders(); // Ejemplo de headers

    /**
     * Clase interna estática que encapsula todos los parámetros para la solicitud.
     * Utiliza el patrón Builder para una construcción flexible y legible.
     */
    public static class RequestParameters {
        private String action;
        private String modulo;
        private Object requestBody; // Renombrado de 'request' para evitar conflictos
        private Class<?> responseType; // Usamos Class<?> para ser más general
        private String timeoutConnections;
        private String tiemposLectura;
        private String transactionId;
        private String pais;

        // Constructor privado para ser usado solo por el Builder
        private RequestParameters(Builder builder) {
            this.action = builder.action;
            this.modulo = builder.modulo;
            this.requestBody = builder.requestBody;
            this.responseType = builder.responseType;
            this.timeoutConnections = builder.timeoutConnections;
            this.tiemposLectura = builder.tiemposLectura;
            this.transactionId = builder.transactionId;
            this.pais = builder.pais;
        }

        // Getters para acceder a los parámetros
        public String getAction() { return action; }
        public String getModulo() { return modulo; }
        public Object getRequestBody() { return requestBody; }
        public Class<?> getResponseType() { return responseType; }
        public String getTimeoutConnections() { return timeoutConnections; }
        public String getTiemposLectura() { return tiemposLectura; }
        public String getTransactionId() { return transactionId; }
        public String getPais() { return pais; }

        /**
         * Builder para construir instancias de RequestParameters.
         */
        public static class Builder {
            private String action;
            private String modulo;
            private Object requestBody;
            private Class<?> responseType;
            private String timeoutConnections;
            private String tiemposLectura;
            private String transactionId;
            private String pais;

            // Métodos 'with' para cada parámetro, retornando el propio Builder para encadenamiento
            public Builder withAction(String action) {
                this.action = action;
                return this;
            }

            public Builder withModulo(String modulo) {
                this.modulo = modulo;
                return this;
            }

            public Builder withRequestBody(Object requestBody) {
                this.requestBody = requestBody;
                return this;
            }

            public Builder withResponseType(Class<?> responseType) {
                this.responseType = responseType;
                return this;
            }

            public Builder withTimeoutConnections(String timeoutConnections) {
                this.timeoutConnections = timeoutConnections;
                return this;
            }

            public Builder withTiemposLectura(String tiemposLectura) {
                this.tiemposLectura = tiemposLectura;
                return this;
            }

            public Builder withTransactionId(String transactionId) {
                this.transactionId = transactionId;
                return this;
            }

            public Builder withPais(String pais) {
                this.pais = pais;
                return this;
            }

            /**
             * Construye y retorna una nueva instancia de RequestParameters.
             * @return Una instancia de RequestParameters.
             */
            public RequestParameters build() {
                return new RequestParameters(this);
            }
        }
    }

    /**
     * Método refactorizado para ejecutar una solicitud POST con RestTemplate,
     * utilizando un objeto RequestParameters que encapsula todos los detalles de la solicitud.
     *
     * @param params El objeto RequestParameters que contiene todos los datos necesarios para la solicitud.
     * @param <T> El tipo de la respuesta esperada.
     * @return Un ResponseEntity que contiene la respuesta del servicio.
     */
    public <T> ResponseEntity<T> ejecutaRestTemplatePost(RequestParameters params) {
        // otras instrucciones.. (manteniendo el contexto del código original)

        // Se utilizan los getters del objeto params para acceder a los valores
        HttpEntity<Object> entityReq = new HttpEntity<>(params.getRequestBody(), headers);

        final RestTemplate restTemplate =
                new RestTemplateBuilder()
                        .setConnectTimeout(Duration.ofMillis(this.connectionTimeout))
                        .setReadTimeout(Duration.ofMillis(this.readTimeout))
                        .build();

        // Se utilizan los getters del objeto params para acceder a los valores
        return (ResponseEntity<T>) restTemplate.postForEntity(uri, entityReq, params.getResponseType());
    }

    // --- Aplicación / Ejemplo de uso ---
    public static void main(String[] args) {
        MyService service = new MyService();

        // 1. Crear los parámetros usando el Builder
        RequestParameters requestParams = new RequestParameters.Builder()
                .withAction("someAction")
                .withModulo("someModule")
                .withRequestBody(new MyRequestBody("data1", 123)) // Objeto de ejemplo para el cuerpo de la solicitud
                .withResponseType(String.class) // Tipo de respuesta esperado
                .withTimeoutConnections("5000")
                .withTiemposLectura("10000")
                .withTransactionId("TXN12345")
                .withPais("COL")
                .build();

        // 2. Llamar al método refactorizado con el objeto RequestParameters
        try {
            ResponseEntity<String> response = service.ejecutaRestTemplatePost(requestParams);
            System.out.println("Respuesta del servicio: " + response.getBody());
            System.out.println("Código de estado: " + response.getStatusCode());
        } catch (Exception e) {
            System.err.println("Error al ejecutar la solicitud: " + e.getMessage());
        }

        // Otro ejemplo con diferentes parámetros
        RequestParameters anotherRequestParams = new RequestParameters.Builder()
                .withAction("anotherAction")
                .withModulo("anotherModule")
                .withRequestBody(new AnotherRequestBody(true, "test"))
                .withResponseType(Integer.class)
                .withTransactionId("TXN67890")
                .withPais("MEX")
                // No es necesario pasar todos los parámetros si tienen valores por defecto o no son obligatorios
                .build();

        try {
            ResponseEntity<Integer> anotherResponse = service.ejecutaRestTemplatePost(anotherRequestParams);
            System.out.println("Otra respuesta del servicio: " + anotherResponse.getBody());
            System.out.println("Otro código de estado: " + anotherResponse.getStatusCode());
        } catch (Exception e) {
            System.err.println("Error al ejecutar la segunda solicitud: " + e.getMessage());
        }
    }

    // Clases de ejemplo para el cuerpo de la solicitud
    static class MyRequestBody {
        String field1;
        int field2;

        public MyRequestBody(String field1, int field2) {
            this.field1 = field1;
            this.field2 = field2;
        }

        @Override
        public String toString() {
            return "MyRequestBody{" +
                   "field1='" + field1 + '\'' +
                   ", field2=" + field2 +
                   '}';
        }
    }

    static class AnotherRequestBody {
        boolean status;
        String message;

        public AnotherRequestBody(boolean status, String message) {
            this.status = status;
            this.message = message;
        }

        @Override
        public String toString() {
            return "AnotherRequestBody{" +
                   "status=" + status +
                   ", message='" + message + '\'' +
                   '}';
        }
    }
}


package com.example.myservice.request;

package com.example.myservice.request;

public class RequestParameters<T> {
    private final String action;
    private final String modulo;
    private final Object requestBody;
    private final Class<T> responseType;
    private final String timeoutConnections;
    private final String tiemposLectura;
    private final String transactionId;
    private final String pais;

    private RequestParameters(Builder<T> builder) {
        this.action = builder.action;
        this.modulo = builder.modulo;
        this.requestBody = builder.requestBody;
        this.responseType = builder.responseType;
        this.timeoutConnections = builder.timeoutConnections;
        this.tiemposLectura = builder.tiemposLectura;
        this.transactionId = builder.transactionId;
        this.pais = builder.pais;
    }

    public String getAction() { return action; }
    public String getModulo() { return modulo; }
    public Object getRequestBody() { return requestBody; }
    public Class<T> getResponseType() { return responseType; }
    public String getTimeoutConnections() { return timeoutConnections; }
    public String getTiemposLectura() { return tiemposLectura; }
    public String getTransactionId() { return transactionId; }
    public String getPais() { return pais; }

    public static class Builder<T> {
        private String action;
        private String modulo;
        private Object requestBody;
        private Class<T> responseType;
        private String timeoutConnections;
        private String tiemposLectura;
        private String transactionId;
        private String pais;

        public Builder<T> withAction(String action) {
            this.action = action;
            return this;
        }

        public Builder<T> withModulo(String modulo) {
            this.modulo = modulo;
            return this;
        }

        public Builder<T> withRequestBody(Object requestBody) {
            this.requestBody = requestBody;
            return this;
        }

        public Builder<T> withResponseType(Class<T> responseType) {
            this.responseType = responseType;
            return this;
        }

        public Builder<T> withTimeoutConnections(String timeoutConnections) {
            this.timeoutConnections = timeoutConnections;
            return this;
        }

        public Builder<T> withTiemposLectura(String tiemposLectura) {
            this.tiemposLectura = tiemposLectura;
            return this;
        }

        public Builder<T> withTransactionId(String transactionId) {
            this.transactionId = transactionId;
            return this;
        }

        public Builder<T> withPais(String pais) {
            this.pais = pais;
            return this;
        }

        public RequestParameters<T> build() {
            return new RequestParameters<>(this);
        }
    }
}


```
