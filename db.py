import time
import boto3
from crawl import *
from boto3.dynamodb.conditions import Key

# DynamoDB 테이블 객체 생성
table = boto3.resource("dynamodb").Table("pycon_bond")


def write_db(bond_list: list) -> None:
    for i, bond in enumerate(bond_list):
        table.put_item(TableName="pycon_bond", Item=bond)
        if not (i + 1) % 5:
            time.sleep(1)


def read_bond_list(corp_name: str) -> list:
    res = table.query(
        KeyConditionExpression=Key("bondIsurNm").eq(corp_name),
        ProjectionExpression="isinCdNm",
    )
    return [bond["isinCdNm"] for bond in res["Items"]]


def read_bond_info(corp_name: str, bond_name: str) -> dict:
    key = {"bondIsurNm": corp_name, "isinCdNm": bond_name}
    return table.get_item(Key=key)["Item"]


if __name__ == "__main__":
    corp_name = input("회사명: ")
    # corp_code = crawl_dart_search(corp_name)
    # corp_reg_no = crawl_dart_select(corp_code)
    # bond_list = get_bond_issu_info_service(corp_reg_no)

    # write_db(bond_list)

    print(read_bond_list(corp_name))

    bond_name = input("채권명: ")
    res_bond = read_bond_info(corp_name, bond_name)
    print(res_bond)
