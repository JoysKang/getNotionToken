import base64
from util import AESCipher, load_json

import requests
from bottle import route, run, request
import sentry_sdk
from sentry_sdk.integrations.bottle import BottleIntegration


conf = load_json("./conf.json")
CLIENT_ID = conf.get("client_id")
CLIENT_SECRET = conf.get("client_secret")
REDIRECT_URI = conf.get("redirect_uri")
AES = AESCipher(conf.get("key"))

sentry_sdk.init(
    dsn=conf.get("sentry_address"),
    integrations=[BottleIntegration()]
)


@route('/address', methods=['GET'])
def get_address():
    """获取地址"""
    address = "https://api.notion.com/v1/oauth/authorize?owner=user" \
              f"&client_id={CLIENT_ID}" \
              f"&redirect_uri={REDIRECT_URI}" \
              "&response_type=code"
    if state := request.GET.get("state", ""):
        state = AES.encrypt(state)  # 加密
        address += f"&state={state}"

    return {"message": "Success", "address": address}


@route('/auth', methods=['GET'])
def auth():
    """授权回调"""
    # 向 https://api.notion.com/v1/oauth/token 发起请求
    code = request.GET.get("code", "")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    authorization = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode("utf-8")).decode("utf-8")
    headers = {
        'content-type': 'application/json',
        'Authorization': f'Basic {authorization}'
    }
    result = requests.post('https://api.notion.com/v1/oauth/token', json=data, headers=headers)
    if result.status_code != 200:
        return {"message": "Failure"}

    json_data = result.json()
    access_token = json_data.get('access_token')
    state = request.GET.get("state", "")
    if state:
        state = AES.decrypt(state)  # 解密

    return {"message": "Success", "access_token": access_token, "state": state}


@route('/', methods=['GET'])
def root():
    return {"message": "Success"}


if __name__ == "__main__":
    run(host='0.0.0.0', port=9000)
