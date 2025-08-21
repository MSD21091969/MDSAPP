# MDSAPP/CasefileManagement/manager.py

import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
import asyncio
from firebase_admin import firestore

from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.CasefileManagement.models.casefile import Casefile, Event
from MDSAPP.core.models.ontology import Role
from MDSAPP.core.models.stix_inspired_models import Campaign, Grouping
from MDSAPP.core.managers.tool_registry import ToolRegistry
from google.generativeai.types import FunctionDeclaration

logger = logging.getLogger(__name__)

class CasefileManager:
    """
    Manages the business logic for the lifecycle of hierarchical casefiles.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        logger.info("CasefileManager initialized.")

    async def create_casefile(
        self,
        name: str,
        description: str,
        user_id: str,
        casefile_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        campaign: Optional[Campaign] = None,
        dossier: Optional[Grouping] = None
    ) -> str:
        """
        Creates a casefile. If a parent_id is provided, it will be created
        as a sub-casefile of the specified parent.
        """
        if parent_id:
            # Use a Firestore transaction to ensure atomicity
            transaction = self.db_manager.db.transaction()

            @firestore.transactional
            def _create_sub_casefile_in_transaction(transaction):
                parent_ref = self.db_manager.db.collection(self.db_manager.casefiles_collection_name).document(parent_id)
                parent_doc = parent_ref.get(transaction=transaction)

                if not parent_doc.exists:
                    raise ValueError(f"Parent casefile with ID '{parent_id}' not found.")

                parent_casefile = Casefile(**parent_doc.to_dict())

                # Permission Check: User must have write access to the parent
                if not (parent_casefile.acl.get(user_id) in [Role.ADMIN, Role.WRITER]):
                     raise PermissionError(f"User '{user_id}' does not have permission to create a sub-casefile under '{parent_id}'.")

                # Inherit from parent, but allow overrides
                sub_campaign = campaign if campaign is not None else parent_casefile.campaign
                sub_dossier = dossier if dossier is not None else parent_casefile.dossier
                
                # Inherit ACL and add creator as admin
                sub_acl = parent_casefile.acl.copy()
                sub_acl[user_id] = Role.ADMIN

                sub_casefile = Casefile(
                    name=name,
                    description=description,
                    owner_id=user_id,
                    acl=sub_acl,
                    campaign=sub_campaign,
                    dossier=sub_dossier,
                    created_at=datetime.utcnow().isoformat() + 'Z',
                    modified_at=datetime.utcnow().isoformat() + 'Z'
                )

                # Add sub-casefile ID to parent
                parent_casefile.sub_casefile_ids.append(sub_casefile.id)
                parent_casefile.touch()

                # Stage the writes in the transaction
                sub_ref = self.db_manager.db.collection(self.db_manager.casefiles_collection_name).document(sub_casefile.id)
                transaction.set(sub_ref, sub_casefile.model_dump(exclude_none=True))
                transaction.set(parent_ref, parent_casefile.model_dump(exclude_none=True))

                return sub_casefile

            # Run the transactional function in a separate thread
            sub_casefile = await asyncio.to_thread(_create_sub_casefile_in_transaction, transaction)
            logger.info(f"Sub-casefile '{sub_casefile.id}' created and saved under parent '{parent_id}' in a transaction.")
            return sub_casefile.id
        else:
            if casefile_id is None:
                casefile_id = f"case-{uuid4().hex[:10]}"

            if campaign is None:
                campaign = Campaign(name=f"Campaign for {name}")
            if dossier is None:
                dossier = Grouping(name=f"Dossier for {name}", context="casefile-dossier")

            casefile = Casefile(
                id=casefile_id,
                name=name,
                description=description,
                owner_id=user_id,
                acl={user_id: Role.ADMIN},
                campaign=campaign,
                dossier=dossier,
                created_at=datetime.utcnow().isoformat() + 'Z',
                modified_at=datetime.utcnow().isoformat() + 'Z'
            )
            await self.db_manager.save_casefile(casefile)
            logger.info(f"Top-level casefile '{casefile.id}' created by user '{user_id}'.")
            return casefile.id

    async def list_all_casefiles(self) -> List[str]:
        """Lists all casefiles from the database as JSON strings."""
        casefiles = await self.db_manager.load_all_casefiles()
        return [casefile.model_dump_json() for casefile in casefiles]

    async def delete_casefile(self, casefile_id: str, user_id: str) -> bool:
        """Deletes a casefile from the database."""
        casefile_json = await self.load_casefile(casefile_id)
        if not casefile_json:
            raise ValueError(f"Casefile with ID '{casefile_id}' not found.")
        casefile = Casefile.model_validate_json(casefile_json)

        # Permission Check
        if casefile.acl.get(user_id) != Role.ADMIN:
            raise PermissionError(f"User '{user_id}' does not have admin rights to delete casefile '{casefile_id}'.")

        logger.info(f"Casefile '{casefile_id}' deleted by user '{user_id}'.")
        return await self.db_manager.delete_casefile(casefile_id)

    async def load_casefile(self, casefile_id: str) -> str:
        """Loads a casefile object from the database and returns it as a JSON string."""
        casefile = await self.db_manager.load_casefile(casefile_id)
        if casefile:
            return casefile.model_dump_json()
        return ""

    async def log_event(
        self,
        casefile_id: str,
        user_id: str,
        source: str,
        event_type: str,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """Logs a structured event to a casefile's event log."""
        casefile_json = await self.load_casefile(casefile_id)
        if not casefile_json:
            logger.error(f"Cannot log event: Casefile with ID '{casefile_id}' not found.")
            return
        casefile = Casefile.model_validate_json(casefile_json)

        # Permission Check: Any user with a role can log an event.
        if not casefile.acl.get(user_id):
            raise PermissionError(f"User '{user_id}' does not have permission to log events for casefile '{casefile_id}'.")

        event = Event(
            source=source,
            event_type=event_type,
            content=content,
            metadata=metadata or {}
        )
        
        casefile.event_log.append(event)
        await self.db_manager.save_casefile(casefile)
        logger.info(f"Logged event for casefile '{casefile_id}' by user '{user_id}': {source} - {event_type}")

    async def grant_access(self, casefile_id: str, user_id_to_grant: str, role: str, current_user_id: str) -> str:
        """
        Grants a role to a user for a specific casefile.
        Only an admin of the casefile can grant access.
        """
        casefile_json = await self.load_casefile(casefile_id)
        if not casefile_json:
            raise ValueError(f"Casefile with ID '{casefile_id}' not found.")
        casefile = Casefile.model_validate_json(casefile_json)

        # Permission Check
        if casefile.acl.get(current_user_id) != Role.ADMIN:
            raise PermissionError(f"User '{current_user_id}' does not have admin rights for casefile '{casefile_id}'.")

        try:
            role_enum = Role(role)
        except ValueError:
            raise ValueError(f"Invalid role '{role}'. Must be one of {[r.value for r in Role]}.")

        casefile.acl[user_id_to_grant] = role_enum
        casefile.touch()
        await self.db_manager.save_casefile(casefile)
        logger.info(f"User '{user_id_to_grant}' granted '{role_enum.value}' role for casefile '{casefile_id}' by user '{current_user_id}'.")
        return casefile.model_dump_json()

    async def revoke_access(self, casefile_id: str, user_id_to_revoke: str, current_user_id: str) -> str:
        """
        Revokes a user's access to a specific casefile.
        Only an admin of the casefile can revoke access.
        The owner's access cannot be revoked.
        """
        casefile_json = await self.load_casefile(casefile_id)
        if not casefile_json:
            raise ValueError(f"Casefile with ID '{casefile_id}' not found.")
        casefile = Casefile.model_validate_json(casefile_json)

        # Permission Check
        if casefile.acl.get(current_user_id) != Role.ADMIN:
            raise PermissionError(f"User '{current_user_id}' does not have admin rights for casefile '{casefile_id}'.")

        if user_id_to_revoke == casefile.owner_id:
            raise ValueError("Cannot revoke access for the owner of the casefile.")

        if user_id_to_revoke not in casefile.acl:
            logger.warning(f"User '{user_id_to_revoke}' already has no access to casefile '{casefile_id}'.")
            return casefile.model_dump_json()

        del casefile.acl[user_id_to_revoke]
        casefile.touch()
        await self.db_manager.save_casefile(casefile)
        logger.info(f"Access for user '{user_id_to_revoke}' revoked from casefile '{casefile_id}' by user '{current_user_id}'.")
        return casefile.model_dump_json()

    def register_tools(self, tool_registry: ToolRegistry):
        """
        Registers the casefile-related functions as tools for the agent.
        """
        create_casefile_tool = FunctionDeclaration(
            name="create_casefile",
            description="Creates a new casefile with a name and a description. Can optionally be a sub-casefile of a parent. The full Mission object can be set via update_casefile.",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The name of the new casefile."},
                    "description": {"type": "string", "description": "A short description of the casefile."},
                    "user_id": {"type": "string", "description": "The ID of the user creating the casefile."},
                    "parent_id": {"type": "string", "description": "The ID of the parent casefile, if creating a sub-casefile."},
                },
                "required": ["name", "description", "user_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="create_casefile",
            tool_declaration=create_casefile_tool,
            tool_handler=self.create_casefile
        )

        get_casefile_tool = FunctionDeclaration(
            name="get_casefile",
            description="Retrieves an existing casefile by its ID.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string", "description": "The unique ID of the casefile to retrieve."},
                },
                "required": ["casefile_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="get_casefile",
            tool_declaration=get_casefile_tool,
            tool_handler=self.load_casefile
        )

        list_casefiles_tool = FunctionDeclaration(
            name="list_all_casefiles",
            description="Lists all available casefiles.",
            parameters={"type": "object", "properties": {}},
        )
        tool_registry.register_tool(
            tool_name="list_all_casefiles",
            tool_declaration=list_casefiles_tool,
            tool_handler=self.list_all_casefiles
        )

        delete_casefile_tool = FunctionDeclaration(
            name="delete_casefile",
            description="Deletes a casefile by its ID.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string", "description": "The unique ID of the casefile to delete."},
                    "user_id": {"type": "string", "description": "The ID of the user deleting the casefile."},
                },
                "required": ["casefile_id", "user_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="delete_casefile",
            tool_declaration=delete_casefile_tool,
            tool_handler=self.delete_casefile
        )

        grant_access_tool = FunctionDeclaration(
            name="grant_access",
            description="Grants a role to a user for a specific casefile.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string", "description": "The ID of the casefile."},
                    "user_id_to_grant": {"type": "string", "description": "The ID of the user to grant access to."},
                    "role": {"type": "string", "description": "The role to grant (admin, writer, or reader)."},
                    "current_user_id": {"type": "string", "description": "The ID of the user performing the grant operation."},
                },
                "required": ["casefile_id", "user_id_to_grant", "role", "current_user_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="grant_access",
            tool_declaration=grant_access_tool,
            tool_handler=self.grant_access
        )

        revoke_access_tool = FunctionDeclaration(
            name="revoke_access",
            description="Revokes a user's access to a specific casefile.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string", "description": "The ID of the casefile."},
                    "user_id_to_revoke": {"type": "string", "description": "The ID of the user whose access is to be revoked."},
                    "current_user_id": {"type": "string", "description": "The ID of the user performing the revoke operation."},
                },
                "required": ["casefile_id", "user_id_to_revoke", "current_user_id"],
            },
        )
        tool_registry.register_tool(
            tool_name="revoke_access",
            tool_declaration=revoke_access_tool,
            tool_handler=self.revoke_access
        )

        update_casefile_tool = FunctionDeclaration(
            name="update_casefile",
            description="Updates an existing casefile with new data.",
            parameters={
                "type": "object",
                "properties": {
                    "casefile_id": {"type": "string", "description": "The unique ID of the casefile to update."},
                    "user_id": {"type": "string", "description": "The ID of the user updating the casefile."},
                    "updates": {"type": "object", "description": "A dictionary of fields to update."},
                },
                "required": ["casefile_id", "user_id", "updates"],
            },
        )
        tool_registry.register_tool(
            tool_name="update_casefile",
            tool_declaration=update_casefile_tool,
            tool_handler=self.update_casefile
        )

        logger.info("CasefileManager tools registered.")

    async def list_all_casefiles_with_status(self) -> List[Dict[str, Any]]:
        """ 
        Retrieves all casefiles and calculates their status based on their content.
        """
        all_casefiles_json = await self.list_all_casefiles()
        status_list = []

        for casefile_json in all_casefiles_json:
            casefile = Casefile.model_validate_json(casefile_json)
            status = "NEW"
            if casefile.engineered_workflows:
                status = "ANALYSIS_COMPLETE"
            elif casefile.execution_results:
                status = "EXECUTION_COMPLETE"
            elif casefile.workflows:
                status = "PLANNING_COMPLETE"
            elif casefile.description:
                status = "MISSION_DEFINED"
            
            casefile_dict = casefile.model_dump()
            casefile_dict["status"] = status
            status_list.append(casefile_dict)
        
        return status_list

    async def update_casefile(self, casefile_id: str, user_id: str, updates: Dict[str, Any]) -> str:
        """
        Updates an existing casefile with the provided data.
        Handles appending to lists and updating other fields.
        """
        casefile_json = await self.load_casefile(casefile_id)
        if not casefile_json:
            raise ValueError(f"Casefile with ID '{casefile_id}' not found.")
        casefile = Casefile.model_validate_json(casefile_json)

        # Permission Check
        if not (casefile.acl.get(user_id) in [Role.ADMIN, Role.WRITER]):
            raise PermissionError(f"User '{user_id}' does not have write permission for casefile '{casefile_id}'.")

        for key, value in updates.items():
            if hasattr(casefile, key):
                current_value = getattr(casefile, key)
                if isinstance(current_value, list) and isinstance(value, list):
                    # Extend existing list with new items
                    current_value.extend(value)
                elif isinstance(current_value, list) and not isinstance(value, list):
                    # If current is list but new value is not, append the single item
                    current_value.append(value)
                else:
                    # Directly update other attributes
                    setattr(casefile, key, value)
            else:
                logger.warning(f"Attempted to update non-existent attribute '{key}' on Casefile '{casefile_id}'.")

        casefile.touch() # Update modified_at timestamp
        await self.db_manager.save_casefile(casefile)
        logger.info(f"Casefile '{casefile_id}' updated successfully by user '{user_id}'.")
        return casefile.model_dump_json()