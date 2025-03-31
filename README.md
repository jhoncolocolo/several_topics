# several_topics
```
import com.ibm.websphere.cache.DistributedObjectCache;
import java.util.HashMap;
import java.util.Map;

public class FakeDistributedObjectCache extends DistributedObjectCache {
    private final Map<Object, Object> cache = new HashMap<>();

    @Override
    public int getMapType() {
        return TYPE_DISTRIBUTED_MAP;
    }

    public Object get(Object key) {
        return cache.get(key);
    }

    public void put(Object key, Object value) {
        cache.put(key, value);
    }

    public void remove(Object key) {
        cache.remove(key);
    }

    public boolean containsKey(Object key) {
        return cache.containsKey(key);
    }

    public int size() {
        return cache.size();
    }
}


import org.junit.Before;
import org.junit.After;
import org.junit.Test;
import static org.junit.Assert.*;

public class FakeDistributedObjectCacheTest {

    private FakeDistributedObjectCache cache;

    @Before
    public void setUp() {
        cache = new FakeDistributedObjectCache();
    }

    @After
    public void tearDown() {
        cache = null;
    }

    @Test
    public void testPutAndGet() {
        cache.put("key1", "value1");
        assertEquals("value1", cache.get("key1"));
    }

    @Test
    public void testGetNonExistentKey() {
        assertNull(cache.get("nonExistentKey"));
    }

    @Test
    public void testRemove() {
        cache.put("key1", "value1");
        cache.remove("key1");
        assertNull(cache.get("key1"));
    }

    @Test
    public void testContainsKey() {
        cache.put("key1", "value1");
        assertTrue(cache.containsKey("key1"));
        cache.remove("key1");
        assertFalse(cache.containsKey("key1"));
    }

    @Test
    public void testSize() {
        assertEquals(0, cache.size());
        cache.put("key1", "value1");
        cache.put("key2", "value2");
        assertEquals(2, cache.size());
        cache.remove("key1");
        assertEquals(1, cache.size());
    }

    @Test
    public void testGetMapType() {
        assertEquals(DistributedObjectCache.TYPE_DISTRIBUTED_MAP, cache.getMapType());
    }
}


```


