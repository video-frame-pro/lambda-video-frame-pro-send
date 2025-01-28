import json
import os
from unittest import TestCase
from unittest.mock import patch

os.environ['BREVO_TOKEN'] = 'mocked_api_key'

from src.send.send import lambda_handler, process_email, send_email, logger


class TestLambdaFunction(TestCase):

    @patch('src.send.send.send_email')
    def test_lambda_handler_success(self, mock_send_email):
        event = {
            "body": json.dumps({
                "error": False,
                "processingLink": "http://example.com/download",
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
        self.assertEqual(response_body["processingLink"], "http://example.com/download")

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
                "processingLink": "http://example.com/download"
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
        self.assertIn("'processingLink' is required when 'error' is False.", response_body["message"])

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

