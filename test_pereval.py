import json

from api import app
from faker import Faker
from dataclass import Pereval

faker = Faker('ru_RU')
class TestPereval:
    def setup(self):
        app.testing = True
        self.client = app.test_client()
        self.faker = Faker('ru_RU')
        self.pereval = Pereval()

    def test_post(self):
        response = self.client.post('/submitData/create/', json={
            "beauty_title": f"{faker.word()}",
            "title": f"{faker.word()}",
            "other_titles": f"{faker.word()}",
            "connect": "",
            "add_time": f"{faker.date_time()}",
            "user": {
                "email": f"{faker.unique.email()}",
                "fam": f"{faker.last_name()}",
                "name": f"{faker.first_name()}",
                "otc": f"{faker.middle_name()}",
                "phone": f"{faker.phone_number()}"
            },
            "coords": {
                "latitude": f"{round(faker.latitude(), 4)}",
                "longitude": f"{round(faker.longitude(), 4)}",
                "height": f"{faker.random_int(0, 5000)}"
            },
            "level": {
                "winter": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "summer": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "autumn": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "spring": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}"
            },
            "images": [
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"}
            ]
        })
        assert response.status_code == 200

    def test_get_pereval_by_id(self):
        if self.pereval.get_random_pereval():
            id = self.pereval.get_random_pereval().id
            response = self.client.get(f'/submitData/{id}/')
            assert response.status_code == 200

    def test_get_perevals_by_user_email(self):
        if self.pereval.get_first_user():
            user_email = self.pereval.get_first_user().email
            response = self.client.get(f'/submitData/', query_string={'user_email': user_email})
            assert response.status_code == 200

    def test_patch(self):
        if self.pereval.get_random_pereval():
            id = self.pereval.get_random_pereval().id
            pereval_data = self.pereval.get_pereval_by_id(id)
            response = self.client.patch(f'/submitData/{id}/', json={
                "beauty_title": f"{faker.word()}",
                "title": f"{faker.word()}",
                "other_titles": f"{faker.word()}",
                "connect": "",
                "add_time": f"{pereval_data['add_time']}",
                "user": {
                    "email": f"{pereval_data['user']['email']}",
                    "fam": f"{pereval_data['user']['fam']}",
                    "name": f"{pereval_data['user']['name']}",
                    "otc": f"{pereval_data['user']['otc']}",
                    "phone": f"{pereval_data['user']['phone']}"
                },
                "coords": {
                    "latitude": f"{round(faker.latitude(), 4)}",
                    "longitude": f"{round(faker.longitude(), 4)}",
                    "height": f"{faker.random_int(0, 5000)}"
                },
                "level": {
                    "winter": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                    "summer": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                    "autumn": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                    "spring": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}"
                },
                "images": [
                    {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                    {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                    {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"}
                ]
            })
            assert response.status_code == 200

    def test_email_validation(self):
        response = self.client.post('/submitData/create/', json={
            "beauty_title": f"{faker.word()}",
            "title": f"{faker.word()}",
            "other_titles": f"{faker.word()}",
            "connect": "",
            "add_time": f"{faker.date_time()}",
            "user": {
                "email": f"{faker.unique.word()}",
                "fam": f"{faker.last_name()}",
                "name": f"{faker.first_name()}",
                "otc": f"{faker.middle_name()}",
                "phone": f"{faker.phone_number()}"
            },
            "coords": {
                "latitude": f"{round(faker.latitude(), 4)}",
                "longitude": f"{round(faker.longitude(), 4)}",
                "height": f"{faker.random_int(0, 5000)}"
            },
            "level": {
                "winter": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "summer": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "autumn": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "spring": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}"
            },
            "images": [
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"}
            ]
        })
        response_data = json.loads(response.data)
        assert response_data == {'status': 400, 'message': 'Неверно введённые данные', 'id': None}

    def test_coords_validation(self):
        response = self.client.post('/submitData/create/', json={
            "beauty_title": f"{faker.word()}",
            "title": f"{faker.word()}",
            "other_titles": f"{faker.word()}",
            "connect": "",
            "add_time": f"{faker.date_time()}",
            "user": {
                "email": f"{faker.unique.email()}",
                "fam": f"{faker.last_name()}",
                "name": f"{faker.first_name()}",
                "otc": f"{faker.middle_name()}",
                "phone": f"{faker.phone_number()}"
            },
            "coords": {
                "latitude": f"{''.join(faker.random_letters(10))}",
                "longitude": f"{''.join(faker.random_letters(10))}",
                "height": f"{''.join(faker.random_letters(10))}"
            },
            "level": {
                "winter": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "summer": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "autumn": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "spring": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}"
            },
            "images": [
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"}
            ]
        })
        response_data = json.loads(response.data)
        assert response_data == {'status': 400, 'message': 'Неверно введённые данные', 'id': None}

    def test_phone_validation(self):
        response = self.client.post('/submitData/create/', json={
            "beauty_title": f"{faker.word()}",
            "title": f"{faker.word()}",
            "other_titles": f"{faker.word()}",
            "connect": "",
            "add_time": f"{faker.date_time()}",
            "user": {
                "email": f"{faker.unique.email()}",
                "fam": f"{faker.last_name()}",
                "name": f"{faker.first_name()}",
                "otc": f"{faker.middle_name()}",
                "phone": f"{faker.word()}"
            },
            "coords": {
                "latitude": f"{round(faker.latitude(), 4)}",
                "longitude": f"{round(faker.longitude(), 4)}",
                "height": f"{faker.random_int(0, 5000)}"
            },
            "level": {
                "winter": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "summer": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "autumn": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "spring": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}"
            },
            "images": [
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"}
            ]
        })
        response_data = json.loads(response.data)
        assert response_data == {'status': 400, 'message': 'Неверно введённые данные', 'id': None}

    def test_title_required(self):
        response = self.client.post('/submitData/create/', json={
            "beauty_title": f"{faker.word()}",
            "title": None,
            "other_titles": f"{faker.word()}",
            "connect": "",
            "add_time": f"{faker.date_time()}",
            "user": {
                "email": f"{faker.unique.email()}",
                "fam": f"{faker.last_name()}",
                "name": f"{faker.first_name()}",
                "otc": f"{faker.middle_name()}",
                "phone": f"{faker.phone_number()}"
            },
            "coords": {
                "latitude": f"{round(faker.latitude(), 4)}",
                "longitude": f"{round(faker.longitude(), 4)}",
                "height": f"{faker.random_int(0, 5000)}"
            },
            "level": {
                "winter": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "summer": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "autumn": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}",
                "spring": f"{faker.random_uppercase_letter()}{faker.random_int(0, 9)}"
            },
            "images": [
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"},
                {"title": f"{faker.unique.word()}", "data": f"{bytes(faker.random_int(1, 500)).decode('utf-8')}"}
            ]
        })
        response_data = json.loads(response.data)
        assert response_data == {'status': 400, 'message': 'Пропущены обязательные поля', 'id': None}

    def teardown(self):
        pass
