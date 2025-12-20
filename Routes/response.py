import json
import os
from fastapi import APIRouter, HTTPException
from datetime import datetime

from MongoDB.schemas import ResponseCreate
from Services.responseService import save_response
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Import from config
from config import (
    SPREADSHEET_ID,
    RANGE_NAME,
    SCOPES,
    GOOGLE_SERVICE_ACCOUNT_JSON,
    SERVICE_ACCOUNT_FILE
)

form_response = APIRouter()


class GoogleSheetsService:
    def __init__(self):
        self.credentials = None
        self.service = None
        self.initialize_service()
    
    def initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            # Try environment variable first (for production)
            if GOOGLE_SERVICE_ACCOUNT_JSON:
                service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
                self.credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=SCOPES
                )
                print("Using service account from environment variable")
            # Fallback to file (for local development)
            elif os.path.exists(SERVICE_ACCOUNT_FILE):
                self.credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE,
                    scopes=SCOPES
                )
                print("Using service account from file")
            else:
                raise Exception("No Google credentials found. Set GOOGLE_SERVICE_ACCOUNT_JSON or provide service-account-key.json")
            
            self.service = build('sheets', 'v4', credentials=self.credentials)
            print("Google Sheets service initialized successfully")
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
            print(f"Google Sheets API error: {error}")
            raise
    
    def get_all_rows(self):
        """Get all rows from the sheet"""
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            print(f"Error fetching rows: {error}")
            raise


# Initialize the service once when the module loads
sheets_service = GoogleSheetsService()


@form_response.post("/submit_response")
def submit_response(response_data: ResponseCreate):
    """
    Submit form response - saves to both Google Sheets and MongoDB
    """
    try:
        print(f"Attempting to submit to form: {response_data.form_id}")
        
        # Prepare data for Google Sheets
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        answers_str = json.dumps(response_data.answers)
        
        row_data = [
            timestamp,
            response_data.form_id,
            answers_str
        ]

        # Save to Google Sheets
        sheets_service.append_row(row_data)
        print("Google Sheets updated successfully")
        
        # Save to MongoDB
        print("Saving to database...")
        result = save_response(
            response_data.form_id,
            response_data.dict()
        )
        print("Database updated successfully")
        
        return result
        
    except Exception as e:
        print(f"Error details: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting form: {str(e)}")



