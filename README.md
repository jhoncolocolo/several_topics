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
