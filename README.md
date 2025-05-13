```
 @ExtendWith(SpringExtension.class)
@SpringBootTest(classes = ModuloCredencialConfiguracionTest.TestConfig.class)
@TestPropertySource("classpath:application.yml")
class ModuloCredencialConfiguracionTest {

    @Autowired
    private ModuloCredencialConfiguracion config;

    @TestConfiguration
    @EnableConfigurationProperties(ModuloCredencialConfiguracion.class)
    static class TestConfig {
        // no necesita cuerpo
    }

    @Test
    void testCargaDesdeYaml() {
        assertNotNull(config);
        assertNotNull(config.getSecrets());
        assertTrue(config.getSecrets().containsKey("modulo_uno"));

        ModuloCredencialConfiguracion.Credencial credencial = config.getSecrets().get("modulo_uno");
        assertEquals("999", credencial.getCliente_id());
        assertEquals("m999", credencial.getRuta());
    }
}

```



