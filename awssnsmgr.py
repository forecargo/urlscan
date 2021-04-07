import boto3
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

class SnsManager():
    arn = ""

    def __init__(self,arn):
        self.arn = arn
    def publishToSns(self,sub,msg):
        sns = boto3.client("sns")
        response = sns.publish(
                TopicArn=self.arn,
                Message=msg,
                Subject=sub
        )
        return response
    def pubNewUrlSanData(self,search_data,diff_list):
        sub = "[Notice] urlscan.io new URL"
        msg = """
            Notice urlscan.io new URL found
            -------------
            search:{search_string}
            -------------
            add URL
            {diff_data}

            end
        """.format(search_string=search_data,diff_data=diff_list)
        response = self.publishToSns(sub,msg)
        return response

    def pubNewUrlSanData2(self,search_data,diff_list):
        #smtpで送信する場合
        smtpobj = smtplib.SMTP('smtp.xxxxx.com', 587)
        #smtpobj = smtplib.SMTP('smtp.gmail.com', 587) #例：Gmailで送信する場合
        smtpobj.ehlo()
        smtpobj.starttls()
        smtpobj.ehlo()
        smtpobj.login('xxxxx@xxxxx.com', 'password') #送信元メールアドレス, パスワードを指定する

        #メッセージ本文作成
        msg = """
            Notice urlscan.io new URL found
            -------------
            search:{search_string}
            -------------
            add URL
        """.format(search_string=search_data)
        msg = msg + "\n"
        for add_url in diff_list:
            msg = msg + add_url + "\n"

        #msg = msg.replace(':', '[:]')
        #msg = msg.replace('.', '[.]')
        #msg = msg.replace('http', 'hxxp')
        to_addr = "xxxxx@xxxxx.com,xxxxx@xxxxx.com" #送信先アドレスをカンマ区切りで指定する

        msg = MIMEText(msg)
        msg['Subject'] = "[Notice] urlscan.io new URL"
        msg['From'] = 'xxxxx@xxxxx.com' #送信元アドレスを指定する
        msg['To'] = to_addr
        msg['Date'] = formatdate()

        #メールを送信
        sendToList = to_addr.split(',')
        response = smtpobj.sendmail('xxxxx@xxxxx.com', sendToList, msg.as_string()) #送信元アドレスを指定する
        smtpobj.close()
        return response
