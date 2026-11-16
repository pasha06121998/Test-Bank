from src.main.api.models.base_model import BaseModel


class CreditRequestingRequest(BaseModel):
    accountId: int
    amount: float
    termMonths: int