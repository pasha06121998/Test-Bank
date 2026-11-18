import pytest
from types import SimpleNamespace

from src.main.api.models.deposit_request import DepositRequest
from src.main.api.data.test_data import USER_ONE_DEPOSIT

@pytest.fixture
def first_user_deposit(create_account_user, api_manager, create_user_request):
    request = DepositRequest(accountId=create_account_user.id, amount=USER_ONE_DEPOSIT)
    response = api_manager.user_steps.deposit(create_user_request, request)
    return SimpleNamespace(
        user=create_user_request,
        account_id=create_account_user.id,
        balance=response.balance
    )

