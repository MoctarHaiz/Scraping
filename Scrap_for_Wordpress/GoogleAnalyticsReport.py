from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import pandas as pd


class GoogleAnalyticsReport:
    def __init__(self, key_file_location='cles_google_analyctics.json'):
        self.SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
        self.KEY_FILE_LOCATION = key_file_location
        self.credentials = Credentials.from_service_account_file(
            self.KEY_FILE_LOCATION, scopes=self.SCOPES)
        self.service = build(serviceName='analyticsreporting',
                             version='v4', credentials=self.credentials)

    def get_report(
        self, view_id,
        start_date='7daysAgo', end_date='yesterday',
        metrics=[], dimensions=[]
    ):
        return self.service.reports().batchGet(
            body={
                'reportRequests': [{
                    'viewId': view_id,
                    'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                    'metrics': [{'expression': m} for m in metrics],
                    'dimensions': [{'name': d} for d in dimensions],
                    'pageSize': 50000,
                }]
            }).execute()

    @staticmethod
    def to_dataframe(res):
        report = res['reports'][0]
        dimensions = report['columnHeader']['dimensions']
        metrics = [m['name'] for m in report['columnHeader']
                   ['metricHeader']['metricHeaderEntries']]
        headers = [*dimensions, *metrics]

        data_rows = report['data']['rows']
        data = []
        print("-> " + str(len(data_rows)) +
              " articles obtained from Google Analytics")
        for row in data_rows:
            data.append([*row['dimensions'], *row['metrics'][0]['values']])

        return pd.DataFrame(data=data, columns=headers)
