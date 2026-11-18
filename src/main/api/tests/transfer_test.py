import pytest
from sqlalchemy.orm import Session
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.classes.api_manager import ApiManager
from src.main.api.db.crud.transaction_crud import TransactionCrudDb as Transaction
from src.main.api.db.crud.account_crud import AccountCrudDb as Account
from src.main.api.data.test_data import VALID_TRANSFER_AMOUNT
from src.main.api.data.test_data import USER_ONE_DEPOSIT
from src.main.api.data.test_data import USER_TWO_DEPOSIT


@pytest.mark.api
class TestTransferAccount:
    def test_transfer_valid(self, db_session: Session, api_manager: ApiManager, first_user_deposit,
                            second_user_deposit):
        # 1. Перевод между счетами
        transfer_request = TransferRequest(fromAccountId=first_user_deposit.account_id,
                                           toAccountId=second_user_deposit.account_id, amount=VALID_TRANSFER_AMOUNT)
        transfer_response = api_manager.user_steps.transfer(first_user_deposit.user, transfer_request)

        # 2. Проверяем баланс после транзакции
        assert transfer_response.fromAccountIdBalance == USER_ONE_DEPOSIT - VALID_TRANSFER_AMOUNT, 'Баланс отправителя после транзакции неверный'

        transactions_response = api_manager.user_steps.get_transactions(second_user_deposit.user,
                                                                        second_user_deposit.account_id)
        assert transactions_response.get(
            "balance") == USER_TWO_DEPOSIT + VALID_TRANSFER_AMOUNT, 'Баланс получателя после транзакции неверный'

        # 3. Проверяем баланс после транзакции в БД
        account_from_db_1 = Account.get_account_by_id(db_session, first_user_deposit.account_id)
        assert account_from_db_1.balance == USER_ONE_DEPOSIT - VALID_TRANSFER_AMOUNT, 'Баланс отправителя после транзакции в БД неверный'

        account_from_db_2 = Account.get_account_by_id(db_session, second_user_deposit.account_id)
        assert account_from_db_2.balance == USER_TWO_DEPOSIT + VALID_TRANSFER_AMOUNT, 'Баланс получателя после транзакции в БД неверный'

        # 4. Проверяем тип транзакции
        transaction_db_1 = Transaction.get_transactions_by_account_id(db_session, first_user_deposit.account_id)
        assert any(t.transaction_type == "transfer" and t.amount == VALID_TRANSFER_AMOUNT for t in
                   transaction_db_1), 'В БД нет транзакции transfer на 500 рублей для счета отправителя'

        transaction_db_2 = Transaction.get_transactions_by_account_id(db_session, second_user_deposit.account_id)
        assert any(t.transaction_type == "transfer" and t.amount == VALID_TRANSFER_AMOUNT for t in
                   transaction_db_2), 'В БД нет входящей транзакции transfer на 500 рублей'

    @pytest.mark.parametrize("invalid_transfer_amount", [499, 10001])
    def test_transfer_invalid(self, db_session: Session, api_manager: ApiManager, first_user_deposit,
                              second_user_deposit, invalid_transfer_amount: int):
        # 1. Негативный перевод
        transfer_request = TransferRequest(fromAccountId=first_user_deposit.account_id,
                                           toAccountId=second_user_deposit.account_id, amount=invalid_transfer_amount)
        api_manager.user_steps.transfer_invalid(first_user_deposit.user, transfer_request)

        # 2. Проверяем баланс после транзакции
        transactions_response_one = api_manager.user_steps.get_transactions(first_user_deposit.user,
                                                                            first_user_deposit.account_id)
        assert transactions_response_one.get("balance") == USER_ONE_DEPOSIT, 'Баланс отправителя изменился'

        transactions_response_two = api_manager.user_steps.get_transactions(second_user_deposit.user,
                                                                            second_user_deposit.account_id)
        assert transactions_response_two.get("balance") == USER_TWO_DEPOSIT, 'Баланс получателя изменился'

        # 3. Проверяем баланс после транзакции в БД
        account_from_db_1 = Account.get_account_by_id(db_session, first_user_deposit.account_id)
        assert account_from_db_1.balance == USER_ONE_DEPOSIT, 'Баланс отправителя в БД изменился'

        account_from_db_2 = Account.get_account_by_id(db_session, second_user_deposit.account_id)
        assert account_from_db_2.balance == USER_TWO_DEPOSIT, 'Баланс получателя в БД изменился'

        # 4. Проверяем тип транзакции
        transaction_db_1 = Transaction.get_transactions_by_account_id(db_session, first_user_deposit.account_id)
        assert not any(t.transaction_type == "transfer" and t.amount == invalid_transfer_amount for t in
                       transaction_db_1), f'В БД ошибочно появилась транзакция transfer на {invalid_transfer_amount} рублей для счета отправителя'

        transaction_db_2 = Transaction.get_transactions_by_account_id(db_session, second_user_deposit.account_id)
        assert not any(t.transaction_type == "transfer" and t.amount == invalid_transfer_amount for t in
                       transaction_db_2), f'В БД ошибочно появилась транзакция transfer на {invalid_transfer_amount} рублей для счета отправителя'
