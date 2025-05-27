```
 import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.ConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.List;
import java.util.stream.Collectors;

public void actualizarFeatureFlag(ConfigurationClient client, String key) {
    try {
        ConfigurationSetting existingSetting = client.getConfigurationSetting(key, null);

        // Deserializamos el valor JSON a la clase intermedia
        ObjectMapper mapper = new ObjectMapper();
        FeatureFlagJson flagJson = mapper.readValue(existingSetting.getValue(), FeatureFlagJson.class);

        // Convertimos los filtros personalizados a FeatureFlagFilter (tipo de Azure)
        List<FeatureFlagFilter> azureFilters = flagJson.getConditions().getClient_filters().stream()
            .map(f -> new FeatureFlagFilter(f.getName()).setParameters(f.getParameters()))
            .collect(Collectors.toList());

        // Creamos el nuevo FeatureFlagConfigurationSetting con los datos actualizados
        FeatureFlagConfigurationSetting updatedSetting = new FeatureFlagConfigurationSetting(flagJson.getId(), flagJson.getEnabled());
        updatedSetting.setDescription(flagJson.getDescription());
        updatedSetting.setDisplayName(flagJson.getDisplayName());
        updatedSetting.setClientFilters(azureFilters);

        // Establecemos el content type especial de feature flags
        updatedSetting.setContentType("application/vnd.microsoft.appconfig.ff+json;charset=utf-8");

        // Guardamos en Azure
        client.setConfigurationSetting(updatedSetting);
        System.out.println("Feature flag actualizado correctamente.");

    } catch (Exception e) {
        System.err.println("Error al actualizar feature flag: " + e.getMessage());
    }
}

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/feature-flags")
public class FeatureFlagController {

    @Autowired
    private ConfigurationClient configurationClient;

    @PutMapping("/{featureId}")
    public String actualizarFeatureFlag(@PathVariable String featureId, @RequestBody FeatureFlagJson featureRequest) {
        try {
            // Convertimos los filtros personalizados a FeatureFlagFilter (tipo de Azure)
            List<FeatureFlagFilter> azureFilters = featureRequest.getConditions().getClient_filters().stream()
                .map(f -> new FeatureFlagFilter(f.getName()).setParameters(f.getParameters()))
                .collect(Collectors.toList());

            // Creamos el nuevo FeatureFlagConfigurationSetting con los datos del request
            FeatureFlagConfigurationSetting updatedSetting = new FeatureFlagConfigurationSetting(featureId, featureRequest.getEnabled());
            updatedSetting.setDescription(featureRequest.getDescription());
            updatedSetting.setDisplayName(featureRequest.getDisplayName());
            updatedSetting.setClientFilters(azureFilters);

            // Azure requiere este contentType para feature flags
            updatedSetting.setContentType("application/vnd.microsoft.appconfig.ff+json;charset=utf-8");

            configurationClient.setConfigurationSetting(updatedSetting);
            return "Feature flag actualizado correctamente.";
        } catch (Exception e) {
            e.printStackTrace();
            return "Error al actualizar el feature flag: " + e.getMessage();
        }
    }
}

✅ 1. Clase intermedia: FeatureFlagJson.java
java
Copiar
Editar
import java.util.List;

public class FeatureFlagJson {
    private String id;
    private String description;
    private Boolean enabled;
    private Conditions conditions;
    private String displayName;

    // Getters y setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public Boolean getEnabled() { return enabled; }
    public void setEnabled(Boolean enabled) { this.enabled = enabled; }

    public Conditions getConditions() { return conditions; }
    public void setConditions(Conditions conditions) { this.conditions = conditions; }

    public String getDisplayName() { return displayName; }
    public void setDisplayName(String displayName) { this.displayName = displayName; }
}
✅ 2. Clases auxiliares: Conditions.java y ClientFilter.java
java
Copiar
Editar
import java.util.List;

public class Conditions {
    private List<ClientFilter> client_filters;

    public List<ClientFilter> getClient_filters() {
        return client_filters;
    }

    public void setClient_filters(List<ClientFilter> client_filters) {
        this.client_filters = client_filters;
    }
}
java
Copiar
Editar
import java.util.Map;

public class ClientFilter {
    private String name;
    private Map<String, Object> parameters;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public Map<String, Object> getParameters() { return parameters; }
    public void setParameters(Map<String, Object> parameters) { this.parameters = parameters; }
}
```



import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagFilter;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class FeatureFlagService {

    private final ConfigurationClient configurationClient;

    public FeatureFlagService(ConfigurationClient configurationClient) {
        this.configurationClient = configurationClient;
    }

    public String actualizarFeatureFlag(String id, FeatureFlagJson flagJson) {
        try {
            String key = ".appconfig.featureflag/" + id;

            // Convertimos los filtros personalizados a filtros Azure
            List<FeatureFlagFilter> azureFilters = flagJson.getConditions().getClient_filters().stream()
                    .map(f -> new FeatureFlagFilter(f.getName()).setParameters(f.getParameters()))
                    .collect(Collectors.toList());

            // Creamos el nuevo FeatureFlagConfigurationSetting
            FeatureFlagConfigurationSetting updatedSetting =
                    new FeatureFlagConfigurationSetting(flagJson.getId(), flagJson.isEnabled());

            updatedSetting.setDescription(flagJson.getDescription());
            updatedSetting.setDisplayName(flagJson.getDisplayName());
            updatedSetting.setClientFilters(azureFilters);

            // Establecemos el content type oficial
            updatedSetting.setContentType("application/vnd.microsoft.appconfig.ff+json;charset=utf-8");

            configurationClient.setConfigurationSetting(updatedSetting);
            return "Feature flag actualizado correctamente.";
        } catch (Exception e) {
            e.printStackTrace();
            return "Error al actualizar feature flag: " + e.getMessage();
        }
    }
}


