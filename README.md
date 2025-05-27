```
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.ConfigurationSetting;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.List;
import java.util.Map;

import static org.mockito.Mockito.*;

public class FeatureFlagServiceImplTest {

    private FeatureFlagServiceImpl service;
    private ConfigurationClient mockClient;

    @BeforeEach
    void setup() {
        service = Mockito.spy(new FeatureFlagServiceImpl());
        mockClient = mock(ConfigurationClient.class);

        // Forzar a que el método obtConexionConAppConfiguration devuelva el mock
        doReturn(mockClient).when(service).obtConexionConAppConfiguration();
    }

    @Test
    void testCrearOActualizarFeatureFlag_noLanzaExcepcion() {
        // Arrange
        ClientFilter filtro = new ClientFilter();
        filtro.setName("countries");
        filtro.setParameters(Map.of("CO", "true", "PE", "true"));

        FeatureFlagConfigurationConditions condiciones = new FeatureFlagConfigurationConditions();
        condiciones.setClientFilters(List.of(filtro));

        FeatureFlagsResponseView flag = new FeatureFlagsResponseView(
            "nuevo-feature",
            "flag para pruebas",
            true,
            condiciones,
            "Nuevo Feature"
        );

        // Act & Assert
        try {
            service.crearOActualizarFeatureFlag(flag);
        } catch (Exception e) {
            assert false : "No se esperaba excepción: " + e.getMessage();
        }

        // Verifica que se haya llamado a setConfigurationSetting
        verify(mockClient, times(1)).setConfigurationSetting(any(ConfigurationSetting.class));
    }
}



import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/feature-flags")
public class FeatureFlagController {

    private final FeatureFlagService featureFlagService;

    @Autowired
    public FeatureFlagController(FeatureFlagService featureFlagService) {
        this.featureFlagService = featureFlagService;
    }

    @PostMapping
    public ResponseEntity<String> crearOActualizarFlag(@RequestBody FeatureFlagsResponseView nuevoFlag) {
        try {
            featureFlagService.actualizarOInsertarFeatureFlag(nuevoFlag);
            return ResponseEntity.ok("Feature flag actualizada/insertada correctamente.");
        } catch (Exception e) {
            return ResponseEntity
                    .status(500)
                    .body("Error al procesar la feature flag: " + e.getMessage());
        }
    }
}


Claro, aquí tienes una clase Java completa que maneja de forma segura:

Lectura de un FeatureFlag existente desde Azure App Configuration

Conversión segura del JSON, corrigiendo id a featureId si es necesario

Creación y envío del nuevo valor actualizado (o el mismo) de vuelta a Azure

✅ Esta clase no depende directamente de que tu DTO tenga featureId, así que puedes usar id y simplemente transformarlo.

✅ Clase: FeatureFlagService.java
java
Copiar
Editar
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.ConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;
import com.azure.data.appconfiguration.models.FeatureFlagContentType;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;

import java.util.ArrayList;
import java.util.List;

public class FeatureFlagService {

    private final ConfigurationClient client;
    private final ObjectMapper objectMapper;

    public FeatureFlagService(ConfigurationClient client) {
        this.client = client;
        this.objectMapper = new ObjectMapper();
    }

    public void actualizarFeatureFlag(String featureId, boolean enabled, List<FeatureFlagFilter> nuevosFiltros) throws Exception {
        String key = ".appconfig.featureflag/" + featureId;

        ConfigurationSetting existingSetting = client.getConfigurationSetting(key, null);

        if (existingSetting == null || existingSetting.getValue() == null) {
            throw new RuntimeException("Feature flag no encontrado en Azure para key: " + key);
        }

        // Corregir campo "id" -> "featureId" si es necesario
        JsonNode jsonNode = objectMapper.readTree(existingSetting.getValue());
        if (jsonNode.has("id")) {
            ((ObjectNode) jsonNode).set("featureId", jsonNode.get("id"));
            ((ObjectNode) jsonNode).remove("id");
        }

        // Convertir el JSON corregido a FeatureFlagConfigurationSetting
        FeatureFlagConfigurationSetting flagSetting = objectMapper.treeToValue(jsonNode, FeatureFlagConfigurationSetting.class);

        // Actualizar valores si lo necesitas
        flagSetting.setEnabled(enabled);
        flagSetting.setClientFilters(nuevosFiltros != null ? nuevosFiltros : new ArrayList<>());

        // Confirmar JSON final antes de enviar
        System.out.println("JSON final del flagSetting:");
        System.out.println(flagSetting.toString());

        // Enviar a Azure App Configuration
        ConfigurationSetting updatedSetting = new ConfigurationSetting()
            .setKey(key)
            .setContentType(FeatureFlagContentType.APPLICATION_VND_MICROSOFT_AZURE_FEATURE_FLAG)
            .setValue(flagSetting.toString());

        client.setConfigurationSetting(updatedSetting);
        System.out.println("Feature flag actualizado exitosamente.");
    }
}
✅ Cómo usarlo
Supón que tienes una lista de filtros:

java
Copiar
Editar
List<FeatureFlagFilter> filtros = new ArrayList<>();
filtros.add(new FeatureFlagFilter("countries")
    .setParameters(Map.of("CO", true, "PE", true)));
filtros.add(new FeatureFlagFilter("platforms")
    .setParameters(Map.of("AND", true, "IPH", true)));

FeatureFlagService service = new FeatureFlagService(configurationClient);
service.actualizarFeatureFlag("mi-feature-id", true, filtros);
✅ Ventajas de este enfoque
Evitas depender de @JsonProperty o tener que modificar todas tus clases.

Corriges el problema id → featureId solo cuando sea necesario.

Verificas el JSON final antes de enviarlo, evitando corromper otros flags.

¿Te gustaría que lo envolvamos en un @RestController para usarlo vía HTTP también?







Tú dijiste:
pero entonces el insert queda aparte ?


ChatGPT Plus
Buena pregunta.

Sí, el insert (crear un feature flag nuevo) debería estar en un método aparte, distinto al de actualización. Esto es una buena práctica tanto por claridad como por control de errores.

Aquí tienes cómo puedes estructurarlo en la misma clase FeatureFlagService:

✅ Método para crear un nuevo FeatureFlag
java
Copiar
Editar
public void crearFeatureFlag(String featureId, boolean enabled, List<FeatureFlagFilter> filtros) throws Exception {
    String key = ".appconfig.featureflag/" + featureId;

    // Verifica si ya existe el feature flag
    try {
        ConfigurationSetting existing = client.getConfigurationSetting(key, null);
        if (existing != null && existing.getValue() != null) {
            throw new IllegalStateException("El feature flag con ID '" + featureId + "' ya existe.");
        }
    } catch (Exception ex) {
        // Si lanza "Setting not found", puedes continuar; si es otro error, propágalo
        if (!ex.getMessage().contains("Setting not found")) {
            throw ex;
        }
    }

    // Crear el nuevo feature flag
    FeatureFlagConfigurationSetting nuevoFlag = new FeatureFlagConfigurationSetting(featureId, enabled)
        .setClientFilters(filtros != null ? filtros : new ArrayList<>());

    ConfigurationSetting setting = new ConfigurationSetting()
        .setKey(key)
        .setContentType(FeatureFlagContentType.APPLICATION_VND_MICROSOFT_AZURE_FEATURE_FLAG)
        .setValue(nuevoFlag.toString());

    client.setConfigurationSetting(setting);

    System.out.println("Feature flag creado exitosamente: " + featureId);
}
✅ Uso de ejemplo para crear un feature flag
java
Copiar
Editar
List<FeatureFlagFilter> filtros = new ArrayList<>();
filtros.add(new FeatureFlagFilter("countries").setParameters(Map.of("CO", true, "PE", true)));
filtros.add(new FeatureFlagFilter("platforms").setParameters(Map.of("AND", true, "IPH", true)));

FeatureFlagService service = new FeatureFlagService(configurationClient);
service.crearFeatureFlag("nuevo-feature-ejemplo", true, filtros);
💡 Diferencias clave entre crear y actualizar
Acción	Método sugerido	Comprobación previa
Crear	crearFeatureFlag(...)	Verifica si ya existe
Actualizar	actualizarFeatureFlag(...)	Falla si no existe

¿Te gustaría que combine ambos en un @RestController con endpoints separados como /create-feature y /update-feature?







Tú dijiste:
si por favor y ademas dame los endpoints como se deben mandar 


ChatGPT Plus
Perfecto. Aquí tienes un controlador REST completo en Spring Boot que expone dos endpoints:

✅ FeatureFlagController con endpoints para crear y actualizar
java
Copiar
Editar
@RestController
@RequestMapping("/api/feature-flags")
public class FeatureFlagController {

    private final FeatureFlagService featureFlagService;

    @Autowired
    public FeatureFlagController(FeatureFlagService featureFlagService) {
        this.featureFlagService = featureFlagService;
    }

    // Endpoint para crear un feature flag
    @PostMapping("/create")
    public ResponseEntity<String> createFeatureFlag(@RequestBody FeatureFlagRequest request) {
        try {
            featureFlagService.crearFeatureFlag(request.getId(), request.isEnabled(), request.getClientFilters());
            return ResponseEntity.ok("Feature flag creado exitosamente.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error al crear feature flag: " + e.getMessage());
        }
    }

    // Endpoint para actualizar un feature flag existente
    @PutMapping("/update")
    public ResponseEntity<String> updateFeatureFlag(@RequestBody FeatureFlagRequest request) {
        try {
            featureFlagService.actualizarFeatureFlag(request.getId(), request.getClientFilters());
            return ResponseEntity.ok("Feature flag actualizado exitosamente.");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error al actualizar feature flag: " + e.getMessage());
        }
    }
}
✅ FeatureFlagRequest (DTO para los endpoints)
java
Copiar
Editar
public class FeatureFlagRequest {
    private String id;
    private boolean enabled;
    private List<FeatureFlagFilter> clientFilters;

    // Getters y setters
    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public List<FeatureFlagFilter> getClientFilters() {
        return clientFilters;
    }

    public void setClientFilters(List<FeatureFlagFilter> clientFilters) {
        this.clientFilters = clientFilters;
    }
}
✅ Ejemplo de JSON para el endpoint /create
URL: POST /api/feature-flags/create

json
Copiar
Editar
{
  "id": "mi_feature_flag_ejemplo",
  "enabled": true,
  "clientFilters": [
    {
      "name": "countries",
      "parameters": {
        "CO": true,
        "PE": true
      }
    },
    {
      "name": "platforms",
      "parameters": {
        "AND": true,
        "IPH": true
      }
    }
  ]
}
✅ Ejemplo de JSON para el endpoint /update
URL: PUT /api/feature-flags/update

json
Copiar
Editar
{
  "id": "mi_feature_flag_ejemplo",
  "clientFilters": [
    {
      "name": "countries",
      "parameters": {
        "CO": true,
        "AR": true
      }
    },
    {
      "name": "platforms",
      "parameters": {
        "AND": true,
        "ANDR": true
      }
    }
  ]
}
⚠️ El campo enabled no es requerido en la actualización; solo se modifican los filtros.

✅ ¿Y si quiero validar antes de actualizar?
Si necesitas validar que tanto el id como la estructura de filtros están correctos antes de actualizar, podemos agregar validaciones con @Valid y usar anotaciones como @NotBlank, @NotNull. Si lo deseas, te ayudo a agregarlo.

¿Te gustaría que prepare también una clase de configuración de prueba (@Configuration) o ejemplos para curl o Postman?


FeatureFlagConfigurationSetting flagSetting = mapper.treeToValue(jsonNode, FeatureFlagConfigurationSetting.class);

```
