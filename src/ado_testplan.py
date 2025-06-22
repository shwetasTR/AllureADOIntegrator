from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from typing import List, Dict
import requests

class ADOTestPlanUpdater:
    def __init__(self, organization_url: str, personal_access_token: str, project: str):
        self.personal_access_token = personal_access_token  # Store PAT for REST API use
        credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=credentials)
        self.project = project
        self.test_client = self.connection.clients.get_test_client()

    def get_test_cases(self, test_plan_id: int) -> List[Dict]:
        """
        Fetches test cases from the specified ADO Test Plan.
        Returns a list of dicts with at least 'id' and 'name'.
        """
        test_cases = []
        # Use get_test_suites_list to get all suites for the test plan (API: get_test_suites_list)
        suites = self.test_client.get_test_suites_list(self.project, test_plan_id)
        for suite in suites:
            points = self.test_client.get_points(self.project, test_plan_id, suite.id)
            for point in points:
                if hasattr(point, 'test_case') and point.test_case:
                    test_cases.append({
                        'id': point.test_case.id,
                        'name': getattr(point.test_case, 'name', f"TestCase-{point.test_case.id}")
                    })
        return test_cases

    def update_test_result(self, test_case_id: int, outcome: str):
        """
        Updates the test result for a given test case in ADO.
        Outcome should be one of: 'Passed', 'Failed', 'NotExecuted', etc.
        """
        print(f"Would update test case {test_case_id} to outcome: {outcome}")
        # To actually update, you would use self.test_client.add_test_results_to_test_run(...)
        # See Azure DevOps Test API documentation for details.

    def get_test_cases_from_suite(self, test_plan_id: int, suite_id: int) -> List[Dict]:
        """
        Fetches test cases from a specific suite in the given ADO Test Plan using the REST API directly.
        Returns a list of dicts with id, name, id_str, test_point_id, test_case_revision, test_case_title.
        """
        # Use the PAT directly for REST API authentication
        url = f"{self.connection.base_url}/{self.project}/_apis/test/Plans/{test_plan_id}/suites/{suite_id}/points?api-version=5.0"
        print(f"[DEBUG] Fetching test points from URL: {url}")
        response = requests.get(url, auth=('', self.personal_access_token))
        print(f"[DEBUG] Response status code: {response.status_code}")
        print(f"[DEBUG] Response text: {response.text[:500]}")
        if response.status_code == 200:
            data = response.json()
            test_cases = []
            for point in data.get('value', []):
                tc = point['testCase']
                test_point_id = point['id']
                test_case_id = tc['id']
                test_case_title = tc.get('name', f"TestCase-{test_case_id}")
                test_case_revision = tc.get('revision', 1)
                print(f"ADO TestCase: id={test_case_id}, title={test_case_title}, point_id={test_point_id}, revision={test_case_revision}")
                test_cases.append({
                    'id': test_case_id,
                    'name': test_case_title,
                    'id_str': str(test_case_id),
                    'test_point_id': test_point_id,
                    'test_case_revision': test_case_revision,
                    'test_case_title': test_case_title
                })
            return test_cases
        else:
            raise Exception(f"Failed to fetch test points from suite: {response.status_code} {response.text}")

    def create_test_run(self, test_plan_id: int, suite_id: int, point_ids: list, run_name: str = "Automated Run") -> int:
        # ...existing code..._run(self, test_plan_id: int, suite_id: int, run_name: str = "Automated Run") -> int:
        """
        Creates a new test run for the given test plan and suite. Returns the run ID.
        """
        url = f"{self.connection.base_url}/{self.project}/_apis/test/runs?api-version=5.0"
        payload = {
            "name": run_name,
            "plan": {"id": str(test_plan_id)},
            "automated": True,
            "pointIds": [],  # You can fill this with test point IDs if needed
            "state": "InProgress",
            "isAutomated": True,
            "automated": True,
            "comment": "Created by automation script",
            "owner": None
        }
        print(f"[DEBUG] Creating test run with URL: {url}")
        print(f"[DEBUG] Payload: {payload}")
        response = requests.post(url, json=payload, auth=('', self.personal_access_token))
        print(f"[DEBUG] Status code: {response.status_code}")
        print(f"[DEBUG] Response: {response.text[:500]}")
        if response.status_code == 200 or response.status_code == 201:
            run_id = response.json()["id"]
            print(f"[ADO] Created test run with ID: {run_id}")
            return int(run_id)
        else:
            raise Exception(f"Failed to create test run: {response.status_code} {response.text}")

    def add_test_result_to_run(self, run_id: int, test_case_id: int, test_point_id: int, test_case_revision: int, test_case_title: str, outcome: str, comment: str = ""):
        """
        Adds or updates a test result for a test case in the specified run.
        """
        url = f"{self.connection.base_url}/{self.project}/_apis/test/runs/{run_id}/results?api-version=5.0"
        payload = [{
            "testCase": {"id": str(test_case_id)},
            "testPoint": {"id": str(test_point_id)},
            "testCaseRevision": test_case_revision,
            "testCaseTitle": test_case_title,
            "outcome": outcome,
            "state": "Completed",
            "comment": comment
        }]
        print(f"[DEBUG] Posting test result: {payload}")
        response = requests.post(url, json=payload, auth=('', self.personal_access_token))
        if response.status_code in (200, 201):
            print(f"[ADO] Updated test case {test_case_id} in run {run_id} with outcome {outcome}")
        else:
            print(f"[ADO] Failed to update test case {test_case_id} in run {run_id}: {response.status_code} {response.text}")

    def get_all_test_cases_from_plan(self, test_plan_id: int) -> List[Dict]:
        """
        Recursively fetches test cases from all suites (including child suites) in the given ADO Test Plan.
        Returns a list of dicts with id, name, id_str, test_point_id, test_case_revision, test_case_title.
        """
        # Get all suites in the test plan
        url = f"{self.connection.base_url}/{self.project}/_apis/test/Plans/{test_plan_id}/suites?api-version=5.0"
        print(f"[DEBUG] Fetching all suites from URL: {url}")
        response = requests.get(url, auth=('', self.personal_access_token))
        print(f"[DEBUG] Response status code: {response.status_code}")
        print(f"[DEBUG] Response text: {response.text[:500]}")
        if response.status_code == 200:
            data = response.json()
            all_test_cases = []
            for suite in data.get('value', []):
                suite_id = suite['id']
                print(f"[DEBUG] Fetching test cases from suite: {suite_id} ({suite.get('name')})")
                try:
                    suite_cases = self.get_test_cases_from_suite(test_plan_id, suite_id)
                    all_test_cases.extend(suite_cases)
                except Exception as e:
                    print(f"[ERROR] Failed to fetch test cases from suite {suite_id}: {e}")
            return all_test_cases
        else:
            raise Exception(f"Failed to fetch suites from plan: {response.status_code} {response.text}")
