Comandos

# Check out to a temporary branch:

git checkout --orphan TEMP_BRANCH

# Add all the files:

git add -A

# Commit the changes:

git commit -am "Initial commit"

# Delete the old branch:

git branch -D master

# Rename the temporary branch to master:

git branch -m master

# Finally, force update to our repository:

git push -f origin master

```text
----mainf.tf
#########################################
# TERRAFORM CONFIG
#########################################

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

#########################################
# SQS DLQ
#########################################

resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_prefix}-dlq"
  message_retention_seconds = 1209600
}

#########################################
# S3 BUCKET
#########################################

resource "aws_s3_bucket" "dlq_bucket" {
  bucket        = "mi-bucket-publicado-${var.project_prefix}"
  force_destroy = true
}

#########################################
# IAM ROLE
#########################################

resource "aws_iam_role" "dlq_lambda_role" {
  name = "${var.project_prefix}-dlq-monitor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "dlq_lambda_policy" {
  name = "${var.project_prefix}-dlq-monitor-policy"
  role = aws_iam_role.dlq_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [

      # CloudWatch Logs
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      },

      # Read from DLQ
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.dlq.arn
      },

      # Write to S3
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject"
        ],
        Resource = "${aws_s3_bucket.dlq_bucket.arn}/*"
      }
    ]
  })
}

#########################################
# LAMBDA PACKAGING
#########################################

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/lambda.zip"
}

#########################################
# LAMBDA MONITOREO DLQ
#########################################

resource "aws_lambda_function" "dlq_monitor_lambda" {
  function_name = "${var.project_prefix}-monitoreo-dlq"
  role          = aws_iam_role.dlq_lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  timeout     = var.lambda_timeout_seconds
  memory_size = var.lambda_memory_mb

  environment {
    variables = {
      BUCKET_NAME = aws_s3_bucket.dlq_bucket.bucket
    }
  }
}

#########################################
# PERMISSION SQS → LAMBDA
#########################################

resource "aws_lambda_permission" "allow_sqs_dlq" {
  statement_id  = "AllowExecutionFromSQS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dlq_monitor_lambda.arn
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.dlq.arn
}

#########################################
# EVENT SOURCE MAPPING (POLLING)
#########################################

resource "aws_lambda_event_source_mapping" "dlq_to_lambda" {
  event_source_arn = aws_sqs_queue.dlq.arn
  function_name    = aws_lambda_function.dlq_monitor_lambda.arn

  batch_size                         = 100
  maximum_batching_window_in_seconds = 5
  enabled                            = true

  function_response_types = ["ReportBatchItemFailures"]
}


variables.tf


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

variable "retry_visibility_timeout_seconds" {
  type    = number
  default = 45
}

variable "lambda_timeout_seconds" {
  type    = number
  default = 30
}

variable "lambda_memory_mb" {
  type    = number
  default = 128
}

variable "batch_size" {
  type    = number
  default = 10
}

variable "sqs_url_endpoint" {
  type    = string
  default = ""
}

variable "EXTRA_ENV_VARS" {
  type    = map(string)
  default = {}
}

lambda_function.py
 import json
import boto3
import os
from datetime import datetime, UTC

s3 = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "test-bucket")

def process_records(records, s3_client):
    failed_items = []
    logs_to_store = []

    for record in records:
        try:
            message_id = record["messageId"]
            body = record["body"]

            log_entry = f"MessageId: {message_id}\nBody: {body}\n---\n"
            logs_to_store.append(log_entry)

        except Exception:
            failed_items.append({
                "itemIdentifier": record["messageId"]
            })

    return logs_to_store, failed_items


def upload_to_s3(content, s3_client):
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    file_name = f"dlq_logs_{timestamp}.txt"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=content
    )


def lambda_handler(event, context):
    print("Evento recibido:")
    print(json.dumps(event))

    records = event.get("Records", [])

    logs_to_store, failed_items = process_records(records, s3)

    if logs_to_store:
        try:
            upload_to_s3("".join(logs_to_store), s3)
        except Exception as e:
            print("Error subiendo a S3:", str(e))
            raise e  # 🔥 Esto es clave para que NO se borren los mensajes

    return {
        "batchItemFailures": failed_items
    }

src/test

import pytest
from unittest.mock import Mock, patch
from lambda_function import process_records,lambda_handler

def test_all_success():
    event = {
        "Records": [
            {"messageId": "1", "body": "ok"},
            {"messageId": "2", "body": "ok"}
        ]
    }

    mock_s3 = Mock()

    with patch("lambda_function.s3", mock_s3):
        response = lambda_handler(event, None)

    assert response["batchItemFailures"] == []

def test_partial_failure():
    records = []

    # 97 buenos
    for i in range(97):
        records.append({"messageId": str(i), "body": "ok"})

    # 3 corruptos (sin body)
    records.append({"messageId": "bad1"})
    records.append({"messageId": "bad2"})
    records.append({"messageId": "bad3"})

    logs, failed = process_records(records, Mock())

    assert len(failed) == 3
    assert len(logs) == 97

def test_s3_failure():
    event = {
        "Records": [
            {"messageId": "1", "body": "ok"}
        ]
    }

    mock_s3 = Mock()
    mock_s3.put_object.side_effect = Exception("S3 failure")

    with patch("lambda_function.s3", mock_s3):
        with pytest.raises(Exception):
            lambda_handler(event, None)

def test_no_records():
    event = {"Records": []}
    response = lambda_handler(event, None)
    assert response["batchItemFailures"] == []

def test_all_failures():
    records = [
        {"messageId": "1"},
        {"messageId": "2"}
    ]

    logs, failed = process_records(records, Mock())

    assert len(logs) == 0
    assert len(failed) == 2


---

```

