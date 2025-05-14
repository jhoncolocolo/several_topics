```
public void setCountries(List<Pais> countries) {
    this.countries = countries;

    // 1. Obtener los secretos del país default
    Map<String, Credencial> secretosDefault = countries.stream()
        .filter(p -> DEFAULT.equals(p.getCode()))
        .findFirst()
        .map(Pais::getSecrets)
        .orElse(Map.of());

    List<Credencial> todas = new ArrayList<>();

    for (Pais pais : countries) {
        Map<String, Credencial> secretosCombinados = new HashMap<>();

        // 2. Heredar secretos del default (copiamos para evitar referencias compartidas)
        for (Map.Entry<String, Credencial> entry : secretosDefault.entrySet()) {
            secretosCombinados.put(entry.getKey(), new Credencial(entry.getValue()));
        }

        // 3. Sobrescribir con los secretos propios del país
        if (pais.getSecrets() != null) {
            for (Map.Entry<String, Credencial> entry : pais.getSecrets().entrySet()) {
                secretosCombinados.put(entry.getKey(), new Credencial(entry.getValue()));
            }
        }

        // 4. Guardar secretos por país
        secretsPorPais.put(pais.getCode(), secretosCombinados);
        todas.addAll(secretosCombinados.values());
    }

    // 5. Agrupar por client_id y enriquecer con token y api_key desde Key Vault
    Map<String, List<Credencial>> porCliente = todas.stream()
        .collect(Collectors.groupingBy(Credencial::getClientId));

    for (var entry : porCliente.entrySet()) {
        String clienteId = entry.getKey();
        KeyVaultSecret token = getKeyVaultSecret(String.format(EXTERNAL_SERVICE_TOKEN_APP, clienteId));
        KeyVaultSecret apiKey = getKeyVaultSecret(String.format(EXTERNAL_SERVICE_X_API_KEY, clienteId));

        for (Credencial c : entry.getValue()) {
            c.setTokenAplicacion(token.getValue());
            c.setApiKey(apiKey.getValue());
        }
    }
}

```



