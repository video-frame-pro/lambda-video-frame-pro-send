import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

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

        mock_send_email.assert_called_once()
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body']['status'], "SEND_SUCCESS")
        self.assertEqual(response['body']['email'], "test@example.com")
        self.assertEqual(response['body']['processingLink'], "http://example.com/download")

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

        mock_send_email.assert_called_once()
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body']['status'], "SEND_ERROR")
        self.assertEqual(response['body']['email'], "test@example.com")

    def test_lambda_handler_missing_email(self):
        event = {
            "body": json.dumps({
                "error": False,
                "processingLink": "http://example.com/download"
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("Missing required fields: email", response['body']['error'])

    def test_lambda_handler_missing_processing_link(self):
        event = {
            "body": json.dumps({
                "error": False,
                "email": "test@example.com"
            })
        }
        context = {}

        response = lambda_handler(event, context)

        self.assertEqual(response['statusCode'], 400)
        self.assertIn("'processingLink' is required when 'error' is False.", response['body']['error'])

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

    @patch('src.send.send.urllib.request.urlopen')
    def test_send_email_exception(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Error")
        data = {
            "email": "test@example.com"
        }
        subject = "Test Email"
        html_content = "<h1>Test Content</h1>"

        with self.assertLogs(logger, level='ERROR') as log:
            send_email(data, subject, html_content)
            self.assertIn("Error while sending email", log.output[-1])

    @patch('src.send.send.send_email')
    def test_process_email_success(self, mock_send_email):
        data = {
            "error": False,
            "email": "test@example.com",
            "processingLink": "http://example.com/download"
        }

        mock_send_email.return_value = None

        response = process_email(data)

        mock_send_email.assert_called_once()
        self.assertEqual(response["status"], "SEND_SUCCESS")
        self.assertEqual(response["email"], "test@example.com")
        self.assertEqual(response["processingLink"], "http://example.com/download")

    @patch('src.send.send.send_email')
    def test_process_email_error(self, mock_send_email):
        data = {
            "error": True,
            "email": "test@example.com"
        }

        mock_send_email.return_value = None

        response = process_email(data)

        mock_send_email.assert_called_once()
        self.assertEqual(response["status"], "SEND_ERROR")
        self.assertEqual(response["email"], "test@example.com")
