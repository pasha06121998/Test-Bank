from src.main.api.models.credit_repay_request import CreditRepayRequest
from src.main.api.models.credit_requesting_request import CreditRequestingRequest
from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.deposit_request import DepositRequest
from src.main.api.specs.response_specs import ResponseSpecs
from src.main.api.foundation.endpoint import Endpoint
from src.main.api.specs.request_specs import RequestSpecs
from src.main.api.foundation.requesters.validate_crud_requester import ValidateCrudRequester
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.foundation.requesters.crud_requester import CrudRequester
from src.main.api.steps.base_steps import BaseSteps


class UserSteps(BaseSteps):
    def create_account(self, create_user_request: CreateUserRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREATE_ACCOUNT,
            ResponseSpecs.request_created()
        ).post()
        return response

    def deposit(self, create_user_request: CreateUserRequest, deposit_request: DepositRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(deposit_request)
        return response

    def transfer(self, create_user_request: CreateUserRequest, transfer_request: TransferRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_ok()
        ).post(transfer_request)
        return response

    def credit_requesting(self, create_user_request: CreateUserRequest,
                          credit_requesting_request: CreditRequestingRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.request_created()
        ).post(credit_requesting_request)
        return response

    def credit_repay(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        response = ValidateCrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_ok()
        ).post(credit_repay_request)
        return response

    def get_transactions(self, create_user_request: CreateUserRequest, account_id: int):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.GET_TRANSACTIONS,
            ResponseSpecs.request_ok()
        ).get(account_id)
        return response.json()

    def deposit_invalid(self, create_user_request: CreateUserRequest, deposit_request: DepositRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.DEPOSIT_ACCOUNT,
            ResponseSpecs.request_bad()
        ).post(deposit_request)
        return response

    def transfer_invalid(self, create_user_request: CreateUserRequest, transfer_request: TransferRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.TRANSFER_ACCOUNT,
            ResponseSpecs.request_bad()
        ).post(transfer_request)
        return response

    def credit_requesting_invalid(self, create_user_request: CreateUserRequest,
                          credit_requesting_request: CreditRequestingRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REQUEST,
            ResponseSpecs.request_forbidden()
        ).post(credit_requesting_request)
        return response

    def credit_repay_invalid(self, create_user_request: CreateUserRequest, credit_repay_request: CreditRepayRequest):
        response = CrudRequester(
            RequestSpecs.auth_headers(username=create_user_request.username, password=create_user_request.password),
            Endpoint.CREDIT_REPAY,
            ResponseSpecs.request_unprocessable()
        ).post(credit_repay_request)
        return response