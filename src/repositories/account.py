from models import Account
import uuid
import hashlib
from server import bcrypt

class AccountRepository:
    @staticmethod
    def logIn(user_name, password):
        user=Account.query.filter_by(user_name=user_name).first()
        if user:
            if(bcrypt.check_password_hash(user.password, password)):
                return user

    @staticmethod
    def getAll():
        return Account.query.all()

    @staticmethod
    def update(self, user_name, password):
        account = self.get(uid)
        account.user_name = user_name
        account.password = password

        return account.save()

    @staticmethod
    def create(user_name, password):
        account = Account(uid=str(uuid.uuid4()), user_name=user_name, password=bcrypt.generate_password_hash(password).decode("utf-8"))

        return account.save()
