from src.main.api.models.transfer_request import TransferRequest
from src.main.api.models.transfer_response import TransferResponse
from src.main.api.requests.requester import Requester
from requests import Response
import requests


class TransferRequester(Requester):
    def post(self, transfer_request: TransferRequest) -> TransferResponse | Response:
        url = f"{self.base_url}/account/transfer"
        response = requests.post(
            url=url,
            json=transfer_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return TransferResponse(**response.json())