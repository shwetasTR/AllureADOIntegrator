# AllureReportPortalIntegrationWithTestcases

This is a basic Python project scaffolded for automated testing and future integration with Allure reports.

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
4. **Update the `config.json` file** with your Azure DevOps and Allure details before running any test cases. Example:

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

   - **How to get the Allure JSON URL:**
     - The `results_url` should point to the Allure JSON file (e.g., `behaviors.json`) that contains your test results.
     - direct HTTP(S) link to the JSON file if hosted remotely.
     - Example for a remote URL:
       ```json
       "results_url": "https://your-server.com/allure-docker-service/projects/your-project/reports/latest/data/behaviors.json"
       ```
     - Example for a URL:
       ```json
       "results_url": "https://ogt-gtm-angular-test-results-api.8443.aws-int.thomsonreuters.com/allure-docker-service/projects/product-classification-api-qa-aws/reports/latest/data/behaviors.json"
       ```
   - Make sure the JSON file is accessible and contains the expected Allure test results structure.

5. To run your code, add your Python scripts to this folder.python main.py

## Next Steps

- Add your test cases and main code files.
- Integrate Allure and ReportPortal as needed.

---

This project is ready for further customization.
