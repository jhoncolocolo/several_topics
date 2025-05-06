
```
 SELECT
    SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2) AS extracted_number
FROM
    EXAMPLE
WHERE
    MESSAGE LIKE '%:% |%';



SELECT
    SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2) AS extracted_value
FROM
    EXAMPLE
WHERE
    MESSAGE LIKE '%:% |%'
    AND CASE
        WHEN SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2) LIKE '%[^0-9-]%'
        OR LENGTH(TRIM(SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2))) = 0
        OR (SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2) LIKE '-' AND LENGTH(SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2)) = 1)
        THEN 0
        ELSE 1
    END = 1;


SELECT VALOR
FROM DATOS_MIX
WHERE
    CASE
        WHEN VALOR LIKE '%[^0-9-]%' THEN 0  -- Contiene caracteres no numéricos (excepto '-')
        WHEN VALOR LIKE '-' AND LENGTH(VALOR) = 1 THEN 0 -- Es solo el signo menos
        WHEN VALOR LIKE '%-%' AND LENGTH(VALOR) = 1 THEN 0 -- Es solo el signo menos (redundante pero por claridad)
        WHEN VALOR LIKE '-%' AND SUBSTR(VALOR, 2) NOT LIKE '%[^0-9]%' THEN 1 -- Empieza con '-' y el resto son dígitos
        WHEN VALOR LIKE '%[0-9]%' AND VALOR NOT LIKE '%[^0-9]%' THEN 1 -- Contiene solo dígitos
        ELSE 0
    END = 1;

Entiendo. Si solo te devolvió los -1, eso sugiere que la condición para los números negativos podría ser demasiado restrictiva o que hay alguna sutileza en tus datos que no estamos considerando.

Revisemos la parte de la consulta relacionada con los números negativos:

SQL

WHEN VALOR LIKE '-%' AND SUBSTR(VALOR, 2) NOT LIKE '%[^0-9]%' THEN 1
Esta condición busca valores que empiecen con un guion (-) y donde todos los caracteres después del guion sean dígitos. Esto debería cubrir casos como -45 o -9.

Posibles causas por las que no se extrajeron otros números negativos:

Espacios en blanco: Podría haber espacios en blanco inesperados alrededor del signo menos o de los números. Por ejemplo, " -45" o "- 45".
Caracteres no visibles: Podría haber caracteres no imprimibles o de control que estén interfiriendo con la coincidencia del patrón LIKE.
Formato inconsistente: Quizás los números negativos tienen un formato ligeramente diferente en algunos registros.
Aquí te propongo una modificación a la consulta para hacerla un poco más robusta ante posibles espacios en blanco y para asegurarnos de que la lógica para los números negativos sea correcta:

SQL

SELECT VALOR
FROM DATOS_MIX
WHERE
    CASE
        WHEN TRIM(VALOR) LIKE '%[^0-9-]%' THEN 0
        WHEN TRIM(VALOR) = '-' THEN 0
        WHEN TRIM(VALOR) LIKE '-%' AND SUBSTR(TRIM(VALOR), 2) NOT LIKE '%[^0-9]%' THEN 1
        WHEN TRIM(VALOR) NOT LIKE '-%' AND TRIM(VALOR) LIKE '%[0-9]%' AND TRIM(VALOR) NOT LIKE '%[^0-9]%' THEN 1
        ELSE 0
    END = 1;
```
