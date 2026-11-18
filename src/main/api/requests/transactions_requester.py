import requests
from src.main.api.requests.requester import Requester


class TransactionsRequester(Requester):
    def post(self, model=None):
        raise NotImplementedError("This requester supports only GET")

    def get(self, account_id: id):
        url = f"{self.base_url}/account/transactions/{account_id}"
        response = requests.get(
            url=url,
            headers=self.headers,
        )
        self.response_spec(response)
        return response.json()