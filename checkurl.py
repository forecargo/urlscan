import urlscanclient
import awssnsmgr
import datetime
import json
import pprint

api_key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# query:検索文字列 path:URLを記録するファイル arn:SNS発行用
#query="#asn:\"AS46664\""
query0="#asn:"
#path="url-list.txt"
path0="url-list"
arn="arn:aws:sns:ap-northeast-1:xxxxxxxxxxxxxxxxx"  #AWSで取得したarnを指定する
# クライアントとマネージャーの生成
usc = urlscanclient.UrlScanClient(api_key)
#chkmgr = urlscanclient.CheckFileDiffManager(path)
snsmgr = awssnsmgr.SnsManager(arn)

listnames = json.load(open('query-list.json'))

for listname in listnames:

    now = datetime.datetime.now()
    print(listname[0] + " start " + now.strftime('%Y-%m-%d %H:%M:%S'))

    query = query0 + "\"" + listname[0] + "\""
    path = path0 + "-" + listname[0] + ".txt"

    chkmgr = urlscanclient.CheckFileDiffManager(path)

    # データの取得
    response = usc.searchApi(query)
    url_list = usc.parseTaskUrl_uniq(response)
    # データの比較
    FLG = chkmgr.checkNewListFromFile(url_list)

    # SNS通知
    if FLG :
        print("Get New list")
        match_list = []
        FLG = chkmgr.getMatchDiffList(match_list)
        if FLG :
            print("match list")
            #snsmgr.pubNewUrlSanData(query,match_list)  #AWSSNSでアラートを通知する場合
            snsmgr.pubNewUrlSanData2(query,match_list)  #SMTPでアラートを通知する場合
        else:
            print("No match list")
    else:
        print("No new list")

    now = datetime.datetime.now()
    print(listname[0] + " end " + now.strftime('%Y-%m-%d %H:%M:%S'))

exit()
