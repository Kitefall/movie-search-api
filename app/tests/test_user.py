from decimal import Decimal

import pytest

# Стартовый баланс пользователя Decimal(5)


class TestUserRoutes:
    @pytest.mark.asyncio
    async def test_top_up(self,
                          authorized_client,
                          session,
                          user_with_balance):
        response = await authorized_client.post("user/top-up",
                                                json={"amount": 100})
        assert response.status_code == 200
        assert "Баланс успешно пополнен" in response.json()["message"]
        balance = user_with_balance.coin_account.balance
        assert balance == Decimal(105)

    @pytest.mark.asyncio
    async def test_top_up_unauthorized(self, client):
        response = await client.post("/top-up", json={"amount": 100})
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_balance(self,
                               authorized_client,
                               session,
                               user_with_balance):
        response = await authorized_client.get("user/balance")
        assert response.status_code == 200
        balance = user_with_balance.coin_account.balance
        assert balance == Decimal(5)

    @pytest.mark.asyncio
    async def test_get_balance_unauthorized(self, client):
        response = await client.get("user/balance")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_predict_history(self, authorized_client):
        response = await authorized_client.get("user/history-predict")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_predict_history_unauthorized(self, client):
        response = await client.get("user/history-predict")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_history_transaction(self, authorized_client):
        response = await authorized_client.get("user/history-transaction")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_get_history_transaction_unauthorized(self, client):
        response = await client.get("user/history-transaction")
        assert response.status_code == 401


class TestTopUpValidation:
    @pytest.mark.asyncio
    async def test_top_up_invalid_amount(self, authorized_client):
        response = await authorized_client.post("user/top-up",
                                                json={"amount": -100})
        assert response.status_code == 400
        assert (response.json()["detail"] ==
                "Сумма пополнения должна быть больше нуля")

    @pytest.mark.asyncio
    async def test_top_up_zero_amount(self, authorized_client):
        response = await authorized_client.post("user/top-up",
                                                json={"amount": 0})
        assert response.status_code == 400
        assert (response.json()["detail"] ==
                "Сумма пополнения должна быть больше нуля")

    @pytest.mark.asyncio
    async def test_top_up_non_numeric_amount(self, authorized_client):
        response = await authorized_client.post("user/top-up",
                                                json={"amount": "abc"})
        assert response.status_code == 422
