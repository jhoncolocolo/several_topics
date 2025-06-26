 https://www.udemy.com/course/aws-certified-developer-associate-dva/learn/lecture/36521046#overview

 package myproject.service;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.assertEquals;

import java.lang.reflect.Method; // Importar la clase Method

public class CalculatorServiceBeanTest {

    private CalculatorServiceBean calculatorServiceBean;

    @Before
    public void setUp() {
        // Inicializar la instancia de tu EJB.
        // En un entorno de prueba real, podrías querer mockear dependencias
        // o usar un contenedor embebido, pero para esta prueba de unidad simple,
        // una instancia directa es suficiente ya que no estamos probando EJB features.
        calculatorServiceBean = new CalculatorServiceBean();
    }

    @Test
    public void testPrivateAddMethod() throws Exception {
        // 1. Obtener el objeto Method para el método privado "add"
        //    Los parámetros son el nombre del método y sus tipos de parámetros.
        Method privateAddMethod = CalculatorServiceBean.class.getDeclaredMethod("add", int.class, int.class);

        // 2. Hacer que el método privado sea accesible
        //    Esto es crucial para eludir las restricciones de acceso.
        privateAddMethod.setAccessible(true);

        // 3. Invocar el método privado
        //    Los parámetros son la instancia del objeto y los argumentos para el método.
        //    El resultado se devuelve como un Object, por lo que lo casteamos a int.
        int result = (int) privateAddMethod.invoke(calculatorServiceBean, 5, 3);

        // 4. Afirmar el resultado
        assertEquals("El método privado 'add' debería sumar correctamente", 8, result);
    }

    @Test
    public void testPublicAddMethod() {
        // Prueba para el método público (enfoque recomendado)
        int result = calculatorServiceBean.publicAdd(10, 7);
        assertEquals("El método público 'publicAdd' debería sumar correctamente", 17, result);
    }
}
