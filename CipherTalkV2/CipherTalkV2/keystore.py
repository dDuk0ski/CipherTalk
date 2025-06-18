import os

class KeyStore:
    @staticmethod
    def seal(name: str, data: str):
        path = os.path.expanduser(f"~/.cipher_talk/keys/{name}.key")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(data)

    @staticmethod
    def unseal(name: str) -> str:
        path = os.path.expanduser(f"~/.cipher_talk/keys/{name}.key")
        with open(path, "r") as f:
            return f.read()
