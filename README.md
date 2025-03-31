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


import com.ibm.websphere.cache.DistributedObjectCache;
import my.project.cache.service.DistributedCacheService;
import my.project.cache.service.UsuarioTransaccion;
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

@RunWith(PowerMockRunner.class)
@PrepareForTest({DistributedCacheService.class, InitialContext.class})
public class DistributedCacheServiceTest {

    private DistributedCacheService cacheService;
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

        cacheService = new DistributedCacheService();
    }

    @Test
    public void testPutCacheObject() throws NamingException {
        UsuarioTransaccion usuario = new UsuarioTransaccion("Juan", "Compra", 100);

        cacheService.putCacheObject("myCache", "user123", usuario);

        verify(mockCache, times(1)).put(eq("user123"), eq(usuario), anyInt(), anyInt(), anyInt(), isNull());
    }

    @Test
    public void testGetCacheObjectByKey() throws NamingException {
        UsuarioTransaccion usuario = new UsuarioTransaccion("Juan", "Compra", 100);
        when(mockCache.get("user123")).thenReturn(usuario);

        Object result = cacheService.getCacheObjectByKey("myCache", "user123");

        assertEquals(usuario, result);
    }

    @Test
    public void testRemoveCacheObjectByKey() throws NamingException {
        cacheService.removeCacheObjectByKey("myCache", "user123");

        verify(mockCache, times(1)).remove("user123");
    }

@Test
public void testPutAndGetCacheObject() throws NamingException {
    UsuarioTransaccion usuario = new UsuarioTransaccion("Juan", "Compra", 100);

    // Simular que cuando se llama a get() devuelve el mismo objeto
    doAnswer(invocation -> {
        Object key = invocation.getArgument(0);
        return "user123".equals(key) ? usuario : null;
    }).when(mockCache).get(anyString());

    // Agregar el objeto a la caché
    cacheService.putCacheObject("myCache", "user123", usuario);

    // Recuperar el objeto
    Object result = cacheService.getCacheObjectByKey("myCache", "user123");

    // Verificar que el objeto insertado es el mismo que se recuperó
    assertEquals(usuario, result);

    // Verificar que se llamó a put con los parámetros correctos
    verify(mockCache, times(1)).put(eq("user123"), eq(usuario), eq(1), eq(660), eq(4), any(Object[].class));

    // Verificar que se llamó a get con la clave correcta
    verify(mockCache, times(1)).get(eq("user123"));
}

}


```


