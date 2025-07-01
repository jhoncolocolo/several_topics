```
 package myproject.service;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

import java.util.Date;

import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import myservice.helper.CustomCacheControllerBean;

public class CalculatorServiceBeanTest {

    private CalculatorServiceBean calculatorServiceBean;

    @Mock
    private CustomCacheControllerBean mockCache;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        calculatorServiceBean = new CalculatorServiceBean() {
            @Override
            protected boolean cacheContieneClave(String key) {
                return mockCache.contieneClave(key);
            }

            @Override
            protected void cachePutObject(String key, String value, String cacheTimeLifeKey) {
                mockCache.put(key, value, cacheTimeLifeKey);
            }
        };
    }

    private String generateValidTOTP(String secret) throws Exception {
        byte[] keyBytes = secret.getBytes();
        long currentUnixTime = new Date().getTime() / 1000;
        java.lang.reflect.Method method = CalculatorServiceBean.class.getDeclaredMethod("generateConvertedToken", byte[].class, long.class);
        method.setAccessible(true);
        int token = (int) method.invoke(calculatorServiceBean, keyBytes, currentUnixTime);
        return String.format("%06d", token);
    }

    @Test
    public void testPublicValidate_WithValidToken() throws Exception {
        String keyWordString = "mySecretKey";
        String codeSixDigit = generateValidTOTP(keyWordString);

        when(mockCache.contieneClave(anyString())).thenReturn(false);
        doNothing().when(mockCache).put(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertTrue("Expected OTP to be valid", result);
    }

    @Test
    public void testPublicValidate_WithInvalidToken() throws Exception {
        String keyWordString = "mySecretKey";
        String invalidCodeSixDigit = "000000"; // deliberately invalid

        when(mockCache.contieneClave(anyString())).thenReturn(false);
        doNothing().when(mockCache).put(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, invalidCodeSixDigit);

        assertFalse("Expected OTP to be invalid", result);
    }
}
```
