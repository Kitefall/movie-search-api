from decimal import Decimal

import pytest

# Стартовый баланс пользователя Decimal(5)


@pytest.mark.asyncio
class TestAdminEndpoints:
    async def test_add_coins_to_user(
            self,
            admin,
            user_with_balance
    ):
        response = await admin.post(
            "/admin/top-up", json={"target_user_id": user_with_balance.id,
                                   "amount": 20}
        )
        assert response.status_code == 200
        balance = user_with_balance.coin_account.balance
        assert balance == Decimal(25)

    async def test_write_off_to_user(self, admin, user_with_balance):
        response = await admin.post(
            "/admin/write-off", json={"target_user_id": user_with_balance.id,
                                      "amount": '2'}
        )
        assert response.status_code == 200
        balance = user_with_balance.coin_account.balance
        assert balance == Decimal(3)

    async def test_get_transaction_to_user(self, admin, user):

        response = await admin.post(
            "/admin/user-transaction", json={"target_user_id": user.id}
        )
        assert response.status_code == 200
