# several_topics
```
  package my.project.cache.service;

import com.ibm.websphere.cache.DistributedObjectCache;
import java.util.HashMap;
import java.util.Map;

public class FakeDistributedObjectCache extends DistributedObjectCache {
    private final Map<Object, Object> cache = new HashMap<>();

    @Override
    public int getMapType() {
        return TYPE_DISTRIBUTED_MAP;
    }

    @Override
    public Object get(Object key) {
        return cache.get(key);
    }

    @Override
    public Object put(Object key, Object value) {
        return cache.put(key, value);
    }

    @Override
    public Object remove(Object key) {
        return cache.remove(key);
    }

    @Override
    public boolean containsKey(Object key) {
        return cache.containsKey(key);
    }

    @Override
    public int size() {
        return cache.size();
    }
}



package my.project.cache.service;

import static org.junit.Assert.*;

import com.ibm.websphere.cache.DistributedObjectCache;
import org.junit.Before;
import org.junit.Test;

public class DistributedCacheServiceTest {
    private DistributedCacheService cacheService;
    private DistributedObjectCache fakeCache;

    @Before
    public void setUp() {
        fakeCache = new FakeDistributedObjectCache(); // Usa la versión de prueba
        cacheService = new DistributedCacheService(fakeCache);
    }

    @Test
    public void testPutAndGetCacheObject() {
        UsuarioTransaccion user = new UsuarioTransaccion("Juan", "Compra", 100);
        cacheService.putCacheObject("user1", user);

        Object retrieved = cacheService.getCacheObjectByKey("user1");
        assertEquals(user, retrieved);
    }

    @Test
    public void testRemoveCacheObject() {
        UsuarioTransaccion user = new UsuarioTransaccion("Maria", "Venta", 200);
        cacheService.putCacheObject("user2", user);
        cacheService.removeCacheObjectByKey("user2");

        Object retrieved = cacheService.getCacheObjectByKey("user2");
        assertNull(retrieved);
    }
}



package my.project.cache.service;

import static org.junit.Assert.*;
import com.ibm.websphere.cache.DistributedObjectCache;
import org.junit.Before;
import org.junit.Test;
import java.lang.reflect.Method;
import java.lang.reflect.Field;
import java.util.Map;

public class DistributedCacheServiceTest {
    private DistributedCacheService cacheService;
    private DistributedObjectCache fakeCache;

    @Before
    public void setUp() throws Exception {
        cacheService = new DistributedCacheService(); 
        fakeCache = new FakeDistributedObjectCache();

        // Usamos Reflection para reemplazar `getCache`
        Field method = DistributedCacheService.class.getDeclaredField("getCache");
        method.setAccessible(true);
        method.set(cacheService, (String cacheInstance) -> fakeCache);
    }

    @Test
    public void testPutAndGetCacheObject() throws Exception {
        UsuarioTransaccion user = new UsuarioTransaccion("Juan", "Compra", 100);
        cacheService.putCacheObject("testCache", "user1", user);

        Object retrieved = cacheService.getCacheObjectByKey("testCache", "user1");
        assertEquals(user, retrieved);
    }

    @Test
    public void testRemoveCacheObject() throws Exception {
        UsuarioTransaccion user = new UsuarioTransaccion("Maria", "Venta", 200);
        cacheService.putCacheObject("testCache", "user2", user);
        cacheService.removeCacheObjectByKey("testCache", "user2");

        Object retrieved = cacheService.getCacheObjectByKey("testCache", "user2");
        assertNull(retrieved);
    }
}


```


