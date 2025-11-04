# 🧩 Proyecto Lambda + SQS con Terraform

Este proyecto implementa una arquitectura **Lambda + SQS + DLQ (Dead Letter Queue)** usando **Terraform** y **AWS CLI (PowerShell)**.  
Permite desplegar una función Lambda que procesa mensajes de una cola SQS principal, y en caso de error, los mensajes fallidos se envían automáticamente a una cola de errores (DLQ).

---

## 📁 Estructura de Archivos

```
.
├── main.tf              # Código Terraform para crear los recursos
├── lambda_function.py   # Lógica principal de la Lambda
├── trust-policy.json    # Política de confianza para IAM Role
├── msg_ok.json          # Mensaje exitoso de prueba
└── msg_fail.json        # Mensaje que genera error (para probar la DLQ)
```

---

## 🧠 Explicación del Flujo

1. **SQS Principal** recibe mensajes.
2. **Lambda** se activa automáticamente al recibir mensajes.
3. Si el procesamiento **falla**, la Lambda lanza una excepción → el mensaje se reintenta hasta 3 veces.
4. Si aún falla, **SQS envía el mensaje a la DLQ**.
5. Todo el proceso se registra en **CloudWatch Logs**.

---

## ⚙️ Archivos Clave

### `trust-policy.json`
```json
{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": { "Service": "lambda.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }]
}
```

### `lambda_function.py`
```python
import json

def lambda_handler(event, context):
    results = []
    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            print(f"📨 Mensaje recibido: {body}")

            # Simular procesamiento
            if not body.get("process_ok", True):
                raise ValueError(f"❌ Error procesando item_id={body.get('item_id')}")

            # Si todo va bien
            print(f"✅ Procesado con éxito item_id={body.get('item_id')}")
            results.append({"item_id": body.get("item_id"), "status": "success"})

        except Exception as e:
            print(f"⚠️ Excepción capturada: {e}")
            raise e

    return {
        "status": "OK",
        "processed": results,
        "records_count": len(results)
    }
```

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
}

provider "aws" {
  region = "us-east-1"
}

# ========= SQS DLQ ==========
resource "aws_sqs_queue" "dlq" {
  name = "${var.custom_name}-dlq"
}

# ========= SQS principal ==========
resource "aws_sqs_queue" "main" {
  name = "${var.custom_name}-main"

  # RedrivePolicy: enviar a la DLQ después de 3 intentos
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })

  # 👇 visibilidad mayor que el timeout de la Lambda
  visibility_timeout_seconds = 90
}

# ========= IAM Role para Lambda ==========
resource "aws_iam_role" "lambda_role" {
  name = "${var.custom_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# ========= IAM Policy inline (logs y SQS) ==========
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.custom_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.main.arn,
          aws_sqs_queue.dlq.arn
        ]
      }
    ]
  })
}

# ========= Lambda Function ==========
resource "aws_lambda_function" "lambda" {
  function_name = "${var.custom_name}-lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  memory_size   = 256
  filename      = "function.zip"
  source_code_hash = filebase64sha256("function.zip")
}

# ========= Conectar Lambda con SQS ==========
resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn = aws_sqs_queue.main.arn
  function_name    = aws_lambda_function.lambda.arn
  batch_size       = 10
  enabled          = true
}

# ========= Outputs ==========
output "main_queue_url" {
  value = aws_sqs_queue.main.url
}

output "dlq_queue_url" {
  value = aws_sqs_queue.dlq.url
}

output "lambda_name" {
  value = aws_lambda_function.lambda.function_name
}

# ========= Comandos PowerShell para pruebas ==========
output "send_ok_command" {
  description = "Comando PowerShell para enviar mensaje OK (usa archivo msg_ok.json)"
  value = "aws sqs send-message --queue-url ${aws_sqs_queue.main.url} --message-body file://msg_ok.json"
}

output "send_fail_command" {
  description = "Comando PowerShell para enviar mensaje de falla (usa archivo msg_fail.json)"
  value = "aws sqs send-message --queue-url ${aws_sqs_queue.main.url} --message-body file://msg_fail.json"
}
```

### `variables.tf`
```terraform
variable "project_name" {
  description = "Nombre base del proyecto (se usa como prefijo en las colas y Lambda)"
  type        = string
}

variable "aws_region" {
  description = "Región de AWS donde se desplegarán los recursos"
  type        = string
  default     = "us-east-1"
}

variable "custom_name" {
  description = "Prefijo personalizado para nombrar los recursos (por ejemplo, mi-lambda-sqs-demo)"
  type        = string
}
```

---

## 🧪 Archivos de Mensajes

### `msg_ok.json`
```json
{
  "process_ok": true,
  "item_id": 100
}
```

### `msg_fail.json`
```json
{
  "process_ok": false,
  "item_id": 200
}
```

---

## 🚀 Despliegue

### 1️⃣ Crear y empacar la Lambda
```powershell
Compress-Archive -Path lambda_function.py -DestinationPath function.zip -Force
```

### 2️⃣ Inicializar Terraform
```powershell
terraform init
terraform apply -auto-approve
```

### 3️⃣ Ver los outputs
```powershell
terraform output
```

Obtendrás las URLs de las colas y los comandos listos para enviar mensajes.

---

## 🧾 Enviar mensajes de prueba

### Mensaje exitoso
```powershell
aws sqs send-message --queue-url "<MAIN_URL>" --message-body file://msg_ok.json
```

### Mensaje con error (va a la DLQ)
```powershell
aws sqs send-message --queue-url "<MAIN_URL>" --message-body file://msg_fail.json
```

---

## 🧹 Limpieza de recursos
```powershell
terraform destroy -auto-approve
```

---

## 📘 Resumen General

| Componente | Descripción |
|-------------|-------------|
| **Lambda** | Procesa mensajes de SQS, lanza excepción si `process_ok = false` |
| **SQS Main** | Cola principal de mensajes |
| **SQS DLQ** | Recibe mensajes fallidos tras 3 intentos |
| **IAM Role/Policy** | Permite a Lambda leer de SQS y escribir en CloudWatch |
| **Terraform** | Gestiona toda la infraestructura como código |
| **PowerShell** | Se usa para enviar mensajes de prueba con AWS CLI |

---

> 💡 **Consejo:** Puedes ver los logs en CloudWatch con el nombre del grupo `/aws/lambda/<nombre_lambda>` para verificar el flujo de mensajes.
