```
import json

def lambda_handler(event, context):
    """
    Función de ejemplo "Hola Mundo" para AWS Lambda.
    """
    # TODO: Agrega más lógica aquí
    
    return {
        'statusCode': 200,
        'body': json.dumps('¡Hola desde Lambda! Este es un "Hola Mundo".')
    }

test_main.py
Para probar la función de Lambda, crearemos un test unitario usando el módulo unittest de Python. Este test verificará que la función lambda_handler devuelve el statusCode esperado y el cuerpo del mensaje correcto.

Python

import unittest
import json
from src.lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):
    """
    Clase de prueba para lambda_function.py.
    """
    def test_lambda_handler_success(self):
        """
        Prueba que la función lambda_handler devuelve un 'statusCode' 200 y el cuerpo del mensaje esperado.
        """
        # Simulamos un evento y un contexto, aunque para esta prueba no se usan.
        event = {}
        context = {}
        
        # Invocamos la función de Lambda
        response = lambda_handler(event, context)
        
        # Verificamos el código de estado
        self.assertEqual(response['statusCode'], 200)
        
        # Verificamos el cuerpo del mensaje.
        # json.loads() es necesario porque el cuerpo del mensaje está en formato JSON.
        body = json.loads(response['body'])
        self.assertEqual(body, '¡Hola desde Lambda! Este es un "Hola Mundo".')

if __name__ == '__main__':
    unittest.main()
python -m unittest tests/test_main.py
```
