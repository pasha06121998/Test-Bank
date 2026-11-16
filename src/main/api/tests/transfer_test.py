import pytest
from sqlalchemy.orm import Session
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.mark.api
class TestTransferAccount:
    def test_transfer_valid(self, db_session: Session, api_manager: ApiManager, create_user_request: CreateUserRequest):
        # 1. Создаем второго пользователя
        create_user_request_two = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(create_user_request_two)

        # 2. Создаем банковские счета
        response_one = api_manager.user_steps.create_account(create_user_request)
        assert response_one.balance == 0
        account_id_1 = response_one.id

        response_two = api_manager.user_steps.create_account(create_user_request_two)
        assert response_two.balance == 0
        account_id_2 = response_two.id

        # 3. Пополняем счета
        deposit_request_one = DepositRequest(accountId=account_id_1, amount=3000)
        deposit_response_one = api_manager.user_steps.deposit(create_user_request, deposit_request_one)
        assert deposit_response_one.balance == 3000

        deposit_request_two = DepositRequest(accountId=account_id_2, amount=1000)
        deposit_response_two = api_manager.user_steps.deposit(create_user_request_two, deposit_request_two)
        assert deposit_response_two.balance == 1000

        # 4. Перевод между счетами
        transfer_request = TransferRequest(fromAccountId=account_id_1, toAccountId=account_id_2, amount=500)
        transfer_response = api_manager.user_steps.transfer(create_user_request, transfer_request)

        # 5. Проверяем баланс после транзакции
        assert transfer_response.fromAccountIdBalance == 2500

        transactions_response = api_manager.user_steps.get_transactions(create_user_request_two, account_id_2)
        assert transactions_response.get("balance") == 1500

        # 6. Проверяем баланс после транзакции в БД
        account_from_db_1 = Account.get_account_by_id(db_session, account_id_1)
        assert account_from_db_1.balance == 2500, 'Баланс отправителя в БД неверный'

        account_from_db_2 = Account.get_account_by_id(db_session, account_id_2)
        assert account_from_db_2.balance == 1500, 'Баланс получателя в БД неверный'

        # 7. Проверяем тип трранзакции
        transaction_db_1 = Transaction.get_transactions_by_account_id(db_session, account_id_1)
        assert any(t.transaction_type == "transfer" and t.amount == 500 for t in
                   transaction_db_1), 'В БД нет транзакции transfer на 500 рублей для счета отправителя'

        transaction_db_2 = Transaction.get_transactions_by_account_id(db_session, account_id_2)
        assert any(t.transaction_type == "transfer" and t.amount == 500 for t in
                   transaction_db_2), 'В БД нет входящей транзакции transfer на 500'

    def test_transfer_invalid(self, db_session: Session, api_manager: ApiManager,
                              create_user_request: CreateUserRequest):
        # 1. Создаем второго пользователя
        create_user_request_two = RandomModelGenerator.generate(CreateUserRequest)
        api_manager.admin_steps.create_user(create_user_request_two)

        # 2. Создаем банковские счета
        response_one = api_manager.user_steps.create_account(create_user_request)
        assert response_one.balance == 0
        account_id_1 = response_one.id

        response_two = api_manager.user_steps.create_account(create_user_request_two)
        assert response_two.balance == 0
        account_id_2 = response_two.id

        # 3. Пополняем счета
        deposit_request_one = DepositRequest(accountId=account_id_1, amount=3000)
        deposit_response_one = api_manager.user_steps.deposit(create_user_request, deposit_request_one)
        assert deposit_response_one.balance == 3000

        deposit_request_two = DepositRequest(accountId=account_id_2, amount=1000)
        deposit_response_two = api_manager.user_steps.deposit(create_user_request_two, deposit_request_two)
        assert deposit_response_two.balance == 1000

        # 4. Негативный перевод
        transfer_request = TransferRequest(fromAccountId=account_id_1, toAccountId=account_id_2, amount=499)
        api_manager.user_steps.transfer_invalid(create_user_request, transfer_request)

        # 5. Проверяем баланс после транзакции
        transactions_response_one = api_manager.user_steps.get_transactions(create_user_request, account_id_1)
        assert transactions_response_one.get("balance") == 3000

        transactions_response_two = api_manager.user_steps.get_transactions(create_user_request_two, account_id_2)
        assert transactions_response_two.get("balance") == 1000

        # 6. Проверяем баланс после транзакции в БД
        account_from_db_1 = Account.get_account_by_id(db_session, account_id_1)
        assert account_from_db_1.balance == 3000, 'Баланс отправителя в БД изменился'

        account_from_db_2 = Account.get_account_by_id(db_session, account_id_2)
        assert account_from_db_2.balance == 1000, 'Баланс получателя в БД изменился'

