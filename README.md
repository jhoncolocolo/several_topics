# several_topics

```
. Modifica tu DTO/Modelo (Ejemplo: CapturaRequest.java):

Asumo que tenías una clase como Usuario.java o algo similar para recibir el nombre y el correo. Ahora, esa clase debería tener los campos username y countryId. Si no la tienes, créala.

Java

package com.example.demo.model;

public class CapturaRequest {
    private String username;
    private String countryId;
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
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getCountryId() {
        return countryId;
    }

    public void setCountryId(String countryId) {
        this.countryId = countryId;
    }

    // Getters y setters para los demás campos (template, bestImage, etc.)
    public String getTemplate() {
        return template;
    }

    public void setTemplate(String template) {
        this.template = template;
    }

    // ... (Getters y setters para los demás campos)
}
2. Modifica tu DemoController:

Java

package com.example.demo.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.example.demo.model.CapturaRequest; // Asegúrate de importar tu DTO/Modelo

@Controller
public class DemoController {

    @GetMapping("/index")
    public String mostrarIndex() {
        return "index";
    }

    @PostMapping("/procesarCaptura")
    public String procesarCaptura(@RequestBody CapturaRequest capturaRequest, Model model) {
        System.out.println("Datos recibidos del widget:");
        System.out.println("Username: " + capturaRequest.getUsername());
        System.out.println("Country ID: " + capturaRequest.getCountryId());
        System.out.println("Template: " + capturaRequest.getTemplate());
        System.out.println("Best Image Tokenized: " + capturaRequest.getBestImageTokenized());

        model.addAttribute("usernameResultado", capturaRequest.getUsername());
        model.addAttribute("countryIdResultado", capturaRequest.getCountryId());
        model.addAttribute("resultadoTemplate", capturaRequest.getTemplate());
        model.addAttribute("resultadoToken", capturaRequest.getBestImageTokenized());
        return "index"; // Volvemos a la misma página para mostrar los resultados
    }

    @GetMapping("/resultado") // Puedes eliminar este endpoint
    public String mostrarResultado(Model model) {
        return "index";
    }
}
Cambios en el Controlador:

@PostMapping("/procesarCaptura"): Ahora recibe un objeto CapturaRequest como @RequestBody. Spring Boot intentará mapear el JSON enviado desde el cliente a esta clase.
Los valores de username y countryId se obtienen del objeto capturaRequest.
Estos mismos valores (capturaRequest.getUsername() y capturaRequest.getCountryId()) se agregan al modelo para que puedan ser mostrados en la vista index.html.
3. Modifica tu src/main/resources/templates/index.html (Asegúrate de que los IDs coincidan):

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

        function enviarDatosCaptura(extractionResultDetail) {
            const username = document.getElementById('username').value;
            const countryId = document.getElementById('countryId').value;

            const dataToSend = {
                username: username,
                countryId: countryId,
                template: extractionResultDetail.template,
                bestImage: JSON.stringify(extractionResultDetail.bestImage),
                bestImageCropped: JSON.stringify(extractionResultDetail.bestImageCropped),
                images: JSON.stringify(extractionResultDetail.images),
                timeStamp: JSON.stringify(extractionResultDetail.timeStamp),
                templateRaw: extractionResultDetail.templateRaw,
                livenessMoveFails: extractionResultDetail.livenessMoveFails,
                livenessMoveHistory: JSON.stringify(extractionResultDetail.livenessMoveHistory),
                livenessMoveStabilizedHistory: JSON.stringify(extractionResultDetail.livenessMoveStabilizedHistory),
                livenessMoveStabilizedStatus: extractionResultDetail.livenessMoveStabilizedStatus,
                bestImageTokenized: extractionResultDetail.bestImageTokenized
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
                document.getElementById("widgetEventResult").innerText = 'Success! Datos enviados y recibidos';
                // Actualiza la vista con los datos recibidos
                document.getElementById("resultadoUsername").innerText = data.usernameResultado;
                document.getElementById("resultadoCountryId").innerText = data.countryIdResultado;
                document.getElementById("resultadoTemplate").innerText = data.resultadoTemplate;
                document.getElementById("resultadoToken").innerText = data.resultadoToken;
                setDemoState(false);
            })
            .catch(error => {
                console.error('Error al enviar datos al servidor:', error);
                document.getElementById("widgetEventResult").innerText = 'Error al enviar datos';
                setDemoState(false);
            });
        }

        function onExtractionFinish(extractionResult) {
            console.warn("[Selphi] onExtractionFinish");
            console.log(extractionResult.detail);
            console.log("Mi template");
            console.log(extractionResult.detail.template);

            enviarDatosCaptura(extractionResult.detail);
        }

        // ... (El resto de tu código JavaScript del widget)
    </script>

    <script type="module" th:src="@{/facephi/main.js}"></script>
    <link rel="stylesheet" th:href="@{/facephi/styles.css}">
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

                    <div class="form-group">
                        <label for="username">User Name:</label>
                        <input type="text" id="username" class="form-control" />
                    </div>

                    <div class="form-group">
                        <label for="countryId">País:</label>
                        <select id="countryId" class="form-control">
                            <option value="CO">Colombia</option>
                            <option value="BR">Brasil</option>
                            <option value="PA">Panamá</option>
                            <option value="CR">Costa Rica</option>
                            <option value="HN">Honduras</option>
                        </select>
                    </div>

                    <div class="my-3">
                        <button type="button" id="btnStartCapture" class="btn btn-primary btn-block">Start capture</button>
                        <button type="button" id="btnStopCapture" class="btn btn-danger btn-block">Stop capture</button>
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
                        <div th:if="${usernameResultado}">Username Recibido: <span id="resultadoUsername" th:text="${usernameResultado}"></span></div>
                        <div th:if="${countryIdResultado}">País Recibido: <span id="resultadoCountryId" th:text="${countryIdResultado}"></span></div>
                        <div th:if="${resultadoTemplate}">Template Recibido: <span id="resultadoTemplate" th:text="${resultadoTemplate}"></span></div>
                        <div th:if="${resultadoToken}">Token Recibido: <span id="resultadoToken" th:text="${resultadoToken}"></span></div>
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
Cambios en index.html (son los mismos de antes, pero los recalco):

Asegúrate de que los campos del formulario tengan los IDs username y countryId:
HTML

<input type="text" id="username" class="form-control" />
<select id="countryId" class="form-control">
    </select>
Asegúrate de que los elementos donde mostrarás la respuesta del servidor tengan los IDs resultadoUsername y resultadoCountryId:
HTML

<div th:if="${usernameResultado}">Username Recibido: <span id="resultadoUsername" th:text="${usernameResultado}"></span></div>
<div th:if="${countryIdResultado}">País Recibido: <span id="resultadoCountryId" th:text="${countryIdResultado}"></span></div>
Puntos Clave:

El JavaScript en main.js ahora tomará los valores del username y countryId directamente de los campos del formulario en el index.html al momento de enviar la petición POST.
El controlador recibe todos los datos en el objeto CapturaRequest.
El controlador devuelve los valores de username y countryId (junto con los otros datos) en el modelo.
El index.html utiliza Thymeleaf (th:if y th:text) para mostrar estos valores de respuesta.
Con esta configuración, deberías tener un flujo completo en un solo archivo index.html donde se captura la información del usuario, se realiza la biometría, y se muestra la respuesta del servidor, todo en la misma página. ¡Espero que funcione perfectamente!
```
