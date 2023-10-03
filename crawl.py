import os
import json
import requests
from pprint import pprint
from datetime import datetime
from bs4 import BeautifulSoup


def crawl_dart_search(corp_name):
    url = "https://dart.fss.or.kr/dsae001/search.ax"
    data = {
        "currentPage": "1",
        "autoSearch": "true",
        "businessCode": "all",
        "textCrpNm": corp_name,
        "corporationType": "all",
    }
    res = requests.post(url, data=data)
    soup = BeautifulSoup(res.text, "html.parser")
    a_tags = soup.find_all("a")

    for a in a_tags:
        a_corpname = a.string.strip()
        if a_corpname == corp_name:
            return a.get("href").split("'")[1]


def crawl_dart_select(corp_code):
    url = "https://dart.fss.or.kr/dsae001/select.ax"
    data = {"selectKey": corp_code}
    res = requests.post(url, data=data)
    soup = BeautifulSoup(res.text, "html.parser")
    corp_reg_no = soup.find("th", string="법인등록번호").find_next("td").text.strip()
    return "".join(corp_reg_no.split("-"))


def get_bond_issu_info_service(corp_reg_no: str) -> list:
    KEY = os.environ.get("PYCON_DATA_TOKEN")
    DATE = datetime.now().strftime("%Y%m%d")
    url = (
        "http://apis.data.go.kr/1160100/service/GetBondIssuInfoService/getBondBasiInfo"
    )
    params = {
        "serviceKey": KEY,
        "numOfRows": "100",
        "pageNo": "1",
        "resultType": "json",
        "basDt": DATE,
        "crno": corp_reg_no,
        "bondIsurNm": "",
    }
    response = requests.get(url, params=params)
    json_string = json.loads(response.content.decode())
    return sorted(
        json_string["response"]["body"]["items"]["item"],
        key=lambda x: x["bondExprDt"],
        reverse=True,
    )


def crawl_krx(isinCd, isinCdNm):
    url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
    data = {
        "bld": "dbms/MDC/STAT/standard/MDCSTAT10901",
        "locale": "ko_KR",
        "tboxisuCd_finder_bondisu0_1": f"{isinCd}/{isinCdNm}",
        "isuCd": isinCd,
        "isuCd2": "",
        "codeNmisuCd_finder_bondisu0_1": isinCdNm,
        "param1isuCd_finder_bondisu0_1": "2",
    }
    res = requests.post(url, data=data)
    pprint(res.json()["output"])


def crawl_news(corp_name):
    url = f"https://www.teamblind.com/kr/company/{corp_name}/news"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    articles = soup.find_all("article")

    links = []
    for i in range(3):
        article = articles[i]
        url_div = article.find("div", class_="url")
        link = url_div.find("a")
        links.append(link.text)

    return links


if __name__ == "__main__":
    corp_name = input("회사명을 정확하게 입력해주세요: ")

    # 뉴스 크롤링
    links = crawl_news(corp_name)
    print("\n".join(links))

    corp_code = crawl_dart_search(corp_name)
    corp_reg_no = crawl_dart_select(corp_code)
    print(corp_name, corp_reg_no)
    bond_list = get_bond_issu_info_service(corp_reg_no)

    for i, bond in enumerate(bond_list):
        print(f"{i+1}.", bond["isinCd"], bond["isinCdNm"])
    select_number = int(input("조회하고자 하는 채권 번호를 입력해주세요: "))
    selected_bond = bond_list[select_number + 1]
    # print(selected_bond)
    res = crawl_krx(selected_bond["isinCd"], selected_bond["isinCdNm"])
    print(res)
