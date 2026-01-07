import json
import os
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from datetime import datetime
import traceback

from MongoDB.schemas import ResponseCreate
from configurations import form_collection
from Services.responseService import save_response, get_responses_by_form_id

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import SPREADSHEET_ID, RANGE_NAME, SCOPES, GOOGLE_SERVICE_ACCOUNT_JSON

form_response = APIRouter()


class GoogleSheetsService:
    def __init__(self):
        self.credentials = Credentials.from_service_account_info(
            GOOGLE_SERVICE_ACCOUNT_JSON,
            scopes=SCOPES
        )
        self.service = build("sheets", "v4", credentials=self.credentials)
        self.spreadsheet_id = SPREADSHEET_ID


    def append_multiple_rows(self, rows: list[list[str]]):
        try:
            body = {"values": rows}
            return (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.spreadsheet_id,
                    range=RANGE_NAME,
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
        except HttpError as e:
            raise RuntimeError(f"Google Sheets API error: {e}")


    def get_all_sheet_names(self) -> list[str]:
        spreadsheet = (
            self.service.spreadsheets()
            .get(spreadsheetId=self.spreadsheet_id)
            .execute()
        )
        return [
            sheet["properties"]["title"]
            for sheet in spreadsheet.get("sheets", [])
        ]

    def ensure_sheet_exists(self, sheet_name: str):
        existing_sheets = self.get_all_sheet_names()

        if sheet_name not in existing_sheets:
            body = {
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": sheet_name
                            }
                        }
                    }
                ]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()

    def clear_sheet(self, sheet_name: str):
        range_all = f"'{sheet_name}'!A:Z"
        self.service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id,
            range=range_all,
            body={}
        ).execute()

    def write_fresh_sheet(self, sheet_name: str, headers: list, rows: list):
        """
        Clears the sheet and writes headers + rows fresh.
        Used by form export to prevent duplicate data.
        """
        # 1. Ensure sheet exists
        self.ensure_sheet_exists(sheet_name)

        # 2. Clear old data
        self.clear_sheet(sheet_name)

        # 3. Write headers + rows
        all_rows = [headers] + rows

        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"'{sheet_name}'",
            valueInputOption="RAW",
            insertDataOption="OVERWRITE",
            body={"values": all_rows}
        ).execute()


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

        form = form_collection.find_one({"_id": ObjectId(form_id)})
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        questions = form.get("questions", [])
        headers = ["Timestamp"] + [q["question_text"] for q in questions]

        rows = []
        for response in responses:
            timestamp = response.get("created_at", datetime.utcnow()).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            answers = response.get("answers", {})
            row = [timestamp]

            for q in questions:
                row.append(answers.get(q["qid"], ""))

            rows.append(row)

        sheet_name = f"Form_{form_id}"

        sheets_service.write_fresh_sheet(sheet_name, headers, rows)

        return {
            "success": True,
            "message": f"Fresh export completed for {len(rows)} responses",
            "exported_count": len(rows),
            "form_id": form_id,
            "sheet_name": sheet_name
        }

    except Exception as e:
        print("========== EXPORT ERROR ==========")
        traceback.print_exc()
        print("==================================")

        raise HTTPException(
            status_code=500,
            detail=f"Error exporting to Google Sheets: {str(e)}"
        )

