```
package customPackage.restservices;

import customPackage.CacheService.CacheServicioProcesoImpl;
import customPackage.CacheService.CustomCacheServiceModel;
import customPackage.CacheService.ModeloBasicoCache;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import static org.mockito.Matchers.*;
import static org.mockito.Mockito.*;

@RunWith(PowerMockRunner.class)
@PrepareForTest(MyMainClass.class)
public class MyMainClassTest {

    @Test
    public void testMyMetodo_WhenUsuarioIsOrlando_ShouldReturnItWorks() throws Exception {
        // Arrange
        CacheServicioProcesoImpl mockCacheService = PowerMockito.mock(CacheServicioProcesoImpl.class);
        CustomCacheServiceModel fakeCacheModel = new CustomCacheServiceModel(true, "Orlando", "S123");

        // Interceptar la creación del objeto dentro de MyMainClass
        PowerMockito.whenNew(CacheServicioProcesoImpl.class).withNoArguments().thenReturn(mockCacheService);

        // Simular comportamiento
        when(mockCacheService.getCacheObjectByKey(anyString(), anyString(), anyObject()))
                .thenReturn(fakeCacheModel);

        MyMainClass myMain = new MyMainClass();

        // Act
        String result = myMain.myMetodo("Orlando", "S123");

        // Assert
        org.junit.Assert.assertEquals("it works", result);

        // Verificar que se haya invocado el cache
        verify(mockCacheService, times(1))
                .fijeCacheAlObjeto(any(ModeloBasicoCache.class), any(CustomCacheServiceModel.class));
    }

    @Test
    public void testMyMetodo_WhenUsuarioIsRoberto_ShouldReturnItAlmostWork() throws Exception {
        CacheServicioProcesoImpl mockCacheService = PowerMockito.mock(CacheServicioProcesoImpl.class);
        CustomCacheServiceModel fakeCacheModel = new CustomCacheServiceModel(true, "Roberto", "S001");

        PowerMockito.whenNew(CacheServicioProcesoImpl.class).withNoArguments().thenReturn(mockCacheService);
        when(mockCacheService.getCacheObjectByKey(anyString(), anyString(), anyObject()))
                .thenReturn(fakeCacheModel);

        MyMainClass myMain = new MyMainClass();

        String result = myMain.myMetodo("Roberto", "S001");

        org.junit.Assert.assertEquals("it almost work", result);
        verify(mockCacheService, times(1))
                .fijeCacheAlObjeto(any(ModeloBasicoCache.class), any(CustomCacheServiceModel.class));
    }

    @Test
    public void testMyMetodo_WhenUsuarioIsUnknown_ShouldReturnNotWork() throws Exception {
        CacheServicioProcesoImpl mockCacheService = PowerMockito.mock(CacheServicioProcesoImpl.class);
        CustomCacheServiceModel fakeCacheModel = new CustomCacheServiceModel(true, "Desconocido", "S000");

        PowerMockito.whenNew(CacheServicioProcesoImpl.class).withNoArguments().thenReturn(mockCacheService);
        when(mockCacheService.getCacheObjectByKey(anyString(), anyString(), anyObject()))
                .thenReturn(fakeCacheModel);

        MyMainClass myMain = new MyMainClass();

        String result = myMain.myMetodo("Desconocido", "S000");

        org.junit.Assert.assertEquals("Not work", result);
        verify(mockCacheService, times(1))
                .fijeCacheAlObjeto(any(ModeloBasicoCache.class), any(CustomCacheServiceModel.class));
    }
}


```
