```
package customPackage.restservices;

import customPackage.CacheService.CacheServicioProcesoImpl;
import customPackage.CacheService.CustomCacheServiceModel;
import customPackage.CacheService.ModeloBasicoCache;
import org.junit.*;
import org.junit.runner.RunWith;
import org.mockito.Mockito;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@RunWith(PowerMockRunner.class)
@PrepareForTest(MyMainClass.class) // <--- importante
public class MyMainClassTest {

    private CacheServicioProcesoImpl cacheMock;
    private MyMainClass myMainClass;

    @Before
    public void setUp() throws Exception {
        myMainClass = new MyMainClass();

        // Creamos un mock de CacheServicioProcesoImpl
        cacheMock = PowerMockito.mock(CacheServicioProcesoImpl.class);

        // Cuando se llame a "new CacheServicioProcesoImpl()" devolver el mock
        PowerMockito.whenNew(CacheServicioProcesoImpl.class)
                .withNoArguments()
                .thenReturn(cacheMock);

        // Mock del objeto que devolverá getCacheObjectByKey
        CustomCacheServiceModel mockCacheModel = new CustomCacheServiceModel(true, "Orlando", "S123");
        when(cacheMock.getCacheObjectByKey(
                eq(CacheServicioProcesoImpl.CACHE_LLAVE),
                Mockito.anyString(),
                eq(CustomCacheServiceModel.class)))
                .thenReturn(mockCacheModel);
    }

    @Test
    public void testMyMetodo_UsuarioOrlando() throws Exception {
        String result = myMainClass.myMetodo("Orlando", "S123");

        Assert.assertEquals("it works", result);

        // Verifica que se llamó a getCacheObjectByKey
        verify(cacheMock, times(1))
                .getCacheObjectByKey(eq(CacheServicioProcesoImpl.CACHE_LLAVE),
                        eq("Orlando"),
                        eq(CustomCacheServiceModel.class));

        // Verifica que se llamó a fijeCacheAlObjeto
        verify(cacheMock, times(1))
                .fijeCacheAlObjeto(any(ModeloBasicoCache.class), any(CustomCacheServiceModel.class));
    }

    @Test
    public void testMyMetodo_UsuarioRoberto() throws Exception {
        String result = myMainClass.myMetodo("Roberto", "S999");
        Assert.assertEquals("it almost work", result);
    }

    @Test
    public void testMyMetodo_UsuarioDesconocido() throws Exception {
        String result = myMainClass.myMetodo("X", "S000");
        Assert.assertEquals("Not work", result);
    }
}


```
