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
```java
@RunWith(PowerMockRunner.class)
@PrepareForTest({CalculatorServiceBean.class, UsuarioLockedExec.class})
public class CalculatorServiceBeanTest {
    
    @Mock
    private QueryExecutor mockQueryExecutor;

    @Mock
    private UsuarioLockedExec mockUsuarioLockedExec;

    @InjectMocks
    private CalculatorServiceBean calculatorServiceBean;

    @Before
    public void setUp() throws Exception {
        MockitoAnnotations.initMocks(this);
        PowerMockito.whenNew(UsuarioLockedExec.class).withNoArguments().thenReturn(mockUsuarioLockedExec);
        calculatorServiceBean = PowerMockito.spy(new CalculatorServiceBean());
        doReturn(false).when(calculatorServiceBean).cacheContainsKey(anyString());
        doNothing().when(calculatorServiceBean).cachePutObject(anyString(), anyString(), anyString());
    }

    @Test
    public void testPublicValidate_WithValidOtp_ShouldReturnTrue() throws Exception {
        UsuarioDTO usuarioDTO = new UsuarioDTO();
        usuarioDTO.setIdentificacion("L00001");
        usuarioDTO.setNombre("benito");
        usuarioDTO.setUsuario("benito.alvez");
        usuarioDTO.setApplication("ForOtp");

        when(mockQueryExecutor.findUsuarioByUsername("benito.alvez")).thenReturn(usuarioDTO);

        UsuarioLockedDTO usuarioLockedDTO = new UsuarioLockedDTO();
        usuarioLockedDTO.setUsuario("benito.alvez");
        usuarioLockedDTO.setEstado(true);

        when(mockUsuarioLockedExec.findUserEstado("benito.alvez")).thenReturn(usuarioLockedDTO);

        long currentUnixTime = System.currentTimeMillis() / 1000;
        String keyWordString = "benito.alvez";
        byte[] keyBytes = ("ForOtp-000000").getBytes();
        Method method = CalculatorServiceBean.class.getDeclaredMethod("generateConvertedToken", byte[].class, long.class);
        method.setAccessible(true);
        long validOtp = (long) method.invoke(calculatorServiceBean, keyBytes, currentUnixTime);
        String otp = String.format("%06d", validOtp);

        boolean result = calculatorServiceBean.publicValidate(keyWordString, otp);
        assertTrue(result);
    }

    @Test
    public void testPublicValidate_WithInvalidOtp_ShouldReturnFalse() throws Exception {
        UsuarioDTO usuarioDTO = new UsuarioDTO();
        usuarioDTO.setIdentificacion("L00001");
        usuarioDTO.setNombre("benito");
        usuarioDTO.setUsuario("benito.alvez");
        usuarioDTO.setApplication("ForOtp");

        when(mockQueryExecutor.findUsuarioByUsername("benito.alvez")).thenReturn(usuarioDTO);

        UsuarioLockedDTO usuarioLockedDTO = new UsuarioLockedDTO();
        usuarioLockedDTO.setUsuario("benito.alvez");
        usuarioLockedDTO.setEstado(true);

        when(mockUsuarioLockedExec.findUserEstado("benito.alvez")).thenReturn(usuarioLockedDTO);

        String keyWordString = "benito.alvez";
        String invalidOtp = "000000";

        boolean result = calculatorServiceBean.publicValidate(keyWordString, invalidOtp);
        assertFalse(result);
    }
}
```


