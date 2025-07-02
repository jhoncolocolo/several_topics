```
package myproject.service;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

import java.lang.reflect.Method;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.Before;
import org.junit.Test;

public class CalculatorServiceBeanTest {
    private CalculatorServiceBean calculatorServiceBean;
¿
    @Before
    public void setUp() {
        calculatorServiceBean = new CalculatorServiceBean() {
            @Override
            protected int getTimeSpace() {
                return 240; // estable
            }
    
            @Override
            protected long gettimeSpaceUnixTime() {
                return 1725100000L; // valor fijo para pruebas
            }
        };
    }

    @Test
    public void testPublicValidate_WithValidToken() throws Exception {
        String keyWordString = "mySecretKey";
        byte[] keyBytes = (keyWordString + "-dummy").getBytes();
        long currentUnixTime = System.currentTimeMillis() / 1000;
        int timeSpace = 240;
        int validOtp = -1;

        Method method = CalculatorServiceBean.class.getDeclaredMethod("generateConvertedToken", byte[].class, long.class);
        method.setAccessible(true);

        for (int i = -((timeSpace - 1) / 2); i <= timeSpace / 2; i++) {
            long timeChanged = currentUnixTime + i;
            int candidateOtp = (int) method.invoke(calculatorServiceBean, keyBytes, timeChanged);
            validOtp = candidateOtp;
            break;
        }

        String codeSixDigit = String.format("%06d", validOtp);
        
        // Simula que el OTP no existe previamente en caché
        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);
        assertTrue("Expected OTP to be valid", result);
    }


    //Nuevo

    @Test
public void testPublicValidate_WithValidTwoToken() throws Exception {
    String keyWordString = "mySecretKey";
    String uniqueWord = keyWordString + "-dummy";
    byte[] keyBytes = uniqueWord.getBytes();

    int timeSpace = 240; // igual que en el método real
    long timeOriginal = 1725100000L; // igual que en el método real
    int validOtp = -1;

    Method method = CalculatorServiceBean.class.getDeclaredMethod(
        "generateConvertedToken", byte[].class, long.class
    );
    method.setAccessible(true);

    // Recorre el mismo rango de tiempos que en validateToken
    for (int i = -((timeSpace - 1) / 2); i <= timeSpace / 2; ++i) {
        long timeChanged = timeOriginal + i;
        int candidateOtp = (int) method.invoke(calculatorServiceBean, keyBytes, timeChanged);
        System.out.println("timeChanged: " + timeChanged + " candidateOtp: " + candidateOtp);

        validOtp = candidateOtp;
        break; // Tomamos el primero para el test
    }

    String codeSixDigit = String.format("%06d", validOtp);

    // Mock de caché
    doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
    doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

    boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

    assertTrue("Expected OTP to be valid", result);
}
}

```

```
package myproject.service;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

import java.lang.reflect.Method;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.junit.Before;
import org.junit.Test;

public class CalculatorServiceBeanTest {
    private CalculatorServiceBean calculatorServiceBean;

    @Before
    public void setUp() {
        calculatorServiceBean = spy(new CalculatorServiceBean() {
            @Override
            protected long gettimeSpaceUnixTime() {
                return 1725100000L; // valor fijo para pruebas determinísticas
            }
        });
    }

    @Test
    public void testPublicValidate_WithValidToken_ShouldReturnTrue() throws Exception {
        String keyWordString = "mySecretKey";
        String uniqueWord = keyWordString + "-" + "000000";
        byte[] keyBytes = uniqueWord.getBytes();

        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);

        long timeChanged = 1725100000L;
        int validOtp = (int) method.invoke(calculatorServiceBean, keyBytes, timeChanged);
        String codeSixDigit = String.format("%06d", validOtp);

        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertTrue("Expected OTP to be valid", result);
    }

    @Test
    public void testPublicValidate_WithInvalidToken_ShouldReturnFalse() throws Exception {
        String keyWordString = "mySecretKey";
        String uniqueWord = keyWordString + "-" + "000000";
        byte[] keyBytes = uniqueWord.getBytes();

        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);

        long timeChanged = 1725100000L;
        int validOtp = (int) method.invoke(calculatorServiceBean, keyBytes, timeChanged);
        int invalidOtp = (validOtp + 1) % 1000000;
        String codeSixDigit = String.format("%06d", invalidOtp);

        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertFalse("Expected OTP to be invalid", result);
    }
}
```


```
//para el vencido

@Before
    public void setUp() {
        calculatorServiceBean = spy(new CalculatorServiceBean() {
            @Override
            protected long gettimeSpaceUnixTime() {
                return 1725099880L; // tiempo fuera de rango para OTP vencido
            }
        });
    }

    @Test
    public void testPublicValidate_WithExpiredToken_ShouldReturnFalse() throws Exception {
        String keyWordString = "mySecretKey";
        String uniqueWord = keyWordString + "-" + "000000";
        byte[] keyBytes = uniqueWord.getBytes();

        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);

        long expiredTime = 1725099880L;
        int expiredOtp = (int) method.invoke(calculatorServiceBean, keyBytes, expiredTime);
        String codeSixDigit = String.format("%06d", expiredOtp);

        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertFalse("Expected OTP to be invalid as it is expired and outside the valid window", result);
    }
```
