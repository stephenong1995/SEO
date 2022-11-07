import pickle
import pandas as pd 
import os

from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from apiclient.discovery import build



class screaming_frog_etl:

    def __init__(self,website, output_folder,sf_destination_table, project_id):

        self.website = website
        self.output_folder = output_folder
        self.sf_destination_table = sf_destination_table
        self.project_id = project_id
        
    def sf_crawl(self):
        website = self.website
        output_folder = self.output_folder
        sf_command = os.system('cd "C:\Program Files (x86)\Screaming Frog SEO Spider" && ScreamingFrogSEOSpiderCli.exe --crawl {} --headless --output-folder {} --export-tabs "Internal:All"'\
            .format(website,output_folder))
        df = pd.read_csv(output_folder + '\internal_all.csv')
        
        return df 
        
    # ETL Method 
    def sf(self):
        
        ### run crawl
        sf_crawl = self.sf_crawl()
        
        sf_crawl.columns = sf_crawl.columns.str.replace(' ', '_')
        
        ### screaming frog Destination Table
        sf_destination_table = self.sf_destination_table
                
        ### Project ID
        project_id = self.project_id
        
        
        ## Screaming Frog Crawl ETL
        sf_crawl.to_gbq(sf_destination_table, project_id, if_exists='append')
        
        print('SF Crawl Complete')
        
        
if __name__ == '__main__':
    
    
    ## Specify website you would like to crawl
    website = ''

    ## Specify Destination table
    sf_destination_table = ''
    
    # Add your Project Id
    project_id = ''
    
    
    ## Add in the folder you would like your crawl exported to 
    output_folder = ''

    
    
    etl = screaming_frog_etl(website, output_folder,sf_destination_table, project_id)

    etl.sf()
    print("Scipt Complete")   
