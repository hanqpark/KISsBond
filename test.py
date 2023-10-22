import boto3


dynamodb = boto3.client("dynamodb")
table_name = "pycon_bond"

# 테이블의 상세 정보 조회
response = dynamodb.describe_table(TableName=table_name)

# 스키마 정보 가져오기
table_schema = response["Table"]["KeySchema"]

# 파티션 키와 정렬 키 출력
for key in table_schema:
    print(f"Key Name: {key['AttributeName']}, Key Type: {key['KeyType']}")
