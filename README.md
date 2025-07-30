package com.example.repositorios;

import com.example.config.EntityManagerFactorySingleton; // Asegúrate de que esta ruta sea correcta
import jakarta.persistence.EntityManager;
import jakarta.persistence.Query;
import jakarta.persistence.NoResultException; // Importar si se usa getSingleResult()

import java.util.Collection;
import java.util.Collections; // Para Collections.nCopies o List.of si se necesita para IN clause
import java.util.List;
import java.util.stream.Collectors; // Para Java 8+ streamCollectors

public class UserRepository {

    // 1. Define la consulta SQL con marcadores de posición (placeholders)
    // Para parámetros nombrados: :parametro
    // Para parámetros posicionales: ?1, ?2, etc. (menos recomendado para más de 1-2 parámetros)
    // Para cláusulas IN: Es un poco más complejo, JPA no soporta directamente Collection para IN nativo
    // La solución más robusta para IN es generar dinámicamente el placeholder.

    // Usaremos un enfoque híbrido: :email para el email y generar los placeholders para my_usernames
    // Nota: Aunque JPA permite createNativeQuery, la capacidad de bindear Collection a IN
    // directamente es para JPQL. Para SQL nativo, a menudo necesitas construir la cadena IN.
    // SIN EMBARGO, incluso construyendo la cadena IN, DEBEMOS usar parámetros para CADA VALOR.

    // A. Opción Segura (recomendada): Construir la cláusula IN con parámetros individuales
    // La consulta inicial no tiene los usernames porque los añadiremos como parámetros.
    private static final String SQL_DELETE_CUSTOM_BASE = "DELETE FROM users WHERE email = :email AND username NOT IN (%s)";


    public boolean deleteCustom(String email, Collection<String> myUsernames) {
        EntityManager em = null; // Inicializar a null para asegurar el finally
        boolean result = false;

        if (myUsernames == null || myUsernames.isEmpty()) {
            // Manejar caso de lista vacía: el NOT IN (vacío) es problemático.
            // Depende de tu lógica de negocio: ¿Debería borrar si no hay usernames para excluir?
            // Aquí, por simplicidad, asumimos que no hace nada si la lista es vacía.
            // O podrías borrar simplemente por email si eso es lo que quieres.
            System.out.println("No usernames provided for exclusion. No custom delete performed.");
            return false;
        }

        // Generar los placeholders para la cláusula IN.
        // Ej: si myUsernames tiene 3 elementos, generará "?1, ?2, ?3"
        // O ':username1, :username2, :username3' si usas parámetros nombrados dinámicos.
        // Usaremos ":p" + indice para el nombre del parámetro.
        List<String> placeholders = myUsernames.stream()
            .map(u -> ":p" + myUsernames.stream().collect(Collectors.toList()).indexOf(u)) // Genera :p0, :p1, etc.
            .collect(Collectors.toList());

        String inClausePlaceholders = String.join(", ", placeholders);

        // Construir la SQL final con los placeholders IN
        String finalSql = String.format(SQL_DELETE_CUSTOM_BASE, inClausePlaceholders);

        try {
            em = EntityManagerFactorySingleton.INSTANCIA.getEntityManager();
            em.getTransaction().begin(); // Iniciar transacción

            Query query = em.createNativeQuery(finalSql);

            // Setear el parámetro de email
            query.setParameter("email", email);

            // Setear cada parámetro de username individualmente
            int i = 0;
            for (String username : myUsernames) {
                query.setParameter("p" + i, username);
                i++;
            }

            // Ejecutar la actualización (DELETE)
            int rowsAffected = query.executeUpdate();

            em.getTransaction().commit(); // Confirmar transacción
            result = rowsAffected > 0; // Si se afectaron filas, fue exitoso

        } catch (Exception e) {
            if (em != null && em.getTransaction().isActive()) {
                em.getTransaction().rollback(); // Revertir en caso de error
            }
            e.printStackTrace(); // O loguear la excepción apropiadamente
            result = false;
        } finally {
            if (em != null) {
                em.close(); // Cerrar el EntityManager siempre
            }
        }
        return result;
    }
}


import org.junit.Test;
import org.mockito.ArgumentCaptor;

import java.util.Arrays;
import java.util.Collection;
import java.util.List;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.verify;

public class UserRepositoryTest_Whitebox {

    // Tus mocks y el captor de SQL...
    // @Mock private EntityManager mockEntityManager;
    // @Mock private Query mockQuery;
    // private ArgumentCaptor<String> sqlCaptor;
    // private ArgumentCaptor<String> paramNameCaptor;
    // private ArgumentCaptor<Object> paramValueCaptor;

    // ... (Tu setUp() se mantiene igual)

    @Test
    public void testDeleteCustom_logginSqlFinal() throws Exception {
        // GIVEN
        String email = "test@example.com";
        Collection<String> usernames = Arrays.asList("user1", "user2", "user3");

        // WHEN
        userRepository.deleteCustom(email, usernames);

        // THEN
        // 1. Capturar el SQL base
        verify(mockEntityManager).createNativeQuery(sqlCaptor.capture());
        String capturedSql = sqlCaptor.getValue();
        
        // 2. Capturar todos los parámetros
        // El comportamiento para capturar ya se definió en setUp()
        verify(mockQuery).setParameter(anyString(), any());
        List<String> allCapturedParamNames = paramNameCaptor.getAllValues();
        List<Object> allCapturedParamValues = paramValueCaptor.getAllValues();

        // 3. Reconstruir la consulta completa con los parámetros
        //    (Esto es lo que nos interesa)
        String finalSql = capturedSql;
        for (int i = 0; i < allCapturedParamNames.size(); i++) {
            String paramName = allCapturedParamNames.get(i);
            Object paramValue = allCapturedParamValues.get(i);

            // Reemplazar el placeholder por el valor, escapando para SQL si es un String.
            // Para fines de logging, solo reemplazaremos el placeholder por el valor entre comillas.
            if (paramValue instanceof String) {
                finalSql = finalSql.replace(":" + paramName, "'" + paramValue + "'");
            } else {
                finalSql = finalSql.replace(":" + paramName, String.valueOf(paramValue));
            }
        }
        
        System.out.println("--- Consulta SQL final reconstruida ---");
        System.out.println(finalSql);
        System.out.println("------------------------------------");

        // Ahora puedes hacer tus verificaciones, sabiendo exactamente cómo se ve la consulta.
        // Ejemplo:
        String expectedSqlFragment = "WHERE email = 'test@example.com' AND username NOT IN ('user1', 'user2', 'user3')";
        // Nota: El orden de los parámetros en el string `finalSql` depende del orden de la colección original.
        assertEquals(true, finalSql.contains(expectedSqlFragment));
        
        // ... (el resto de tus verificaciones)
    }
}