```
record_processor.py
def process_records(records):
    failed_items = []
    logs_to_store = []

    for record in records:
        try:
            message_id = record["messageId"]
            body = record["body"]

            log_entry = f"MessageId: {message_id}\nBody: {body}\n---\n"
            logs_to_store.append(log_entry)

        except Exception:
            failed_items.append({
                "itemIdentifier": record.get("messageId", "unknown")
            })

    return logs_to_store, failed_items

✅ 2️⃣ s3_uploader.py
from datetime import datetime, UTC
import os

BUCKET_NAME = os.environ.get("BUCKET_NAME", "test-bucket")

def upload_to_s3(content, s3_client):
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    file_name = f"dlq_logs_{timestamp}.txt"

    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=content
    )

✅ 3️⃣ lambda_secundaria.py (nuevo handler)
import json
import boto3

from record_processor import process_records
from s3_uploader import upload_to_s3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    print("Evento recibido:")
    print(json.dumps(event))

    records = event.get("Records", [])

    logs_to_store, failed_items = process_records(records)

    if logs_to_store:
        try:
            upload_to_s3("".join(logs_to_store), s3)
        except Exception as e:
            print("Error subiendo a S3:", str(e))
            raise e  # 🔥 mantiene mensajes en la cola

    return {
        "batchItemFailures": failed_items
    }

🧪 4️⃣ test_lambda_secundaria.py (adaptado)

Ahora ajustamos imports para nueva estructura.

import pytest
from unittest.mock import Mock, patch

from lambda_secundaria import lambda_handler
from record_processor import process_records


def test_all_success():
    event = {
        "Records": [
            {"messageId": "1", "body": "ok"},
            {"messageId": "2", "body": "ok"}
        ]
    }

    mock_s3 = Mock()

    with patch("lambda_secundaria.s3", mock_s3):
        response = lambda_handler(event, None)

    assert response["batchItemFailures"] == []


def test_partial_failure():
    records = []

    for i in range(97):
        records.append({"messageId": str(i), "body": "ok"})

    records.append({"messageId": "bad1"})
    records.append({"messageId": "bad2"})
    records.append({"messageId": "bad3"})

    logs, failed = process_records(records)

    assert len(failed) == 3
    assert len(logs) == 97


def test_s3_failure():
    event = {
        "Records": [
            {"messageId": "1", "body": "ok"}
        ]
    }

    mock_s3 = Mock()
    mock_s3.put_object.side_effect = Exception("S3 failure")

    with patch("lambda_secundaria.s3", mock_s3):
        with pytest.raises(Exception):
            lambda_handler(event, None)


def test_no_records():
    event = {"Records": []}
    response = lambda_handler(event, None)
    assert response["batchItemFailures"] == []


def test_all_failures():
    records = [
        {"messageId": "1"},
        {"messageId": "2"}
    ]

    logs, failed = process_records(records)

    assert len(logs) == 0
    assert len(failed) == 2
```

