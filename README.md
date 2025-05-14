```
¡Entendido! Vamos a refinar la solución para que no dependa del contexto de Spring Boot y trabaje directamente con la carga del archivo YAML que contiene una estructura de arreglo de objetos.

1. Archivo YAML (src/test/resources/paises.yml):

Crea un archivo llamado paises.yml dentro de la carpeta src/test/resources con el siguiente contenido:

YAML

countries:
  - code: default
    secrets:
      module_one:
        cliente_id: 1
        apikey: "miApi1"
      module_dos:
        cliente_id: 2
        apikey: "miApi2"
  - code: CO
    secrets:
      module_dos:
        cliente_id: 9
        apikey: "miApi9"
2. Clase para representar la estructura del YAML (opcional pero recomendado para un acceso más fácil):

Aunque no es estrictamente necesario para cargar el YAML como un arreglo genérico, crear clases que representen la estructura de tu YAML te facilitará el acceso a los datos de forma tipada en tu test.

Java

import java.util.List;
import java.util.Map;
import java.util.Objects;

public class Pais {
    private String code;
    private List<Map<String, Map<String, Object>>> secrets;

    // Constructor, getters, setters, equals y hashCode (generados por tu IDE o Lombok)

    public Pais() {
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public List<Map<String, Map<String, Object>>> getSecrets() {
        return secrets;
    }

    public void setSecrets(List<Map<String, Map<String, Object>>> secrets) {
        this.secrets = secrets;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Pais pais = (Pais) o;
        return Objects.equals(code, pais.code) && Objects.equals(secrets, pais.secrets);
    }

    @Override
    public int hashCode() {
        return Objects.hash(code, secrets);
    }

    @Override
    public String toString() {
        return "Pais{" +
               "code='" + code + '\'' +
               ", secrets=" + secrets +
               '}';
    }
}
3. Test Unitario sin contexto de Spring Boot:

Aquí tienes el test unitario que carga el archivo YAML y verifica su contenido como un arreglo de mapas:

Fragmento de código

import org.junit.jupiter.api.Test;
import org.yaml.snakeyaml.Yaml;

import java.io.InputStream;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class CargaYamlListaObjetosTest {

    @Test
    void cargarListaDePaisesDesdeYaml() {
        // 1. Obtiene el InputStream del archivo YAML desde el classpath
        InputStream inputStream = this.getClass().getClassLoader().getResourceAsStream("paises.yml");
        assertNotNull(inputStream, "No se pudo encontrar el archivo paises.yml");

        // 2. Crea una instancia de Yaml
        Yaml yaml = new Yaml();

        // 3. Carga el contenido del YAML. Esperamos un Map donde la clave "countries"
        //    contiene la lista de mapas.
        Map<String, List<Map<String, Object>>> data = yaml.load(inputStream);
        assertNotNull(data, "No se pudo cargar el contenido del YAML");
        assertTrue(data.containsKey("countries"), "El YAML no contiene la clave 'countries'");

        List<Map<String, Object>> countriesCargados = data.get("countries");
        assertNotNull(countriesCargados, "La lista de países no debería ser nula");
        assertEquals(2, countriesCargados.size(), "El número de países cargados no es el esperado");

        // 4. Define la estructura esperada
        List<Map<String, Object>> countriesEsperados = List.of(
                Map.of(
                        "code", "default",
                        "secrets", List.of(
                                Map.of("module_one", Map.of("cliente_id", 1, "apikey", "miApi1")),
                                Map.of("module_dos", Map.of("cliente_id", 2, "apikey", "miApi2"))
                        )
                ),
                Map.of(
                        "code", "CO",
                        "secrets", List.of(
                                Map.of("module_dos", Map.of("cliente_id", 9, "apikey", "miApi9"))
                        )
                )
        );

        // 5. Realiza las aserciones para verificar la carga correcta
        assertEquals(countriesEsperados.size(), countriesCargados.size(), "El tamaño de la lista de países no coincide");

        for (int i = 0; i < countriesEsperados.size(); i++) {
            assertEquals(countriesEsperados.get(i), countriesCargados.get(i), "El país en el índice " + i + " no coincide");
        }
    }

    @Test
    void cargarListaDePaisesComoObjetos() {
        // 1. Obtiene el InputStream del archivo YAML
        InputStream inputStream = this.getClass().getClassLoader().getResourceAsStream("paises.yml");
        assertNotNull(inputStream, "No se pudo encontrar el archivo paises.yml");

        // 2. Crea una instancia de Yaml
        Yaml yaml = new Yaml();

        // 3. Carga el contenido del YAML directamente como un Map y luego extrae la lista
        Map<String, List<Pais>> data = yaml.load(inputStream);
        assertNotNull(data, "No se pudo cargar el contenido del YAML");
        assertTrue(data.containsKey("countries"), "El YAML no contiene la clave 'countries'");

        List<Pais> paisesCargados = data.get("countries");
        assertNotNull(paisesCargados, "La lista de países cargados no debería ser nula");
        assertEquals(2, paisesCargados.size(), "El número de países cargados no es el esperado");

        // 4. Define la lista esperada de objetos Pais
        List<Pais> paisesEsperados = List.of(
                new Pais("default", List.of(
                        Map.of("module_one", Map.of("cliente_id", 1, "apikey", "miApi1")),
                        Map.of("module_dos", Map.of("cliente_id", 2, "apikey", "miApi2"))
                )),
                new Pais("CO", List.of(
                        Map.of("module_dos", Map.of("cliente_id", 9, "apikey", "miApi9"))
                ))
        );

        // 5. Realiza las aserciones
        assertEquals(paisesEsperados.size(), paisesCargados.size(), "El tamaño de la lista de países no coincide");
        assertEquals(paisesEsperados, paisesCargados, "La lista de países no coincide");
    }
}
Explicación del Test Unitario:

@Test: Anotación de JUnit 5 que marca el método como un caso de prueba.
getClass().getClassLoader().getResourceAsStream("paises.yml"): Esta es la forma estándar en Java para acceder a los recursos que se encuentran en el classpath (como el archivo paises.yml que colocaste en src/test/resources). Devuelve un InputStream para leer el contenido del archivo.
Yaml yaml = new Yaml();: Crea una instancia de la clase Yaml de SnakeYAML para parsear el archivo.
yaml.load(inputStream): Lee el contenido del InputStream y lo parsea según la estructura del YAML.
En el primer test (cargarListaDePaisesDesdeYaml), cargamos el YAML como un Map<String, List<Map<String, Object>>> porque la raíz del YAML tiene una clave "countries" que contiene la lista.
En el segundo test (cargarListaDePaisesComoObjetos), si utilizas la clase Pais, podrías intentar cargar directamente a Map<String, List<Pais>> si SnakeYAML puede inferir la estructura correctamente basándose en tu clase Pais. Sin embargo, la forma más robusta suele ser cargar primero la estructura genérica y luego, si es necesario, mapearla a tus objetos. En este ejemplo, la carga directa a Map<String, List<Pais>> podría no funcionar directamente debido a la anidación de la lista de secrets. Por eso, el primer test que carga la estructura genérica es más seguro.
Aserciones (assertNotNull, assertEquals, assertTrue): Se utilizan para verificar que la carga del archivo fue exitosa y que el contenido coincide con lo esperado. Comprobamos que la lista no sea nula, que tenga el tamaño correcto y que cada elemento sea igual al elemento esperado.
Puntos Clave:

No dependencia de Spring Boot Context: Este test unitario no utiliza @SpringBootTest ni ninguna otra anotación que levante el contexto completo de Spring Boot. Se enfoca únicamente en la lectura y el parsing del archivo YAML utilizando la librería SnakeYAML.
Carga como Arreglo de Mapas: El primer test carga el YAML como una estructura de datos nativa de Java (un Map que contiene una List de Maps), lo que te permite inspeccionar la estructura tal cual se parsea desde el YAML.
Opcional: Carga como Objetos: El segundo test intenta cargar la lista directamente en objetos de la clase Pais. Esto puede ser más conveniente si planeas trabajar con estos datos como objetos en tu aplicación. Sin embargo, ten en cuenta que SnakeYAML necesita poder mapear la estructura del YAML a los campos de tu clase Pais.
Ubicación del Archivo: Recuerda colocar el archivo paises.yml en la carpeta src/test/resources para que el ClassLoader pueda encontrarlo.
Este enfoque te proporciona un test unitario aislado y eficiente para verificar la carga de tu archivo YAML con la estructura deseada. ¡Espero que esto sea exactamente lo que necesitabas! Si tienes más preguntas, no dudes en consultarme.











Canvas

Gemini puede come
 
```



