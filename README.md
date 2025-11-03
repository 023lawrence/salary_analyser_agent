# 🧾 Salary Analyzer & Tax Opportunity Agent (Streamlit)

> **“Confidential, Calculated, and Clear.”**  
> An AI-powered Streamlit app that analyzes your salary slip, identifies tax-saving opportunities, and generates a professional, downloadable PDF report — all while keeping your data private.

---

## 📌 Overview

The **Salary Analyzer & Tax Opportunity Agent** transforms unstructured salary slips into structured, actionable insights.  
Using OpenAI’s advanced parsing and analysis models, it:

1. **Extracts** key salary components (Basic, HRA, PF, etc.).
2. **Identifies** existing deductions and optimization gaps.
3. **Explains** tax-saving options (like Section 80C/80D).
4. **Generates** a secure and polished **AI-generated report in PDF** format.

> ⚠️ **Disclaimer:**  
> This tool is for **educational and informational purposes only**.  
> It is not financial or tax advice. Always consult a qualified tax advisor before making financial decisions.

---

## 🏗️ Project Structure
/salary-agent-streamlit/
├── .streamlit/
│   └── config.toml          # Streamlit theme customization
├── app.py                   # Main Streamlit app entry point
├── agent.py                 # Core AI logic (parser + analyzer)
├── prompts.py               # Custom OpenAI system prompts
├── tax_rules.py             # Country-wise tax rules (India, USA)
├── tools.py                 # Pydantic data schema for salary parsing
├── pdf_report.py            # PDF generation logic
├── fonts/                   # DejaVuSans fonts (for ₹/$ symbol support)
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
└── .env                     # API key template
text---

## ⚙️ Setup Instructions

### 1. Clone the Repository

 “git clone https://github.com/023lawrence/salary-agent-streamlit.git"
cd salary-agent-streamlit
2. Create a Virtual Environment
"bashpython -m venv venv"
"source venv/bin/activate"  # macOS/Linux
# venv\Scripts\activate  # Windows
3. Install Dependencies
bashpip install -r requirements.txt
4. Set Up Environment Variables
Copy .env.example to .env and add your OpenAI API key:
bashOPENAI_API_KEY="sk-your-key-here"
5. Run the Application
Start the app:
bashstreamlit run app.py
Then open your browser:
http://localhost:8501


💼 How It Works

Paste Your Payslip Text
Remove sensitive info like Name, PAN, Bank Account, etc.
AI Parser (Call 1)
Extracts components (Basic, HRA, PF, etc.) → JSON output.
Confirm Extracted Data
You verify monthly values before analysis.
AI Analyst (Call 2)
Applies country tax rules (e.g., India FY 2024–25).
Highlights tax-saving gaps, deductions, and opportunities.
Generate & Download Report
Produces a professional PDF including:

Parsed data summary
Tax savings breakdown
Educational explanations
Disclaimer footer




🧮 Example Output (India FY 2024–25)
Section 80C Gap Analysis

Observation: You currently invest ₹72,000 annually in PF.
Opportunity: You can still utilize ₹78,000 to reach the ₹1,50,000 limit.
Explanation: Section 80C covers instruments like PPF, ELSS, and Tax-Saver FDs.

Section 80D

Observation: No health insurance premium detected.
Opportunity: Premiums paid for health insurance (self/family/parents) can be claimed under Section 80D (up to ₹25,000 for self, ₹25,000 for parents).


🔐 Data Privacy & Compliance

🛡️ No Data Stored: All analysis runs in-memory (session-based).
✅ User Confirmation: You verify extracted data before analysis.
🚫 No Third-Party Sharing: The app runs locally and uses OpenAI’s API securely.
🧠 AI Transparency: Every report includes an AI-generated report disclaimer.


🧰 Tech Stack
LayerTools & LibrariesFrontend/UIStreamlitBackend LogicPython 3.12, OpenAI APIData ValidationPydanticStyling & UI.streamlit/config.tomlDocument Gen.ReportLab (with Unicode fonts)Environmentpython-dotenvVersion ControlGit & GitHub

🌟 Future Enhancements

📄 OCR Integration: Extract payslip data from uploaded PDFs.
🌍 Multi-Country Support: Expand tax rules (e.g., USA, UK, Canada).
💹 Simulation Tool: Project tax savings based on new investments.
🔐 User Auth: Optional authentication with encrypted local storage.


📜 License
This project is open-source under the MIT License.

🙌 Acknowledgements

OpenAI API — For structured parsing and intelligent text analysis.
Streamlit — For building a quick, interactive user interface.
ReportLab — For professional PDF rendering with Unicode font support.


👨‍💻 Author
Lawrence Mondal
🎓 Data Science & Analytics Enthusiast | 💼 Financial Analyst
🧾 Creator of the “Confidential Tax Analyst” Agent
📧 Email: lawrence.mondal24@gmail.com
🌐 LinkedIn: linkedin.com/in/lawrence-mondal
💻 GitHub: github.com/023lawrence
