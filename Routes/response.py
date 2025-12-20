import json
from fastapi import APIRouter, HTTPException
from MongoDB.schemas import ResponseCreate
from Services.responseService import save_response
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

form_response = APIRouter()



# Configuration
SPREADSHEET_ID = "1nObbLebQpAibmDcIi74y1MTza5sjse48CM0Nok3iR24"  # Get this from the URL of your Google Sheet
RANGE_NAME = "Sheet1!A:Z"  # Adjust based on your sheet name
SERVICE_ACCOUNT_FILE = "service-account-key.json"  # Path to your JSON key file

# Scopes required for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            self.credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, 
                scopes=SCOPES
            )
            self.service = build('sheets', 'v4', credentials=self.credentials)
        except Exception as e:
            print(f"Error initializing Google Sheets service: {e}")
            raise
    
    def append_row(self, values: list):
        """Append a row to the Google Sheet"""
        try:
            body = {
                'values': [values]
            }
            result = self.service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return result
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise
    
    def get_all_rows(self):
        """Get all rows from the sheet (optional, for reading data)"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise


# Initialize the service
sheets_service = GoogleSheetsService()


@form_response.post("/submit_response")
def submit_response(response_data: ResponseCreate):
    try:
        # ADD THIS DEBUG LINE
        print(f"Attempting to submit to form: {response_data.form_id}")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        answers_str = json.dumps(response_data.answers)
        
        row_data = [
            timestamp,
            response_data.form_id,
            answers_str
        ]

        sheets_service.append_row(row_data)
        
        # ADD THIS DEBUG LINE
        print("Google Sheets updated, now saving to DB...")
        
        return save_response(
            response_data.form_id,
            response_data.dict()
        )
    except Exception as e:
        print(f"Error details: {e}")  # This will show more info
        raise HTTPException(status_code=500, detail=f"Error submitting form: {str(e)}")