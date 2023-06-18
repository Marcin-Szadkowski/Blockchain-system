import ecdsa
import jwt


def generate_ecdsa_keys() -> tuple[str, str]:
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    # each public key is a valid address
    public_key = private_key.get_verifying_key()

    return private_key.to_pem().decode(), public_key.to_pem().decode()


class InvalidSignatureError(Exception):
    pass


class SigningAuthority:
    def __init__(self, private_key: str) -> None:
        self._private_key = private_key
        self.algorithm = "ES256K"

    def sign(self, payload) -> str:
        token = jwt.encode(payload, self._private_key, algorithm=self.algorithm)
        return token

    @staticmethod
    def verify(token: str, public_key: str) -> dict:
        try:
            token = jwt.decode(token, public_key, algorithms=["ES256K"])
        except jwt.exceptions.InvalidSignatureError:
            raise InvalidSignatureError()

        return token
