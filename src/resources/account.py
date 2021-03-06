from flask.json import jsonify
from flask_restful import Resource
from flask_restful.reqparse import Argument
from repositories import AccountRepository
from util import parse_params
from flask import request
import jwt
import config
from repositories import CodeAuthRepository
import http.client
from numpy import random
import bcrypt
import datetime
class AccountResourceAuth(Resource):

    @staticmethod
    def post():
        if request.is_json:
            data = request.get_json()
            account = AccountRepository.logIn(user_name=data['user_name'], password=data['password'])
            if account:
                return {
                        "message":"Login successfully",
                        "data":{
                            "account":{
                                "uid":account.uid,
                                "user_name":account.user_name
                            },
                            "token":account.encode_auth_token(account.uid)
                        },
                        "status":200
                        }
            else:
                return {"message": "Username or password does not exists", "status": 400}
        else:
            return {"error": "The request failed"}


    @staticmethod
    def get():
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                auth_token = auth_header.split(" ")[1]
            else:
                auth_token = ''
            if auth_token:
                try:
                    payload=jwt.decode(auth_token, "secret",algorithms="HS256")
                    resp=payload['sub']
                except jwt.ExpiredSignatureError:
                    return {"message": "Signature expired. Please log in again.", "status": 400}
                except jwt.InvalidTokenError:
                    return {"message": "Invalid token. Please log in again.", "status": 400}
            accounts = AccountRepository.getAll()
            results= [
                {
                "uid": account.uid,
                "user_name": account.user_name,
                } for account in accounts]
        except Exception as e:
            print(e)
            return {"message": "No account found", "status": 400}
        return ({"accounts": results, "status": 200})

class AccountResourceUnAuth(Resource):

    @staticmethod
    def post():
        if request.is_json:
            data = request.get_json()
            accounts=AccountRepository.getAll()
            for user in accounts:
                if data['user_name']==user.user_name:
                    return {"message": f"Username {data['user_name']} already exists.", "status": 400}
            account = AccountRepository.create(user_name=data["user_name"], password=data['password'])
            auth_token=account.encode_auth_token(account.uid)
            print(auth_token)
            return {"message": f"Account {account.user_name} has been registered successfully.","auth_token": auth_token,"status": 200}
        else:
            return {"error": "The request payload is not in JSON format"}

class AccountResourceSendCode(Resource):

    @staticmethod
    def post():
        if request.is_json:
            data = request.get_json()
            email=data['email']
            conn = http.client.HTTPSConnection("api.mailgun.net")
            code_rand=random.randint(999999)
            payload = "from=mailgun@sandboxbb982a75ac924997852a2e52acf7ad6b.mailgun.org&to={}&subject=Code authentication&text=Code authentication: \n{}".format(email, code_rand)
            headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic YXBpOjM3N2U0ZWEwZjc2N2MyMzhlOTdlZGRkZjYwMzAxMzhkLTZlMGZkM2E0LTg2OWVmZmYy'
            }
            try:
                conn.request("POST", "/v3/sandboxbb982a75ac924997852a2e52acf7ad6b.mailgun.org/messages", payload, headers)
                code = CodeAuthRepository.create(code=code_rand, email=email)
                res = conn.getresponse()
                data = res.read()
                if(code):
                    return {"message":"Send code success", "data": data.decode("utf8")}
                else:
                    return {"message": "Send code failed"}
            except:
                return {"error": "The request failed"}
        else:
            return {"error": "The request payload is not in JSON format"}


class AccountResourceResetPassword(Resource):
     @staticmethod
     def put():
            try:
                if request.is_json:
                    data=request.get_json()
                    codes_auth=CodeAuthRepository.getAll()
                    for code_auth in codes_auth:
                        if(code_auth.code == data['code']):
                            try:
                                if(data['user_name'] == code_auth.email):
                                            user=AccountRepository.getUserByEmail(data['user_name'])
                                            account = AccountRepository.update(uid=user.uid, password=data['new_password'])
                                            if account.uid:
                                                return {"message": "Update success"}
                                            else:
                                                return {"message": "Update failed", "status": 400}
                            except Exception as e:
                                print(e)
                    return {"message": "Code authentication invalid", "status": 400}
            except Exception as e:
                return {"error": e}