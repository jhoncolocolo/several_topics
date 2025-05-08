
```
✅ Método setSecrets modificado:
java
Copiar
Editar
public void setSecrets(Map<String, Credencial> secrets) {
    this.secrets = secrets;

    // Agrupar credenciales por cliente_id
    Map<String, List<Credencial>> agrupadasPorClienteId = secrets.values().stream()
        .collect(Collectors.groupingBy(Credencial::getCliente_id));

    for (Map.Entry<String, List<Credencial>> entry : agrupadasPorClienteId.entrySet()) {
        String clienteId = entry.getKey();
        List<Credencial> credenciales = entry.getValue();

        // Obtener secretos una sola vez por cliente_id
        KeyVaultSecret tokenAplicacionSecret = getKeyVaultSecret(
                String.format(EXTERNAL_SERVICE_TOKEN_APP, clienteId));
        KeyVaultSecret xApiKeySecret = getKeyVaultSecret(
                String.format(EXTERNAL_SERVICE_X_API_KEY, clienteId));

        for (Credencial credencial : credenciales) {
            if (credencial.getTokenAplicacion() == null && tokenAplicacionSecret != null) {
                credencial.setTokenAplicacion(tokenAplicacionSecret.getValue());
            }
            if (credencial.getApiKey() == null && xApiKeySecret != null) {
                credencial.setApiKey(xApiKeySecret.getValue());
            }
        }
    }
}
✅ Unit Test con Mockito (JUnit 5, Java 17)
Supongamos que tienes:

KeyVaultSecret(String value)

KeyVaultService.getSecret(String name) que devuelve KeyVaultSecret

java
Copiar
Editar
@ExtendWith(MockitoExtension.class)
class ModuloCredencialConfiguracionTest {

    @Mock
    KeyVaultService keyVaultService;

    @InjectMocks
    ModuloCredencialConfiguracion configuracion;

    @Test
    void testSetSecrets_agrupadoPorClienteId() {
        // Arrange
        Map<String, Credencial> mapa = new LinkedHashMap<>();
        mapa.put("modulo_uno", new Credencial("999", "m999", null, null));
        mapa.put("modulo_dos", new Credencial("999", "m999", null, null));
        mapa.put("modulo_tres", new Credencial("999", "m999", null, null));
        mapa.put("modulo_cuatro", new Credencial("777", "m777", null, null));
        mapa.put("modulo_cinco", new Credencial("777", "m777", null, null));
        mapa.put("modulo_seis", new Credencial("666", "m666", null, null));
        mapa.put("modulo_siete", new Credencial("555", "m555", null, null));
        mapa.put("defecto", new Credencial("88", "desarrollo2", null, null));

        // Simular getSecret para cada cliente_id (2 secretos por cada uno)
        when(keyVaultService.getSecret("ext_serv-token-app-999"))
            .thenReturn(new KeyVaultSecret("TOKEN999"));
        when(keyVaultService.getSecret("ext_serv-x-api-key-999"))
            .thenReturn(new KeyVaultSecret("API999"));

        when(keyVaultService.getSecret("ext_serv-token-app-777"))
            .thenReturn(new KeyVaultSecret("TOKEN777"));
        when(keyVaultService.getSecret("ext_serv-x-api-key-777"))
            .thenReturn(new KeyVaultSecret("API777"));

        when(keyVaultService.getSecret("ext_serv-token-app-666"))
            .thenReturn(new KeyVaultSecret("TOKEN666"));
        when(keyVaultService.getSecret("ext_serv-x-api-key-666"))
            .thenReturn(new KeyVaultSecret("API666"));

        when(keyVaultService.getSecret("ext_serv-token-app-555"))
            .thenReturn(new KeyVaultSecret("TOKEN555"));
        when(keyVaultService.getSecret("ext_serv-x-api-key-555"))
            .thenReturn(new KeyVaultSecret("API555"));

        when(keyVaultService.getSecret("ext_serv-token-app-88"))
            .thenReturn(new KeyVaultSecret("TOKEN88"));
        when(keyVaultService.getSecret("ext_serv-x-api-key-88"))
            .thenReturn(new KeyVaultSecret("API88"));

        // Act
        configuracion.setSecrets(mapa);

        // Assert
        assertEquals("TOKEN999", mapa.get("modulo_uno").getTokenAplicacion());
        assertEquals("API999", mapa.get("modulo_uno").getApiKey());
        assertEquals("TOKEN999", mapa.get("modulo_tres").getTokenAplicacion());

        assertEquals("TOKEN777", mapa.get("modulo_cinco").getTokenAplicacion());
        assertEquals("API777", mapa.get("modulo_cinco").getApiKey());

        assertEquals("TOKEN666", mapa.get("modulo_seis").getTokenAplicacion());
        assertEquals("API666", mapa.get("modulo_seis").getApiKey());

        assertEquals("TOKEN555", mapa.get("modulo_siete").getTokenAplicacion());
        assertEquals("API555", mapa.get("modulo_siete").getApiKey());

        assertEquals("TOKEN88", mapa.get("defecto").getTokenAplicacion());
        assertEquals("API88", mapa.get("defecto").getApiKey());

        // Verifica que solo se llamaron 10 veces (2 por cada cliente_id distinto)
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
    }

    // Clase auxiliar simulada si no existe
    static class Credencial {
        private String cliente_id;
        private String ruta;
        private String apiKey;
        private String tokenAplicacion;

        public Credencial(String cliente_id, String ruta, String apiKey, String tokenAplicacion) {
            this.cliente_id = cliente_id;
            this.ruta = ruta;
            this.apiKey = apiKey;
            this.tokenAplicacion = tokenAplicacion;
        }

        public String getCliente_id() { return cliente_id; }
        public String getRuta() { return ruta; }
        public String getApiKey() { return apiKey; }
        public String getTokenAplicacion() { return tokenAplicacion; }
        public void setApiKey(String apiKey) { this.apiKey = apiKey; }
        public void setTokenAplicacion(String tokenAplicacion) { this.tokenAplicacion = tokenAplicacion; }
    }

    static class KeyVaultSecret {
        private final String value;
        public KeyVaultSecret(String value) { this.value = value; }
        public String getValue() { return value; }
    }
}

```
