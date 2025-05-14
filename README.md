```
import org.junit.jupiter.api.Test;
import org.yaml.snakeyaml.Yaml;

import java.io.InputStream;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class CargaYamlListaObjetosTest {

    @Test
    void cargarListaDePaisesDesdeYaml() {
        // 1. Obtiene el InputStream del archivo YAML desde el classpath
        InputStream inputStream = this.getClass().getClassLoader().getResourceAsStream("modules.yml");
        assertNotNull(inputStream, "No se pudo encontrar el archivo modules.yml");

        // 2. Crea una instancia de Yaml
        Yaml yaml = new Yaml();

        // 3. Carga el contenido del YAML.  Ahora esperamos un Map con "modules" y luego "countries"
        Map<String, Object> data = yaml.load(inputStream);
        assertNotNull(data, "No se pudo cargar el contenido del YAML");
        assertTrue(data.containsKey("modules"), "El YAML no contiene la clave 'modules'");

        Map<String, Object> modules = (Map<String, Object>) data.get("modules");
        assertNotNull(modules, "El YAML no contiene la clave 'modules'");
        assertTrue(modules.containsKey("countries"), "El YAML no contiene la clave 'countries' dentro de 'modules'");

        List<Map<String, Object>> countriesCargados = (List<Map<String, Object>>) modules.get("countries");
        assertNotNull(countriesCargados, "La lista de países no debería ser nula");
        assertEquals(2, countriesCargados.size(), "El número de países cargados no es el esperado");

        // 4. Define la estructura esperada
        List<Map<String, Object>> countriesEsperados = List.of(
                Map.of(
                        "code", "default",
                        "secrets", Map.of(
                                "module_one", Map.of("client_id", "1", "api_key", "miApi1"),
                                "module_dos", Map.of("client_id", "2", "api_key", "miApi2")
                        )
                ),
                Map.of(
                        "code", "CO",
                        "secrets", Map.of(
                                "module_dos", Map.of("client_id", "9", "api_key", "miApi9")
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
        InputStream inputStream = this.getClass().getClassLoader().getResourceAsStream("modules.yml");
        assertNotNull(inputStream, "No se pudo encontrar el archivo modules.yml");

        // 2. Crea una instancia de Yaml
        Yaml yaml = new Yaml();

        // 3. Carga el contenido del YAML y navega a la lista de países
        Map<String, Object> data = yaml.load(inputStream);
        assertNotNull(data, "No se pudo cargar el contenido del YAML");

        Map<String, Object> modules = (Map<String, Object>) data.get("modules");
        assertNotNull(modules, "No se encontró la sección 'modules' en el YAML");

        List<Map<String, Object>> countriesData = (List<Map<String, Object>>) modules.get("countries");
        assertNotNull(countriesData, "No se encontró la lista de 'countries' en el YAML");
        assertEquals(2, countriesData.size(), "El número de países cargados no es el esperado");

        // 4. Define la lista esperada de objetos Pais
        List<Pais> paisesEsperados = List.of(
                new Pais("default", Map.of(
                        "module_one", new Credential("1", "miApi1"),
                        "module_dos", new Credential("2", "miApi2")
                )),
                new Pais("CO", Map.of(
                        "module_dos", new Credential("9", "miApi9")
                ))
        );

        // 5. Convierte la lista de Map<String,Object> a lista de objetos Pais
        List<Pais> paisesCargados = convertirAModelos(countriesData);

        // 6. Realiza las aserciones
        assertEquals(paisesEsperados.size(), paisesCargados.size(), "El tamaño de la lista de países no coincide");
        assertEquals(paisesEsperados, paisesCargados, "La lista de países no coincide");
    }

    // Método auxiliar para convertir la lista de Map<String, Object> a List<Pais>
    private List<Pais> convertirAModelos(List<Map<String, Object>> countriesData) {
        return countriesData.stream()
                .map(this::convertirAPais)
                .collect(Collectors.toList());
    }

    private Pais convertirAPais(Map<String, Object> paisData) {
        Pais pais = new Pais();
        pais.setCode((String) paisData.get("code"));

        Map<String, Map<String, Object>> secretsData = (Map<String, Map<String, Object>>) paisData.get("secrets");
        Map<String, Credential> secrets = secretsData.entrySet().stream()
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        entry -> {
                            Map<String, Object> credentialMap = entry.getValue();
                            String clientId = (String) credentialMap.get("client_id");
                            String apiKey = (String) credentialMap.get("api_key");
                            return new Credential(clientId, apiKey);
                        }
                ));
        pais.setSecrets(secrets);
        return pais;
    }

    // Clase para representar la estructura del YAML (Pais)
    public static class Pais {
        private String code;
        private Map<String, Credential> secrets;

        public Pais() {
        }

        public Pais(String code, Map<String, Credential> secrets) {
            this.code = code;
            this.secrets = secrets;
        }

        public String getCode() {
            return code;
        }

        public void setCode(String code) {
            this.code = code;
        }

        public Map<String, Credential> getSecrets() {
            return secrets;
        }

        public void setSecrets(Map<String, Credential> secrets) {
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

    // Clase para representar las credenciales
    public static class Credential {
        private String client_id;
        private String api_key;

        public Credential() {
        }

        public Credential(String client_id, String api_key) {
            this.client_id = client_id;
            this.api_key = api_key;
        }

        public String getClient_id() {
            return client_id;
        }

        public void setClient_id(String client_id) {
            this.client_id = client_id;
        }

        public String getApi_key() {
            return api_key;
        }

        public void setApi_key(String api_key) {
            this.api_key = api_key;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Credential that = (Credential) o;
            return Objects.equals(client_id, that.client_id) && Objects.equals(api_key, that.api_key);
        }

        @Override
        public int hashCode() {
            return Objects.hash(client_id, api_key);
        }

        @Override
        public String toString() {
            return "Credential{" +
                    "client_id='" + client_id + '\'' +
                    ", api_key='" + api_key + '\'' +
                    '}';
        }
    }
}

modules:
  countries:
    - code: default
      secrets:
        module_one:
          client_id: "1"
          api_key: "miApi1"
        module_dos:
          client_id: "2"
          api_key: "miApi2"
    - code: CO
      secrets:
        module_dos:
          client_id: "9"
          api_key: "miApi9"


```



