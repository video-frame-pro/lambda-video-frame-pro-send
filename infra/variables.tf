# Região da AWS
variable "aws_region" {
  description = "Região onde os recursos serão provisionados"
  type        = string
  default     = "us-east-1"
}

# Nome da Lambda de sendemail
variable "lambda_sendemail_name" {
  description = "Nome da função Lambda de registro"
  type        = string
}

# Tempo de retenção dos logs
variable "log_retention_days" {
  description = "Número de dias para reter logs no CloudWatch"
  default     = 7
}

# Nome da fila SQS
variable "sqs_queue_name" {
  description = "Nome da fila SQS"
  type        = string
}