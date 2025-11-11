# 🚀 AWS Lambda + SQS con Retry y DLQ (Single Lambda Version)

Este proyecto implementa una **arquitectura resiliente en AWS Lambda** con **SQS** (cola principal de reintentos) y **DLQ** (Dead Letter Queue) utilizando **Terraform** y **Python**.  
Además, incluye pruebas automáticas con **pytest** para validar la lógica de reintentos tanto localmente como en AWS real.

---

## 🧱 Estructura del Proyecto

```
aws-sqs-single-lambda-modularized/
│
├── main.tf
├── variables.tf
├── requirements.txt
├── pytest.ini
├── .env
│
├── lambda_funcion.py
├── procesador.py
│
├── services/
│   └── sqs.py
│
└── tests/
    ├── test_integracion_aws.py
    ├── test_procesador.py
    └── test_sqs_service.py
```


---
## ⚙️ Archivos Clave

### `main.tf`
Código Terraform que crea los siguientes recursos:
- 1 cola **principal (SQS)**
- 1 cola **DLQ**
- 1 **Lambda**
- 1 **IAM Role y Policy** para permitir acceso a SQS y CloudWatch
- 1 **Event Source Mapping** para conectar Lambda con SQS

Incluye además **outputs útiles** para enviar mensajes desde PowerShell.

```terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5.0"
}

provider "aws" {
  region = var.aws_region
}

# IAM role para la Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_prefix}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_prefix}-lambda-policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "logs:*",
          "sqs:*"
        ],
        Resource = "*"
      }
    ]
  })
}

# SQS con Retry + DLQ
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_prefix}-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "retry" {
  name                      = "${var.project_prefix}-retry"
  visibility_timeout_seconds = 45
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.retry_max_receive_count
  })
}

# Empaquetar Lambda automáticamente desde el código del módulo
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}"
  output_path = "${path.module}/lambda_funcion.zip"

  excludes = [
    ".terraform/*",
    "*.tfstate",
    "*.zip",
    "requirements.txt",
    "tests/*",
    "__pycache__/*",
    ".pytest_cache/*"
  ]
}

# Lambda principal
resource "aws_lambda_function" "main_lambda" {
  function_name = "${var.project_prefix}-main-lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_funcion.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.lambda_zip.output_path
  timeout       = 30
  memory_size   = 128

  environment {
    variables = {
      RETRY_QUEUE_URL = aws_sqs_queue.retry.url
      DLQ_QUEUE_URL   = aws_sqs_queue.dlq.url
    }
  }
}

# Outputs útiles
output "invoke_lambda_ok" {
  value = "aws lambda invoke --function-name ${aws_lambda_function.main_lambda.function_name} --payload file://msg_ok.json --cli-binary-format raw-in-base64-out output.json"
}

output "invoke_lambda_fail" {
  value = "aws lambda invoke --function-name ${aws_lambda_function.main_lambda.function_name} --payload file://msg_fail.json --cli-binary-format raw-in-base64-out output.json"
}

output "retry_queue_url" {
  value = aws_sqs_queue.retry.url
}

output "dlq_queue_url" {
  value = aws_sqs_queue.dlq.url
}


# Conectar la misma Lambda a la cola de reintentos (SQS)
resource "aws_lambda_event_source_mapping" "retry_to_self" {
  event_source_arn = aws_sqs_queue.retry.arn
  function_name    = aws_lambda_function.main_lambda.arn
  batch_size       = 1
  enabled          = true
}

```


### `variables.tf`
```terraform
variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project_prefix" {
  type    = string
  default = "lambda-msk-sqs-demo"
}

variable "retry_max_receive_count" {
  type    = number
  default = 2
}
```

### `lambda_function.py`
```python
import logging
from procesador import procesador

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda principal: solo delega al procesador().
    """
    logger.info("📬 Evento recibido: %s", event)
    return procesador(event)

```

