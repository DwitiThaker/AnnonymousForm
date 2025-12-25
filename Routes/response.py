import json
import os
from fastapi import APIRouter, HTTPException
from datetime import datetime

from MongoDB.schemas import ResponseCreate
from Services.responseService import save_response, get_responses_by_form_id

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SPREADSHEET_ID, RANGE_NAME, SCOPES, GOOGLE_SERVICE_ACCOUNT_JSON

form_response = APIRouter()


class GoogleSheetsService:
    def __init__(self):
        self.credentials = Credentials.from_service_account_info(
            GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
        )
        self.service = build("sheets", "v4", credentials=self.credentials)

    def append_multiple_rows(self, rows: list[list[str]]):
        try:
            body = {"values": rows}
            return (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=SPREADSHEET_ID,
                    range=RANGE_NAME,
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
        except HttpError as e:
            raise RuntimeError(f"Google Sheets API error: {e}")


sheets_service = GoogleSheetsService()


@form_response.post("/submit_response")
def submit_response(response_data: ResponseCreate):
    try:
        result = save_response(response_data.form_id, response_data.dict())
        return {
            "success": True,
            "message": "Form response submitted successfully",
            "data": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error submitting form response: {str(e)}"
        )


@form_response.get("/admin/export_to_sheets/{form_id}")
def export_form_to_sheets(form_id: str):
    try:
        responses = get_responses_by_form_id(form_id)

        if not responses:
            return {
                "success": True,
                "message": "No responses found for this form",
                "exported_count": 0,
            }

        rows = []
        for response in responses:
            timestamp = response.get("created_at", datetime.utcnow()).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            answers_str = json.dumps(response.get("answers", {}))

            rows.append([timestamp, form_id, answers_str, str(response.get("_id", ""))])

        sheets_service.append_multiple_rows(rows)

        return {
            "success": True,
            "message": f"Successfully exported {len(rows)} responses to Google Sheets",
            "exported_count": len(rows),
            "form_id": form_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error exporting to Google Sheets: {str(e)}"
        )
