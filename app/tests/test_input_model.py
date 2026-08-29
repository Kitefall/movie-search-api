import pytest
from schemas.use_model_schema import InputDataModel


class TestModelInputData:
    @pytest.mark.asyncio
    async def test_model_input_data_insufficient_funds(
        self,
        authorized_client,
        session,
        user
    ):
        data = InputDataModel(data="test data")
        response = await authorized_client.post(
            "model/data-input",
            json=data.model_dump())
        assert response.status_code == 422
        assert response.json()["detail"] == "Недостаточно средств"

    @pytest.mark.asyncio
    async def test_model_input_data_error(self, authorized_client):
        data = InputDataModel(data="")
        response = await authorized_client.post(
            "model/data-input",
            json=data.model_dump())
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_model_input_data_unauthorized(self, client):
        data = InputDataModel(data="test data")
        response = await client.post("/data-input", json=data.model_dump())
        assert response.status_code == 404