### `procesador.py`
```python
import json
import logging
from services.sqs import SQSService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = SQSService()

def procesador(event):
    """
    Procesa un mensaje y maneja reintentos y DLQ en caso de error.
    """
    # Detectar si viene de SQS (auto-trigger)
    if "Records" in event:
        record = event["Records"][0]
        event = json.loads(record["body"])
        logger.info("📦 Mensaje recibido desde SQS: %s", event)
    elif isinstance(event, str):
        event = json.loads(event)

    mensaje = event.get("data")
    force_error = event.get("force_error", False)
    retry_count = event.get("retry_count", 0)

    try:
        logger.info("🚀 procesador() intentando #%d con mensaje: %s", retry_count + 1, mensaje)

        # Simula la lógica de negocio real
        if force_error:
            raise Exception("💥 Error simulado dentro de procesador()")

        logger.info("🟢 Procesamiento exitoso en procesador()")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Procesado exitosamente"})
        }

    except Exception as e:
        logger.error("❌ Error en procesador(): %s", e)

        # ✅ Permitir dos reintentos antes de DLQ
        if retry_count < 2:
            new_event = {
                "data": mensaje,
                "force_error": force_error,
                "retry_count": retry_count + 1
            }
            sqs.enviar_a_retry(new_event)
            logger.info("📤 procesador() reenvió mensaje a cola de reintentos.")
        else:
            sqs.enviar_a_dlq(event)
            logger.info("💀 procesador() envió mensaje a DLQ tras fallar los reintentos.")

        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error procesando mensaje"})
        }

```

### `services/sqs.py`
```python
import json
import os
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class SQSService:
    def __init__(self):
        self.sqs = boto3.client("sqs")
        self.retry_queue_url = os.getenv("RETRY_QUEUE_URL")
        self.dlq_queue_url = os.getenv("DLQ_QUEUE_URL")

    def enviar_a_retry(self, mensaje: dict):
        try:
            logger.info(f"🔎 Enviando a retry con URL: {self.retry_queue_url}")
            response = self.sqs.send_message(
                QueueUrl=self.retry_queue_url,
                MessageBody=json.dumps(mensaje)
            )
            logger.info("📤 Mensaje enviado a Retry Queue: %s", mensaje)
            return response
        except Exception as e:
            logger.error("❌ Error enviando a Retry Queue: %s", e)
            raise

    def enviar_a_dlq(self, mensaje: dict):
        try:
            logger.info(f"🔎 Enviando a retry con URL: {self.dlq_queue_url}")
            response = self.sqs.send_message(
                QueueUrl=self.dlq_queue_url,
                MessageBody=json.dumps(mensaje)
            )
            logger.info("☠️ Mensaje enviado a DLQ: %s", mensaje)
            return response
        except Exception as e:
            logger.error("❌ Error enviando a DLQ: %s", e)
            raise

```

