import pytest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.data.test_data import VALID_DEPOSIT_AMOUNT


@pytest.mark.api
class TestDeposit:
    def test_deposit_valid(self, db_session: Session, api_manager: ApiManager, create_account_user,
                           create_user_request):
        # 1. Пополнение счета и проверка баланса
        deposit_request = DepositRequest(accountId=create_account_user.id, amount=VALID_DEPOSIT_AMOUNT)
        deposit_response = api_manager.user_steps.deposit(create_user_request, deposit_request)
        assert deposit_response.balance == VALID_DEPOSIT_AMOUNT, 'Баланс не равен 1000 после депозита'

        # 2. Проверка баланса в БД
        account_from_db = Account.get_account_by_id(db_session, create_account_user.id)
        assert account_from_db.balance == VALID_DEPOSIT_AMOUNT, 'Баланс в БД не равен 1000 после депозита'

    @pytest.mark.parametrize("invalid_amount", [999, 9001])
    def test_deposit_invalid(self, db_session: Session, api_manager: ApiManager, create_user_request,
                             create_account_user, invalid_amount: int):
        # 1. Пополнение счета и проверка баланса
        deposit_request = DepositRequest(accountId=create_account_user.id, amount=invalid_amount)
        api_manager.user_steps.deposit_invalid(create_user_request, deposit_request)

        # 2. Проверка баланса после невалидного отправления
        transactions_response = api_manager.user_steps.get_transactions(create_user_request, create_account_user.id)
        assert transactions_response.get("balance") == 0, 'Баланс изменился после невалидного пополнения'

        # 3. Проверка баланса в БД
        account_from_db = Account.get_account_by_id(db_session, create_account_user.id)
        assert account_from_db.balance == 0, 'Баланс в БД изменился после невалидного пополнения'
