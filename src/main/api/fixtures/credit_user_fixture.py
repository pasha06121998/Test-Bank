import pytest
from src.main.api.models.create_user_request import CreateUserRequest
from src.main.api.generators.model_generator import RandomModelGenerator


@pytest.fixture
def credit_user_request(api_manager):
    credit_user_request = RandomModelGenerator.generate(CreateUserRequest)
    credit_user_request.role = "ROLE_CREDIT_SECRET"
    api_manager.admin_steps.create_user(credit_user_request)
    return credit_user_request