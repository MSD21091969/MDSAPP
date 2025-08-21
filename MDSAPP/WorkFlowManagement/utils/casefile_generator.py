import random
from typing import Dict, Any, List

from MDSAPP.CasefileManagement.manager import CasefileManager
from MDSAPP.core.managers.database_manager import DatabaseManager
from MDSAPP.CasefileManagement.models.casefile import CasefileType, Casefile # Added Casefile
from MDSAPP.core.models.mission import Mission # New import
from MDSAPP.core.models.stix_inspired_models import Campaign # Add this import

def _mission_to_campaign(mission_obj: Any) -> Campaign:
    if isinstance(mission_obj, Mission):
        # Convert Mission object to Campaign
        campaign_name = mission_obj.goal
        campaign_description = f"Context: {mission_obj.context}"
        if mission_obj.parameters:
            campaign_description += f" Parameters: {mission_obj.parameters}"
        return Campaign(name=campaign_name, description=campaign_description)
    elif isinstance(mission_obj, str):
        # If it's a string, use it as the campaign name
        return Campaign(name=mission_obj)
    else:
        raise TypeError(f"Unsupported mission object type: {type(mission_obj)}")

def generate_real_estate_data() -> Dict[str, Any]:
    """Generates sample data for a real estate market analysis casefile."""
    main_casefile_name = "Real Estate Market Analysis 2025"
    main_casefile_description = "Comprehensive analysis of current and projected real estate market trends for 2025."
    main_casefile_mission_obj = Mission(
        goal="Provide actionable insights for investment and development strategies",
        context="real estate market analysis",
        parameters={
            "location": "Arnhem",
            "family_composition": "m/f and two children between 10-15",
            "data_sources": ["CBS", "Kadaster"],
            "data_year": "2024 Q4",
            "house_price_range": "300000-7000000",
            "income_data": "various variables"
        },
        target_audience="real estate agent",
        timeframe="2024 Q4"
    )

    sub_casefiles_data = [
        {
            "name": "Residential Market Trends",
            "description": "Analysis of housing prices, sales volume, and inventory across key regions.",
            "mission": Mission(
                goal="Identify emerging residential investment opportunities and risks",
                context="residential market trends",
                parameters={"region": "Arnhem"},
                target_audience="real estate agent"
            ),
            "casefile_type": CasefileType.RESEARCH
        },
        {
            "name": "Commercial Property Outlook",
            "description": "Review of office, retail, and industrial property performance and vacancy rates.",
            "mission": "Assess the viability of new commercial developments and redevelopments.",
            "casefile_type": CasefileType.RESEARCH
        },
        {
            "name": "Demographic Impact on Housing",
            "description": "Study of population shifts, age groups, and income levels affecting housing demand.",
            "mission": "Forecast long-term housing needs based on demographic changes.",
            "casefile_type": CasefileType.RESEARCH
        }
    ]

    return {
        "main_casefile": {
            "name": main_casefile_name,
            "description": main_casefile_description,
            "mission": main_casefile_mission_obj, # Corrected to use the Mission object
            "casefile_type": CasefileType.RESEARCH # Main project type
        },
        "sub_casefiles_data": sub_casefiles_data
    }

async def create_real_estate_casefile_with_data(casefile_manager: CasefileManager, user_id: str) -> Casefile:
    """
    Simulates the Workflow Engineer creating a new real estate casefile
    and sub-casefiles with generated data.
    """
    data = generate_real_estate_data()
    main_cf_data = data["main_casefile"]

    print(f"Creating main casefile: {main_cf_data['name']}")
    main_casefile = await casefile_manager.create_casefile(
        name=main_cf_data["name"],
        description=main_cf_data["description"],
        user_id=user_id
    )
    # Update casefile_type and mission
    updates = {"casefile_type": main_cf_data["casefile_type"], "campaign": _mission_to_campaign(main_cf_data["mission"])}
    await casefile_manager.update_casefile(main_casefile.id, user_id, updates)

    for sub_cf_data in data["sub_casefiles_data"]:
        print(f"Creating sub-casefile: {sub_cf_data['name']} under {main_casefile.name}")
        sub_casefile = await casefile_manager.create_casefile(
            name=sub_cf_data["name"],
            description=sub_cf_data["description"],
            parent_id=main_casefile.id,
            user_id=user_id
        )
        # Update casefile_type and mission for sub-casefile
        updates = {"casefile_type": sub_cf_data["casefile_type"], "campaign": _mission_to_campaign(sub_cf_data["mission"])}
        await casefile_manager.update_casefile(sub_casefile.id, user_id, updates)

    print(f"Successfully created main casefile '{main_casefile.name}' and its sub-casefiles.")
    main_casefile = await casefile_manager.load_casefile(main_casefile.id)
    return main_casefile

# Example usage (for testing purposes, not part of the main agent flow)
if __name__ == "__main__":
    import asyncio
    # This part would typically be handled by the main application's dependency injection
    # or initialization process.
    db_manager = DatabaseManager()
    casefile_manager = CasefileManager(db_manager)

    async def main():
        new_real_estate_casefile = await create_real_estate_casefile_with_data(casefile_manager, user_id="test_user")
        print(f"New main casefile ID: {new_real_estate_casefile.id}")

        # Verify creation by listing all casefiles
        all_casefiles = await casefile_manager.list_all_casefiles()
        print("\nAll Casefiles in the system:")
        for cf in all_casefiles:
            print(f"- {cf.name} (ID: {cf.id}, Type: {cf.casefile_type.value})")
            if cf.sub_casefile_ids:
                for sub_cf_id in cf.sub_casefile_ids:
                    sub_cf = await casefile_manager.load_casefile(sub_cf_id)
                    if sub_cf:
                        print(f"  - Sub: {sub_cf.name} (ID: {sub_cf.id}, Type: {sub_cf.casefile_type.value})")

    asyncio.run(main())

