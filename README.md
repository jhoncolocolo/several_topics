# several_topics
```
import my.project.cache.service.ValidadorServicioDeValidadorCache;
import my.project.model.SeguridadEntrasRequisitosDeSeguridadEnTransferencias;
import my.project.model.ValidadorDeParametrosDeCache;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Matchers;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import javax.naming.NamingException;
import java.util.HashMap;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.*;

@RunWith(PowerMockRunner.class)
@PrepareForTest({ValidadorServicioDeValidadorCache.class, LoggerCustomHelper.class})
public class ValidadorServicioDeValidadorCacheTest {

    private ValidadorServicioDeValidadorCache validadorCacheService;

    @Before
    public void setUp() throws Exception {
        // Mockear la clase LoggerCustomHelper
        PowerMockito.mockStatic(LoggerCustomHelper.class);
        PowerMockito.doNothing().when(LoggerCustomHelper.class, "logInfo", any(String.class), any(String.class), any(HashMap.class));

        // Instanciar la clase que extiende de DistributedCacheService
        validadorCacheService = PowerMockito.spy(new ValidadorServicioDeValidadorCache());

        // Mockear el método putCacheObject para simular el almacenamiento en caché
        doNothing().when(validadorCacheService).putCacheObject(anyString(), anyString(), anyString());

        // Mockear el método getCacheObjectByKey para devolver el objeto guardado
        doAnswer(invocation -> {
            String key = invocation.getArgument(1);
            return "testKey".equals(key) ? "{ \"session\": \"testSession\", \"pais\": \"CO\" }" : null;
        }).when(validadorCacheService).getCacheObjectByKey(anyString(), anyString());
    }

    @Test
    public void testPonerValidadorDeCache_CasoExitoso() throws NamingException {
        // Crear datos de prueba
        SeguridadEntrasRequisitosDeSeguridadEnTransferencias seguridadInfo = new SeguridadEntrasRequisitosDeSeguridadEnTransferencias();
        ValidadorDeParametrosDeCache validadorInfo = new ValidadorDeParametrosDeCache();
        validadorInfo.setLlave("testKey");
        validadorInfo.setSesionID("testSession");
        validadorInfo.setPais("CO"); // País válido para almacenamiento en caché
        validadorInfo.setNeedCara(false); // Se activará por país

        // Ejecutar el método a probar
        validadorCacheService.ponerValidadorDeCache(seguridadInfo, validadorInfo);

        // Verificar que se llamó a putCacheObject con los parámetros correctos
        verify(validadorCacheService, times(1)).putCacheObject(eq("servicios/cache/validador_cache"), eq("testKey"), anyString());

        // Recuperar el objeto de la caché
        Object result = validadorCacheService.getCacheObjectByKey("servicios/cache/validador_cache", "testKey");

        // Verificar que el objeto insertado es el mismo que se recuperó
        assertEquals("{ \"session\": \"testSession\", \"pais\": \"CO\" }", result);

        // Verificar que se llamó al log correctamente
        PowerMockito.verifyStatic(LoggerCustomHelper.class, times(1));
        LoggerCustomHelper.logInfo(eq("Mis_logs"), anyString(), any(HashMap.class));
    }

    @Test
    public void testPonerValidadorDeCache_NoGuardaEnCache() throws NamingException {
        // Crear datos de prueba donde NO debería guardarse en caché
        SeguridadEntrasRequisitosDeSeguridadEnTransferencias seguridadInfo = new SeguridadEntrasRequisitosDeSeguridadEnTransferencias();
        ValidadorDeParametrosDeCache validadorInfo = new ValidadorDeParametrosDeCache();
        validadorInfo.setLlave("testKey");
        validadorInfo.setSesionID("testSession");
        validadorInfo.setPais("US"); // País diferente a "CO"
        validadorInfo.setNeedCara(false); // No cumple ninguna condición

        // Ejecutar el método a probar
        validadorCacheService.ponerValidadorDeCache(seguridadInfo, validadorInfo);

        // Verificar que NO se llamó a putCacheObject
        verify(validadorCacheService, never()).putCacheObject(anyString(), anyString(), anyString());

        // Verificar que NO se llamó al log
        PowerMockito.verifyStatic(LoggerCustomHelper.class, never());
        LoggerCustomHelper.logInfo(anyString(), anyString(), any(HashMap.class));
    }

    @Test
    public void testPonerValidadorDeCache_ManejoDeExcepcion() throws NamingException {
        // Crear datos de prueba
        SeguridadEntrasRequisitosDeSeguridadEnTransferencias seguridadInfo = new SeguridadEntrasRequisitosDeSeguridadEnTransferencias();
        ValidadorDeParametrosDeCache validadorInfo = new ValidadorDeParametrosDeCache();
        validadorInfo.setLlave("testKey");
        validadorInfo.setSesionID("testSession");
        validadorInfo.setPais("CO");

        // Simular que putCacheObject lanza una excepción
        doThrow(new NamingException("Error de cache")).when(validadorCacheService).putCacheObject(anyString(), anyString(), anyString());

        // Ejecutar el método
        validadorCacheService.ponerValidadorDeCache(seguridadInfo, validadorInfo);

        // Verificar que el error se registró en el log
        PowerMockito.verifyStatic(LoggerCustomHelper.class, times(1));
        LoggerCustomHelper.logInfo(eq("Mis_logs"), contains("Error de cache"), any(HashMap.class));
    }
}

```


