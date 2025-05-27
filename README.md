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
