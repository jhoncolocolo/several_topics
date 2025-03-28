# several_topics
```
package my.project.cache.service;

import static org.junit.Assert.assertEquals;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyObject;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.junit.MockitoJUnitRunner;

import com.ibm.websphere.cache.DistributedObjectCache;
import com.ibm.websphere.cache.EntryInfo;

@RunWith(MockitoJUnitRunner.class)
public class DistributedCacheServiceTest {

    private static final String CACHE_INSTANCE_KEY = "services/cache/validador_cache";
    private static final String USUARIO = "USUARIO";
    private static final String OBJETO = "objeto";

    private DistributedCacheService distributedCacheService;
    private DistributedObjectCache distributedObjectCacheMock;
    private InitialContext initialContextMock;

    @Before
    public void setUp() throws NamingException {
        initialContextMock = mock(InitialContext.class);
        distributedObjectCacheMock = mock(DistributedObjectCache.class);

        // Simular la creación del InitialContext y la búsqueda de la caché
        when(PowerMock.mockConstruction(InitialContext.class, anyObject())).thenReturn(initialContextMock);
        when(initialContextMock.lookup(CACHE_INSTANCE_KEY)).thenReturn(distributedObjectCacheMock);

        distributedCacheService = new DistributedCacheService();
    }

    @Test
    public void putAndGetCacheObjectTest() throws Exception {

        // Creamos el objeto UsuarioTransaccion que vamos a poner y obtener
        UsuarioTransaccion transaccionParaCache = new UsuarioTransaccion(USUARIO, "Detalle de prueba", OBJETO);

        // Configuramos el comportamiento del mock para el método put
        when(distributedObjectCacheMock.put(eq(USUARIO), eq(transaccionParaCache), anyInt(), anyInt(), anyObject(), eq(null))).thenReturn(false);

        // Configuramos el comportamiento del mock para el método get
        when(distributedObjectCacheMock.get(USUARIO)).thenReturn(transaccionParaCache);

        // Llamamos al método para poner el objeto en la caché
        distributedCacheService.putCacheObject(CACHE_INSTANCE_KEY, USUARIO, transaccionParaCache);

        // Llamamos al método para obtener el objeto de la caché
        Object result = distributedCacheService.getCacheObjectByKey(CACHE_INSTANCE_KEY, USUARIO);
        UsuarioTransaccion transaccionRecuperada = (UsuarioTransaccion) result;

        // Verificamos que el método put fue llamado con los argumentos esperados
        verify(distributedObjectCacheMock, times(1)).put(eq(USUARIO), eq(transaccionParaCache), anyInt(), anyInt(), anyObject(), eq(null));

        // Verificamos que el método get fue llamado con la clave correcta
        verify(distributedObjectCacheMock, times(1)).get(eq(USUARIO));

        // Verificamos que el objeto recuperado es igual al objeto que se puso
        assertEquals(transaccionParaCache, transaccionRecuperada);
    }
}
```
