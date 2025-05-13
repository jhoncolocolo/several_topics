```
public class CredencialService {

    private final Map<String, Map<String, ModuloCredencialConfiguracion.Credencial>> paises;

    public CredencialService(Map<String, Map<String, ModuloCredencialConfiguracion.Credencial>> paises) {
        this.paises = paises;
    }

    /**
     * Obtiene una credencial por módulo y país.
     * Si el país es null o vacío, busca solo en "default".
     */
    public ModuloCredencialConfiguracion.Credencial obtenerCredencial(String modulo, String pais) {
        // Validar el parámetro
        if (modulo == null || modulo.isBlank()) {
            throw new IllegalArgumentException("El nombre del módulo no puede ser nulo o vacío");
        }

        // Si hay país, intenta buscar primero en ese país
        if (pais != null && !pais.isBlank()) {
            ModuloCredencialConfiguracion.Credencial credencial = buscarEnPais(modulo, pais);
            if (credencial != null) {
                return credencial;
            }
        }

        // Si no encontró en el país o no se proporcionó, buscar en 'default'
        ModuloCredencialConfiguracion.Credencial credencial = buscarEnPais(modulo, "default");
        if (credencial != null) {
            return credencial;
        }

        // Retornar el default.default
        return buscarEnPais("default", "default");
    }

    /**
     * Busca una credencial dentro del mapa de un país específico.
     */
    private ModuloCredencialConfiguracion.Credencial buscarEnPais(String modulo, String pais) {
        Map<String, ModuloCredencialConfiguracion.Credencial> modulos = paises.get(pais);
        if (modulos != null) {
            return modulos.get(modulo);
        }
        return null;
    }
}
```
