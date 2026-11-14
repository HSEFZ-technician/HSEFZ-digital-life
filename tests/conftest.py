import pytest


@pytest.fixture
def student(django_user_model):
    return django_user_model.objects.create_user(
        username="test_student",
        email="test_student@hsefz.cn",
        password="Passw0rd123",
        student_id="202400001",
        student_real_name="测试",
        is_created=True,
    )
