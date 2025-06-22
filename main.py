import json
import os
from src.allure_report import AllureReportFetcher
from src.ado_testplan import ADOTestPlanUpdater

def main():
    try:
        print("Hello, World! This is a basic Python project ready for Allure integration.")
        # Load config from config.json
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        ado_config = config.get('ado', {})
        allure_config = config.get('allure', {})
        ADO_ORG_URL = f"https://dev.azure.com/{ado_config.get('organization')}"
        ADO_PROJECT = ado_config.get('project')
        ADO_PAT = ado_config.get('pat')
        ADO_TEST_PLAN_ID = int(ado_config.get('test_plan_id'))
        ADO_TEST_SUITE_ID = int(ado_config.get('test_suite_id'))
        REPORTPORTAL_URL = allure_config.get('results_url')
        allowed_statuses = set(allure_config.get('update_statuses', ['passed', 'failed']))

        print(f"REPORTPORTAL_URL: {REPORTPORTAL_URL}")
        print(f"ADO_ORG_URL: {ADO_ORG_URL}")
        print(f"ADO_PROJECT: {ADO_PROJECT}")
        print(f"ADO_TEST_PLAN_ID: {ADO_TEST_PLAN_ID}")
        print(f"ADO_TEST_SUITE_ID: {ADO_TEST_SUITE_ID}")
        print(f"ALLOWED_STATUSES: {allowed_statuses}")

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
