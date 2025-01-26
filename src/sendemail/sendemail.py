import sys
sys.path.append('/opt/bin/')

import json
import requests
import logging
import boto3
import os

email_sender = "videoframeprofiap@gmail.com"
url_smtp = "https://api.brevo.com/v3/smtp/email"
queue_url = 'https://sqs.${var.aws_region}.amazonaws.com/${data.aws_caller_identity.current.account_id}/${var.sqs_queue_name}'
email_api_key = os.environ['email_api_key']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs_client = boto3.client('sqs', region_name=os.environ["aws_region"])

def lambda_handler(event, context):
    logger.info(f"event: {event}")
    for message in event['Records']:
        body_message = json.loads(message['body'])
        process_message(body_message)
        
        receipt_handle = message['receiptHandle']
        delete_message(receipt_handle)

def process_message(body_message):
    status = body_message['status']
    destinatario = body_message['to_address']

    if status == "sucesso":
        url_download = body_message['url_download']
        send_email_success(destinatario, url_download)
    else:
        send_email_error(destinatario)

    return {"statusCode": 200}

def send_email_success(destinatario, url_download):
    headers = {
        "api-key": email_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "sender": {"email": email_sender},
        "to": [{"email": destinatario}],
        "subject": "Video Frame Pro",
        "htmlContent": f"<html><body><h1>Link para download do .zip: {url_download}</h1></body></html>"
    }

    try:
        response = requests.post(url_smtp, headers=headers, json=data)

        if response.status_code in [202, 201]:
            logger.info("✅ E-mail enviado com sucesso!")
        else:
            logger.info(f"❌ Erro ao enviar o e-mail: {response.status_code}")
    except Exception as e:
        logger.info(f"Erro na requisição: {str(e)}")
        

def send_email_error(destinatario):
    headers = {
        "api-key": email_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "sender": {"email": email_sender},
        "to": [{"email": destinatario}],
        "subject": "Video Frame Pro",
        "htmlContent": "<html><body><h1>Erro ao processar o video</h1></body></html>"
    }

    try:
        response = requests.post(url_smtp, headers=headers, json=data)

        if response.status_code in [200, 201, 202]:
            logger.info(f"✅ E-mail de erro enviado.")
        else:
            logger.info(f"❌ Erro ao enviar o e-mail de erro: {response.status_code}")

    except Exception as e:
        logger.info("Erro na requisição:", str(e))

def delete_message(receipt_handle):
    try:
        sqs_client.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        logger.info(f"Mensagem deletada da fila.")
    except Exception as e:
        logger.info("Erro ao deletar a mensagem da fila:", str(e))
