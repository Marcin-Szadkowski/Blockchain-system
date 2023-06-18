import pytest
from blockchain_system.signing_authority import (
    generate_ecdsa_keys,
    InvalidSignatureError,
    SigningAuthority,
)


def test_sign_and_verify():
    private_key, public_key = generate_ecdsa_keys()
    signing_authority = SigningAuthority(private_key)

    payload = {"user_id": 123, "username": "john_doe"}
    token = signing_authority.sign(payload)

    decoded_token = signing_authority.verify(token, public_key)
    assert decoded_token["user_id"] == payload["user_id"]
    assert decoded_token["username"] == payload["username"]


def test_invalid_signature():
    private_key1, public_key1 = generate_ecdsa_keys()
    private_key2, public_key2 = generate_ecdsa_keys()
    signing_authority = SigningAuthority(private_key1)

    payload = {"user_id": 123, "username": "john_doe"}
    token = signing_authority.sign(payload)

    with pytest.raises(InvalidSignatureError):
        signing_authority.verify(token, public_key2)
