import pytest
from types import SimpleNamespace
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator
from src.main.api.data.test_data import USER_TWO_DEPOSIT

@pytest.fixture
def second_user_deposit(api_manager):
    user_two = RandomModelGenerator.generate(CreateUserRequest)
    api_manager.admin_steps.create_user(user_two)
    account_two = api_manager.user_steps.create_account(user_two)
    request = DepositRequest(accountId=account_two.id, amount=USER_TWO_DEPOSIT)
    response = api_manager.user_steps.deposit(user_two, request)
    return SimpleNamespace(
        user=user_two,
        account_id=account_two.id,
        balance=response.balance
    )