```
# =========================================================
# Archivo: src/services/procesador.py
# =========================================================
import os
import json
import base64
import logging
from services.openfga_sync_retry_hander import enviar_registro_a_reintento_o_dlq
if os.getenv("TEST_MODE") != "SANDBOX": from services.servicio_redis import ServicioRedis
from utilitarios.funcion_evento import obtener_evento_identificador, procesar_evento
from services.excepciones import (
    BadRequestError,
    RedisError,
    TransientError,
    OpenFGAError
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# =========================================================
#   PUNTO DE ENTRADA
# =========================================================
def process_message(event):
    print("Evento recibido:", event)

    if es_evento_kafka(event):
        return proceso_kafka_evento(event)

    if es_evento_sqs(event):
        return proceso_sqs_evento(event)

    raise ValueError("Origen de evento no reconocido")


def es_evento_kafka(event):
    return event.get("eventSource") == "aws:kafka"


def es_evento_sqs(event):
    return "Records" in event and event["Records"][0].get("eventSource") == "aws:sqs"

# =========================================================
#   KAFKA (MSK)
# =========================================================
def proceso_kafka_evento(event):
    batch_log = crear_batch_log("MSK")

    for partition, rec_list in event.get("records", {}).items():
        for idx, record in enumerate(rec_list):

            payload = construir_evento_payload(record)
            if payload is None:
                continue

            payload["messageId"] = f"{partition}:{idx}"
            payload["retry"] = 0

            process_with_log(payload, batch_log)

    logger.info("MSK Batch Log: " + json.dumps(batch_log))
    return batch_log


# =========================================================
#   SQS - RETORNA PARTIAL BATCH RESPONSE
# =========================================================
def proceso_sqs_evento(event):
    sqs_records = event["Records"]
    batch_log = crear_batch_log("SQS")
    failed_items = []

    for record in sqs_records:
        body = json.loads(record["body"])
        registro = body["openfgaOperations"][0]
        registro["messageId"] = record["messageId"]
        registro["retry"] = record["attributes"].get("ApproximateReceiveCount", "1")

        try:
            result = process(registro)

            if result is None:
                continue

            batch_log["itemsProcesados"] += 1
            batch_log["itemExitososBatch"].append({
                "itemIdentificador": registro["messageId"],
                "numeroReintento": registro["retry"]
            })

        except BadRequestError:
            # ❗ BAD REQUEST → DLQ automático por SQS
            batch_log["itemsFallidos"] += 1
            batch_log["itemFallidosBatch"].append({
                "itemIdentificador": registro["messageId"],
                "numeroReintento": registro["retry"],
                "error": "BadRequestError",
                "destino": "DLQ"
            })

            # ❗ SQS enviará directo a DLQ → NO LLAMAR al handler
            failed_items.append(registro["messageId"])

        except (RedisError, OpenFGAError, TransientError) as e:
            # ❗ Retry automático → SQS lo maneja
            batch_log["itemsFallidos"] += 1
            batch_log["itemFallidosBatch"].append({
                "itemIdentificador": registro["messageId"],
                "numeroReintento": registro["retry"],
                "error": e.__class__.__name__,
                "destino": "RETRY_AUTO_SQS"
            })

            # ❗ SQS hará el reintento → NO LLAMAR al handler
            failed_items.append(registro["messageId"])

    logger.info("SQS Batch Log: " + json.dumps(batch_log))

    # SOLO SE DEBE RETORNAR batchItemFailures
    if failed_items:
        return {
            "batchItemFailures": [
                {"itemIdentifier": item} for item in failed_items
            ]
        }

    # ÉXITO
    return {}



# =========================================================
#   DECODE MSK
# =========================================================
def construir_evento_payload(record):
    try:
        decoded = base64.b64decode(record["value"]).decode("utf-8")
        print("Evento DECODIFICAD0:", decoded)
        return json.loads(decoded)
    except Exception as e:
        logger.error(f"Error decodificando payload MSK: {e}")
        return None


# =========================================================
#   PROCESAMIENTO INDIVIDUAL
# =========================================================
def process_with_log(event, batch_log):
    try:
        result = process(event)

        if result is None:
            return

        batch_log["itemsProcesados"] += 1
        batch_log["itemExitososBatch"].append({
            "itemIdentificador": event["messageId"],
            "numeroReintento": event["retry"]
        })

    except BadRequestError:
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event["messageId"],
            "numeroReintento": event["retry"],
            "error": "BadRequestError",
            "destino": "DLQ"
        })

        enviar_registro_a_reintento_o_dlq(event, es_dlq=True)

    except (RedisError, OpenFGAError, TransientError) as e:
        batch_log["itemsFallidos"] += 1
        batch_log["itemFallidosBatch"].append({
            "itemIdentificador": event["messageId"],
            "numeroReintento": event["retry"],
            "error": e.__class__.__name__,
            "destino": "RETRY"
        })

        enviar_registro_a_reintento_o_dlq(event, es_dlq=False)


# =========================================================
#   LÓGICA REAL
# =========================================================
def process(event):

    # SANDBOX mock (por si aún quieres pruebas en consola)
    if os.getenv("TEST_MODE") == "SANDBOX":
        action = event.get("sandbox_action", "OK")
        attempt = int(event.get("retry", 0))
        print("action")
        print(action)
        print("attempt")
        print(attempt)
        # SIEMPRE FALLA → reintentos
        if action == "ALWAYS_FAIL":
            raise TransientError("mock failure")

        # EXISTENTES
        if action == "IDEMPOTENTE":
            return None

        if action == "RETRY":
            if attempt >= 2:
                return True
            raise TransientError("retry simulated")

        if action == "DLQ":
            raise BadRequestError("dlq simulated")

        if action == "REDIS":
            raise RedisError("redis simulated")

        if action == "OPENFGA":
            raise OpenFGAError("openfga simulated")

        return True

    if os.getenv("TEST_MODE") != "SANDBOX": 
        redis = ServicioRedis()
        event_identifier = obtener_evento_identificador(event)

        new_event = redis.guardar_evento(event, event_identifier["fuente"], event_identifier["tipo"])

        if not new_event:
            return None

    procesar_evento(event, event_identifier["fuente"], event_identifier["tipo"])
    return True


# =========================================================
#   UTILIDADES
# =========================================================
def crear_batch_log(origen):
    return {
        "origen": origen,
        "itemsProcesados": 0,
        "itemsFallidos": 0,
        "itemExitososBatch": [],
        "itemFallidosBatch": []
    }

```
