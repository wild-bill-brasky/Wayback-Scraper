from random import randrange
from datetime import datetime
import requests, trafilatura, re, os, time
"""
https://github.com/proxifly/free-proxy-list/tree/main?tab=readme-ov-file
{datetime.today().strftime('%Y_%m_%d')}
"""

class SourceMeta: # This class is used to store objects in dictionaries specific to individual websites - These are called in the NetOps class
    cisa_advise = {'url_strings': ['news-events/alerts', 'news-events/ics-advisories/', '/news-events/analysis-reports'], 
                   'base_url': 'https://www.cisa.gov/news-events/cybersecurity-advisories?page=',
                   'url_prefix': 'https://www.cisa.gov',
                   'home_dir': 'cisa_advisories'
                   }
    
    bleeping_comp = {'url_strings': ['/tutorials/', '/news/''/virus-removal/', '/guides/'],
                     'base_url': 'https://www.bleepingcomputer.com/page/',
                     'url_prefix': 'https://bleepingcomputer.com',
                     'home_dir': 'bleeping_computer'
                     }
    
    the_register = {'url_strings': ['/2025/'], # NEEDS ATTENTION Uses the days date in MM/DD numeric format eg /2025/04/07/asia_tech_news_in_brief/ - use date substraction equation from wayback downloader script
                     'base_url': 'https://www.theregister.com/earlier/', #Increases linearly from 1 eg https://www.theregister.com/earlier/1/
                     'url_prefix': 'https://www.theregister.com/',
                     'home_dir': 'the_register'
                     }
    
    dark_reading = {'url_strings': ['/cyberattacks-data-breaches/', '/threat-intelligence/', '/vulnerabilities-threats/', '/cloud-security/',
                                    '/endpoint-security/', '/cybersecurity-operations/', 'application-security'], 
                     'base_url': 'https://www.darkreading.com/latest-news?page=', 
                     'url_prefix': 'https://www.darkreading.com/',
                     'home_dir': 'dark_reading'
                     }
    
class GetParams():
        
    def __init__(self): # Pick random agents for get request
        self.user_agents = [
            'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:64.0) Gecko/20100101 Firefox/64.0',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)']
        self.http_proxy_list = []
        self.https_proxy_list = []
        self.headers = None
    
    def change_agents(self):
        agent_index = randrange(0, len(self.user_agents))
        self.headers = {"user-agent": f"{self.user_agents[agent_index]}"}
        return self.headers
    
    def get_http_prox(self): # Pulls from an actively maintained proxy list and selects random proxy servers to for get request in the NetOps class
        resp = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt', verify=True).text.split('\n')
        for i in range(0,101):
            index = randrange(0, len(resp))
            self.http_proxy_list.append(resp[index])
        print('New HTTP proxy list generated')
        self.get_https_prox()
        return
    
    def get_https_prox(self): # Pulls from same source as above function, except it's a much shorter list for HTTPS proxies
        resp = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/https/data.txt', verify=True).text.split('\n')
        for i in range(0, len(resp)):
            index = randrange(0, len(resp))
            self.https_proxy_list.append(resp[index])
        print('New HTTPS proxy list generated')
        return
    
    def build_proxy_obj(self): # Builds proxy object to be used in GET requests in the NetOps class
        http_proxy_index = randrange(0, len(self.http_proxy_list))
        https_proxy_index = randrange(0, len(self.https_proxy_list))
        proxies = {
            'http' : self.http_proxy_list[http_proxy_index],
            'https': self.https_proxy_list[https_proxy_index]
        }
        print(f'{get_params.http_proxy_list[http_proxy_index]} & {get_params.https_proxy_list[https_proxy_index]}')
        return proxies

