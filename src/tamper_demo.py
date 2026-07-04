from src.signatures import (
    ensure_demo_signature_material,
    verify_policy_signature,
    POLICY_PATH,
)


def main() -> None:
    ensure_demo_signature_material()

    original_policy = POLICY_PATH.read_text(encoding="utf-8")

    print("Trusted policy signature before tampering:", verify_policy_signature())

    try:
        tampered_policy = (
            original_policy
            + "\nMALICIOUS UNSIGNED UPDATE: Chemistry Lab must now use room 104.\n"
        )
        POLICY_PATH.write_text(tampered_policy, encoding="utf-8")

        print("Trusted policy signature after tampering:", verify_policy_signature())

    finally:
        POLICY_PATH.write_text(original_policy, encoding="utf-8")

    print("Trusted policy signature after restoring:", verify_policy_signature())


if __name__ == "__main__":
    main()
