# several_topics
```
@RunWith(PowerMockRunner.class)
@PrepareForTest({ValidadorServicioDeValidadorCache.class})
public class ValidadorControllerTest {

    private ValidadorController validadorController;
    private ValidadorServicioDeValidadorCache validadorCacheService;

    @Before
    public void setUp() throws Exception {
        // Crear un spy para permitir la ejecución real de los métodos
        validadorCacheService = PowerMockito.spy(new ValidadorServicioDeValidadorCache());

        // Inyectar manualmente la instancia del spy en el controlador
        validadorController = new ValidadorController(validadorCacheService);
    }

    @Test
    public void testGetCacheObjectByKey_DesdeControlador() throws Exception {
        String cacheInstance = "servicios/cache/validador_cache";
        String testKey = "testKey";

        // Ejecutar el método real en el controlador
        Object result = validadorController.getCacheValue(testKey);

        // Verificar que se llamó al método getCacheObjectByKey con los parámetros correctos
        PowerMockito.verifyPrivate(validadorCacheService, times(1))
                .invoke("getCacheObjectByKey", eq(cacheInstance), eq(testKey));
    }
}


```


