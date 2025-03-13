from cryptography.fernet import Fernet
from src.config import ENCRYPTION_KEY
import base64


def encrypt_token(token: str) -> str:
    key = ENCRYPTION_KEY.encode()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    key = ENCRYPTION_KEY.encode()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    return fernet.decrypt(encrypted_token.encode()).decode()
