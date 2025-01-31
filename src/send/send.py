import sys
sys.path.append('/opt/bin/')

import json
import logging
import os
import urllib.request
import urllib.error

# Configurações globais
EMAIL_SENDER = "videoframeprofiap@gmail.com"
BREVO_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TOKEN = os.environ["BREVO_TOKEN"]

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def create_response(status_code, message=None, data=None):
    """
    Gera uma resposta formatada.
    """
    response = {"statusCode": status_code, "body": {}}
    if message:
        response["body"]["message"] = message
    if data:
        response["body"].update(data)
    return response

def normalize_body(event):
    """
    Normaliza o corpo da requisição para garantir que seja um dicionário.
    """
    if isinstance(event.get("body"), str):
        return json.loads(event["body"])  # Desserializa string JSON para dicionário
    elif isinstance(event.get("body"), dict):
        return event["body"]  # Já está em formato de dicionário
    else:
        raise ValueError("Request body is missing or invalid.")

def validate_request(body):
    """
    Valida os campos obrigatórios na requisição.
    """
    required_fields = ["email"]
    missing_fields = [field for field in required_fields if field not in body]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    # Valida 'frame_url' caso 'error' seja False
    if not body.get("error", False) and "frame_url" not in body:
        raise ValueError("'frame_url' is required when 'error' is False.")

def send_email(data, subject, html_content):
    """
    Envia um e-mail utilizando a API Brevo.
    """
    headers = {
        "api-key": BREVO_TOKEN,
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "sender": {"email": EMAIL_SENDER},
        "to": [{"email": data["email"]}],
        "subject": subject,
        "htmlContent": html_content
    }).encode("utf-8")

    try:
        request = urllib.request.Request(BREVO_URL, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(request) as response:
            if response.status in [202, 201]:
                logger.info(f"Email sent to {data['email']} with subject: {subject}")
            else:
                logger.error(f"Failed to send email. HTTP Status: {response.status}")
    except urllib.error.URLError as e:
        logger.error(f"Error while sending email: {e}")

def process_email(data):
    """
    Processa o envio do e-mail com base no flag de erro.
    """
    logo_url = "https://i.ibb.co/tLQk12V/logo.png"  # URL do logotipo

    if data.get("error", False):
        logger.info("Error flag is True. Sending error email.")
        subject = "Video Frame Pro - Processing Error"
        html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
                    <table align="center" width="600" style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <tr>
                            <td align="center">
                                <img src="{logo_url}" alt="Video Frame Pro" style="width: 200px; margin-bottom: 20px;">
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; text-align: center;">
                                <h1 style="color: #ff4c4c;">Oops! Something went wrong</h1>
                                <p style="font-size: 16px; color: #555;">We were unable to complete the processing of your video. Please try again later or contact support if the issue persists.</p>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding-top: 20px;">
                                <a href="mailto:videoframeprofiap@gmail.com" style="background-color: #ff4c4c; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-size: 16px;">Contact Support</a>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding-top: 20px; font-size: 12px; color: #999;">
                                &copy; 2025 Video Frame Pro. All rights reserved.
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        """
        send_email(data, subject, html_content)
        return {
            "email": data["email"]
        }
    else:
        logger.info("Error flag is False. Sending success email.")
        subject = "Video Frame Pro - Download Link"
        html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
                    <table align="center" width="600" style="background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <tr>
                            <td align="center">
                                <img src="{logo_url}" alt="Video Frame Pro" style="width: 200px; margin-bottom: 20px;">
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 20px; text-align: center;">
                                <h1 style="color: #4caf50;">Your video is ready!</h1>
                                <p style="font-size: 16px; color: #555;">Click the button below to download your processed video:</p>
                                <a href="{data['frame_url']}" style="background-color: #4caf50; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 5px; font-size: 16px;">Download Video</a>
                            </td>
                        </tr>
                        <tr>
                            <td align="center" style="padding-top: 20px; font-size: 12px; color: #999;">
                                &copy; 2025 Video Frame Pro. All rights reserved.
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        """
        send_email(data, subject, html_content)
        return {
            "email": data["email"],
            "frame_url": data["frame_url"]
        }

def lambda_handler(event, context):
    """
    Entrada principal da Lambda.
    """
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Normalizar o corpo da requisição
        body = normalize_body(event)

        # Validar os campos obrigatórios no corpo da requisição
        validate_request(body)

        # Processar o envio do e-mail
        response_data = process_email(body)

        return create_response(200, data=response_data)

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")

        try:
            # Garante que email e frame_url tenham um valor válido antes de reenviar o e-mail
            body.setdefault("email", "nao preenchido")
            body.setdefault("frame_url", "nao preenchido")

            # Define explicitamente error como True
            body["error"] = True

            # Tenta enviar o e-mail de erro
            logger.info("Attempting to send failure email due to a validation error.")
            process_email(body)
        except Exception as email_error:
            logger.error(f"Failed to send error email: {email_error}")

        return create_response(400, message=str(ve))

    except Exception as e:
        logger.error(f"Unexpected error: {e}")

        try:
            # Garante que email e frame_url tenham um valor válido antes de reenviar o e-mail
            body.setdefault("email", "nao preenchido")
            body.setdefault("frame_url", "nao preenchido")

            # Define explicitamente error como True
            body["error"] = True

            # Tenta enviar o e-mail de erro
            logger.info("Attempting to send failure email due to an exception.")
            process_email(body)
        except Exception as email_error:
            logger.error(f"Failed to send error email: {email_error}")

        return create_response(500, message="An unexpected error occurred. Please try again later.")