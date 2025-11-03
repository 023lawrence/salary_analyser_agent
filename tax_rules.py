import json

# This database can be expanded with more countries or updated yearly.
TAX_RULES_DB = {
    "india": {
        "2024-25": {
            "80C_Limit": 150000,
            "80D_Self_Limit": 25000,
            "80D_Parents_Limit": 25000,
            "80D_Senior_Citizen_Limit": 50000,
            "Standard_Deduction": 50000,
            "Professional_Tax_Deductible": True
        },
        "2023-24": {
            "80C_Limit": 150000,
            "80D_Self_Limit": 25000,
            "80D_Parents_Limit": 25000,
            "80D_Senior_Citizen_Limit": 50000,
            "Standard_Deduction": 50000,
            "Professional_Tax_Deductible": True
        }
    },
    "usa": {
        "2024": {
            # Example data for a different country
            "401k_Limit": 23000,
            "Standard_Deduction_Single": 14600,
            "Standard_Deduction_Married": 29200
        }
    }
}

def get_tax_rules(country: str, year: str) -> dict:
    """
    Fetches the tax rules for a given country and year.
    Returns a dictionary of rules or None if not found.
    """
    country_rules = TAX_RULES_DB.get(country.lower())
    if not country_rules:
        return None
    
    year_rules = country_rules.get(year)
    return year_rules

def get_tax_rules_as_string(country: str, year: str) -> str:
    """
    Returns the tax rules as a formatted JSON string for the prompt.
    """
    rules = get_tax_rules(country, year)
    if not rules:
        return "No rules found for the specified country and year."
    
    return json.dumps(rules, indent=2)