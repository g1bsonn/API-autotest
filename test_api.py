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
      # Негативный тест, start старше чем finish
      {
        "sid": SauresTestAPI.class_sid,
        "id": "67340",
        "start": "2024-11-10T00:00:00",
        "finish": "2024-11-05T00:00:00",
        "group": "day",
        "absolute": "true",
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "Ошибка данных",
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
          "id": "67335",
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
            'email': 'gxgxgxdisol@mail.ru',
            "id": 4218,
            "level": 1,
            'name': 'Владимир Владимирович '
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
          "id": "84925",
          "email": "a.kolchin@saures.ru",
          "level": "0",
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
    time.sleep(2)
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
        "sn": "BCFF4D3D68FF",
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
            "sn": ['В облачном сервисе отсутствует информация о новых устройствах.']
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет доступа к контроллеру
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "BCFF4D3D7CEC",
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": ['В облачном сервисе отсутствует информация о новых устройствах.']
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный серийный номер
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "1",
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
      {
        # Негативный тест некорректный sn
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "12",
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
    time.sleep(3)
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "sn": test_case['sn']}
      response = requests.get("https://testapi.saures.ru/1.0/sensor/settings", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_sensor_settings_post(self):
    string = f"{uuid.uuid4()}"
    test_cases = [
      {
        # Положительный тест редактирование контроллера объект Москва, Новочеремушкинская, 61, TEST 3.5а
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "CC50E32C7A4B",
          "name": string[:25],
          "new_firmware": "",
          "check_hours": "12",
          "send": "120",
          "log": "60",
          "vol": "1000",
          "scan": "1",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест, длинное имя контроллера
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "CC50E32C7A4B",
          "name": f"{uuid.uuid4()}",
          "check_hours": "12",
          "send": "120",
          "log": "60",
          "vol": "1000",
          "scan": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'name': [
                'Длина не должна превышать 30 символов'
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав на контроллер
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "051900450021",
          "name": f"{uuid.uuid4()}",
          "new_firmware": "",
          "check_hours": "12",
          "send": "120",
          "log": "60",
          "vol": "1000",
          "scan": "1",
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
        # Негативный тест, некорректный sid
        "data": {
          "sid": "invalid_sid",
          "sn": "CC50E32C7A4B",
          "name": f"{uuid.uuid4()}",
          "new_firmware": "",
          "check_hours": "12",
          "send": "120",
          "log": "60",
          "vol": "1000",
          "scan": "1",
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
        # Негативный тест некорректная версия прошивки
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "CC50E32C7A4B",
          "name": "qwe",
          "new_firmware": "11111111",
          "check_hours": "12",
          "send": "120",
          "log": "60",
          "vol": "1000",
          "scan": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "new_firmware": [
                'Контроллер не выходил на связь более 15 суток.'
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректная версия прошивки НУЖЕН ФИКС
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "name": "qwe",
          "new_firmware": "11111111",
          "check_hours": "12",
          "send": "120",
          "log": "60",
          "vol": "1000",
          "scan": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "msg": "",
            "name": "SystemError"
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный тип данных
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "CC50E32C7A4B",
          "name": "1,2",
          "new_firmware": "1,2",
          "check_hours": "1,2",
          "send": "1,2",
          "log": "1,2",
          "vol": "1,2",
          "scan": "1,2",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "check_hours": [
                "Not a valid integer value."
            ],
            "log": [
                "Not a valid integer value."
            ],
            "new_firmware": [
                "Контроллер не выходил на связь более 15 суток."
            ],
            "scan": [
                "Not a valid integer value.",
                "Значение от 0 до 3600"
            ],
            "send": [
                "Not a valid integer value."
            ],
            "vol": [
                "Not a valid integer value."
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест отсутствие sn
        "data": {
          "sid": SauresTestAPI.class_sid,
          "name": "",
          "new_firmware": "",
          "check_hours": "",
          "send": "",
          "log": "",
          "vol": "",
          "scan": "",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": [
                "Серийный номер: 6,7,8 цифр или 12 символов",
                "Обязательный параметр"
            ]
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, малые периоды отправки
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "CC50E32C7A4B",
          "name": "qwe",
          "check_hours": "12",
          "send": "1",
          "log": "1",
          "vol": "1000",
          "scan": "1",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            "log": [
                "Период журналирования. Значения меньше 5 недоступны."
            ],
            "send": [
                "Период связи. Значения меньше 5 недоступны."
            ]
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(5)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/sensor/settings", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_sensor_battery_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "B4E62D3F7178",
        "start": "2024-08-01",
        "finish": "2024-08-10",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "sn": "B4E62D3F7178",
        "start": "2024-08-01",
        "finish": "2024-08-10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав на контроллер
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "051900450020",
        "start": "2024-08-01",
        "finish": "2024-08-10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, start задан некорректно
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "B4E62D3F7178",
        "start": "123",
        "finish": "2024-08-10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "start": [
              "Неверный формат даты"
            ]
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, finish задан некорректно
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "B4E62D3F7178",
        "start": "2024-08-10",
        "finish": "123",
        "expected_status": "bad",
        "expected_errors": [
          {
            "finish": [
              "Неверный формат даты"
            ]
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный sn
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "qwe",
        "start": "",
        "finish": "",
        "expected_status": "bad",
        "expected_errors": [
          {
            "sn": ["Неверный идентификатор контроллера"]
          }
        ],
        "expected_data": {}
      }
    ]
    time.sleep(2)
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "sn": test_case['sn'], "start": test_case['start'], "finish": test_case['finish']}
      response = requests.get("https://testapi.saures.ru/1.0/sensor/battery", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_sensor_move_post(self):  #Добавить удаление доступа
    test_cases = [
      {
        # Положительный тест перемещение контроллера
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "from": "80251",
          "to": "79528",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест перемещение обратно
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "from": "79528",
          "to": "80251",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест неверный sid
        "data": {
          "sid": "invalid_sid",
          "sn": "BCFF4D3D68FF",
          "from": "79528",
          "to": "80251",
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
        # Негативный тест некорректный sn
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "qwe",
          "from": "79528",
          "to": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'sn': ['Неверный идентификатор контроллера']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав для контроллера
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "0A1500250042",
          "from": "79528",
          "to": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'sn': ['Контроллер не привязан к объекту']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест Отсутствие меток на объекты
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "from": "",
          "to": "",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': '',
            'name': 'SystemError'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректные метки на объекты
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "from": "1234567890",
          "to": "1234567890",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id to
        "data": {
          "sid": SauresTestAPI.class_sid,
          "sn": "BCFF4D3D68FF",
          "from": "79528",
          "to": "1234",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      }
    ]
    print(SauresTestAPI.email)
    time.sleep(2)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/sensor/move", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_sensor_clear_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "BCFF4D3D68FF",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "sn": "BCFF4D3D68FF",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный sn
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "qwe",
        "expected_status": "bad",
        "expected_errors": [
        {
          "sn": ["Неверный идентификатор контроллера"]
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, нет прав для sn
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "0A1500250042",
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
    time.sleep(3)
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "sn": test_case['sn']}
      response = requests.get("https://testapi.saures.ru/1.0/sensor/clear", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_sensor_delete_get(self): # Добавить положительный тест

    test_cases = [
      # Негативный тест, повторное удаление
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "40F5200B5CAB",
        "expected_status": "bad",
        "expected_errors": [
          {
            'sn': ['Неверный идентификатор контроллера']
          }
        ],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "sn": "BCFF4D3D68FF",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный sn
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "qwe",
        "expected_status": "bad",
        "expected_errors": [
        {
          'sn': ['Неверный идентификатор контроллера']
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, нет прав для sn
      {
        "sid": SauresTestAPI.class_sid,
        "sn": "0A1500250042",
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
    time.sleep(2)
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "sn": test_case['sn']}
      response = requests.get("https://testapi.saures.ru/1.0/sensor/delete", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_meter_save_post(self):
    string = f"{uuid.uuid4()}"
    test_cases = [
      {
        # Положительный тест редактирование контроллера объект Москва, Новочеремушкинская, 61, TEST 3.5а
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "88427",
          "name": string,
          "sn": "123456",
          "approve_dt": "2025-08-10",
          "eirc_num": "111111",
          "active_text": "датчик температуры неактивен",
          "passive_text": "датчик температуры неактивен",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректный sid
        "data": {
          "sid": "invalid_sid",
          "id": "88427",
          "name": "api_autotest",
          "sn": "123456",
          "approve_dt": "2025-08-10",
          "eirc_num": "111111",
          "active_text": "датчик температуры активен",
          "passive_text": "датчик температуры неактивен",
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
        # Негативный тест нет прав на id устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "18799",
          "name": "api_autotest",
          "sn": "123456",
          "approve_dt": "2025-08-10",
          "eirc_num": "111111",
          "active_text": "датчик температуры активен",
          "passive_text": "датчик температуры неактивен",
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
        # Негативный тест, некорректный id устройства
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "99999999999",
          "name": "api_autotest",
          "sn": "123456",
          "approve_dt": "2025-08-10",
          "eirc_num": "111111",
          "active_text": "датчик температуры активен",
          "passive_text": "датчик температуры неактивен",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Неверный идентификатор устройства',
            'name': 'AbstractException'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест длинное название
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "88427",
          "name": "api_autotest111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
          "sn": "123456",
          "approve_dt": "2025-08-10",
          "eirc_num": "111111",
          "active_text": "датчик температуры активен",
          "passive_text": "датчик температуры неактивен",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'name': ['Длина не должна превышать 100 символов']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест неверный формат даты
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "88427",
          "name": "api_autotest",
          "sn": "123456",
          "approve_dt": "123",
          "eirc_num": "111111",
          "active_text": "датчик температуры активен",
          "passive_text": "датчик температуры неактивен",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'approve_dt': ['Not a valid date value.']
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/meter/save", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_object_journal_get(self):

    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "page": "1",
        "step": "10",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "id": "358",
        "page": "1",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "82212",
        "page": "1",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id
      {
        "sid": SauresTestAPI.class_sid,
        "id": "qwe",
        "page": "1",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Неверный идентификатор объекта',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректная страница
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "page": "0",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недопустимое значение параметра page',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный тип данных
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "page": "1,2",
        "step": "1,2",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': '',
            'name': 'SystemError'
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id'], "page": test_case['page'], "step": test_case['step']}
      response = requests.get("https://testapi.saures.ru/1.0/object/journal", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_tariffs_get(self): # Добавить положительный тест

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "object_id": "358",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invelid_sid",
        "object_id": "358",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "object_id": "665",
        "expected_status": "bad",
        "expected_errors": [
        {
          'msg': 'Недостаточно прав!',
          'name': 'PermissionDenied'
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "object_id": "11111111111111111111111111",
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
      query_headers = {"sid": test_case["sid"], "object_id": test_case['object_id']}
      response = requests.get("https://testapi.saures.ru/1.0/object/tariffs", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_tariffs_post(self):
    test_cases = [
      {
        # Положительный тест смена тарифа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "plug": "9",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест смена тарифа обратно
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "plug": "4",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест неверный sid
        "data": {
          "sid": "invalid_sid",
          "object_id": "13946",
          "plug": "4",
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
        # Негативный тест некорректный id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "11111111111111111",
          "plug": "4",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав на объект
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "665",
          "plug": "4",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id тарифа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "13946",
          "plug": "999999",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'На этот тариф нельзя перейти',
            'name': 'AbstractException'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест тариф для УК
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "13946",
          "plug": "6",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'На этот тариф нельзя перейти',
            'name': 'AbstractException'
          }
        ],
        "expected_data": {}
      }
    ]
    print(SauresTestAPI.email)
    time.sleep(2)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/object/tariffs", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_object_services_get(self):

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "object_id": "358",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invelid_sid",
        "object_id": "358",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "object_id": "665",
        "expected_status": "bad",
        "expected_errors": [
        {
          'msg': 'Недостаточно прав!',
          'name': 'PermissionDenied'
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "object_id": "11111111111111111111111111",
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
      query_headers = {"sid": test_case["sid"], "object_id": test_case['object_id']}
      response = requests.get("https://testapi.saures.ru/1.0/object/services", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_services_post(self):
    test_cases = [
      {
        # Положительный тест подключение услуги
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "13946",
          "plug": "10",
          "tariff_id": "4",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест отключение услуги
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "13946",
          "unplug": "10"
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Неверные параметры запроса',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест неверный sid
        "data": {
          "sid": "invalid_sid",
          "object_id": "13946",
          "plug": "9",
          "tariff_id": "4",
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
        # Негативный тест некорректный id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "0",
          "plug": "9",
          "tariff_id": "4",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав на объект
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "665",
          "plug": "9",
          "tariff_id": "4",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id тарифа
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "665",
          "plug": "9",
          "tariff_id": "99999",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест тариф не активен
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "665",
          "plug": "9",
          "tariff_id": "10",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id услуги
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "665",
          "plug": "999999",
          "tariff_id": "4",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      }
    ]
    print(SauresTestAPI.email)
    time.sleep(2)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/object/services", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_payment_create_post(self):
    string = f"{uuid.uuid4()}"
    test_cases = [
      {
        # Положительный тест создание платежа банковской картой
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "tariff_id": "1800",
          "payment_method": "bank_card",
          "value": "10",
          "return_url": "https://test.saures.ru/",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректный sid
        "data": {
          "sid": "invalid_sid",
          "object_id": "80251",
          "tariff_id": "4",
          "payment_method": "bank_card",
          "value": "10",
          "return_url": "https://test.saures.ru/",
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
        # Негативный тест нет прав на id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "123",
          "tariff_id": "4",
          "payment_method": "bank_card",
          "value": "10",
          "return_url": "https://test.saures.ru/",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Ошибка доступа',
            'name': 'AbstractException'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректный метод оплаты
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "tariff_id": "4",
          "payment_method": "qwe",
          "value": "10",
          "return_url": "https://test.saures.ru/",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Ошибка доступа',
            'name': 'AbstractException'
          }
        ],
        "expected_data": {}
      },
    ]
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/payment/create", data=test_case["data"])
      self.assertEqual(response.status_code, 200)
      print(response.json()["data"])
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_transactions_get(self):
    test_cases = [
      # Положительный тест, корректный sid
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "page": "1",
        "step": "10",
        "expected_status": "ok",
        "expected_errors": [],
        # Добавить expected data опционально
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invalid_sid",
        "id": "358",
        "page": "1",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "82212",
        "page": "1",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "PermissionDenied",
            "msg": "Недостаточно прав!"
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id
      {
        "sid": SauresTestAPI.class_sid,
        "id": "qwe",
        "page": "1",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Неверный идентификатор объекта',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректная страница
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "page": "0",
        "step": "10",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недопустимое значение параметра page',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      },
      # Негативный тест, некорректный тип данных
      {
        "sid": SauresTestAPI.class_sid,
        "id": "358",
        "page": "1,2",
        "step": "1,2",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': '',
            'name': 'SystemError'
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id'], "page": test_case['page'],
                       "step": test_case['step']}
      response = requests.get("https://testapi.saures.ru/1.0/object/journal", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_schedule_get(self):

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "id": "80251",
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
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "665",
        "expected_status": "bad",
        "expected_errors": [
        {
          'msg': 'Недостаточно прав!',
          'name': 'PermissionDenied'
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "11111111111111111111111111",
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
      response = requests.get("https://testapi.saures.ru/1.0/object/schedule", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_schedule_post(self):
    test_cases = [
      {
        # Положительный тест добавление уведомления email объект Москва, тест
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
          "object_id": "80251",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест добавление уведомления mvk объект Москва, тест
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "mvk",
          "day": "32",
          "time": "8:00",
          "personal_account": "777777",
          "fraction": "1",
          "resource": "1",
          "resource": "2",
          "object_id": "80251",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест редактирование уведомления sms объект Москва, тест
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "26975",
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "999999",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
#      {
        # Положительный тест удаление уведомления
#        "data": {
#          "sid": SauresTestAPI.class_sid,
#          "delete": "80251",
#        },
#        "expected_status": "ok",
#        "expected_errors": [],
#        "expected_data": {}
#      },
      {
        # Положительный тест ручная отправка
        "data": {
          "sid": SauresTestAPI.class_sid,
          "manual": "26975",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест, некорректный sid
        "data": {
          "sid": "invalid_sid",
          "id": "80251",
          "type": "80251",
          "day": "80251",
          "time": "80251",
          "personal_account": "80251",
          "fraction": "80251",
          "receiver": "80251",
          "template": "80251",
          "new_template": "80251",
          "new_template_title": "80251",
          "resource": "80251",
          "delete": "80251",
          "manual": "80251",
          "remove": "notice+error",
          "object_id": "email",
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
        # Негативный тест, некорректный type
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "qwe",
          "day": "32",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
          "object_id": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'type': ['Not a valid choice.']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id объекта при создании
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
          "object_id": "0",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав на id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
          "object_id": "22222",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректное время
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "32",
          "time": "11",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
          "object_id": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'time': ['Not a valid choice.']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный день
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "123123",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
          "object_id": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'day': ['Not a valid choice.']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный тип ресурса
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "123123123",
          "object_id": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'resource': ['Выберите хотя бы один тип ресурса']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный личный счет
        "data": {
          "sid": SauresTestAPI.class_sid,
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "111111",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "123123123",
          "resource": "1",
          "object_id": "80251",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'template': ['Not a valid choice.']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id для редактирования
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "123123",
          "type": "email",
          "day": "32",
          "time": "0:00",
          "personal_account": "777777",
          "fraction": "1",
          "receiver": SauresTestAPI.email,
          "template": "1",
          "resource": "1",
          "resource": "2",
          "resource": "9",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Неверные параметры запроса',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      },
    ]
    time.sleep(2)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/object/schedule", data=test_case["data"])
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_schedule_templates_get(self):

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {
          "1": "По умолчанию",
          "11": "АТОМЭНЕРГОСБЫТ, EMAIL и SMS, электроэнергия",
          "12": "ЯрОбл ЕИРЦ, SMS, вода",
          "13": "ЕРЦ Мурманской области, EMAIL, SMS",
          "14": "ВЦ ИНКОМУС Пермь, SMS, вода",
          "15": "Пермэнергосбыт, SMS, электроэнергия",
          "17": "ТНС энерго, EMAIL, электроэнергия",
          "2": "Стандартный (фио, адрес, лицевой счет в теле)\n",
          "20": "ГАЗПРОММЕЖРЕГИОНГАЗ (разделитель *, в конце #), SMS, газ",
          "21": "АМУРЭНЕРГОСБЫТ, EMAIL",
          "22": "АМУРЭНЕРГОСБЫТ, SMS",
          "23": "Промтехэнерго, SMS",
          "24": "СарРЦ Саратов, SMS, вода",
          "25": "ВОДОКАНАЛ-НТ НИЖНИЙ ТАГИЛ, вода",
          "3": "ВЦ по КП г. Владивостока, EMAIL, вода\n",
          "4": "ГАЗПРОММЕЖРЕГИОНГАЗ (разделитель пробел), SMS, газ",
          "6": "ПАО ДЭК, SMS, электроэнергия",
          "7": "ГАЗПРОММЕЖРЕГИОНГАЗ (разделитель #), SMS, газ",
          "9": "ГАЗПРОММЕЖРЕГИОНГАЗ (разделитель *), SMS, газ"
        },
      },
      # Негативный тест, некорректный sid
      {
        "sid": "invelid_sid",
        "object_id": "358",
        "expected_status": "bad",
        "expected_errors": [
          {
            "name": "WrongSIDException",
            "msg": "Неверный sid"
          }
        ],
        "expected_data": {}
      },
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"]}
      response = requests.get("https://testapi.saures.ru/1.0/schedule/templates", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_schedule_template_get(self):

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "id": "1",
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
      # Негативный тест, некорректный id шаблона
      {
        "sid": SauresTestAPI.class_sid,
        "id": "111111111111",
        "expected_status": "bad",
        "expected_errors": [
        {
          'msg': 'Неверный идентификатор шаблона',
          'name': 'BadRequest'
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "0",
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Неверный идентификатор шаблона',
            'name': 'BadRequest'
          }
        ],
        "expected_data": {}
      }
    ]
    for test_case in test_cases:
      query_headers = {"sid": test_case["sid"], "id": test_case['id']}
      response = requests.get("https://testapi.saures.ru/1.0/schedule/template", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_notice_get(self):

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "id": "80251",
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
      # Негативный тест, некорректный id шаблона
      {
        "sid": SauresTestAPI.class_sid,
        "id": "111111111111",
        "expected_status": "bad",
        "expected_errors": [
        {
          'msg': 'Недостаточно прав!',
          'name': 'PermissionDenied'
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "0",
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
      response = requests.get("https://testapi.saures.ru/1.0/object/notice", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])

  def test_object_notice_post(self):
    test_cases = [
      {
        # Положительный тест добавление уведомления email объект Москва, тест
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "type": "notice+error",
          "dispatch": "email",
          "receiver": SauresTestAPI.email,
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Положительный тест редактирование уведомления объект Москва, тест
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "36005",
          "type": "notice+error",
          "receiver": "apiautotest@saures.ru",
        },
        "expected_status": "ok",
        "expected_errors": [],
        "expected_data": {}
      },
      {
        # Негативный тест запрещенный домен
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "36005",
          "type": "notice+error",
          "receiver": "artem.kolchin.979@gmail.com",
        },
        "expected_status": "bad",
        "expected_errors": [{'receiver': ['Почтовые домены gmail.com, yahoo.com, hotmail.com, live.com, '
               'outlook.com, icloud.com, me.com и mac.com в системе SAURES '
               'использовать невозможно. Укажите EMAIL другой почтовой '
               'службы.']}],
        "expected_data": {}
      },
 #     {
        # Положительный тест удаление уведомления
#        "data": {
#          "sid": SauresTestAPI.class_sid,
#          "delete": "34200",
#        },
#        "expected_status": "ok",
#        "expected_errors": [],
#        "expected_data": {}
 #     },
      {
        # Негативный тест, некорректный sid
        "data": {
          "sid": "invalid_sid",
          "object_id": "123",
          "type": "2025-08-10",
          "dispatch": "111111",
          "receiver": "датчик температуры неактивен",
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
        # Негативный тест, нет прав на удаление id
        "data": {
          "sid": SauresTestAPI.class_sid,
          "delete": "12",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': '',
            'name': 'SystemError'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id объекта при создании
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "123123123123",
          "type": "notice+error",
          "dispatch": "email",
          "receiver": SauresTestAPI.email,
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест нет прав на id объекта
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "11111",
          "type": "notice+error",
          "dispatch": "email",
          "receiver": SauresTestAPI.email,
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректное поле type
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "36005",
          "type": "notice",
          "receiver": "apiautotest@saures.ru",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'type': ['Not a valid choice.']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный тип отправки
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "type": "notice+error",
          "dispatch": "123",
          "receiver": SauresTestAPI.email,
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'dispatch': ['Not a valid choice.']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест неорректный email получателя
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "type": "notice+error",
          "dispatch": "email",
          "receiver": "qwe",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'receiver': ['Введён неверный email']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный номер телефона
        "data": {
          "sid": SauresTestAPI.class_sid,
          "object_id": "80251",
          "type": "notice+error",
          "dispatch": "sms",
          "receiver": "qwe",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'receiver': ['В формате: +7XXXXXXXXXX']
          }
        ],
        "expected_data": {}
      },
      {
        # Негативный тест некорректный id для редактирования
        "data": {
          "sid": SauresTestAPI.class_sid,
          "id": "12345",
          "type": "notice+error",
          "receiver": "+79651974538",
        },
        "expected_status": "bad",
        "expected_errors": [
          {
            'msg': 'Недостаточно прав!',
            'name': 'PermissionDenied'
          }
        ],
        "expected_data": {}
      },
    ]
    time.sleep(2)
    for test_case in test_cases:
      response = requests.post("https://testapi.saures.ru/1.0/object/notice", data=test_case["data"])
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])
      self.assertEqual(response.json()["data"], test_case["expected_data"])

  def test_object_weather_get(self):

    test_cases = [
      # Положительный тест, получение тарифов
      {
        "sid": SauresTestAPI.class_sid,
        "id": "80251",
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
      # Негативный тест, нет прав на объект
      {
        "sid": SauresTestAPI.class_sid,
        "id": "665",
        "expected_status": "bad",
        "expected_errors": [
        {
          'msg': 'Недостаточно прав!',
          'name': 'PermissionDenied'
        }
      ],
        "expected_data": {}
      },
      # Негативный тест, некорректный id объекта
      {
        "sid": SauresTestAPI.class_sid,
        "id": "11111111111111111111111111",
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
      response = requests.get("https://testapi.saures.ru/1.0/object/weather", params=query_headers)
      print(response.json()["data"])
      self.assertEqual(response.status_code, 200)
      self.assertEqual(response.json()["status"], test_case["expected_status"])
      self.assertEqual(response.json()["errors"], test_case["expected_errors"])


if __name__ == "__main__":
  unittest.main()

  # у некоторых тестов отсутствует положительный тест кейс, также пройтись поиском по systemerror