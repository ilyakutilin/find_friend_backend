from http import HTTPStatus

import pytest

API_URL = "/api/v1"


@pytest.mark.django_db(transaction=True)
class TestUserChangesAPI:
    """Тесты изменения профиля пользователя."""

    objects_url = f"{API_URL}/users/"

    def check_user_info(self, info, another_user, url):
        """Проверка содержания полей в списке."""
        fields = ["id", "email", "first_name", "last_name"]
        for field in fields:
            assert field in info, (
                f"Ответ на GET-запрос к `{url}` содержит "
                f"неполную информацию о черном списке. Проверьте, что поле "
                f"`{field}` добавлено в список полей `fields`."
            )
        assert info["email"] == another_user.email, (
            f"Ответ на GET-запрос к `{url}` содержит "
            f"некорректную информацию о черном списке. Проверьте, что "
            f"в списке есть пользователь с email:`{another_user.email}`"
        )

    def test_user_list_not_auth(self, client):
        """Проверка получения данных неавторизованного пользователя."""
        response = client.get(self.objects_url)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            "Проверьте, что GET-запрос неавторизованного пользователя к "
            f"`{self.objects_url}` возвращает ответ со статусом 401."
        )

    def test_user_list_auth(
        self, user_client, user, another_user
    ):
        """Проверка данных авторизованного пользователя."""
        response = user_client.get(self.objects_url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f"Эндпоинт `{self.objects_url}` не найден, проверьте настройки"
            " в *urls.py*."
        )
        test_data = response.json()
        if "results" in test_data.keys():
            test_obj = test_data["results"][0]
            self.check_user_info(test_obj, another_user, self.objects_url)
            test_obj = test_data["results"][1]
            self.check_user_info(test_obj, user, self.objects_url)
        else:
            assert (
                response.status_code == HTTPStatus.UNAUTHORIZED
            ), f"Ошибка доступа `{test_data['detail']}`"

    @pytest.mark.skip(reason="Необходимо пофиксить поведение анонимного юзера")
    def test_user_put_not_auth(self, client, user):
        """Проверка изменения неавторизованного пользователя."""
        url = f"{API_URL}/users/{user.id}/"
        data = {}
        response = client.put(url, data=data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            "Проверьте, что неавторизованному пользователю при попытке "
            "изменения возвращается статус 401."
        )

    @pytest.mark.skip(reason="Необходимо пофиксить поведение анонимного юзера")
    def test_user_patch_not_auth(self, client, user):
        """Проверка изменения неавторизованного пользователя."""
        url = f"{API_URL}/users/{user.id}/"
        data = {}
        response = client.patch(url, data=data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            "Проверьте, что неавторизованному пользователю при попытке "
            "изменения возвращается статус 401."
        )

    def test_user_put_auth(self, user_client, user, city):
        """Проверка изменения авторизованного пользователя."""
        url = f"{API_URL}/users/{user.id}/"
        data = {
            "first_name": "Тестов",
            "last_name": "Юзя",
            "email": "test11@test.ru",
            "birthday": "2001-08-24",
            "sex": "М",
            "city": city,
            "interests": [],
            "friends": [],
            "profession": "string11",
            "purpose": "string12",
            "additionally": "string13",
            "is_geoip_allowed": False
        }
        response = user_client.put(url, data=data)
        assert response.status_code == HTTPStatus.OK, (
            "Проверьте, что авторизованному пользователю при попытке "
            "изменения возвращается статус 200."
        )
        response = user_client.get(url)
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            f"Эндпоинт `{self.objects_url}` не найден, проверьте настройки"
            " в *urls.py*."
        )
        test_data = response.json()
        data["city"] = city.name
        for key in data:
            assert test_data[key] == data[key], (
                f"Ошибка сохранения данных `{key}` - `{data[key]}`"
            )

    def test_user_patch_auth(self, user_client, user, city):
        """Проверка изменения авторизованного пользователя."""
        url = f"{API_URL}/users/{user.id}/"
        data = {
            "birthday": "2000-08-24",
            "sex": "Ж",
            "city": city,
            "interests": [],
            "friends": [],
            "profession": "string1",
            "purpose": "string2",
            "additionally": "string3",
            "is_geoip_allowed": True
        }
        response = user_client.patch(url, data=data)
        assert response.status_code == HTTPStatus.OK, (
            "Проверьте, что авторизованному пользователю при попытке "
            "изменения возвращается статус 200."
        )
        test_data = response.json()
        data["city"] = city.name
        for key in data:
            assert test_data[key] == data[key], (
                f"Ошибка сохранения данных `{key}` - `{data[key]}`"
                )
