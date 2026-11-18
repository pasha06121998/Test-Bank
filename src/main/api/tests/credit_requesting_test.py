import pytest
from src.main.api.models.credit_requesting_request import CreditRequestingRequest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.data.test_data import VALID_CREDIT_AMOUNT
from src.main.api.data.test_data import VALID_CREDIT_TERM_MONTHS


@pytest.mark.api
class TestCreditRequesting:
    def test_credit_request_valid(self, db_session: Session, api_manager: ApiManager, credit_user_request,
                                  create_account_credit):
        # 1. Запрос на получение кредита
        credit_requesting_request = CreditRequestingRequest(accountId=create_account_credit.id,
                                                            amount=VALID_CREDIT_AMOUNT,
                                                            termMonths=VALID_CREDIT_TERM_MONTHS)
        credit_requesting_response = api_manager.user_steps.credit_requesting(credit_user_request,
                                                                              credit_requesting_request)

        # 2. Проверка баланса счета
        assert credit_requesting_response.balance == VALID_CREDIT_AMOUNT, 'Баланс счета не изменился после выдачи кредита'
        assert credit_requesting_response.id == create_account_credit.id, 'Выданный кредит не связан с нужным счетом'

        # 3. Проверка баланса счёта в БД
        account_from_db = Account.get_account_by_id(db_session, create_account_credit.id)
        assert account_from_db.balance == VALID_CREDIT_AMOUNT, 'Баланс счета в БД не изменился после выдачи кредит'

        # 4. Проверка кредита в БД
        credit_request_from_db = Credit.get_credit_by_account_id(db_session, create_account_credit.id)
        assert credit_request_from_db is not None, 'Кредит не найден в БД'
        assert credit_request_from_db.balance == -VALID_CREDIT_AMOUNT, 'Баланс долга по кредиту в БД неверный'
        assert credit_request_from_db.amount == VALID_CREDIT_AMOUNT, 'Сумма кредита в БД неверная'

    def test_credit_request_invalid(self, db_session: Session, api_manager: ApiManager, create_user_request,
                                    create_account_user):
        # 1. Запрос на получение кредита обычного пользователя
        credit_requesting_request = CreditRequestingRequest(accountId=create_account_user.id,
                                                            amount=VALID_CREDIT_AMOUNT,
                                                            termMonths=VALID_CREDIT_TERM_MONTHS)
        api_manager.user_steps.credit_requesting_invalid(create_user_request,
                                                         credit_requesting_request)

        # 2. Проверка баланса счета
        transactions_response = api_manager.user_steps.get_transactions(create_user_request, create_account_user.id)
        assert transactions_response.get(
            "balance") == 0, 'Баланс счета у обычного пользователя ошибочно изменился после попытки получения кредита'

        # 3. Проверка кредита в БД
        credit_request_from_db = Credit.get_credit_by_account_id(db_session, create_account_user.id)
        assert credit_request_from_db is None, 'Кредит ошибочно создан у обычного пользователя в БД'
