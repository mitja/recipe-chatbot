# backend/tool_executor.py

from sqlalchemy.orm import Session
from typing import Any, Dict, Optional

from database import services as db_services # Using 'as' for clarity
from database.models import GenderEnum # For converting string from LLM to Enum

def execute_tool(tool_name: str, tool_args: Dict[str, Any], db: Session) -> Any:
    """
    Executes the appropriate database service function based on the tool_name.
    Args:
        tool_name: The name of the function/tool to execute.
        tool_args: A dictionary of arguments for the function.
        db: The SQLAlchemy database session.

    Returns:
        The result from the service function, or an error message string.
    """
    
    print(f"Executing tool: {tool_name} with args: {tool_args}") # Debug print

    if tool_name == "create_family":
        if not all(k in tool_args for k in ("name", "slug")):
            return "Error: Missing required arguments 'name' or 'slug' for create_family."
        family = db_services.create_family(db, name=tool_args["name"], slug=tool_args["slug"])
        if family:
            return f"Successfully created family: {family.name} (ID: {family.id})"
        else:
            return f"Error: Could not create family. A family with name '{tool_args['name']}' or slug '{tool_args['slug']}' may already exist."

    elif tool_name == "add_family_member":
        required_args = ["family_slug", "name"]
        if not all(k in tool_args for k in required_args):
            return f"Error: Missing one or more required arguments for add_family_member: {', '.join(required_args)}"

        family_slug = tool_args["family_slug"]
        family = db_services.get_family_by_slug(db, slug=family_slug)
        if not family:
            return f"Error: Family with slug '{family_slug}' not found."

        # Prepare member details, converting gender string to GenderEnum
        member_details = {k: v for k, v in tool_args.items() if k != "family_slug"}
        if "gender" in member_details and isinstance(member_details["gender"], str):
            try:
                member_details["gender"] = GenderEnum[member_details["gender"].upper()]
            except KeyError:
                valid_genders = [g.value for g in GenderEnum]
                return f"Error: Invalid gender value '{member_details['gender']}'. Valid options are: {', '.join(valid_genders)}."
        
        member = db_services.add_family_member(db, family_id=family.id, **member_details)
        if member:
            return f"Successfully added member: {member.name} to family {family.name} (Member ID: {member.id})"
        else:
            # This path might not be hit if family check is solid and add_family_member doesn't return None for other reasons
            return f"Error: Could not add member {tool_args.get('name', 'Unknown')} to family {family.name}."


    elif tool_name == "get_family_members_summary":
        if "family_slug" not in tool_args:
            return "Error: Missing required argument 'family_slug' for get_family_members_summary."
        
        family_slug = tool_args["family_slug"]
        family = db_services.get_family_by_slug(db, slug=family_slug)
        if not family:
            return f"Error: Family with slug '{family_slug}' not found."
        
        summary_csv = db_services.get_family_members_summary(db, family_id=family.id)
        # The service already returns "Family not found." or "No members found..."
        # So, we can directly return the result.
        return summary_csv

    # Add other tool dispatches here later (e.g., for shopping list)

    else:
        return f"Error: Unknown tool '{tool_name}'."
