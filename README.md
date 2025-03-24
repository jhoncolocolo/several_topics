# several_topics
```
import com.google.gson.Gson;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class ValidarTokenRsaTestOriginal {

    @Mock
    private ServicioRespuesta validateRsaPort;

    @Mock
    private Gson gson;

    @InjectMocks
    private ValidarTokenRsa validarTokenRsa;

    private Map<String, ValidarEstado> validateRsaMap;

    @BeforeEach
    public void setUp() {
        validateRsaMap = new HashMap<>();
        validateRsaMap.put("SATISFACTORIO", ValidarEstado.SATISFACTORIO);
        validateRsaMap.put("INVALIDO", ValidarEstado.INVALIDO);
        validateRsaMap.put("SIGUIENTE", ValidarEstado.SIGUIENTE);
        validarTokenRsa.initializeValidateRsaMap();
    }

    @Test
    public void testValidateToken_Satisfactorio() {
        String jsonResponse = "{\"contexto\":\"Validación de credenciales del usuario\",\"resultadosValidacionCredenciales\":[],\"intentoCodigoRespuesta\": \"SATISFACTORIO\",\"razonCodigoRespuesta\": \"OK\",\"metodosRetos\": {\"retos\": []}}";
        JsonElement jsonElement = JsonParser.parseString(jsonResponse);
        RespuestaValidacion respuestaValidacion = new Gson().fromJson(jsonElement, RespuestaValidacion.class);

        when(validateRsaPort.validateToken(any())).thenReturn(Mono.just(jsonElement));
        when(gson.fromJson(any(JsonElement.class), any())).thenReturn(respuestaValidacion);

        StepVerifier.create(validarTokenRsa.validateToken(new Credenciales("user", "token")))
                .expectNextMatches(result -> result.getStatus() == ValidarEstado.SATISFACTORIO)
                .verifyComplete();
    }

    @Test
    public void testValidateToken_Invalido() {
        String jsonResponse = "{\"contexto\":\"Validación de credenciales del usuario\",\"resultadosValidacionCredenciales\":[],\"intentoCodigoRespuesta\": \"INVALIDO\",\"razonCodigoRespuesta\": \"Credenciales inválidas\",\"metodosRetos\": {\"retos\": []}}";
        JsonElement jsonElement = JsonParser.parseString(jsonResponse);
        RespuestaValidacion respuestaValidacion = new Gson().fromJson(jsonElement, RespuestaValidacion.class);

        when(validateRsaPort.validateToken(any())).thenReturn(Mono.just(jsonElement));
        when(gson.fromJson(any(JsonElement.class), any())).thenReturn(respuestaValidacion);

        StepVerifier.create(validarTokenRsa.validateToken(new Credenciales("user", "token")))
                .expectError(DataPowerLoginException.class)
                .verify();
    }

    @Test
    public void testValidateToken_Siguiente() {
        String jsonResponse = "{\"contexto\":\"Validación de credenciales del usuario\",\"resultadosValidacionCredenciales\":[],\"intentoCodigoRespuesta\": \"SIGUIENTE\",\"razonCodigoRespuesta\": \"Siguiente paso\",\"metodosRetos\": {\"retos\": []}}";
        JsonElement jsonElement = JsonParser.parseString(jsonResponse);
        RespuestaValidacion respuestaValidacion = new Gson().fromJson(jsonElement, RespuestaValidacion.class);

        when(validateRsaPort.validateToken(any())).thenReturn(Mono.just(jsonElement));
        when(gson.fromJson(any(JsonElement.class), any())).thenReturn(respuestaValidacion);

        StepVerifier.create(validarTokenRsa.validateToken(new Credenciales("user", "token")))
                .expectNextMatches(result -> result.getStatus() == ValidarEstado.SIGUIENTE)
                .verifyComplete();
    }
}
```
