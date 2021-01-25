from getpass import getpass
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

"""
Stores username and encrypted password
"""
class Credentials:
    def __init__(self):
        self.username = input("Enter username: ")
        self.fernet = Fernet(Fernet.generate_key())
        self.password = self.fernet.encrypt(bytes(getpass(prompt="Password: ").encode('utf-8')))
        self.token = self.fernet.encrypt(bytes(getpass(prompt="Token: ").encode('utf-8')))

    def get_username(self):
        return self.username

    def get_password(self):
        return self.fernet.decrypt(self.password).decode('utf-8')

    def get_token(self):
        return self.fernet.decrypt(self.token).decode('utf-8')