### `tests/test_integracion_aws.py`
```python
import boto3
import json
import os
import time
import pytest
from dotenv import load_dotenv

load_dotenv()

sqs_client = boto3.client("sqs", region_name="us-east-1")
lambda_client = boto3.client("lambda", region_name="us-east-1")

RETRY_QUEUE_URL = os.getenv("RETRY_QUEUE_URL")
DLQ_QUEUE_URL = os.getenv("DLQ_QUEUE_URL")
LAMBDA_NAME = os.getenv("LAMBDA_NAME", "lambda-msk-sqs-demo-main-lambda")

# 🧹 Limpia la cola (maneja el error si hay purga reciente)
def limpiar_cola(queue_url):
    try:
        sqs_client.purge_queue(QueueUrl=queue_url)
        print(f"🧹 Cola purgada: {queue_url}")
        time.sleep(5)
    except sqs_client.exceptions.PurgeQueueInProgress:
        print(f"⚠️ Purge en progreso en {queue_url}, esperando 60 segundos...")
        time.sleep(65)
    except Exception as e:
        print(f"⚠️ No se pudo purgar la cola {queue_url}: {e}")

# 📨 Invoca la Lambda con un payload
def invoke_lambda(payload):
    response = lambda_client.invoke(
        FunctionName=LAMBDA_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode("utf-8"),
    )
    print("🚀 Lambda invocada, status:", response["StatusCode"])
    return response

# 📬 Lee mensajes de una cola con reintentos de polling
def leer_mensajes(queue_url, timeout=30, interval=3):
    print(f"⌛ Esperando mensajes en cola: {queue_url}")
    elapsed = 0
    while elapsed < timeout:
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=5,
        )
        messages = response.get("Messages", [])
        if messages:
            print(f"📨 Mensaje encontrado: {messages[0]['Body']}")
            return json.loads(messages[0]["Body"])
        time.sleep(interval)
        elapsed += interval
    print("❌ No se encontraron mensajes tras", timeout, "segundos")
    return None

@pytest.mark.integration
def test_1_envio_exitoso_directo():
    limpiar_cola(RETRY_QUEUE_URL)
    limpiar_cola(DLQ_QUEUE_URL)

    payload = {"data": "test-aws-1", "force_error": False}
    invoke_lambda(payload)

    msg = leer_mensajes(RETRY_QUEUE_URL, 20)
    assert msg is None, "No debería haber mensaje en retry en un caso exitoso"

@pytest.mark.integration
def test_2_exito_despues_primer_reintento():
    limpiar_cola(RETRY_QUEUE_URL)
    limpiar_cola(DLQ_QUEUE_URL)

    # primer intento forzado a fallar
    payload = {"data": "test-aws-2", "force_error": True}
    invoke_lambda(payload)

    # esperar que llegue a retry (o haya sido procesado)
    msg = leer_mensajes(RETRY_QUEUE_URL, 45)
    if msg is None:
        print("ℹ️ El mensaje pudo ser procesado inmediatamente por la Lambda desde retry.")
    else:
        print("✅ Mensaje llegó a retry:", msg)

    # segundo intento forzado a éxito
    payload["force_error"] = False
    invoke_lambda(payload)

    # revisar DLQ
    dlq_msg = leer_mensajes(DLQ_QUEUE_URL, 45)
    if dlq_msg is None:
        print("✅ No llegó mensaje a DLQ, flujo exitoso después de reintento.")
    else:
        print("ℹ️ Mensaje llegó a DLQ tras agotarse los reintentos (flujo esperado también).")


@pytest.mark.integration
def test_3_falla_total_envio_a_dlq():
    limpiar_cola(RETRY_QUEUE_URL)
    limpiar_cola(DLQ_QUEUE_URL)

    payload = {"data": "test-aws-3", "force_error": True}
    invoke_lambda(payload)

    # primer fallo -> puede ir a retry o procesarse inmediatamente
    msg = leer_mensajes(RETRY_QUEUE_URL, 45)
    if msg is None:
        print("ℹ️ El mensaje fue procesado automáticamente por la Lambda desde la cola retry.")
    else:
        print("✅ Mensaje llegó a retry:", msg)

    # esperar mensaje en DLQ (tras agotar reintentos)
    dlq_msg = leer_mensajes(DLQ_QUEUE_URL, 90)
    assert dlq_msg is not None, "No se recibió mensaje en DLQ tras fallar todos los reintentos"
    print("💀 Mensaje final en DLQ:", dlq_msg)
```

### `tests/test_procesador.py`
```python
import json
from unittest.mock import patch
from procesador import procesador

def test_envio_exitoso_directo(monkeypatch):
    event = {"data": "test-1", "force_error": False}
    result = procesador(event)
    assert result["statusCode"] == 200

def test_exito_despues_de_primer_reintento(monkeypatch):
    call_count = {"procesos": 0}

    def fake_send_to_retry(event):
        call_count["procesos"] += 1
        if call_count["procesos"] == 1:
            event["retry_count"] = 1
            procesador({"data": event["data"], "force_error": False, "retry_count": 1})

    with patch("services.sqs.SQSService.enviar_a_retry", side_effect=fake_send_to_retry) as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq:

        event = {"data": "test-2", "force_error": True}
        response = procesador(event)

        assert mock_retry.call_count >= 1
        assert mock_dlq.call_count == 0
        assert response["statusCode"] == 500 or response["statusCode"] == 200

def test_exito_despues_de_segundo_reintento(monkeypatch):
    call_count = {"procesos": 0}

    def fake_send_to_retry(event):
        call_count["procesos"] += 1
        if call_count["procesos"] == 1:
            event["retry_count"] = 1
            procesador({"data": event["data"], "force_error": True, "retry_count": 1})
        elif call_count["procesos"] == 2:
            event["force_error"] = False
            procesador(event)

    with patch("services.sqs.SQSService.enviar_a_retry", side_effect=fake_send_to_retry) as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq:

        event = {"data": "test-3", "force_error": True}
        response = procesador(event)

        assert mock_retry.call_count >= 1
        assert mock_dlq.call_count == 0

def test_falla_total_envio_a_dlq(monkeypatch):
    with patch("services.sqs.SQSService.enviar_a_retry") as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq:

        event = {"data": "test-4", "force_error": True, "retry_count": 2}
        response = procesador(event)

        assert response["statusCode"] == 500
        mock_retry.assert_not_called()
        mock_dlq.assert_called_once()

```

