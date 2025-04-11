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

```
