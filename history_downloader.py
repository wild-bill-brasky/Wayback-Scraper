from random import randrange
from datetime import datetime
from datetime import timedelta
import requests, trafilatura, re, os, time
"""
https://github.com/proxifly/free-proxy-list/tree/main?tab=readme-ov-file
"""
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
    
    def get_https_prox(self):
        resp = requests.get('https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/https/data.txt', verify=True).text.split('\n')
        for i in range(0, len(resp)):
            index = randrange(0, len(resp))
            self.https_proxy_list.append(resp[index])
        print('New HTTPS proxy list generated')
        return
    
    def build_proxy_obj(self):
        http_proxy_index = randrange(0, len(self.http_proxy_list))
        https_proxy_index = randrange(0, len(self.https_proxy_list))
        proxies = {
            'http' : self.http_proxy_list[http_proxy_index],
            #'https': self.https_proxy_list[https_proxy_index]
        }
        print(f'{get_params.http_proxy_list[http_proxy_index]} & {get_params.https_proxy_list[https_proxy_index]}')
        return proxies

class NetOps():

    def __init__(self):
        self.base_url = f'https://www.cisa.gov/news-events/cybersecurity-advisories?page={self.page_num}' #https://www.cisa.gov/known-exploited-vulnerabilities-catalog - Another good source
        self.punc_reg = r'[^\w\s]'
        self.urlpat = r'href=[\'"]?([^\'" >]+)'
        self.flat_data = None
        self.page_urls = None
        self.page_num = 0
        
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
    
    def result_parse(self, result):
        clean_data = []
        for i in result:
            i = i.lower()
            if 'url:' in i or 'date:' in i:
                clean_data.append(f'{i} ')
            elif 'https://' in i:
                i = i.replace('[', '').replace(']', '').replace(')', '').replace('(', '').replace('→', '')
                clean_data.append(f'{i} ')
            else:
                i = re.sub(self.punc_reg, '', i) # Uses regex to clean data of any punctuation
                clean_data.append(f'{i} ')
        self.flat_data = ' '.join(clean_data)
        self.file_writer(self.flat_data)
        return
    
    def iterator(self):
        for i in range(1,11): # It all starts here dawg
            try:
                main_page = self.get_resp(self.base_url)
                self.page_num = self.page_num+1
                self.page_urls = re.findall(self.urlpat, main_page)
            except Exception as e:
                print(f'Error with stuff: {e}')
                continue
        return

    def url_iterator(self):
        for j in self.page_urls:
            if 'https://' not in j:
                j = f'https://{j}'
            article = self.get_resp(j)
            self.traf_func(article)
        return

    def file_writer(self, clean_data):
        with open(f'{os.getcwd()}/bleeping_computer/bleeping_computer_{self.get_true()}.txt', 'w', encoding='utf-8') as file:
            file.write(clean_data)
        print(f'{self.get_true()} processing completed.')
        return
    
    def file_check(self): # Picks back up where you left off if scraping is interrupted
        if os.path.exists(f'{os.getcwd()}/bleeping_computer/bleeping_computer_{self.get_true()}.txt'):
            return True
        else:
            return False

    def get_time(self):
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def logging(self, error):
        log_time = self.get_time()
        with open('hist_dl.log', 'a') as alert_file:
            alert_file.write(f'{log_time}:{error}\n')
        return
        
if __name__ == '__main__':
    get_params = GetParams()
    get_params.get_http_prox()
    net_ops = NetOps()
    net_ops.iterator()