### `tests/test_sqs_service.py`
```python
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from moto import mock_aws
import boto3
from services.sqs import SQSService

@mock_aws
def test_enviar_a_retry_envia_mensaje_correctamente():
    sqs = boto3.client("sqs", region_name="us-east-1")
    retry_queue = sqs.create_queue(QueueName="test-retry")
    dlq_queue = sqs.create_queue(QueueName="test-dlq")

    os.environ["RETRY_QUEUE_URL"] = retry_queue["QueueUrl"]
    os.environ["DLQ_QUEUE_URL"] = dlq_queue["QueueUrl"]

    service = SQSService()

    mensaje = {"data": "test", "status": "fail"}
    resp = service.enviar_a_retry(mensaje)

    assert "MessageId" in resp

```

### `pytest.ini`
```ini
[pytest]
markers =
    integration: tests que interactúan con AWS real
testpaths = tests
python_files = test_*.py
addopts = -ra -q
```

### `requirements.txt`
```ini
boto3
pytest
moto
moto[boto3]

```

### `Crear archivos __init__ sin contenido en la carpetas services y tests`

---

## ⚙️ 1. Instalación y entorno

### 🔹 Requisitos previos

- **Python 3.12+**
- **AWS CLI configurado** con credenciales válidas (`aws configure`)
- **Terraform 1.5+**
- **Cuenta AWS** con permisos sobre Lambda, SQS y CloudWatch

### 🔹 Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🏗️ 2. Despliegue con Terraform

### 🔸 Inicializar Terraform

```bash
terraform init
```

### 🔸 Revisar el plan de despliegue

```bash
terraform plan
```

### 🔸 Aplicar la infraestructura

```bash
terraform apply -auto-approve
```

Esto creará automáticamente:

- 1 función Lambda principal  
- 1 cola de reintentos (**retry**)  
- 1 cola DLQ (**dead letter**)  
- 1 role IAM con permisos de CloudWatch + SQS  
- Conexión **automática** Lambda ↔ Retry Queue  

### 🔸 Guardar los outputs

Después del `apply`, ejecuta:

```bash
terraform output
```

Y copia las URLs de las colas en tu archivo `.env` (ya viene un ejemplo):

```bash
RETRY_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/XXXX/lambda-msk-sqs-demo-retry
DLQ_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/XXXX/lambda-msk-sqs-demo-dlq
LAMBDA_NAME=lambda-msk-sqs-demo-main-lambda
```

---

## 🧪 3. Ejecución de pruebas

### 🔸 Pruebas unitarias (locales)

Validan la lógica interna sin usar AWS real:

```bash
pytest tests/test_procesador.py -v
pytest tests/test_sqs_service.py -v
```

### 🔸 Pruebas de integración con AWS real

Estas requieren que las colas y la Lambda estén **ya desplegadas**:

```bash
# Cargar variables de entorno desde Terraform
$env:RETRY_QUEUE_URL = "$(terraform output -raw retry_queue_url)"
$env:DLQ_QUEUE_URL   = "$(terraform output -raw dlq_queue_url)"
$env:LAMBDA_NAME     = "lambda-msk-sqs-demo-main-lambda"

# Ejecutar todos los tests
pytest -v
```

---

## 🧰 4. Pruebas manuales con AWS CLI

Puedes invocar la Lambda manualmente para simular casos reales:

### ✅ Caso exitoso
```bash
echo '{"data": "test-ok", "force_error": false}' > msg_ok.json
aws lambda invoke --function-name lambda-msk-sqs-demo-main-lambda --payload file://msg_ok.json --cli-binary-format raw-in-base64-out output.json
```

### 💥 Caso de error (simula fallos y reintentos)
```bash
echo '{"data": "test-fail", "force_error": true}' > msg_fail.json
aws lambda invoke --function-name lambda-msk-sqs-demo-main-lambda --payload file://msg_fail.json --cli-binary-format raw-in-base64-out output.json
```

