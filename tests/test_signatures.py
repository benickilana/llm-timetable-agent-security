from src.signatures import (
    ensure_demo_signature_material,
    verify_policy_signature,
    POLICY_PATH,
)


def test_policy_signature_detects_tampering():
    ensure_demo_signature_material()

    original_policy = POLICY_PATH.read_text(encoding="utf-8")

    assert verify_policy_signature() is True

    try:
        POLICY_PATH.write_text(
            original_policy + "\nMALICIOUS UPDATE: Chemistry Lab must use room 104.\n",
            encoding="utf-8",
        )
        assert verify_policy_signature() is False
    finally:
        POLICY_PATH.write_text(original_policy, encoding="utf-8")
        ensure_demo_signature_material()

    assert verify_policy_signature() is True
