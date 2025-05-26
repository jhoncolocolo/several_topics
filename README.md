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
        Map<String, Boolean> config = Map.of("CO", true);
        ClientFilter clientFilter = new ClientFilter("countries", new Parameters(config));
        Conditions conditions = new Conditions(List.of(clientFilter));

        FeatureFlagsResponseView flag = new FeatureFlagsResponseView(
            "nuevo-feature",
            "flag para pruebas",
            true,
            conditions,
            "Nuevo Feature"
        );

        // Act
        try {
            service.crearOActualizarFeatureFlag(flag);
        } catch (Exception e) {
            assert false : "No se esperaba excepción";
        }

        // Assert
        verify(mockClient, times(1)).setConfigurationSetting(any(ConfigurationSetting.class));
    }
}

import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import com.azure.data.appconfiguration.models.SettingSelector;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class FeatureFlagService {

    private final ConfigurationClient client;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public FeatureFlagService() {
        this.client = getConnectionConConfiguration(); // ya lo tienes
    }

    /**
     * Inserta o actualiza una feature flag en Azure App Configuration
     *
     * @param flagId        ID de la bandera
     * @param description   Descripción opcional
     * @param enabled       Estado booleano
     * @param filters       Lista de filtros tipo Map<String, Object>
     */
    public void updateOrInsertFeatureFlag(String flagId, String description, boolean enabled, List<Map<String, Object>> filters) {
        FeatureFlagConfigurationSetting flagSetting;

        try {
            // Verificamos si ya existe
            try {
                flagSetting = client.getFeatureFlag(flagId);
            } catch (Exception e) {
                flagSetting = new FeatureFlagConfigurationSetting(flagId, enabled);
            }

            // Seteamos datos básicos
            flagSetting.setEnabled(enabled);
            flagSetting.setDescription(description);
            flagSetting.setDisplayName(null); // si aplica

            // Agregamos condiciones (filtros)
            flagSetting.clearClientFilters();
            for (Map<String, Object> filter : filters) {
                String name = (String) filter.get("name");
                Map<String, Object> parameters = (Map<String, Object>) filter.get("parameters");

                flagSetting.addClientFilter(name, parameters);
            }

            // Finalmente hacemos upsert
            client.setConfigurationSetting(flagSetting);
            System.out.println("Bandera actualizada o insertada correctamente.");

        } catch (Exception ex) {
            ex.printStackTrace();
            System.err.println("Error al insertar/actualizar la bandera: " + ex.getMessage());
        }
    }

    // Este método ya lo tienes, lo incluyo solo para el contexto
    private ConfigurationClient getConnectionConConfiguration() {
        // Debes tener este método que devuelve ConfigurationClient
        return null; // implementación propia
    }
}

private FeatureFlagsResponseView getFeatureFlag(String flagId) throws JsonProcessingException {
    // Nombre estándar con prefijo
    String key = ".appconfig.featureflag/" + flagId;

    ConfigurationSetting setting = client.getConfigurationSetting(key, null); // label puede ser null

    if (setting == null || setting.getValue() == null) {
        return null;
    }

    // Usa tu helper para convertir el JSON a la clase
    return HelperClassConverter.convTextToClass(setting.getValue(), FeatureFlagsResponseView.class);
}


public void actualizarOInsertarFeatureFlag(FeatureFlagsResponseView nuevoFlag) {
    if (client == null) {
        obtConexionConAppConfiguration();
    }

    try {
        FeatureFlagConfigurationSetting featureFlagSetting;

        String key = ".appconfig.featureflag/" + nuevoFlag.getId();
        ConfigurationSetting existingSetting = client.getConfigurationSetting(key, null);

        if (existingSetting != null && existingSetting.getValue() != null) {
            featureFlagSetting = HelperClassConverter.convTextToClass(
                existingSetting.getValue(), FeatureFlagConfigurationSetting.class
            );
        } else {
            featureFlagSetting = new FeatureFlagConfigurationSetting(nuevoFlag.getId(), nuevoFlag.isEnabled());
        }

        featureFlagSetting.setEnabled(nuevoFlag.isEnabled());
        featureFlagSetting.setDescription(nuevoFlag.getDescription());
        featureFlagSetting.setDisplayName(nuevoFlag.getDisplay_name());
        featureFlagSetting.clearClientFilters();

        // Ahora sí: accedemos a conditions.client_filters
        if (nuevoFlag.getConditions() != null && nuevoFlag.getConditions().getClient_filters() != null) {
            for (FeatureFlagsResponseView.ClientFilter filter : nuevoFlag.getConditions().getClient_filters()) {
                featureFlagSetting.addClientFilter(filter.getName(), filter.getParameters());
            }
        }

        client.setConfigurationSetting(featureFlagSetting);

    } catch (Exception e) {
        throw new RuntimeException("Error al insertar o actualizar feature flag", e);
    }
}



```
