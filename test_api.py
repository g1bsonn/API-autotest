import requests
import unittest
import uuid

class SauresTestAPI(unittest.TestCase):
  class_sid = 0

  def test_registration_post(self):

    test_cases = [
      # Положительный тест
      {
        "data": {
          "email": "testuser36@saures.ru",
          "firstname": "api",
          "lastname": "autotest",
          "phone": "+79991234567",
          "password": "testpassword"
        },
        "expected_status_code": 200,
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      # Неверный email
      {
        "data": {
          "email": "invalid-email",
          "firstname": "api",
          "lastname": "autotest",
          "phone": "+79991234567",
          "password": "testpassword"
        },
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {"email": ["Введён неверный email"]}
        ],
        "expected_data": {}
      },
      # Отсутствующий пароль
      {
        "data": {
          "email": "testuser@saures.ru",
          "firstname": "api",
          "lastname": "autotest",
          "phone": "+79991234567",
          "password": ""
        },
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {"password": ["Обязательное поле"]}
        ],
        "expected_data": {}
      },
      # Неверный номер телефона
      {
        "data": {
          "email": "testuser@saures.ru",
          "firstname": "api",
          "lastname": "autotest",
          "phone": "123",
          "password": "testpassword"
        },
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {"phone": ["Номер телефона от 7 до 16 цифр"]}
        ],
        "expected_data": {}
      },
      # Запрещенный домен email
      {
        "data": {
          "email": "testuser@gmail.com",
          "firstname": "api",
          "lastname": "autotest",
          "phone": "+79991234567",
          "password": "testpassword"
        },
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {"email": [
            "Почтовые домены gmail.com, yahoo.com, hotmail.com, live.com, outlook.com, icloud.com, me.com и mac.com в системе SAURES использовать невозможно. Укажите EMAIL другой почтовой службы."]}
        ],
        "expected_data": {}
      },
      # Повторная регистрация
      {
        "data": {
          "email": "a.kolchin@saures.ru",
          "firstname": "api",
          "lastname": "autotest",
          "phone": "+79991234567",
          "password": "testpassword"
        },
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {"email": ["Пользователь уже зарегистрирован"]}
        ],
        "expected_data": {}
      },
    ]

    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/user/register", data=test_case["data"])
      self.assertEqual(response.status_code, test_case["expected_status_code"])
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])


  def test_login_post(self):

    test_cases = [
      # Положительный тест (наличие telegram закомментировано)
      {
        "data": {
        "email": "artem.kolchin.979@gmail.com",
        "password": "qwerty"
        },
        "expected_status_code": 200,
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {
          "sid": "",
          "role": 1,
          "api": 1,
          "telegram": True
        }
      },
      # Негативный тест
      {
        "data": {
        "email": "a.kolchin@saures.ru",
        "password": "="
        },
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {"name": "WrongCredsException", "msg": "Неправильный email или пароль"}
        ],
        "expected_data": {}
      },
    ]

    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/login", data=test_case["data"])

      self.assertEqual(response.status_code, test_case["expected_status_code"])
      if response.json()["status"] == "ok":
        self.assertEqual(response.json()["errors"], test_case["expected_errors"])
        self.assertEqual(response.json()["data"]["role"], test_case["expected_data"]["role"])
        self.assertEqual(response.json()["data"]["api"], test_case["expected_data"]["api"])
        # self.assertEqual(response.json()["data"]["telegram"], test_case["expected_data"]["telegram"])
        sid = response.json()["data"]["sid"]
        self.assertTrue(uuid.UUID(sid, version=4), msg="sid не соответствует формату UUID4")
        SauresTestAPI.class_sid = sid
        print(sid)
        # print(response.json()["data"]["telegram"])
      else:
        self.assertEqual(response.json()["status"], test_case["expected_status"])
        self.assertEqual(response.json()["errors"], test_case["expected_errors"])
        self.assertEqual(response.json()["data"], test_case["expected_data"])
        print(response.json()["errors"])

  def test_user_profile_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "description": "Успешное получение профиля",
        "sid": SauresTestAPI.class_sid,
        "expected_status_code": 200,
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {
          "firstname": "API_autotest",
          "lastname": "Колчин",
          "email": "artem.kolchin.979@gmail.com",
          "phone": "89001111111"
        }
      },
      # Негативный тест, некорректный sid
      {
        "description": "Некорректный SID",
        "sid": "invalid_sid",
        "expected_status_code": 200,
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      }
    ]

    for test_case in test_cases:
      print(test_case["sid"])
      query_headers = {"sid": test_case["sid"]}
      response = requests.get("https://testapi.saures.ru/1.0/user/profile", params=query_headers)
      print("отслеживание статуса")
      print(response.json()["status"])
      self.assertEqual(response.status_code, test_case["expected_status_code"])
      if response.json()["status"] == "ok":
        print("сид подошел")
        self.assertEqual(response.json()["errors"], test_case["expected_errors"])
        self.assertEqual(response.json()["data"], test_case["expected_data"])
        print(response.json()["data"])
      else:
        self.assertEqual(response.json()["status"], test_case["expected_status"])
        self.assertEqual(response.json()["errors"], test_case["expected_errors"])
        self.assertEqual(response.json()["data"], test_case["expected_data"])
        print(response.json()["errors"])

  def test_user_profile_post(self):

    test_cases = [
      {
        # Корректное редактирование данных пользователя
        "data": {
          "sid": SauresTestAPI.class_sid,
          "email": "artem.kolchin.979@gmail.com",
          "firstname": "API_autotest",
          "lastname": "Колчин",
          "phone": "89001111111",
          "password": "qwerty"
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Некорректный SID
        "data": {
          "sid": "invalid_sid",
          "email": "new_email@example.com",
          "firstname": "test",
          "lastname": "test",
          "phone": "89001111111",
          "password": "new_password"
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      {
        # Некорректный номер
        "data": {
          "sid": SauresTestAPI.class_sid,
          "email": "new_email@example.com",
          "firstname": "test",
          "lastname": "test",
          "phone": "123",
          "password": "new_password"
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "phone": [
              "Введён неверный телефон"
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Некорректный email
        "data": {
          "sid": SauresTestAPI.class_sid,
          "email": "invalid_email",
          "firstname": "test",
          "lastname": "test",
          "phone": "89001111111",
          "password": "new_password"
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "email": [
              "Введён неверный email"
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Ввод существующего email
        "data": {
          "sid": SauresTestAPI.class_sid,
          "email": "a.kolchin@saures.ru",
          "firstname": "test",
          "lastname": "test",
          "phone": "89001111111",
          "password": "new_password"
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "email": [
              "Пользователь уже зарегистрирован"
            ]
          }
        ],
        "expected_data": {}
      }
    ]

    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/user/profile", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])
      print(test_case["expected_errors"])


if __name__ == "__main__":
  unittest.main()