# several_topics

```
package com.example.demo.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;

import com.example.demo.model.CapturaRequest;

@Controller
public class DemoController {

    @GetMapping("/index")
    public String mostrarIndex() {
        return "index";
    }

    @PostMapping("/procesarCaptura")
    @ResponseBody
    public ResponseEntity<CapturaResponse> procesarCaptura(@RequestBody CapturaRequest capturaRequest) {
        System.out.println("Datos recibidos del widget:");
        System.out.println("Username: " + capturaRequest.getUsername());
        System.out.println("Country ID: " + capturaRequest.getCountryId());
        System.out.println("Template: " + capturaRequest.getTemplate());
        System.out.println("Best Image Tokenized: " + capturaRequest.getBestImageTokenized());

        CapturaResponse response = new CapturaResponse();
        response.setUsernameResultado(capturaRequest.getUsername());
        response.setCountryIdResultado(capturaRequest.getCountryId());
        response.setResultadoTemplate(capturaRequest.getTemplate());
        response.setResultadoToken(capturaRequest.getBestImageTokenized());

        return new ResponseEntity<>(response, HttpStatus.OK);
    }

    // Clase para la respuesta JSON
    static class CapturaResponse {
        private String usernameResultado;
        private String countryIdResultado;
        private String resultadoTemplate;
        private String resultadoToken;

        // Getters y setters
        public String getUsernameResultado() {
            return usernameResultado;
        }

        public void setUsernameResultado(String usernameResultado) {
            this.usernameResultado = usernameResultado;
        }

        public String getCountryIdResultado() {
            return countryIdResultado;
        }

        public void setCountryIdResultado(String countryIdResultado) {
            this.countryIdResultado = countryIdResultado;
        }

        public String getResultadoTemplate() {
            return resultadoTemplate;
        }

        public void setResultadoTemplate(String resultadoTemplate) {
            this.resultadoTemplate = resultadoTemplate;
        }

        public String getResultadoToken() {
            return resultadoToken;
        }

        public void setResultadoToken(String resultadoToken) {
            this.resultadoToken = resultadoToken;
        }
    }
}
Cambios en el Controlador:

@ResponseBody: Esta anotación se agrega al método procesarCaptura. Indica que el valor de retorno del método (en este caso, un objeto ResponseEntity) debe ser serializado directamente en el cuerpo de la respuesta HTTP. Spring Boot automáticamente lo convertirá a JSON gracias a las dependencias como Jackson.
ResponseEntity<CapturaResponse>: Se utiliza ResponseEntity para tener control sobre el código de estado HTTP (que sigue siendo HttpStatus.OK) y el cuerpo de la respuesta (un objeto CapturaResponse).
CapturaResponse class: Se crea una clase interna estática para representar la estructura del JSON que se enviará como respuesta. Contiene los mismos campos que quieres mostrar en la vista. Se proporcionan getters y setters para que Jackson pueda serializar el objeto a JSON.
2. Modifica tu JavaScript en index.html para procesar la respuesta JSON:

Ahora, en el bloque .then() de tu fetch en enviarDatosCaptura (dentro de index.html), necesitas parsear la respuesta como JSON y acceder a los campos correspondientes para actualizar la vista.

JavaScript

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
    .then(response => response.json()) // Parse the response as JSON
    .then(data => {
        console.log('Respuesta del servidor (JSON):', data);
        document.getElementById("widgetEventResult").innerText = 'Success! Datos enviados y recibidos';
        // Actualiza la vista con los datos recibidos del JSON
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
```
