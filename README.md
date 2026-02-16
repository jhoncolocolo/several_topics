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
