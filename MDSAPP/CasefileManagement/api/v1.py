# MDSAPP/CasefileManagement/api/v1.py

from fastapi import APIRouter, Depends, Body, HTTPException, BackgroundTasks, Header
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from MDSAPP.CasefileManagement.models.casefile import Casefile
from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.dependencies import get_casefile_manager
from MDSAPP.core.models.stix_inspired_models import Campaign, Grouping
from MDSAPP.core.models.ontology import Role


def get_current_user_id(x_user_id: str = Header(..., alias="X-User-ID")) -> str:
    return x_user_id

router = APIRouter()

class CreateCasefileRequest(BaseModel):
    name: str
    description: str = ""
    casefile_id: Optional[str] = None
    parent_id: Optional[str] = None
    campaign: Optional[Campaign] = None
    dossier: Optional[Grouping] = None

class RunProcessorRequest(BaseModel):
    mission: str = Field(..., description="The mission for the processor agent.")

class RunExecutorRequest(BaseModel):
    workflow_dict: Dict[str, Any] = Field(..., description="The workflow dictionary to execute.")

class UpdateCasefileRequest(BaseModel):
    updates: Dict[str, Any]

class GrantAccessRequest(BaseModel):
    user_id_to_grant: str
    role: Role

class RevokeAccessRequest(BaseModel):
    user_id_to_revoke: str

@router.get("/casefiles/status", response_model=List[Dict[str, Any]])
async def get_all_casefiles_with_status(
    casefile_manager: CasefileManager = Depends(get_casefile_manager)
):
    """Retrieves a list of all casefiles, each with a calculated status."""
    return await casefile_manager.list_all_casefiles_with_status()

@router.post("/casefiles", response_model=str, status_code=201)
async def create_new_casefile(
    request: CreateCasefileRequest,
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    user_id: str = Depends(get_current_user_id)
):
    """
    Creates a new casefile. If a parent_id is provided, it will be nested
    under the parent.
    """
    try:
        new_casefile = await casefile_manager.create_casefile(
            name=request.name,
            description=request.description,
            user_id=user_id,
            casefile_id=request.casefile_id,
            parent_id=request.parent_id,
            campaign=request.campaign,
            dossier=request.dossier,
        )
        return new_casefile
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) # For parent not found
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/casefiles", response_model=List[str])
async def get_all_casefiles(
    casefile_manager: CasefileManager = Depends(get_casefile_manager)
):
    """
    Retrieves a list of all top-level casefiles (those without a parent).
    """
    try:
        all_casefiles_json = await casefile_manager.list_all_casefiles()
        all_casefiles = [Casefile.model_validate_json(json_str) for json_str in all_casefiles_json]
        top_level_casefiles = [casefile for casefile in all_casefiles if getattr(casefile, 'parent_id', None) is None]
        return [casefile.model_dump_json() for casefile in top_level_casefiles]
    except Exception as e:
        # Log the exception for debugging purposes
        # In a real application, you'd use a proper logger
        print(f"Error loading casefiles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not load casefiles. This might be due to a database connection issue. Please check the server logs and ensure that the application has the correct credentials to connect to Firestore."
        )

@router.get("/casefiles/{casefile_id}", response_model=str)
async def get_casefile_by_id(
    casefile_id: str,
    casefile_manager: CasefileManager = Depends(get_casefile_manager)
):
    """Retrieves a specific casefile by its ID."""
    casefile = await casefile_manager.load_casefile(casefile_id)
    if not casefile:
        raise HTTPException(status_code=404, detail="Casefile not found")
    return casefile

@router.delete("/casefiles/{casefile_id}", status_code=204)
async def delete_existing_casefile(
    casefile_id: str,
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    user_id: str = Depends(get_current_user_id)
):
    """Deletes a casefile by its ID."""
    try:
        success = await casefile_manager.delete_casefile(casefile_id=casefile_id, user_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Casefile not found for deletion")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return

@router.patch("/casefiles/{casefile_id}", response_model=str)
async def update_existing_casefile(
    casefile_id: str,
    request: UpdateCasefileRequest,
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    user_id: str = Depends(get_current_user_id)
):
    """Updates an existing casefile."""
    try:
        updated_casefile = await casefile_manager.update_casefile(
            casefile_id=casefile_id,
            user_id=user_id,
            updates=request.updates
        )
        return updated_casefile
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/casefiles/{casefile_id}/acl/grant", response_model=str)
async def grant_casefile_access(
    casefile_id: str,
    request: GrantAccessRequest,
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    current_user_id: str = Depends(get_current_user_id)
):
    """Grants access to a casefile."""
    try:
        updated_casefile = await casefile_manager.grant_access(
            casefile_id=casefile_id,
            user_id_to_grant=request.user_id_to_grant,
            role=request.role,
            current_user_id=current_user_id
        )
        return updated_casefile
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/casefiles/{casefile_id}/acl/revoke", response_model=str)
async def revoke_casefile_access(
    casefile_id: str,
    request: RevokeAccessRequest,
    casefile_manager: CasefileManager = Depends(get_casefile_manager),
    current_user_id: str = Depends(get_current_user_id)
):
    """Revokes access to a casefile."""
    try:
        updated_casefile = await casefile_manager.revoke_access(
            casefile_id=casefile_id,
            user_id_to_revoke=request.user_id_to_revoke,
            current_user_id=current_user_id
        )
        return updated_casefile
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
