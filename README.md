```
 public String crearFeatureFlag(FeatureFlagJson flagJson) {
    try {
        String key = ".appconfig.featureflag/" + flagJson.getId();

        // Verificar si ya existe el feature flag
        try {
            ConfigurationSetting existing = configurationClient.getConfigurationSetting(key, null);
            if (existing != null && existing.getValue() != null) {
                return "Ya existe un feature flag con el ID proporcionado.";
            }
        } catch (com.azure.core.exception.ResourceNotFoundException ex) {
            // OK: no existe, podemos crearlo
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
