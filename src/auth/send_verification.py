import os
import random
from flask import Flask, request, render_template, redirect, url_for, flash
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def generate_verification_code() -> int:
    return random.randint(100000, 999999)

def send_verification_email(to_email: str, code: int) -> bool:
    """Sends the verification email using SendGrid."""
    try:
        message = Mail(
            from_email=os.getenv("SENDER_EMAIL"),
            to_emails=to_email,
            subject="Your EduAlign Verification Code",
            html_content=f"<p>Your verification code is: <strong>{code}</strong></p>"
        )
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"SendGrid response status: {response.status_code}")
        print(f"SendGrid response body: {response.body}")
        print(f"SendGrid response headers: {response.headers}")
        return True
    except Exception as e:
        import traceback
        print(f"SendGrid error: {str(e)}")
        traceback.print_exc()
        if hasattr(e, 'body'):
            print(f"SendGrid error body: {e.body}")
        return False
