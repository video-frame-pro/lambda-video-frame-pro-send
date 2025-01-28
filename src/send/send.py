import sys
sys.path.append('/opt/bin/')

import json
import requests
import logging
import os

EMAIL_SENDER = "videoframeprofiap@gmail.com"
BREVO_URL = "https://api.brevo.com/v3/smtp/email"
BREVO_TOKEN = os.environ["BREVO_TOKEN"]

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Extract and validate input data
        error_flag = event.get("error", False)  # Default is False
        processing_link = event.get("processingLink")
        email = event.get("email")

        # Validate 'email'
        if not email or not email.strip():
            logger.error("Validation error: 'email' cannot be null or empty.")
            raise ValueError("'email' cannot be null or empty.")

        # Validate 'processingLink' for success scenario
        if not error_flag and not processing_link:
            logger.error("Validation error: 'processingLink' is required when 'error' is False.")
            raise ValueError("'processingLink' is required for successful email.")

        # Decide whether to send success or error email
        if error_flag:
            logger.info("Error flag is set to True. Sending error email.")
            send_email_error(email)
            response = {
                "status": "SEND_ERROR",
                "email": email
            }
        else:
            logger.info("Error flag is False. Sending success email.")
            send_email_success(email, processing_link)
            response = {
                "status": "SEND_SUCCESS",
                "email": email,
                "processingLink": processing_link
            }

        logger.info(f"Lambda response: {json.dumps(response)}")
        return {
            "statusCode": 200,
            "body": json.dumps(response)
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error."})
        }


def send_email_success(recipient, download_url):
    headers = {
        "api-key": BREVO_TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "sender": {"email": EMAIL_SENDER},
        "to": [{"email": recipient}],
        "subject": "Video Frame Pro - Download Link",
        "htmlContent": f"""
            <html>
                <body>
                    <h1>Your video processing is complete!</h1>
                    <p>Click the link below to download the processed video:</p>
                    <a href="{download_url}">{download_url}</a>
                </body>
            </html>
        """
    }

    try:
        response = requests.post(BREVO_URL, headers=headers, json=data)
        if response.status_code in [202, 201]:
            logger.info(f"Success email sent to {recipient}.")
        else:
            logger.error(f"Failed to send success email. HTTP Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error while sending success email: {str(e)}")


def send_email_error(recipient):
    headers = {
        "api-key": BREVO_TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "sender": {"email": EMAIL_SENDER},
        "to": [{"email": recipient}],
        "subject": "Video Frame Pro - Processing Error",
        "htmlContent": """
            <html>
                <body>
                    <h1>An error occurred while processing your video.</h1>
                    <p>We were unable to complete the processing of your video. Please try again later or contact support if the issue persists.</p>
                </body>
            </html>
        """
    }

    try:
        response = requests.post(BREVO_URL, headers=headers, json=data)
        if response.status_code in [202, 201]:
            logger.info(f"Error email sent to {recipient}.")
        else:
            logger.error(f"Failed to send error email. HTTP Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error while sending error email: {str(e)}")