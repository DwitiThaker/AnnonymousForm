import os
from dotenv import load_dotenv
import json


# Load environment variables from .env file
load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", "dwiti.thaker04@gmail.com")
smtp_use_tls_str = os.getenv("SMTP_USE_TLS", "True").strip().lower()
SMTP_USE_TLS = smtp_use_tls_str in ["true", "1", "yes"]
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = os.getenv("RANGE_NAME", "Sheet1!A:Z")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

_raw_sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
if not _raw_sa_json:
    raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON is missing")

GOOGLE_SERVICE_ACCOUNT_JSON = json.loads(_raw_sa_json)
GOOGLE_SERVICE_ACCOUNT_JSON["private_key"] = (
    GOOGLE_SERVICE_ACCOUNT_JSON["private_key"].replace("\\n", "\n")
)