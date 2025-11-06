import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_access_code(access_code, recipient_email):
    SMTP_SERVER   = os.getenv("SMTP_SERVER")
    SMTP_PORT     = int(os.getenv("SMTP_PORT"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    SMTP_FROM     = os.getenv("SMTP_FROM", SMTP_USERNAME)
    SMTP_USE_TLS  = os.getenv("SMTP_USE_TLS", "True").lower() == "true"

    msg = EmailMessage()
    msg["Subject"] = "Your Access Code"
    msg["From"] = SMTP_FROM
    msg["To"] = recipient_email
    msg.set_content(f"Hello,\n\nYour access code is: {access_code}\n\nKeep it safe!")

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        if SMTP_USE_TLS:
            smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(msg)

    print(f"Access code sent to {recipient_email}")

# Example usage
if __name__ == "__main__":
    access_code = "8J5LGL "  
    send_access_code(access_code, "dwitithaker5@gmail.com")
    



        