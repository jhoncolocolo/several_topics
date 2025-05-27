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

```
