import streamlit as st
import json
import sys
from pdf_report import generate_pdf_report
from zoneinfo import ZoneInfo
from datetime import datetime
# Import all our custom agent modules
from agent import SalaryAgent
import prompts
from tax_rules import get_tax_rules, get_tax_rules_as_string

# --- Page Configuration ---
st.set_page_config(
    page_title="Salary Analyzer & Tax Opportunity Agent",
    page_icon="🧾",
    layout="wide"
)

# --- Agent Initialization ---
@st.cache_resource
def get_agent():
    """
    Caches the SalaryAgent instance to avoid re-initializing
    and wasting API key loads on every script rerun.
    """
    try:
        return SalaryAgent()
    except EnvironmentError as e:
        st.error(f"Error initializing agent: {e}")
        st.error("Please ensure you have a .env file in the root directory with your OPENAI_API_KEY.")
        return None

agent = get_agent()

# --- Session State Management ---
# This is the core of the Streamlit app. We use the "step"
# variable to manage the UI flow (a simple state machine).

if "step" not in st.session_state:
    st.session_state.step = "awaiting_input"
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None
if "country" not in st.session_state:
    st.session_state.country = "India"
if "tax_year" not in st.session_state:
    st.session_state.tax_year = "2024-25"

def start_over():
    """
    Function to reset the session state and go back to the beginning.
    """
    st.session_state.step = "awaiting_input"
    st.session_state.parsed_data = None
    st.session_state.final_report = None
    # Keep country and year as they were
    st.rerun()

# --- Sidebar ---
# The sidebar holds the disclaimers and configuration.
st.sidebar.title("🧾 Confidential Tax Analyst")
st.sidebar.markdown("---")
st.sidebar.warning(prompts.DATA_HANDLING_WARNING)
st.sidebar.markdown("---")
st.sidebar.info(prompts.NOT_ADVICE_DISCLAIMER_START)
st.sidebar.markdown("---")
st.sidebar.header("Configuration")

# Update session state from sidebar inputs
st.session_state.country = st.sidebar.selectbox(
    "Select Country", 
    ["India", "USA"], 
    index=0
)
st.session_state.tax_year = st.sidebar.text_input(
    "Enter Financial Year", 
    value="2024-25" if st.session_state.country == "India" else "2024"
)

if st.sidebar.button("Start Over / Reset"):
    start_over()

# --- Main Application Body ---

st.title("Salary Analyzer & Tax Opportunity Agent")
st.markdown(f"""
Welcome! This agent will analyze your pasted salary slip to find potential tax-saving opportunities.
Your current settings are: **Country: {st.session_state.country}**, **Year: {st.session_state.tax_year}**.
""")

# If the agent failed to initialize (e.g., no API key), stop here.
if not agent:
    st.error("Agent could not be initialized. Stopping application.")
    sys.exit()

# --- STEP 1: Awaiting Input ---
if st.session_state.step == "awaiting_input":
    st.subheader("Step 1: Paste Your Salary Slip Text")
    payslip_text = st.text_area(
        "Paste your payslip text here. Remember to remove personal info.", 
        height=300,
        placeholder="Basic Salary: 50,000\nHRA: 20,000\nEmployee PF: 6,000\n..."
    )

    if st.button("Analyze Payslip", type="primary"):
        if not payslip_text:
            st.error("Please paste your payslip text before analyzing.")
        else:
            # Check if tax rules exist
            tax_rules = get_tax_rules(st.session_state.country, st.session_state.tax_year)
            if not tax_rules:
                st.error(f"Sorry, I don't have the tax rules for {st.session_state.country} {st.session_state.tax_year}.")
            else:
                with st.spinner("Calling AI Parser Engine... (Cost-efficient call 1/2)"):
                    st.session_state.payslip_text = payslip_text
                    parsed_data = agent.parse_payslip_text(payslip_text)
                
                if parsed_data:
                    st.session_state.parsed_data = parsed_data
                    st.session_state.step = "awaiting_confirmation"
                    st.rerun()
                else:
                    st.error("Sorry, I was unable to parse your payslip. Please try pasting it again, perhaps with clearer formatting.")

# --- STEP 2: Awaiting Confirmation ---
elif st.session_state.step == "awaiting_confirmation":
    st.subheader("Step 2: Please Confirm Your Parsed Data")
    st.write("Thank you. I have parsed the following *monthly* figures from your data. Please confirm if these are correct before I proceed with the full analysis.")
    
    st.json(st.session_state.parsed_data)
    
    st.markdown("---")
    
    st.write("If this data is incorrect, click 'Start Over' to re-paste your slip.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Confirm & Generate Report", type="primary"):
            with st.spinner("Calling AI Analysis Engine... (Smarter call 2/2)"):
                tax_rules_string = get_tax_rules_as_string(st.session_state.country, st.session_state.tax_year)
                
                final_report = agent.generate_analysis_report(
                    confirmed_data=st.session_state.parsed_data,
                    country=st.session_state.country,
                    tax_year=st.session_state.tax_year,
                    tax_rules_string=tax_rules_string
                )
            
            st.session_state.final_report = final_report
            st.session_state.step = "showing_report"
            st.rerun()

    with col2:
        if st.button("Start Over"):
            start_over()

# --- STEP 3: Showing Report ---
elif st.session_state.step == "showing_report":
    st.subheader("Step 3: Your Personalized Tax Opportunity Report")
    st.balloons()

    st.markdown(st.session_state.final_report)

    st.markdown("---")
    st.success("I hope this analysis is useful!")
    st.info(prompts.NOT_ADVICE_DISCLAIMER_END)

    # Prepare data for PDF
    payslip_text = st.session_state.get("payslip_text", None)
    confirmed_data = st.session_state.get("parsed_data", {})
    final_report_text = st.session_state.get("final_report", "")

    # Generate the PDF bytes
    with st.spinner("Generating downloadable PDF..."):
        pdf_bytes = generate_pdf_report(
            confirmed_data=confirmed_data,
            final_report=final_report_text,
            payslip_text=payslip_text,
            country=st.session_state.country,
            tax_year=st.session_state.tax_year,
            title="Salary Analyzer & Tax Opportunity Report"
        )

    # Filename with timestamp
    try:
        tz = ZoneInfo("Asia/Kolkata")
        timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
    except Exception:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    filename = f"salary_report_{timestamp}.pdf"

    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )

    if st.button("Analyze Another Payslip"):
        start_over()
