import json
import requests
from pprint import pprint


url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
data = {
    "bld": "dbms/MDC/STAT/standard/MDCSTAT10901",
    "locale": "ko_KR",
    "tboxisuCd_finder_bondisu0_1": "KR6086951D65/푸본현대생명보험24(후)",
    "isuCd": "KR6086951D65",
    "isuCd2": "",
    "codeNmisuCd_finder_bondisu0_1": "푸본현대생명보험24(후)",
    "param1isuCd_finder_bondisu0_1": "2",
}

res = requests.post(url, data=data)
pprint(res.json()["output"])
