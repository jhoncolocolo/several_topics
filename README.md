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

import java.util.*;
import java.util.function.Function;

public class GenericSorter {

    /**
     * Ordena genéricamente una lista por el campo indicado por la extractorFunction.
     *
     * @param lista             Lista de elementos de tipo T
     * @param extractorFunction Función que extrae el campo sobre el que se ordena
     * @param ascendente        true para ascendente, false para descendente
     * @param <T>               Tipo del objeto en la lista
     */
    public static <T> void ordenarListaPorCampo(
            List<T> lista,
            Function<T, ? extends Comparable> extractorFunction,
            boolean ascendente) {

        Comparator<T> comparator = Comparator.comparing(extractorFunction, Comparator.nullsLast(Comparator.naturalOrder()));
        if (!ascendente) {
            comparator = comparator.reversed();
        }
        lista.sort(comparator);
    }
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

Ordenamineto multiple
```
✅ Método genérico de ordenación por múltiples campos
java
Copiar
Editar
import java.util.*;
import java.util.function.Function;

public class GenericSorter {

    public static <T> void ordenarListaPorMultiplesCampos(
            List<T> lista,
            List<Function<T, ? extends Comparable>> extractors,
            List<Boolean> ascendentes) {

        if (extractors.size() != ascendentes.size()) {
            throw new IllegalArgumentException("El número de extractores y banderas de orden deben coincidir");
        }

        Comparator<T> comparator = Comparator.comparing(
                extractors.get(0),
                Comparator.nullsLast(Comparator.naturalOrder())
        );

        if (!ascendentes.get(0)) {
            comparator = comparator.reversed();
        }

        for (int i = 1; i < extractors.size(); i++) {
            Comparator<T> nextComparator = Comparator.comparing(
                    extractors.get(i),
                    Comparator.nullsLast(Comparator.naturalOrder())
            );
            if (!ascendentes.get(i)) {
                nextComparator = nextComparator.reversed();
            }
            comparator = comparator.thenComparing(nextComparator);
        }

        lista.sort(comparator);
    }
}
✅ Ejemplo de uso en tu caso:
java
Copiar
Editar
List<UsuarioDTO> usuarios = new ArrayList<>();
usuarios.add(new UsuarioDTO("L00001", "benito", "benito.alvez", "appB", "2020-10-16 01:02:03.999"));
usuarios.add(new UsuarioDTO("L00002", "alan", "alan.roldan", "appC", "2024-05-06 01:02:03.999"));
usuarios.add(new UsuarioDTO("L00004", "luisa", "luisa.orrego", "appA", "2025-04-06 01:02:03.999"));
usuarios.add(new UsuarioDTO("L00003", "roberta", "roberta.canizales", "appA", "2018-01-06 01:02:03.999"));

// Ordenar por aplicación (ascendente), luego por fecha de modificación (descendente)
GenericSorter.ordenarListaPorMultiplesCampos(
    usuarios,
    Arrays.asList(UsuarioDTO::getApplication, UsuarioDTO::getFechaModificacion),
    Arrays.asList(true, false) // ascendente para aplicación, descendente para fecha
);

usuarios.forEach(System.out::println);
✅ Resultado esperado
bash
Copiar
Editar
UsuarioDTO{identificacion='L00004', nombre='luisa', usuario='luisa.orrego', application='appA', fechaModificacion='2025-04-06 01:02:03.999'}
UsuarioDTO{identificacion='L00003', nombre='roberta', usuario='roberta.canizales', application='appA', fechaModificacion='2018-01-06 01:02:03.999'}
UsuarioDTO{identificacion='L00001', nombre='benito', usuario='benito.alvez', application='appB', fechaModificacion='2020-10-16 01:02:03.999'}
UsuarioDTO{identificacion='L00002', nombre='alan', usuario='alan.roldan', application='appC', fechaModificacion='2024-05-06 01:02:03.999'}
```
