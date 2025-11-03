from pydantic import BaseModel, Field
from typing import Optional

# This Pydantic model defines the *structure* we want OpenAI to extract.
# This is our "Payslip Parser Engine" tool schema.
class PayslipComponents(BaseModel):
    """
    The extracted components from a user's monthly salary slip.
    All values should be the *monthly* amount.
    """
    basic_salary: Optional[float] = Field(
        None, description="The monthly Basic Salary or Basic Pay."
    )
    house_rent_allowance: Optional[float] = Field(
        None, description="The monthly House Rent Allowance (HRA)."
    )
    employee_pf_contribution: Optional[float] = Field(
        None, description="The monthly Employee's Provident Fund (PF) contribution."
    )
    professional_tax: Optional[float] = Field(
        None, description="The monthly Professional Tax (PT) deduction."
    )
    leave_travel_allowance: Optional[float] = Field(
        None, description="The monthly Leave Travel Allowance (LTA)."
    )
    special_allowance: Optional[float] = Field(
        None, description="The monthly Special Allowance or Other Allowance."
    )
    
    def to_dict(self):
        """Helper function to convert model to a clean dictionary."""
        return self.model_dump(exclude_unset=True, exclude_none=True)