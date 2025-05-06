
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
```
