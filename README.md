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
        // ... (El primer test se mantiene igual, no necesita cambios para este requerimiento) ...
        InputStream inputStream = this.getClass().getClassLoader().getResourceAsStream("paises.yml");
        assertNotNull(inputStream, "No se pudo encontrar el archivo paises.yml");
        Yaml yaml = new Yaml();
        Map<String, List<Map<String, Object>>> data = yaml.load(inputStream);
        assertNotNull(data, "No se pudo cargar el contenido del YAML");
        assertTrue(data.containsKey("countries"), "El YAML no contiene la clave 'countries'");
        List<Map<String, Object>> countriesCargados = data.get("countries");
        assertNotNull(countriesCargados, "La lista de países no debería ser nula");
        assertEquals(2, countriesCargados.size(), "El número de países cargados no es el esperado");
        List<Map<String, Object>> countriesEsperados = List.of(
                Map.of(
                        "code", "default",
                        "secrets", Map.of(
                                "module_one", Map.of("cliente_id", "1", "apikey", "miApi1"),
                                "module_dos", Map.of("cliente_id", "2", "apikey", "miApi2")
                        )
                ),
                Map.of(
                        "code", "CO",
                        "secrets", Map.of(
                                "module_dos", Map.of("cliente_id", "9", "apikey", "miApi9")
                        )
                )
        );
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
        Map<String, List<Map<String, Object>>> data = yaml.load(inputStream);
        assertNotNull(data, "No se pudo cargar el contenido del YAML");
        assertTrue(data.containsKey("countries"), "El YAML no contiene la clave 'countries'");

        List<Map<String, Object>> countriesData = data.get("countries");
        assertNotNull(countriesData, "La lista de países cargados no debería ser nula");
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
                            String clienteId = (String) credentialMap.get("cliente_id");
                            String apiKey = (String) credentialMap.get("apikey");
                            return new Credential(clienteId, apiKey);
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
        private String clienteId;
        private String apiKey;

        public Credential() {
        }

        public Credential(String clienteId, String apiKey) {
            this.clienteId = clienteId;
            this.apiKey = apiKey;
        }

        public String getClienteId() {
            return clienteId;
        }

        public void setClienteId(String clienteId) {
            this.clienteId = clienteId;
        }

        public String getApiKey() {
            return apiKey;
        }

        public void setApiKey(String apiKey) {
            this.apiKey = apiKey;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Credential that = (Credential) o;
            return Objects.equals(clienteId, that.clienteId) && Objects.equals(apiKey, that.apiKey);
        }

        @Override
        public int hashCode() {
            return Objects.hash(clienteId, apiKey);
        }

        @Override
        public String toString() {
            return "Credential{" +
                    "clienteId='" + clienteId + '\'' +
                    ", apiKey='" + apiKey + '\'' +
                    '}';
        }
    }
}

countries:
  - code: default
    secrets:
      module_one:
        cliente_id: "1"
        apikey: "miApi1"
      module_dos:
        cliente_id: "2"
        apikey: "miApi2"
  - code: CO
    secrets:
      module_dos:
        cliente_id: "9"
        apikey: "miApi9"
```



