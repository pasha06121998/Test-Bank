import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_requesting_request import CreditRequestingRequest


@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay_valid(self, db_session: Session, api_manager: ApiManager, credit_user_request):
        # 1. Создаем банковский счет
        response = api_manager.user_steps.create_account(credit_user_request)
        assert response.balance == 0
        account_id = response.id

        # 2. Запрос на получение кредита
        credit_requesting_request = CreditRequestingRequest(accountId=account_id, amount=5000, termMonths=12)
        credit_requesting_response = api_manager.user_steps.credit_requesting(credit_user_request,
                                                                              credit_requesting_request)

        assert credit_requesting_response.balance == 5000
        credit_id = credit_requesting_response.creditId

        # 3. Погашение кредита
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=5000)
        credit_repay_response = api_manager.user_steps.credit_repay(credit_user_request, credit_repay_request)
        assert credit_repay_response.amountDeposited == 5000

        # 4. Проверка баланса счета
        transactions_response = api_manager.user_steps.get_transactions(credit_user_request, account_id)
        assert transactions_response.get("balance") == 0

        # 5. Проверка баланса счёта аккаунта в БД
        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.balance == 0, 'Баланс счета в БД не изменился после погашения кредита'

        # 6. Проверка кредита в БД
        credit_request_from_db = Credit.get_credit_by_account_id(db_session, account_id)
        assert credit_request_from_db.balance == 0, 'Баланс долга по кредиту в БД не равен 0'

    def test_credit_repay_invalid(self, db_session: Session, api_manager: ApiManager, credit_user_request):
        # 1. Создаем банковский счет
        response = api_manager.user_steps.create_account(credit_user_request)
        assert response.balance == 0
        account_id = response.id

        # 2. Запрос на получение кредита
        credit_requesting_request = CreditRequestingRequest(accountId=account_id, amount=5000, termMonths=12)
        credit_requesting_response = api_manager.user_steps.credit_requesting(credit_user_request,
                                                                              credit_requesting_request)

        assert credit_requesting_response.balance == 5000
        credit_id = credit_requesting_response.creditId

        # 3. Погашение кредита
        credit_repay_request = CreditRepayRequest(creditId=credit_id, accountId=account_id, amount=5000)
        credit_repay_response = api_manager.user_steps.credit_repay(credit_user_request, credit_repay_request)
        assert credit_repay_response.amountDeposited == 5000

        # 4. Повторное погашение
        api_manager.user_steps.credit_repay_invalid(credit_user_request, credit_repay_request)

        transactions_response = api_manager.user_steps.get_transactions(credit_user_request, account_id)
        assert transactions_response.get("balance") == 0

        # 5. Проверка баланса счета и кредита в БД
        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.balance == 0, 'Баланс счета изменился после попытки повторного погашения'

        credit_request_from_db = Credit.get_credit_by_account_id(db_session, account_id)
        assert credit_request_from_db.balance == 0, 'Баланс долга изменился после попытки повторного погашения'

