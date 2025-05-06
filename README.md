
```
 SELECT
    SUBSTR(MESSAGE, LOCATE(':', MESSAGE) + 2, LOCATE('|', MESSAGE) - LOCATE(':', MESSAGE) - 2) AS extracted_number
FROM
    EXAMPLE
WHERE
    MESSAGE LIKE '%:% |%';
```
