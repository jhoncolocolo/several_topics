```
package myProject.service;

import static org.mockito.Mockito.*;
import static org.junit.Assert.*;

import java.util.Arrays;
import java.util.List;

import myProject.domain.entity.MyUserData;
import myProject.domain.entity.UserArtefactoEmisoraId;
import myProject.domain.entity.UserDataEntity;
import myProject.domain.entity.UserDataId;
import myProject.repository.dao.UserArtefactoEmisoraDaoRepository;

import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

public class RegistrarImplServiceTest {

    @Mock
    private UserArtefactoEmisoraDaoRepository userArtefactoEmisoraDaoRepository;

    private RegistrarImplService registrarImplService;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        registrarImplService = new RegistrarImplService(userArtefactoEmisoraDaoRepository);
    }

    @Test
    public void testDisableAllUserArtefactoEmisoraByArtefactoId_updatesCondition() {
        // Arrange
        String artefactoId = "ART123";
        String user = "usuario1";

        // Creamos datos simulados
        UserDataEntity entityActivo = new UserDataEntity();
        entityActivo.setCondition("A");
        entityActivo.setId(buildMyUserData(user, artefactoId, "EMISORA1"));

        UserDataEntity entityInactivo = new UserDataEntity();
        entityInactivo.setCondition("I");
        entityInactivo.setId(buildMyUserData(user, artefactoId, "EMISORA2"));

        List<UserDataEntity> mockList = Arrays.asList(entityActivo, entityInactivo);

        when(userArtefactoEmisoraDaoRepository.findAllByIdArtefacto(eq(artefactoId), eq(user), anyList()))
                .thenReturn(mockList);

        // Act
        registrarImplService.disableAllUserArtefactoEmisoraByArtefactoId(artefactoId, user);

        // Assert
        ArgumentCaptor<List<UserDataEntity>> captor = ArgumentCaptor.forClass(List.class);
        verify(userArtefactoEmisoraDaoRepository, times(1)).save(captor.capture());

        List<UserDataEntity> savedEntities = captor.getValue();

        // Verificamos que el primero cambió de A -> I
        UserDataEntity updatedEntity1 = savedEntities.get(0);
        assertEquals("I", updatedEntity1.getCondition());

        // El segundo ya estaba I y se mantiene
        UserDataEntity updatedEntity2 = savedEntities.get(1);
        assertEquals("I", updatedEntity2.getCondition());
    }

    // Método auxiliar para crear la estructura del ID
    private MyUserData buildMyUserData(String usuario, String artefactoId, String emisora) {
        UserDataId userDataId = new UserDataId();
        userDataId.setUsuarioFk(usuario);
        userDataId.setArtefactoId(artefactoId);

        MyUserData myUserData = new MyUserData();
        myUserData.setUserDataKey(userDataId);
        myUserData.setEmisoraFk(emisora);

        return myUserData;
    }
}

```
