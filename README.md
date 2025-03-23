# several_topics
```
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import reactor.core.publisher.Mono;
import reactor.test.StepVerifier;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class ProcesadorCredencialesTest {

    @Mock
    private ProcesadorCredenciales procesadorCredencialesMock;

    @InjectMocks
    private ProcesadorCredenciales procesadorCredenciales;

    @Test
    public void testProcesarCredenciales() {
        // Configura los datos de entrada
        Credenciales credenciales = Credenciales.builder()
                .usuario("testUsuario")
                .token("testToken")
                .build();

        // Configura los mocks para simular las respuestas de las librerías externas
        JsonObject remoteRequestJson = new JsonObject();
        remoteRequestJson.addProperty("token", "testToken");
        RemoteRequestParam remoteRequestParam = new RemoteRequestParam();
        remoteRequestParam.setAuthToken("testToken");

        when(procesadorCredencialesMock.insertarTokenAutenticacion(any(JsonElement.class)))
                .thenReturn(Mono.just(remoteRequestParam));

        JsonObject dataPowerJson = JsonParser.parseString("{\"contexto\": \"Validación de credenciales del usuario\", \"resultadosValidacionCredenciales\": [{\"metodoRespuesta\": \"Contraseña incorrecta\", \"codigoMetodo\": \"401\", \"razonCodigo\": \"Credenciales inválidas\", \"atributosAutenticacion\": {}}], \"intentoCodigoRespuesta\": \"401\", \"razonCodigoRespuesta\": \"Credenciales inválidas\", \"metodosRetos\": {\"retos\": [{\"metodoId\": \"preguntaSeguridad\", \"metodoRequerido\": true}]}}").getAsJsonObject();

        when(procesadorCredencialesMock.obtenerDatosDatapower(any(RemoteRequestParam.class)))
                .thenReturn(Mono.just(dataPowerJson));

        // Llama al método a probar
        Mono<JsonElement> resultado = procesadorCredenciales.procesarCredenciales(credenciales);

        // Verifica el resultado
        StepVerifier.create(resultado)
                .expectNextMatches(jsonElement -> jsonElement.getAsJsonObject().equals(dataPowerJson))
                .verifyComplete();
    }
}
```
