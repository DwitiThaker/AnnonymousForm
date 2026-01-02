
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from MongoDB.models import AccessCode, AccessCodeBatch
from MongoDB.schemas import BulkEmailRequest, EmailStatusResponse
from Services.emailServices import generate_access_code, send_bulk_emails_task
from Services.accessCodeService import save_access_code_batch
from configurations import form_collection
from bson import ObjectId


admin_email = APIRouter()


@admin_email.post("/admin/send_access_codes", response_model=EmailStatusResponse)
async def send_access_codes_to_users(
    request: BulkEmailRequest,
    background_tasks: BackgroundTasks
):
   
    try:
        print(f"Admin {request.generated_by} sending access codes to {len(request.emails)} users")
        
        # Validate inputs
        if not request.emails:
            raise HTTPException(
                status_code=400,
                detail="Email list cannot be empty"
            )
        
        if len(request.emails) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Cannot send to more than 1000 emails at once"
            )
        
        if not ObjectId.is_valid(request.form_id):
            raise HTTPException(status_code=400, detail="Invalid form_id")

        form = form_collection.find_one({"_id": ObjectId(request.form_id)})

        if not form:
            raise HTTPException(status_code=404, detail="Form not found")

        if form.get("status") != "published":
            raise HTTPException(
                status_code=400,
                detail="Form is not published"
            )
        
        # Remove duplicate emails
        unique_emails = list(set(request.emails))

        if len(unique_emails) < len(request.emails):
            print(f"Removed {len(request.emails) - len(unique_emails)} duplicate emails")
        
        # Generate unique access codes for each email
        access_codes = []
        email_code_pairs = []
        
        for email in unique_emails:
            code = generate_access_code()
            
            access_code = AccessCode(
                email=email,
                code=code,
                limit=request.code_limit,
                used_count=0,
                is_valid=True,
                generated_at=datetime.utcnow()
            )
            
            access_codes.append(access_code.dict())
            email_code_pairs.append({
                'email': email,
                'code': code
            })
        
        # Create batch record
        batch = AccessCodeBatch(
            emails=unique_emails,
            form_id=request.form_id,
            generated_by=request.generated_by,
            form_link=request.form_link,
            created_at=datetime.utcnow(),
            codes=access_codes
        )
        
        # Save to MongoDB first (before sending emails)
        batch_id = save_access_code_batch(batch.dict())
        print(f"Batch saved with ID: {batch_id}")
        
        # Send emails in background (non-blocking)
        background_tasks.add_task(
            send_bulk_emails_task,
            email_code_pairs,
            request.form_link
        )
        
        print(f"Background task scheduled for {len(unique_emails)} emails")
        
        return EmailStatusResponse(
            success=True,
            message=f"Access codes generated and emails are being sent to {len(unique_emails)} users",
            total_emails=len(unique_emails),
            success_count=len(unique_emails),  # Optimistic - actual results logged in background
            failed_count=0,
            batch_id=batch_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in send_access_codes endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error sending access codes: {str(e)}"
        )

