import os
import sys
from celery import Celery

# Add the project root to the Python path
# This helps Celery find the MDSAPP module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# It's a good practice to get the broker URL from environment variables
# For local development, we can fall back to a default Redis URL.
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

app = Celery("MDSAPP")

app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_track_started=True,
    # Explicitly name the modules to import
    imports=("MDSAPP.WorkFlowManagement.workers.workflow_tasks",)
)

if __name__ == "__main__":
    app.start()