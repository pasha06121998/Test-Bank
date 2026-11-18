import pytest


@pytest.fixture
def create_account_credit(credit_user_request, api_manager):
    response = api_manager.user_steps.create_account(credit_user_request)
    return response
