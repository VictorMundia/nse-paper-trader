"""Tests for registration, login, tokens, and password changes and resets."""
# This imports pytest for parametrised tests.
import pytest

# This imports the shared helpers.
from conftest import TEST_PASSWORD, register_and_login


def test_register_gives_new_student_starting_balance(client):
    """A valid registration returns 201, cleans the input, and starts the student with KES 100,000."""
    # This registers with messy capitals and spaces.
    response = client.post("/api/auth/register", json={"full_name": "  Jane Doe ", "email": " Jane@Example.COM ", "password": TEST_PASSWORD, "experience_level": "Intermediate"})
    # This reads the reply.
    body = response.get_json()
    # 201 means created.
    assert response.status_code == 201
    # The email and level are normalised.
    assert body["email"] == "jane@example.com" and body["experience_level"] == "intermediate"
    # Every student starts with the same virtual money.
    assert body["virtual_balance"] == "100000.00"


@pytest.mark.parametrize(
    "payload, message_part",
    [
        ({"email": "a@b.com", "password": TEST_PASSWORD, "experience_level": "beginner"}, "required"),
        ({"full_name": "Jane", "email": "not-an-email", "password": TEST_PASSWORD, "experience_level": "beginner"}, "valid email"),
        ({"full_name": "Jane", "email": "a@b.com", "password": "short", "experience_level": "beginner"}, "at least 8"),
        ({"full_name": "Jane", "email": "a@b.com", "password": "p" * 73, "experience_level": "beginner"}, "72 bytes"),
        ({"full_name": "Jane", "email": "a@b.com", "password": TEST_PASSWORD, "experience_level": "expert"}, "experience_level"),
        ({"full_name": ["Jane"], "email": "a@b.com", "password": TEST_PASSWORD, "experience_level": "beginner"}, "required"),
    ],
)
def test_register_rejects_bad_input(client, payload, message_part):
    """Each broken rule gets a 400 with a helpful message, never a crash."""
    # This sends the bad registration.
    response = client.post("/api/auth/register", json=payload)
    # 400 means "your request was wrong".
    assert response.status_code == 400
    # The message names the problem.
    assert message_part in response.get_json()["message"]


def test_non_json_body_is_rejected_cleanly(client):
    """A body that is not a JSON object returns 400, not a 500 crash."""
    # This sends a list instead of an object.
    assert client.post("/api/auth/login", json=[1, 2, 3]).status_code == 400
    # This sends plain text.
    assert client.post("/api/auth/login", data="hello", content_type="text/plain").status_code == 400


def test_duplicate_email_is_rejected_whatever_the_capitals(client):
    """The same email in different capitals counts as a duplicate."""
    # This creates the first account.
    register_and_login(client, email="dup@example.com")
    # This tries again in capitals.
    response = client.post("/api/auth/register", json={"full_name": "Copy", "email": "DUP@example.com", "password": TEST_PASSWORD, "experience_level": "beginner"})
    # 409 means conflict.
    assert response.status_code == 409


def test_login_gives_the_same_message_for_wrong_password_and_unknown_email(client):
    """Login never reveals whether an email is registered."""
    # This creates an account.
    register_and_login(client, email="known@example.com")
    # This uses the right email with a wrong password.
    wrong_password = client.post("/api/auth/login", json={"email": "known@example.com", "password": "WrongPass999"})
    # This uses an email that does not exist.
    unknown_email = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "WrongPass999"})
    # Both are 401 with identical messages.
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.get_json() == unknown_email.get_json()


def test_me_needs_a_valid_token_and_never_returns_the_password_hash(client):
    """/me rejects missing or fake tokens and returns the profile without secrets."""
    # No token -> 401.
    assert client.get("/api/auth/me").status_code == 401
    # A fake token -> 401 (not 422).
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.token"}).status_code == 401
    # A real token -> 200.
    response = client.get("/api/auth/me", headers=register_and_login(client))
    # This checks the result.
    assert response.status_code == 200
    # The password hash must never leave the server.
    assert "password_hash" not in response.get_json()


def test_changing_password_logs_out_old_tokens(client):
    """After a password change the old token stops working and the new one works."""
    # This creates an account and keeps its first token.
    old_headers = register_and_login(client, email="change@example.com")
    # A wrong current password is a 400, so the student is not logged out by a typo.
    wrong = client.post("/api/auth/change-password", json={"current_password": "nope12345", "new_password": "BrandNew456!"}, headers=old_headers)
    assert wrong.status_code == 400
    # This changes the password correctly.
    response = client.post("/api/auth/change-password", json={"current_password": TEST_PASSWORD, "new_password": "BrandNew456!"}, headers=old_headers)
    assert response.status_code == 200
    # The old token is now rejected.
    assert client.get("/api/auth/me", headers=old_headers).status_code == 401
    # The fresh token from the response works.
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {response.get_json()['access_token']}"}).status_code == 200
    # Only the new password logs in.
    assert client.post("/api/auth/login", json={"email": "change@example.com", "password": TEST_PASSWORD}).status_code == 401
    assert client.post("/api/auth/login", json={"email": "change@example.com", "password": "BrandNew456!"}).status_code == 200


def test_forgot_and_reset_password_flow(client, monkeypatch):
    """Same reply for known and unknown emails; the link works once; only 3 emails per hour."""
    # This will hold the "sent" emails instead of really sending them.
    sent = []
    # This replaces the email sender with one that records the email.
    monkeypatch.setattr("app.services.password_reset_service.send_email_in_background", lambda to, subject, body: sent.append(body))
    # This creates an account.
    register_and_login(client, email="forgot@example.com")
    # This asks for resets for a known and an unknown email.
    known = client.post("/api/auth/forgot-password", json={"email": "forgot@example.com"})
    unknown = client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
    # The replies are identical, so accounts cannot be discovered.
    assert known.get_json() == unknown.get_json() and known.status_code == 200
    # Only the real account received an email.
    assert len(sent) == 1
    # This pulls the token out of the link in the email.
    token = sent[0].split("token=")[1].split()[0]
    # The link sets a new password.
    assert client.post("/api/auth/reset-password", json={"token": token, "new_password": "ResetPass789!"}).status_code == 200
    # The same link cannot be used twice.
    assert client.post("/api/auth/reset-password", json={"token": token, "new_password": "Another000!"}).status_code == 400
    # The new password works.
    assert client.post("/api/auth/login", json={"email": "forgot@example.com", "password": "ResetPass789!"}).status_code == 200
    # Four more requests within the hour: two allowed (3 total), two blocked.
    for _ in range(4):
        client.post("/api/auth/forgot-password", json={"email": "forgot@example.com"})
    # 1 earlier email + 2 allowed = 3 emails in total.
    assert len(sent) == 3
