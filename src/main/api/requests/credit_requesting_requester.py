from src.main.api.models.credit_requesting_request import CreditRequestingRequest
from src.main.api.models.credit_requesting_response import CreditRequestingResponse
from src.main.api.requests.requester import Requester
from requests import Response
import requests

class CreditRequestingRequester(Requester):
    def post(self, credit_requesting_request: CreditRequestingRequest) -> CreditRequestingResponse| Response:
        url = f"{self.base_url}/credit/request"
        response = requests.post(
            url=url,
            json=credit_requesting_request.model_dump(),
            headers=self.headers
        )
        self.response_spec(response)
        return CreditRequestingResponse(**response.json())