from cryptography.fernet import Fernet
import base64
import os

def encrypt_token(token: str) -> str:
    key = os.getenv("ENCRYPTION_KEY").encode()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    key = os.getenv("ENCRYPTION_KEY").encode()
    fernet = Fernet(base64.urlsafe_b64encode(key))
    return fernet.decrypt(encrypted_token.encode()).decode()
