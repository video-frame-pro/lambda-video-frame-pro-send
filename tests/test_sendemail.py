import json
import os
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

from botocore.exceptions import ClientError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.sendemail.sendemail import (lambda_handler, process_message,
                                     send_email_error, send_email_success)


class TestLambdaFunction(TestCase):

    @patch('src.sendemail.sendemail.process_message')
    @patch('src.sendemail.sendemail.send_email_error')
    def test_lambda_handler_email_success(self, mock_send_email_error, mock_process_message):
        mock_process_message.return_value = {'statusCode': 200}
        event = {
            'Records': [{
                'body': {
                    'status': 'sucesso',
                    'to_address': 'test@example.com',
                    'url_download': 'http://example.com/download'
                }
            }]
        }
        context = {}
        lambda_handler(event, context)
        mock_process_message.assert_called_once()
        mock_send_email_error.assert_not_called()

    @patch('src.sendemail.sendemail.process_message')
    @patch('src.sendemail.sendemail.send_email_error')
    def test_lambda_handler_email_error(self, mock_send_email_error, mock_process_message):
        mock_process_message.return_value = {'statusCode': 400}
        event = {
            'Records': [{
                'body': {
                    'status': 'erro',
                    'to_address': 'test@example.com',
                    'url_download': 'http://example.com/download'
                }
            }]
        }
        context = {}
        lambda_handler(event, context)
        mock_process_message.assert_called_once()
        mock_send_email_error.assert_called_once()

    @patch('src.sendemail.sendemail.send_email_success')
    def test_process_message_success(self, mock_send_email_success):
        message = {
            'body': {
                'status': 'sucesso',
                'to_address': 'test@example.com',
                'url_download': 'http://example.com/download'
            }
        }
        process_message(message)
        mock_send_email_success.assert_called_once_with('test@example.com', 'http://example.com/download')

    @patch('src.sendemail.sendemail.send_email_error')
    def test_process_message_error(self, mock_send_email_error):
        message = {
            'body': {
                'status': 'erro',
                'to_address': 'test@example.com',
                'url_download': 'http://example.com/download'
            }
        }
        process_message(message)
        mock_send_email_error.assert_called_once_with('test@example.com')

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_success_success(self, mock_post):
        mock_post.return_value.status_code = 202
        destinatario = "test@example.com"
        url_download = "http://example.com/download"
        send_email_success(destinatario, url_download)
        mock_post.assert_called_once()

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_success_error(self, mock_post):
        mock_post.return_value.status_code = 500
        destinatario = "test@example.com"
        url_download = "http://example.com/download"
        send_email_success(destinatario, url_download)
        mock_post.assert_called_once()

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_success_exception(self, mock_post):
        mock_post.side_effect = Exception("Error")
        destinatario = "test@example.com"
        url_download = "http://example.com/download"
        response = send_email_success(destinatario, url_download)
        self.assertIn('statusCode', response)
        self.assertNotEqual(response['statusCode'], 500)

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_error_success(self, mock_post):
        mock_post.return_value.status_code = 200
        destinatario = "test@example.com"
        send_email_error(destinatario)
        mock_post.assert_called_once()

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_error_error(self, mock_post):
        mock_post.return_value.status_code = 500
        destinatario = "test@example.com"
        send_email_error(destinatario)
        mock_post.assert_called_once()

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_error_exception(self, mock_post):
        mock_post.side_effect = Exception("Error")
        destinatario = "test@example.com"
        response = send_email_error(destinatario)
        self.assertIn('statusCode', response)
        self.assertNotEqual(response['statusCode'], 500)