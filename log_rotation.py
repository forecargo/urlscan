import glob
import subprocess
from datetime import datetime, date, timedelta

baseday = datetime.today()
tgtday = datetime.strftime(baseday - timedelta(days=3), '%Y%m%d')
today = datetime.strftime(baseday, '%Y%m%d')

cmd = 'cp checkurl.log checkurl.log' + today
result = subprocess.run(cmd, shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

cmd = 'rm checkurl.log'
result = subprocess.run(cmd, shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

cmd = 'rm checkurl.log' + tgtday
result = subprocess.run(cmd, shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

cmd = 'rm url-list-AS' + '*.txt' + tgtday + '*'
result = subprocess.run(cmd, shell=True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
