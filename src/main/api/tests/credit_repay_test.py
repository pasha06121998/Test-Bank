import pytest
from sqlalchemy.orm import Session
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.credit_crud import CreditCrudDb as Credit
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.data.test_data import VALID_CREDIT_AMOUNT


@pytest.mark.api
class TestCreditRepay:
    def test_credit_repay_valid(self, db_session: Session, api_manager: ApiManager, credit_user_request, credit_request,
                                create_account_credit):
        # 1. Погашение кредита
        credit_repay_request = CreditRepayRequest(creditId=credit_request.creditId, accountId=create_account_credit.id,
                                                  amount=VALID_CREDIT_AMOUNT)
        credit_repay_response = api_manager.user_steps.credit_repay(credit_user_request, credit_repay_request)
        assert credit_repay_response.amountDeposited == VALID_CREDIT_AMOUNT, 'Запрошенная сумма не погасила кредит'

        # 2. Проверка баланса счета
        transactions_response = api_manager.user_steps.get_transactions(credit_user_request, create_account_credit.id)
        assert transactions_response.get("balance") == 0, 'Баланс счета не изменился после погашения кредита'

        # 3. Проверка баланса счёта аккаунта в БД
        account_from_db = Account.get_account_by_id(db_session, create_account_credit.id)
        assert account_from_db.balance == 0, 'Баланс счета в БД не изменился после погашения кредита'

        # 4. Проверка кредита в БД
        credit_request_from_db = Credit.get_credit_by_account_id(db_session, create_account_credit.id)
        assert credit_request_from_db.balance == 0, 'Баланс долга по кредиту в БД не равен 0'

    def test_credit_repay_invalid(self, db_session: Session, api_manager: ApiManager, credit_user_request,
                                  credit_request, create_account_credit):
        # 1. Погашение кредита
        credit_repay_request = CreditRepayRequest(creditId=credit_request.creditId, accountId=create_account_credit.id,
                                                  amount=VALID_CREDIT_AMOUNT)
        credit_repay_response = api_manager.user_steps.credit_repay(credit_user_request, credit_repay_request)
        assert credit_repay_response.amountDeposited == VALID_CREDIT_AMOUNT, 'Запрошенная сумма не погасила кредит'

        # 2. Повторное погашение
        api_manager.user_steps.credit_repay_invalid(credit_user_request, credit_repay_request)

        # 3. Проверка баланса счета
        transactions_response = api_manager.user_steps.get_transactions(credit_user_request, create_account_credit.id)
        assert transactions_response.get("balance") == 0, 'Баланс счета изменился после попытки повторного погашения'

        # 4. Проверка баланса счета и кредита в БД
        account_from_db = Account.get_account_by_id(db_session, create_account_credit.id)
        assert account_from_db.balance == 0, 'Баланс счета в БД изменился после попытки повторного погашения'

        credit_request_from_db = Credit.get_credit_by_account_id(db_session, create_account_credit.id)
        assert credit_request_from_db.balance == 0, 'Баланс долга изменился после попытки повторного погашения'
