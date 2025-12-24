
import smtplib
import secrets
import string
from email.message import EmailMessage
from typing import List, Optional

from config import (
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_FROM,
    SMTP_USE_TLS 
)


def generate_access_code(length: int = 8) -> str:
    """Generate a random access code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def send_access_code_email(
    access_code: str,
    recipient_email: str,
    form_link: Optional[str] = None
) -> bool:
    """
    Send access code to a single recipient
    Returns True if successful, False otherwise
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = "Your Access Code for Form Submission"
        msg["From"] = SMTP_FROM
        msg["To"] = recipient_email
        
        # Email body with optional form link
        email_body = f"""Hello,

Your access code is: {access_code}

This code will allow you to submit the form.
"""
        
        if form_link:
            email_body += f"""
Form Link: {form_link}

Please use the access code above when submitting the form.
"""
        
        email_body += """
Keep this code safe and do not share it with others.

Best regards,
Form Management Team
"""
        
        msg.set_content(email_body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            if SMTP_USE_TLS :
                smtp.starttls()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")
        return False


def send_bulk_emails_task(
    email_code_pairs: List[dict],
    form_link: Optional[str] = None
):
    success_count = 0
    failed_emails = []
    
    print(f"Starting bulk email send to {len(email_code_pairs)} recipients...")
    
    for pair in email_code_pairs:
        try:
            success = send_access_code_email(
                access_code=pair['code'],
                recipient_email=pair['email'],
                form_link=form_link
            )
            
            if success:
                success_count += 1
                print(f"✓ Email sent to {pair['email']}")
            else:
                failed_emails.append({
                    'email': pair['email'],
                    'code': pair['code'],
                    'error': 'Failed to send'
                })
                print(f"✗ Failed to send email to {pair['email']}")
                
        except Exception as e:
            failed_emails.append({
                'email': pair['email'],
                'code': pair['code'],
                'error': str(e)
            })
            print(f"✗ Error sending to {pair['email']}: {e}")
    
    print(f"Bulk email complete: {success_count} success, {len(failed_emails)} failed")
    
    return {
        'success_count': success_count,
        'failed_count': len(failed_emails),
        'failed_emails': failed_emails
    }
