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
        self.base_url = 'https://web.archive.org/web/var_date000000/https://www.bleepingcomputer.com/' #Archive url
        self.punc_reg = r'[^\w\s]'
        self.response = None
        self.working_date = None
        self.var_date = None
        self.flat_data = None
        self.fail_list = []
        
    def get_resp(self, url):
        try:
            return requests.get(url, verify=True, timeout=60, proxies=get_params.build_proxy_obj(), headers=get_params.change_agents()).text
        except Exception as e:
            print(f'Error with GET request to {url}: {e}')
            self.fail_list.append(url)
            print(f'Added {url} to fail list')
            self.reset()

    def reset(self):
        print('Starting over...')
        time.sleep(5)
        self.iterator()
        return
    
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
    
    def date_creator(self, num_days):
        self.var_date = datetime.today() - timedelta(days=num_days) # Subtracts number of days counted by for loop in below function)
        return self.var_date.strftime('%Y%m%d')
    
    def file_writer(self, clean_data):
        with open(f'{os.getcwd()}/bleeping_computer/bleeping_computer_{self.get_true()}.txt', 'w', encoding='utf-8') as file:
            file.write(clean_data)
        print(f'{self.get_true()} processing completed.')
        return
    
    def iterator(self):
        for i in range(1,366): # Number of days to look back
            try:
                self.working_date = self.date_creator(i)
                if self.file_check():
                    continue
                else:
                    time.sleep(2)
                    new_url = self.base_url.replace('var_date', self.working_date)
                    if new_url in self.fail_list:
                        continue
                    self.response = self.get_resp(new_url)
                    self.result_parse(self.traf_func(self.response))
            except Exception as e:
                print(f'Error with stuff: {e}')
                continue
        return
    
    def file_check(self): # Picks back up where you left off if scraping is interrupted
        if os.path.exists(f'{os.getcwd()}/bleeping_computer/bleeping_computer_{self.get_true()}.txt'):
            return True
        else:
            return False
        
    def get_true(self):
        true_date = self.var_date - timedelta(days=1) #Requests to Wayback return a date 1 day later than requested in the Get request for some fucking reason
        return true_date.strftime('%Y%m%d')

    def get_time(self):
        return datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    
    def logging(self, error):
        log_time = self.get_time()
        with open('wayback.log', 'a') as alert_file:
            alert_file.write(f'{log_time}:{error}\n')
        return
        
if __name__ == '__main__':
    get_params = GetParams()
    get_params.get_http_prox()
    net_ops = NetOps()
    net_ops.iterator()