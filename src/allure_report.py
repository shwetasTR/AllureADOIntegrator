import requests
import json
from typing import List, Dict

class AllureReportFetcher:
    def __init__(self, reportportal_url: str):
        self.url = reportportal_url

    def fetch_results(self) -> List[Dict]:
        """

                Fetches and parses Allure/ReportPortal results.
        Returns a list of test case dicts with at least 'name' and 'status'.
        """
        response = requests.get(self.url)
        if response.status_code == 200:
            try:
                data = response.json()
                # If the data is a list, return as-is (Allure behaviors.json format)
                if isinstance(data, list):
                    for tc in data:
                        print(f"Allure TestCase: name={tc.get('name')}, status={tc.get('status')}")
                    return [
                        {'name': tc.get('name'), 'status': tc.get('status')}
                        for tc in data if 'name' in tc and 'status' in tc
                    ]
                # Try to extract test cases from common Allure/ReportPortal structures
                elif 'children' in data:  # Allure summary
                    test_cases = []
                    for child in data['children']:
                        if 'name' in child and 'status' in child:
                            print(f"Allure TestCase: name={child['name']}, status={child['status']}")
                            test_cases.append({
                                'name': child['name'],
                                'status': child['status']
                            })
                    return test_cases
                elif 'testCases' in data:  # ReportPortal format
                    for tc in data['testCases']:
                        print(f"Allure TestCase: name={tc.get('name')}, status={tc.get('status')}")
                    return [
                        {'name': tc.get('name'), 'status': tc.get('status')}
                        for tc in data['testCases'] if 'name' in tc and 'status' in tc
                    ]
                else:
                    print(f"Allure raw data: {data}")
                    return data
            except Exception as e:
                raise Exception(f"Failed to parse Allure/ReportPortal results: {e}")
        else:
            raise Exception(f"Failed to fetch report: {response.status_code}")
