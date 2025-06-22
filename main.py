from src.allure_report import AllureReportFetcher
from src.ado_testplan import ADOTestPlanUpdater

def main():
    try:
        print("Hello, World! This is a basic Python project ready for Allure integration.")
        ADO_ORG_URL = "https://dev.azure.com/tr-corp-tax"   
        ADO_PROJECT = "onesource-global-trade" 

        # Prompt user for all required inputs
        REPORTPORTAL_URL = input("Enter the Allure results JSON URL: ").strip()
        # Ask user which statuses to update
        print("Which test results do you want to update in ADO?")
        print("1. Passed only")
        print("2. Passed and Failed")
        print("3. All (Passed, Failed, NotExecuted/Skipped)")
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == '1':
            allowed_statuses = {'passed'}
        elif choice == '2':
            allowed_statuses = {'passed', 'failed'}
        else:
            allowed_statuses = {'passed', 'failed', 'notexecuted', 'skipped'}
        ADO_TEST_PLAN_ID = int(input("Enter Azure DevOps Test Plan ID: ").strip())
        ADO_TEST_SUITE_ID = int(input("Enter Azure DevOps Test Suite ID: ").strip())
        ADO_PAT = input("Enter your Azure DevOps Personal Access Token (PAT): ").strip()

        print(f"REPORTPORTAL_URL: {REPORTPORTAL_URL}")
        print(f"ADO_ORG_URL: {ADO_ORG_URL}")
        print(f"ADO_PROJECT: {ADO_PROJECT}")
        print(f"ADO_TEST_PLAN_ID: {ADO_TEST_PLAN_ID}")
        print(f"ADO_TEST_SUITE_ID: {ADO_TEST_SUITE_ID}")

        print("Starting Allure fetch...")
        # Fetch Allure/ReportPortal results
        allure = AllureReportFetcher(REPORTPORTAL_URL)
        results = allure.fetch_results()
        print(f"Fetched {len(results)} test results from Allure/ReportPortal.")
        print("Starting ADO fetch...")
        # Connect to ADO and update test results
        ado = ADOTestPlanUpdater(ADO_ORG_URL, ADO_PAT, ADO_PROJECT)
        test_cases = ado.get_all_test_cases_from_plan(ADO_TEST_PLAN_ID)
        print(f"Fetched {len(test_cases)} test cases from all suites in ADO Test Plan.")

        # Collect all test point IDs for the test run
        point_ids = [tc['test_point_id'] for tc in test_cases]
        # Create a new test run with the correct test points
        run_id = ado.create_test_run(ADO_TEST_PLAN_ID, ADO_TEST_SUITE_ID, point_ids, run_name="Automated Run")
        print(f"Created test run with ID: {run_id}")

        # Match and update test results
        for tc in test_cases:
            tc_id = tc['id']
            tc_id_str = tc['id_str']
            test_point_id = tc['test_point_id']
            test_case_revision = tc['test_case_revision']
            test_case_title = tc['test_case_title']
            found = False
            for r in results:
                allure_name = r.get('name', '')
                status = r.get('status', '').lower()
                if tc_id_str in allure_name and status in allowed_statuses:
                    found = True
                    # Map Allure/ReportPortal status to ADO outcome
                    if status and status == 'passed':
                        ado_outcome = 'Passed'
                    elif status and status == 'failed':
                        ado_outcome = 'Failed'
                    else:
                        ado_outcome = 'NotExecuted'
                    ado.add_test_result_to_run(
                        run_id, tc_id, test_point_id, test_case_revision, test_case_title, ado_outcome,
                        comment=f"Updated by automation. Allure status: {status}"
                    )
                    print(f"Matched ADO TestCase {tc_id} with Allure name '{allure_name}' and status '{status}'")
                    break
            if not found:
                print(f"No result found for test case: TestCase-{tc_id} (ID: {tc_id})")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")

if __name__ == "__main__":
    print("[DEBUG] __name__ == '__main__'")
    main()
