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


```
