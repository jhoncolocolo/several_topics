```
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.function.Function;

public class GenericSorter {

    /**
     * Ordena de forma genérica una lista por un campo especificado, de forma ascendente o descendente.
     * 
     * @param lista         Lista de cualquier tipo
     * @param campo         Campo sobre el cual ordenar (soporta "fecha_modificacion" y "application" para AnyDTO)
     * @param ascendente    true para ascendente, false para descendente
     * @param <T>           Tipo de objeto de la lista
     */
    public static <T> void ordenarListaPorCampo(List<T> lista, String campo, boolean ascendente) {
        if (lista == null || lista.isEmpty()) return;

        Comparator<T> comparator;

        T firstElement = lista.get(0);
        if (firstElement instanceof UsuarioDTO) {
            UsuarioDTO dummy = (UsuarioDTO) firstElement;

            if ("fecha_modificacion".equalsIgnoreCase(campo)) {
                SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
                comparator = Comparator.comparing((T obj) -> {
                    try {
                        String fechaStr = ((UsuarioDTO) obj).getFechaModificacion();
                        return sdf.parse(fechaStr);
                    } catch (ParseException e) {
                        throw new RuntimeException(e);
                    }
                });
            } else if ("application".equalsIgnoreCase(campo)) {
                comparator = Comparator.comparing(obj -> ((UsuarioDTO) obj).getApplication());
            } else {
                throw new IllegalArgumentException("Campo no soportado: " + campo);
            }
        } else {
            throw new IllegalArgumentException("Tipo no soportado: " + firstElement.getClass().getName());
        }

        if (!ascendente) {
            comparator = comparator.reversed();
        }

        lista.sort(comparator);
    }
}

@Test
public void testOrdenarUsuariosPorFechaModificacionDesc() {
    List<UsuarioDTO> usuarios = new ArrayList<>();
    usuarios.add(new UsuarioDTO("L00001", "benito", "benito.alvez", "appB", "2020-10-16 01:02:03.999"));
    usuarios.add(new UsuarioDTO("L00002", "alan", "alan.roldan", "appC", "2024-05-06 01:02:03.999"));
    usuarios.add(new UsuarioDTO("L00003", "roberta", "roberta.canizales", "appA", "2018-01-06 01:02:03.999"));

    // Invocar el método genérico de orden
    GenericSorter.ordenarListaPorCampo(usuarios, "fecha_modificacion", false);

    // Validar orden descendente
    assertEquals("L00002", usuarios.get(0).getIdentificacion());
    assertEquals("L00001", usuarios.get(1).getIdentificacion());
    assertEquals("L00003", usuarios.get(2).getIdentificacion());

    usuarios.forEach(System.out::println);
}

@Test
public void testOrdenarUsuariosPorApplicationAsc() {
    List<UsuarioDTO> usuarios = new ArrayList<>();
    usuarios.add(new UsuarioDTO("L00001", "benito", "benito.alvez", "appB", "2020-10-16 01:02:03.999"));
    usuarios.add(new UsuarioDTO("L00002", "alan", "alan.roldan", "appC", "2024-05-06 01:02:03.999"));
    usuarios.add(new UsuarioDTO("L00003", "roberta", "roberta.canizales", "appA", "2018-01-06 01:02:03.999"));

    // Invocar el método genérico de orden
    GenericSorter.ordenarListaPorCampo(usuarios, "application", true);

    // Validar orden ascendente por aplicación
    assertEquals("appA", usuarios.get(0).getApplication());
    assertEquals("appB", usuarios.get(1).getApplication());
    assertEquals("appC", usuarios.get(2).getApplication());

    usuarios.forEach(System.out::println);
}
```
