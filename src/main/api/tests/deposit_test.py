import pytest
from sqlalchemy.orm import Session
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.models.deposit_request import DepositRequest


@pytest.mark.api
class TestDeposit:
    def test_deposit_valid(self, db_session: Session, api_manager: ApiManager, create_user_request: CreateUserRequest):
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0
        account_id = response.id

        deposit_request = DepositRequest(accountId=account_id, amount=1000)
        deposit_response = api_manager.user_steps.deposit(create_user_request, deposit_request)
        assert deposit_response.balance == 1000

        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.balance == 1000, 'Баланс в БД не равен 1000 после депозита'

    def test_deposit_invalid(self,  db_session: Session, api_manager: ApiManager, create_user_request: CreateUserRequest):
        response = api_manager.user_steps.create_account(create_user_request)
        assert response.balance == 0
        account_id = response.id

        deposit_request = DepositRequest(accountId=account_id, amount=999)
        api_manager.user_steps.deposit_invalid(create_user_request, deposit_request)

        transactions_response = api_manager.user_steps.get_transactions(create_user_request, account_id)
        assert transactions_response.get("balance") == 0

        account_from_db = Account.get_account_by_id(db_session, account_id)
        assert account_from_db.balance == 0, 'Баланс в БД изменился после депозита'
