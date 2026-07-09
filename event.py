import redis
import json

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

user_id = "123"
user_name = "Tao ko có tên"

r.rpush(
    "user_queue",
    json.dumps({
        "user_id": user_id,
        "user_name": user_name
    })
)

print("đã thêm user và đẩy message đến agent...")