import hashlib

def hash_secret(secret):
    return hashlib.sha256(secret.encode()).hexdigest()