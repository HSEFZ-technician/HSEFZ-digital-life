"""Smoke tests: the project boots, URLs resolve, and key pages render."""
import pytest
from django.core.management import call_command
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_system_check_passes():
    call_command("check")


@pytest.mark.parametrize("name", ["home", "login", "register"])
def test_public_pages_render(client, name):
    response = client.get(reverse(f"club:{name}"))
    assert response.status_code == 200


def test_login_with_valid_credentials(client, student):
    assert client.login(username="test_student", password="Passw0rd123")


def test_selection_home_renders_for_anonymous_user(client):
    response = client.get(reverse("club:selection_home"))
    assert response.status_code == 200


def test_selection_home_renders_for_logged_in_student(client, student):
    client.force_login(student)
    response = client.get(reverse("club:selection_home"))
    assert response.status_code == 200


def test_unknown_url_returns_404(client):
    response = client.get("/this-page-does-not-exist/")
    assert response.status_code == 404
