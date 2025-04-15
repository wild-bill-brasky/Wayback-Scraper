import os
from datetime import datetime

class SourceMeta:
    cisa_advise = {'url_strings': ['news-events/alerts', 'news-events/ics-advisories/', '/news-events/analysis-reports'], 
                   'base_url': 'https://www.cisa.gov/news-events/cybersecurity-advisories?page=',
                   'url_prefix': 'https://www.cisa.gov',
                   'home_dir': f'{os.getcwd()}/cisa_advisories/{datetime.today().strftime('%Y_%m_%d')}'
                   }
    
    bleeping_comp = {'url_strings': ['/tutorials/', '/news/''/virus-removal/', '/guides/'],
                     'base_url': 'https://www.bleepingcomputer.com/page/',
                     'url_prefix': 'https://bleepingcomputer.com',
                     'home_dir': f'{os.getcwd()}/bleeping_computer/{datetime.today().strftime('%Y_%m_%d')}'
                     }
    
class PrintInfo:
    def __init__(self, source):
        self.source = source

    def print_shit(self):
        print(self.source['url_strings'])  # Access the 'url_strings' key

def call_stuff():
    printinfo = PrintInfo(SourceMeta.cisa_advise)  # Pass the source dictionary
    printinfo.print_shit()  # Call the method correctly

call_stuff()