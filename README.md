# AllureReportPortalIntegrationWithTestcases

This is a basic Python project scaffolded for automated testing and future integration with Allure and ReportPortal.

## Getting Started

1. Ensure you have Python 3.8+ installed.
2. (Recommended) Create a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. **Update the `config.json` file** with your Azure DevOps and Allure/ReportPortal details before running any test cases. Example:
   ```json
   {
     "ado": {
       "organization": "tr-corp-tax",
       "project": "onesource-global-trade",
       "pat": "YOUR_PAT_TOKEN",
       "test_plan_id": 123,
       "test_suite_id": 456
     },
     "allure": {
       "results_url": "ENTER_YOUR_ALLURE_RESULTS_JSON_URL_HERE",
       "update_statuses": ["passed", "failed"]
     }
   }
   ```
5. To run your code, add your Python scripts to this folder.

## Next Steps

- Add your test cases and main code files.
- Integrate Allure and ReportPortal as needed.

---

This project is ready for further customization.
