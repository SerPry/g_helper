"""
This is a helper bundel forwork with GA report API v4
"""
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


class Analytics(object):

    def __init__(self, config):
        self.__config = config
        self.__init_analyticsreporting()


    def __init_analyticsreporting(self):
        """Initializes an Analytics Reporting API V4 service object.

        Returns:
            An authorized Analytics Reporting API V4 service object.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.__config.KEY_FILE_LOCATION, self.__config.SCOPES)

        # Build the service object.
        self.__analytics = build('analyticsreporting', 'v4', credentials=credentials)

        # return analytics

    def get_report(self, metrics=[], dimensions=[]):
        """Queries the Analytics Reporting API V4.

        Args:
        analytics: An authorized Analytics Reporting API V4 service object.
        Returns:
        The Analytics Reporting API V4 response.
        """
        if not metrics or not dimensions:
            return None
        self.response = self.__analytics.reports().batchGet(
            body={
            'reportRequests': [
            {
                'viewId': self.__config.VIEW_ID,
                'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
            #   'metrics': [{'expression': 'ga:sessions'}],
                'metrics': [{'expression': 'ga:{}'.format(metric)} for metric in metrics],
                # 'dimensions': [{'name': 'ga:userType'}]
                'dimensions': [{'name': 'ga:{}'.format(dim)} for dim in dimensions]
            }]
            }
        ).execute()
        if self.response:
            print("Report is ready")

    def response2df(self):
        """
        Parse and wrap data into pandas DataFrame

        Args:
            response:An Analytics Reporting API V4 response
        Returns:
            The pandas DataFrames

        """
        dfs = []
        for report in self.response.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimensionHeaders = columnHeader.get('dimensions', [])
            metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
            metric_headers = ["m_" + metric["name"] for metric in metricHeaders]
            df_columns = dimensionHeaders + metric_headers
            df_data = []
            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                dateRangeValues = row.get('metrics', [])
                df_data.append(dimensions + dateRangeValues[0]["values"])
            df = pd.DataFrame(data =df_data, columns=df_columns)
            dfs.append(df)
        if len(dfs) == 1:
            return dfs[0]
        elif len(dfs) == 0:
            return None
        else:
            return dfs

if __name__ == "__main__":
    pass