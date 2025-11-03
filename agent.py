import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import ValidationError
import re

# Import our custom modules
import prompts
from tools import PayslipComponents

# Load environment variables (OPENAI_API_KEY)
load_dotenv()

class SalaryAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        if not self.client.api_key:
            raise EnvironmentError("OPENAI_API_KEY not found in .env file. Please create a .env file with your key.")

    def parse_payslip_text(self, payslip_text: str) -> dict:
        """
        Call 1: The "Parsing" Call.
        Uses OpenAI Tool Calling to extract structured data from the payslip.
        """
        try:
            # In agent.py, inside parse_payslip_text()

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": prompts.PARSER_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Here is my payslip text: \n\n{payslip_text}"}
                ],
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "PayslipComponents",  # <-- The required function name
                            "description": "Extracts salary components from a user's payslip text.", # <-- A simple description
                            "parameters": PayslipComponents.model_json_schema() # <-- The Pydantic schema for the parameters
                        }
                    }
                ],
                tool_choice={"type": "function", "function": {"name": "PayslipComponents"}}
            )
            
            # Extract the tool call arguments
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name != "PayslipComponents":
                raise ValueError("Model did not call the correct tool.")
            
            # Load the arguments as JSON and validate with Pydantic
            raw_args = tool_call.function.arguments
            parsed_args = json.loads(raw_args)
            
            # Validate and convert to our model
            validated_components = PayslipComponents(**parsed_args)
            
            # Return as a clean dictionary
            return validated_components.to_dict()

        except ValidationError as e:
            print(f"[Agent Error: Pydantic validation failed]\n{e}")
            return None
        except Exception as e:
            print(f"[Agent Error: OpenAI API call failed]\n{e}")
            return None

    
# (other imports above)

    def generate_analysis_report(self, confirmed_data: dict, country: str, tax_year: str, tax_rules_string: str) -> str:
        """
        Call 2: The "Analysis" Call.
        Uses the confirmed JSON data and tax rules to generate the report.
        """

        # Safely substitute only the specific tokens we want — avoid using str.format()
        system_template = prompts.ANALYSIS_SYSTEM_PROMPT_TEMPLATE

        # Replace only the exact placeholders we expect
        system_prompt = re.sub(r"\{country\}", str(country), system_template)
        system_prompt = re.sub(r"\{tax_year\}", str(tax_year), system_prompt)
        # tax_rules_string may contain braces etc.; we insert it as-is
        system_prompt = re.sub(r"\{tax_rules\}", str(tax_rules_string), system_prompt)

        # Create the user message with the confirmed data
        user_message = f"""
        Here is my *confirmed* monthly salary data in JSON format.
        Please analyze it based on the tax rules provided in your system prompt.

        Confirmed Data:
        {json.dumps(confirmed_data, indent=2)}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"[Agent Error: OpenAI API call failed]\n{e}")
            return "An error occurred during analysis. Please try again."
