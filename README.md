# several_topics
```
package my.project.cache.service;

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.junit.Test;
import org.easymock.EasyMock;
import org.junit.Assert;
import org.junit.runner.RunWith;
import org.powermock.api.easymock.PowerMock;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import com.ibm.websphere.cache.DistributedOBJETOCache;
import com.ibm.websphere.cache.EntryInfo;

@RunWith(PowerMockRunner.class)
@PrepareForTest({DistributedCacheService.class})
public class DistributedCacheServiceTest {

    private static final String CACHE_INSTANCE_KEY = "services/cache/validador_cache";
    private static final String USUARIO = "USUARIO";
    private static final String OBJETO = "objeto";

    @Test
    public void putAndGetCacheObjectTest() throws Exception {

        InitialContext initialContextMock = PowerMock.createMock(InitialContext.class);
        DistributedOBJETOCache distributedOBJETOCacheMock = EasyMock.createMock(DistributedOBJETOCache.class);

        PowerMock.expectNew(InitialContext.class).andReturn(initialContextMock);
        EasyMock.expect(initialContextMock.lookup(CACHE_INSTANCE_KEY)).andReturn(distributedOBJETOCacheMock);

        // Creamos el objeto UsuarioTransaccion que vamos a poner y obtener
        UsuarioTransaccion transaccionParaCache = new UsuarioTransaccion(USUARIO, "Detalle de prueba", OBJETO);

        // Expectativa para el método put
        EasyMock.expect(distributedOBJETOCacheMock.put(eq(USUARIO), eq(transaccionParaCache), EasyMock.anyInt(), EasyMock.anyInt(), EasyMock.anyObject(), EasyMock.isNull())).andReturn(false);

        // Expectativa para el método get
        when(distributedOBJETOCacheMock.get(USUARIO)).thenReturn(transaccionParaCache);

        PowerMock.replay(initialContextMock, InitialContext.class);
        PowerMock.replay(distributedOBJETOCacheMock, DistributedOBJETOCache.class);

        DistributedCacheService distributedCacheService = new DistributedCacheService();

        // Llamamos al método para poner el objeto en la caché
        distributedCacheService.putCacheObject(CACHE_INSTANCE_KEY, USUARIO, transaccionParaCache);

        // Llamamos al método para obtener el objeto de la caché
        UsuarioTransaccion transaccionRecuperada = (UsuarioTransaccion) distributedCacheService.getCacheObjectByKey(CACHE_INSTANCE_KEY, USUARIO);

        // Verificamos que el método put fue llamado con los argumentos esperados
        EasyMock.verify(distributedOBJETOCacheMock, times(1)).put(eq(USUARIO), eq(transaccionParaCache), EasyMock.anyInt(), EasyMock.anyInt(), EasyMock.anyObject(), EasyMock.isNull());

        // Verificamos que el método get fue llamado con la clave correcta
        verify(distributedOBJETOCacheMock, times(1)).get(eq(USUARIO));

        // Verificamos que el objeto recuperado es igual al objeto que se puso
        assertEquals(transaccionParaCache, transaccionRecuperada);
    }
}
```
