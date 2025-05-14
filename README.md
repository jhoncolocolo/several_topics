```
 @ConfigurationProperties(prefix = "modules")
@Data
public class ModuloCredencialConfiguracion {

    private List<Pais> countries;

    @Autowired
    private KeyVaultService keyVaultService;

    @PostConstruct
    public void inicializar() {
        Map<String, Map<String, Credencial>> secretsPorPais = new HashMap<>();

        // 1. Separar default
        Map<String, Credencial> secretosDefault = countries.stream()
                .filter(p -> "default".equals(p.getCode()))
                .findFirst()
                .map(Pais::getSecrets)
                .orElse(Map.of());

        List<Credencial> todasLasCredenciales = new ArrayList<>();

        // 2. Procesar países y aplicar herencia
        for (Pais pais : countries) {
            Map<String, Credencial> secretos = new HashMap<>(secretosDefault);
            secretos.putAll(pais.getSecrets()); // Sobrescribir si aplica

            todasLasCredenciales.addAll(secretos.values());
            secretsPorPais.put(pais.getCode(), secretos);
        }

        // 3. Agrupar por client_id
        Map<String, List<Credencial>> porClienteId = todasLasCredenciales.stream()
                .collect(Collectors.groupingBy(Credencial::getClientId));

        for (Map.Entry<String, List<Credencial>> entry : porClienteId.entrySet()) {
            String clienteId = entry.getKey();
            List<Credencial> credenciales = entry.getValue();

            KeyVaultSecret token = getKeyVaultSecret(String.format(EXTERNAL_SERVICE_TOKEN_APP, clienteId));
            KeyVaultSecret apiKey = getKeyVaultSecret(String.format(EXTERNAL_SERVICE_X_API_KEY, clienteId));

            for (Credencial cred : credenciales) {
                cred.setTokenAplicacion(token.getValue());
                cred.setApiKey(apiKey.getValue());
            }
        }

        // Podrías guardar secretsPorPais como un atributo si quieres accederlo luego
    }

    private KeyVaultSecret getKeyVaultSecret(String nombre) {
        return keyVaultService.getSecret(nombre);
    }

    @Data
    public static class Pais {
        private String code;
        private Map<String, Credencial> secrets;
    }

    @Data
    public static class Credencial {
        @JsonProperty("client_id")
        private String clientId;

        @JsonProperty("api_key")
        private String apiKey;

        private String tokenAplicacion;
    }
}

```



