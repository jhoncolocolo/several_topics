# several_topics
```
  package my.project.cache.service;

import static org.junit.Assert.*;
import static org.powermock.api.mockito.PowerMockito.*;

import com.ibm.websphere.cache.DistributedObjectCache;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import javax.naming.NamingException;

@RunWith(PowerMockRunner.class)
@PrepareForTest(DistributedCacheService.class)
public class DistributedCacheServiceTest {
    private DistributedCacheService cacheService;

    @Mock
    private DistributedObjectCache fakeCache;

    @Before
    public void setUp() throws Exception {
        cacheService = spy(new DistributedCacheService()); // Espiamos la clase real
        fakeCache = new FakeDistributedObjectCache(); // Instancia del cache fake

        // Mockeamos el método privado getCache para que devuelva fakeCache
        when(cacheService, "getCache", anyString()).thenReturn(fakeCache);
    }

    @Test
    public void testPutAndGetCacheObject() throws NamingException {
        UsuarioTransaccion user = new UsuarioTransaccion("Juan", "Compra", 100);
        cacheService.putCacheObject("testCache", "user1", user);

        Object retrieved = cacheService.getCacheObjectByKey("testCache", "user1");
        assertEquals(user, retrieved);
    }

    @Test
    public void testRemoveCacheObject() throws NamingException {
        UsuarioTransaccion user = new UsuarioTransaccion("Maria", "Venta", 200);
        cacheService.putCacheObject("testCache", "user2", user);
        cacheService.removeCacheObjectByKey("testCache", "user2");

        Object retrieved = cacheService.getCacheObjectByKey("testCache", "user2");
        assertNull(retrieved);
    }
}

```


