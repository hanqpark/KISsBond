import json
import requests
from pprint import pprint
from datetime import datetime


def get_bond_issu_info_service(KEY):
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
        "crno": "1101112762668",
        "bondIsurNm": "푸본현대생명보험",
    }
    return requests.get(url, params=params)


if __name__ == "__main__":
    KEY = "R5Kw0NfB8F8EiNpnGWIy061bCZX5MHKeW69uA54r/Gw/q8kLgVaqWMV5bUpGG8xXH1fxIe3r4M+hoKU/U11WLQ=="
    response = get_bond_issu_info_service(KEY)
    json_string = json.loads(response.content.decode())
    pprint(json_string)
