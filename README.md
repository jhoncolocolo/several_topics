```
import com.azure.data.appconfiguration.ConfigurationClient;
import com.azure.data.appconfiguration.models.ConfigurationSetting;
import com.azure.data.appconfiguration.models.FeatureFlagConfigurationSetting;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Map;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class FeatureFlagServiceImplTest {

    @InjectMocks
    FeatureFlagServiceImpl service;

    @Test
    void crearOActualizarFeatureFlag_deberiaGuardarFeatureFlagEnAzure() throws Exception {
        // Arrange
        // Crear los objetos necesarios
        Map<String, Boolean> countries = Map.of("CO", true, "PE", true);
        Parameters parameters = new Parameters(countries);
        ClientFilter filter = new ClientFilter("countries", parameters);
        Conditions conditions = new Conditions(List.of(filter));

        FeatureFlagsResponseView nuevoFlag = new FeatureFlagsResponseView(
            "nuevo-feature",
            "Descripción test",
            true,
            conditions,
            "Test Flag"
        );

        String featureFlagJson = "{\"id\":\"nuevo-feature\"}"; // Mínimo necesario para el mock

        // Mock estático de HelperClassConverter
        try (MockedStatic<HelperClassConverter> mockedHelper = Mockito.mockStatic(HelperClassConverter.class)) {
            mockedHelper.when(() -> HelperClassConverter.convClassToText(any()))
                        .thenReturn(featureFlagJson);

            // Mock del cliente de configuración
            ConfigurationClient mockClient = mock(ConfigurationClient.class);

            // Sobrescribimos el método obtConexionConAppConfiguration usando espía
            FeatureFlagServiceImpl spyService = spy(service);
            doReturn(mockClient).when(spyService).obtConexionConAppConfiguration();

            // Act
            spyService.crearOActualizarFeatureFlag(nuevoFlag);

            // Assert
            verify(mockClient, times(1)).setConfigurationSetting(any(FeatureFlagConfigurationSetting.class));
        }
    }
}


public void crearOActualizarFeatureFlag(FeatureFlagsResponseView featureFlag) throws AppConfigurationException {
    try {
        // 1. Serializar el feature flag a JSON
        String valorJson = HelperClassConverter.convClassToText(featureFlag);

        // 2. Crear la clave con el prefijo estándar de Azure
        String key = ".appconfig.featureflag/" + featureFlag.id();

        // 3. Crear el objeto FeatureFlagConfigurationSetting
        ConfigurationSetting setting = new FeatureFlagConfigurationSetting()
            .setKey(key)
            .setValue(valorJson)
            .setContentType("application/vnd.microsoft.appconfig.ff+json;charset=utf-8");

        // 4. Obtener cliente
        ConfigurationClient client = obtConexionConAppConfiguration();

        // 5. Guardar o actualizar en Azure App Configuration
        client.setConfigurationSetting(setting);

    } catch (Exception e) {
        throw new AppConfigurationException("Error al crear o actualizar el feature flag", e);
    }
}


```
