```
# Propuesta de mejora: Soporte para configuración de secretos por país

## 📌 Contexto

Actualmente, la aplicación lee un archivo de configuración YAML que contiene un conjunto de secretos utilizados por diferentes módulos funcionales. Sin embargo, esta estructura está diseñada para trabajar con un único conjunto de secretos globales, lo cual presenta limitaciones cuando se desea operar en un entorno multi-país donde los valores sensibles, como `clientId`, `apiKey` o `ruta`, pueden variar por región o país.

---

## ❗ Problema identificado

La configuración actual no permite distinguir ni aplicar secretos personalizados por país, lo que genera los siguientes inconvenientes:

- No se pueden definir `clientId` o `token` distintos por país para un mismo módulo.
- La estructura global limita la escalabilidad y flexibilidad para nuevas regiones.
- No existe una herencia clara de valores comunes que puedan sobreescribirse de forma controlada.

---

## ⚠️ Consecuencias

### Consecuencias negativas del enfoque actual

- 🔁 **Duplicación de lógica** para manejar variaciones regionales manualmente.
- 💥 **Errores de configuración** por sobrescritura no controlada de claves entre países.
- 🚫 **Imposibilidad de crecimiento** a nuevas regiones sin refactorizar código.
- 🔒 **Riesgo de seguridad** si las credenciales se mezclan o se reutilizan de forma incorrecta.

### Consecuencias positivas esperadas con la nueva solución

- 🌍 Soporte natural para múltiples países y regiones.
- 🧬 Herencia de valores comunes desde un país base (`default`) con posibilidad de sobrescritura por país.
- 🔐 Seguridad reforzada: las credenciales son únicas por país y se enriquecen desde Azure Key Vault.
- 🧩 Estructura extensible y fácil de mantener a largo plazo.
- 🧪 Mejora de la cobertura y claridad en pruebas unitarias.

---

## 🔁 Opciones consideradas

### 1. **Seguir con estructura global actual**
- ✅ Sin cambios estructurales.
- ❌ No resuelve el problema de multi-país.
- ❌ Alto riesgo de errores con múltiples entornos.

### 2. **Crear un archivo YAML por país**
- ✅ Separa claramente las configuraciones.
- ❌ Mayor complejidad de mantenimiento.
- ❌ No permite herencia ni valores comunes.
- ❌ Requiere lógica adicional para cargar múltiples archivos.

### 3. ✅ **(Propuesta actual) Refactor a estructura por país con herencia**
- ✅ Un solo archivo YAML estructurado por país.
- ✅ Herencia automática desde `default`.
- ✅ Enriquecimiento dinámico con Key Vault.
- ✅ Flexible, seguro y escalable.

---

## ✅ Propuesta

Implementar una estructura de configuración basada en una lista de países (`countries`), donde cada uno tenga su propio mapa de secretos (`Map<String, Credencial>`). La clave `default` contendrá los valores comunes y será usada como base para heredar valores que no estén definidos en los demás países.

Los secretos se agruparán por `clientId` y se enriquecerán automáticamente con valores sensibles (`token`, `apiKey`) desde Azure Key Vault.

---

## 🧱 Estructura YAML propuesta

```yaml
countries:
  - code: default
    secrets:
      modulo1:
        clientId: abc
        ruta: /default/ruta
  - code: CO
    secrets:
      modulo1:
        clientId: abc-co
        ruta: /co/ruta
  - code: MX
    secrets:
      # Hereda módulo1 de default

```



