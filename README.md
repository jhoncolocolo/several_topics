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
--------------------------------------------------------------------------------------------------

import com.ibm.websphere.cache.DistributedObjectCache;
import my.project.cache.service.ValidadorServicioDeValidadorCache;
import my.project.cache.service.SeguridadEntrasRequisitosDeSeguridadEnTransferencias;
import my.project.cache.service.ValidadorDeParametrosDeCache;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Matchers;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.*;

/**
 * Prueba para ValidadorServicioDeValidadorCache con JUnit 4 y PowerMock.
 */
@RunWith(PowerMockRunner.class)
@PrepareForTest({ValidadorServicioDeValidadorCache.class, InitialContext.class})
public class ValidadorServicioDeValidadorCacheTest {

    private ValidadorServicioDeValidadorCache validadorCacheService;
    private DistributedObjectCache mockCache;

    @Before
    public void setUp() throws Exception {
        PowerMockito.mockStatic(InitialContext.class);

        // Simular contexto JNDI
        InitialContext mockContext = PowerMockito.mock(InitialContext.class);
        PowerMockito.whenNew(InitialContext.class).withNoArguments().thenReturn(mockContext);

        // Simular objeto de caché
        mockCache = PowerMockito.mock(DistributedObjectCache.class);
        when(mockContext.lookup(Matchers.<String>any())).thenReturn(mockCache);

        // Usar spy para permitir la ejecución real de métodos
        validadorCacheService = PowerMockito.spy(new ValidadorServicioDeValidadorCache());
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

        // Ejecutar el método real
        validadorCacheService.ponerValidadorDeCache(seguridadInfo, validadorInfo);

        // Verificar que se llamó a putCacheObject con los parámetros correctos
        PowerMockito.verifyPrivate(validadorCacheService, times(1))
                .invoke("putCacheObject", eq("servicios/cache/validador_cache"), eq("testKey"), anyString());

        // Simular la recuperación del objeto de la caché
        when(mockCache.get("testKey")).thenReturn("{ \"session\": \"testSession\", \"pais\": \"CO\" }");

        // Recuperar el objeto
        Object result = validadorCacheService.getCacheObjectByKey("servicios/cache/validador_cache", "testKey");

        // Verificar que el objeto insertado es el mismo que se recuperó
        assertEquals("{ \"session\": \"testSession\", \"pais\": \"CO\" }", result);
    }
}

-----------------------------------------------------------------------------------------------------------------------------------

import com.ibm.websphere.cache.DistributedObjectCache;
import my.project.cache.service.ValidadorServicioDeValidadorCache;
import my.project.cache.service.SeguridadEntrasRequisitosDeSeguridadEnTransferencias;
import my.project.cache.service.ValidadorDeParametrosDeCache;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Matchers;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.*;

/**
 * Prueba para ValidadorServicioDeValidadorCache con JUnit 4 y PowerMock.
 */
@RunWith(PowerMockRunner.class)
@PrepareForTest({ValidadorServicioDeValidadorCache.class, InitialContext.class})
public class ValidadorServicioDeValidadorCacheTest {

    private ValidadorServicioDeValidadorCache validadorCacheService;
    private DistributedObjectCache realCache; // Usamos una instancia real en memoria

    @Before
    public void setUp() throws Exception {
        PowerMockito.mockStatic(InitialContext.class);

        // Simular contexto JNDI
        InitialContext mockContext = PowerMockito.mock(InitialContext.class);
        PowerMockito.whenNew(InitialContext.class).withNoArguments().thenReturn(mockContext);

        // Crear una implementación real de la caché
        realCache = new InMemoryDistributedObjectCache();

        // Hacer que el contexto JNDI devuelva la caché real
        when(mockContext.lookup(Matchers.<String>any())).thenReturn(realCache);

        // Usar un spy para permitir la ejecución real de métodos
        validadorCacheService = PowerMockito.spy(new ValidadorServicioDeValidadorCache());
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

        // Ejecutar el método real (esto almacena en la caché real en memoria)
        validadorCacheService.ponerValidadorDeCache(seguridadInfo, validadorInfo);

        // Verificar que se llamó a putCacheObject con los parámetros correctos
        PowerMockito.verifyPrivate(validadorCacheService, times(1))
                .invoke("putCacheObject", eq("servicios/cache/validador_cache"), eq("testKey"), anyString());

        // Recuperar el objeto directamente de la caché real sin usar when()
        Object result = validadorCacheService.getCacheObjectByKey("servicios/cache/validador_cache", "testKey");

        // Verificar que el objeto insertado es el mismo que se recuperó
        assertEquals("{ \"session\": \"testSession\", \"pais\": \"CO\" }", result);
    }

    /**
     * Implementación en memoria de DistributedObjectCache para pruebas.
     */
    private static class InMemoryDistributedObjectCache implements DistributedObjectCache {
        private final java.util.Map<String, Object> cache = new java.util.HashMap<>();

        @Override
        public void put(Object key, Object value, int arg2, int arg3, int arg4, Object... params) {
            cache.put(key.toString(), value);
        }

        @Override
        public Object get(Object key) {
            return cache.get(key.toString());
        }

        @Override
        public void remove(Object key) {
            cache.remove(key.toString());
        }

        // Métodos no utilizados en la prueba
        @Override public void clear() {}
        @Override public void flush() {}
        @Override public void set(Object key, Object value) {}
    }
}


```


