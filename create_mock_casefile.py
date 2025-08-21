import asyncio
import os
import datetime
import logging
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.CasefileManagement.models.casefile import Casefile, Event, EventLog

# Configure basic logging for the script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def create_and_upload_mock_casefile():
    logging.info("Initializing DatabaseManager...")
    db_manager = DatabaseManager()

    # Generate ISO 8601 formatted timestamps
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Create a mock EventLog
    mock_event = Event(
        timestamp=now_iso,
        agent_id="mock_agent",
        event_type="mock_event",
        description="This is a mock event for testing."
    )
    mock_event_log = EventLog(events=[mock_event])

    # Create a mock Casefile instance with string timestamps
    mock_casefile_id = "mock_casefile_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    mock_casefile = Casefile(
        id=mock_casefile_id,
        name="Mock Test Casefile",
        description="This is a temporary casefile created for testing timestamp conversion.",
        created_at=now_iso,
        modified_at=now_iso,
        status="active",
        spec_version="1.0",
        type="test",
        casefile_type="mock",
        event_log=mock_event_log
    )

    logging.info(f"Attempting to save mock casefile: {mock_casefile.id}")
    try:
        await db_manager.save_casefile(mock_casefile)
        logging.info(f"Mock casefile '{mock_casefile.id}' saved successfully to Firestore.")
    except Exception as e:
        logging.error(f"Failed to save mock casefile: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(create_and_upload_mock_casefile())