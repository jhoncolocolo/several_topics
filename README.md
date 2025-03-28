# several_topics
```
 package my.project.cache.service;

import static org.junit.Assert.assertEquals;

import java.util.Collection;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

import javax.naming.InitialContext;
import javax.naming.NamingException;

import org.easymock.EasyMock;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.powermock.api.easymock.PowerMock;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import com.ibm.websphere.cache.DistributedObjectCache;
import com.ibm.websphere.cache.EntryInfo;

// Clase de prueba para combinar put y get en la caché.
@RunWith(PowerMockRunner.class)
@PrepareForTest({ DistributedCacheService.class, InitialContext.class })
public class DistributedCacheServiceCombinedTest {

    private static final String CACHE_INSTANCE_KEY = "services/cache/validador_cache";
    private static final String USUARIO_KEY = "usuarioKey";

    /**
     * Implementación "fake" de DistributedObjectCache que extiende HashMap.
     * Se utiliza para simular el comportamiento real de la caché.
     */
    private static class FakeDistributedObjectCache extends HashMap<Object, Object> implements DistributedObjectCache {

        private static final long serialVersionUID = 1L;

        // Implementa el método put con los parámetros extendidos y delega en HashMap.
        @Override
        public Object put(Object key, Object value, int priority, int timeToLive, int entryInfo, Object metadata) {
            return super.put(key, value);
        }

        // Se sobreescriben los métodos necesarios de Map (los demás se heredan de HashMap)
        @Override
        public void clear() {
            super.clear();
        }

        @Override
        public boolean containsKey(Object key) {
            return super.containsKey(key);
        }

        @Override
        public boolean containsValue(Object value) {
            return super.containsValue(value);
        }

        @Override
        public Set<Entry<Object, Object>> entrySet() {
            return super.entrySet();
        }

        @Override
        public boolean isEmpty() {
            return super.isEmpty();
        }

        @Override
        public Set<Object> keySet() {
            return super.keySet();
        }

        @Override
        public void putAll(Map<? extends Object, ? extends Object> m) {
            super.putAll(m);
        }

        @Override
        public int size() {
            return super.size();
        }

        @Override
        public Collection<Object> values() {
            return super.values();
        }
    }

    @Test
    public void putAndGetUsuarioTransaccionTest() throws Exception {
        // Se crea el mock del InitialContext
        InitialContext initialContextMock = PowerMock.createMock(InitialContext.class);

        // Se crea una instancia fake de la caché que simula el almacenamiento interno.
        FakeDistributedObjectCache fakeCache = new FakeDistributedObjectCache();

        // Se intercepta la creación del InitialContext y se hace que el lookup retorne la misma caché fake.
        PowerMock.expectNew(InitialContext.class).andReturn(initialContextMock).anyTimes();
        EasyMock.expect(initialContextMock.lookup(CACHE_INSTANCE_KEY)).andReturn(fakeCache).anyTimes();

        // Se activan los mocks.
        PowerMock.replay(initialContextMock, InitialContext.class);

        DistributedCacheService distributedCacheService = new DistributedCacheService();

        // Se crea un objeto de prueba UsuarioTransaccion.
        UsuarioTransaccion usuarioTransaccion = new UsuarioTransaccion("usuario1", "detalle1", 123);

        // Se pone el objeto en la caché.
        distributedCacheService.putCacheObject(CACHE_INSTANCE_KEY, USUARIO_KEY, usuarioTransaccion);

        // Se obtiene el objeto de la caché.
        Object retrieved = distributedCacheService.getCacheObjectByKey(CACHE_INSTANCE_KEY, USUARIO_KEY);

        // Se verifica que el objeto obtenido es igual al que se puso.
        assertEquals(usuarioTransaccion, retrieved);
    }
}

```
