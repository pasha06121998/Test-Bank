import pytest
from src.main.api.classes.api_manager import ApiManager


@pytest.mark.api
class TestUserLogin:
    def test_login_admin(self, api_manager: ApiManager, admin_login_request):
        # Авторизация админа и проверка
        response = api_manager.admin_steps.login_user(admin_login_request)

        assert admin_login_request.username == response.user.username, 'Имя пользователя в ответе не совпадает'
        assert response.user.role == "ROLE_ADMIN", "У пользователя другая роль"

    def test_login_user(self, api_manager, create_user_request):
        # Авторизация пользователя и проверка
        response = api_manager.admin_steps.login_user(create_user_request)

        assert create_user_request.username == response.user.username, 'Имя пользователя в ответе не совпадает'
        assert response.user.role == "ROLE_USER", "У пользователя другая роль"
