```
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class ModuloCredencialConfiguracionTest {

    private KeyVaultService keyVaultService;
    private ModuloCredencialConfiguracion moduloConfig;

    @BeforeEach
    void setUp() {
        keyVaultService = mock(KeyVaultService.class);
        moduloConfig = new ModuloCredencialConfiguracion(keyVaultService);
    }

    @Test
    void testSetCountriesConHerenciaYEnriquecimiento() {
        List<Pais> countries = new ArrayList<>();

        // default
        countries.add(new Pais("default", Map.of(
                "modulo5", crearCredencial("888", "rutaDefault")
        )));

        // Panamá
        countries.add(new Pais("PA", Map.of(
                "modulo1", crearCredencial("123", "ruta1"),
                "modulo2", crearCredencial("123", "ruta2"),
                "modulo3", crearCredencial("456", "ruta3")
        )));

        // Costa Rica, sin todos los módulos
        countries.add(new Pais("CR", Map.of(
                "modulo4", crearCredencial("999", "rutaX")
        )));

        // Mocks
        mockSecrets("123", "TOKEN123", "API123");
        mockSecrets("456", "TOKEN456", "API456");
        mockSecrets("999", "TOKEN999", "API999");
        mockSecrets("888", "TOKEN888", "API888");

        // Ejecutar
        moduloConfig.setCountries(countries);

        // Verificar llamadas al KeyVault
        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-token-app-123");
        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-x-api-key-123");

        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-token-app-456");
        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-x-api-key-456");

        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-token-app-999");
        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-x-api-key-999");

        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-token-app-888");
        verify(keyVaultService, times(1)).getKeyVaultService("ext_serv-x-api-key-888");

        // Validación: módulo propio
        var credPA = moduloConfig.getSecretsPorPais().get("PA").get("modulo1");
        assertEquals("TOKEN123", credPA.getTokenAplicacion());
        assertEquals("API123", credPA.getApiKey());

        // Validación: otro cliente_id
        var credPA456 = moduloConfig.getSecretsPorPais().get("PA").get("modulo3");
        assertEquals("TOKEN456", credPA456.getTokenAplicacion());

        // Validación: módulo heredado desde default
        var credDefaultCR = moduloConfig.getSecretsPorPais().get("CR").get("modulo5");
        assertEquals("TOKEN888", credDefaultCR.getTokenAplicacion());
        assertEquals("API888", credDefaultCR.getApiKey());
    }

    private ModuloCredencialConfiguracion.Credencial crearCredencial(String clienteId, String ruta) {
        var cred = new ModuloCredencialConfiguracion.Credencial();
        cred.setCliente_id(clienteId);
        cred.setRuta(ruta);
        return cred;
    }

    private void mockSecrets(String clienteId, String token, String apiKey) {
        when(keyVaultService.getKeyVaultService("ext_serv-token-app-" + clienteId))
                .thenReturn(new KeyVaultSecret("ext_serv-token-app-" + clienteId, token));
        when(keyVaultService.getKeyVaultService("ext_serv-x-api-key-" + clienteId))
                .thenReturn(new KeyVaultSecret("ext_serv-x-api-key-" + clienteId, apiKey));
    }

    // Clase auxiliar simulada
    static class Pais {
        private final String code;
        private final Map<String, ModuloCredencialConfiguracion.Credencial> secrets;

        public Pais(String code, Map<String, ModuloCredencialConfiguracion.Credencial> secrets) {
            this.code = code;
            this.secrets = secrets;
        }

        public String getCode() {
            return code;
        }

        public Map<String, ModuloCredencialConfiguracion.Credencial> getSecrets() {
            return secrets;
        }
    }
}

```



