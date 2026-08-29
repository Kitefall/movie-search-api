import pytest
from models.user import User
from sqlalchemy import select


class TestAuthRoute:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ["name", "email", "password"],
        [
            ("Иван", "myemail@mail.ru", "Password1"),
            ("Мария", "ema123@gmail.com", "sdfgsFdsg123"),
            ("Сергей", "ekfdf@ya.ru", "12FDdFdf12"),
        ],
    )
    async def test_signup(self, client, session, name, email, password):
        response = await client.post(
            "/auth/signup", json={"name": name,
                                  "email": email,
                                  "password": password}
        )
        assert response.status_code == 200
        message = response.json()["message"]
        assert message == "Пользователь успешно создан"
        result = await session.execute(select(User).filter(
            User.email == email))
        user = result.scalars().one_or_none()
        assert user is not None

    @pytest.mark.asyncio
    async def test_get_token(self, client, user):
        response = await client.post(
            "/auth/signin", data={"username": user.email,
                                  "password": "Password1"}
        )
        data = response.json()
        access_token = data.get("access_token")
        assert access_token is not None
        token_type = data.get("token_type")
        assert token_type == "bearer"

    @pytest.mark.asyncio
    async def test_signup_with_incorrect_data(self, client, session):
        response = await client.post(
            "/auth/signup", json={"name": "name",
                                  "email": "email",
                                  "password": "pas"}
        )
        assert response.status_code == 422
        data = response.json()
        assert data["detail"][0]["type"] == "value_error"

    @pytest.mark.asyncio
    async def test_incorrect_signin(self, client, user):
        response = await client.post(
            "/auth/signin", data={"username": user.email,
                                  "password": "Password11"}
        )
        assert response.status_code == 401
        data = response.json()
        assert data.get('detail') == 'Неверный логин или пароль'