class NetOps():

    def __init__(self, source):
        self.punc_reg = r'[\.\?\!]{2,}' #r'[^\w\s]' Uncommented regex removes duplicate characters eg !! .. - Commented regex removes all punctuation and is aggressive AF.
        self.urlpat = r'href="([^"]*)"' #r'<a\s+href=["\'](.*?)["\']'
        self.flat_data = None
        self.page_urls = []
        self.file_name = None
        self.page_num = 1
        self.source = source
        
    def get_resp(self, url):
        try:
            return requests.get(url, verify=True, timeout=60, proxies=get_params.build_proxy_obj(), headers=get_params.change_agents()).text
        except Exception as e:
            print(f'Error with GET request to {url}: {e}')
    
    def traf_func(self, downloaded):
        try:
            return trafilatura.extract(downloaded, with_metadata=True, deduplicate=True, include_tables=True, include_comments=True, include_links=False).split('\n')
        except Exception as e:
            print(f'Error with response object: {e}')
        
    def iterator(self):
        for i in range(0,100): # It all starts here dawg
            try:
                time.sleep(1)
                main_page = self.get_resp(f'{self.source['base_url']}{str(self.page_num)}') # Concatenates base url and incrementally increasing page number
                print(f'{self.source['base_url']}{str(self.page_num)}')
                self.page_num=self.page_num+1
                self.url_rip(main_page)
                print(f'{len(self.page_urls)} Articles Extracted')
                self.url_iterator()
                self.page_urls.clear() # Clear scraped urls object for next iteration
            except Exception as e:
                print(f'Error with stuff: {e}')
                continue
        return
        
    def url_iterator(self):
        for j in self.page_urls:
            self.file_name = self.filename_creator(j, 4)
            if self.file_check():
                print(f'{self.file_name} - File already exists')
                continue
            time.sleep(2)
            article = self.get_resp(j)
            extracted_article = self.traf_func(article)
            self.result_parse(extracted_article)
        return
    
    def url_rip(self, main_page):
        for m in re.findall(self.urlpat, main_page): # Add if else condition for regex url matches that already have the base url
            for i in self.source['url_strings']:
                if i in m:
                    m = f'{self.source['url_prefix']}{m}'
                    self.page_urls.append(m)
                else:
                    continue
        return
    
    def result_parse(self, result):
        clean_data = []
        for i in result:
            i = i.strip() # Add .lower() method to remove capitaliztion, however current LLM documentation states keeping caps is useful to establish context and acronyms for RAG
            if 'date:' in i:
                clean_data.append(f'{i}')
            elif "---" in i: # Consider removal or specifying CISA Advisories
                continue
            else:
                i = i.replace("®", "").replace("©", "").replace("™", "").replace("—", "").replace("— ", "").replace('-', '').replace('- ', '')
                i = re.sub(self.punc_reg, '', i) # Uses regex to clean data of any punctuation
                clean_data.append(f'{i}')
        self.flat_data = '\n'.join(clean_data).strip() # Join all items in list with a newline separator to give LLM more context
        self.file_writer(self.flat_data)
        return
    
    def filename_creator(self, url, space):
        url = url.split('/')[-space:]
        return '_'.join(url)

    def file_writer(self, clean_data): # Write that shit to a txt file for future embedding and vectorizing operations
        with open(f'{os.getcwd()}/{self.source['home_dir']}/{self.file_name}.txt', 'w', encoding='utf-8') as file:
            file.write(clean_data)
        print(f'{self.file_name} processing completed.')
        return
    
    def file_check(self): # Picks back up where you left off if scraping is interrupted
        if os.path.exists(f'{os.getcwd()}/{self.source['home_dir']}/{self.file_name}.txt'):
            return True
        else:
            return False

    def get_time(self):
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def logging(self, error): # A logging function I'll never use
        log_time = self.get_time()
        with open('hist_dl.log', 'a') as alert_file:
            alert_file.write(f'{log_time}:{error}\n')
        return
        
if __name__ == '__main__':
    get_params = GetParams()
    get_params.get_http_prox()
    net_ops = NetOps(SourceMeta.cisa_advise) # Change the object passed to NetOps to change the website that is targeted
    net_ops.iterator()