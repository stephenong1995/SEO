import pickle
import pandas as pd 
import os

from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build

class gsc_etl:

    def __init__(self,website,credentials, pickled_file_folder, start_date,end_date, gbq_project):

        self.website = website
        self.start_date = start_date
        self.end_date = end_date
        self.credentials = credentials
        self.pickled_file_folder = pickled_file_folder
    
    
    # Returns URL Level Data

    def url_level_data(self):

        SITE_URL = self.website

        OAUTH_SCOPE = ('https://www.googleapis.com/auth/webmasters.readonly', 'https://www.googleapis.com/auth/webmasters')

        # Redirect URI for installed apps
        REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
        
    
        gsc_credentials =   self.credentials 

        
        pickled_credentials = self.pickled_file_folder


        try:
            credentials = pickle.load(open(pickled_credentials  + ".pickle", "rb"))
        except (OSError, IOError) as e:
            flow = InstalledAppFlow.from_client_secrets_file(gsc_credentials, scopes=OAUTH_SCOPE)
            credentials = flow.run_console()
            pickle.dump(credentials, open(pickled_credentials  + ".pickle", "wb"))

            # Connect to Search Console Service using the credentials 
        webmasters_service = build('webmasters', 'v3', credentials=credentials)

        maxRows = 25000
        i = 0
        output_rows = []
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        def date_range(start_date, end_date, delta=timedelta(days=1)):

            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += delta
        print('script start date:', start_date)

        for date in date_range(start_date, end_date):
            date = date.strftime("%Y-%m-%d")
            i = 0
            while True:

                request = {
                    'startDate' : date,
                    'endDate' : date,
                    'dimensions' : ["page"],
                    "searchType": "Web",
                    'rowLimit' : maxRows,
                    'startRow' : i * maxRows
                }

                response = webmasters_service.searchanalytics().query(siteUrl = SITE_URL, body=request).execute()
                if response is None:
                    break
                if 'rows' not in response:
                    break
                else:
                    for row in response['rows']:
                        page = row['keys'][0]
                        output_row = [page, row['clicks'], row['impressions'], row['position']]
                        output_rows.append(output_row)
                    i = i + 1
        print('script end date:', end_date)

        df = pd.DataFrame(output_rows, columns=['Address', 'URL_Clicks', 'URL_Impressions', 'URL_Average_Position'])
        df = df.groupby(['Address']).agg({'URL_Clicks':'sum','URL_Impressions':'sum','URL_Average_Position':'mean'}).reset_index()
        df['URL_CTR'] = df['URL_Clicks'] / df['URL_Impressions'] 
        

        df['Start_Date_Data'] = start_date
        df['End_Date_Data'] = end_date
        
        return df


    # Returns KW Data 
    def gsc_kw(self):

        SITE_URL = self.website

        OAUTH_SCOPE = ('https://www.googleapis.com/auth/webmasters.readonly', 'https://www.googleapis.com/auth/webmasters')

        # Redirect URI for installed apps
        REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
        
        gsc_credentials =   self.credentials 

        
        pickled_credentials = self.pickled_file_folder


        try:
            credentials = pickle.load(open(pickled_credentials  + ".pickle", "rb"))
        except (OSError, IOError) as e:
            flow = InstalledAppFlow.from_client_secrets_file(gsc_credentials, scopes=OAUTH_SCOPE)
            credentials = flow.run_console()
            pickle.dump(credentials, open(pickled_credentials  + ".pickle", "wb"))

            # Connect to Search Console Service using the credentials 
        webmasters_service = build('webmasters', 'v3', credentials=credentials)

        maxRows = 25000
        i = 0
        output_rows = []
        start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        
        def date_range(start_date, end_date, delta=timedelta(days=1)):

            current_date = start_date
            while current_date <= end_date:
                yield current_date
                current_date += delta
        print('script start date:', start_date)

        for date in date_range(start_date, end_date):
            date = date.strftime("%Y-%m-%d")
            i = 0
            while True:

                request = {
                    'startDate' : date,
                    'endDate' : date,
                    'dimensions' : ["page",'query'],
                    "searchType": "Web",
                    'rowLimit' : maxRows,
                    'startRow' : i * maxRows
                }

                response = webmasters_service.searchanalytics().query(siteUrl = SITE_URL, body=request).execute()
                if response is None:
                    break
                if 'rows' not in response:
                    break
                else:
                    for row in response['rows']:
                        page = row['keys'][0]
                        keyword = row['keys'][1]
                        output_row = [ page,keyword, row['clicks'], row['impressions'], row['ctr'], row['position']]
                        output_rows.append(output_row)
                    i = i + 1
        print('script end date:', end_date)

        df = pd.DataFrame(output_rows, columns=['Address','Main_Keyword', 'KW_Clicks', 'KW_Impressions', 'KW_CTR',  'KW_Average_Position'])
        df = df.groupby(['Address','Main Keyword']).agg({'KW_Clicks':'sum','KW_Impressions':'sum','KW_Average_Position':'mean'}).reset_index()
        df['KW_CTR'] = df['KW_Clicks'] / df['KW_Impressions'] 
        
        df['Start_Date_Data'] = start_date
        df['End_Date_Data'] = end_date
        
        return df
    
        
    # ETL Method 
    def gbq_etl(self):
        
        ### returns GSC Keyword Data 
        keyword_data = self.gsc_kw()
        
        ### Returns GSC URL Level Data
        url_data = self.url_level_data()
        
        
        ### Keyword Destination Table
        keyword_destination_table = self.keyword_destination_table
        
        ### URL Destination Table
        url_destination_table = self.url_destination_table
        
        ### Project ID
        project_id = self.project_id
        
        
        ## GSC Keyword Data ETL
        keyword_data.to_gbq(keyword_destination_table, project_id, if_exists='append')
        
        print('GSC Keyword Data ETL Complete')
        
        
        ## GSC URL Level Data ETL                
        url_data.to_gbq(url_destination_table, project_id, if_exists='append')

        print('GSC URL Data ETL Complete')

            
   
if __name__ == '__main__':
    
    
    ## Specify website you would like to crawl
    website = ''

    ## Specify Keyword Destination table
    keyword_destination_table = ''
    
    # GSC API Credentials
    credentials = ''
    
    # specify where you want your pickled file to live
    pickled_file_folder = ''
    
    ## Specify URL Destination table
    url_destination_table = ''
    
    
    ### Specify project id
    project_id = ''
    
    ## Specify what start date you want to pull data from
    start_date = ''
    
    ## Specify what end date you want to pull data from
    end_date = ''
    
    
    
    etl = gsc_etl(website,credentials, pickled_file_folder, start_date,end_date, project_id, url_destination_table, keyword_destination_table)

    etl.gbq_etl()
    print("Script Complete")
