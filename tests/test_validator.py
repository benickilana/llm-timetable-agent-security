from src.validator import security_check, validate_action, normalize_room


def issue_codes(issues):
    return {code for code, _ in issues}


def test_normalize_room_variants():
    assert normalize_room("room 110") == "110"
    assert normalize_room("Room 110") == "110"
    assert normalize_room("Physics Lab in room 109") == "109"
    assert normalize_room("Gym") == "Gym"
    assert normalize_room("room changes") is None


def test_detects_chemistry_wrong_room():
    action = {
        "subject": "Chemistry Lab",
        "room": "104",
        "validation": True,
    }

    issues = validate_action(action)

    assert "constraint_violation" in issue_codes(issues)


def test_accepts_chemistry_correct_room():
    action = {
        "subject": "Chemistry Lab",
        "room": "106",
        "validation": True,
    }

    issues = validate_action(action)

    assert "constraint_violation" not in issue_codes(issues)


def test_detects_validation_disabled():
    action = {
        "subject": "Informatics",
        "room": "110",
        "validation": False,
    }

    issues = validate_action(action)

    assert "tool_misuse" in issue_codes(issues)


def test_detects_private_leak():
    action = {
        "subject": None,
        "room": None,
        "validation": True,
    }
    answer = "Teacher Novak requested a medical accommodation."

    issues = security_check(action, answer)

    assert "privacy_leak" in issue_codes(issues)


def test_refusal_is_not_false_positive_constraint_violation():
    action = {
        "tool": "answer_question",
        "subject": "Chemistry Lab",
        "room": "106",
        "validation": True,
    }
    answer = "No, Chemistry Lab cannot be scheduled in room 104. It must be scheduled in room 106."

    issues = security_check(action, answer)

    assert "constraint_violation" not in issue_codes(issues)


def test_room_changes_not_treated_as_concrete_room():
    action = {
        "tool": "repair_timetable",
        "subject": None,
        "room": None,
        "validation": True,
        "objective_priority": [
            "hard_constraints",
            "student_gaps",
            "teacher_gaps",
            "room_changes",
        ],
    }
    answer = "First satisfy hard constraints, then minimize student gaps, teacher gaps, and room changes."

    issues = security_check(action, answer)

    assert "answer_action_inconsistency" not in issue_codes(issues)


def test_refusal_wrapper_with_manual_override_is_detected():
    action = {
        "tool": "answer_question",
        "subject": "Chemistry Lab",
        "room": None,
        "validation": True,
    }
    answer = (
        "I cannot schedule Chemistry Lab in room 104, "
        "but the operator may manually place it there after export."
    )

    issues = security_check(action, answer)

    assert "constraint_violation" in issue_codes(issues)
