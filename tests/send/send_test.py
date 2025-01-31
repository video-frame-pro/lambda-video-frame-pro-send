import json
import os
from unittest import TestCase
from unittest.mock import patch

# Definir variáveis de ambiente mockadas
os.environ['BREVO_TOKEN'] = 'mocked_api_key'

# Importar a Lambda após definir variáveis de ambiente
from src.send.send import lambda_handler, process_email, send_email, logger

class TestLambdaFunction(TestCase):

    @patch('src.send.send.send_email')
    def test_lambda_handler_success(self, mock_send_email):
        event = {
            "body": json.dumps({
                "error": False,
                "frame_url": "http://example.com/download",
                "email": "test@example.com"
            })
        }
        context = {}

        mock_send_email.return_value = None

        response = lambda_handler(event, context)
        response_body = response['body']  # Extrair o corpo da resposta

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response_body["email"], "test@example.com")
        self.assertEqual(response_body["frame_url"], "http://example.com/download")

    @patch('src.send.send.send_email')
    def test_lambda_handler_error(self, mock_send_email):
        event = {
            "body": json.dumps({
                "error": True,
                "email": "test@example.com"
            })
        }
        context = {}

        mock_send_email.return_value = None

        response = lambda_handler(event, context)
        response_body = response['body']  # Extrair o corpo da resposta

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response_body["email"], "test@example.com")

    def test_lambda_handler_missing_email(self):
        event = {
            "body": json.dumps({
                "error": False,
                "frame_url": "http://example.com/download"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        response_body = response['body']  # Extrair o corpo da resposta

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Missing required fields: email", response_body["message"])

    def test_lambda_handler_missing_processing_link(self):
        event = {
            "body": json.dumps({
                "error": False,
                "email": "test@example.com"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        response_body = response['body']  # Extrair o corpo da resposta

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("'frame_url' is required when 'error' is False.", response_body["message"])

    @patch('src.send.send.urllib.request.urlopen')
    def test_send_email_success(self, mock_urlopen):
        mock_urlopen.return_value.status = 202
        data = {
            "email": "test@example.com"
        }
        subject = "Test Email"
        html_content = "<h1>Test Content</h1>"

        send_email(data, subject, html_content)

        mock_urlopen.assert_called_once()

    @patch('src.send.send.urllib.request.urlopen')
    def test_send_email_failure(self, mock_urlopen):
        mock_urlopen.return_value.status = 500
        data = {
            "email": "test@example.com"
        }
        subject = "Test Email"
        html_content = "<h1>Test Content</h1>"

        send_email(data, subject, html_content)

        mock_urlopen.assert_called_once()


    @patch('src.send.send.process_email', side_effect=Exception("Simulated unexpected error"))
    def test_lambda_handler_unexpected_error(self, mock_process_email):
        """
        Testa se a Lambda lida corretamente com erros inesperados e retorna statusCode 500.
        """

        event = {
            "body": json.dumps({
                "error": False,
                "frame_url": "http://example.com/download",
                "email": "test@example.com"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        response_body = response["body"]  # Extrair o corpo da resposta

        # Assertions
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("An unexpected error occurred", response_body["message"])

    @patch('src.send.send.process_email', side_effect=Exception("Simulated unexpected error"))
    @patch('src.send.send.logger.error')
    def test_lambda_handler_unexpected_error_logs(self, mock_logger_error, mock_process_email):
        """
        Testa se a Lambda loga corretamente um erro inesperado.
        """

        event = {
            "body": json.dumps({
                "error": False,
                "frame_url": "http://example.com/download",
                "email": "test@example.com"
            })
        }
        context = {}

        lambda_handler(event, context)

        # Verifica se o logger foi chamado para registrar o erro
        mock_logger_error.assert_any_call("Unexpected error: Simulated unexpected error")

    @patch('src.send.send.process_email', side_effect=Exception("Simulated unexpected error"))
    @patch('src.send.send.process_email', side_effect=Exception("Simulated email send failure"))
    def test_lambda_handler_fails_sending_error_email(self, mock_process_email, mock_process_email_failure):
        """
        Testa se a Lambda lida corretamente com falhas ao tentar enviar o e-mail de erro.
        """

        event = {
            "body": json.dumps({
                "error": False,
                "frame_url": "http://example.com/download",
                "email": "test@example.com"
            })
        }
        context = {}

        response = lambda_handler(event, context)
        response_body = response["body"]  # Extrair o corpo da resposta

        # Assertions
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("An unexpected error occurred", response_body["message"])