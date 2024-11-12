import requests
import unittest
import uuid
import time

class SauresTestAPI(unittest.TestCase):
  class_sid = 0
  email = f"{uuid.uuid4()}@saures.ru"

  def test_first_registration_post(self):

    test_cases = [
      # Положительный тест
      {
        "data": {
          "email": SauresTestAPI.email,
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


  def test_user_objects_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
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
      query_headers = {"sid": test_case["sid"]}
      response = requests.get("https://testapi.saures.ru/1.0/user/objects", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "id": "358",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "qwe",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "BadRequest",
            "msg": "Неверный идентификатор объекта"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, непривязанный объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "1",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id']}
      response = requests.get("https://testapi.saures.ru/1.0/object/get", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_meters_get(self):

    test_cases = [
      # Положительный тест без даты
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "date": "",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Положительный тест с датой
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "date": "2023-08-11T00:00:00",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "id": "358",
        "date": "2023-08-11T00:00:00",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "qwe",
        "date": "2023-08-11T00:00:00",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Идентификатор объекта является обязательным параметром",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, непривязанный объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "1",
        "date": "2023-08-11T00:00:00",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      },
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "date": "qwe",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Неверный формат даты/времени",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(4)
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id'], "date": test_case['date']}
      response = requests.get("https://testapi.saures.ru/1.0/object/meters", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_meter_get(self):

    test_cases = [
      # Положительный тест абсолютные значения
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67340",
        "start": "2024-08-05T00:00:00",
        "finish": "2024-08-10T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Положительный тест расход
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67340",
        "start": "2024-07-05T00:00:00",
        "finish": "2024-11-05T00:00:00",
        "group": "month",
        "absolute": "false",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "123",
        "id": "67340",
        "start": "2024-08-05T00:00:00",
        "finish": "2024-11-30T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, несуществующий id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "1",
        "start": "2024-07-30T00:00:00",
        "finish": "2024-11-30T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Устройства с таким идентификатором не существует",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, отсутствие параметра id
        "sid": SauresTestAPI.class_sid,
        "id": "",
        "start": "2024-07-30T00:00:00",
        "finish": "2024-11-30T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Идентификатор устройства является обязательным параметром",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав для id
      {
        "sid": SauresTestAPI.class_sid,
        "id": "66666",
        "start": "2024-07-30T00:00:00",
        "finish": "2024-11-30T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Недостаточно прав!",
            "name": "PermissionDenied"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет поля start
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67340",
        "start": "",
        "finish": "2024-11-30T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Не найден обязательный параметр: start",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, неверный формат даты
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67340",
        "start": "123",
        "finish": "123",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Неверный формат даты",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
    ]
    time.sleep(3)
    for test_case in test_cases:
      query_headers = {
        "sid": test_case["sid"],
        "id": test_case['id'],
        "start": test_case['start'],
        "finish": test_case['finish'],
        "group": test_case['group'],
        "absolute": test_case['absolute']
      }
      response = requests.get("https://testapi.saures.ru/1.0/meter/get", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])


  def test_meter_control_post(self):

    test_cases = [
      {
        # Корректная активация крана
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67343",
          "command": "activate",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {
        "description": "ожидается закрытие",
        "type": "close"
        },
      },
      {
        # Некорректный SID
        "data": {
          "sid": "invalid_sid",
          "id": "67343",
          "command": "activate",
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
        # Несуществующий id устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "1",
          "command": "activate",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Устройства с таким идентификатором не существует",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, отсутствие параметра id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "",
          "command": "activate",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Идентификатор устройства является обязательным параметром",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Нет прав для id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "66666",
          "command": "activate",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Недостаточно прав!",
            "name": "PermissionDenied"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, id неуправляемого устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67340",
          "command": "activate",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Неуправляемый тип устройства",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректная команда для устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67343",
          "command": "deactivate",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Неверная команда",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, отсутствие команды
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67343",
          "command": "",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Команда является обязательным параметром",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректная команда
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67343",
          "command": "qwe",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Неизвестная команда",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(2)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/meter/control", data=test_case["data"])
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_meter_settings_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67340",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "id": "67340",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id устройства
      {
        "sid": SauresTestAPI.class_sid,
        "id": "1",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "AbstractException",
            "msg": "Неверный идентификатор устройства"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, непривязанное устройство
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67300",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id']}
      response = requests.get("https://testapi.saures.ru/1.0/meter/settings", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_meter_settings_post(self):

    test_cases = [
      {
        # Корректное изменение настроек устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67340",
          "lk": "30",
          "st": "600",
          "pv": "+10",
          "sv": "1689",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Некорректный SID
        "data": {
          "sid": "invalid_sid",
          "id": "67340",
          "lk": "30",
          "st": "600",
          "pv": "+10",
          "sv": "1689.01",
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
        # Несуществующий id устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "1",
          "lk": "30",
          "st": "600",
          "pv": "+10",
          "sv": "1689.01",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Неверный идентификатор устройства",
            "name": "AbstractException"
          }
        ],
        "expected_data": {}
      },
      {
        # Нет прав для id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "66666",
          "lk": "30",
          "st": "600",
          "pv": "+10",
          "sv": "1689.01",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Недостаточно прав!",
            "name": "PermissionDenied"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, не целые числа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "67340",
          "lk": "100.01",
          "st": "100.01",
          "pv": "100.01",
          "sv": "100.01",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "lk": [
              "Not a valid integer value."
            ],
            "pv": [
              "Not a valid integer value."
            ],
            "st": [
              "Not a valid integer value."
            ],
            "sv": [
              "Not a valid integer value."
            ]
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(2.5)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/meter/settings", data=test_case["data"])
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_meter_types_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {
            "types": [
              {
                  "id": 1,
                  "name": "Холодная вода"
              },
              {
                  "id": 2,
                  "name": "Горячая вода"
              },
              {
                  "id": 3,
                  "name": "Газ"
              },
              {
                  "id": 4,
                  "name": "Протечка"
              },
              {
                  "id": 5,
                  "name": "Температура"
              },
              {
                  "id": 6,
                  "name": "Кран/реле"
              },
              {
                  "id": 7,
                  "name": "Тепло"
              },
              {
                  "id": 8,
                  "name": "Электричество"
              },
              {
                  "id": 9,
                  "name": "Датчик"
              },
              {
                  "id": 10,
                  "name": "Состояние крана"
              },
              {
                  "id": 11,
                  "name": "Тепло"
              },
              {
                  "id": 12,
                  "name": "Тепло"
              },
              {
                  "id": 13,
                  "name": "Тепло"
              },
              {
                  "id": 14,
                  "name": "Давление"
              },
              {
                  "id": 18,
                  "name": "Температура и влажность"
              },
              {
                  "id": 19,
                  "name": "Температура"
              },
              {
                  "id": 20,
                  "name": "Влажность"
              },
              {
                  "id": 15,
                  "name": "Виртуальный измеритель"
              },
              {
                  "id": 16,
                  "name": "Виртуальный датчик"
              },
              {
                  "id": 17,
                  "name": "Психрометр"
              },
              {
                  "id": 21,
                  "name": "Виртуальный счётчик"
              }
          ]
        },
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
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
      query_headers = {"sid": test_case["sid"]}
      response = requests.get("https://testapi.saures.ru/1.0/meter/types", params=query_headers)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_object_add_post(self):

    test_cases = [
      {
        # Положительный тест добавление объекта по city_id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "city_id": "1",
          "street": f"{uuid.uuid4()}",
          "building": "1",
          "number": "1",
          "type": "1",
          "management_inn": "111111111",
          "personal_account": "111111",
          "account_id": "222222",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест добавление объекта по координатам
        "data": {
          "sid": SauresTestAPI.class_sid,
          "latitude": "56.8519",
          "longitude": "60.6122",
          "street": f"{uuid.uuid4()}",
          "building": "1",
          "number": "1",
          "type": "5",
          "management_inn": "111111111",
          "personal_account": "111111",
          "account_id": "222222",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест добавление объекта по названию + utc
        "data": {
          "sid": SauresTestAPI.class_sid,
          "city": "Астрахань",
          "utc": "4",
          "street": f"{uuid.uuid4()}",
          "building": "1",
          "number": "1",
          "type": "7",
          "management_inn": "111111111",
          "personal_account": "111111",
          "account_id": "222222",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный utc и тип объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "city": "Астрахань",
          "utc": "qwe",
          "street": f"{uuid.uuid4()}",
          "building": "1",
          "number": "1",
          "type": "100",
          "management_inn": "111111111",
          "personal_account": "111111",
          "account_id": "222222",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "utc": ["Некорректное дробное число"],
            "type": ["Not a valid choice."]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректный sid
        "data": {
          "sid": "invalid_sid",
          "city_id": "",
          "latitude": "",
          "longitude": "79528",
          "city": "",
          "utc": "1",
          "street": "1",
          "building": "1",
          "number": "1",
          "type": "1",
          "install_inn": "1",
          "management_inn": "1",
          "personal_account": "1",
          "account_id": "1",
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
        # Нет прав для id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "latitude": "11,11",
          "longitude": "11,111",
          "street": "1",
          "building": "1",
          "number": "1",
          "type": "1",
          "install_inn": "1",
          "management_inn": "1",
          "personal_account": "1",
          "account_id": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'latitude': ['Некорректное дробное число'],
            'longitude': ['Некорректное дробное число'],
            'install_inn': ['ИНН организаций от 9 до 12 цифр'],
            'account_id': ['Лицевой счёт от 6 до 20 цифр'],
            'management_inn': ['ИНН организаций от 9 до 12 цифр'],
            'personal_account': ['Лицевой счёт от 6 до 20 цифр']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный city_id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "city_id": "9999999999",
          "street": f"{uuid.uuid4()}",
          "building": "1",
          "number": "1",
          "type": "1",
          "management_inn": "111111111",
          "personal_account": "111111",
          "account_id": "222222",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'city_id': ['Город/населённый пункт не найден']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, повторное создание объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "city_id": "1",
          "street": "9bac5c04-471e-426e-b7ff-42025ce74d38",
          "building": "1",
          "number": "1",
          "type": "1",
          "management_inn": "111111111",
          "personal_account": "111111",
          "account_id": "222222",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'number': ['Объект уже существует']
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(3.5)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/object/add", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_access_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": [
          {
            "email": "losevvv@mail.ru",
            "id": 4218,
            "level": 1,
            "name": "Владимир Владимирович Лосев"
          },
          {
            "email": "demo@saures.ru",
            "id": 10684,
            "level": 0,
            "name": "DEMO DEMO"
          },
          {
            "email": "v.zhdanov@saures.ru",
            "id": 74042,
            "level": 1,
            "name": "Владимир Жданов"
          },
          {
            "email": "artem.kolchin.979@gmail.com",
            "id": 83984,
            "level": 1,
            "name": "API_autotest Колчин"
          }
        ]
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "id": "358",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "1",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "qwe",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "BadRequest",
            "msg": "Неверный идентификатор объекта"
          }
        ],
        "expected_data": {}
      },
      {
        "sid": SauresTestAPI.class_sid,
        "id": "",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "BadRequest",
            "msg": "Неверный идентификатор объекта"
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id']}
      response = requests.get("https://testapi.saures.ru/1.0/object/access", params=query_headers)
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_object_access_post(self):  #Добавить удаление доступа
    test_cases = [
      {
        # Положительный тест редактирование доступа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "85391",
          "email": "testuser5@saures.ru",
          "level": "1",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест добавление доступа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "79528",
          "email": SauresTestAPI.email,
          "level": "0",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест неверный sid
        "data": {
          "sid": "invalid_sid",
          "id": "85391",
          "email": "a.kolchin1@saures.ru",
          "level": "0",
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
        # Негативный тест нет прав для id доступа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "4219",
          "email": "testuser2@saures.ru",
          "level": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Недостаточно прав!",
            "name": "PermissionDenied"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав для id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "1",
          "email": "artem.kolchin.979@gmail.com",
          "level": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Недостаточно прав!",
            "name": "PermissionDenied"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест не зарегестрированный email
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "79528",
          "email": "qweqweqwe@gmail.com",
          "level": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "email": [
                "Пользователь не зарегистрирован"
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест неверный email
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "79528",
          "email": "qweqweqwe",
          "level": "1",
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
        # Негативный тест повторное добавление доступа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "79528",
          "email": "artem.kolchin.979@gmail.com",
          "level": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "email": [
              "Пользователь уже имеет доступ к этому объекту"
            ]
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(6)
    print(SauresTestAPI.email)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/object/access", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_sensor_add_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "40F5200B61E5",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "sn": "B4E62D3F7178",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, контроллер не выходил на связь
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "B4E62D3F7178",
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": ["Контроллер не настроен или не выходил на связь более 3 дней"]
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет новых устройств
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "BCFF4D3D68FF",
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": ["В облачном сервисе отсутствует информация о новых устройствах."]
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный серийный номер
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "123",
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": ["Контроллер не настроен или не выходил на связь более 3 дней"]
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "sn": test_case['sn']}
      response = requests.get("https://testapi.saures.ru/1.0/sensor/add", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_sensor_add_post(self):

    test_cases = [
      #Добавить устройство если есть свободный канал
      #{
        # Положительный тест добавление устройства
        #"data": {
          #"sid": SauresTestAPI.class_sid,
          #"sn": "BCFF4D3D68FF",
          #"object_id": "79528",
          #"5_name": "test_api",
          #"5_sn": "123123",
          #"5_eirc": "11111111",
          #"add_lic": "",
        #},
        #"expected_status": "ok",
        #"expected_errors": [],
        #"expected_data": {}
      #},
      {
        # Негативный тест неверный sid
        "data": {
          "sid": "invalid_sid",
          "sn": "BCFF4D3D68FF",
          "object_id": "79528",
          "5_name": "test_api",
          "5_sn": "123123",
          "5_eirc": "11111111",
          "add_lic": "",
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
        # Негативный тест некорректный серийный номер
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "08F9E056BFF5",
          "object_id": "79528",
          "5_name": "test_api",
          "5_sn": "123123",
          "5_eirc": "11111111",
          "add_lic": "",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": ["Контроллер не настроен или не выходил на связь более 3 суток"]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав для id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "object_id": "1",
          "5_name": "test_api",
          "5_sn": "123123",
          "5_eirc": "11111111",
          "add_lic": "",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Недостаточно прав!",
            "name": "PermissionDenied"
          }
        ],
        "expected_data": {}
      },
    ]
    print(SauresTestAPI.email)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/sensor/add", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_sensor_settings_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "B4E62D3F7178",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "sn": "B4E62D3F7178",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, контроллер не выходил на связь
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "40F5200B61E5",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет новых устройств
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "qwe",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "AbstractException",
            "msg": "Неверный идентификатор контроллера"
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "sn": test_case['sn']}
      response = requests.get("https://testapi.saures.ru/1.0/sensor/settings", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

if __name__ == "__main__":
  unittest.main()