1) Resumen de arquitectura (qué vamos a crear)

Cola principal (Standard o FIFO) — MiColaPrincipal.

Dead-Letter Queue (DLQ) — MiColaDLQ.

Lambda function (ej. miLambdaProcesadora) con rol que le permita leer SQS.

Event source mapping (SQS → Lambda) para que Lambda reciba mensajes en batches.

RedrivePolicy en la cola principal que indique deadLetterTargetArn y maxReceiveCount (cuántos intentos antes de mandar a DLQ).

Pruebas: enviar mensajes con aws sqs send-message, verificar CloudWatch + mensajes en DLQ. 
docs.aws.amazon.com
+1

2) Crear colas (AWS CLI)

Asumo que tienes aws configurado (aws configure) con credenciales y región.

Crear DLQ:

aws sqs create-queue --queue-name MiColaDLQ
# Guarda la URL de respuesta y obtén su ARN:
DLQ_URL=$(aws sqs get-queue-url --queue-name MiColaDLQ --query 'QueueUrl' --output text)
DLQ_ARN=$(aws sqs get-queue-attributes --queue-url "$DLQ_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
echo "DLQ_ARN=$DLQ_ARN"


Crear cola principal con RedrivePolicy
maxReceiveCount = número de intentos antes de mover a DLQ (ej. 3).

aws sqs create-queue --queue-name MiColaPrincipal \
  --attributes RedrivePolicy="{\"deadLetterTargetArn\":\"$DLQ_ARN\",\"maxReceiveCount\":\"3\"}"
  
MAIN_URL=$(aws sqs get-queue-url --queue-name MiColaPrincipal --query 'QueueUrl' --output text)
MAIN_ARN=$(aws sqs get-queue-attributes --queue-url "$MAIN_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
echo "MAIN_ARN=$MAIN_ARN"


Nota: para FIFO usa --attributes FifoQueue=true y nombres terminados en .fifo. La DLQ debe ser del mismo tipo. 
docs.aws.amazon.com
+1

3) Crear rol IAM para la Lambda

Puedes usar la política gestionada AWSLambdaSQSQueueExecutionRole (la documentación la recomienda para Lambda que procesa SQS).

Crear rol (JSON de confianza para Lambda) — guarda en trust-policy.json:

{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "lambda.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}


Crear rol y adjuntar la política gestionada + CloudWatchLogs:

ROLE_NAME=LambdaSQSExecutionRolePersonal
aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json

# Adjuntar la política recomendada para SQS + logs
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaSQSQueueExecutionRole
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/CloudWatchLogsFullAccess


La política AWSLambdaSQSQueueExecutionRole le da permiso a Lambda para leer de SQS y las acciones necesarias. 
docs.aws.amazon.com
+1

4) Crear la Lambda (ejemplo Python)

Ejemplo mínimo lambda_function.py:

# lambda_function.py
import json

def lambda_handler(event, context):
    # event["Records"] es la lista de mensajes SQS
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        # ejemplo: si body["process_ok"] == False -> lanzamos excepción para simular fallo
        if not body.get("process_ok", True):
            raise ValueError(f"Procesamiento falló para item_id={body.get('item_id')}")
        print(f"Procesado OK: {body.get('item_id')}")
    return {"status": "done"}


Empaqueta y sube:

zip function.zip lambda_function.py

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

aws lambda create-function \
  --function-name miLambdaProcesadora \
  --runtime python3.11 \
  --role "$ROLE_ARN" \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --timeout 60 \
  --memory-size 256


(ajusta runtime, timeout y memoria según tu función)

5) Conectar SQS → Lambda (Event Source Mapping)

Puedes crear el mapeo con CLI (o agregar el trigger desde la consola Lambda):

aws lambda create-event-source-mapping \
  --function-name miLambdaProcesadora \
  --batch-size 10 \
  --event-source-arn "$MAIN_ARN" \
  --enabled


Parámetros importantes:

batch-size: hasta 10 (FIFO) / hasta 10,000 para standard (pero Lambda limita comportamientos; la doc oficial lista límites).

enabled: true/false.
Si usas consola, al añadir trigger SQS te pedirá la cola y creará el mapping automáticamente. 
docs.aws.amazon.com
+1

6) Ajustes importantes (para comportamiento correcto)

maxReceiveCount (en RedrivePolicy): define después de cuántos fallos se mueve el mensaje a la DLQ. Lo configuraste al crear la cola (ej. 3). 
docs.aws.amazon.com

Visibility Timeout: debe ser mayor que el tiempo máximo de ejecución de tu Lambda (timeout), para evitar reentregas prematuras. Recomiendo VisibilityTimeout >= Lambda timeout * 2.

Lambda timeout: pon un timeout apropiado (ej. 30-60 s). Si lambda nunca responde (timeout) eso cuenta como fallo y, después de maxReceiveCount, SQS lo moverá a DLQ. 
docs.aws.amazon.com
+1

7) Probar (en AWS, con CLI)

Enviar mensaje de éxito:

aws sqs send-message --queue-url "$MAIN_URL" --message-body '{"process_ok": true, "item_id": 100}'


Enviar mensaje que provoque fallo:

aws sqs send-message --queue-url "$MAIN_URL" --message-body '{"process_ok": false, "item_id": 200}'


Observar:

En CloudWatch Logs del Lambda verás invocaciones y excepciones.

Tras maxReceiveCount fallos, el mensaje aparecerá en la DLQ (usa aws sqs receive-message --queue-url $DLQ_URL).
Ejemplo para leer DLQ:

aws sqs receive-message --queue-url "$DLQ_URL" --max-number-of-messages 10


Si la Lambda lanza excepción para un mensaje del batch, Lambda considera la invocación fallida y no borra los mensajes procesados en ese batch (ocurre reintento según el comportamiento de event source mapping). 
docs.aws.amazon.com

8) Monitoreo y depuración

CloudWatch Logs: revisa logs de la función para entender fallos.

CloudWatch Metrics: ApproximateNumberOfMessagesVisible en la cola y métricas Lambda (Invocations, Errors, DLQDeliveryFailures).

Dead-Letter monitoring: configura alarmas cuando la DLQ tenga mensajes (p. ej. si ApproximateNumberOfMessagesVisible > 0). 
docs.aws.amazon.com

9) Opcional — usar Infrastructure as Code

Recomiendo usar CloudFormation, SAM o Serverless Framework para reproducir todo (creación de colas, rol, lambda y event source mapping) de forma declarativa. La doc de AWS::Lambda::EventSourceMapping y los ejemplos SAM facilitan esto. 
docs.aws.amazon.com
+1

10) Ejemplo mínimo de flujo de pruebas (resumen rápido)

Crear DLQ.

Crear cola principal con RedrivePolicy apuntando al DLQ (ej. maxReceiveCount = 3).

Crear rol IAM con AWSLambdaSQSQueueExecutionRole.

Crear Lambda (zip) y subirla.

Crear event source mapping con el ARN de la cola.

Enviar mensajes que provoquen process_ok=false y observar cómo después de 3 intentos terminan en DLQ. 
docs.aws.amazon.com
+1

Si quieres, hago cualquiera de estas cosas contigo en uno de dos modos (elige uno):

Te doy un CloudFormation / SAM template completo que cree las 2 colas, la DLQ, la función y el mapping (lista para desplegar con sam deploy o aws cloudformation create-stack).

Te doy un script bash completo que ejecuta las órdenes CLI en el orden correcto (crea colas, rol, empaqueta la lambda y crea el mapping) — útil si prefieres CLI.

Dime cuál prefieres y te lo genero ahora mismo. ✅
