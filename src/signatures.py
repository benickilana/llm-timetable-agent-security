from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"

PRIVATE_KEY_PATH = DATA_DIR / "signing_private_key.pem"
PUBLIC_KEY_PATH = DATA_DIR / "signing_public_key.pem"
POLICY_PATH = DATA_DIR / "trusted_policy.txt"
SIGNATURE_PATH = DATA_DIR / "trusted_policy.sig"


def generate_keypair() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    PRIVATE_KEY_PATH.write_bytes(private_bytes)
    PUBLIC_KEY_PATH.write_bytes(public_bytes)


def load_private_key() -> Ed25519PrivateKey:
    key_bytes = PRIVATE_KEY_PATH.read_bytes()
    return serialization.load_pem_private_key(key_bytes, password=None)


def load_public_key() -> Ed25519PublicKey:
    key_bytes = PUBLIC_KEY_PATH.read_bytes()
    return serialization.load_pem_public_key(key_bytes)


def sign_policy() -> None:
    private_key = load_private_key()
    policy_bytes = POLICY_PATH.read_bytes()
    signature = private_key.sign(policy_bytes)
    SIGNATURE_PATH.write_bytes(signature)


def verify_policy_signature() -> bool:
    if not PUBLIC_KEY_PATH.exists() or not SIGNATURE_PATH.exists():
        return False

    public_key = load_public_key()
    policy_bytes = POLICY_PATH.read_bytes()
    signature = SIGNATURE_PATH.read_bytes()

    try:
        public_key.verify(signature, policy_bytes)
        return True
    except InvalidSignature:
        return False


def ensure_demo_signature_material() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not PRIVATE_KEY_PATH.exists() or not PUBLIC_KEY_PATH.exists():
        generate_keypair()

    sign_policy()


def main() -> None:
    ensure_demo_signature_material()
    verified = verify_policy_signature()

    print(f"Generated/updated signature: {SIGNATURE_PATH}")
    print(f"Public key: {PUBLIC_KEY_PATH}")
    print(f"Private key: {PRIVATE_KEY_PATH}")
    print(f"Trusted policy signature valid: {verified}")


if __name__ == "__main__":
    main()