import com.azure.data.appconfiguration.models.ConfigurationSetting;
import com.fasterxml.jackson.databind.ObjectMapper;

// ...

public FeatureFlagJson obtenerFeatureFlagPorId(String id) {
    try {
        String key = ".appconfig.featureflag/" + id;
        ConfigurationSetting setting = configurationClient.getConfigurationSetting(key, null);

        if (setting == null || setting.getValue() == null) {
            return null;
        }

        ObjectMapper mapper = new ObjectMapper();
        return mapper.readValue(setting.getValue(), FeatureFlagJson.class);

    } catch (Exception e) {
        e.printStackTrace();
        return null;
    }
}

public String eliminarFeatureFlag(String id) {
    try {
        String key = ".appconfig.featureflag/" + id;
        ConfigurationSetting deleted = configurationClient.deleteConfigurationSetting(key, null);

        if (deleted == null) {
            return "No se encontró el feature flag para eliminar.";
        }

        return "Feature flag eliminado correctamente.";
    } catch (Exception e) {
        e.printStackTrace();
        return "Error al eliminar feature flag: " + e.getMessage();
    }
}
✅ 2. Controlador: FeatureFlagController.java
Agrega estos endpoints:

java
Copiar
Editar
@GetMapping("/{id}")
public ResponseEntity<?> obtenerFeatureFlagPorId(@PathVariable String id) {
    FeatureFlagJson flag = featureFlagService.obtenerFeatureFlagPorId(id);
    if (flag == null) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Feature flag no encontrado.");
    }
    return ResponseEntity.ok(flag);
}

@DeleteMapping("/{id}")
public ResponseEntity<String> eliminarFeatureFlag(@PathVariable String id) {
    String resultado = featureFlagService.eliminarFeatureFlag(id);
    if (resultado.contains("eliminado correctamente")) {
        return ResponseEntity.ok(resultado);
    } else {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(resultado);
    }
}
📬 Ejemplo de llamadas al API
🔍 Obtener por ID
http
Copiar
Editar
GET /api/feature-flags/mi-feature-id
Respuesta:

json
Copiar
Editar
{
  "id": "mi-feature-id",
  "enabled": true,
  "description": "Descripción del flag",
  "displayName": "Mi Flag",
  "conditions": {
    "client_filters": [
      {
        "name": "Microsoft.Percentage",
        "parameters": {
          "Value": 50
        }
      }
    ]
  }
}
❌ Eliminar por ID
http
Copiar
Editar
DELETE /api/feature-flags/mi-feature-id
Respuesta exitosa:

nginx
Copiar
Editar
Feature flag eliminado correctamente.
Si no se encuentra:

yaml
Copiar
Editar
No se encontró el feature flag para eliminar.


étodo para crear un Feature Flag
java
Copiar
Editar
@Service
public class FeatureFlagService {

    private final ConfigurationClient configurationClient;

    public FeatureFlagService(ConfigurationClient configurationClient) {
        this.configurationClient = configurationClient;
    }

    public String crearFeatureFlag(FeatureFlagJson flagJson) {
        try {
            String key = ".appconfig.featureflag/" + flagJson.getId();

            // Verifica si ya existe (opcional, para evitar sobrescribir)
            ConfigurationSetting existing = configurationClient.getConfigurationSetting(key, null);
            if (existing != null && existing.getValue() != null) {
                return "Ya existe un feature flag con el ID proporcionado.";
            }

            // Convertir filtros personalizados a filtros Azure
            List<FeatureFlagFilter> azureFilters = flagJson.getConditions().getClient_filters().stream()
                    .map(f -> new FeatureFlagFilter(f.getName()).setParameters(f.getParameters()))
                    .collect(Collectors.toList());

            // Crear el nuevo FeatureFlagConfigurationSetting
            FeatureFlagConfigurationSetting newSetting =
                    new FeatureFlagConfigurationSetting(flagJson.getId(), flagJson.isEnabled());

            newSetting.setDescription(flagJson.getDescription());
            newSetting.setDisplayName(flagJson.getDisplayName());
            newSetting.setClientFilters(azureFilters);

            newSetting.setContentType("application/vnd.microsoft.appconfig.ff+json;charset=utf-8");

            // Guardar en Azure App Configuration
            configurationClient.setConfigurationSetting(newSetting);
            return "Feature flag creado correctamente.";
        } catch (Exception e) {
            e.printStackTrace();
            return "Error al crear feature flag: " + e.getMessage();
        }
    }
}
✅ Controlador: POST /feature-flags
Agrega en tu controlador:

java
Copiar
Editar
@PostMapping
public ResponseEntity<String> crearFeatureFlag(@RequestBody FeatureFlagJson flagJson) {
    String resultado = featureFlagService.crearFeatureFlag(flagJson);
    if (resultado.contains("creado correctamente")) {
        return ResponseEntity.status(HttpStatus.CREATED).body(resultado);
    } else if (resultado.contains("Ya existe")) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(resultado);
    } else {
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(resultado);
    }
}
📬 Ejemplo de llamada POST
http
Copiar
Editar
POST /api/feature-flags
Content-Type: application/json

{
  "id": "mi-nuevo-flag",
  "enabled": true,
  "description": "Un nuevo flag para pruebas",
  "displayName": "Mi Nuevo Flag",
  "conditions": {
    "client_filters": [
      {
        "name": "Microsoft.Percentage",
        "parameters": {
          "Value": 30
        }
      }
    ]
  }
}
Respuesta:

nginx
Copiar
Editar
Feature flag creado correctamente.
