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

lambda.py

import json
import boto3
import os
from datetime import datetime

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["BUCKET_NAME"]

def lambda_handler(event, context):
    print("Evento recibido desde SQS DLQ:")
    print(json.dumps(event))

    failed_items = []
    logs_to_store = []

    for record in event.get("Records", []):
        try:
            message_id = record["messageId"]
            body = record["body"]

            log_entry = f"MessageId: {message_id}\nBody: {body}\n---\n"
            logs_to_store.append(log_entry)

            print(f"Procesado mensaje {message_id}")

        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")
            failed_items.append({
                "itemIdentifier": record["messageId"]
            })

    # Guardar en S3
    if logs_to_store:
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        file_name = f"dlq_logs_{timestamp}.txt"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body="".join(logs_to_store)
        )

        print(f"Archivo subido a S3: {file_name}")

    return {
        "batchItemFailures": failed_items
    }

```
