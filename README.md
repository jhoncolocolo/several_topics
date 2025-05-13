```
public class CredencialService {

    private final Map<String, Map<String, ModuloCredencialConfiguracion.Credencial>> paises;

    public CredencialService(Map<String, Map<String, ModuloCredencialConfiguracion.Credencial>> paises) {
        this.paises = paises;
    }

    /**
     * Obtiene una credencial por módulo y país.
     * Si el país es null o vacío, busca solo en "default".
     */
    public ModuloCredencialConfiguracion.Credencial obtenerCredencial(String modulo, String pais) {
        // Validar el parámetro
        if (modulo == null || modulo.isBlank()) {
            throw new IllegalArgumentException("El nombre del módulo no puede ser nulo o vacío");
        }

        // Si hay país, intenta buscar primero en ese país
        if (pais != null && !pais.isBlank()) {
            ModuloCredencialConfiguracion.Credencial credencial = buscarEnPais(modulo, pais);
            if (credencial != null) {
                return credencial;
            }
        }

        // Si no encontró en el país o no se proporcionó, buscar en 'default'
        ModuloCredencialConfiguracion.Credencial credencial = buscarEnPais(modulo, "default");
        if (credencial != null) {
            return credencial;
        }

        // Retornar el default.default
        return buscarEnPais("default", "default");
    }

    /**
     * Busca una credencial dentro del mapa de un país específico.
     */
    private ModuloCredencialConfiguracion.Credencial buscarEnPais(String modulo, String pais) {
        Map<String, ModuloCredencialConfiguracion.Credencial> modulos = paises.get(pais);
        if (modulos != null) {
            return modulos.get(modulo);
        }
        return null;
    }
}




import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.HashMap;
import java.util.Map;

public class CredencialServiceTest {

    private CredencialService service;

    @BeforeEach
    void setup() {
        Map<String, Map<String, ModuloCredencialConfiguracion.Credencial>> paises = new HashMap<>();

        // default.default
        ModuloCredencialConfiguracion.Credencial defaultDefault = new ModuloCredencialConfiguracion.Credencial();
        defaultDefault.setCliente_id("88");
        defaultDefault.setLlave_ruta("AAAAAAAAAAAAAAAAAAAAA");

        Map<String, ModuloCredencialConfiguracion.Credencial> defaultModulos = new HashMap<>();
        defaultModulos.put("modulo_tres", crearCredencial("999", "m999"));
        defaultModulos.put("default", defaultDefault);

        Map<String, ModuloCredencialConfiguracion.Credencial> argentinaModulos = new HashMap<>();
        argentinaModulos.put("modulo_tres", crearCredencial("333", "m333"));

        paises.put("default", defaultModulos);
        paises.put("Argentina", argentinaModulos);

        service = new CredencialService(paises);
    }

    @Test
    void testObtenerCredencialConPais() {
        var cred = service.obtenerCredencial("modulo_tres", "Argentina");
        assertNotNull(cred);
        assertEquals("333", cred.getCliente_id());
        assertEquals("m333", cred.getRuta());
    }

    @Test
    void testObtenerCredencialSinPais() {
        var cred = service.obtenerCredencial("modulo_tres");
        assertNotNull(cred);
        assertEquals("999", cred.getCliente_id());
        assertEquals("m999", cred.getRuta());
    }

    @Test
    void testFallbackADefaultDefault() {
        var cred = service.obtenerCredencial("modulo_inexistente", "Argentina");
        assertNotNull(cred);
        assertEquals("88", cred.getCliente_id());
        assertEquals("AAAAAAAAAAAAAAAAAAAAA", cred.getLlave_ruta());
    }

    @Test
    void testModuloNoExisteEnDefault() {
        var cred = service.obtenerCredencial("modulo_inexistente");
        assertNotNull(cred);
        assertEquals("88", cred.getCliente_id());
        assertEquals("AAAAAAAAAAAAAAAAAAAAA", cred.getLlave_ruta());
    }

    @Test
    void testModuloNuloLanzaExcepcion() {
        assertThrows(IllegalArgumentException.class, () -> {
            service.obtenerCredencial(null, "Argentina");
        });
    }

    @Test
    void testModuloVacioLanzaExcepcion() {
        assertThrows(IllegalArgumentException.class, () -> {
            service.obtenerCredencial("  ");
        });
    }

    private ModuloCredencialConfiguracion.Credencial crearCredencial(String clienteId, String ruta) {
        ModuloCredencialConfiguracion.Credencial cred = new ModuloCredencialConfiguracion.Credencial();


paises:
  default:
    modulos:
      secretos:
        modulo_uno:
          cliente_id: 999
          ruta: m999
        modulo_dos:
          cliente_id: 999
          ruta: m999
        modulo_tres:
          cliente_id: 999
          ruta: m999
        modulo_cuatro:
          cliente_id: 777
          ruta: m777
        modulo_cinco:
          cliente_id: 777
          ruta: m777
        modulo_seis:
          cliente_id: 666
          ruta: m666
        modulo_siete:
          cliente_id: 555
          ruta: m555
      default:
        cliente_id: 88
        llave_ruta: AAAAAAAAAAAAAAAAAAAAA
  Colombia:
    modulos:
      secretos:
        modulo_uno:
          cliente_id: 999
          ruta: m999
        modulo_dos:
          cliente_id: 999
          ruta: m999
        modulo_tres:
          cliente_id: 999
          ruta: m999
        modulo_cuatro:
          cliente_id: 777
          ruta: m777
        modulo_cinco:
          cliente_id: 777
          ruta: m777
        modulo_seis:
          cliente_id: 666
          ruta: m666
        modulo_siete:
          cliente_id: 555
          ruta: m555
      default:
        cliente_id: 88
        llave_ruta: AAAAAAAAAAAAAAAAAAAAA
  Peru:
    modulos:
      secretos:
        modulo_uno:
          cliente_id: 999
          ruta: m999
        modulo_dos:
          cliente_id: 999
          ruta: m999
        modulo_tres:
          cliente_id: 999
          ruta: m999
        modulo_cuatro:
          cliente_id: 777
          ruta: m777
        modulo_cinco:
          cliente_id: 777
          ruta: m777
        modulo_seis:
          cliente_id: 666
          ruta: m666
        modulo_siete:
          cliente_id: 555
          ruta: m555
      default:
        cliente_id: 88
        llave_ruta: AAAAAAAAAAAAAAAAAAAAA
  Argentina:
    modulos:
      secretos:
        modulo_uno:
          cliente_id: 999
          ruta: m999
        modulo_dos:
          cliente_id: 999
          ruta: m999
        modulo_tres:
          cliente_id: 333
          ruta: m333
        modulo_cuatro:
          cliente_id: 777
          ruta: m777
        modulo_cinco:
          cliente_id: 777
          ruta: m777
        modulo_seis:
          cliente_id: 666
          ruta: m666
        modulo_siete:
          cliente_id: 555
          ruta: m555
      default:
        cliente_id: 88
        llave_ruta: AAAAAAAAAAAAAAAAAAAAA
@Component
@ConfigurationProperties(prefix = "paises")
@Data
public class PaisesConfig {
    private Map<String, Pais> paises;

    @Data
    public static class Pais {
        private Modulos modulos;
    }

    @Data
    public static class Modulos {
        private Map<String, ModuloCredencialConfiguracion.Credencial> secretos;
        private ModuloCredencialConfiguracion.Credencial defaultCredencial; // usa "default" del YAML
    }
}


@ExtendWith(SpringExtension.class)
@SpringBootTest(classes = PaisesConfig.class)
@TestPropertySource(locations = "classpath:application.yml")
@EnableConfigurationProperties(PaisesConfig.class)
class PaisesConfigTest {

    @Autowired
    private PaisesConfig config;

    @Test
    void debeCargarConfiguracionDesdeYaml() {
        assertNotNull(config);
        assertNotNull(config.getPaises());

        // Verificamos que exista el país Argentina
        assertTrue(config.getPaises().containsKey("Argentina"));

        var argentina = config.getPaises().get("Argentina");

        assertNotNull(argentina.getModulos().getSecretos().get("modulo_tres"));
        assertEquals("333", argentina.getModulos().getSecretos().get("modulo_tres").getCliente_id());

        // Verificamos default
        assertNotNull(argentina.getModulos().getDefaultCredencial());
        assertEquals("88", argentina.getModulos().getDefaultCredencial().getCliente_id());
    }
}


```




