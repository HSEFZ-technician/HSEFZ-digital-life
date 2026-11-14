"""Security regression tests (authn/authz, CSRF, redirects, headers, secrets)."""
import pytest
from django.test import Client
from django.urls import reverse

from club.tokens import PasswordGenerator

pytestmark = pytest.mark.django_db

LOGIN_URL = "/login/"


def _login_post(client, next_url):
    return client.post(LOGIN_URL, {
        "email": "test_student",
        "password": "Passw0rd123",
        "next_url": next_url,
    })


# ---- Authentication & passwords ----------------------------------------

def test_password_is_stored_hashed(student):
    assert student.password != "Passw0rd123"
    assert student.password.startswith(("pbkdf2_", "argon2", "bcrypt", "scrypt"))


def test_login_rejects_wrong_password(client, student):
    response = client.post(LOGIN_URL, {"email": "test_student", "password": "wrong-password"})
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_generated_passwords_are_unique_and_well_formed():
    passwords = {PasswordGenerator(12) for _ in range(200)}
    assert len(passwords) == 200
    for p in passwords:
        assert len(p) == 12
        assert any(c.isdigit() for c in p) and any(c.isalpha() for c in p)


# ---- Open redirect -----------------------------------------------------

@pytest.mark.parametrize("evil", [
    "https://evil.example.com/",
    "//evil.example.com/",
    "/\\evil.example.com",
    "javascript:alert(1)",
])
def test_login_does_not_redirect_offsite(client, student, evil):
    response = _login_post(client, evil)
    assert response.status_code == 302
    assert response["Location"] == "/"


def test_login_follows_same_site_next_url(client, student):
    response = _login_post(client, "/selection/")
    assert response.status_code == 302
    assert response["Location"] == "/selection/"


# ---- CSRF --------------------------------------------------------------

def test_login_post_without_csrf_token_is_rejected(student):
    client = Client(enforce_csrf_checks=True)
    response = client.post(LOGIN_URL, {"email": "test_student", "password": "Passw0rd123"})
    assert response.status_code == 403


# ---- Authorization -----------------------------------------------------

@pytest.mark.parametrize("name", [
    "user_info", "user_security", "event_manage", "notice_manage",
])
def test_private_pages_redirect_anonymous_users_to_login(client, name):
    response = client.get(reverse(f"club:{name}"))
    assert response.status_code == 302
    assert response["Location"].startswith(LOGIN_URL)


@pytest.mark.parametrize("name", ["event_manage", "notice_manage"])
def test_management_pages_hidden_from_regular_students(client, student, name):
    client.force_login(student)
    response = client.get(reverse(f"club:{name}"))
    assert response.status_code == 404


def test_admin_requires_staff(client, student):
    client.force_login(student)
    response = client.get("/admin/")
    assert response.status_code == 302
    assert "/admin/login/" in response["Location"]


# ---- Headers & information leakage -------------------------------------

def test_clickjacking_protection_header(client):
    response = client.get(reverse("club:home"))
    assert response["X-Frame-Options"] == "DENY"


def test_content_type_nosniff_header(client):
    response = client.get(reverse("club:home"))
    assert response["X-Content-Type-Options"] == "nosniff"


def test_session_cookie_is_http_only(client, student):
    _login_post(client, "/")
    assert client.cookies["sessionid"]["httponly"]


def test_404_does_not_leak_debug_info(client, settings):
    settings.DEBUG = False
    response = client.get("/definitely-missing-page/")
    assert response.status_code == 404
    body = response.content.decode(errors="ignore")
    assert "Traceback" not in body
    assert "SECRET_KEY" not in body
    assert "URLconf" not in body
