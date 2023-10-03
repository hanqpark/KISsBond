import json
import requests
from pprint import pprint
from bs4 import BeautifulSoup


url = "https://dart.fss.or.kr/dsae001/search.ax"
data = {
    "currentPage": "5",
    "autoSearch": "true",
    "businessCode": "all",
    "textCrpNm": "삼성",
    "corporationType": "all",
}

res = requests.post(url, data=data)
soup = BeautifulSoup(res.text, "html.parser")
print(soup)
