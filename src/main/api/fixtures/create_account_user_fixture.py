import pytest


@pytest.fixture
def create_account_user(create_user_request, api_manager):
    response = api_manager.user_steps.create_account(create_user_request)
    return response
