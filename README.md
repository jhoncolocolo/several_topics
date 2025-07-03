```
 package myproject.service;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

import java.lang.reflect.Method;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import myproject.dao.QueryExecutor;
import myproject.model.UsuarioDTO;
import org.junit.Before;
import org.junit.Test;

public class CalculatorServiceBeanTest {
    private CalculatorServiceBean calculatorServiceBean;
    private QueryExecutor mockQueryExecutor;
    private long currentUnixTime;
    private byte[] keyBytes;
    private String keyWordString;

    @Before
    public void setUp() throws Exception {
        currentUnixTime = System.currentTimeMillis() / 1000;
        mockQueryExecutor = mock(QueryExecutor.class);
        calculatorServiceBean = spy(new CalculatorServiceBean(mockQueryExecutor) {
            @Override
            protected long gettimeSpaceUnixTime() {
                return currentUnixTime;
            }
        });
        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());
    }

    private void configureUsuarioDTO(String identificacion, String nombre, String usuario, String application) {
        UsuarioDTO usuarioDTO = new UsuarioDTO();
        usuarioDTO.setIdentificacion(identificacion);
        usuarioDTO.setNombre(nombre);
        usuarioDTO.setUsuario(usuario);
        usuarioDTO.setApplication(application);
        this.keyWordString = usuario;
        this.keyBytes = (application + "-000000").getBytes();
        when(mockQueryExecutor.findUsuarioByUsername(usuario)).thenReturn(usuarioDTO);
    }

    private String generateOtpAtTime(long time) throws Exception {
        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);
        int otp = (int) method.invoke(calculatorServiceBean, keyBytes, time);
        return String.format("%06d", otp);
    }

    @Test
    public void testPublicValidate_WithValidToken_ShouldReturnTrue() throws Exception {
        configureUsuarioDTO("L00001", "benito", "benito.alvez", "ForOtp");
        String codeSixDigit = generateOtpAtTime(currentUnixTime);
        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);
        assertTrue(result);
    }

    @Test
    public void testPublicValidate_WithExpiredToken_ShouldReturnFalse() throws Exception {
        configureUsuarioDTO("L00002", "ana", "ana.gomez", "ForOtp");
        String codeSixDigit = generateOtpAtTime(currentUnixTime - 500);
        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);
        assertFalse(result);
    }

    @Test
    public void testPublicValidate_WithInvalidOtp_ShouldReturnFalse() {
        configureUsuarioDTO("L00003", "carlos", "carlos.martin", "ForOtp");
        String invalidOtp = "999999";
        boolean result = calculatorServiceBean.publicValidate(keyWordString, invalidOtp);
        assertFalse(result);
    }
}

```
--------------------------------------------------------------------------------
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
    private long currentUnixTime;

    @Before
    public void setUp() {
        currentUnixTime = System.currentTimeMillis() / 1000;
        calculatorServiceBean = spy(new CalculatorServiceBean() {
            @Override
            protected long gettimeSpaceUnixTime() {
                return currentUnixTime;
            }
        });
    }

    @Test
    public void testPublicValidate_WithValidToken_ShouldReturnTrue() throws Exception {
        String keyWordString = "mySecretKey";
        String uniqueWord = keyWordString + "-000000";
        byte[] keyBytes = uniqueWord.getBytes();

        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);

        long validTime = currentUnixTime;
        int validOtp = (int) method.invoke(calculatorServiceBean, keyBytes, validTime);
        String codeSixDigit = String.format("%06d", validOtp);

        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertTrue("Expected OTP to be valid and within the current window", result);
    }

    @Test
    public void testPublicValidate_WithExpiredToken_ShouldReturnFalse() throws Exception {
        String keyWordString = "mySecretKey";
        String uniqueWord = keyWordString + "-000000";
        byte[] keyBytes = uniqueWord.getBytes();

        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);

        long expiredTime = currentUnixTime - 500; // fuera de rango de ventana
        int expiredOtp = (int) method.invoke(calculatorServiceBean, keyBytes, expiredTime);
        String codeSixDigit = String.format("%06d", expiredOtp);

        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertFalse("Expected OTP to be invalid as it is expired", result);
    }

    @Test
    public void testPublicValidate_WithInvalidOtp_ShouldReturnFalse() {
        String keyWordString = "mySecretKey";
        String invalidOtp = "999999"; // OTP inválido asegurado

        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());

        boolean result = calculatorServiceBean.publicValidate(keyWordString, invalidOtp);

        assertFalse("Expected OTP to be invalid due to incorrect token", result);
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
    private long currentUnixTime;
    private final String keyWordString = "mySecretKey";
    private final String uniqueWord = keyWordString + "-000000";
    private final byte[] keyBytes = uniqueWord.getBytes();

    @Before
    public void setUp() {
        currentUnixTime = System.currentTimeMillis() / 1000;
        calculatorServiceBean = spy(new CalculatorServiceBean() {
            @Override
            protected long gettimeSpaceUnixTime() {
                return currentUnixTime;
            }
        });
        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());
    }

    private String generateOtpAtTime(long time) throws Exception {
        Method method = CalculatorServiceBean.class.getDeclaredMethod(
            "generateConvertedToken", byte[].class, long.class
        );
        method.setAccessible(true);
        int otp = (int) method.invoke(calculatorServiceBean, keyBytes, time);
        return String.format("%06d", otp);
    }

    @Test
    public void testPublicValidate_WithValidToken_ShouldReturnTrue() throws Exception {
        String codeSixDigit = generateOtpAtTime(currentUnixTime);
        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);
        assertTrue("Expected OTP to be valid and within the current window", result);
    }

    @Test
    public void testPublicValidate_WithExpiredToken_ShouldReturnFalse() throws Exception {
        String codeSixDigit = generateOtpAtTime(currentUnixTime - 500);
        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);
        assertFalse("Expected OTP to be invalid as it is expired", result);
    }

    @Test
    public void testPublicValidate_WithInvalidOtp_ShouldReturnFalse() {
        String invalidOtp = "999999";
        boolean result = calculatorServiceBean.publicValidate(keyWordString, invalidOtp);
        assertFalse("Expected OTP to be invalid due to incorrect token", result);
    }
}


```
