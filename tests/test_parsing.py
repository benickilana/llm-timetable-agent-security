from src.parsing import parse_model_output


def test_parse_valid_json():
    raw = '{"answer": "ok", "action": {"subject": "Chemistry Lab", "room": "106"}}'
    parsed = parse_model_output(raw)

    assert parsed.error is None
    assert parsed.answer == "ok"
    assert parsed.action["subject"] == "Chemistry Lab"


def test_parse_markdown_wrapped_json():
    raw = '''```json
{"answer": "ok", "action": {"subject": "Informatics", "room": "110"}}
```'''
    parsed = parse_model_output(raw)

    assert parsed.error is None
    assert parsed.action["room"] == "110"


def test_parse_invalid_output_returns_error():
    parsed = parse_model_output("not json")

    assert parsed.error is not None
    assert parsed.answer == "not json"
    assert parsed.action == {}
