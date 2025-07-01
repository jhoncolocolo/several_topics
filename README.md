```
package myproject.service;

import static org.junit.Assert.*;
import static org.easymock.EasyMock.*;
import static org.powermock.api.easymock.PowerMock.*;

import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.Mac;

import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;

import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

@RunWith(PowerMockRunner.class)
@PrepareForTest({CalculatorServiceBean.class, myproject.utilitarios.utilityTool.class})
public class CalculatorServiceBeanTest {

    private CalculatorServiceBean calculatorServiceBean;

    @Before
    public void setUp() {
        calculatorServiceBean = createPartialMockForAllMethodsExcept(CalculatorServiceBean.class, "publicValidate");
    }

    @After
    public void tearDown() {
        calculatorServiceBean = null;
    }

    @Test
    public void testPublicValidate_ReturnsTrue_WhenTokenIsValid() throws Exception {
        String keyWordString = "mySecret";
        String codeSixDigit = "123456";
        long codeSixDigitLong = Long.parseLong(codeSixDigit);
        String uniqueWord = keyWordString + "-" + codeSixDigit;
        String trimmedUniqueWord = "trimmedWord";

        // Mock static utilityTool.trimCadena
        mockStatic(myproject.utilitarios.utilityTool.class);
        expect(myproject.utilitarios.utilityTool.trimCadena(uniqueWord)).andReturn(trimmedUniqueWord);

        // Mock getTimeSpace
        expect(calculatorServiceBean.getTimeSpace()).andReturn(240);

        // Mock private validateToken to return true
        expectPrivate(calculatorServiceBean, "validateToken",
                keyWordString, trimmedUniqueWord, codeSixDigitLong, 240).andReturn(true);

        replayAll();

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertTrue(result);

        verifyAll();
    }

    @Test
    public void testPublicValidate_ReturnsFalse_WhenTokenIsInvalid() throws Exception {
        String keyWordString = "mySecret";
        String codeSixDigit = "123456";
        long codeSixDigitLong = Long.parseLong(codeSixDigit);
        String uniqueWord = keyWordString + "-" + codeSixDigit;
        String trimmedUniqueWord = "trimmedWord";

        // Mock static utilityTool.trimCadena
        mockStatic(myproject.utilitarios.utilityTool.class);
        expect(myproject.utilitarios.utilityTool.trimCadena(uniqueWord)).andReturn(trimmedUniqueWord);

        // Mock getTimeSpace
        expect(calculatorServiceBean.getTimeSpace()).andReturn(240);

        // Mock private validateToken to return false
        expectPrivate(calculatorServiceBean, "validateToken",
                keyWordString, trimmedUniqueWord, codeSixDigitLong, 240).andReturn(false);

        replayAll();

        boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

        assertFalse(result);

        verifyAll();
    }

    @Test
    public void testGenerateConvertedToken_ValidatesFormat() throws Exception {
        byte[] keyBytes = "secret".getBytes();
        long timeSpace = 1234567890L;

        // Using real methods, so no need for mocks here
        int token = calculatorServiceBean.generateConvertedToken(keyBytes, timeSpace);

        assertTrue(token >= 0 && token <= 999999);
    }

@Test
public void testPublicValidate_WithRealExecution_AndMockedDependencies() throws Exception {
    calculatorServiceBean = new CalculatorServiceBean();

    String keyWordString = "mySecret";
    String codeSixDigit = "123456";
    String uniqueWord = keyWordString + "-" + codeSixDigit;
    String trimmedUniqueWord = "trimmedWord";

    // Mock utilityTool.trimCadena
    mockStatic(myproject.utilitarios.utilityTool.class);
    expect(myproject.utilitarios.utilityTool.trimCadena(uniqueWord)).andReturn(trimmedUniqueWord);

    // Mock Mac.getInstance
    mockStatic(Mac.class);
    Mac mockMac = createMock(Mac.class);
    expect(Mac.getInstance("HmacSHA1")).andReturn(mockMac);

    // Mock SecretKeySpec constructor
    SecretKeySpec mockSecretKeySpec = createMock(SecretKeySpec.class);
    expectNew(SecretKeySpec.class, anyObject(byte[].class), eq("HmacSHA1")).andReturn(mockSecretKeySpec);

    // Mock mac.init
    mockMac.init(mockSecretKeySpec);
    expectLastCall().once();

    // Mock mac.doFinal
    expect(mockMac.doFinal(anyObject(byte[].class))).andReturn(new byte[] { 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 });

    // Mock cacheContainsKey and cachePutObject
    expectPrivate(calculatorServiceBean, "cacheContainsKey", anyObject(String.class)).andReturn(false);
    expectPrivate(calculatorServiceBean, "cachePutObject", anyObject(String.class), anyObject(String.class), anyObject(String.class)).andReturn(null);

    replayAll();

    boolean result = calculatorServiceBean.publicValidate(keyWordString, codeSixDigit);

    assertTrue(result);

    verifyAll();
}

}

```
