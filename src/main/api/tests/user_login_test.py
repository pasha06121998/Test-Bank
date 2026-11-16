import pytest
from src.main.api.classes.api_manager import ApiManager

@pytest.mark.api
class TestUserLogin:
    def test_login_admin(self, api_manager: ApiManager, admin_login_request):
        response = api_manager.admin_steps.login_user(admin_login_request)

        assert admin_login_request.username == response.user.username
        assert response.user.role == "ROLE_ADMIN"

    def test_login_user(self, api_manager, create_user_request):
        response = api_manager.admin_steps.login_user(create_user_request)

        assert create_user_request.username == response.user.username
        assert response.user.role == "ROLE_USER"
