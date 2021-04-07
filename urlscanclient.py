import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import json
import datetime
from bs4 import BeautifulSoup
import re
import tldextract
import cchardet

class UrlScanClient():
    api = ""
    submission_url = "https://urlscan.io/api/v1/scan/"
    result_url = "https://urlscan.io/api/v1/result/"
    search_url = "https://urlscan.io/api/v1/search/"

    def __init__(self,api_key):
        self.api = api_key

    def checkApiKey(self):
        if(self.api):
            return True
        else:
            return False
    def submissionApi(self,check_url):
        if not self.checkApiKey():
            raise Exception("Error! Not set API-KEY")
        headers = {'API-Key': self.api ,'Content-Type':'application/json'}
        data = {"url": check_url, "visibility": "public"}
        response = requests.post(self.submission_url,headers=headers, data=json.dumps(data))
        return response
    def resultApi(self,uuid):
        headers = {'Content-Type':'application/json'}
        check_url = self.result_url + uuid + "/"
        response = requests.get(check_url,headers=headers)
        return response
    def searchApi(self,query,size=1000,search_after=None):
        headers = {'API-Key': self.api ,'Content-Type':'application/json'}
        if search_after:
            payload = {'q' : query , 'size' : size , 'search_after' : search_after}
        else:
            payload = {'q' : query , 'size' : size }
        response = requests.get(self.search_url, headers=headers,params=payload)
        return response
    def parseTaskUrl_uniq(self,response):
        url_list = []
        jsondata = response.json()
        for jdata in jsondata["results"]:
            url_list.append(jdata["task"]["url"])
        return list(set(url_list))

class CheckFileDiffManager():
    path = ""
    diff_list = []
    diff_FLG = False

    filenotfound_FLG = False

    def __init__(self,path):
        self.path = path

    def checkNewListFromFile(self,check_list):
        try:
            #print(self.path)
            with open(self.path,mode='r') as f:
                before_list = f.read().splitlines()
        except FileNotFoundError as e:
            before_list = []
            self.filenotfound_FLG = True
        check_list.sort()
        before_list.sort()
        self.diff_list = list(set(check_list) - set(before_list))
        if (len(self.diff_list) != 0 ):
            dt_now = datetime.datetime.now()
            rireki_path = self.path + dt_now.strftime('%Y%m%d%H%M%S')
            with open(rireki_path,mode='w') as f:
                f.write('\n'.join(check_list))
            with open(self.path,mode='w') as f:
                f.write('\n'.join(check_list))
            self.diff_FLG = True
            if self.filenotfound_FLG:
                # 比較するファイルがない場合はdiff_FLGをFalseにする
                self.diff_FLG = False
            return self.diff_FLG
        else:
            #print("diff 0")
            self.diff_FLG = False
            return self.diff_FLG
    def getDiffList(self):
        return self.diff_list
    def getMatchDiffList(self,match_list):
        match_FLG = False
        whitelists = json.load(open('white-list.json'))
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/83.0.4103.88 Mobile/15E148 Safari/604.1'}   #UAを指定する
        urllib3.disable_warnings(InsecureRequestWarning)
        for diff_url in self.diff_list:
            #print(diff_url)
            diff_domain = tldextract.extract(diff_url)
            diff_domain = diff_domain.domain+"."+diff_domain.suffix
            #print(diff_domain)
            white_FLG = False
            for whitelist in whitelists:
                if diff_domain == whitelist[0]:
                    white_FLG = True
                    #print("whitelist match")
            if white_FLG:
                pass
            else:
                match_url = re.search('.+\.(csv|pdf|zip|exe|xls|xlsm|xlsx|doc|docm|docx|apk|iso)',diff_url)
                if match_url is None:
                    try:
                        notice_url = re.search('(ドメインキーワード１|ドメインキーワード２)',diff_url)
                        if notice_url is None:
                            pass
                        else:
                            match_FLG = True
                            print(diff_url)
                            replace_url = diff_url
                            replace_url = replace_url.replace(':', '[:]')
                            replace_url = replace_url.replace('.', '[.]')
                            replace_url = replace_url.replace('http', 'hxxp')
                            match_list.append(replace_url)

                        reshead = requests.head(diff_url,headers=headers,verify=False,timeout=3)
                        #print(reshead.headers['content-type'])
                        #if int(reshead.headers['Content-Length']) < 10485760:
                        if "text" in reshead.headers['Content-Type']:
                            html = requests.get(diff_url,headers=headers,verify=False,timeout=5)
                            #print(html.status_code)
                            if html.status_code == 200:
                                try:
                                    html.encoding = cchardet.detect(html.content)["encoding"]
                                    match_keyword = re.search('(キーワード１|キーワード２|キーワード３|キーワード４)',html.text,flags=re.IGNORECASE)    #自社WEBサイトに適したキーワードを指定する
                                    if match_keyword is None:
                                        pass
                                    else:
                                        if notice_url is None:
                                            match_FLG = True
                                            replace_url = diff_url
                                            replace_url = replace_url.replace(':', '[:]')
                                            replace_url = replace_url.replace('.', '[.]')
                                            replace_url = replace_url.replace('http', 'hxxp')
                                            match_list.append(replace_url)

                                        soup = BeautifulSoup(html.text, "html.parser")

                                        if hasattr(soup, "string" ):
                                            print(diff_url)
                                            print(match_keyword)
                                            match_list.append(str(match_keyword))
                                            if soup.title.string is None:
                                                print("Title None")
                                                match_list.append(">>Title>>None")
                                            else:
                                                print(soup.title.string)
                                                match_list.append(">>Title>>" + soup.title.string)
                                        else:
                                            match_list.append(">>>>nothing")
                                except Exception as e:
                                    print(e)
                                    pass
                        else:
                            #print("Content-Type Error")
                            pass
                    except Exception as e:
                        #print(e)
                        pass
        return match_FLG
