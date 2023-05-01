from pymongo import MongoClient
client = MongoClient('localhost', 27017)  # mongoDB는 27017 포트로 돌아갑니다.
db = client.sms  # 'dbsparta'라는 이름의 db를 사용합니다. 'dbsparta' db가 없다면 새로 만듭니다.

# MongoDB에서 데이터 모두 보기
all_users = list(db.collection.find({}))

print(all_users[0])  # 0번째 결과값을 보기
print(all_users[0]['phone_number'])  # 0번째 결과값의 'name'을 보기

# delete_data = {'phone_number': '01030125625'}
# db.collection.delete_one(delete_data)
