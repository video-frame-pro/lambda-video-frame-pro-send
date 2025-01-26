import json
import os
import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch
from unittest import mock
import boto3

from botocore.exceptions import ClientError

os.environ['email_api_key'] = 'mocked_api_key'
os.environ['AWS_REGION'] = 'us-east-1'
session = boto3.Session(region_name='your-region-name')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.sendemail.sendemail import (lambda_handler, process_message,
                                     send_email_error, send_email_success, delete_message)

class TestLambdaFunction(TestCase):

    @patch('boto3.client')
    @patch('src.sendemail.sendemail.process_message')
    @patch('src.sendemail.sendemail.delete_message')
    def test_lambda_handler(self, delete_message, mock_process_message, mock_boto_client):
        mock_process_message.return_value = {'statusCode': 200}
        mock_boto_client.return_value = MagicMock()
        event = {
            'Records': [{
                'body': json.dumps({
                    'status': 'sucesso',
                    'to_address': 'test@example.com',
                    'url_download': 'http://example.com/download'
                }),
                'receiptHandle': 'mock_receipt_handle'
            }]
        }
        context = {}
        lambda_handler(event, context)
        mock_process_message.assert_called_once()
        delete_message.assert_called_once()

    @patch('src.sendemail.sendemail.send_email_success')
    def test_process_message_success(self, mock_send_email_success):
        body_message  = {
            'status': 'sucesso',
            'to_address': 'test@example.com',
            'url_download': 'http://example.com/download'
        }
        process_message(body_message )
        mock_send_email_success.assert_called_once_with('test@example.com', 'http://example.com/download')

    @patch('src.sendemail.sendemail.send_email_error')
    def test_process_message_error(self, mock_send_email_error):
        body_message = {
            'status': 'erro',
            'to_address': 'test@example.com',
            'url_download': 'http://example.com/download'
        }
        process_message(body_message)
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
        send_email_success(destinatario, url_download)

    @patch('src.sendemail.sendemail.requests.post')
    def test_send_email_error_success(self, mock_post):
        mock_post.return_value.status_code = 200
        destinatario = "test@example.com"
        send_email_error(destinatario)

    @patch.dict(os.environ, {"email_api_key": "mocked_api_key"})
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
        send_email_error(destinatario)

    @patch('src.sendemail.sendemail.sqs_client.delete_message')
    def test_delete_message_success(self, mock_delete_message):
        mock_delete_message.return_value = MagicMock()
        QueueUrl='MockedQueueUrl',
        receipt_handle = 'mock_receipt_handle'
        
        delete_message(receipt_handle)

    @patch('src.sendemail.sendemail.sqs_client.delete_message')
    def test_delete_message_exception(self, mock_delete_message):
        mock_delete_message.side_effect = Exception("Error")
        receipt_handle = 'mock_receipt_handle'
        
        delete_message(receipt_handle)