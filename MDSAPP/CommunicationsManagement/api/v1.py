# MDSAPP/CommunicationsManagement/api/v1.py

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Optional

# This will be updated to point to the new MDSAPP DI system
from MDSAPP.core.dependencies import get_communication_manager
from MDSAPP.CommunicationsManagement.manager import CommunicationManager

router = APIRouter()

class ChatRequest(BaseModel):
    user_input: str
    casefile_id: str # Made mandatory for clarity

@router.post("/chat", summary="Process a user message.")
async def process_chat_message(
    request: ChatRequest,
    user_id: str = Header(..., alias="X-User-ID"),
    comm_manager: CommunicationManager = Depends(get_communication_manager)
):
    """
    This endpoint is the single point of entry for all user chat interactions.
    It requires a valid casefile_id to maintain context.
    """
    try:
        response = await comm_manager.handle_user_request(
            user_input=request.user_input,
            casefile_id=request.casefile_id,
            user_id=user_id
        )
        return response
    except ValueError as e:
        # This will catch the error if the casefile_id is not found
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/test")
async def test_chat_route():
    return {"message": "Chat router test endpoint is working!"}
