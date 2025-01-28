######### PREFIXO DO PROJETO ###########################################
prefix_name = "video-frame-pro" # Prefixo para nomear todos os recursos

######### AWS INFOS ####################################################
aws_region = "us-east-1" # Região AWS onde os recursos serão provisionados

######### PROJECT INFOS ################################################
lambda_name     = "send" # Nome da função Lambda principal
lambda_handler  = "send.lambda_handler" # Handler da função Lambda principal
lambda_zip_path = "../lambda/send/send.zip" # Caminho para o ZIP da função Lambda
lambda_runtime  = "python3.12" # Runtime da função Lambda principal

######### LOGS CLOUD WATCH #############################################
log_retention_days = 7 # Dias para retenção dos logs no CloudWatch

######### SSM VARIABLES INFOS ##########################################
brevo_token_ssm = "/video-frame-pro/brevo/token" # Caminho no SSM para o Token do Brevo

