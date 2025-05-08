
```
import com.azure.security.keyvault.secrets.models.KeyVaultSecret;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import static org.mockito.Mockito.*;

import java.util.*;

import static org.junit.jupiter.api.Assertions.*;

class ModuloCredencialConfiguracionTest {

    private KeyVaultService keyVaultService;
    private ModuloCredencialConfiguracion moduloConfig;

    @BeforeEach
    void setUp() {
        keyVaultService = mock(KeyVaultService.class);
        moduloConfig = new ModuloCredencialConfiguracion(keyVaultService);
    }

    @Test
    void testSetSecrets_optimizacionPorClienteId() {
        // Datos de entrada
        Map<String, ModuloCredencialConfiguracion.Credencial> inputMap = new LinkedHashMap<>();

        // Reutilizar cliente_id 999 para 3 módulos
        inputMap.put("modulo_uno", createCredencial("999", "m999"));
        inputMap.put("modulo_dos", createCredencial("999", "m999"));
        inputMap.put("modulo_tres", createCredencial("999", "m999"));

        // Cliente_id 777 para 2 módulos
        inputMap.put("modulo_cuatro", createCredencial("777", "m777"));
        inputMap.put("modulo_cinco", createCredencial("777", "m777"));

        // Cliente_id únicos
        inputMap.put("modulo_seis", createCredencial("666", "m666"));
        inputMap.put("modulo_siete", createCredencial("555", "m555"));

        // Defecto
        inputMap.put("defecto", createCredencial("88", "desarrollo2"));

        // Mock de secretos para cada cliente_id
        mockSecrets("999", "TOKEN999", "API999");
        mockSecrets("777", "TOKEN777", "API777");
        mockSecrets("666", "TOKEN666", "API666");
        mockSecrets("555", "TOKEN555", "API555");
        mockSecrets("88", "TOKEN88", "API88");

        // Ejecutar
        moduloConfig.setSecrets(inputMap);

        // Verificaciones
        verify(keyVaultService, times(1)).getSecret("ext_serv-token-app-999");
        verify(keyVaultService, times(1)).getSecret("ext_serv-x-api-key-999");
        verify(keyVaultService, times(1)).getSecret("ext_serv-token-app-777");
        verify(keyVaultService, times(1)).getSecret("ext_serv-x-api-key-777");
        verify(keyVaultService, times(1)).getSecret("ext_serv-token-app-666");
        verify(keyVaultService, times(1)).getSecret("ext_serv-x-api-key-666");
        verify(keyVaultService, times(1)).getSecret("ext_serv-token-app-555");
        verify(keyVaultService, times(1)).getSecret("ext_serv-x-api-key-555");
        verify(keyVaultService, times(1)).getSecret("ext_serv-token-app-88");
        verify(keyVaultService, times(1)).getSecret("ext_serv-x-api-key-88");

        // Validar que las credenciales ahora tienen los valores esperados
        assertEquals("TOKEN999", inputMap.get("modulo_uno").getTokenAplicacion());
        assertEquals("API999", inputMap.get("modulo_dos").getLlave_ruta());
        assertEquals("TOKEN777", inputMap.get("modulo_cuatro").getTokenAplicacion());
        assertEquals("API777", inputMap.get("modulo_cinco").getLlave_ruta());
        assertEquals("TOKEN666", inputMap.get("modulo_seis").getTokenAplicacion());
        assertEquals("API666", inputMap.get("modulo_seis").getLlave_ruta());
        assertEquals("TOKEN555", inputMap.get("modulo_seis").getTokenAplicacion());
        assertEquals("TOKEN88", inputMap.get("defecto").getTokenAplicacion());
    }

    private ModuloCredencialConfiguracion.Credencial createCredencial(String clienteId, String ruta) {
        ModuloCredencialConfiguracion.Credencial c = new ModuloCredencialConfiguracion.Credencial();
        c.setCliente_id(clienteId);
        c.setRuta(ruta);
        return c;
    }

    private void mockSecrets(String clienteId, String token, String apiKey) {
        when(keyVaultService.getSecret("ext_serv-token-app-" + clienteId))
                .thenReturn(new KeyVaultSecret("ext_serv-token-app-" + clienteId, token));
        when(keyVaultService.getSecret("ext_serv-x-api-key-" + clienteId))
                .thenReturn(new KeyVaultSecret("ext_serv-x-api-key-" + clienteId, apiKey));
    }
}

```
