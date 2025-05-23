# backend/tool_definitions.py

# Schemas for tools that the LLM can call.
# Based on OpenAI's function calling schema.

# Import GenderEnum to use its values in the add_family_member tool description
# This assumes database models are accessible from here, adjust path if needed.
# For simplicity, we might just list gender strings in description and handle conversion in tool_executor.
# from database.models import GenderEnum # Let's avoid direct model import here for now.

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "create_family",
            "description": "Creates a new family unit. Use a short, memorable, URL-friendly slug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the family."
                    },
                    "slug": {
                        "type": "string",
                        "description": "A short, URL-friendly slug for the family (e.g., 'the-smiths')."
                    }
                },
                "required": ["name", "slug"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_family_member",
            "description": "Adds a new member to a specified family. All details are optional except name and family_slug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "family_slug": {
                        "type": "string",
                        "description": "The slug of the family to add the member to."
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the family member."
                    },
                    "height_cm": {
                        "type": "integer",
                        "description": "Height of the member in centimeters (optional)."
                    },
                    "weight_kg": {
                        "type": "number", # JSON schema uses 'number' for floats
                        "description": "Weight of the member in kilograms (optional)."
                    },
                    "age_years": {
                        "type": "integer",
                        "description": "Age of the member in years (optional)."
                    },
                    "gender": {
                        "type": "string",
                        "description": "Gender of the member (e.g., 'male', 'female', 'diverse', 'prefer_not_to_say') (optional).",
                        # "enum": [gender.value for gender in GenderEnum] # Dynamically listing enum values
                        "enum": ["male", "female", "diverse", "prefer_not_to_say"] # Hardcode for simplicity in schema
                    },
                    "target_caloric_intake_kcal": {
                        "type": "integer",
                        "description": "Target daily caloric intake in kcal for the member (optional)."
                    }
                },
                "required": ["family_slug", "name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_family_members_summary",
            "description": "Retrieves a CSV summary of all members for a given family slug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "family_slug": {
                        "type": "string",
                        "description": "The slug of the family to retrieve members from."
                    }
                },
                "required": ["family_slug"]
            }
        }
    }
    # Add Shopping List tools here later
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "create_shopping_list",
    #         ...
    #     }
    # },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_latest_shopping_list",
    #         ...
    #     }
    # }
]

# Example of how to get just the function schemas if needed by some LiteLLM configurations
# (though often the full tool definition above is used)
FUNCTION_SCHEMAS = [tool["function"] for tool in TOOL_DEFINITIONS if tool["type"] == "function"]
