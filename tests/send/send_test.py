import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

os.environ['BREVO_TOKEN'] = 'mocked_api_key'

from src.send.send import lambda_handler, send_email_error, send_email_success


class TestLambdaFunction(TestCase):

    @patch('src.send.send.send_email_success')
    @patch('src.send.send.send_email_error')
    def test_lambda_handler_success(self, mock_send_email_error, mock_send_email_success):
        event = {
            "error": False,
            "processingLink": "http://example.com/download",
            "email": "test@example.com"
        }
        context = {}

        response = lambda_handler(event, context)

        mock_send_email_success.assert_called_once_with(
            "test@example.com", "http://example.com/download"
        )
        mock_send_email_error.assert_not_called()
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("SEND_SUCCESS", response['body'])

    @patch('src.send.send.send_email_success')
    @patch('src.send.send.send_email_error')
    def test_lambda_handler_error(self, mock_send_email_error, mock_send_email_success):
        event = {
            "error": True,
            "email": "test@example.com"
        }
        context = {}

        response = lambda_handler(event, context)

        mock_send_email_error.assert_called_once_with("test@example.com")
        mock_send_email_success.assert_not_called()
        self.assertEqual(response['statusCode'], 200)
        self.assertIn("SEND_ERROR", response['body'])

    def test_lambda_handler_missing_email(self):
        event = {
            "error": False,
            "processingLink": "http://example.com/download"
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("'email' cannot be null or empty.", response['body'])

    def test_lambda_handler_missing_processing_link(self):
        event = {
            "error": False,
            "email": "test@example.com"
        }
        context = {}

        response = lambda_handler(event, context)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("'processingLink' is required", response['body'])

    @patch('src.send.send.requests.post')
    def test_send_email_success_success(self, mock_post):
        mock_post.return_value.status_code = 202
        recipient = "test@example.com"
        processing_link = "http://example.com/download"
        send_email_success(recipient, processing_link)
        mock_post.assert_called_once()

    @patch('src.send.send.requests.post')
    def test_send_email_success_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        recipient = "test@example.com"
        processing_link = "http://example.com/download"
        send_email_success(recipient, processing_link)
        mock_post.assert_called_once()

    @patch('src.send.send.requests.post')
    def test_send_email_success_exception(self, mock_post):
        mock_post.side_effect = Exception("Error")
        recipient = "test@example.com"
        processing_link = "http://example.com/download"
        send_email_success(recipient, processing_link)

    @patch('src.send.send.requests.post')
    def test_send_email_error_success(self, mock_post):
        mock_post.return_value.status_code = 202
        recipient = "test@example.com"
        send_email_error(recipient)
        mock_post.assert_called_once()

    @patch('src.send.send.requests.post')
    def test_send_email_error_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        recipient = "test@example.com"
        send_email_error(recipient)
        mock_post.assert_called_once()

    @patch('src.send.send.requests.post')
    def test_send_email_error_exception(self, mock_post):
        mock_post.side_effect = Exception("Error")
        recipient = "test@example.com"
        send_email_error(recipient)
