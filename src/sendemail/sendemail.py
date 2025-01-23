import sys
import json
import requests
import os
import logging

# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

sys.path.append('/opt/bin/')

email_sender = "videoframeprofiap@gmail.com"
email_api_key = os.environ['email_api_key']

url_smtp = "https://api.brevo.com/v3/smtp/email"

def lambda_handler(event, context):
    logger.info("Iniciando o processamento do evento...")

    try:
        for message in event['Records']:
            logger.debug(f"Mensagem recebida: {message}")
            response = process_message(message)

            if response['statusCode'] not in [200, 201, 202]:
                logger.error(f"Erro ao processar mensagem: {response}")
                to_address = message['body']['to_address']
                send_email_error(to_address)
            else:
                logger.info(f"Mensagem processada com sucesso: {response}")

        return {
            'statusCode': 200,
            'body': json.dumps('Processamento concluído com sucesso.')
        }
    except Exception as e:
        logger.exception("Erro durante o processamento do evento.")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro durante o processamento: {str(e)}")
        }

def process_message(message):
    try:
        body_message = json.loads(message['body'])
        status = body_message['status']
        destinatario = body_message['to_address']

        if status == "sucesso":
            logger.info(f"Processando mensagem de sucesso para {destinatario}")
            url_download = body_message['url_download']
            response = send_email_success(destinatario, url_download)
        else:
            logger.warning(f"Status não é 'sucesso' para {destinatario}. Enviando e-mail de erro.")
            response = send_email_error(destinatario)

        return response
    except Exception as e:
        logger.exception("Erro ao processar a mensagem.")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro ao processar a mensagem: {str(e)}")
        }

def send_email_success(destinatario, url_download):
    headers = {
        "api-key": email_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "sender": {"email": email_sender},
        "to": [{"email": destinatario}],
        "subject": "Seu vídeo está pronto para download!",
        "htmlContent": f"""
        <html>
        <body>
            <div style="font-family: Arial, sans-serif; text-align: center;">
                <img alt="Video Frame Pro Logo" style="width: 150px; margin-bottom: 20px;" />
                <h1 style="color: #2E86C1;">Olá!</h1>
                <p style="font-size: 16px; color: #333;">
                    Seu vídeo foi processado com sucesso e está disponível para download.
                </p>
                <p>
                    <a href="{url_download}" style="display: inline-block; padding: 10px 20px; color: white; background-color: #28a745; text-decoration: none; border-radius: 5px; font-size: 16px;">
                        Clique aqui para baixar seu arquivo
                    </a>
                </p>
                <p style="font-size: 14px; color: #555;">
                    Obrigado por usar o Video Frame Pro! Se tiver dúvidas, entre em contato conosco.
                </p>
            </div>
        </body>
        </html>
        """
    }

    try:
        logger.info(f"Enviando e-mail de sucesso para {destinatario}...")
        response = requests.post(url_smtp, headers=headers, json=data)

        if response.status_code in [202, 201]:
            logger.info(f"E-mail enviado com sucesso para {destinatario}.")
            return {
                'statusCode': response.status_code,
                'body': json.dumps('E-mail enviado com sucesso!')
            }
        else:
            logger.error(f"Erro ao enviar o e-mail para {destinatario}: {response.status_code}")
            return {
                'statusCode': response.status_code,
                'body': json.dumps(f'Erro ao enviar o e-mail: {response.status_code}')
            }

    except Exception as e:
        logger.exception(f"Erro ao enviar o e-mail para {destinatario}.")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro na requisição: {str(e)}")
        }

def send_email_error(destinatario):
    headers = {
        "api-key": email_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "sender": {"email": email_sender},
        "to": [{"email": destinatario}],
        "subject": "Video Frame Pro",
        "htmlContent": "<html><body><h1>Erro ao processar o vídeo</h1></body></html>"
    }

    try:
        logger.info(f"Enviando e-mail de erro para {destinatario}...")
        response = requests.post(url_smtp, headers=headers, json=data)

        if response.status_code in [200, 201, 202]:
            logger.info(f"E-mail de erro enviado para {destinatario}.")
            return {
                'statusCode': response.status_code,
                'body': json.dumps('E-mail de erro enviado.')
            }
        else:
            logger.error(f"Erro ao enviar o e-mail de erro para {destinatario}: {response.status_code}")
            return {
                'statusCode': response.status_code,
                'body': json.dumps(f"Erro ao enviar o e-mail de erro: {response.status_code}")
            }

    except Exception as e:
        logger.exception(f"Erro ao enviar o e-mail de erro para {destinatario}.")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro na requisição: {str(e)}")
        }
