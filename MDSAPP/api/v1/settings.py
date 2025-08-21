# MDSAPP/api/v1/settings.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.core.models.prompts import Prompt
from MDSAPP.core.dependencies import get_database_manager

router = APIRouter()

@router.get("/settings/prompts", response_model=List[Prompt])
async def get_all_prompts(db_manager: DatabaseManager = Depends(get_database_manager)):
    """
    Get all prompts from the database.
    """
    try:
        prompts = await db_manager.load_all_prompts()
        return prompts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/settings/prompts", response_model=Prompt, status_code=status.HTTP_201_CREATED)
async def create_prompt(prompt: Prompt, db_manager: DatabaseManager = Depends(get_database_manager)):
    """
    Create a new prompt in the database.
    """
    try:
        await db_manager.save_prompt(prompt)
        return prompt
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/settings/prompts/{prompt_id}", response_model=Prompt)
async def update_prompt(prompt_id: str, prompt: Prompt, db_manager: DatabaseManager = Depends(get_database_manager)):
    """
    Update a prompt in the database.
    """
    try:
        existing_prompt = await db_manager.load_prompt(prompt_id)
        if not existing_prompt:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found.")
        
        prompt.id = prompt_id
        prompt.touch()
        await db_manager.save_prompt(prompt)
        return prompt
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/settings/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(prompt_id: str, db_manager: DatabaseManager = Depends(get_database_manager)):
    """
    Delete a prompt from the database.
    """
    try:
        await db_manager.delete_prompt(prompt_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Placeholder for settings endpoints
@router.get("/settings/config")
async def get_settings():
    return {"message": "Settings endpoint not implemented yet."}

@router.put("/settings/config")
async def update_settings():
    return {"message": "Settings endpoint not implemented yet."}