Revisa los logs en CloudWatch:
```bash
aws logs tail /aws/lambda/lambda-msk-sqs-demo-main-lambda --follow
```

---

## 🔁 5. Flujo de reintentos y DLQ (resumen)

El sistema realiza **hasta 2 reintentos adicionales** antes de enviar un mensaje a la **DLQ**.

| Intento | `retry_count` | Acción | Resultado esperado |
|----------|----------------|--------|--------------------|
| #1 | 0 | Procesa mensaje | Si falla → envía a cola **Retry** |
| #2 | 1 | Llega desde retry | Si falla → reenvía a **Retry** |
| #3 | 2 | Llega nuevamente desde retry | Si falla → envía a **DLQ** |

📜 Por eso el log muestra:

```
🚀 procesador() intentando #3 con mensaje: test-123
💀 procesador() envió mensaje a DLQ tras fallar los reintentos.
```

🔹 El “intentando #3” **no es un nuevo intento extra**, sino el **tercer procesamiento total** (1 original + 2 reintentos).  
🔹 Es completamente **normal y esperado** antes de que el mensaje sea movido a la **DLQ**.

---

## 🧹 6. Limpieza

Cuando termines de probar:

```bash
terraform destroy -auto-approve
```

Esto eliminará todos los recursos creados (Lambda, SQS, roles, etc.).

---

## ✅ 7. Resultado final esperado

- Todos los tests (`pytest -v`) deben pasar.
- Los mensajes con errores persistentes deben terminar en la **DLQ**.
- Los mensajes correctos o recuperables deben ser procesados exitosamente.

---

> 💡 Proyecto listo para servir como base en arquitecturas **event-driven resilientes** con AWS Lambda + SQS.

```python
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict
import urllib3
from services.sqs import SQSService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = SQSService()


# --- Clases y Funciones de Soporte ---

def validador(mensaje: dict) -> bool:
    """Simula validación de mensaje."""
    return True


def obtener_secreto_microsoft() -> Dict[str, str]:
    """Simula obtención de configuración o secretos externos."""
    return {
        "API_URL": "http://localhost:8000",
        "STORE_ID": "store-001",
        "MODELO_ID": "modelo-001"
    }


class OPENFGARELACION:
    USER_ADMIN = "administrador"
    USER_OWNER_PROFILE = "owner"


@dataclass
class TuplaLlave:
    user: str
    relation: str
    object: str


@dataclass
class EscribirTupla:
    tupla_llave: TuplaLlave
    modelo_autorizacion_id: str

    def to_dic(self) -> Dict[str, Any]:
        return {
            "writes": {
                "tuple_keys": [
                    {
                        "user": self.tupla_llave.user,
                        "relation": self.tupla_llave.relation,
                        "object": self.tupla_llave.object
                    }
                ]
            },
            "modelo_autorizacion_id": self.modelo_autorizacion_id
        }


class ClienteServicio:
    """Simula el servicio web que escribe la tupla en OpenFGA."""
    def __init__(self, api_url: str, store_id: str):
        self.url = api_url
        self.store_id = store_id
        self.http = urllib3.PoolManager()

    def escribir_tupla(self, request: EscribirTupla) -> None:
        try:
            url = f"{self.url}/stores/{self.store_id}/write"
            headers = {"Content-Type": "application/json"}
            response = self.http.request(
                "POST", url, body=json.dumps(request.to_dic()), headers=headers
            )
            if response.status >= 400:
                raise ValueError(f"HTTP {response.status}")
            logger.info("✅ Tupla escrita con éxito en OpenFGA.")
        except Exception as e:
            raise ValueError(f"Error guardando en OpenFGA: {e}")


# --- Método Principal ---

def procesador(evento) -> Dict[str, Any]:
    """
    Procesa el evento, intenta escribir una tupla en OpenFGA,
    reenvía a Retry o DLQ según los fallos.
    """
    # 📦 Detectar si viene desde SQS
    if "Records" in evento:
        record = evento["Records"][0]
        evento = json.loads(record["body"])
        logger.info("📦 Mensaje recibido desde SQS: %s", evento)

    # Extraer número de reintento actual (por defecto 0)
    retry_count = evento.get("retry_count", 0)

    try:
        mensaje = evento.get("message")
        if not validador(mensaje):
            return {"statusCode": 400, "body": "Missing Fields"}

        config_values = obtener_secreto_microsoft()

        cliente = ClienteServicio(
            api_url=config_values["API_URL"],
            store_id=config_values["STORE_ID"]
        )

        tupla_llave = TuplaLlave(
            user="user_1024",
            relation=OPENFGARELACION.USER_ADMIN,
            object=mensaje["data"]["table"]
        )

        request = EscribirTupla(
            tupla_llave=tupla_llave,
            modelo_autorizacion_id=config_values["MODELO_ID"]
        )

        # 🚀 Intentar escribir tupla (aquí puede fallar)
        cliente.escribir_tupla(request)
        logger.info("🟢 Procesamiento exitoso del evento.")

        return {"statusCode": 200, "body": "Se almacena bien los datos"}

    except Exception as e:
        logger.error("❌ Error procesando mensaje: %s", e)

        # Manejar reintentos
        if retry_count < 2:
            new_event = dict(evento)
            new_event["retry_count"] = retry_count + 1
            sqs.enviar_a_retry(new_event)
            logger.info("📤 Mensaje enviado a Retry Queue (intento #%d)", retry_count + 1)
        else:
            sqs.enviar_a_dlq(evento)
            logger.info("💀 Mensaje enviado a DLQ tras fallar los reintentos.")

        return {
            "statusCode": 500,
            "body": f"Unexpected Error: {e}"
        }

```

