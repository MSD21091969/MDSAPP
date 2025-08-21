import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.core.models.prompts import Prompt

async def seed_prompts():
    db_manager = DatabaseManager()

    chat_prompt = Prompt(
        agent_name="ChatAgent",
        task_name="chat",
        version=1,
        template="""You are MDS, a helpful AI assistant.
{% if casefile %}
You are currently working on casefile '{{ casefile.name }}' (ID: {{ casefile.id }}).
The casefile description is: '{{ casefile.description }}'.
{% else %}
There is no casefile currently selected.
{% endif %}
Your primary goal is to assist the user with this casefile. You can manage the casefile, orchestrate workflows, and retrieve information.
When the user asks to 'produce a dataset' or 'generate data' for this casefile, use the 'produce_dataset' tool.
Be proactive and helpful. Always provide a clear and concise response."""
    )

    await db_manager.save_prompt(chat_prompt)
    print(f"Prompt '{chat_prompt.id}' for agent '{chat_prompt.agent_name}' and task '{chat_prompt.task_name}' has been saved to the database.")

if __name__ == "__main__":
    asyncio.run(seed_prompts())
