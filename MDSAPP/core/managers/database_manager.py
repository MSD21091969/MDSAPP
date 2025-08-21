# MDSAPP/core/managers/database_manager.py

import logging
import asyncio
import os
import datetime
from typing import List, Any

import firebase_admin
from firebase_admin import credentials, firestore
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from sentence_transformers import SentenceTransformer

# Import Casefile from the new MDSAPP location
from MDSAPP.CasefileManagement.models.casefile import Casefile
from MDSAPP.core.models.prompts import Prompt
from MDSAPP.core.models.conversation_session import ConversationSession, Message

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages the connection to the Firestore database, including all
    CRUD (Create, Read, Update, Delete) operations for casefiles and prompts.
    """
    def __init__(self):
        print("DatabaseManager __init__ called")
        self._db = None
        self.embedding_model = None
        self.casefiles_collection_name = "casefiles"
        self.documents_collection_name = "document_chunks"
        self.prompts_collection_name = "prompts"
        self._initialize_embedding_model()

        # Add a file handler for debug logs specifically for this logger
        debug_file_handler = logging.FileHandler('debug_conversion.log')
        debug_file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        debug_file_handler.setFormatter(formatter)
        logger.addHandler(debug_file_handler)

    def _connect(self):
        try:
            if not firebase_admin._apps:
                project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
                if not project_id:
                    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set.")
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': project_id,
                })
            self._db = firestore.client()
            logger.info("Successfully connected to Firestore.")
        except Exception as e:
            logger.error(f"Error connecting to Firestore: {e}", exc_info=True)
            raise

    def _initialize_embedding_model(self):
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer embedding model initialized.")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}", exc_info=True)
            self.embedding_model = None

    @property
    def db(self):
        if not self._db:
            self._connect()
        return self._db

    def _convert_datetimes_to_iso(self, data: Any) -> Any:
        """
        Recursively converts datetime objects within a dictionary or list to ISO 8601 strings.
        """
        logger.debug(f"_convert_datetimes_to_iso received type: {type(data)}")
        if isinstance(data, dict):
            logger.debug("  - Is dict")
            return {k: self._convert_datetimes_to_iso(v) for k, v in data.items()}
        elif isinstance(data, list):
            logger.debug("  - Is list")
            return [self._convert_datetimes_to_iso(v) for v in data]
        elif isinstance(data, (datetime.datetime, DatetimeWithNanoseconds)):
            logger.debug(f"  - Is datetime or DatetimeWithNanoseconds: {data}")
            return data.isoformat()
        else:
            logger.debug("  - Is other type")
            return data

    async def save_casefile(self, casefile: Casefile):
        doc_ref = self.db.collection(self.casefiles_collection_name).document(casefile.id)
        await asyncio.to_thread(doc_ref.set, casefile.model_dump(exclude_none=True))
        logger.info(f"Casefile '{casefile.id}' saved to Firestore.")

    async def load_casefile(self, casefile_id: str) -> Casefile | None:
        doc_ref = self.db.collection(self.casefiles_collection_name).document(casefile_id)
        doc = await asyncio.to_thread(doc_ref.get)
        if doc.exists:
            casefile_data = doc.to_dict()
            casefile_data = self._convert_datetimes_to_iso(casefile_data) # Convert datetimes to ISO strings
            casefile_data['id'] = doc.id  # Ensure the ID is the document ID
            return Casefile(**casefile_data)
        return None

    def save_document_chunk(self, chunk_data: dict):
        chunk_id = f"{chunk_data['case_id']}-{chunk_data['file_id']}-{chunk_data['chunk_index']}"
        doc_ref = self.db.collection(self.documents_collection_name).document(chunk_id)
        doc_ref.set(chunk_data)
        logger.info(f"Document chunk '{chunk_id}' opgeslagen in Firestore.")

    async def load_all_casefiles(self) -> List[Casefile]:
        """Retrieves all casefile documents from the collection."""
        logger.info(f"Alle casefiles worden opgehaald uit de '{self.casefiles_collection_name}' collectie.")
        
        def _load_all():
            docs = self.db.collection(self.casefiles_collection_name).stream()
            casefiles = []
            for doc in docs:
                casefile_data = doc.to_dict()
                casefile_data = self._convert_datetimes_to_iso(casefile_data) # Convert datetimes to ISO strings
                casefile_data['id'] = doc.id # Ensure the ID is the document ID
                casefiles.append(Casefile(**casefile_data))
            return casefiles

        casefiles = await asyncio.to_thread(_load_all)
        logger.info(f"{len(casefiles)} casefiles gevonden en geladen.")
        return casefiles

    async def delete_casefile(self, casefile_id: str) -> bool:
        """Deletes a specific casefile document from Firestore."""
        doc_ref = self.db.collection(self.casefiles_collection_name).document(casefile_id)
        
        doc = await asyncio.to_thread(doc_ref.get)
        if doc.exists:
            await asyncio.to_thread(doc_ref.delete)
            logger.info(f"Casefile '{casefile_id}' successfully deleted from Firestore.")
            return True
        else:
            logger.warning(f"Attempted to delete, but casefile '{casefile_id}' not found.")
            return False

    async def save_prompt(self, prompt: Prompt):
        doc_ref = self.db.collection(self.prompts_collection_name).document(prompt.id)
        await asyncio.to_thread(doc_ref.set, prompt.model_dump(exclude_none=True))
        logger.info(f"Prompt '{prompt.id}' saved to Firestore.")

    async def load_prompt(self, prompt_id: str) -> Prompt | None:
        doc_ref = self.db.collection(self.prompts_collection_name).document(prompt_id)
        doc = await asyncio.to_thread(doc_ref.get)
        if doc.exists:
            prompt_data = doc.to_dict()
            prompt_data['id'] = doc.id
            return Prompt(**prompt_data)
        return None

    async def load_all_prompts(self) -> List[Prompt]:
        """Retrieves all prompt documents from the collection."""
        logger.info(f"Alle prompts worden opgehaald uit de '{self.prompts_collection_name}' collectie.")
        
        def _load_all():
            docs = self.db.collection(self.prompts_collection_name).stream()
            prompts = []
            for doc in docs:
                prompt_data = doc.to_dict()
                prompt_data['id'] = doc.id
                prompts.append(Prompt(**prompt_data))
            return prompts

        prompts = await asyncio.to_thread(_load_all)
        logger.info(f"{len(prompts)} prompts gevonden en geladen.")
        return prompts

    async def delete_prompt(self, prompt_id: str) -> bool:
        """Deletes a specific prompt document from Firestore."""
        doc_ref = self.db.collection(self.prompts_collection_name).document(prompt_id)
        
        doc = await asyncio.to_thread(doc_ref.get)
        if doc.exists:
            await asyncio.to_thread(doc_ref.delete)
            logger.info(f"Prompt '{prompt_id}' successfully deleted from Firestore.")
            return True
        else:
            logger.warning(f"Attempted to delete, but prompt '{prompt_id}' not found.")
            return False

    async def save_conversation_session(self, session: ConversationSession):
        """Saves a conversation session to Firestore."""
        doc_ref = self.db.collection("conversation_sessions").document(session.id)
        await asyncio.to_thread(doc_ref.set, session.model_dump(exclude_none=True))
        logger.info(f"Conversation session '{session.id}' saved to Firestore.")

    async def load_conversation_session(self, session_id: str) -> ConversationSession | None:
        """Loads a conversation session from Firestore."""
        doc_ref = self.db.collection("conversation_sessions").document(session_id)
        doc = await asyncio.to_thread(doc_ref.get)
        if doc.exists:
            session_data = doc.to_dict()
            session_data['id'] = doc.id
            return ConversationSession(**session_data)
        return None
