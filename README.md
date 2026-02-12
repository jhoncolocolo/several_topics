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
#########################################
# PROVIDERS
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
# IAM ROLE + POLICY (LAMBDA PRINCIPAL)
#########################################

resource "aws_iam_role" "lambda_role" {
  name = "${var.project_prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_prefix}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Logs
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      },

      # SQS
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
          "sqs:GetQueueUrl"
        ],
        Resource = "*"
      },

      # Lambda invoke
      {
        Effect   = "Allow",
        Action   = ["lambda:InvokeFunction"],
        Resource = "*"
      }
    ]
  })
}

#########################################
# SQS QUEUES
#########################################

resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_prefix}-dlq"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "retry" {
  name                       = "${var.project_prefix}-retry"
  visibility_timeout_seconds = var.retry_visibility_timeout_seconds

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.retry_max_receive_count
  })
}

#########################################
# LAMBDA PACKAGING
#########################################

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/lambda.zip"

  excludes = [
    ".terraform/*",
    "*.tfstate",
    "*.zip",
    "tests/*",
    "__pycache__/*",
    ".pytest_cache/*"
  ]
}

#########################################
# LAMBDA PRINCIPAL
#########################################

resource "aws_lambda_function" "main_lambda" {
  function_name = "${var.project_prefix}-main-lambda"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"

  filename    = data.archive_file.lambda_zip.output_path
  timeout     = var.lambda_timeout_seconds
  memory_size = var.lambda_memory_mb

  environment {
    variables = merge(
      {
        TEST_MODE        = "SANDBOX"
        SQS_URL_ENDPOINT = var.sqs_url_endpoint
        RETRY_QUEUE_URL  = aws_sqs_queue.retry.url
        DLQ_QUEUE_URL    = aws_sqs_queue.dlq.url
      },
      var.EXTRA_ENV_VARS
    )
  }
}

#########################################
# PERMISSIONS
#########################################

resource "aws_lambda_permission" "allow_sqs_retry" {
  statement_id  = "${var.project_prefix}-allow-sqs-retry"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.main_lambda.arn
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.retry.arn
}

#########################################
# EVENT SOURCE MAPPING (RETRY → MAIN)
#########################################

resource "aws_lambda_event_source_mapping" "retry_to_lambda" {
  event_source_arn = aws_sqs_queue.retry.arn
  function_name    = aws_lambda_function.main_lambda.arn
  batch_size       = var.batch_size
  enabled          = true

  function_response_types = ["ReportBatchItemFailures"]
}

#########################################
# ===========================
# NUEVO: MONITOREO DE DLQ
# ===========================
#########################################

# S3 BUCKET
resource "aws_s3_bucket" "dlq_bucket" {
  bucket        = "mi_bucket_publicado"
  force_destroy = true
}

# IAM ROLE
resource "aws_iam_role" "dlq_lambda_role" {
  name = "${var.project_prefix}-dlq-monitor-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy" "dlq_lambda_policy" {
  name = "${var.project_prefix}-dlq-monitor-policy"
  role = aws_iam_role.dlq_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      # Logs
      {
        Effect = "Allow",
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:*:*:*"
      },

      # SQS DLQ
      {
        Effect = "Allow",
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = aws_sqs_queue.dlq.arn
      },

      # S3
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject"
        ],
        Resource = "${aws_s3_bucket.dlq_bucket.arn}/*"
      }
    ]
  })
}

# LAMBDA DLQ
resource "aws_lambda_function" "dlq_monitor_lambda" {
  function_name = "${var.project_prefix}-monitoreo-dlq"
  role          = aws_iam_role.dlq_lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"

  filename = data.archive_file.lambda_zip.output_path
  timeout  = 30

  environment {
    variables = {
      DLQ_QUEUE_URL = aws_sqs_queue.dlq.url
      DLQ_BUCKET    = aws_s3_bucket.dlq_bucket.bucket
    }
  }
}

resource "aws_lambda_permission" "allow_sqs_dlq" {
  statement_id  = "${var.project_prefix}-allow-sqs-dlq"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.dlq_monitor_lambda.arn
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.dlq.arn
}

resource "aws_lambda_event_source_mapping" "dlq_to_monitor_lambda" {
  event_source_arn = aws_sqs_queue.dlq.arn
  function_name    = aws_lambda_function.dlq_monitor_lambda.arn

  batch_size                         = 100
  maximum_batching_window_in_seconds = 5
  enabled                            = true

  function_response_types = ["ReportBatchItemFailures"]
}

#########################################
# OUTPUTS
#########################################

output "retry_queue_url" {
  value = aws_sqs_queue.retry.url
}

output "dlq_queue_url" {
  value = aws_sqs_queue.dlq.url
}

output "lambda_function_name" {
  value = aws_lambda_function.main_lambda.function_name
}
```
