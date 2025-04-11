# several_topics

```
¡Hola! Como Géminis, entiendo perfectamente tu necesidad de integrar Thymeleaf a tu proyecto Spring Boot con Java 17 para añadirle una capa de presentación. Aquí te dejo la sintaxis y un ejemplo práctico para que puedas empezar:

1. Agregar la dependencia de Thymeleaf en pom.xml (si usas Maven):

XML

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-thymeleaf</artifactId>
</dependency>
Si utilizas Gradle, la dependencia sería en tu archivo build.gradle:   

Gradle

implementation 'org.springframework.boot:spring-boot-starter-thymeleaf'
Asegúrate de sincronizar tu proyecto con los cambios en el archivo de dependencias.

2. Configuración básica (opcional pero recomendable):

Spring Boot autoconfigura Thymeleaf, por lo que en la mayoría de los casos no necesitas configuración adicional. Sin embargo, puedes personalizar algunas propiedades en tu archivo application.properties o application.yml. Aquí algunos ejemplos comunes:

application.properties:

Properties

spring.thymeleaf.cache=false # Desactivar la caché en desarrollo para ver los cambios inmediatamente
spring.thymeleaf.mode=HTML # Establecer el modo de plantilla a HTML5
spring.thymeleaf.prefix=classpath:/templates/ # Ubicación por defecto de las plantillas HTML
spring.thymeleaf.suffix=.html # Sufijo de los archivos HTML
spring.thymeleaf.encoding=UTF-8 # Codificación de caracteres
application.yml:

YAML

spring:
  thymeleaf:
    cache: false
    mode: HTML
    prefix: classpath:/templates/
    suffix: .html
    encoding: UTF-8
3. Estructura de directorios:

Por convención, Spring Boot buscará tus archivos HTML de Thymeleaf dentro de la carpeta src/main/resources/templates/. Crea esta carpeta en tu proyecto si aún no existe.

4. Ejemplo práctico: Controlador y plantillas Thymeleaf

Vamos a crear un controlador simple que maneja una petición GET para mostrar un formulario y una petición POST para procesar los datos del formulario.

Controlador Java (DemoController.java):

Java

package com.example.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
public class DemoController {

    @GetMapping("/formulario")
    public String mostrarFormulario(Model model) {
        model.addAttribute("usuario", new Usuario()); // Creamos un objeto vacío para el formulario
        return "formulario"; // Nombre del archivo HTML en la carpeta templates
    }

    @PostMapping("/procesarFormulario")
    public String procesarFormulario(@ModelAttribute Usuario usuario, Model model) {
        model.addAttribute("nombre", usuario.getNombre());
        model.addAttribute("email", usuario.getEmail());
        return "resultado"; // Nombre del archivo HTML para mostrar el resultado
    }
}
Clase Usuario.java (un simple POJO):

Java

package com.example.demo.model;

public class Usuario {
    private String nombre;
    private String email;

    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }
}
Plantilla Thymeleaf para el formulario (src/main/resources/templates/formulario.html):

HTML

<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>Formulario de Usuario</title>
</head>
<body>
    <h1>Ingrese sus datos</h1>
    <form action="/procesarFormulario" th:object="${usuario}" method="post">
        <div>
            <label for="nombre">Nombre:</label>
            <input type="text" id="nombre" th:field="*{nombre}" />
        </div>
        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" th:field="*{email}" />
        </div>
        <button type="submit">Enviar</button>
    </form>
</body>
</html>
Plantilla Thymeleaf para mostrar el resultado (src/main/resources/templates/resultado.html):

HTML

<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>Resultado del Formulario</title>
</head>
<body>
    <h1>Datos Recibidos</h1>
    <p th:text="'Nombre: ' + ${nombre}"></p>
    <p th:text="'Email: ' + ${email}"></p>
    <a href="/formulario">Volver al formulario</a>
</body>
</html>




//////////////////////////////////////////////////////////////////////
¡Entendido! Quieres integrar el widget de FacePhi en tu index.html (que ahora actúa como el formulario) y, al finalizar la captura exitosa (onExtractionFinish), enviar los datos del extractionResult.detail junto con el nombre y email que originalmente venían del formulario, a un endpoint POST en tu controlador Spring Boot.

Aquí te explico los pasos y las modificaciones que necesitas realizar:

1. Modifica tu index.html para Thymeleaf:

Necesitas agregar el namespace de Thymeleaf y adaptar las partes donde quieras mostrar los datos nombre y email que vienen del controlador. Aunque el template de FacePhi es principalmente JavaScript dinámico, puedes incluir elementos Thymeleaf donde sea necesario.

HTML

<!DOCTYPE html>
<html lang="en" xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=0.8, maximum-scale=1, user-scalable=no, shrink-to-fit=no">
    <meta name="description" content="FacePhi">

    <script>
        if (window.location.href.includes("127.0.0.1")) {
            window.location.href = window.location.href.replace("127.0.0.1", "localhost");
        }
    </script>

    <script type="module" th:src="@{/facephi/main.js}"></script>
</head>
<body class="d-flex flex-column justify-content-between align-items-stretch min-h-100 bg-light">
    <header class="bg-dark">
        <div class="container p-3 d-flex align-items-center justify-content-between">
            <a href="https://www.facephi.com/" title="FacePhi" target="_blank">
                <img th:src="@{/facephi/img/facephi_logo.svg}" alt="FacePhi-Logo" height="30" />
            </a>
        </div>
    </header>
    <main class="flex-grow-1 d-flex align-items-stretch">
        <div class="container p-3">
            <div class="row h-100">
                <div class="col-12 col-md-9" style="min-height: 550px;">
                    <div id="fPhiWidgetContainer" style="height: 100%;"></div>
                    <div id="widgetEventResult" style="position: absolute; top: 0;"></div>
                </div>

                <div class="col-12 col-md-3 mt-3 mt-md-0">
                    <div>Selphi Web Widget Demo</div>

                    <div class="my-3">
                        <button type="button" id="btnStartCapture" class="btn btn-primary btn-block">Start capture</button>
                        <button type="button" id="btnStopCapture" class="btn btn-danger btn-block">Stop capture</button>
                    </div>

                    <div class="form-group">
                        <label for="cameraResolution">Camera resolution</label>
                        <select id="cameraResolution" class="form-control">
                            <option data-width="640" data-height="480">640x480</option>
                            <option data-width="800" data-height="600">800x600</option>
                            <option data-width="1024" data-height="768">1024x768</option>
                            <option data-width="1280" data-height="720" selected>1280x720 (720p)</option>
                            <option data-width="1920" data-height="1080">1920x1080 (1080p)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="cameraType">Camera type</label>
                        <select id="cameraType" class="form-control">
                            <option value="Front" selected>Front</option>
                            <option value="Back">Back</option>
                        </select>
                    </div>

                    <div class="form-group form-check m-0">
                        <input id="interactive" type="checkbox" class="form-check-input" checked />
                        <label for="interactive" class="form-check-label">Interactive</label>
                    </div>

                    <div class="form-group form-check m-0">
                        <input id="stabilizationStage" type="checkbox" class="form-check-input" checked />
                        <label for="stabilizationStage" class="form-check-label">Stabilization stage</label>
                    </div>

                    <div class="form-group form-check m-0">
                        <input id="cameraSwitchButton" type="checkbox" class="form-check-input" />
                        <label for="cameraSwitchButton" class="form-check-label">Camera Switch Button</label>
                    </div>

                    <div class="form-group form-check m-0">
                        <input id="faceTracking" type="checkbox" class="form-check-input" />
                        <label for="faceTracking" class="form-check-label">Face tracking</label>
                    </div>

                    <div class="form-group form-check m-0">
                        <input id="showLog" type="checkbox" class="form-check-input" />
                        <label for="showLog" class="form-check-label">Show extended log</label>
                    </div>
                    <div class="form-group mt-2">
                        <div>Widget Version: <span id="widgetVersion"></span></div>
                        <div th:if="${nombre}">Nombre: <span th:text="${nombre}"></span></div>
                        <div th:if="${email}">Email: <span th:text="${email}"></span></div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="bg-dark text-white">
        <div class="container px-3 d-flex justify-content-between align-items-center">
            <small>&copy; 2025 @FacePhi. All rights reserved.</small>
            <div class="small font-weight-bold px-3 py-2 bg-success">HTML Static + Bootstrap</div>
        </div>
    </footer>
</body>
</html>
Cambios en el HTML:

Se agregó el namespace xmlns:th="http://www.thymeleaf.org" a la etiqueta <html>.
Se utilizaron los atributos th:src="@{/facephi/main.js}" y th:src="@{/facephi/img/facephi_logo.svg}" para que Thymeleaf genere las rutas correctas a tus recursos estáticos.
Se agregaron divs para mostrar el nombre y el email si estos atributos están presentes en el modelo (th:if="${nombre}" y th:if="${email}").
2. Modifica la función onExtractionFinish en main.js para hacer un POST:

Dentro de la función onExtractionFinish, necesitas construir un objeto con los datos del extractionResult.detail, el nombre, y el email, y luego realizar una petición POST a tu controlador Spring Boot.

JavaScript

function onExtractionFinish(extractionResult) {
    console.warn("[Selphi] onExtractionFinish");
    console.log(extractionResult.detail);
    console.log("Mi template");
    console.log(extractionResult.detail.template);

    const dataToSend = {
        nombre: /* Aquí debes obtener el valor del nombre (si está en el DOM o lo pasas de alguna manera) */ document.getElementById('nombre')?.value, // Ejemplo si tienes un input con id 'nombre'
        email: /* Aquí debes obtener el valor del email (si está en el DOM o lo pasas de alguna manera) */ document.getElementById('email')?.value,   // Ejemplo si tienes un input con id 'email'
        template: extractionResult.detail.template,
        bestImage: JSON.stringify(extractionResult.detail.bestImage), // Convertir a string si es necesario
        bestImageCropped: JSON.stringify(extractionResult.detail.bestImageCropped),
        images: JSON.stringify(extractionResult.detail.images),
        timeStamp: JSON.stringify(extractionResult.detail.timeStamp),
        templateRaw: extractionResult.detail.templateRaw,
        livenessMoveFails: extractionResult.detail.livenessMoveFails,
        livenessMoveHistory: JSON.stringify(extractionResult.detail.livenessMoveHistory),
        livenessMoveStabilizedHistory: JSON.stringify(extractionResult.detail.livenessMoveStabilizedHistory),
        livenessMoveStabilizedStatus: extractionResult.detail.livenessMoveStabilizedStatus,
        bestImageTokenized: extractionResult.detail.bestImageTokenized
    };

    fetch('/procesarCaptura', { // Define la URL de tu endpoint POST en el controlador
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json()) // O response.text() dependiendo de la respuesta del servidor
    .then(data => {
        console.log('Respuesta del servidor:', data);
        document.getElementById("widgetEventResult").innerText = 'Success! Datos enviados al servidor';
        setDemoState(false);
    })
    .catch(error => {
        console.error('Error al enviar datos al servidor:', error);
        document.getElementById("widgetEventResult").innerText = 'Error al enviar datos';
        setDemoState(false);
    });
}
Puntos importantes en main.js:

Obtención de nombre y email: Necesitas determinar cómo vas a obtener los valores de nombre y email en este punto. Si los tenías en un formulario HTML antes de iniciar la captura, podrías intentar acceder a sus valores desde el DOM usando document.getElementById('nombre')?.value y document.getElementById('email')?.value. Asegúrate de que los IDs coincidan con los de tus elementos HTML (si los mantienes en el index.html). Si la lógica es diferente, ajusta esta parte según tu flujo.
dataToSend: Se crea un objeto JavaScript con los datos del extractionResult.detail y los campos nombre y email.
fetch('/procesarCaptura', ...): Se utiliza la API fetch para realizar una petición POST a la URL /procesarCaptura (puedes elegir la URL que desees para tu endpoint).
headers: Se establece el Content-Type a application/json para indicar que estás enviando datos JSON.
body: El objeto dataToSend se convierte a una cadena JSON con JSON.stringify().
.then() y .catch(): Se manejan las respuestas exitosas y los errores de la petición.
3. Crea un endpoint POST en tu controlador Spring Boot:

Necesitas crear un método en tu DemoController (o en otro controlador que prefieras) para recibir la petición POST y el objeto ExtractionResultDetail.

Java

package com.example.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

@Controller
public class DemoController {

    @GetMapping("/formulario") // O la ruta que uses para mostrar el index.html
    public String mostrarFormulario(Model model) {
        model.addAttribute("usuario", new Usuario());
        return "index"; // Ahora tu index.html es el formulario
    }

    @PostMapping("/procesarCaptura")
    public String procesarCaptura(@RequestBody ExtractionResultDetail data, Model model) {
        System.out.println("Datos recibidos del widget:");
        System.out.println("Nombre: " + data.getNombre()); // Asegúrate de tener getters y setters en ExtractionResultDetail
        System.out.println("Email: " + data.getCorreo());
        System.out.println("Template: " + data.getTemplate());
        System.out.println("Best Image Tokenized: " + data.getBestImageTokenized());

        // Aquí puedes procesar los datos recibidos
        model.addAttribute("resultadoTemplate", data.getTemplate());
        model.addAttribute("resultadoToken", data.getBestImageTokenized());
        return "resultado_captura"; // Crea una página para mostrar el resultado
    }

    @GetMapping("/sendData")
    public String mostrarResultado(Model model) {
        // ... (tu lógica para mostrar la página de resultado si es necesario)
        return "resultado_captura";
    }
}
Clase ExtractionResultDetail.java (Asegúrate de tenerla con getters y setters):

Java

public class ExtractionResultDetail {
    private String nombre;
    private String correo;
    private String template;
    private Object bestImage;
    private Object bestImageCropped;
    private Object[] images;
    private Object[] timeStamp;
    private String templateRaw;
    private int livenessMoveFails;
    private Object[] livenessMoveHistory;
    private int[] livenessMoveStabilizedHistory;
    private int livenessMoveStabilizedStatus;
    private String bestImageTokenized;

    // Getters y setters para todos los campos
    public String getNombre() {
        return nombre;
    }

    public void setNombre(String nombre) {
        this.nombre = nombre;
    }

    public String getCorreo() {
        return correo;
    }

    public void setCorreo(String correo) {
        this.correo = correo;
    }

    // ... (Getters y setters para los demás campos)
}
Explicación del Controlador:

@PostMapping("/procesarCaptura"): Mapea las peticiones POST a la URL /procesarCaptura.
@RequestBody ExtractionResultDetail data: Indica que el cuerpo de la petición POST se debe convertir en un objeto ExtractionResultDetail. Es crucial que los nombres de los campos en tu objeto JavaScript (dataToSend) coincidan con los nombres de los atributos en tu clase ExtractionResultDetail de Java.
El método procesarCaptura recibe el objeto ExtractionResultDetail y el Model para pasar datos a una vista de resultado (resultado_captura.html - debes crear este archivo Thymeleaf).
4. (Opcional) Crea una página de resultado (resultado_captura.html):

Puedes crear un archivo src/main/resources/templates/resultado_captura.html para mostrar los datos recibidos:

HTML

<!DOCTYPE html>
<html xmlns:th="http://www.thymeleaf.org">
<head>
    <title>Resultado de la Captura</title>
</head>
<body>
    <h1>Datos Recibidos:</h1>
    <div th:if="${resultadoTemplate}">
        <p>Template: <span th:text="${resultadoTemplate}"></span></p>
    </div>
    <div th:if="${resultadoToken}">
        <p>Best Image Tokenized: <span th:text="${resultadoToken}"></span></p>
    </div>
    <a th:href="@{/formulario}">Volver al formulario</a>
</body>
</html>


function onExtractionFinish(extractionResult) {
    console.warn("[Selphi] onExtractionFinish");
    console.log(extractionResult.detail);
    console.log("Mi template");
    console.log(extractionResult.detail.template);

    const nombre = document.querySelector('#nombre')?.textContent; // Obtén el nombre del span
    const email = document.querySelector('#email')?.textContent;   // Obtén el email del span

    const dataToSend = {
        nombre: nombre,
        email: email,
        template: extractionResult.detail.template,
        bestImage: JSON.stringify(extractionResult.detail.bestImage),
        bestImageCropped: JSON.stringify(extractionResult.detail.bestImageCropped),
        images: JSON.stringify(extractionResult.detail.images),
        timeStamp: JSON.stringify(extractionResult.detail.timeStamp),
        templateRaw: extractionResult.detail.templateRaw,
        livenessMoveFails: extractionResult.detail.livenessMoveFails,
        livenessMoveHistory: JSON.stringify(extractionResult.detail.livenessMoveHistory),
        livenessMoveStabilizedHistory: JSON.stringify(extractionResult.detail.livenessMoveStabilizedHistory),
        livenessMoveStabilizedStatus: extractionResult.detail.livenessMoveStabilizedStatus,
        bestImageTokenized: extractionResult.detail.bestImageTokenized
    };

    fetch('/procesarCaptura', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        document.getElementById("widgetEventResult").innerText = 'Success! Datos enviados al servidor';
        setDemoState(false);
    })
    .catch(error => {
        console.error('Error al enviar datos al servidor:', error);
        document.getElementById("widgetEventResult").innerText = 'Error al enviar datos';
        setDemoState(false);
    });
}

```
