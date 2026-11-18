import pytest
from src.main.api.models.credit_requesting_request import CreditRequestingRequest
from src.main.api.data.test_data import VALID_CREDIT_AMOUNT
from src.main.api.data.test_data import VALID_CREDIT_TERM_MONTHS

@pytest.fixture
def credit_request(create_account_credit, api_manager, credit_user_request):
    credit_requesting_request = CreditRequestingRequest(accountId=create_account_credit.id, amount=VALID_CREDIT_AMOUNT,
                                                        termMonths=VALID_CREDIT_TERM_MONTHS)
    credit_requesting_response = api_manager.user_steps.credit_requesting(credit_user_request,
                                                                          credit_requesting_request)
    return credit_requesting_response