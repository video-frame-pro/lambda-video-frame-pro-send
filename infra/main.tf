provider "aws" {
  region = var.aws_region
}

# Obter informações sobre a conta AWS (ID da conta, ARN, etc.)
data "aws_caller_identity" "current" {}

# Recuperar valores do SSM
data "aws_ssm_parameter" "brevo_token" {
  name = "/video-frame-pro/brevo/token"
}

# Função Lambda para sendemail de Usuário
resource "aws_lambda_function" "sendemail" {
  function_name = var.lambda_sendemail_name

  handler = "sendemail.lambda_handler"
  runtime = "python3.8"
  role    = aws_iam_role.lambda_sendemail_role.arn

  environment {
    variables = {
      cognito_user_pool_id = data.aws_ssm_parameter.brevo_token.value
      cognito_client_id    = data.aws_ssm_parameter.brevo_token.value
    }
  }

  filename         = "../lambda/sendemail/sendemail_lambda_function.zip"
  source_code_hash = filebase64sha256("../lambda/sendemail/sendemail_lambda_function.zip")
}


resource "aws_cloudwatch_log_group" "lambda_sendemail_log_group" {
  name              = "/aws/lambda/${aws_lambda_function.sendemail.function_name}"
  retention_in_days = var.log_retention_days
}

# Role para Lambda de sendemail
resource "aws_iam_role" "lambda_sendemail_role" {
  name = "lambda_sendemail_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Política de Permissões para CloudWatch Logs
resource "aws_iam_policy" "lambda_logging_policy" {
  name        = "lambda_logging_policy"
  description = "Permissões para Lambdas gravarem nos logs do CloudWatch"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*"
      }
    ]
  })
}

# Política de Permissão para SQS
resource "aws_iam_policy" "lambda_sqs_policy" {
  name        = "lambda_sqs_policy"
  description = "Permissões para a Lambda acessar a fila SQS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "sqs:ReceiveMessage",
          "sqs:GetQueueAttributes"
        ],
        Resource = "arn:aws:sqs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${var.sqs_queue_name}"
      }
    ]
  })
}

# Anexar a política de logs à role da Lambda de sendemail
resource "aws_iam_role_policy_attachment" "sendemail_logging_policy_attachment" {
  role       = aws_iam_role.lambda_sendemail_role.name
  policy_arn = aws_iam_policy.lambda_logging_policy.arn
}

# Anexar a política de SQS à role da Lambda de sendemail
resource "aws_iam_role_policy_attachment" "lambda_sqs_policy_attachment" {
  role       = aws_iam_role.lambda_sendemail_role.name
  policy_arn = aws_iam_policy.lambda_sqs_policy.arn
}
