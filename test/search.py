from bs4 import BeautifulSoup
import requests

keyword = "삼성전자"
url = "https://search.naver.com/search.naver?"
params = {"where": "nexearch", "fbm": "1", "query": keyword}

resp = requests.get(url, params)
soup = BeautifulSoup(resp.content, "lxml")
content_list = soup.select("div.tit")

print(content_list)
