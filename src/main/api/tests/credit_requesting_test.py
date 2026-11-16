import pytest
from src.main.api.models.credit_requesting_request import CreditRequestingRequest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.account_crud import AccountCrudDb as Account

@pytest.mark.api
class TestCreditRequesting:
    def test_credit_request_valid(self, db_session: Session, api_manager: ApiManager, credit_user_request):
        # 1. Создаем банковский счет
        response = api_manager.user_steps.create_account(credit_user_request)
        assert response.balance == 0
        account_id = response.id

        # 2. Запрос на получение кредита
        credit_requesting_request = CreditRequestingRequest(accountId=account_id, amount=5000, termMonths=12)
        credit_requesting_response = api_manager.user_steps.credit_requesting(credit_user_request,
                                                                              credit_requesting_request)

        # 3. Проверка баланса счета
        assert credit_requesting_response.balance == 5000
        assert credit_requesting_response.id == account_id

        # 4. Проверка баланса счёта в БД
        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.balance == 5000, 'Баланс счета в БД не изменился после выдачи кредит'

        # 5. Проверка кредита в БД
        credit_request_from_db = Credit.get_credit_by_account_id(db_session, account_id)
        assert credit_request_from_db is not None, 'Кредит не найден в БД'
        assert credit_request_from_db.balance == -5000, 'Баланс долга в БД неверный'
        assert credit_request_from_db.amount == 5000, 'Сумма кредита в БД неверная'



    def test_credit_request_invalid(self, db_session: Session, api_manager: ApiManager, create_user_request):
        # 1. Создаем банковский счет с обычным пользователем
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0
        account_id = response.id

        # 2. Запрос на получение кредита
        credit_requesting_request = CreditRequestingRequest(accountId=account_id, amount=5000, termMonths=12)
        api_manager.user_steps.credit_requesting_invalid(create_user_request,
                                                                              credit_requesting_request)

        # 3. Проверка баланса счета
        transactions_response = api_manager.user_steps.get_transactions(create_user_request, account_id)
        assert transactions_response.get("balance") == 0

        # 4. Проверка кредита в БД
        credit_request_from_db = Credit.get_credit_by_account_id(db_session, account_id)
        assert credit_request_from_db is None, 'Кредит ошибочно создан в БД'