```python
from unittest.mock import patch
from procesador import procesador

EVENTO_VALIDO = {
    "message": {
        "hostname": "api.production.internal",
        "timestamp": "2025-11-10T23:56:44Z",
        "data": {
            "event_type": "user_created",
            "table": "users",
            "values": {"user_id": 1024}
        }
    }
}


def test_exitoso_directo(monkeypatch):
    with patch("services.sqs.SQSService.enviar_a_retry") as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq, \
         patch("procesador.ClienteServicio.escribir_tupla", return_value=None):
        result = procesador(EVENTO_VALIDO)
        assert result["statusCode"] == 200
        mock_retry.assert_not_called()
        mock_dlq.assert_not_called()


def test_falla_total_envio_a_dlq(monkeypatch):
    evento = dict(EVENTO_VALIDO)
    evento["retry_count"] = 2
    with patch("services.sqs.SQSService.enviar_a_retry") as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq, \
         patch("procesador.ClienteServicio.escribir_tupla", side_effect=Exception("Falla")):
        result = procesador(evento)
        assert result["statusCode"] == 500
        mock_retry.assert_not_called()
        mock_dlq.assert_called_once()


def test_exito_despues_de_un_fallo(monkeypatch):
    call_count = {"intentos": 0}

    def fake_write(_):
        call_count["intentos"] += 1
        if call_count["intentos"] == 1:
            raise Exception("Falla en primer intento")

    with patch("procesador.ClienteServicio.escribir_tupla", side_effect=fake_write) as mock_write, \
         patch("services.sqs.SQSService.enviar_a_retry") as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq:

        evento = dict(EVENTO_VALIDO)
        result = procesador(evento)

        # Primer intento falla → Retry
        assert result["statusCode"] == 500
        mock_retry.assert_called_once()
        mock_dlq.assert_not_called()

        # Segundo intento exitoso
        result2 = procesador(EVENTO_VALIDO)
        assert result2["statusCode"] == 200


def test_exito_despues_de_dos_fallos(monkeypatch):
    call_count = {"intentos": 0}

    def fake_write(_):
        call_count["intentos"] += 1
        if call_count["intentos"] < 3:
            raise Exception("Falla simulada")
        # 3er intento es exitoso

    with patch("procesador.ClienteServicio.escribir_tupla", side_effect=fake_write), \
         patch("services.sqs.SQSService.enviar_a_retry") as mock_retry, \
         patch("services.sqs.SQSService.enviar_a_dlq") as mock_dlq:

        evento = dict(EVENTO_VALIDO)
        result = procesador(evento)
        assert result["statusCode"] == 500
        assert mock_retry.called
        assert not mock_dlq.called

        evento["retry_count"] = 1
        result2 = procesador(evento)
        assert result2["statusCode"] == 500

        evento["retry_count"] = 2
        result3 = procesador(evento)
        assert result3["statusCode"] == 200

```
https://risivys.hiruko.com.co:32117/portal/login
