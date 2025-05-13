```
@Component
@ConfigurationProperties(prefix = "modules")
@Data
public class ModuloCredencialConfiguracion {
    private List<PaisSecretsConfig> countries;

    private final Map<String, Map<String, Credencial>> secretsPorPais = new HashMap<>();

    @PostConstruct
    public void init() {
        Map<String, Map<String, Credencial>> porPais = new HashMap<>();
        for (PaisSecretsConfig pais : countries) {
            porPais.put(pais.getCode(), pais.getSecrets());
        }

        // Ahora llama al setSecrets con ese mapa
        setSecrets(porPais);
    }

    public void setSecrets(Map<String, Map<String, Credencial>> configuracionPorPais) {
        // Tu algoritmo tal como lo tienes va aquí y funcionará perfectamente
    }
}

@Data
public class PaisSecretsConfig {
    private String code;
    private Map<String, Credencial> secrets;
}

@Data
public class Credencial {
    @JsonProperty("client_id")
    private String cliente_id;
    private String path;

    // Esto lo asignas luego con los secretos
    private String tokenAplicacion;
    private String apiKey;
}


modules:
  countries:
    - code: default
      secrets:
        module_one:
          client_id: 999
          path: m999
    - code: pa
      secrets:
        module_two:
          client_id: 888
          path: m888
 
```



